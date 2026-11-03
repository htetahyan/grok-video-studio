# Captions

- **Transcribe locally** with `fw listen` (faster-whisper base.en by default, which is free and runs on CPU). Pass names
  and jargon with `--prompt "Htet, Framewright"`, since it fixes spellings far more often than not.
- **Check the low-confidence words** listed by `fw listen` (and in `*.words.json`). Correct the SRT by hand.
  The SRT is the source of truth; ASS files are generated from it for each preset.
- **Reading speed:** at most ~17 characters per second, 1–2 lines, and a 1–6 s cue duration.
  fw breaks cues at sentence ends, at commas after about 30 characters, at pauses over 0.6 s, and at 4 s.
- **Looks:** `lower-band` (Inter, boxed, lower third) for landscape and square; `reel-center` (Poppins bold,
  outlined, raised into the vertical safe zone at about 28% from the bottom) for 9:16, clear of platform UI.
- **Ship sidecars too** (`.srt`, `.vtt`) when the platform supports them. They're accessible and searchable.
- Captions must never cover faces, product shots or the key UI in a screen recording. Move them, or style a cue specially.
