#!/usr/bin/env bash
# Framewright setup + doctor. Idempotent: safe to run any time, by any bot.
#   bin/setup.sh            reuse/create the shared venv, install missing extras, run doctor
#   bin/setup.sh --check    doctor only (installs nothing)
#   bin/setup.sh --models   also fetch free models (whisper base.en, piper en_US-lessac-medium) if absent
# Env: FW_STUDIO (default: parent of repo), FW_VENV (default: $FW_STUDIO/.venv), FW_MODELS.
set -euo pipefail
REPO="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
STUDIO="${FW_STUDIO:-$(dirname "$REPO")}"
VENV="${FW_VENV:-$STUDIO/.venv}"
MODELS="${FW_MODELS:-$STUDIO/models}"
CHECK_ONLY=0; WANT_MODELS=0
for arg in "$@"; do
  case "$arg" in
    --check) CHECK_ONLY=1 ;;
    --models) WANT_MODELS=1 ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
  esac
done
say(){ printf '[setup] %s\n' "$*"; }

command -v ffmpeg >/dev/null || { say "ffmpeg missing: ask the user before installing system packages (sudo apt-get install ffmpeg)"; }
command -v python3 >/dev/null || { say "python3 missing"; exit 1; }

if [[ $CHECK_ONLY -eq 0 ]]; then
  # Shared box: one lock so two bots don't pip-install into the same venv at once.
  mkdir -p "$STUDIO"
  exec 9>"$STUDIO/.framewright-setup.lock"
  if ! flock -w 600 9; then say "another bot is running setup; try later"; exit 1; fi

  if [[ ! -x "$VENV/bin/python" ]]; then
    say "creating venv at $VENV"
    python3 -m venv "$VENV"
  else
    say "reusing venv at $VENV"
  fi
  missing=()
  while read -r line; do
    req="${line%%#*}"; req="$(echo "$req" | xargs)"; [[ -z "$req" ]] && continue
    name="${req%%[=<>]*}"
    want="$(echo "$req" | sed -n 's/.*==\(.*\)/\1/p')"
    have="$("$VENV/bin/python" -m pip show "$name" 2>/dev/null | awk '/^Version:/{print $2}')"
    if [[ -z "$have" || ( -n "$want" && "$have" != "$want" ) ]]; then missing+=("$req"); fi
  done < "$REPO/requirements.txt"
  if (( ${#missing[@]} )); then
    say "installing: ${missing[*]}"
    "$VENV/bin/python" -m pip install --quiet "${missing[@]}"
  else
    say "python extras already satisfied"
  fi

  if [[ $WANT_MODELS -eq 1 ]]; then
    mkdir -p "$MODELS/whisper" "$MODELS/piper"
    if ! ls "$MODELS/whisper" | grep -q 'faster-whisper-base.en'; then
      say "fetching whisper base.en (free, ~150 MB)"
      "$VENV/bin/python" -c "from faster_whisper import WhisperModel; WhisperModel('base.en', device='cpu', compute_type='int8', download_root='$MODELS/whisper')"
    fi
    if [[ ! -f "$MODELS/piper/en_US-lessac-medium.onnx" ]]; then
      say "fetching piper voice en_US-lessac-medium (free, MIT/CC-BY per voice card)"
      base="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium"
      curl -fsSL -o "$MODELS/piper/en_US-lessac-medium.onnx" "$base/en_US-lessac-medium.onnx"
      curl -fsSL -o "$MODELS/piper/en_US-lessac-medium.onnx.json" "$base/en_US-lessac-medium.onnx.json"
    fi
  fi
  flock -u 9
fi

PY="$VENV/bin/python"; [[ -x "$PY" ]] || PY=python3
FW_STUDIO="$STUDIO" FW_MODELS="$MODELS" PYTHONPATH="$REPO" "$PY" -m framewright doctor
