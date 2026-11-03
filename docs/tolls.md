# Tolls: the approval-gate policy

A **toll** is any step that costs money, leaves the box, can't be undone, or speaks for the user.
Bots pay a toll only with the user's explicit yes for **that specific action**.

## What counts as a toll

| toll | examples | never assume |
|---|---|---|
| **Spend** | paid stock footage/music, paid fonts, paid APIs (cloud transcription, generative video, upscalers), cloud render time | "it's only a few cents" |
| **Send** | uploading to a drive, emailing a link, messaging a client, posting to any platform, scheduling a post | "they said they liked it" |
| **Publish** | YouTube, Instagram, TikTok, X, a website, an ad account | ever. See *Hands Off the Send* |
| **Destroy** | deleting or overwriting source, deleting old cuts, clearing another bot's files, emptying caches others use | "it's a duplicate" |
| **Licence** | accepting terms for an asset, using a person's likeness or voice, using a brand's mark | "it's on the internet" |
| **Shared-box change** | system package installs (apt), changing the shared venv's major versions, editing other bots' setup | "it's needed for my job" |

Free things that stay on the box (local ffmpeg renders, local Whisper, local Piper, scratch files in your own
production) are **not** tolls. Do them without asking.

## How to ask

1. Do all the free, reversible work first, so the ask is concrete.
2. Ask in one message covering what, why, cost and alternatives, e.g.:
   *"To finish the reel I'd license 'Track X' from <site> for $15 (standard web licence). The free
   alternative is the royalty-free bed already in intake. Should I buy it?"*
3. Log it in `ledger/tolls.md` with the user's answer **verbatim** and the time.
4. A yes covers exactly what it named. A new price, a new platform or a new file means asking again.
5. Silence, "maybe" or "later" all mean no. Tell the user what you'll do in the meantime.

## The publishing line

`fw handover` is where every bot stops. It packages files and prints the path. Nothing in this toolkit
uploads, posts or sends anything, and adding that kind of automation needs the user's explicit request.
