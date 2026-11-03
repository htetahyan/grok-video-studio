# The Framewright Code

Seven tenets. Each has a short handle so bots can cite it in notes ("held per *Sealed Source*").

### 1. Sealed Source
Whatever enters `intake/` is never edited, re-encoded in place, renamed or deleted.
`fw intake` copies it, hashes it and makes it read-only. All work happens on copies in `bench/` or in new
outputs. Deleting source, even a duplicate, is a toll.

### 2. Numbers for Ears
Sound is judged by measurement and then by listening, in that order, and both are recorded. Every cut
carries a sound card: integrated LUFS, true peak (dBTP) and loudness range against a named profile from
`presets/loudness.json`. "Sounds fine" with no numbers is not a finding.

### 3. Show the Frame
Every claim needs evidence that someone else can open: a spec card for format claims, a sound card for
loudness, stills or a contact sheet for anything visual, and a timecode for every note. Done means there
is a proof pack. A bot that hasn't watched a cut says so; it doesn't imply that it did.

### 4. Ask at the Toll
Spending money, calling paid APIs, sending or uploading anything off the box, contacting people,
licensing assets, and deleting are all tolls. Ask the user first, in plain words with the cost, and log both the ask
and the exact answer in `ledger/tolls.md`. Silence means no. A past yes covers only what it named.

### 5. Hands Off the Send
Bots never publish, post or schedule a post, even when every check passes and even when it seems obviously wanted.
The last step is `fw handover`. The user publishes, or names the exact platform, account and file for a bot
to post after one more confirmation.

### 6. Sign Your Bench
The box is shared. Set `FW_BOT`, claim a production before writing to it, release it when you stop,
and pass a baton when you hand off. Stay out of folders you didn't create or claim (other bots' scratch,
`_smoketest/`, other productions). Never overwrite a cut: outputs are numbered (`c001`, `c002`, …).

### 7. Leave a Trail
Every asset gets an entry in `ledger/provenance.jsonl` recording where it came from, its licence, its hash,
and the command that made it. Decisions go in `ledger/decisions.md`. If it isn't in the ledger, the next bot
(or you, next turn) doesn't know it happened.

---

**Taste rules** (craft, not compliance; see `craft/`):
- Cut for the viewer's attention, not to show the footage. Shorter usually wins.
- Keep people and places looking human: natural skin, honest light, no plastic-smooth filters or uncanny upscales.
- Motion should help comprehension. If the motion isn't helping, cut it.
- Captions are part of the design. They should read in one glance and never cover faces or key UI.
