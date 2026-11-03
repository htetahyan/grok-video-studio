# Motion, brand films and UI motion (Loom)

- **Build outside, intake inside.** Loom builds titles, end cards and UI animations (HTML/Canvas via Node,
  ffmpeg drawtext/overlay, or image sequences from Pillow) in `bench/loom/`. Finished renders are intaken
  with `--source "Loom build: bench/loom/<file>, <tool>"` and a licence for every font and logo.
- **Motion has a job.** It should reveal, guide or connect. Ease in and out (no linear moves), hold
  readable text for at least reading time plus 0.5 s, and keep a consistent motion vocabulary across the piece.
- **UI motion from real product:** record the real UI at 2× resolution if you can, then crop, zoom and
  highlight. Don't fake screens unless the brief asks for concept work, and label concept work as such.
- **Brand kit:** colors, fonts and logo rules live in the production's `blueprint.md`, or in a shared
  `bench/loom/brand.md` that Loom maintains.
- Render masters at the delivery frame rate. Don't upsample 24p motion to 60p.
