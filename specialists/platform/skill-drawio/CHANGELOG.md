---
Title: skill-drawio changelog
Category: log
Status: current
Authority: local-supplement
Scope: Release and governance history of the skill-drawio pack
Last reviewed: 2026-10-19
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Summary: Release history and governance changes of skill-drawio; the release heading holds the version of record.
Last rotated: 20261119_1659
---

# Changelog

## Reference moved out

Sections moved verbatim from this file (read on need; a citation by section name resolves there):
- [docs/changelog-reference-1-20261122_2350.md](docs/changelog-reference-1-20261122_2350.md): Unreleased.

## 20261126_2020 — drawio_export.py runs from the scripts folder

- references/export-and-self-review.md Learned 2026-11-26: run by path with `python3 -I` from a project it cannot import the `drawio` package. Source: me/nas.

## 20261126_1449 — Home NAS map: colons in parts, depends_on for Overview links

- references/data-first-diagrams.md: a plain YAML value with ": " breaks a flow-map part; a component needs depends_on to be linked on the Overview (home NAS, 2026-11-26).

## 20261125_1820 — YAML flow-list items split by commas

- references/data-first-diagrams.md, Learned 2026-11-25 (b): an unquoted flow-list item with a comma inside parentheses loads as two items; quote it; unbalanced-parenthesis check as a validator candidate (home NAS; screenshot 20261125-yaml-flow-list-split).

## 20261125_1310 — Home NAS map: reversed dependency and italic host text

- references/data-first-diagrams.md, Learned 2026-11-25: an Overview shared run caused by a reversed `depends_on`; `*` in host text renders italic (home NAS map; screenshot 20261125-home-nas-flowmap).

## 20261123_1422 — Ishikawa page data first

- references/data-first-diagrams.md, Learned 2026-11-23: Ishikawa page data first: joints as tiny vertices so every route has ends, one arrow only into the effect (continuum IDEA-456).

## 20261123_0021 — Correction: wrapped_lines counts characters

data-first-diagrams.md: the card-height entry passed pixels to wrapped_lines(), which counts characters, so it never wrapped; corrected to convert the box width to characters (about 6.6 px each at font 11) with about 16 px a line, CORRECTION note kept (continuum journey, 2026-11-23).

## 20261123_0011 — Card line height corrected

data-first-diagrams.md: the card-height entry now says 17.5 px per line; 16.5 px let a four-line card touch its border (continuum journey, 2026-11-23).

## 20261123_0000 — Templates kept: Ishikawa (fishbone) and story map

documents/drawio-templates-20261123: the draw.io blog's Ishikawa manufacturing example (SVG with its embedded diagram extracted to .drawio) and story-map.drawio, verbatim, with a readme on what each suits (fishbone: root-cause analysis after incidents; story map: scope and releases) and how to rebuild them data first; pointer in data-first-diagrams.md.

## 20261122_2358 — Learned: one-click links and a story map on plain pages; card heights

references/data-first-diagrams.md, two Learned 2026-11-22 from continuum's journey.drawio: a plain drawio.mxfile.Page needs base_locked for one-click links, lanes go before their cards, a story-map page and short link schemes; page_audit() misses card labels taller than their box (screenshot 20261122-journey-one-pager).

## 20261119_1659 — compare_drawings.py; Learned: consumer drawings after a renderer change

- `scripts/compare_drawings.py` (`just compare-drawings`): two drawings compared per page, labels apart from style and geometry, compressed pages read; exit 1 on a label change. Tests in `tests/test_compare_drawings.py`.
- references/data-first-diagrams.md Learned 2026-11-19: a renderer change turns consumer flows-check red; compare before re-rendering.

## 20261119_1635 — Periodic review; 90-day review window; tracker path; write-back headers

- Periodic review (operator, 2026-11-19): every due doc re-read in full and dated 2026-11-19; references, Summaries and Scopes fixed, body rules aligned with their Learned entries (`NOTE_LINE_H` 13, base-layer lock supersedes "never locked"). Review window now 90 days (`--window-days 90`).
- The stray root file `this` (a rotation tracker named from "this file") moved to `docs/trackers/open-items-20261028_2305.md`; closed items dropped, SCRATCHPAD header made a path.
- Write-back headers repaired (no words changed): references/data-first-diagrams.md Learned 2026-11-18, references/export-and-self-review.md Learned 2026-11-13. Logged late: references/data-first-diagrams.md Learned 2026-11-17 (ASCII fix, now in skill-ascii-diagrams).
- AGENTS.md governance block: check command filled in (`just check`).

## 20261102_1347 — Learned: skip branch in its own lane; drift is not truth

`references/layout-audits.md`, from ansible-wifi (2026-11-02).
