# Setup on the shared box

All of the user's Grok Bots share one persistent Linux machine, while each bot has its own desktop.
Anything installed here is visible to every bot, so setup is written to be **idempotent and polite**:
it reuses what's already there, takes a lock while installing, and never removes anything.

## Layout on the box

```
/workspace/video-studio/
  .venv/                 shared Python venv (all bots)
  models/whisper/        faster-whisper model cache (HF layout)
  models/piper/          Piper voices (.onnx + .json)
  grok-video-studio/     this repo
    productions/<slug>/  one folder per production
  _smoketest/ ...        other bots' scratch: not ours, don't touch
```

Override any of these with `FW_STUDIO`, `FW_VENV`, `FW_MODELS` or `FW_PRODUCTIONS`.

## Steps

```bash
cd /workspace/video-studio/grok-video-studio
bin/setup.sh --check     # doctor only, installs nothing
bin/setup.sh             # reuse/create venv, pip-install missing pinned extras, doctor
bin/setup.sh --models    # also fetch whisper base.en + piper en_US-lessac-medium if absent (free)
```

What the doctor checks:

- **Required:** `ffmpeg`/`ffprobe` with the `ass`, `loudnorm`, `ebur128`, `drawtext`, `blackdetect`,
  `freezedetect`, `silencedetect`, `tile` and `boxblur` filters, the `libx264` encoder, and Python ≥ 3.10.
- **Optional:** venv in use, node, git, gh, a whisper engine and the PyAV pin, Piper, Pillow, models,
  caption fonts (Inter, Poppins), and at least 10 GB of free disk.

Exit code `0` means every required tool is present. `2` means something required is missing.

## Pins (verified Nov 2026)

| package | pin | why |
|---|---|---|
| faster-whisper | 1.2.1 | CPU int8 transcription with word timestamps |
| av (PyAV) | 15.1.0 | newer PyAV (16+ / 19) breaks faster-whisper 1.2.1 audio decoding |
| piper-tts | 1.8.0 | offline TTS, used only for the demo's voice line |
| pillow | ≥10 | optional image work |

The core CLI needs **no** Python packages beyond the standard library.

## System packages

apt on this box may be unavailable (proxy errors) and is a shared-machine change, so **ask the user before
installing system packages**. Everything Framewright needs works with ffmpeg plus Python. Where you'd
reach for sox or ImageMagick, use ffmpeg filters or Pillow instead.

## Node

Node is available, but Framewright doesn't need it. Use it for Loom work such as HTML/Canvas/Lottie-style UI motion
rendered to frames or video, and then intake the render like any other asset (with `--source "Loom build: <path>"`).

## Troubleshooting

- `ass` filter missing → ffmpeg was built without libass; captions can still be delivered as SRT/VTT sidecars.
- Whisper wants to download → set `FW_MODELS` to the shared models dir, or run `bin/setup.sh --models` once.
- `piper` missing → the test clip falls back to a tone. Captions will then be empty, which is expected.
