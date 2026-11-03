"""Sound: loudness readouts (sound cards) and two-pass loudnorm tuning."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .util import FwError, ffmpeg, preset, save_json, say


def profile(name: str) -> dict:
    profs = preset("loudness")
    if name not in profs:
        raise FwError(f"unknown loudness profile '{name}'. Known: {', '.join(profs)}")
    return {"name": name, **profs[name]}


def _loudnorm_json(stderr: str) -> dict:
    blocks = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", stderr, re.S)
    if not blocks:
        raise FwError("could not read loudnorm statistics from ffmpeg output")
    return json.loads(blocks[-1])


def measure(path: Path) -> dict:
    """Integrated loudness, true peak, LRA (EBU R128 via ffmpeg ebur128 + loudnorm analysis)."""
    res = ffmpeg(["-i", str(path), "-vn", "-af",
                  "ebur128=peak=true:framelog=quiet,loudnorm=print_format=json", "-f", "null", "-"],
                 quiet=True)
    err = res.stderr
    stats = _loudnorm_json(err)
    summ = err[err.rfind("Summary:"):] if "Summary:" in err else ""

    def grab(label):
        m = re.search(label + r":\s+(-?[\d.]+|-inf)", summ)
        return float(m.group(1)) if m and m.group(1) != "-inf" else None

    return {
        "integrated_lufs": grab(r"I") if grab(r"I") is not None else float(stats["input_i"]),
        "true_peak_dbtp": grab(r"Peak") if grab(r"Peak") is not None else float(stats["input_tp"]),
        "lra_lu": grab(r"LRA") if grab(r"LRA") is not None else float(stats["input_lra"]),
        "threshold": float(stats["input_thresh"]),
        "loudnorm_pass1": stats,
    }


def verdict(m: dict, prof: dict) -> dict:
    di = m["integrated_lufs"] - prof["integrated"]
    ok_i = abs(di) <= prof["tolerance_lu"]
    ok_tp = m["true_peak_dbtp"] <= prof["true_peak"] + 0.1
    return {"integrated_ok": ok_i, "true_peak_ok": ok_tp, "delta_lu": round(di, 2), "pass": ok_i and ok_tp}


def sound_card(path: Path, prof_name: str, outdir: Path, m: dict | None = None) -> dict:
    prof = profile(prof_name)
    m = m or measure(path)
    v = verdict(m, prof)
    card = {"file": str(path), "profile": prof, "measured": {k: m[k] for k in
            ("integrated_lufs", "true_peak_dbtp", "lra_lu")}, "verdict": v}
    outdir.mkdir(parents=True, exist_ok=True)
    save_json(outdir / f"{path.name}.sound.json", card)
    mark = lambda b: "PASS" if b else "FAIL"
    md = (f"### Sound card — {path.name}\n\nProfile **{prof_name}** ({prof['label']})\n\n"
          f"| metric | measured | target | result |\n|---|---|---|---|\n"
          f"| integrated | {m['integrated_lufs']:.1f} LUFS | {prof['integrated']:.1f} ±{prof['tolerance_lu']} | {mark(v['integrated_ok'])} |\n"
          f"| true peak | {m['true_peak_dbtp']:.1f} dBTP | ≤ {prof['true_peak']:.1f} | {mark(v['true_peak_ok'])} |\n"
          f"| loudness range | {m['lra_lu']:.1f} LU | ~{prof['lra']:.0f} (guide) | info |\n")
    (outdir / f"{path.name}.sound.md").write_text(md)
    return card


# Lossy encoders (AAC/MP3/Opus) add inter-sample overshoot; aim the limiter lower so the
# *encoded* file still meets the profile's true-peak ceiling.
LOSSY_TP_MARGIN = 0.6


def loudnorm_filter(src: Path, prof_name: str, lossy: bool = True) -> tuple[str, dict]:
    """Pass 1: analyse src; returns the pass-2 filter string with measured values."""
    prof = profile(prof_name)
    tp = prof["true_peak"] - (LOSSY_TP_MARGIN if lossy else 0.0)
    m = measure(src)
    s = m["loudnorm_pass1"]
    f = (f"loudnorm=I={prof['integrated']}:TP={tp}:LRA={prof['lra']}:"
         f"measured_I={s['input_i']}:measured_TP={s['input_tp']}:measured_LRA={s['input_lra']}:"
         f"measured_thresh={s['input_thresh']}:offset={s['target_offset']}:linear=true:print_format=summary,"
         f"aresample=48000")
    return f, m


def tune(src: Path, out: Path, prof_name: str) -> dict:
    """Two-pass loudnorm. Video stream (if any) is copied untouched."""
    is_audio_only = out.suffix.lower() in (".wav", ".flac", ".m4a", ".mp3")
    filt, before = loudnorm_filter(src, prof_name, lossy=out.suffix.lower() not in (".wav", ".flac"))
    out.parent.mkdir(parents=True, exist_ok=True)
    args = ["-i", str(src), "-map", "0:a:0", "-af", filt]
    if is_audio_only:
        args += ["-c:a", "pcm_s24le" if out.suffix == ".wav" else "aac"]
    else:
        args = ["-i", str(src), "-map", "0:v:0?", "-map", "0:a:0", "-c:v", "copy", "-af", filt,
                "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart"]
    ffmpeg([*args, "-ar", "48000", str(out)])
    after = measure(out)
    say(f"sound: {before['integrated_lufs']:.1f} LUFS -> {after['integrated_lufs']:.1f} LUFS "
        f"(TP {after['true_peak_dbtp']:.1f} dBTP) target {profile(prof_name)['integrated']}")
    return {"before": before, "after": after}
