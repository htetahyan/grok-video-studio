"""`fw` — one entry point for every Framewright step."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__, captions, doctor, media, production, proof, render, sound
from .util import FwError, Production, now, rel, say


def _prod(a) -> Production:
    return Production.find(getattr(a, "production", None))


# ------------------------------------------------------------------ handover
def handover(prod: Production, cuts: list[str] | None = None) -> Path:
    """Gather chosen cuts + proof packs into handover/ with an index for the user."""
    m = prod.manifest()
    chosen = [c for c in m.get("cuts", []) if not cuts or Path(c["file"]).stem in cuts or c["file"] in cuts]
    if not chosen:
        raise FwError("no cuts to hand over")
    stamp = now()[:16].replace(":", "")
    dest = prod.handover / f"package_{stamp}"
    dest.mkdir(parents=True, exist_ok=True)
    rows = []
    for c in chosen:
        src = prod.root / c["file"]
        shutil.copy2(src, dest / src.name)
        if c.get("proof"):
            pdir = (prod.root / c["proof"]).parent
            target = dest / f"proof_{src.stem}"
            shutil.copytree(pdir, target, dirs_exist_ok=True)
            report = target / Path(c["proof"]).name
        else:
            report = None
        rows.append(f"| `{src.name}` | {c['preset']} | {c.get('proof_status','no proof yet')} | "
                    f"{rel(report, dest) if report else '-'} |")
    tmpl = (Path(__file__).resolve().parents[1] / "templates" / "handover-report.md").read_text()
    text = (tmpl.replace("{{TITLE}}", m["title"]).replace("{{SLUG}}", prod.slug).replace("{{DATE}}", now())
                .replace("{{ROWS}}", "\n".join(rows))
                .replace("{{TEST}}", "> TEST MATERIAL — synthetic source; pipeline check only.\n" if m.get("test_material") else ""))
    (dest / "HANDOVER.md").write_text(text)
    prod.log("handover", package=rel(dest, prod.root), cuts=[c["file"] for c in chosen])
    say(f"handover package: {dest}  (nothing was published or sent)")
    return dest


# ---------------------------------------------------------------------- demo
def demo(slug: str = "demo-test-signal", model: str = "base.en") -> dict:
    """End-to-end run on a synthetic clip: new > testclip > intake > listen > render x3 > proof > handover."""
    prod = production.new("Demo — synthetic test signal", slug=slug,
                          deliverables=["master-16x9", "reel-9x16", "square-1x1"], test_material=True)
    production.claim(prod, note="demo pipeline run")
    clip_name = "framewright_testclip.mp4"
    if not (prod.intake / clip_name).exists():
        tmp = prod.bench / "generated" / clip_name
        info = media.testclip(tmp)
        media.intake(prod, [tmp], source="generated locally by `fw testclip` (ffmpeg testsrc2 + piper voice)",
                     license="own work / CC0 — synthetic TEST MATERIAL", synthetic=True,
                     note=f"script: {info['script']}")
    src = prod.intake / clip_name
    production.set_stage(prod, "intake")
    try:
        lst = captions.listen(src, prod.bench / "captions", model=model, prompt="Framewright toolkit.")
        srt = Path(lst["srt"])
        prod.update(captions=rel(srt, prod.root))
        prod.log("transcribe", file=rel(srt, prod.root), engine=lst["engine"], cues=lst["cue_count"])
    except FwError as e:
        say(f"transcription skipped: {e}")
        srt = None
    production.set_stage(prod, "polish")
    n = prod.next_cut()
    results = {}
    for preset_name in ("master-16x9", "reel-9x16", "square-1x1"):
        r = render.render(prod, src, preset_name, srt=srt, cut=n, note="demo")
        results[preset_name] = proof.proof(prod, Path(r["file"]).stem)
    production.set_stage(prod, "proof")
    pkg = handover(prod)
    production.set_stage(prod, "handover")
    production.release(prod, note="demo finished")
    summary = {k: {"status": v["status"], "report": v["report"], "sheet": v["stills"]["sheet"]}
               for k, v in results.items()}
    say("demo summary:\n" + json.dumps(summary, indent=2))
    say(f"handover: {pkg}")
    return summary


# ----------------------------------------------------------------------- cli
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="fw", description="Framewright — footage-first video toolkit for Grok Bots")
    ap.add_argument("--version", action="version", version=f"framewright {__version__}")
    pp = argparse.ArgumentParser(add_help=False)
    pp.add_argument("-p", "--production", help="production slug or folder (default: the one you are inside)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="check tools, versions, models (read-only)")
    s = sub.add_parser("new", help="scaffold a production folder")
    s.add_argument("title"); s.add_argument("--slug")
    s.add_argument("--deliver", default="master-16x9", help="comma list of delivery presets")
    s.add_argument("--loudness", default="web-social"); s.add_argument("--test", action="store_true")
    sub.add_parser("list", help="list productions with stage and claim")
    sub.add_parser("status", parents=[pp], help="show one production")
    s = sub.add_parser("claim", parents=[pp], help="take the production for this bot (FW_BOT)")
    s.add_argument("--note", default=""); s.add_argument("--force", action="store_true")
    s = sub.add_parser("release", parents=[pp]); s.add_argument("--note", default="")
    s = sub.add_parser("stage", parents=[pp], help="move along the arc"); s.add_argument("stage", choices=production.ARC)
    s = sub.add_parser("baton", parents=[pp], help="write a handoff note to another bot/role")
    s.add_argument("--to", required=True); s.add_argument("summary")
    s = sub.add_parser("testclip", help="generate a labelled synthetic test clip")
    s.add_argument("out", type=Path); s.add_argument("--seconds", type=float, default=0)
    s = sub.add_parser("intake", parents=[pp], help="copy + seal + probe + log source media")
    s.add_argument("files", nargs="+", type=Path); s.add_argument("--source", required=True)
    s.add_argument("--license", required=True); s.add_argument("--note", default="")
    s.add_argument("--synthetic", action="store_true")
    s = sub.add_parser("spec", help="ffprobe spec card (json + md)"); s.add_argument("file", type=Path)
    s.add_argument("--out", type=Path, default=Path("."))
    s = sub.add_parser("listen", parents=[pp], help="transcribe to SRT/VTT/words.json")
    s.add_argument("file", type=Path); s.add_argument("--model", default="base.en"); s.add_argument("--lang", default="en")
    s.add_argument("--prompt", help="spelling hints for names/jargon")
    s.add_argument("--out", type=Path)
    s = sub.add_parser("captions", help="SRT -> styled ASS for a frame size")
    s.add_argument("srt", type=Path); s.add_argument("--preset", default="master-16x9")
    s.add_argument("--style"); s.add_argument("--out", type=Path)
    s = sub.add_parser("burn", help="burn an ASS file into a video"); s.add_argument("video", type=Path)
    s.add_argument("ass", type=Path); s.add_argument("out", type=Path)
    s = sub.add_parser("sound", help="measure or tune loudness")
    ss = s.add_subparsers(dest="action", required=True)
    m = ss.add_parser("measure"); m.add_argument("file", type=Path); m.add_argument("--profile", default="web-social")
    m.add_argument("--out", type=Path, default=Path("."))
    t = ss.add_parser("tune"); t.add_argument("src", type=Path); t.add_argument("out", type=Path)
    t.add_argument("--profile", default="web-social")
    s = sub.add_parser("stills", help="PNG stills + contact sheet"); s.add_argument("video", type=Path)
    s.add_argument("--count", type=int, default=6); s.add_argument("--at", help="comma list of seconds")
    s.add_argument("--out", type=Path, default=Path("stills"))
    s = sub.add_parser("render", parents=[pp], help="render a numbered cut for a delivery preset")
    s.add_argument("src", type=Path); s.add_argument("--preset", required=True)
    s.add_argument("--srt", type=Path); s.add_argument("--style"); s.add_argument("--loudness")
    s.add_argument("--cut", type=int); s.add_argument("--note", default="")
    s = sub.add_parser("proof", parents=[pp], help="build the proof pack (QA report) for a cut")
    s.add_argument("cut", nargs="?"); s.add_argument("--stills", type=int, default=6)
    s = sub.add_parser("handover", parents=[pp], help="gather cuts + proof into handover/ (never publishes)")
    s.add_argument("cuts", nargs="*")
    s = sub.add_parser("demo", help="full pipeline on a synthetic clip"); s.add_argument("--slug", default="demo-test-signal")
    s.add_argument("--model", default="base.en")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        c = a.cmd
        if c == "doctor":
            text, ok = doctor.report(); print(text); return 0 if ok else 2
        if c == "new":
            production.new(a.title, a.slug, a.deliver.split(","), a.loudness, a.test)
        elif c == "list":
            print("\n".join(production.list_all()) or "(no productions)")
        elif c == "status":
            print(production.status(_prod(a)))
        elif c == "claim":
            production.claim(_prod(a), a.note, a.force)
        elif c == "release":
            production.release(_prod(a), a.note)
        elif c == "stage":
            production.set_stage(_prod(a), a.stage)
        elif c == "baton":
            production.baton(_prod(a), a.to, a.summary)
        elif c == "testclip":
            media.testclip(a.out, a.seconds)
        elif c == "intake":
            media.intake(_prod(a), a.files, a.source, a.license, a.note, a.synthetic)
        elif c == "spec":
            p = media.spec_card(a.file, a.out); print((a.out / f"{a.file.name}.md").read_text()); say(f"json: {p}")
        elif c == "listen":
            out = a.out
            if out is None:
                try:
                    out = _prod(a).bench / "captions"
                except FwError:
                    out = Path(".")
            print(json.dumps(captions.listen(a.file, out, a.model, a.lang, a.prompt), indent=2))
        elif c == "captions":
            p = render.delivery(a.preset)
            out = a.out or a.srt.with_suffix(f".{a.preset}.ass")
            captions.styled_ass(a.srt, out, p["width"], p["height"], a.style or p["caption_style"]); say(f"ass: {out}")
        elif c == "burn":
            if a.out.exists():
                raise FwError(f"{a.out} exists — pick a new versioned name")
            captions.burn(a.video, a.ass, a.out)
        elif c == "sound":
            if a.action == "measure":
                card = sound.sound_card(a.file, a.profile, a.out)
                print((a.out / f"{a.file.name}.sound.md").read_text())
                return 0 if card["verdict"]["pass"] else 3
            if a.out.exists():
                raise FwError(f"{a.out} exists — pick a new versioned name")
            sound.tune(a.src, a.out, a.profile)
        elif c == "stills":
            at = [float(x) for x in a.at.split(",")] if a.at else None
            print(json.dumps(media.stills(a.video, a.out, a.count, at), indent=2))
        elif c == "render":
            render.render(_prod(a), a.src, a.preset, a.srt, a.loudness, a.cut, a.style, a.note)
        elif c == "proof":
            proof.proof(_prod(a), a.cut, a.stills)
        elif c == "handover":
            handover(_prod(a), a.cuts or None)
        elif c == "demo":
            demo(a.slug, a.model)
        return 0
    except FwError as e:
        print(f"[fw] error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
