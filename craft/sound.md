# Sound

## Measure, then listen
`fw sound measure <file> --profile <name>` writes a sound card. Profiles (presets/loudness.json):

| profile | integrated | true peak | use |
|---|---|---|---|
| web-social | −14 LUFS ±1 | ≤ −1 dBTP | YouTube, Reels, Shorts, TikTok, web |
| podcast-voice | −16 LUFS ±1 | ≤ −1 dBTP | spoken word |
| broadcast-r128 | −23 LUFS ±0.5 | ≤ −1 dBTP | EBU R128 (EU broadcast) |
| broadcast-a85 | −24 LUFS ±2 | ≤ −2 dBTP | ATSC A/85 (US broadcast) |
| cinema-quiet | −20 LUFS ±1 | ≤ −2 dBTP | screeners, festival, dynamic mixes |

## How fw tunes loudness
Two-pass `loudnorm` in linear mode: pass 1 measures, pass 2 applies one gain using the measured values,
so the mix's dynamics are preserved rather than pumped. The limiter aims **0.6 dB below** the ceiling
when the output is lossy (AAC), because encoding adds inter-sample overshoot. The demo's QA caught this:
a 160 kb/s AAC proxy came out at −0.8 dBTP against a −1.0 ceiling before the margin was added.

## Mixing guidance
- Dialogue is king: aim for dialogue-gated speech around the target, with music beds 12–18 dB under speech.
- Duck music under voice with gentle sidechain or keyframed volume, never hard cuts.
- Keep room tone under edits in dialogue so cuts don't "click to silence".
- High-pass voice around 80 Hz and remove hum before raising levels.
- Always listen to the start and end: music should finish on a phrase or fade on purpose.
