---
name: skill-commtracker
description: "Thread emails/Teams messages/transcripts into a markdown comms tracker."
metadata:
  short-description: Extract comm data from email/Teams and maintain a markdown thread tracker
---

# skill-commtracker — Communication Thread Tracker

## Use When

Invoke for any of:
- User provides a raw `.eml` file path and wants it added to a thread tracker
- User pastes email text and wants it logged
- User has a Teams message/notification to add to a thread
- User points to a `teams-messages.md` staging file with one or more messages to process
- User wants to create a new `communications-tracking.md` for a project
- User wants to reconcile communications source files against an existing thread tracker

**Do not invoke** for interpreting, analyzing, or strategizing on communications — that is project-specific work. This skill handles extraction and formatting only.

---

## Step 1 — Identify Source Type and Multi-Email Containers

| Signal | Source type |
|---|---|
| File path ending in `.eml` | EML file (single email) |
| File path ending in `.eml` AND filename starts with `conversations-` or `multi-` | **Multi-email container** — one file holding multiple embedded `.eml` attachments that should each become a separate entry in the thread tracker |
| Text block with `From:`, `To:`, `Subject:`, `Date:` header lines | Pasted email |
| File path ending in `teams-messages.md` (or similar staging file) | Teams staging file |
| User says "teams", "chat", or text from a Teams notification | Teams message (direct) |
| User provides a phone-call transcript/recording writeup | Call |
| User provides an in-person/meeting transcript or notes | Meeting |
| Anything else | Other — ask user for fields interactively |

If the source type is ambiguous, ask the user before proceeding.

**Multi-email container (`conversations-*.eml` / `multi-*.eml`):** When detected, the outer email body is discarded (it is typically a forwarding wrapper with no substantive content). Instead, process each embedded `.eml` attachment as its own email entry. The `extract.py` script names them `{slug}-01-*.eml`, `{slug}-02-*.eml`, etc. — run `extract.py` first to extract all embedded `.eml` files, then run `extract.py` again on each extracted `.eml` file individually to get its headers, body, and attachments for the thread tracker.

---

## Step 2 — Determine Thread File

1. Check if the user specified a thread file path explicitly. If yes, use it.
2. **Per-subdirectory threading:** If the source `.eml` file lives in a subdirectory of `communications/` (e.g. `communications/apn/`, `communications/vocus/`), the thread file belongs in that same subdirectory — use `communications/<subdir>/communications-tracking.md`. This keeps threads isolated per correspondence stream.
3. Check if the project has a `communications/communications-tracking.md` relative to the working directory. If yes, use it.
4. If no thread file exists yet, ask the user for:
   - Thread file path (suggest the appropriate path per rule 2)
   - Thread title (e.g. "Medical Examination Request Thread")
   - One-line description of what the thread tracks
   - Source file reference (e.g. the `.eml` filename or "pasted email")
   Then bootstrap a new thread file (see **New Thread Bootstrap** below).

---

## Step 3 — Extract Fields

### EML file

Read the file. Extract from MIME headers:
- `Date:` → parse to full human-readable date + time (e.g. `Thursday, February 26, 2026 1:29 AM`)
- `From:` → display name; if an internal domain is configured and the email address domain does NOT match it, append ` **[External]**` after the display name
- `To:` → display name(s); apply same external marking
- `Cc:` → display name(s) with external marking; omit field if empty
- `Subject:` → full subject line
- Body → decoded plain-text part (prefer text/plain over text/html)

**Internal domain configuration:** If the project specifies an internal domain (e.g. `apn.net.au`), preserve the email address only long enough to check the domain, then discard it. Mark any sender or recipient whose domain does not match as `**[External]**`. If no domain is configured, show display names only with no marking.

**Attachments and inline images:** After extracting headers and body, walk all MIME parts:

- **Attachments** — parts with `Content-Disposition: attachment`:
  - Filename: from `Content-Disposition: attachment; filename="..."` or `Content-Type: ...; name="..."`
  - Content: base64-decode the part body
  - Classify as: attachment

