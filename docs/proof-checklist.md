# Proof checklist: what "done" means

A cut is **ready for the user** only when both halves below pass. `fw proof` runs the automated half and
writes `proof/cNNN/<cut>.proof.md` with the evidence inline. Witness does the human half.

## Automated (fw proof)

| check | blocking? | evidence written |
|---|---|---|
| Frame size matches preset | block | spec card |
| H.264 High, yuv420p | block | spec card |
| AAC 48 kHz stereo | block | spec card |
| Integrated loudness within profile tolerance | block | sound card |
| True peak ≤ profile ceiling | block | sound card |
| No black span ≥ 0.5 s | block | blackdetect spans |
| Every intake asset has a source and licence | block | ledger count |
| Duration within 0.1 s of source | warn | both durations |
| No frozen picture ≥ 1.5 s | warn | freezedetect |
| No dead air ≥ 2 s below −50 dB | warn | silencedetect |
| Captions burned if captions are planned | warn | ASS path |

Also produced every time: 6 full-resolution PNG stills, a 12-frame contact sheet with timestamps,
and JSON for every number.

## Human (Witness): tick only what you actually saw

- [ ] Watched the whole cut at 1× with sound on (if you can't play audio, say so and don't tick sound items)
- [ ] First and last frames are deliberate, with no flash frames
- [ ] Cuts land on action or breath; no accidental jump cuts
- [ ] Captions match the words (check low-confidence words in `*.words.json`), read in one glance,
      and stay clear of faces and key UI
- [ ] No clipped words, pops or clicks, and music doesn't end mid-phrase
- [ ] Faces, skin and product colors look natural; nothing looks synthetic or over-smoothed
- [ ] Every visible or audible asset is in the ledger with a licence
- [ ] The brief's success criteria are met (quote them)

## How to report "done" to the user

Include: the cut file path, the proof pack path, the verdict line, the sound numbers, and one or two stills.
If anything was skipped (no audio playback, no transcript), name it. Never round a WARN up to a PASS.
