---
Title: skill-coder changelog
Category: log
Status: current
Authority: local-supplement
Scope: Release and governance history of the skill-coder pack
Last reviewed: 2026-10-19
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/
Summary: Release history and governance changes of skill-coder; the release heading holds the version of record.
---

# Changelog

## Unreleased

- 20261019 Archcore review (operator: "assess the archcore entries ... are they correct logically? any missing?", then "yes apply all"): all nine accepted
  (runtime ADR and code-map rule promoted); helpers rule allows the explicit `--write-baseline` write and exempts imported modules from recipes;
  code-map rule names `[scan.exclude]`, `[naming]` and their reason checks; rules-cite-sources limited to load-bearing rules; runtime ADR lists the
  missing skill pin and untested 3.11 as open; activation ADR records the narrowed description. `SKILL.md` description narrowed to invoke-by-name
  until activation (operator: "narrow until activation"). References gain the decided size tiers (`module-and-function-shape.md`) and the script
  header standard (`documentation-and-headers.md`), which had lived only in code and this log.

- 20261019 Archcore promotion (operator, 2026-10-19: "assess and add missing archcore entries"): 7 new accepted documents, each naming its source and enforcement. ADRs `naming-mapping-is-data`,
  `default-activation-waits-for-testing`; rules `rule-precedence`, `rules-cite-sources`, `cross-project-write-back`, `pack-text-stays-generic`, `helpers-are-portable-and-catalogued`.
  `.archcore/index.guide.md` lists them and records the candidates not promoted, with reasons; tags consolidated to a shared set. The two earlier records stay `proposed`.

- 20261019 skill-ai-it refresh: navigation blocks already at `2026-10-14-compact-v2` (dry run, no changes). `just govern` failed on 3 doc-freshness findings, fixed rather than baselined:
  `context-map.yaml` gains its header summary comment; the two proposed Archcore records (`.archcore/adr/helpers-run-in-target-environment.adr.md`,
  `.archcore/rules/code-map-holds-decisions-only.rule.md`) gain `Last reviewed: 2026-10-19` from their own `created` date. `just check`, `just test` (42), `just nav-validate` and `archcore doctor`
  pass.

- 20261019 Naming as data (operator, 2026-10-19: "is it better to have a json or yaml or toml file for the mapping"): `naming.toml` (TOML, read with the project's own Python) is the source;
  `scripts/naming_table.py` renders the table in `references/naming-conventions.md` (drift fails `just self-check`); `scripts/naming_check.py` checks file and `just` recipe names, with project
  overrides and reasoned exceptions in `code-map.toml` `[naming]`. Measured read-only: unified-network-controller 6 template recipes off the rule, no file; ansible-wifi 11 files (hyphenated or
  camelCase `.py`/`.sh`). Governance `/Volumes/Data/_ai/governance/categories/coding-guide.md` naming clause revised to the same rule.

- 20261019 Naming mapping (operator, 2026-10-19: "define a mapping for language against convention"): new `references/naming-conventions.md`, every row checked against a primary source (26 new
  captures); the rule is code files and identifiers follow their language, typed commands are kebab-case, a tool's parser wins. `module-and-function-shape.md` points to it; claims C-C72 to C-C79.
  `languages/ansible.md` gains the tag-rename transition step (behaviour evaluation gap). Shared `scripts/pyparse.py`; shell heredoc and `${#` fixes in `code_size.py` (found on a second repository).

## 0.1.0 — 2026-10-19

### 20261019_1635 — Pack created

- Created (operator, 2026-10-19: "create skill-coder and capture all the intelligence for the programming in general ... programming language agnostic ... specific each language type of override that
  can be tweaked later"). Governance scaffold from skill-ai-it templates; content from the operator's rules (unified-network-controller code architecture design R1-R36, global policy, governance
  categories, auto-memory feedback) and primary sources (see `sources.yaml` and `documents/`).
- Helpers promoted from unified-network-controller and made generic, each characterised against the original: `import_layers.py` (from `scripts/checks/import_graph.py`: same 4 cycles on the same
  roots, same layer verdict), `write_gates.py` (from `check_write_gates`: with the project's patterns and register, 51 writers, every one gated or registered, as the project's own check). New:
  `code_size.py` (rule R34 with a warn tier: modules 300/400, functions 40/60, shell 100/200), `call_timeouts.py` (R15), `script_headers.py` (header = a script's front matter: summary, run line,
  safety), `code_map.py` and `templates/code-map.toml` (operator, 2026-10-19: one intent file for code, TOML so it is read with the project's own Python), `ratchet.py` (the shrink-only baseline).
- Runtime rule decided (operator, 2026-10-19): helpers run in the target project's environment with its interpreter; the pack's own interpreter only as a fallback; nothing installed into a project.
- Measured on unified-network-controller (read-only, 2026-10-19): 25 modules over 400 lines and 68 functions over 60; 30 runnable scripts with header gaps. Not acted on: recorded there as candidates.

### 20261019_1711 — Installed, not default; recipes kebab-case; behaviour evaluation

- Installed (operator, 2026-10-19: "install it as skill but dont make it default yet"): directory symlinks in `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills/domain`, and a row in the
  skills_stuff `README.md`. The global routing line stays pending (SCRATCHPAD, Activation).
- Recipes renamed to kebab-case by skill-ai-it's upgrader after its rename map was inverted (`nav-upgrade`, `lint-md`, `audit-scripts` and the rest); the `[naming.exceptions]` kept for them were
  removed, and `naming_check.py` now reports no name off the mapping.
- Tests: behaviour evaluation of C-S02, C-S04 and C-S17 with and without the skill (results in SCRATCHPAD); new contract check that every capture a claim cites exists (the sample check done by hand,
  made permanent). 42 tests.
- Incident, corrected the same session: `.archcore/` ADR and rule were written directly during bootstrap and marked `accepted`, against
  `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/archcore-routing.md` (only `promote` writes Archcore content, with the operator's authorization). Found while
  reviewing that pattern for `just check`; both now `proposed`, awaiting the operator's promotion approval. `archcore status` passes.
- Feedback to all-scraper: the ShellCheck wiki page answered with a bot challenge during research; recorded in its `ROADMAP.md` Backlog.

## 20261019_1643 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-14-compact-v2 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-14-compact-v2`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md, context-map.yaml, AGENTS.md, scripts/README.md
