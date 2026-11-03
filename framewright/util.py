"""Shared helpers: paths, process runs, ffprobe, ledger, claims."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STUDIO = Path(os.environ.get("FW_STUDIO", REPO.parent)).resolve()
PRODUCTIONS = Path(os.environ.get("FW_PRODUCTIONS", REPO / "productions")).resolve()
MODELS = Path(os.environ.get("FW_MODELS", STUDIO / "models")).resolve()
PRESETS = REPO / "presets"
TEMPLATES = REPO / "templates"

CLAIM_STALE_HOURS = 12


class FwError(RuntimeError):
    """A user-facing failure (printed without a traceback)."""


def bot_name() -> str:
    return os.environ.get("FW_BOT") or os.environ.get("GROK_BOT_NAME") or "unnamed-bot"


def now() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def say(msg: str) -> None:
    print(f"[fw] {msg}", flush=True)


def run(cmd: list[str], *, capture: bool = False, cwd: Path | None = None, quiet: bool = False) -> subprocess.CompletedProcess:
    if not quiet:
        say("$ " + " ".join(shlex.quote(str(c)) for c in cmd))
    res = subprocess.run([str(c) for c in cmd], cwd=cwd, text=True,
                         capture_output=True)
    if res.returncode != 0:
        tail = "\n".join((res.stderr or "").strip().splitlines()[-25:])
        raise FwError(f"command failed ({res.returncode}): {cmd[0]}\n{tail}")
    return res


def ffmpeg(args: list, **kw) -> subprocess.CompletedProcess:
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *args], **kw)


def ffprobe_json(path: Path) -> dict:
    res = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format",
               "-show_streams", str(path)], quiet=True)
    return json.loads(res.stdout)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def preset(name: str) -> dict:
    return load_json(PRESETS / f"{name}.json", {})


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "untitled"


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def fontfile() -> str:
    for cand in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(cand).exists():
            return cand
    return ""


def filter_path(p: Path) -> str:
    """Escape a path for use inside an ffmpeg filtergraph option."""
    s = str(p)
    for ch in ("\\", ":", "'", ",", "[", "]", ";"):
        s = s.replace(ch, "\\" + ch)
    return s


# ---------------------------------------------------------------- productions
class Production:
    DIRS = ("intake", "ledger/batons", "bench", "cuts", "proof", "handover")

    def __init__(self, root: Path):
        self.root = root
        self.slug = root.name

    @classmethod
    def find(cls, ref: str | None) -> "Production":
        if ref is None:
            cwd = Path.cwd().resolve()
            for p in (cwd, *cwd.parents):
                if (p / "production.json").exists():
                    return cls(p)
            raise FwError("no production given and none found above the current folder (use -p <slug>)")
        p = Path(ref)
        if not (p / "production.json").exists():
            p = PRODUCTIONS / ref
        if not (p / "production.json").exists():
            raise FwError(f"production not found: {ref}")
        return cls(p.resolve())

    # paths
    def __getattr__(self, name):  # intake, ledger, bench, cuts, proof, handover
        if name in ("intake", "ledger", "bench", "cuts", "proof", "handover"):
            return self.root / name
        raise AttributeError(name)

    @property
    def manifest_path(self) -> Path:
        return self.root / "production.json"

    def manifest(self) -> dict:
        return load_json(self.manifest_path, {})

    def update(self, **changes) -> dict:
        m = self.manifest()
        m.update(changes)
        m["updated"] = now()
        save_json(self.manifest_path, m)
        return m

    def log(self, kind: str, **fields) -> None:
        rec = {"at": now(), "bot": bot_name(), "kind": kind, **fields}
        self.ledger.mkdir(parents=True, exist_ok=True)
        with open(self.ledger / "provenance.jsonl", "a") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def ledger_records(self) -> list[dict]:
        p = self.ledger / "provenance.jsonl"
        if not p.exists():
            return []
        return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

    def next_cut(self) -> int:
        nums = [int(m.group(1)) for f in self.cuts.glob("*") if (m := re.search(r"_c(\d{3})", f.name))]
        return max(nums, default=0) + 1

    def check_claim(self, force: bool = False) -> None:
        """Refuse to write when another bot holds a fresh claim."""
        claim = self.manifest().get("claim")
        if not claim or claim.get("bot") == bot_name() or force:
            return
        try:
            since = _dt.datetime.fromisoformat(claim["since"])
            age_h = (_dt.datetime.now().astimezone() - since).total_seconds() / 3600
        except Exception:
            age_h = 0
        if age_h < CLAIM_STALE_HOURS:
            raise FwError(
                f"'{self.slug}' is claimed by {claim['bot']} since {claim['since']} ({claim.get('note','')}). "
                "Write a baton to ask for it, or wait. Set FW_BOT to your bot name if this is you.")
        say(f"warning: stale claim by {claim['bot']} ({age_h:.0f}h old) — proceeding; leave a note in ledger/decisions.md")


def rel(p: Path, base: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(base.resolve()))
    except ValueError:
        return str(p)


def die(msg: str) -> int:
    print(f"[fw] error: {msg}", file=sys.stderr)
    return 1
