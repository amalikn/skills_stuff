---
Title: skill-coder scratchpad
Category: state
Status: current
Authority: local-supplement
Scope: Working state of the skill-coder pack between sessions
Last reviewed: 2026-10-19
Kind: state
Budget: 200 lines, 25 KB
Keep: KEEP-marked items only
Open items tracker: docs/trackers/open-items-20261119_1559.md
Summary: Transient working state for skill-coder; durable facts move to references, sources.yaml or CHANGELOG.
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261126_1437
---

# Scratchpad

## Open items

- Older open items are tracked in [open-items-20261119_1559.md](docs/trackers/open-items-20261119_1559.md).
- 2026-11-21: P-82 is CANDIDATE (one project, continuum FR-237); promote when a second project encrypts into a content-addressed store.
- Review follow-ups (periodic review 2026-11-19, found by the review agents, not fixed): scripts/language_split.py misses `>  **Learned` (two spaces) and files a Learned body under the section title, and shell/topics.toml names learned-remote and learned-quoting with no files; Learned headers that run into their body (ansible learned-lint-and-tests 15-16 and 20-22, hcl.md 49, shell learned-format-and-lint 15-16, shell learned-safety 15-16); POSIX.1-2024 `set -o pipefail` not checked (posix-sh.md); efficiency-and-measurement 2026-11-09 `cut`/`head` line-buffering claim not checked (GNU stdbuf); documentation-and-headers and C-C13/C-C82 cite auto-memory feedback_no_noqa.md as source (promote the rule to governance); AI_NAVIGATION managed block names files the pack lacks.
- KEEP enforcement of skill-coder on every code change (operator, 2026-11-11, unified-network-controller session: "shouldn't we be making it
  mandatory that whenever any code change needs to happen, skill coder should be used"; all four layers chosen, built in a dedicated session).
  Today a hook only checks that skill-coder was loaded, not that the code follows it; that session wrote two scripts and a plan's script
  excerpts with four-space indentation, a 51-line function and five logic bugs before checks and a review caught them. Build, smallest first:
  (1) lint code in documents: skill-ai-it `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/scripts/markdown/md_examples_check.py` also runs the project's formatter and lint on Python excerpts;
  (2) the load gate in every repo: UNC's `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/scripts/registries/skill-domains.json` code rule (`.py`, `.sh`, `.js`, `.ts`, justfile) moved to the
  governance hooks so skills_stuff, tools and every project get it; (3) a check on each code write: a PostToolUse hook runs the fast
  checkers (`ruff format --check` with the project's config, `script_headers`, `call_timeouts`, `code_size`) on the written file and shows the
  findings to the agent (a settings change: show it before applying); (4) skill-coder checks in every project's `just check`, a Core item of
  skill-ai-it's central tooling plan, rolled out in its waves. Feedback memory: `/Volumes/Data/_ai/claude-auto-memory/feedback_skill_coder_before_code.md`.
- KEEP Activation DONE 2026-10-20 (operator: "if you are now happy with skill-coder, promote it as well"; all four steps below, in one pass).
  Was PENDING until the pack is tested (operator, 2026-10-19: "make it default once we have tested the skill"). Then, in one pass:
  1. global policy `~/.agents/AGENTS.md`, "Skills, context, and task routing": "for any code use `skill-coder`" beside `safe-change-validation`; re-run
     `/Volumes/Data/_ai/governance/scripts/sync-codex-agents.sh` so `~/.codex/AGENTS.md` carries it; 2. DONE 2026-10-19 (operator: "install it as skill but dont make it default yet"): directory
     symlinks into `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills/domain` and the skills_stuff `README.md` row;
     3. still to do with the default: `/Volumes/Data/_ai/_skills/skills_stuff/.agents/skill-surfaces.md` row, and restore the broad `SKILL.md` trigger
     ("Use before writing, changing, reviewing or refactoring code in any project"; narrowed to invoke-by-name until activation, operator 2026-10-19);
  4. `/Volumes/Data/_ai/governance/categories/coding-guide.md` links skill-coder as its detailed pack (check `/Volumes/Data/_ai/governance/sync-map.yaml`). Later, separately: skill-ai-it's code checks
     call skill-coder's helpers (one source per rule).

- Done 2026-10-20: unified-network-controller adopted `code-map.toml` (layers, write gates, module statuses). Open: its check scans Python only; `write_gates.py`
  also flags its shell backup runner (the config-backup shell script). Baselines (`--write-baseline`) not yet adopted there.
