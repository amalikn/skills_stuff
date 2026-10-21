---
Title: skill-drawio changelog
Category: log
Status: current
Authority: local-supplement
Scope: Release and governance history of the skill-drawio pack
Last reviewed: 2026-10-19
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/
Summary: Release history and governance changes of skill-drawio; the release heading holds the version of record.
---

# Changelog

## Unreleased

- 20261021 Overview and End-to-end boxes take their lane head's symbol (`drawing.look.component_shapes`, default on; operator, smc-resiliency): clouds and cylinders sized for their outline (`shapes.FIT`), the person figure bottom right, "Shapes on this page" on both pages, an index-box legend on the Overview; two tests; Learned 2026-10-21 in `references/visual-style.md`. Every consumer's drawing changes at its next `just flows`.
- 20261021 `option_pages`: several option pages by subject, each tab its title (no "Options:" prefix); `options` unchanged and byte-identical; ids unique across pages; two tests; Learned 2026-10-21 in `references/data-first-diagrams.md`.
- 20261021 `profile.look_report`: `render_flowmap.py --write` names the map's pinned `look` keys and warns about a pin equal to the current default; projects list the look commented under `look: {}` so they follow future defaults; one test; Learned entry in `references/data-first-diagrams.md` updated.
- 20261021 `scripts/split_flowmap.py` writes a `#%` header (Part, Lands under) on every part, as catalog parts carry; projects with a YAML header standard (unified-network-controller) refused parts without one.
- 20261021 `scripts/assemble_flowmap.py` (`just assemble-flowmap`): flows.yaml generated from parts/master.yaml and its parts (banner, no pointers, `#%` part headers dropped, stray part refused); split_flowmap.py now writes the master into parts/ and assembles; `drawing.look` (schema, `profile.DEFAULT_LOOK`): group_fill, shapes, step_width, decision_width, step_chars, back_arrows, action_bullets; tests for assembly, stray parts, drift and look; smc-resiliency and unified-network-controller converted, drawings byte-identical.
- 20261021 Return arrows take the short way (source's left side, along its lane, into the target's top right) when no step blocks it, else the band below the lanes; the test now asserts the route crosses no other step, in both cases.
- 20261021 Flow pages after review: arrow ends pinned on slanted shapes; decisions in a wider column (`scripts/flowmap/flow_geometry.py`, new: step widths, column positions, back-arrow route); back arrows routed below the lanes with a label mark; action clauses as bullets; step text estimate 38 characters; one test updated (back arrow), one added (geometry). Learned 2026-10-21 in `references/visual-style.md`.
- 20261021 `scripts/split_flowmap.py` (`just split-flowmap`): split a long map into parts by component group and flow section, proved to load the same data before writing; two tests; used on unified-network-controller's map (1,843 lines to an 85-line master and 13 parts, drawing byte-identical).
- 20261021 Dashed boxes are opaque: Overview group boxes white (were `fillColor=none`); `OpaqueDashedBoxTests` fails on any dashed vertex without a fill; Learned 2026-10-21 in `references/visual-style.md`.
- 20261021 Options page: the Decisions taken box is a document like the decisions below it; chain arrows start on a document's wavy edge (`options.WAVE`).
- 20261021 Shape vocabulary adopted (`scripts/flowmap/shapes.py`; schema: step `shape` and `flow`, component `shape`, `drawing.kind_shapes`, `drawing.io_vias`): flow page steps and lane heads drawn as flowchart symbols derived from the map, a predefined process links to the flow it runs, every flow page ends with "Shapes on this page"; the Options page draws decisions taken as documents, questions with a diamond, option steps as terminator and process (or a named shape), pros and cons as notes, and a shapes and colours legend; three tests; UNC, smc-resiliency and the example re-rendered and exported. Learned 2026-10-21 in `references/visual-style.md`.
- 20261021 Page headers: Overview, End-to-end and Options headers boxed with `HEADER_STYLE`, sized to their wrapped text by `header_height` (growing upward so the layout below stays put) and set out like flow-page headers (bold title, generation note, one bold-named line per item); UNC, smc-resiliency and the example re-rendered and exported. Learned 2026-10-21 (headers, legends, categories) and a proposed shape vocabulary with a sample in `references/visual-style.md`.
- 20261021 Flow pages: a forward arrow that skips a column into another lane enters its target from below (lane above) or above (lane below), so draw.io's router climbs it in the target's column instead of crossing the step in between (`pages.step_edges`); one test; Learned 2026-10-21 in `references/layout-and-routing.md`; UNC and the example unchanged by it.
- 20261021 The Overview and End-to-end page headers are boxed like every flow page's header (style only, same place and size); UNC, smc-resiliency and the example re-rendered and reviewed.
- 20261021 `scripts/flowmap/overview_index.py`: the Overview's flow index and legends moved out of `overview.py` (size budget 400); behaviour unchanged; one test.
- 20261021 Map parts: `#@include <path>` in a map is replaced by that part, indented to the include line (`flowmap.model.expand_includes`); a part included twice is refused and a part nobody includes is reported (`stray_parts`); three tests; Learned 2026-10-21 in `references/data-first-diagrams.md`; a map without includes reads as before.
- 20261021 `status` on components, flows and steps (schema `$defs/status`: proposed, designed, spike-proved, built, live, since, evidence): proposed and designed draw dashed on the Overview, End-to-end and flow lanes; a flow's status shows in its page header and Overview index line, with a status legend; three tests; maps without status byte-identical (UNC drift ok).
- 20261021 The Overview's flow index links the Options page when the map has one.
- 20261021 Options page (`scripts/flowmap/options.py`, schema `$defs/options`, `--audit` covers it): page after the Overview, linked from its flow index: colour legend, decision flow beside option step chains, aligned pros and cons; duplicate option ids refused; four tests; Learned 2026-10-21 in `references/data-first-diagrams.md` and (sips `--cropOffset 0 0` centres) in `references/export-and-self-review.md`; maps without `options` byte-identical.
- 20261020 `drawing.group_columns` (schema, `Profile`, Overview layout): columns per group for boxes with no arrow inside the group, default 3; Learned 2026-10-20 (unlinked boxes) in `references/layout-and-routing.md`; UNC and the shop example byte-identical.
- 20261020 `drawing.group_layout` (`vertical`, `horizontal`, `grid N`), the readable form of `group_columns` (`flowmap.profile.layout_columns`, `group_columns`; 0 columns = one row); a group in both is refused; two tests; Learned 2026-10-20 (unlinked boxes) extended.
- 20261020 `drawing.group_cell: {group: [row, column]}` places an Overview group in the group grid (`overview_layout.grid_cells`); the rest fill free cells in map order; empty rows allowed; one test; UNC and the shop example byte-identical.
- 20261020 `just test-matrix` builds one venv per mise interpreter under the working cache (`matrix/py<v>`, `requirements.txt`, so PyYAML), instead of the bare interpreters that lacked it; 3.12 to 3.14 OK (12 s first run, 4.5 s cached); 3.11 still not installed.
- 20261020 New `scripts/count_crossings.py` (`just count-crossings FILE --page N --prefix ov-d-`): crossings between arrows on one page from `drawio.read` full paths, to compare a consumer's drawing before and after an engine change; tests in `tests/test_count_crossings.py` (the contract now reads every `tests/test_*.py`). Measured by full paths, the 20261020 track-order fix took UNC's Overview thin arrows from 54 to 44 crossings (19 to 15 counted on stored points only).
- 20261020 Learned 2026-10-20 in `references/layout-and-routing.md`: a mutual `depends_on` draws a thin arrow through a box title, and a one-group tier put End-to-end labels on arrows; both fixed in the map (smc-resiliency S2 flows).
- 20261020 Fix: thin arrows in an Overview row gap take tracks that cut their crossings there (`drawio.route.gap_order`, `gap_ranks`; operator in smc-resiliency: "unnecessary overlaps on p1"). Chain order is kept unless a neighbour swap strictly helps, so the example renders byte-identical; UNC's Overview drops from 19 to 15 thin crossings and changes at its next `just flows`. Learned 2026-10-20 in `references/layout-and-routing.md`, screenshots in `references/screenshots/20261020-thin-track-order/`; tests `ThinTrackOrder`. Found: `just test-matrix` fails on 3.12 to 3.14 before and after this change (the bare mise interpreters have no PyYAML).
- 20261020 Write-back contract: every entry recording how something is done carries a code excerpt (source path, commit) and, for a visual surface, a redacted screenshot under `references/screenshots/<YYYYMMDD>-<slug>/` (operator, 2026-10-20).
- 20261019 Adopted by unified-network-controller in full: its renderer wrapper retired (its profile is now the `drawing:` block of its map,
  rendered by `render_flowmap.py`; the drawing changed only in its banner and `host` lines), and its as-built reader re-exports `drawio.read`
  (byte-identical output on 27 as-built files). The engine tests it held moved here as `tests/test_layout_rules.py` (17 tests: text fitting, notes,
  step boxes, header lines, bold spans, arrow ports, overview arrow styles and each audit at its exact threshold).
