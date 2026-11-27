---
Title: Roadmap
Category: roadmap
Status: current
Authority: canonical
Scope: Current phase and open milestones of skill-coder
Summary: Current phase and open milestones; done items move to docs/history (just rotate).
Kind: roadmap
Budget: 200 lines, 25 KB
Archive: docs/history/ (roadmap-*.md, `just rotate`)
Last reviewed: 2026-11-19
---

# Roadmap — skill-coder

## Current phase

**2026-11-19.** Version 0.1.0 is built and installed (Claude, Codex, Hermes) and has been the default for code work since 2026-10-20 (global `~/.agents/AGENTS.md` names it for any code; history: `just
history "Made the default"`). Projects write back to it regularly. skill-drawio is built to its rules. Open work is skill-ai-it calling the helpers, adoption in unified-network-controller, the red
write-back contract test, and the evidence gaps below.

## Activation

- [ ] **skill-ai-it calls these helpers** — after activation, skill-ai-it's code checks call this pack's helpers, so each rule has one source.

## Adoption in unified-network-controller

Detail and order: UNC's [retirement assessment](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/reports/project-reviews/skill-drawio-and-skill-coder-retirement-assessment-20261019_1841.md).

- [x] **Per-root package naming** — `import_layers.py --graph` names packages by top folder; UNC's graph names them per root (`under`/`self`), 16 packages against
  29. Add the option (or a roots table in `code-map.toml`), match UNC's report, then UNC's `scripts/checks/import_graph.py` retires.
- [ ] **Write gates** — decide whether local file writes count as writes (`write_gates.py` found none in skill-drawio although `--write`/`--apply` write files; on UNC it flagged a capture script UNC's
  own check does not see). Then UNC's patterns and register move into a `--config` file.
- [ ] **Baselines** — UNC adopts the helpers with recorded baselines (`--write-baseline`) and a `code-map.toml`, so existing findings do not turn `just check` red.

## Evidence and languages

- [ ] **Python 3.11 floor** — `mise install python@3.11`, then `just test-matrix` (the declared floor is untested).
- [ ] **Shell limits** — the 100-line warn is now sourced (`documents/research-sources-20261019/google-shell-style.txt` line 53, "more than 100 lines long"); the 200-line fail in `code_size.py`
  `LANG_LIMITS` has no source: record it as the pack's own decision or find one (reviewed 2026-11-19).
- [ ] **Ansible and YAML size** — `code_size.py` measures no `.yml` files; decide a task-file limit once `languages/ansible.md` has a source.

## Open items (tools)

- [ ] language_split.py on a language already split (2026-11-25, continuum session): `python3 -I scripts/language_split.py --lang python` (plan) proposed rewriting languages/python/learned-other.md (190 lines) to 17 lines, built from python.md's own learned blocks only; applied, it would have dropped the topic file's entries. Not applied. Expected: refuse, or split the over-budget topic file itself. `just check`'s hint ("split it: --lang <name> --apply") points at this path for topic files too.
- [ ] scripts/code_size.py names some Rust functions after a parameter type when the signature spans lines (continuum-app baseline held `lib.rs::Path`, `::Json`,
  `::State` for plan_handoff and siblings), so adding a parameter or reformatting a signature makes the entry STALE ("in the baseline but no longer found") although
  the function still exists. Seen 2026-11-22: `just code-size` in continuum-app after adding `axum::Extension(actor): axum::Extension<identity::Actor>` to
  stream_events and plan_handoff. Fix: take the name from `fn <name>` on the header line, not from the first identifier before `(` across lines.

## Completed

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).
