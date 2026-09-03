# Plan: commtracker helper scripts

## Context

skill-commtracker currently re-derives EML parsing logic inline via `ctx_execute` each session.
This is slow, repeats the same Python every time, and pushes large data into Claude's context.
Three focused scripts extract the deterministic work; Claude keeps all judgment (what's
substantive, entry titles, body cleaning, CID substitution decisions).

---

## Placement

`~/.agents/scripts/commtracker/`

Three scripts, stdlib Python only (no pip installs), Python 3.14.

---

## Script 1 — `extract.py`

**Purpose:** Parse one EML, extract headers + body + MIME parts, save attachments to disk,
output a JSON summary to stdout. Claude reads the JSON; no raw EML bytes in context.

**Usage:**
```
python ~/.agents/scripts/commtracker/extract.py <eml-path> \
  [--attachments-dir <dir>]   # default: <eml-dir>/attachments/
  [--internal-domain <domain>] # e.g. apn.net.au — marks external senders
  [--slug <YYYYMMDD_HHMM>]    # override timestamp slug for file naming
  [--save-signatures]          # default: off — skip Outlook-*.png + UUID-named images
```

**Output (stdout JSON):**
```json
{
  "date_iso": "2026-04-13T00:21:41+00:00",
  "date_human": "Monday, 13 April 2026 12:21 AM UTC",
  "slug": "20260413_0021",
  "from": "Malik Ahmad",
  "from_external": false,
  "to": [{"name": "Stu Guzzardi", "external": false}],
  "cc": [],
  "subject": "Re: URGENT ACTION REQUIRED...",
  "body_text": "...(plain text, disclaimers stripped)...",
  "attachments": [
    {
      "original_filename": "image001.png",
      "saved_filename": "20260413_0021-image001.png",
      "saved_path": "/path/to/attachments/20260413_0021-image001.png",
      "content_type": "image/png",
      "size_bytes": 10718,
      "cid": "image001.png@01DC60AB.A3146850",
      "is_image": true,
      "is_signature": false
    }
  ],
  "signature_images_skipped": 36
}
```

**Signature detection logic** (skip by default):
- Filename matches `Outlook-[a-z0-9]{8}\.png` → Outlook modern signature chrome
- Filename is a bare UUID (`[0-9a-f-]{36}\.png`) → Teams/Outlook avatar tile
- Size ≤ 200 bytes → spacer/tracker pixel

**Disclaimer stripping** (mechanical, in the script):
- Lines starting with: `DISCLAIMER`, `CONFIDENTIAL`, `This email and any files transmitted`
- Trailing signature block heuristic: first line containing only phone/fax pattern after body

**Body text preference:** `text/plain` over `text/html`. If HTML only, strip tags.

---

## Script 2 — `reconcile.py`

**Purpose:** Given a `communications/` directory, compare EML files against entries in
`communications-tracking.md` and report any EML files not yet tracked.

**Usage:**
```
python ~/.agents/scripts/commtracker/reconcile.py <communications-dir>
```

**Output (stdout):**
```
Tracker: communications-tracking.md (15 entries, last: Email 15 - 20260413_0853)

UNTRACKED (1):
  Stu Guzzardi sent a message.eml
    Date:    Wed, 08 Apr 2026 21:31:39 +0000 → 20260409_0731 AEST
    Subject: Stu Guzzardi sent a message
    → Already covered? Tracker has Teams 1 - 20260409_0731 (date match)

ALL EML FILES ACCOUNTED FOR
```

**Match logic:**
- Extract date slug from each EML
- Check if any entry in the tracker contains that slug
- Report: confirmed match / date match / unmatched / no tracker found

---

## Script 3 — `toc.py`

**Purpose:** Regenerate the `## Contents` TOC section in a tracker file from its `## Email N`
and `## Teams N` headings. Eliminates manual anchor calculation.

**Usage:**
```
python ~/.agents/scripts/commtracker/toc.py <tracker-file>
  [--update]   # rewrite the Contents section in-place (default: print diff to stdout)
```

**Output (--update):** Rewrites only the `## Contents` block between the first `## Contents`
heading and the first `---` separator. Preserves everything else unchanged.

**Anchor generation:** GitHub-flavored Markdown: lowercase, spaces→hyphens, strip
non-alphanumeric except hyphens. Matches GFM exactly.

---

## Script 4 — `__init__.py` (empty)

Makes `commtracker/` a package for future `import commtracker.extract` use if needed.

---

## Files to create

```
~/.agents/scripts/commtracker/
  __init__.py          (empty)
  extract.py
  reconcile.py
  toc.py
  README.md            (usage reference for all three scripts)
```

---

## SKILL.md update

After scripts are in place, add a **Helper scripts** section to both skill-commtracker SKILL.md
files (authoring + installed) documenting the scripts and when to use them instead of inline
`ctx_execute`. Do not remove the inline fallback — scripts are preferred but ctx_execute remains
the fallback for one-off sessions without the scripts.

---

## Permanent plan save

Save this plan to:
`/Volumes/Data/_ai/_skills/skills_stuff/governance/plans/commtracker-scripts-20260422.md`

---

## Verification

```bash
# Extract test
python ~/.agents/scripts/commtracker/extract.py \
  "/Volumes/Data/_ai/_project/project_stuff/apn/aurukun-fni/communications/FW_ Aurukun Trial - First Nation Initiative [Commercial - Anyone].eml" \
  --internal-domain apn.net.au \
  --attachments-dir /tmp/test-attachments/

# Reconcile test
python ~/.agents/scripts/commtracker/reconcile.py \
  /Volumes/Data/_ai/_project/project_stuff/me/of-si/communications/

# TOC test
python ~/.agents/scripts/commtracker/toc.py \
  /Volumes/Data/_ai/_project/project_stuff/me/of-si/communications/communications-tracking.md
```

Expected: extract outputs valid JSON with 7 attachments (images 1-7) + 36 signatures skipped;
reconcile reports all EML accounted for; toc prints unchanged TOC (already correct).
