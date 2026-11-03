"""Proof packs: evidence-backed QA reports for a rendered cut."""
from __future__ import annotations

import re
from pathlib import Path

from . import media, sound
from .render import delivery
from .util import FwError, Production, bot_name, ffmpeg, now, rel, save_json, say

WITNESS_ITEMS = [
    "Watched the full cut start to finish at 100% speed with sound on",
    "First and last frames are intentional (no flash frames, no stray black)",
    "Cuts land on motion or breath; no jump cuts unless chosen",
    "Captions match the spoken words, are readable, and stay inside the safe zone",
    "No clipped dialogue, pops, clicks, or music ending mid-phrase",
    "Faces, skin tones and product colors look natural (no plastic/synthetic look)",
    "Every asset in the ledger has a source and a licence; nothing unlicensed is visible or audible",
    "Brief success criteria are met (see brief.md)",
]


def _detect(video: Path) -> dict:
    res = ffmpeg(["-i", str(video), "-vf", "blackdetect=d=0.5:pix_th=0.10,freezedetect=n=-60dB:d=1.5",
                  "-af", "silencedetect=noise=-50dB:d=2", "-f", "null", "-"], quiet=True)
    err = res.stderr
    black = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)]
    freeze = [float(x) for x in re.findall(r"freeze_duration: ([\d.]+)", err)]
    silence = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", err)]
    return {"black_spans": black, "freeze_durations": freeze, "silence_durations": silence}


def _find_cut(prod: Production, ref: str | None) -> dict:
    cuts = prod.manifest().get("cuts", [])
    if not cuts:
        raise FwError("no cuts recorded yet — render one first")
    if ref is None:
        return cuts[-1]
    for c in cuts:
        if ref in (c["file"], Path(c["file"]).name, Path(c["file"]).stem):
            return c
    raise FwError(f"cut not found: {ref}")


