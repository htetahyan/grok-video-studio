# The crew: four hats and how bots share a production

A **hat** is a responsibility, not a bot. One bot can wear every hat on a small job. On a bigger job,
coordinating bots each take a hat. The only hard rule is **the bot that rendered a cut shouldn't be its only
Witness** whenever a second bot is available.

| hat | owns | typical outputs |
|---|---|---|
| **Compass** | Direction and the relationship with the user: brief, blueprint, priorities, tolls, handover | `brief.md`, `blueprint.md`, `tolls.md`, `HANDOVER.md` |
| **Loom** | Made elements: titles, lower thirds, end cards, UI motion, caption looks, brand kit | renders in `bench/loom/` → intake as assets, caption style presets |
| **Splicer** | Real footage: selects, assembly, timing, sound mix to target, captions, reframes, renders | `shot-log.md`, `cuts/cNNN_*`, sound cards |
| **Witness** | Independent QA: runs `fw proof`, watches the cut, ticks only what it saw, bounces with timecodes | `proof/cNNN/*.proof.md`, `review-notes.md` |

## Coordination on one shared box

1. **Claim before you write.** `FW_BOT=<name> fw claim -p <slug> --note "polishing c004"`.
   Commands that write (`intake`, `render`, `stage`) refuse while another bot holds a fresh claim (< 12 h).
   A stale claim produces a warning, and you leave a note in `decisions.md`.
2. **One writer at a time per production.** Several productions can run in parallel. Within one production,
   work in turns, or keep Loom's work in `bench/loom/` and intake it when it's ready.
3. **Hand off with a baton.** `fw baton -p <slug> --to Witness "c004 ready, focus on captions 00:12–00:20"`
   writes `ledger/batons/<time>_<from>_to_<to>.md` from the template. Fill in the "What I need" section, then
   `fw release`. The receiver reads the baton and runs `fw claim`.
4. **Talk through files, not memory.** Whatever the next bot needs goes in the production (baton, decisions,
   review notes). Bot memory holds pointers and preferences (see memory-and-routines.md).
5. **The user is the only tie-breaker.** If two hats disagree, for example Witness bounces and Splicer thinks
   it's fine, Compass puts the question to the user with stills or timecodes for both sides.

## A typical multi-bot run

```
Compass (Video Studio bot)  Spark + Blueprint with the user → baton → Splicer
Splicer (Video Studio bot)  intake, listen, weave, polish → render c001 (3 presets) → baton → Witness
Loom    (Design bot)        builds end card + lower-third in bench/loom → intake → baton → Splicer
Witness (Review bot)        fw proof each cut, watches, signs or bounces with review-notes → baton → Compass
Compass                     fw handover → tells the user where the package is; waits for their call
```
