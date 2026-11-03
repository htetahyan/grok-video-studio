"""Doctor: check the shared box has what a production needs. Read-only."""
from __future__ import annotations

import importlib
import importlib.metadata as md
import shutil
import subprocess
import sys
from pathlib import Path

from .util import MODELS, PRODUCTIONS, REPO, STUDIO

REQUIRED_FILTERS = ["ass", "loudnorm", "ebur128", "drawtext", "blackdetect", "freezedetect",
                    "silencedetect", "tile", "boxblur"]


def _ver(cmd: list[str]) -> str | None:
    if not shutil.which(cmd[0]):
        return None
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (out.stdout or out.stderr).strip().splitlines()[0][:80]
    except Exception as e:  # pragma: no cover
        return f"error: {e}"


def _pkg(name: str, mod: str | None = None) -> str | None:
    try:
        importlib.import_module(mod or name)
        return md.version(name)
    except Exception:
        return None


def checks() -> list[tuple[str, str, str, bool]]:
    """Returns (item, status, detail, required)."""
    rows = []
    ff = _ver(["ffmpeg", "-version"])
    rows.append(("ffmpeg", "ok" if ff else "MISSING", ff or "install ffmpeg (with libass, libx264)", True))
    fp = _ver(["ffprobe", "-version"])
    rows.append(("ffprobe", "ok" if fp else "MISSING", fp or "comes with ffmpeg", True))
    if ff:
        flt = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        names = {l.split()[1] for l in flt.splitlines() if len(l.split()) > 2}
        miss = [f for f in REQUIRED_FILTERS if f not in names]
        rows.append(("ffmpeg filters", "ok" if not miss else "MISSING", "missing: " + ", ".join(miss) if miss else ", ".join(REQUIRED_FILTERS), True))
        enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        rows.append(("libx264 encoder", "ok" if "libx264" in enc else "MISSING", "", True))
    rows.append(("python", "ok" if sys.version_info >= (3, 10) else "OLD", f"{sys.version.split()[0]} at {sys.executable}", True))
    in_venv = sys.prefix != sys.base_prefix
    rows.append(("venv", "ok" if in_venv else "warn", sys.prefix if in_venv else "running on system python (run bin/setup.sh)", False))
    for item, cmd in (("node", ["node", "--version"]), ("git", ["git", "--version"]), ("gh", ["gh", "--version"])):
        v = _ver(cmd)
        rows.append((item, "ok" if v else "absent", v or "optional", False))
    fw = _pkg("faster-whisper", "faster_whisper")
    ow = _pkg("openai-whisper", "whisper")
    rows.append(("whisper engine", "ok" if (fw or ow) else "absent",
                 f"faster-whisper {fw}" if fw else (f"openai-whisper {ow}" if ow else "captions need a hand-made SRT"), False))
    av = _pkg("av")
    if fw:
        rows.append(("PyAV pin", "ok" if av and av.startswith("15.") else "warn", f"av {av} (faster-whisper 1.2.1 wants av 15.x)", False))
    pi = _pkg("piper-tts", "piper")
    rows.append(("piper TTS (demo voice)", "ok" if pi else "absent", f"piper-tts {pi}" if pi else "test clip will be tone-only", False))
    rows.append(("pillow", "ok" if _pkg("pillow", "PIL") else "absent", "optional", False))
    wm = list((MODELS / "whisper").glob("models--*whisper*"))
    rows.append(("whisper models", "ok" if wm else "absent", ", ".join(p.name.split("--")[-1] for p in wm) or f"none in {MODELS/'whisper'} (downloads on first use)", False))
    pv = list((MODELS / "piper").glob("*.onnx"))
    rows.append(("piper voices", "ok" if pv else "absent", ", ".join(p.stem for p in pv) or "none", False))
    fonts = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout if shutil.which("fc-list") else ""
    for fam in ("Inter", "Poppins"):
        rows.append((f"font {fam}", "ok" if fam in fonts else "warn", "caption style font" if fam in fonts else "libass will substitute", False))
    du = shutil.disk_usage(STUDIO if STUDIO.exists() else REPO)
    rows.append(("disk free", "ok" if du.free > 10e9 else "warn", f"{du.free/1e9:.0f} GB free at {STUDIO}", False))
    rows.append(("productions dir", "ok", str(PRODUCTIONS), False))
    return rows


def report() -> tuple[str, bool]:
    rows = checks()
    width = max(len(r[0]) for r in rows)
    lines = [f"framewright doctor — repo {REPO}", ""]
    for item, status, detail, req in rows:
        lines.append(f"  {item:<{width}}  {status:<8} {detail}")
    ok = all(s == "ok" for _, s, _, req in rows if req)
    lines += ["", "required tools: " + ("ALL PRESENT" if ok else "SOMETHING MISSING — see above")]
    return "\n".join(lines), ok