- **Inline images** — parts with `Content-Type: image/*` (regardless of Content-Disposition):
  - Filename: from Content-Type `name` param; if absent generate `inline-image-N.{ext}`
  - Content-ID: extract `cid:...` value if present (used for body CID substitution)
  - Content: base64-decode the part body
  - Classify as: inline image

For large EML files (>256KB): use `ctx_execute` with Python `email.parser.BytesParser` to decode MIME parts and extract attachment bytes — same approach as body extraction.

### Pasted email text

Parse header block from the top of the pasted text. Headers end at the first blank line. Extract same fields as above. Body is everything after the header block.

Attachments: user must supply attachment files manually. Note each as `[Attachment: filename — file not provided, add manually]`.

### Teams staging file

A `teams-messages.md` file contains one or more pre-formatted Teams messages. Standard entry format:

```markdown
## Message N

**Sender:** [Name]
**Date:** [YYYY-MM-DD HH:MM]
**Channel/Conversation:** [channel or DM context]

[message body]
```

Read the file. For each `## Message N` block:
- `**Sender:**` → From
- `**Date:**` → parse to `YYYYMMDD_HHMM` slug and human-readable date
- `**Channel/Conversation:**` → Subject
- Body → everything after the header block until the next `---` or `## Message`
- No To/Cc unless a `**To:**` field is present in the block

Process all messages in the file in sequence. If some messages are already in the tracker (slug match), skip them. Process only new ones.

Prefix the entry ID with `Teams` not `Email`.

### Teams message (direct)

Extract:
- Sender name
- Timestamp (convert to `YYYYMMDD_HHMM` slug)
- Channel or conversation name (use as Subject)
- Message body text

Prefix the entry ID with `Teams` not `Email`.

### Call / Meeting transcript

A phone call or in-person meeting, provided as a transcript file, pasted dictation, or the user's
own recollection. Extract:
- Date/time (may be approximate — see verbatim-vs-reported handling below)
- Medium: `Phone call` or `In-person meeting`
- Participants (names, not roles, unless roles are how the user refers to them)
- Body: the dialogue or summary as provided

Prefix the entry ID with `Call` (phone) or `Meeting` (in-person) — not `Email` or `Teams`.

**Verbatim transcript vs. reported speech — mark clearly which one this is:**
- If a full transcript exists (recording writeup, dictation), treat it as verbatim per ADR-001
  (no paraphrasing) and write it up as a normal dialogue entry.
- If no transcript exists and the user is recounting a call/meeting from memory, the entry is
  **reported speech, not verbatim**. Mark it explicitly: add a `**Status:** VERBAL_UNRECORDED —
  reported by [name] from memory; no transcript exists` line, and label the dialogue/summary
  section `**Reported account (not verbatim — [name]'s recollection):**` rather than presenting
  it as quoted dialogue. Do not upgrade a recollection into quoted speech.

**Long transcripts — cross-reference instead of full duplication:** if the source transcript is
long (as a rule of thumb, longer than roughly 150–200 lines, or clearly a full meeting/consultation
transcript rather than a short exchange), do not paste the entire transcript into the tracker
entry. Instead:
1. Keep the full transcript as its own file under `communications/` (reformatted per **Transcript
   source cleanup** below if needed).
2. In the tracker entry, write: a **Source** line pointing to the full file, a short set of **key
   verbatim extracts** (the handful of quotes that actually matter, per ADR-001), a **Key points**
   bullet summary, and a **Case note** giving strategic significance.
This keeps the tracker itself scannable while preserving the full record separately.

**Transcript source cleanup:** user-provided transcripts (dictated, exported from a recording
tool) often use plain-text conventions instead of markdown — unicode section dividers (e.g. `⸻`)
instead of `---`, and unlabelled `Speaker:` lines instead of bold. Before filing, reformat the
source file itself to standard markdown: `#`/`##` headers for sections, `**Speaker:**` for
turn labels, `---` for dividers. Preserve all wording exactly — this is formatting cleanup only,
never a content edit.

