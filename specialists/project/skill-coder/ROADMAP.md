---
Title: Roadmap
Category: roadmap
Status: current
Authority: canonical
Scope: Current phase and open milestones of skill-coder
Summary: Current phase and open milestones; done items move to docs/history (just rotate).
Kind: roadmap
Budget: 200 lines
Archive: docs/history/ (roadmap-*.md, `just rotate`)
Last reviewed: 2026-10-19
---

# Roadmap — skill-coder

## Current phase

**2026-10-19.** Version 0.1.0 is built, tested (mechanical tests green; three behaviour scenarios met every decide point) and installed (Claude, Codex, Hermes), but invoked by name only: it is not yet
the default for code work. skill-drawio is built to its rules. Open work is activation (the operator's call), adoption in unified-network-controller, and the evidence gaps below.

## Activation

- [x] **Make it the default** (done 2026-10-20, operator: "if you are now happy with skill-coder, promote it as well") — in one pass: the global policy line beside `safe-change-validation` and the Codex sync; the
  `skill-surfaces.md` row; restore the broad `SKILL.md` trigger; link it from the governance `coding-guide.md` (check `sync-map.yaml`). Steps in `SCRATCHPAD.md` Open items.
- [ ] **skill-ai-it calls these helpers** — after activation, skill-ai-it's code checks call this pack's helpers, so each rule has one source.

## Adoption in unified-network-controller

Detail and order: UNC's [retirement
assessment](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/reports/project-reviews/skill-drawio-and-skill-coder-retirement-assessment-20261019_1841.md).

- [x] **Layer check** — UNC's `check_import_layers` calls `scripts/import_layers.py` (same verdict on 2026-10-19; its baseline file is already this format).
- [x] **Per-root package naming** — `import_layers.py --graph` names packages by top folder; UNC's graph names them per root (`under`/`self`), 16 packages against
  29. Add the option (or a roots table in `code-map.toml`), match UNC's report, then UNC's `scripts/checks/import_graph.py` retires.
- [ ] **Write gates** — decide whether local file writes count as writes (`write_gates.py` found none in skill-drawio although `--write`/`--apply` write files; on UNC it flagged a capture script UNC's
  own check does not see). Then UNC's patterns and register move into a `--config` file.
- [ ] **Baselines** — UNC adopts the helpers with recorded baselines (`--write-baseline`) and a `code-map.toml`, so existing findings do not turn `just check` red.

## Evidence and languages

- [ ] **Python 3.11 floor** — `mise install python@3.11`, then `just test-matrix` (the declared floor is untested).
- [ ] **Shell limits** — 100/200 lines are UNVERIFIED until the Google Shell Style Guide capture is in `documents/`.
- [ ] **Ansible and YAML size** — `code_size.py` measures no `.yml` files; decide a task-file limit once `languages/ansible.md` has a source.

## Completed

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).
