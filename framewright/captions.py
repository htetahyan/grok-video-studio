"""Captions: transcription (listen), SRT/VTT writing, styled ASS, burn-in."""
from __future__ import annotations

import json
import os
import re
import textwrap
from pathlib import Path

from .util import MODELS, FwError, ffmpeg, filter_path, preset, say


# -------------------------------------------------------------- time formats
def _ts(t: float, sep: str = ",") -> str:
    t = max(t, 0)
    h, rem = divmod(int(round(t * 1000)), 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def _ass_ts(t: float) -> str:
    cs = int(round(max(t, 0) * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, c = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def parse_srt(path: Path) -> list[dict]:
    cues = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        idx = 1 if "-->" in lines[1] else 0
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", lines[idx])
        if not m:
            continue
        g = list(map(int, m.groups()))
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        cues.append({"start": start, "end": end, "text": " ".join(lines[idx + 1:]).strip()})
    return cues


def write_srt(cues: list[dict], path: Path) -> None:
    path.write_text("".join(f"{i}\n{_ts(c['start'])} --> {_ts(c['end'])}\n{c['text']}\n\n"
                            for i, c in enumerate(cues, 1)))


def write_vtt(cues: list[dict], path: Path) -> None:
    path.write_text("WEBVTT\n\n" + "".join(f"{_ts(c['start'], '.')} --> {_ts(c['end'], '.')}\n{c['text']}\n\n"
                                         for c in cues))


# -------------------------------------------------------------------- listen
def _cues_from_words(words: list[dict], max_chars: int = 64, max_dur: float = 4.0, gap: float = 0.6) -> list[dict]:
    """Group words into readable cues: break on punctuation, pauses, length and duration."""
    cues, cur = [], []
    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > gap or
                    len(" ".join(x["word"] for x in cur + [w])) > max_chars or
                    w["end"] - cur[0]["start"] > max_dur):
            cues.append(cur)
            cur = []
        cur.append(w)
        text = " ".join(x["word"] for x in cur)
        if re.search(r"[.!?]$", w["word"]) or (re.search(r"[,;:]$", w["word"]) and len(text) >= 30):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    return [{"start": c[0]["start"], "end": c[-1]["end"],
             "text": " ".join(x["word"] for x in c).strip()} for c in cues]


def listen(media: Path, outdir: Path, model: str = "base.en", language: str | None = "en",
           prompt: str | None = None) -> dict:
    """Transcribe with faster-whisper (preferred) or openai-whisper -> .srt/.vtt/.words.json.

    `prompt` biases spelling of names/jargon (e.g. "Framewright, Htet")."""
    outdir.mkdir(parents=True, exist_ok=True)
    words, engine = [], None
    cache = Path(os.environ.get("FW_WHISPER_DIR", MODELS / "whisper"))
    try:
        from faster_whisper import WhisperModel  # type: ignore
        engine = f"faster-whisper:{model}"
        wm = WhisperModel(model, device="cpu", compute_type="int8", download_root=str(cache))
        segments, info = wm.transcribe(str(media), language=language, word_timestamps=True, vad_filter=True,
                                          initial_prompt=prompt)
        for seg in segments:
            for w in seg.words or []:
                words.append({"word": w.word.strip(), "start": round(w.start, 3),
                              "end": round(w.end, 3), "p": round(w.probability, 3)})
    except ImportError:
        try:
            import whisper  # type: ignore
            engine = f"openai-whisper:{model}"
            wm = whisper.load_model(model, download_root=str(cache))
            result = wm.transcribe(str(media), language=language, word_timestamps=True, initial_prompt=prompt)
            for seg in result["segments"]:
                for w in seg.get("words", []):
                    words.append({"word": w["word"].strip(), "start": round(w["start"], 3),
                                  "end": round(w["end"], 3), "p": round(w.get("probability", 0), 3)})
        except ImportError:
            raise FwError("no whisper engine installed. Run bin/setup.sh, or supply a hand-made SRT "
                          "with `fw captions --srt your.srt`.")
    cues = _cues_from_words(words)
    stem = media.stem
    srt, vtt, wj = outdir / f"{stem}.srt", outdir / f"{stem}.vtt", outdir / f"{stem}.words.json"
    write_srt(cues, srt)
    write_vtt(cues, vtt)
    wj.write_text(json.dumps({"engine": engine, "words": words}, indent=1))
    low = [w for w in words if w["p"] < 0.5]
    say(f"transcribed {len(words)} words into {len(cues)} cues ({engine}); {len(low)} low-confidence words")
    return {"srt": str(srt), "vtt": str(vtt), "words": str(wj), "engine": engine,
            "cue_count": len(cues), "low_confidence": [w["word"] for w in low]}


# ----------------------------------------------------------------------- ASS
def styled_ass(srt: Path, out: Path, width: int, height: int, style: str = "lower-band") -> Path:
    styles = preset("captions")
    if style not in styles:
        raise FwError(f"unknown caption style '{style}'. Known: {', '.join(styles)}")
    s = styles[style]
    size = round(height * s["size_ratio"]) if width >= height else round(width * s["size_ratio"] * 1.6)
    outline = max(1, round(height * s["outline_px"]))
    margin_v = round(height * s["margin_v_ratio"])
    margin_h = round(width * 0.08)
    header = f"""[Script Info]
; made by framewright captions ({style})
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{s['font']},{size},{s['primary']},&H000000FF,{s['outline']},{s['back']},{-1 if s['bold'] else 0},0,0,0,100,100,0,0,{s['border_style']},{outline},{s['shadow']},{s['alignment']},{margin_h},{margin_h},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for c in parse_srt(srt):
        lines = textwrap.wrap(c["text"], width=s["max_chars"]) or [""]
        if len(lines) > s["max_lines"]:  # split long cue over time instead of stacking lines
            chunks = [lines[i:i + s["max_lines"]] for i in range(0, len(lines), s["max_lines"])]
            span = (c["end"] - c["start"]) / len(chunks)
            for k, ch in enumerate(chunks):
                events.append((c["start"] + k * span, c["start"] + (k + 1) * span, ch))
        else:
            events.append((c["start"], c["end"], lines))
    body = "".join(f"Dialogue: 0,{_ass_ts(a)},{_ass_ts(b)},Cap,,0,0,0,,"
                   + "\\N".join(l.replace("{", "(").replace("}", ")") for l in ls) + "\n"
                   for a, b, ls in events)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header + body, encoding="utf-8")
    return out


def burn(video: Path, ass: Path, out: Path, crf: int = 18) -> Path:
    """Burn an ASS file into a video (audio copied)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg(["-i", str(video), "-vf", f"ass={filter_path(ass)}", "-c:v", "libx264", "-crf", str(crf),
            "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(out)])
    return out