**Fact conflicts — stop and confirm, don't guess:** if a call/meeting transcript's stated date,
a name, or another detail conflicts with an already-tracked fact elsewhere in the project (a
different dated communication implies a different date, a name doesn't match a known person),
stop and ask the user to confirm before filing. Do not silently pick one version or infer which
is correct — get it wrong here and every downstream chronology/case-file entry inherits the error.

### Other

Ask the user to supply: date/time, sender, recipient(s), subject or topic, and body text.

---

## Step 4 — Clean the Body

Strip the following from the body before writing to the thread file:
- Legal disclaimers and confidentiality notices (lines starting with "DISCLAIMER", "CONFIDENTIAL", "This email and any files transmitted")
- Contact blocks / signature blocks (phone, address, company logo references)
- Raw base64 blobs (replaced by file references in Step 4.5)
- Quoted/forwarded prior messages when the full prior message is already in the thread (keep the most recent message only; note `[prior thread omitted — see earlier entries]` if trimmed)
- Excessive blank lines (collapse 3+ consecutive blank lines to 2)

**Keep:**
- The full substantive body text of the message
- Any inline blockquotes that add context not captured elsewhere
- Any explicit references to attachments (replace with `[Attachment: filename]`)

**CID substitution:** Replace `[cid:CONTENT-ID]` references in the body with a markdown image link
pointing to the saved file: `![filename](attachments/YYYYMMDD_HHMM-filename)`. Match by the
Content-ID extracted in Step 3. If no CID match is found, substitute with
`![inline image](attachments/YYYYMMDD_HHMM-inline-image-N.ext)`.

---

## Step 4.5 — Save attachments and inline images to disk

Skip entirely if no attachments or inline images were found in Step 3.

1. **Save path:** `communications/attachments/` relative to the thread file. Create the directory if it does not exist.
2. **Naming convention:** `{YYYYMMDD_HHMM}-{original-filename}` using the email timestamp slug.
   - Replace spaces in the original filename with hyphens.
   - If a collision exists (same name already in the folder), append `-2`, `-3`, etc.
3. **Write files:** decode the base64 part body and write each file to `attachments/{slug}-{filename}`.
4. **Build the attachments list** for use in the entry header (Step 6):
   - Images (`image/*`): `![{filename}](attachments/{slug}-{filename})` — renders inline
   - Non-image files: `[{filename}](attachments/{slug}-{filename})` — link only

---

## Step 5 — Assign Entry ID and Slug

1. Count existing entries in the thread file for the correct prefix (`Email`, `Teams`, `Call`, or
   `Meeting` — each type numbers independently). New entry = N+1 for that prefix.
2. Format the timestamp slug: `YYYYMMDD_HHMM` in 24-hour time from the extracted date (or
   `YYYYMMDD` alone if no reliable time is known — do not invent a time).
3. Generate a 5–7 word summary of the message content for the heading.

Example: `Email 3 - 20260226_1340 - Scope-limited medical details proposed`

**Newly-discovered communications that predate or interleave with the existing sequence:** when a
communication surfaces after the tracker is already built and numbered — an older foundational
document, or a second item on the same day as an already-numbered entry — do not renumber the
existing sequence to fit it in. Renumbering touches every cross-reference to those entries
elsewhere in the project (chronology, case file, discussion log, skill/scratchpad state) and is
error-prone. Instead:
- If it predates entry 1 of its type: number it `0` (e.g. `Meeting 0`), matching the `Email 0a` /
  `Email 0b` convention already used for pre-sequence items.
- If it is a second item of the same type on the same day as an existing entry, or otherwise
  needs to sit between two already-numbered entries without shifting them: append a letter
  suffix (e.g. `Meeting 0b` immediately after `Meeting 0`, `Email 12a` between `Email 12` and
  `Email 13`).
- Insert the new entry at its correct chronological position in the document (see Step 6) even
  though its number doesn't sort there numerically — the letter/zero suffix is what preserves
  correct ordering without a renumber.

---

## Step 6 — Insert Entry

Find the correct chronological position in the thread file (entries are ordered by timestamp slug, oldest first). Insert the new entry at the correct position.

Entry format:

```markdown
## [Entry ID] - [YYYYMMDD_HHMM] - [short summary]

**Date:** [Full human-readable date and time]
**From:** [Sender Name]
**To:** [Recipient Name(s)]
**Cc:** [CC Name(s)]
**Subject:** [Subject line]
**Attachments:** [filename1](attachments/slug-filename1), [filename2](attachments/slug-filename2)

[Cleaned body text — inline images appear as ![alt](attachments/...) where CID refs were]

---
```

**Call / Meeting entry format** (metadata differs — no From/To/Cc, no email Subject):

```markdown
## [Entry ID] - [YYYYMMDD_HHMM or YYYYMMDD] - [short summary]

**Date:** [Full human-readable date, and time if known]
**Medium:** [Phone call | In-person meeting]
**Participants:** [Name, Name, ...]
**Status:** [only if VERBAL_UNRECORDED — see Step 3]
**Source:** [only if cross-referencing a long transcript file rather than embedding it]

[Full dialogue if short/verbatim, OR: key verbatim extracts + Key points + Case note if long — see Step 3]

---
```

**Formatting rules — strictly follow these:**

- **No trailing spaces** on metadata lines (`**Date:**`, `**From:**`, etc.) — they are plain markdown, no line-break escape needed
- **Omit `**Cc:**`** if no CC recipients. **Omit `**Attachments:**`** entirely if there are no substantive attachments — do not write "None" or "None substantive"
- **Attachment links** must use markdown link syntax `[filename](path)` so the path is visible on hover. Do not use backtick-quoted plain text (`filename`) for attachment references
- **`**Attachments:**` placement** — this line goes in the entry header between `**Subject:**` and the body, not in a separate table or section at the bottom
- **Image paths** in `[cid:...]` substitutions must be relative to the thread file directory:
  - Wrong: `communications/attachments/slug-filename.png`
  - Correct: `attachments/slug-filename.png`
- **CID substitution** — replace `[cid:CONTENT-ID]` with `![alt text](attachments/slug-filename)` using the saved image, never with a text placeholder like `[Attachment: filename]`
- **Forwarded messages** — strip the full forwarded/quoted content; replace with `*[Prior thread omitted — see below for summary]*` then a concise bullet-point summary. Do not use subheadings like `### Forwarded`

---

## Step 7 — Update Contents TOC

At the top of the thread file, in the `## Contents` section, add (or insert in chronological order):

```markdown
- [Email N - YYYYMMDD_HHMM - short summary](#email-n)
```

Anchor format: lowercase, spaces → hyphens, remove special characters. E.g. `Email 3 - 20260226_1340 - Scope-limited medical details proposed` → `#email-3---20260226_1340---scope-limited-medical-details-proposed`.

**Special characters — how GFM slugging actually handles them** (verify against these, not just
"remove special characters" — this is where anchor mismatches most often happen):
- Punctuation with no letters either side (`:`, `,`, `;`, `"`, `'`, `(`, `)`) — removed entirely,
  **not** replaced with a hyphen. `"hard reset" meeting:` → `hard reset meeting` (single space
  where the colon was, since the colon sat between two words already separated by a space).
- `/` — removed with no replacement and no space inserted. `hours/attendance` → `hoursattendance`.
- `+` and em-dash `—` — removed, but since they're normally surrounded by spaces on both sides,
  removing just the character leaves a double space, which becomes a **double hyphen** in the
  anchor. `Stu + Martin` → `stu--martin`; `2026 — Title` → `2026--title`.
- Compute the anchor by hand for anything with this punctuation, then double-check it against an
  existing similarly-punctuated heading elsewhere in the same file if one exists — don't guess.

Verify the anchor matches what GitHub-flavored Markdown would generate from the heading text.

---

## New Thread Bootstrap

When creating a thread file from scratch, write:

```markdown
# [Thread Name]

Source: `filename-or-description`

[One-line description of what this thread tracks.]

## Contents

[entries will be added here]

---

```

Then proceed to insert the first entry as per Steps 5–7.

---

## Helper Scripts

Helper scripts at `scripts/` (relative to this skill):
Use these instead of inline `ctx_execute` when available. The `ctx_execute` fallback remains
valid for one-off sessions without the scripts.

### extract.py — use instead of inline ctx_execute for Step 3 + Step 4.5

```bash
python ~/.agents/scripts/commtracker/extract.py <eml-path> \
  [--attachments-dir <dir>]    # default: <eml-dir>/attachments/
  [--internal-domain <domain>] # e.g. apn.net.au
  [--save-signatures]          # include Outlook/Teams chrome (default: skip)
```

Outputs JSON to stdout: `date_iso`, `date_human`, `slug`, `from/to/cc`, `subject`,
`body_text` (disclaimers stripped), `attachments[]` (saved to disk), `signature_images_skipped`.

Claude reads the JSON and performs Steps 4–7 (body cleaning decisions, CID substitution,
entry title, tracker write). For EML files >256KB, use this script — it avoids pushing
raw base64 into context.

### reconcile.py — use for Step 2 reconciliation runs

```bash
python ~/.agents/scripts/commtracker/reconcile.py <communications-dir>
```

Compares `.eml` files in the folder against `communications-tracking.md`. Reports exact
matches, AEST-timezone matches, same-date candidates, and genuinely untracked files.

### toc.py — regenerate Contents TOC

```bash
python ~/.agents/scripts/commtracker/toc.py <tracker-file>          # preview
python ~/.agents/scripts/commtracker/toc.py <tracker-file> --update  # apply
```

Regenerates the `## Contents` block from `## Email N` / `## Teams N` headings using
correct GFM anchors. Run after adding a new entry instead of computing anchors manually.

---

## Project Integration

Projects that have a specific communications folder, preferred thread file path, or an internal domain can define a thin wrapper skill that sets defaults and delegates here. Example wrapper (project-local):

```markdown
# of-si-thread-sync

Default thread file: `communications/communications-tracking.md`
Default project context: of-si workplace HR matter
Internal domain: apn.net.au  ← senders/recipients on other domains marked [External]

Delegate all extraction, cleaning, and formatting to `skill-commtracker`.
```

The `internal domain` setting controls external sender highlighting. Without it, no marking is applied.

---

## Extraction Quality Check

Before writing to the thread file, verify:
- [ ] Date is unambiguous and in the correct format
- [ ] From/To/Cc are display names, not raw email addresses (unless no display name available)
- [ ] Body contains no disclaimer text, contact blocks, or raw base64 blobs
- [ ] Entry ID is sequential and correct for the prefix type
- [ ] TOC anchor will resolve correctly in rendered markdown
- [ ] Chronological position is correct relative to surrounding entries
- [ ] Attachments saved to `communications/attachments/` with correct `YYYYMMDD_HHMM-filename` naming
- [ ] CID references in body replaced with working markdown image links
- [ ] `**Attachments:**` line present in entry header when attachments exist; omitted when none
- [ ] For Call/Meeting entries: `**Status:** VERBAL_UNRECORDED` present if there is no transcript (reported speech, not quoted dialogue)
- [ ] For long transcripts: full text kept in its own source file, not duplicated into the tracker; tracker entry has a `**Source:**` pointer + key extracts + case note
- [ ] Any date/name in the source conflicts with an already-tracked fact? — confirmed with the user, not assumed

If any check fails, fix it before writing.
