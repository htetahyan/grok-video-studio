# PLAN — grok-video-studio (the Framewright toolkit)

A from-first-principles design for a video production toolkit operated by Grok Bots
on one shared, persistent Linux box. Nothing here is derived from any other "video kit";
names, layout, rules and workflow were invented for this repo.

## Core idea

A *production* is a self-contained folder. Raw media enters once, is sealed read-only,
and every later artifact is a numbered, re-creatable output with a written trail.
Bots never say "done" without a **proof pack** (spec card + sound card + stills + checklist).

## Names we chose

Roles (a single bot may wear several hats; a hat is a responsibility, not a process):
- **Compass**  — sets direction: brief, story, plan, gates with the user.
- **Loom**     — designs and builds made elements: titles, lower thirds, UI motion, caption styles.
- **Splicer**  — cuts real footage, mixes and measures sound, finishes, renders cuts.
- **Witness**  — independent QA: inspects evidence, signs or rejects the proof pack.

Stages (the "arc"):
1. **Spark**     — brief captured, success criteria agreed.
2. **Blueprint** — beat sheet / edit plan, formats, loudness profile picked.
3. **Intake**    — media copied in, sealed, probed, provenance logged.
4. **Weave**     — assembly and build of the cut.
5. **Polish**    — captions, sound to target, color, motion details.
6. **Proof**     — Witness reviews evidence; fixes loop back to Weave/Polish.
7. **Handover**  — reviewable package presented; user decides publishing.

House rules: **The Framewright Code** (docs/CODE.md), seven tenets with short handles:
Sealed Source · Numbers for Ears · Show the Frame · Ask at the Toll · Hands Off the Send ·
Sign Your Bench · Leave a Trail.

## Layout

```
grok-video-studio/
  README.md  PLAN.md  LICENSE  .gitignore
  bin/            setup.sh (idempotent setup + doctor), fw (CLI launcher)
  framewright/    Python package, single CLI: `fw <command>`
  presets/        delivery.json (frame formats), loudness.json (sound profiles), caption styles
  templates/      brief, blueprint, shot log, review notes, tolls, decisions, baton (bot handoff), handover report
  docs/           setup, CODE (standards), arc (stages), crew (multi-bot), tolls (approval gates),
                  proof checklist, memory & routines, glossary
  craft/          knowledge notes: cutting rhythm, sound, captions, motion, color, formats
  examples/       demo walkthrough, multi-bot session
  tests/          fast stdlib unit tests
  productions/    one folder per production (git-ignored except README and the demo skeleton)
```

Production folder:
```
productions/<slug>/
  production.json   manifest: title, stage, claim (owner bot + time), versions
  intake/           sealed originals (chmod a-w), never edited
  ledger/           provenance.jsonl, tolls.md (approvals), batons/, decisions.md
  bench/            scratch & intermediates (captions drafts, normalized audio, proxies)
  cuts/             numbered renders  <slug>_c001_<preset>.mp4 ...
  proof/            spec cards, sound cards, stills, contact sheets, proof report
  handover/         what the user reviews: chosen cut(s), stills, report links
```

## CLI (`fw`)
doctor · new · testclip · intake · spec · listen (transcribe) · captions · burn ·
sound (measure / tune) · stills · render (preset) · proof · claim / release · demo

Dependencies: Python stdlib + ffmpeg; optional faster-whisper (or openai-whisper) in `.venv`.
