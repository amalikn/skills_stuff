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
- [ ] **Write-back contract test red (found 2026-11-12, enterprise-strategy closeout)** — `tests/test_package_contract.py` test_write_back_entries_logged stops on 13 Learned entries written 2026-10-30
  to 2026-11-12 (languages/ansible/learned-templating.md 90 and 139; languages/python/learned-other.md 119; languages/shell/learned-other.md 22; references/design-patterns.md 1040, 1424, 1459, 1661,
  1686; design-principles.md 48; engine-composition.md 188; testing.md 313 and 318; tooling-and-runtime.md 81). Some look well formed, so check the parser's header join (six lines, " ·" at a line end)
  before rewriting entries. design-patterns.md P-65 (2026-11-10) only lacked its `· Source:` field and was fixed in the same closeout. **State 2026-11-19 (full scan, not first failure):** 13 malformed
  headers (languages/rust.md 61, `(recurred)` is not a one-letter suffix; design-patterns.md 1101, 1119, 1330, 1344, 1362, 1382; design-principles.md 48; engine-composition.md 162;
  generated-artifacts.md 97; refactoring-and-promotion.md 135; testing.md 304; tooling-and-runtime.md 99) and 6 entries with no CHANGELOG line (design-patterns.md 2026-11-05 ×2, errors-and-timeouts.md
  2026-11-10, generated-artifacts.md 2026-11-12, security.md 2026-11-09 ×2). testing.md also repeats labels (2026-10-20 (b), 2026-11-02, 11-08, 11-09, 11-18 twice each). Line numbers drift; rescan
  before fixing.
- [ ] **Ansible and YAML size** — `code_size.py` measures no `.yml` files; decide a task-file limit once `languages/ansible.md` has a source.

## Completed

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).
