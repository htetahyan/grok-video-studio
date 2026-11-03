# The arc: seven stages of a production

```
Spark ─► Blueprint ─► Intake ─► Weave ─► Polish ─► Proof ─► Handover
                         ▲         ▲        │         │
                         └─────────┴────────┴─ fix ◄──┘
```

Move the production along with `fw stage <name>`. The current stage is stored in `production.json` and
logged to the ledger. Skipping a stage is allowed only if `ledger/decisions.md` says why.

| stage | lead hat | goes in | comes out | gate to leave |
|---|---|---|---|---|
| **Spark** | Compass | the user's ask | `brief.md` filled in | user ticks "Agreed" on the brief |
| **Blueprint** | Compass + Splicer + Loom | brief | `blueprint.md`: beats, formats, sound plan, crew | plan matches brief; tolls listed |
| **Intake** | Splicer | camera files, recordings, music, VO, Loom renders | sealed `intake/`, spec cards, provenance, transcripts, `shot-log.md` | every asset has a source and licence |
| **Weave** | Splicer (+ Loom builds) | intake, blueprint | assembly in `bench/`, first numbered cut in `cuts/` | story reads end to end |
| **Polish** | Splicer + Loom | assembly | captions, sound at target, color, motion details; cut `cNNN` per preset | sound card PASS, captions checked |
| **Proof** | Witness | cut + evidence | `proof/cNNN/*.proof.md` signed or bounced | all blocking checks pass and Witness signs |
| **Handover** | Compass | signed cuts | `handover/package_*/HANDOVER.md` | user reviews; publishing is the user's call |

## The production folder

```
productions/<slug>/
  production.json     manifest: title, stage, claim, deliverables, loudness profile, cuts[]
  brief.md            Spark
  blueprint.md        Blueprint
  shot-log.md         Intake notes (Splicer)
  review-notes.md     notes from Witness and the user, each with a cut and timecode
  intake/             sealed originals (folder and files read-only)
  ledger/
    provenance.jsonl  one JSON line per event: intake, render, transcribe, proof, claim, baton…
    tolls.md          approvals asked and answered
    decisions.md      why we chose what we chose
    batons/           handoff notes between bots
  bench/              scratch: captions, generated clips, conforms, Loom builds, temp audio
  cuts/               <slug>_c001_<preset>.mp4, never overwritten
  proof/
    spec/             spec cards for intake media
    c001/             spec + sound cards, stills/, contact sheet, *.proof.md/json for cut 1
  handover/
    package_<time>/   copies of the chosen cuts + proof packs + HANDOVER.md
```

## Cut numbering

- A **cut number** is one creative revision. All presets rendered from the same revision share it
  (`c003_master-16x9`, `c003_reel-9x16`).
- Any change, however small, gets a new number. Old cuts stay put so review notes keep pointing at the right file.
- Clean up old cuts only with the user's yes. That's a toll, because it deletes.
