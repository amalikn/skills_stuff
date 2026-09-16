Title: Graphify SCRATCHPAD
Category: ai-governance
Status: current
Labels: graphify, skills_stuff, ai-files, governance
Last reviewed: 2026-04-28

# SCRATCHPAD

Agent working memory for graphify workspace.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: updated 2026-04-30 12:55 — slurp-chat checkpoint slurp-20260430-graphify-bootstrap -->

## Current state

**Phase:** execution

This folder is now onboarded as a governed project workspace under `skills_stuff`, centered on the local upstream clone in `graphify-github/`. Global/project memory confirms active Graphify operations and MCP installation activity on 2026-04-28. Next actions are to maintain local governance files and keep install/runtime facts current, including the macOS local install path.

---

## Open items

- [ ] Add explicit parent-level routing/index entries for this `graphify/` workspace if missing.
- [ ] Keep local install notes aligned with actual CLI/interpreter paths after Graphify upgrades.
- [ ] Update local AGENTS.md / README.md to document `graphify-bootstrap.sh` launcher and the hybrid CLI + Claude Code workflow it enables.
- [ ] Run `/skill-ai-it` on this folder if governance refresh is wanted (the existing AGENTS/README don't yet mention the bootstrap script).

---

## Key anchors

| Item | Detail |
|---|---|
| Workspace root | `/Volumes/Data/_ai/_skills/skills_stuff/graphify` |
| Upstream clone | `/Volumes/Data/_ai/_skills/skills_stuff/graphify/graphify-github` |
| Local Graphify CLI | `/Users/malik.ahmad/.local/bin/graphify` |
| Local Graphify Python | `/Users/malik.ahmad/.local/share/uv/tools/graphifyy/bin/python` |
| Parent project context ID | `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c` |
| Bootstrap launcher (source) | `/Volumes/Data/_ai/_skills/skills_stuff/graphify/graphify-bootstrap.sh` |
| Bootstrap launcher (PATH) | `~/.local/bin/graphify-bootstrap` (symlink) |

---

## Recent decisions

- 2026-04-30 — Added `graphify-bootstrap.sh` launcher for hybrid CLI + Claude Code workflow. CLI runs the free structural pipeline (detect + AST + cluster + viz); `/graphify <path> --update` in Claude Code fills semantic gaps. Symlinked to `~/.local/bin/graphify-bootstrap` (matches existing aider/aider-desk launcher pattern).
- 2026-04-30 — Confirmed hard boundary: graphify CLI cannot do semantic extraction (no embedded LLM credentials). Docs-only corpora must use the slash command. CLI helps when AST has work to do.
- 2026-04-28 — Treat this folder as the governed local workspace for Graphify in `skills_stuff`, with upstream code in `graphify-github/` and local governance at folder root.
- 2026-04-28 — Record local macOS Graphify install paths as operational anchors in governance docs.

---

## Session history (summaries — full detail in memory-keeper)

### 2026-04-30 — graphify-bootstrap CLI launcher
- Created `graphify-bootstrap.sh` here; symlinked into `~/.local/bin/`.
- Reuses graphify uv-tool Python via `which graphify` shebang resolution.
- Smoke-tested on 2-file corpus (1 .py + 1 .md): 3 AST nodes, 0 tokens, handoff message printed.
- Pairs with `/graphify <path> --update` in Claude Code; ~95% token saving on code-only repos, 0% on docs-only.
- Evidence basis: memory-keeper keys `graphify.note.cli-vs-slash-boundary`, `graphify.progress.bootstrap-script-created`.

### 2026-04-28 — Graphify workspace governance bootstrap
- Created baseline governance files for `graphify/` and linked them to parent governance.
- Added explicit local install note that Graphify is already installed on macOS via uv tool paths.
- Synthesized current state from memory-keeper and project-context because no dedicated prior graphify workspace log existed.
- Evidence basis: memory-keeper key `skills/graphify/source_install_mapping`; project-context note `graphify MCP installed in Claude Code — 2026-04-28`

---

## Next actions

- Maintain this workspace as the source-of-truth location for local Graphify operational documentation.
- Add/update dated outcome notes when graphify-specific work changes install, runtime, or workflow behavior.
- Persist future graphify session closeouts with direct file-change and validation details in memory-keeper.

---

## Memory pointers (navigation only — content is above)

- memory-keeper channel `graphify` keys (added 2026-04-30):
  - `graphify.note.cli-vs-slash-boundary`
  - `graphify.progress.bootstrap-script-created`
- memory-keeper checkpoint: `slurp-20260430-graphify-bootstrap` (ID ed2b42dc, 233 items)
- project-context project ID: `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c` (skills_stuff), channel `graphify`, checkpoint `slurp-20260430-graphify-bootstrap` (ID 162b60b4-4d45-4a88-8831-45130121cfe8)
- earlier memory-keeper keys (still relevant): `skills/graphify/source_install_mapping`, `skills_stuff.graphify.mcp-install-20260428`
- claude-mem: not queried this slurp
