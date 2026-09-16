Title: skill-anydoc Skill Workspace
Category: skill-workspace
Status: current
Scope: Local setup, runtime, and install state for the `skill-anydoc` document-to-Markdown skill
Last reviewed: 2026-08-10

# skill-anydoc

Converts Word, PowerPoint, Excel, OpenDocument, RTF, EPUB, CSV, and PDF files to GitHub-Flavored Markdown. Upstream project: [firecrawl/anydoc](https://github.com/firecrawl/anydoc) (MIT).

## Layout

| Path | Role |
|---|---|
| `SKILL.md` | Canonical skill contract — author here, then sync to install targets |
| `bin/anydoc` | Launcher: runs the working-cache install, falls back to `npx -y @firecrawl/anydoc` |
| `anydoc-github/` | Upstream clone, reference only — do not edit |
| `/Volumes/Data/_ai/_skills/skills-working-cache/anydoc/` | Rebuildable runtime: `.mise.toml` (node 26) + `node_modules/@firecrawl/anydoc` |

The Rust workspace in `anydoc-github/` has no binary target — the CLI is `node/cli.js` wrapping a napi-rs native binding, so the runtime is installed from npm rather than built with cargo. `npm install` pulls the platform binary as an optional dep (`@firecrawl/anydoc-darwin-arm64` on this machine).

## Install state (2026-08-10)

| Target | Path | Status |
|---|---|---|
| Claude Code | `~/.claude/skills/skill-anydoc/SKILL.md` | ✓ symlink → canonical |
| Codex | `~/.codex/skills/skill-anydoc/SKILL.md` | ✓ symlink → canonical |
| Hermes | `~/.hermes/skills/domain/skill-anydoc/SKILL.md` | ✓ symlink → canonical |

All three install targets are symlinks to `skills_stuff/skills/skill-anydoc/SKILL.md`. Editing the canonical file updates every agent immediately — there is no copy to re-sync and no drift to reconcile.

Runtime: `@firecrawl/anydoc` 0.1.7, node v26.5.0.

## Maintenance

```bash
# upgrade the runtime
cd /Volumes/Data/_ai/_skills/skills-working-cache/anydoc && npm install @firecrawl/anydoc@latest

# (re)create the install symlinks — only needed on a fresh machine or if a link is broken
SRC=/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-anydoc/SKILL.md
for T in ~/.claude/skills/skill-anydoc ~/.codex/skills/skill-anydoc ~/.hermes/skills/domain/skill-anydoc; do
  mkdir -p "$T" && ln -sfn "$SRC" "$T/SKILL.md"
done

# refresh the upstream reference clone
cd /Volumes/Data/_ai/_skills/skills_stuff/skills/skill-anydoc/anydoc-github && git pull
```

## Verified

- CSV via file path and via stdin (`- --format csv`)
- `.docx` — `APN Technology Strategy 2027-2030.docx`, exit 0
- `.pdf` — text-layer resume PDF, exit 0
- `.xlsx` — `project_status_template.xlsx`, tables rendered as GFM, exit 0
- Missing file → `anydoc: io error ...` on stderr, exit 1

Not verified: `.ppt`/`.pptx`, `.epub`, `.rtf`, legacy `.doc`, OpenDocument formats. Scanned/image-only PDFs are unsupported by design (no OCR).
