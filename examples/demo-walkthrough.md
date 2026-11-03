# Demo walkthrough: `fw demo`

`fw demo` creates `productions/demo-test-signal/` and runs the whole arc on **synthetic test material**:

1. `new`: scaffolds the folder, templates and manifest (`test_material: true`).
2. `claim`: the bot (`FW_BOT`) holds the production.
3. `testclip`: ffmpeg `testsrc2` (1920×1080, 30p) with "SYNTHETIC TEST MATERIAL" burned on screen,
   a quiet 220 Hz bed, and a Piper voice line (if Piper and a voice are installed). The mix is about −21 LUFS on purpose,
   so loudness tuning has real work to do.
4. `intake`: the clip is copied, hashed, sealed read-only and logged with source and licence (CC0 / own work).
5. `listen`: faster-whisper base.en writes SRT/VTT/words JSON with a spelling hint for "Framewright".
6. `render` ×3: cut `c001` for master-16x9, reel-9x16 (blur-pad, reel-center captions) and square-1x1,
   each normalized to web-social (−14 LUFS, ≤ −1 dBTP) with captions burned in.
7. `proof` ×3: proof pack per cut with automated checks, a spec card, a sound card, 6 stills and a contact sheet.
8. `handover`: `handover/package_<time>/HANDOVER.md` plus copies. Nothing is uploaded.
9. `release`: the claim is freed.

Then open, for example:
- `productions/demo-test-signal/proof/c001/demo-test-signal_c001_reel-9x16.proof.md`
- `productions/demo-test-signal/proof/c001/stills/demo-test-signal_c001_reel-9x16_sheet.jpg`

Re-running `fw demo` reuses the production and the sealed clip, and renders the next cut number (`c002` …).
Delete the demo folder only if you made it. `chmod -R u+w` is needed first because intake is sealed.
