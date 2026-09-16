# commtracker scripts

Helper scripts for the `skill-commtracker` workflow. Handle the deterministic parts
(parse, decode, save, reconcile); Claude handles the judgment parts (what's substantive,
entry titles, body editing, CID substitution decisions).

Python 3.14, stdlib only — no pip installs required.

---

## extract.py — Parse one EML to JSON

```bash
python ~/.agents/scripts/commtracker/extract.py <eml-path> \
  [--attachments-dir <dir>]    # default: <eml-dir>/attachments/
  [--internal-domain <domain>] # e.g. apn.net.au — marks external senders
  [--slug <YYYYMMDD_HHMM>]     # override timestamp slug for file naming
  [--save-signatures]          # include Outlook/Teams UI chrome (default: skip)
```

**Output (stdout):** JSON with `date_iso`, `date_human`, `slug`, `from`, `to`, `cc`,
`subject`, `body_text`, `attachments[]`, `signature_images_skipped`.

**Side effect:** Saves non-signature attachments/images to `--attachments-dir` using
the naming convention `{slug}-{filename}`. Creates the directory if needed.

**Signature detection (skipped by default):**
- `Outlook-[a-z0-9]{8}.png` — Outlook modern signature chrome
- UUID-named files (`xxxxxxxx-xxxx-...png`) — Teams/Outlook avatar tiles
- Files ≤ 200 bytes — spacer pixels / tracker GIFs

### Example

```bash
python ~/.agents/scripts/commtracker/extract.py \
  "/path/to/communications/FW_ Aurukun Trial.eml" \
  --internal-domain apn.net.au \
  --attachments-dir "/path/to/communications/attachments/"
```

---

## reconcile.py — Diff EML files vs tracker

```bash
python ~/.agents/scripts/commtracker/reconcile.py <communications-dir>
```

**Output:** Lists each `.eml` file and whether it's accounted for in
`communications-tracking.md`. Reports exact slug matches, same-date candidates,
and genuinely untracked files.

### Example

```bash
python ~/.agents/scripts/commtracker/reconcile.py \
  "/path/to/project/communications/"
```

---

## toc.py — Regenerate Contents TOC

```bash
python ~/.agents/scripts/commtracker/toc.py <tracker-file>
python ~/.agents/scripts/commtracker/toc.py <tracker-file> --update
```

Without `--update`: prints the generated TOC and reports whether it differs from current.
With `--update`: rewrites only the `## Contents` block in-place.

Anchor generation matches GitHub-Flavored Markdown exactly.

### Example

```bash
# Preview
python ~/.agents/scripts/commtracker/toc.py \
  "/path/to/communications/communications-tracking.md"

# Apply
python ~/.agents/scripts/commtracker/toc.py \
  "/path/to/communications/communications-tracking.md" --update
```

---

## Integration with skill-commtracker

When processing a new EML via skill-commtracker, run `extract.py` first:

```bash
python ~/.agents/scripts/commtracker/extract.py "<eml-path>" \
  --internal-domain <domain> \
  --attachments-dir "<comms-dir>/attachments/"
```

Claude reads the JSON output and performs Steps 4–7 of the skill (body cleaning,
CID substitution, entry formatting, TOC update). After adding the new entry,
optionally run `toc.py --update` to regenerate the TOC automatically.

For reconciliation runs, use `reconcile.py` first to identify untracked files,
then run `extract.py` on each untracked file.

---

## Placement

`~/.agents/scripts/commtracker/` — global, available to all projects.
No project-local copies needed.
