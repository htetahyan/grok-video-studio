# Glossary

| term | meaning |
|---|---|
| **Framewright** | This toolkit's name, and the `framewright` Python package behind `fw`. |
| **Production** | One job in its own folder under `productions/<slug>/`. |
| **Arc** | The seven stages: Spark → Blueprint → Intake → Weave → Polish → Proof → Handover. |
| **Hat** | A responsibility a bot wears: Compass, Loom, Splicer or Witness. |
| **Compass** | The direction hat: brief, plan, the user relationship, tolls and handover. |
| **Loom** | The made-elements hat: titles, UI motion, caption looks, brand graphics. |
| **Splicer** | The real-footage hat: cutting, sound, captions, renders. |
| **Witness** | The independent QA hat: proof packs and sign-off. |
| **Intake** | Both the stage and the folder: originals copied in and sealed read-only. |
| **Sealed** | Read-only and hashed. A sealed file is never modified. |
| **Bench** | Scratch space inside a production for intermediates. |
| **Cut / cNNN** | A numbered creative revision, rendered per preset; never overwritten. |
| **Preset** | A delivery format in `presets/delivery.json` (master-16x9, reel-9x16, square-1x1, review-720p). |
| **Sound profile** | A loudness target in `presets/loudness.json` (web-social, podcast-voice, broadcast-r128 …). |
| **Spec card** | ffprobe facts about a file, as JSON plus a markdown table. |
| **Sound card** | Measured integrated LUFS, true peak and LRA against a sound profile, with PASS/FAIL. |
| **Contact sheet** | A grid of timestamped frames, so a cut can be seen at a glance. |
| **Proof pack** | Spec card + sound card + stills + contact sheet + automated checks + the Witness checklist. |
| **Ledger** | `ledger/`: provenance.jsonl, tolls.md, decisions.md, batons/. |
| **Provenance** | Where an asset came from, its licence, its hash, and how it was made. |
| **Toll** | An action that needs the user's explicit yes: spend, send, publish, destroy, licence, shared-box change. |
| **Claim** | A note in `production.json` saying which bot is writing to a production right now. |
| **Baton** | A handoff note from one bot or hat to another. |
| **Handover** | The final stage: a package for the user to review. Never a publish. |
| **Test material** | Synthetic media (e.g. `fw testclip`), always labelled on screen and in the ledger. |
| **LUFS / dBTP / LRA** | Loudness units relative to full scale (integrated), true-peak decibels, loudness range. |