- 20261019 Fix: a map whose components share one End-to-end tier raised IndexError (no channel between columns). The grid keeps at least one
  channel and the page widens to hold it; drawings with two or more tiers are unchanged (UNC's and the example's byte-identical). Learned 2026-10-19 in `references/layout-and-routing.md`; regression test `test_one_column_end_to_end_page_draws_and_passes_every_audit`.
- 20261019 `ROADMAP.md` and `SETUP.md` added (operator, 2026-10-19: "add ROADMAP.md in both the skills", "and SETUP.md"), to skill-ai-it's templates; ROADMAP from this pack's SCRATCHPAD open items and unified-network-controller's retirement assessment, SETUP from the justfile, `.mise.toml` and requirements. README lists both and links SETUP from Quick start.
- 20261019 Archcore promoted (operator: "promote and accept"): 4 ADRs and 7 rules written `accepted` under `.archcore/`, indexed in
  `.archcore/index.guide.md` with the deferred spec and guide and the never-promoted reasons; `ARCHCORE_PROMOTION_CANDIDATES.md` deleted;
  `context-map.yaml`, `repomix.config.json` and the checker's `CONDITIONAL_PATHS` updated to match.
  Incident, no harm: a heredoc edit script failed its assertion, but the `git rm` on the following line still ran (the delete was intended).

