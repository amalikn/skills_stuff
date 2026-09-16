---
name: skill-anydoc
description: "Convert Word/PPT/Excel/ODF/RTF/EPUB/CSV/PDF files to GitHub-flavored Markdown."
license: MIT
---

# skill-anydoc — convert documents to Markdown

Converts one document per invocation and writes GitHub-Flavored Markdown to stdout. Never prompts; all diagnostics go to stderr.

Wraps [firecrawl/anydoc](https://github.com/firecrawl/anydoc) (MIT). Canonical source of this contract: `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-anydoc/SKILL.md`.

## Command

Use the local launcher first — it runs the `@firecrawl/anydoc` package already installed in the skills working cache, so there is no network fetch at call time:

```bash
/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-anydoc/bin/anydoc <file>              # Markdown to stdout
/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-anydoc/bin/anydoc <file> -o out.md    # write to a file
/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-anydoc/bin/anydoc - --format csv < f  # read stdin
```

If that path does not exist (different machine, cache wiped), the launcher falls back to `npx -y @firecrawl/anydoc` automatically. On a machine without this repo, call `npx -y @firecrawl/anydoc
<file>` directly — it needs Node 20+ and no install.

## Rules

1. Supported inputs: `.doc`, `.docx`, `.docm`, `.odt`, `.rtf`, `.epub`, `.pdf`, `.ppt`, `.pps`, `.pot`, `.pptx`, `.pptm`, `.ppsx`, `.ppsm`, `.odp`, `.xls`, `.xlsx`, `.xlsm`, `.xlsb`, `.ods`, `.csv`.
2. The format is detected from file content. Pass `--format <name>` only when detection cannot work: CSV from stdin, or a missing or wrong extension.
3. Exit codes: `0` success, `1` the document could not be read or converted, `2` usage error. Failures print one `anydoc: <message>` line to stderr.
4. For a large document, write to a file with `-o` and read the parts you need instead of streaming everything into context. Prefer this by default for anything over a few pages.
5. Scanned and image-only PDFs need OCR, which anydoc does not do — they fail as unsupported. Use the hosted [Firecrawl Parse](https://firecrawl.dev/parse) API or a local OCR path for those.
6. Inside a Node, Python, or Rust codebase, prefer the library over shelling out: `@firecrawl/anydoc` on npm, `firecrawl-anydoc` on PyPI, `anydoc` on crates.io. Each exposes the same `to_markdown` /
   `toMarkdown` API.
7. anydoc reads text runs, not page layout. Column alignment, tab runs, and multi-column PDF flow are not preserved faithfully — the output is LLM-ready, not layout-faithful. When exact Word styling
   matters in the other direction (DOCX → PDF), use Microsoft Word's PDF engine, not this tool.
8. Conversion output is derived data. Write it to a scratch or working directory, not next to the source document, unless the operator asked for a persisted Markdown artifact.

## Maintenance

| Item | Path |
|---|---|
| Canonical skill source | `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-anydoc/SKILL.md` |
| Launcher | `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-anydoc/bin/anydoc` |
| Upstream clone (reference only) | `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-anydoc/anydoc-github/` |
| Runtime package (rebuildable) | `/Volumes/Data/_ai/_skills/skills-working-cache/anydoc/` |

The runtime directory keeps the name `anydoc` — it is the npm package install, not the skill.

Rebuild or upgrade the runtime:

```bash
cd /Volumes/Data/_ai/_skills/skills-working-cache/anydoc && npm install @firecrawl/anydoc@latest
```

Install targets (`~/.claude/skills/skill-anydoc/`, `~/.codex/skills/skill-anydoc/`, `~/.hermes/skills/domain/skill-anydoc/`) are symlinks to this file, not copies. Editing this file updates all three
agents immediately — there is no sync step.
