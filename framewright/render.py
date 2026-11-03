"""Render a numbered cut for a delivery preset: frame fit, captions, measured sound."""
from __future__ import annotations

import shlex
from pathlib import Path

from . import captions, media, sound
from .util import (FwError, Production, ffmpeg, filter_path, fontfile, preset, rel,
                   say, sha256)


def delivery(name: str) -> dict:
    d = preset("delivery")
    if name not in d:
        raise FwError(f"unknown delivery preset '{name}'. Known: {', '.join(d)}")
    return {"name": name, **d[name]}


def frame_filter(p: dict, src_fps: float) -> str:
    w, h = p["width"], p["height"]
    fit = p.get("fit", "cover")
    if fit == "cover":
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    elif fit == "fit-pad":
        vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black"
    elif fit == "blur-pad":
        vf = (f"split=2[bg][fg];[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
              f"boxblur=luma_radius=40:luma_power=2,eq=brightness=-0.08[bgb];"
              f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2")
    else:
        raise FwError(f"unknown fit '{fit}'")
    vf += ",setsar=1"
    if src_fps and src_fps > p.get("max_fps", 60) + 0.01:
        vf += f",fps={p['max_fps']}"
    return vf


def render(prod: Production, src: Path, preset_name: str, srt: Path | None = None,
           loudness: str | None = None, cut: int | None = None, caption_style: str | None = None,
           note: str = "") -> dict:
    prod.check_claim()
    p = delivery(preset_name)
    src = Path(src).resolve()
    prof = loudness or prod.manifest().get("loudness_profile") or p["loudness"]
    n = cut or prod.next_cut()
    stem = f"{prod.slug}_c{n:03d}_{preset_name}"
    out = prod.cuts / f"{stem}.mp4"
    if out.exists():
        raise FwError(f"{out.name} already exists — cuts are never overwritten; use a new cut number")
    if prod.intake.resolve() in out.resolve().parents:
        raise FwError("refusing to write into intake/")

    info = media.summarize(media.ffprobe_json(src))
    vf = frame_filter(p, (info.get("video") or {}).get("fps", 0))
    ass = None
    if srt:
        ass = captions.styled_ass(Path(srt), prod.bench / "captions" / f"{stem}.ass",
                                  p["width"], p["height"], caption_style or p["caption_style"])
        vf += f",ass={filter_path(ass)}"
    if p.get("timecode"):
        font = fontfile()
        ff = f"fontfile={filter_path(Path(font))}:" if font else ""
        vf += (f",drawtext={ff}text='{stem}  %{{pts\\:hms}}':fontsize=24:fontcolor=white:"
               f"box=1:boxcolor=black@0.55:x=20:y=h-50")
    vf += ",setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709,format=yuv420p"

    args = ["-i", str(src), "-filter_complex", f"[0:v:0]{vf}[v]", "-map", "[v]"]
    before = None
    if info.get("audio"):
        af, before = sound.loudnorm_filter(src, prof)
        args += ["-map", "0:a:0", "-af", af, "-c:a", "aac", "-b:a", p["audio_bitrate"], "-ar", "48000"]
    args += ["-c:v", "libx264", "-preset", p["x264_preset"], "-crf", str(p["crf"]),
             "-profile:v", "high", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
             "-movflags", "+faststart", "-metadata", f"comment=framewright {stem}", str(out)]
    out.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg(args)

    proof_dir = prod.proof / f"c{n:03d}"
    spec = media.spec_card(out, proof_dir)
    card = sound.sound_card(out, prof, proof_dir) if info.get("audio") else None
    entry = {"number": n, "preset": preset_name, "file": rel(out, prod.root), "source": rel(src, prod.root),
             "captions": rel(ass, prod.root) if ass else None, "loudness_profile": prof,
             "sound_pass": card["verdict"]["pass"] if card else None, "note": note}
    m = prod.manifest()
    m.setdefault("cuts", []).append(entry)
    prod.update(cuts=m["cuts"])
    prod.log("render", output=entry["file"], sha256=sha256(out), inputs=[entry["source"]],
             preset=preset_name, loudness=prof, captions=entry["captions"],
             command="ffmpeg " + " ".join(shlex.quote(a) for a in args),
             before_lufs=before["integrated_lufs"] if before else None,
             spec=rel(spec, prod.root))
    say(f"cut ready: {out}")
    return {"file": str(out), "entry": entry, "sound": card}
