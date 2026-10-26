---
Title: Roadmap
Category: roadmap
Status: current
Authority: canonical
Scope: Current phase and open milestones of skill-drawio
Summary: Current phase and open milestones; done items move to docs/history (just rotate).
Kind: roadmap
Budget: 200 lines, 25 KB
Archive: docs/history/ (roadmap-*.md, `just rotate`)
Last reviewed: 2026-10-19
---

# Roadmap — skill-drawio

## Current phase

**2026-10-19.** Version 0.1.0 is built, installed (Claude, Codex, Hermes) and fully adopted by one project: unified-network-controller renders
its flow map with `render_flowmap.py` from its map's `drawing:` block and reads its as-built drawings with `drawio.read`, with no draw.io code of its
own. Open work is proving the engine on a second project and closing the version and evidence gaps below.

## Adoption in unified-network-controller

Detail and order: UNC's [retirement
assessment](/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/reports/project-reviews/skill-drawio-and-skill-coder-retirement-assessment-20261019_1841.md).

- [x] **As-built reader** — UNC `wc-local/scripts/site_onboarding/asbuilt_read.py` becomes a thin caller of `scripts/drawio/read.py` (its KMZ part stays there). Done when both site as-built sets read
  the same before and after.
- [x] **Engine tests move here** — UNC's `TextFits`, `NoteLayout`, `StepBoxLayout`, `LabelBoldTest`, `OverviewLayoutRules` and `AuditsCanFail` test this engine through UNC's wrapper; move them into
  `tests/test_helpers.py` (this pack has no text-fit, note, bold-label or failing-audit tests yet).
- [x] **UNC profile into its map** — UNC's kind colours, tiers and families move into a `drawing:` block in its `flows.yaml`; byte-identical render. Then its wrapper retires in favour of
  `scripts/render_flowmap.py` (one deliberate re-render: the banner names the new generator).

## Engine and evidence

- [x] **Second project** — smc-resiliency draws its S2 flows from `docs/flows/flows.yaml` with this engine and the generic schema (2026-10-20).
- [ ] **Archcore flow-map spec and adoption guide** — unblocked by the second project; write them (see `.archcore/index.guide.md`).
- [ ] **C-D16 on the current app** — re-check "static export draws orthogonal edges through boxes" on draw.io desktop 32.5.5 (checked only on 32.4.1; `compatibility.yaml`).
- [ ] **Python 3.11 floor** — `mise install python@3.11`, then `just test-matrix` (3.11 is not installed, so the declared floor is untested).
- [ ] **Redaction test decision** — vendor captures under `documents/drawio-sources-20261019/` hold example private addresses from the vendor docs; decide before adding a redaction test like
  skill-nautobot's (verbatim captures are exempt by design).

## Completed

- [x] **test-matrix needs PyYAML** (2026-10-20): one venv per interpreter under the working cache (`matrix/py<v>`); 3.12 to 3.14 OK.

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).
