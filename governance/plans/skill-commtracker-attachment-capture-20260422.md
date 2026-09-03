# Plan: skill-commtracker — attachment and inline image capture

## Context

skill-commtracker currently strips inline image placeholders (`[image001.jpg]`, `[cid:...]`,
base64 blobs) and replaces attachment references with a plain `[Attachment: filename]` text.
The user wants the skill to actually capture attachments and inline images — extract them from
the EML, save to disk, and reference them properly in the thread tracker entry.

---

## What changes

Two files, identical content:
- `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-commtracker/SKILL.md` (authoring)
- `/Users/malik.ahmad/.claude/skills/skill-commtracker/SKILL.md` (installed)

No other files change.

---

## Changes per section

### Step 3 — Extract Fields (EML subsection) — add attachment detection

After extracting headers and body, also extract MIME parts:

**Attachments** — MIME parts with `Content-Disposition: attachment`:
- Filename: from `Content-Disposition: attachment; filename="..."` or `Content-Type: ...; name="..."`
- Content: base64-decode the part body
- Classify as attachment

**Inline images** — MIME parts with `Content-Type: image/*` (regardless of Content-Disposition):
- Filename: from Content-Type `name` param, or generate `inline-image-N.{ext}` if none
- Content-ID: extract `cid:...` value if present (used for body substitution)
- Content: base64-decode the part body
- Classify as inline image

For pasted email: user must supply attachment files manually. Note them as
`[Attachment: filename — file not provided, add manually]`.

---

### Step 4 — Clean the Body — replace strip with capture

Current rule strips image placeholders and replaces attachments with plain text.

New rule:
- Replace `[cid:CONTENT-ID]` references in body with markdown image link:
  `![filename](attachments/YYYYMMDD_HHMM-filename)` — matching by Content-ID
- If no CID match found, substitute with `![inline image](attachments/YYYYMMDD_HHMM-inline-image-N.ext)`
- Keep `[Attachment: filename]` as-is in body (it becomes a link in the Attachments section)
- Remove raw base64 blobs from body text (replaced by file references)

---

### New Step 4.5 — Save attachments and inline images to disk

After body cleaning, before assigning entry ID:

1. Determine save path: `communications/attachments/` relative to the thread file. Create if missing.
2. Naming convention: `{YYYYMMDD_HHMM}-{original-filename}` (slug from email timestamp, original name preserved)
   - If original filename contains spaces: replace with hyphens
   - If filename collision: append `-2`, `-3`, etc.
3. Write each decoded binary to `attachments/{slug}-{filename}` using the Write tool (base64-decoded bytes).
4. Build the attachments list for the entry:
   - Images: `![{filename}](attachments/{slug}-{filename})` — renders inline in markdown
   - Non-image files: `[{filename}](attachments/{slug}-{filename})` — link only
5. If no attachments or inline images found: skip this step entirely (no empty section).

For large EML files (>256KB): use `ctx_execute` with Python `email.parser.BytesParser` to decode
MIME parts and write attachment bytes — same approach used for body extraction.

---

### Step 6 — Insert Entry — add Attachments section to entry format

Updated entry format:

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

Omit `**Attachments:**` line if no attachments. Omit `**Cc:**` if no CC.

---

### Extraction Quality Check — add attachment checks

Add to checklist:
- [ ] Attachments saved to `communications/attachments/` with correct slug-filename naming
- [ ] CID references in body replaced with working markdown image links
- [ ] Attachments line present in entry header when attachments exist
- [ ] No raw base64 blobs remain in body text

---

## Execution order

1. Save this plan to permanent location: `/Volumes/Data/_ai/_skills/skills_stuff/governance/plans/skill-commtracker-attachment-capture-20260422.md`
2. Edit authoring SKILL.md
3. Copy identical change to installed SKILL.md
4. Verify no placeholder text (`<...>`) remains