def proof(prod: Production, cut_ref: str | None = None, stills_count: int = 6) -> dict:
    cut = _find_cut(prod, cut_ref)
    video = prod.root / cut["file"]
    stem = video.stem
    p = delivery(cut["preset"])
    outdir = prod.proof / f"c{cut['number']:03d}"
    spec = media.summarize(media.ffprobe_json(video))
    src_path = prod.root / cut["source"]
    src_spec = media.summarize(media.ffprobe_json(src_path)) if src_path.exists() else None
    card = sound.sound_card(video, cut["loudness_profile"], outdir) if spec.get("audio") else None
    det = _detect(video)
    shots = media.stills(video, outdir / "stills", count=stills_count)

    v, a = spec.get("video") or {}, spec.get("audio") or {}
    checks = []

    def check(name, ok, evidence, severity="block"):
        checks.append({"check": name, "pass": bool(ok), "evidence": evidence, "severity": severity})

    check("frame size matches preset", v.get("width") == p["width"] and v.get("height") == p["height"],
          f"{v.get('width')}x{v.get('height')} vs {p['width']}x{p['height']}")
    check("H.264 / yuv420p (plays everywhere)", v.get("codec") == "h264" and v.get("pix_fmt") == "yuv420p",
          f"{v.get('codec')} {v.get('pix_fmt')}")
    check("audio AAC 48 kHz stereo", a.get("codec") == "aac" and a.get("sample_rate") == 48000 and a.get("channels") == 2,
          f"{a.get('codec')} {a.get('sample_rate')} Hz {a.get('channels')} ch" if a else "no audio")
    if src_spec:
        d = abs(spec["duration"] - src_spec["duration"])
        check("duration holds vs. source", d <= 0.1, f"cut {spec['duration']:.3f}s / source {src_spec['duration']:.3f}s (Δ {d:.3f}s)", "warn")
    if card:
        m, pr = card["measured"], card["profile"]
        check(f"integrated loudness {pr['integrated']} ±{pr['tolerance_lu']} LUFS", card["verdict"]["integrated_ok"],
              f"{m['integrated_lufs']:.1f} LUFS")
        check(f"true peak ≤ {pr['true_peak']} dBTP", card["verdict"]["true_peak_ok"], f"{m['true_peak_dbtp']:.1f} dBTP")
    check("no black holes ≥0.5 s", not det["black_spans"],
          ", ".join(f"{s:.2f}-{e:.2f}s" for s, e in det["black_spans"]) or "none found")
    check("no frozen picture ≥1.5 s", not det["freeze_durations"],
          ", ".join(f"{x:.1f}s" for x in det["freeze_durations"]) or "none found", "warn")
    check("no dead air ≥2 s (−50 dB)", not det["silence_durations"],
          ", ".join(f"{x:.1f}s" for x in det["silence_durations"]) or "none found", "warn")
    check("captions burned (if planned)", bool(cut.get("captions")) or not prod.manifest().get("captions"),
          cut.get("captions") or "no captions on this cut", "warn")

    recs = prod.ledger_records()
    intake = [r for r in recs if r["kind"] == "intake"]
    missing = [r["file"] for r in intake if not r.get("source") or not r.get("license")]
    check("every intake asset has source + licence", not missing and intake,
          f"{len(intake)} asset(s) logged" + (f"; missing: {missing}" if missing else ""))
    synthetic = [r["file"] for r in intake if r.get("synthetic")]

    blocking = [c for c in checks if not c["pass"] and c["severity"] == "block"]
    status = "READY FOR WITNESS" if not blocking else "NOT READY"

    def relp(x):
        return rel(Path(x), outdir)

    md = [f"# Proof pack — {stem}", "",
          f"- Production: **{prod.manifest()['title']}** (`{prod.slug}`)",
          f"- Cut: `{cut['file']}` · preset **{cut['preset']}** ({p['label']})",
          f"- Generated: {now()} by `{bot_name()}`",
          f"- Automated verdict: **{status}** ({sum(c['pass'] for c in checks)}/{len(checks)} checks pass)"]
    if synthetic:
        md += ["", f"> **TEST MATERIAL:** contains synthetic source ({', '.join(synthetic)}). "
               "Not a deliverable; for pipeline verification only."]
    md += ["", "## Automated checks", "", "| | check | evidence |", "|---|---|---|"]
    for c in checks:
        icon = "PASS" if c["pass"] else ("FAIL" if c["severity"] == "block" else "WARN")
        md.append(f"| {icon} | {c['check']} | {c['evidence']} |")
    md += ["", media.spec_md(video.name, spec)]
    if card:
        md += [(outdir / f"{video.name}.sound.md").read_text()]
    md += ["## Stills", "", f"Contact sheet: ![contact sheet]({relp(shots['sheet'])})", ""]
    md += [f"- t={t:.3f}s ![]({relp(f)})" for t, f in zip(shots["times"], shots["stills"])]
    md += ["", "## Witness sign-off (human-eye review — tick only what you actually saw)", ""]
    md += [f"- [ ] {item}" for item in WITNESS_ITEMS]
    md += ["", "Witness: ____________  Verdict: ☐ pass ☐ fix-and-return  Notes → `review-notes.md`", "",
           "## Not decided here", "", "Publishing, posting, sending to clients, or deleting anything is a **toll** "
           "(see docs/tolls.md). This report never authorises those actions."]
    report = outdir / f"{stem}.proof.md"
    report.write_text("\n".join(md) + "\n")
    data = {"cut": cut, "status": status, "checks": checks, "spec": spec, "sound": card,
            "detect": det, "stills": shots, "report": str(report)}
    save_json(outdir / f"{stem}.proof.json", data)
    m = prod.manifest()
    for c in m.get("cuts", []):
        if c["file"] == cut["file"]:
            c["proof"] = rel(report, prod.root)
            c["proof_status"] = status
    prod.update(cuts=m["cuts"])
    prod.log("proof", cut=cut["file"], status=status, report=rel(report, prod.root))
    say(f"proof pack: {report}  [{status}]")
    return data
