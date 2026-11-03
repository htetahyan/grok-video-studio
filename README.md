# grok-video-studio — the Framewright toolkit

A footage-first video production kit for **Grok Bots** working on one shared Linux box.
It turns real camera footage, screen recordings and voice into reviewable masters, story reels,
captioned cuts, brand films and UI motion pieces, and every claim of "done" comes with evidence.

Framewright is built around four ideas:

1. **Real footage first.** Synthetic material is for tests and is labelled that way.
2. **Sound is measured.** Every cut has a sound card with integrated LUFS and true peak against a named profile.
3. **Proof over promises.** A cut isn't ready until its proof pack exists: spec card, sound card, stills, contact sheet and a checklist.
4. **The user holds the keys.** Bots never publish, never spend, and never delete source without an explicit yes (see [tolls](docs/tolls.md)).

## Quick start

```bash
git clone https://github.com/htetahyan/grok-video-studio.git /workspace/video-studio/grok-video-studio
cd /workspace/video-studio/grok-video-studio
bin/setup.sh                 # idempotent: reuse/create the shared venv, install extras, run the doctor
export FW_BOT=video-studio   # who you are; used for claims and the ledger
bin/fw demo                  # full pipeline on a synthetic test clip (≈30 s on CPU)
```

A real production:

```bash
bin/fw new "Cafe launch reel" --deliver reel-9x16,master-16x9 --loudness web-social
bin/fw claim -p cafe-launch-reel --note "first assembly"
bin/fw intake -p cafe-launch-reel ~/footage/*.mov --source "Htet, iPhone 15, 2026-11-01" --license "owned by user"
bin/fw listen -p cafe-launch-reel productions/cafe-launch-reel/intake/A001.mov --prompt "Htet, Framewright"
bin/fw render -p cafe-launch-reel <assembled.mp4> --preset reel-9x16 --srt productions/cafe-launch-reel/bench/captions/A001.srt
bin/fw proof  -p cafe-launch-reel          # proof pack for the newest cut
bin/fw handover -p cafe-launch-reel        # packages cuts + proof for the user; publishes nothing
```

## What's in the box

| path | what it is |
|---|---|
| `bin/setup.sh` | Setup + doctor. Safe to re-run. `--check` installs nothing, `--models` fetches free models. |
| `bin/fw` | CLI launcher (picks the shared venv automatically). |
| `framewright/` | The Python package behind `fw`. Uses only the stdlib plus ffmpeg; Whisper and Piper are optional extras. |
| `presets/` | `delivery.json` (frame formats), `loudness.json` (sound profiles), `captions.json` (caption looks). |
| `templates/` | Brief, blueprint, shot log, review notes, tolls ledger, decisions, baton (bot handoff), handover report. |
| `docs/` | How we work: setup, the Code, the arc, the crew, tolls, the proof checklist, memory & routines, glossary. |
| `craft/` | Short craft notes: cutting rhythm, sound, captions, reframing, motion, color. |
| `examples/` | A walkthrough of the demo production and a multi-bot example. |
| `productions/` | Where productions live (git-ignored apart from its README). |

## The `fw` commands

| command | does |
|---|---|
| `doctor` | Read-only report on tools, versions, filters, models, fonts and disk. |
| `new`, `list`, `status` | Create a production folder, list all of them, or show one. |
| `claim`, `release`, `stage`, `baton` | Shared-box coordination: hold a production, move it along the arc, hand off. |
| `testclip` | Make a labelled synthetic clip (testsrc2 plus an optional Piper voice line). |
| `intake` | Copy media in, seal it read-only, hash it, write a spec card, log provenance. |
| `spec` | ffprobe spec card (JSON + markdown). |
| `listen` | Transcribe to SRT, VTT and word-level JSON (faster-whisper, with openai-whisper as fallback). |
| `captions`, `burn` | Turn SRT into styled ASS for a frame size, then burn it in. |
| `sound measure`, `sound tune` | Sound card, or two-pass loudnorm to a profile. |
| `stills` | Full-resolution PNG stills plus a timestamped contact sheet. |
| `render` | Numbered cut for a preset: reframe, captions, measured loudness, then spec and sound cards. |
| `proof` | QA report for a cut: automated checks, evidence, and Witness sign-off boxes. |
| `handover` | Collects the chosen cuts and proof packs into `handover/` with a HANDOVER.md. |
| `demo` | Runs all of the above on synthetic test material. |

## Reading order for a new bot

1. [docs/CODE.md](docs/CODE.md): the seven tenets. They are short and they are not optional.
2. [docs/arc.md](docs/arc.md): the stages and the production folder.
3. [docs/crew.md](docs/crew.md): the four hats and how bots hand work to each other.
4. [docs/tolls.md](docs/tolls.md): what needs the user's yes.
5. [docs/proof-checklist.md](docs/proof-checklist.md): what "done" means.
6. [docs/memory-and-routines.md](docs/memory-and-routines.md): what to remember, and what to schedule.
7. [docs/glossary.md](docs/glossary.md): our words.

## License

MIT © 2026 Htet Ah Yan. Footage, music, fonts and models that you bring keep their own licences,
and the ledger records each one.
