# Memory and routines

Grok Bots remember across turns, share a computer, and can run scheduled routines.
Framewright splits what goes where so that nothing important lives only in one bot's head.

## Bot memory vs. project files

| put it in **bot memory** | put it in the **production folder** |
|---|---|
| The user's standing preferences (pace, caption look, "always -14 LUFS for reels") | Anything about one production: brief, plan, decisions |
| Where things are: "Cafe reel lives at productions/cafe-launch-reel, now at Polish" | Every asset's source and licence (ledger) |
| Standing tolls the user granted *in general* ("free stock from Pexels is fine"), with the date | Each specific toll asked and answered (`tolls.md`) |
| Lessons learned across jobs ("AAC at 160k overshoots TP by about 0.3 dB, keep 0.6 dB margin") | Review notes with timecodes |
| Which bot usually wears which hat | Batons between bots |

Rules of thumb:
- **Memory holds pointers and preferences. Files hold facts and evidence.**
- At the start of a turn, read `production.json`, the latest baton, and `review-notes.md` before acting.
  Don't rely on remembering what the cut looked like.
- At the end of a turn, update the stage, release or keep the claim on purpose, and write what's next in a
  baton or `decisions.md`.
- Don't store secrets, card numbers or tokens in memory or in the repo.

## Routines (scheduled or recurring checks)

Routines are good for watching and reminding. They are not for publishing. Suggested routines, which are
only created when the user asks:

| routine | cadence | what it does | never does |
|---|---|---|---|
| **Render queue sweep** | every 30 min while a production is in Polish | `fw status` across productions; flags cuts without proof packs | renders on its own |
| **Review nudge** | daily at the user's chosen time | if a handover package is older than 48 h with no reply, sends one gentle reminder to the user | messages anyone but the user |
| **Stale claim check** | daily | `fw list`; flags claims older than 12 h to the holder or Compass | breaks claims |
| **Doctor** | weekly, or after any box change | `bin/setup.sh --check`; reports changes in tool versions | installs or upgrades |
| **Disk watch** | daily | warns when free space < 20 GB, listing the largest `bench/` folders | deletes anything |

A routine's report should link the evidence (paths to proof packs and stills), as any other report would.
