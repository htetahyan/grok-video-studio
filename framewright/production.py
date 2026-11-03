"""Production folders: scaffold, claim/release, stage, status, batons."""
from __future__ import annotations

import shutil

from .util import (PRODUCTIONS, TEMPLATES, FwError, Production, bot_name, now,
                   save_json, say, slugify)

ARC = ["spark", "blueprint", "intake", "weave", "polish", "proof", "handover"]

# template file -> where it lands inside a production
SEED = {
    "brief.md": "brief.md",
    "blueprint.md": "blueprint.md",
    "review-notes.md": "review-notes.md",
    "shot-log.md": "shot-log.md",
    "tolls.md": "ledger/tolls.md",
    "decisions.md": "ledger/decisions.md",
}


def new(title: str, slug: str | None = None, deliverables: list[str] | None = None,
        loudness: str = "web-social", test_material: bool = False) -> Production:
    slug = slugify(slug or title)
    root = PRODUCTIONS / slug
    if (root / "production.json").exists():
        say(f"production '{slug}' already exists — leaving it untouched")
        return Production(root)
    for d in Production.DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    for src, dst in SEED.items():
        target = root / dst
        if not target.exists():
            text = (TEMPLATES / src).read_text()
            text = text.replace("{{TITLE}}", title).replace("{{SLUG}}", slug) \
                       .replace("{{DATE}}", now()[:10]).replace("{{BOT}}", bot_name())
            target.write_text(text)
    manifest = {
        "slug": slug,
        "title": title,
        "created": now(),
        "created_by": bot_name(),
        "stage": "spark",
        "test_material": test_material,
        "deliverables": deliverables or ["master-16x9"],
        "loudness_profile": loudness,
        "claim": None,
        "cuts": [],
        "captions": None,
    }
    save_json(root / "production.json", manifest)
    prod = Production(root)
    prod.log("scaffold", note=f"production '{title}' created")
    say(f"new production at {root}")
    return prod


def claim(prod: Production, note: str = "", force: bool = False) -> None:
    prod.check_claim(force=force)
    prod.update(claim={"bot": bot_name(), "since": now(), "note": note})
    prod.log("claim", note=note)
    say(f"{bot_name()} now holds '{prod.slug}'")


def release(prod: Production, note: str = "") -> None:
    c = prod.manifest().get("claim")
    if c and c.get("bot") != bot_name():
        raise FwError(f"claim belongs to {c['bot']}; only they (or the user) may release it")
    prod.update(claim=None)
    prod.log("release", note=note)
    say(f"released '{prod.slug}'")


def set_stage(prod: Production, stage: str) -> None:
    if stage not in ARC:
        raise FwError(f"unknown stage '{stage}'. Arc: {' > '.join(ARC)}")
    prod.check_claim()
    old = prod.manifest().get("stage")
    prod.update(stage=stage)
    prod.log("stage", frm=old, to=stage)
    say(f"stage {old} -> {stage}")


def baton(prod: Production, to: str, summary: str) -> str:
    """Write a handoff note from this bot to another role/bot."""
    stamp = now().replace(":", "")[:15]
    path = prod.ledger / "batons" / f"{stamp}_{slugify(bot_name())}_to_{slugify(to)}.md"
    text = (TEMPLATES / "baton.md").read_text()
    text = (text.replace("{{FROM}}", bot_name()).replace("{{TO}}", to)
                .replace("{{DATE}}", now()).replace("{{SLUG}}", prod.slug)
                .replace("{{SUMMARY}}", summary))
    path.write_text(text)
    prod.log("baton", to=to, file=str(path.relative_to(prod.root)))
    say(f"baton written: {path}")
    return str(path)


def status(prod: Production) -> str:
    m = prod.manifest()
    lines = [f"{m['title']}  ({m['slug']})",
             f"  stage     : {m.get('stage')}   arc: {' > '.join(ARC)}",
             f"  claim     : {m['claim']['bot'] + ' since ' + m['claim']['since'] if m.get('claim') else 'free'}",
             f"  test clip : {'yes (synthetic test material)' if m.get('test_material') else 'no'}",
             f"  targets   : {', '.join(m.get('deliverables', []))} | sound {m.get('loudness_profile')}"]
    for c in m.get("cuts", []):
        lines.append(f"  cut c{c['number']:03d} {c['preset']:<12} {c['file']}  proof={c.get('proof','-')}")
    intake = [p.name for p in sorted(prod.intake.glob('*')) if p.is_file()]
    lines.append(f"  intake    : {len(intake)} file(s) {', '.join(intake[:5])}")
    return "\n".join(lines)


def list_all() -> list[str]:
    out = []
    if PRODUCTIONS.exists():
        for p in sorted(PRODUCTIONS.glob("*/production.json")):
            prod = Production(p.parent)
            m = prod.manifest()
            who = m["claim"]["bot"] if m.get("claim") else "free"
            out.append(f"{m['slug']:<28} {m.get('stage',''):<10} {who}")
    return out


def copy_to_handover(prod: Production, files: list) -> None:
    for f in files:
        shutil.copy2(f, prod.handover / f.name)