- 20261019 Installed (operator: "Install skill-drawio into Claude, Codex and Hermes, as skill-coder was"): directory symlinks into the Claude and
  Codex skill folders and Hermes's `diagramming` category, all pointing at this canonical folder; Claude Code lists the skill.
- 20261019 Process notes from the build (no effect on the pack's content): `# noqa` imports were written twice (UNC wrapper, `tests/test_helpers.py`)
  and replaced with `importlib` the same hour (skill-coder Learned entry in its Python override); one check log went to `/tmp` instead of the
  scratchpad; skill-drawio files were marked intent-to-add in the skills_stuff index (`git add -N`) so doc freshness could see them before the commit.
  `references/export-and-self-review.md` crop example no longer writes to `/tmp`.
- 20261019 Archcore candidates reviewed (operator: "assess if the archcore entries for skill-drawio are correct ... fix them before I promote"):
  `ARCHCORE_PROMOTION_CANDIDATES.md` rewritten in skill-ai-it's report format with five corrections and six new candidates. Code fixed to match:
  `scripts/flowmap/pages.py` `write_drawing` refuses to write over a drawing without the generated banner (test added); `Profile` defaults neutral
  (`default_tier` 0, band title "Stores and secrets"). unified-network-controller's drawing re-proven byte-identical.
## 0.1.0 — 2026-10-19

- 20261019 Pack created (operator, 2026-10-19: a reusable skill capturing all the draw.io work from unified-network-controller, so any project can draw
  its own components from YAML). Engine promoted from unified-network-controller `scripts/render/flows_drawio.py` (2342 lines) and split into the
  `drawio` package (`mxfile`, `audit`, `route`, `read`, `export`) and the `flowmap` package (`profile`, `model`, `overview_layout`, `overview`,
  `e2e_grid`, `e2e`, `pages`), with `schema_lite.py` and `code_refs.py`; UNC's constants became a `Profile`, and `Profile.from_drawing()` reads an
  optional `drawing:` block for new projects. Every module is under 400 lines and every function under 60 (the 192-line overview function became an
  `Overview` class; the End-to-end class split into grid and search-and-draw).
- Proof: unified-network-controller's drawing renders byte-identical through the skill (SHA-1 `b8b22e66e1fb1932323ba6f103c6bd9a2a1953cd`
  before and after); its `just test` (1640) and `just check` pass with its renderer as a thin wrapper. Render time unchanged (0.89 to 0.90 s).
- New: `scripts/drawio/read.py` (from UNC's as-built reader, draw.io part, plus the page codec's encoder and nearest-line label matching),
  `scripts/drawio/export.py` and `drawio_export.py` (desktop CLI, pages from 1, layers, subprocess timeout), `yaml_list_patch.py` (comment-preserving list
  edits, plan by default, `--apply`; generalised from a one-off), `render_flowmap.py` (generic front end with `--audit`),
  `schemas/flowmap.schema.json`, and the example map `examples/shop/` (renders, current, every audit clean, every component reached).
- References (7) captured from UNC `docs/flows/readme.md`, UNC CHANGELOG 20261019_1602 and 20261019_1607, the enterprise-strategy CHANGELOG of
  2026-10-12, and the draw.io documentation (21 verbatim captures); `sources.yaml` C-D01 to C-D34; `compatibility.yaml` (desktop 32.4.1 and 32.5.5).
- Governance through skill-ai-it (AGENTS, AI_NAVIGATION, context-map, checker, justfile); `.archcore/` initialised empty, candidates in
  `ARCHCORE_PROMOTION_CANDIDATES.md` (proposed).
