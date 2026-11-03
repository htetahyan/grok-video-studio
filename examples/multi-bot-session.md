# Example: three bots, one reel

```bash
# Compass: Video Studio bot, with the user
export FW_BOT=video-studio
fw new "Cafe launch reel" --deliver reel-9x16,master-16x9
fw claim -p cafe-launch-reel --note "brief + blueprint"
#   fill brief.md with the user → user ticks Agreed → fill blueprint.md
fw stage -p cafe-launch-reel blueprint
fw baton -p cafe-launch-reel --to Loom "need end card + lower-third, brand colors in blueprint.md"
#   (Compass keeps the claim; Loom works only in bench/loom/ until handing back)

# Loom: Design bot
export FW_BOT=design-bot
#   builds bench/loom/endcard.mov with Node/ffmpeg
fw baton -p cafe-launch-reel --to Splicer "end card ready at bench/loom/endcard.mov (Inter, OFL)"

# Splicer: Video Studio bot again
export FW_BOT=video-studio
fw intake -p cafe-launch-reel ~/drop/*.mov --source "user's phone, 2026-11-01" --license "owned by user"
fw intake -p cafe-launch-reel productions/cafe-launch-reel/bench/loom/endcard.mov \
   --source "Loom build by design-bot" --license "own work; Inter font OFL"
fw stage -p cafe-launch-reel weave
#   assemble → bench/assembly_v1.mp4
fw listen -p cafe-launch-reel productions/cafe-launch-reel/bench/assembly_v1.mp4 --prompt "Htet"
#   fix low-confidence words in the SRT by hand
fw render -p cafe-launch-reel productions/cafe-launch-reel/bench/assembly_v1.mp4 --preset reel-9x16 \
   --srt productions/cafe-launch-reel/bench/captions/assembly_v1.srt
fw release -p cafe-launch-reel
fw baton -p cafe-launch-reel --to Witness "c001 reel ready"

# Witness: Review bot
export FW_BOT=review-bot
fw claim -p cafe-launch-reel --note "proof c001"
fw proof -p cafe-launch-reel
#   watch, tick boxes, write review-notes.md with timecodes → bounce or sign
fw release -p cafe-launch-reel
fw baton -p cafe-launch-reel --to Compass "c001 signed; 2 WARNs noted"

# Compass
export FW_BOT=video-studio
fw handover -p cafe-launch-reel
#   tell the user where HANDOVER.md is. Publishing is their call.
```
