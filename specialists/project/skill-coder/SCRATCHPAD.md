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
---

# Scratchpad

## Open items

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
- Test status 2026-10-19: mechanical green (35 tests, check 391); helpers characterised on unified-network-controller and canaried on ansible-wifi (shell heredoc and `${#` bugs found and fixed with
  regression tests); 8 of 8 sampled VERIFIED_PRIMARY claims matched their captures. Behaviour (C-S02, C-S04, C-S17; sonnet, fresh contexts, with and without the skill): all three with-skill runs
  routed to the scenario's first reference and met every Decide point; each added pack-specific practice the baseline lacked (writer-held gate, non-admin writer, outcome read-back, moved-paths and
  register, owning-skill check, canary then hand-over, exit-code gating). Caveat: the baseline is not clean, as subagents inherit the global CLAUDE.md and auto-memory index. One gap found and fixed:
  `languages/ansible.md` had no tag-rename transition rule (the run contradicted itself on an alias); step 6 added.

- Next actions (20261019_1812): skill-drawio built to this pack's rules (its `just self-check` runs these helpers); commit this pack's package rule, write-back
  mechanism and python Learned entry when the operator approves; activation when the operator says so; `mise install python@3.11` then
  `just test-matrix` to prove the floor by a run.
- `write_gates.py` found 0 writers in skill-drawio although `render_flowmap.py --write` and `yaml_list_patch.py --apply` write files: its patterns look for
  remote and database writes, not `write_text`. Decide whether local file writes count (a renderer's `--write` is the skill's own exception).
- Done 2026-10-20: unified-network-controller adopted `code-map.toml` (layers, write gates, module statuses). Open: its check scans Python only; `write_gates.py`
  also flags its shell backup runner (the config-backup shell script). Baselines (`--write-baseline`) not yet adopted there.
- Ansible and YAML: `code_size.py` measures no `.yml` files yet; decide a module limit for task files once `languages/ansible.md` has a source.
- Shell limits (100/200) are UNVERIFIED until the Google Shell Style Guide capture is in `documents/`.
