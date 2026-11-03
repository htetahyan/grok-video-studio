# Color and look: keep it human

- Correct first (exposure, white balance, matching shots), then grade (mood). Most real footage only needs correction.
- Skin tones are the reference. If faces look orange, grey or waxy, back off.
- Avoid the synthetic tells: heavy skin smoothing, crushed blacks with glowing highlights, oversharpening halos,
  AI upscales on faces, and frame interpolation on handheld footage.
- Deliver tagged BT.709 for SDR web (fw render tags primaries, transfer and matrix).
- HDR sources (HLG/PQ) need a deliberate tone-map decision. Record it in `decisions.md`.
