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
Open items tracker: this file, Open items
Summary: Transient working state for skill-coder; durable facts move to references, sources.yaml or CHANGELOG.
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261107_1723
---

# Scratchpad

## Open items

- Older open items are tracked in [this](this).
- KEEP design-patterns.md follow-ups (2026-10-27): (1) all twelve patterns are `reusable_candidate`: when a second project uses one, cite it and
  raise the evidence (falsifiers are in each header); (2) P-05 is CANDIDATE until ansible-wifi applies `plans/smc-change-resume-20261027_1038/
  prepare-once.patch` and its canary passes; (3) harvest patterns from other projects (operator: "all the out of the box thinking"):
  DONE for unified-network-controller and smc-resiliency (P-13 to P-29, 2026-10-27; P-02, P-10, P-15 now in two projects); still to
  harvest: skill-drawio (data-first diagrams with drift check), skill-ai-it (governed-file budgets and rotation); (4) Python column has two suggested rows (P-05, P-06): move to built when a project does.
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
