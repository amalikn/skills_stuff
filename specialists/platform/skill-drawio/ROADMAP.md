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

- [ ] **Archcore flow-map spec and adoption guide** — unblocked by the second project; write them (see `.archcore/index.guide.md`).
- [ ] **C-D16 on the current app** — re-check "static export draws orthogonal edges through boxes" on draw.io desktop 32.5.5 (checked only on 32.4.1; `compatibility.yaml`).
- [ ] **Python 3.11 floor** — `mise install python@3.11`, then `just test-matrix` (3.11 is not installed, so the declared floor is untested).
- [ ] **E2E dependency connector picks the nearest actor, not the writer** (found 2026-10-26, smc-resiliency flow 14 `box-operation`): a store the flow's
  steps write (`writes:` on the agent's steps) is joined by its dashed line to UNC, the nearest actor, rather than to the component that writes it; prefer the
  actor whose steps name the store in `reads`/`writes`. Screenshot: smc-resiliency drawing page 11 (E2E: On-box operations).
- [ ] **Redaction test decision** — vendor captures under `documents/drawio-sources-20261019/` hold example private addresses from the vendor docs; decide before adding a redaction test like
  skill-nautobot's (verbatim captures are exempt by design).

## Completed

- [x] **Fold long flow pages** (built 2026-10-27): `look.fold` serpentine/z, `fold_after`, per-flow `layout`; `scripts/flowmap/fold.py`, `fold_turns.py`;
  consumers byte-identical with fold off; CHANGELOG 20261027.

Done items move to `docs/history/roadmap-*.md` (`just rotate`; find one with `just history <term>`).

## Engine performance review (2026-10-28) `OPEN`

Read-only review, nothing applied; the operator approves each item: `docs/performance-review-20261028_2317.md`. Measured A+B+C+D+G
together: UNC render 17.5 -> 5.95 s, byte-identical. Order: B, F, C, A, H, E, D+G, then the shared crossing/search engine.

## Layout quality analysis (2026-10-28, operator) `OPEN`

Not part of the speed review. Next: a quality baseline per page for the three consumers (crossings, shared runs, bends, length,
label clashes); then routing (port order, channel track nudging as libavoid, orthogonal routing as ELK), E2E placement scored on real
routes (the shared engine loop), and overview channel routing (most of UNC's 130 remaining crossings).

## Box placement research (2026-10-28, operator: "search them, don't incorporate at this stage") `OPEN`

Built (`scripts/flowmap/placement.py`, opt-in look keys): `e2e_row_search` (E2E column order, grid estimate): smc_change E2E 93 -> 43,
PHP E2E 31 -> 13. `overview_row_search` (group rows): UNC 245 -> 243. `overview_group_search`: candidate placements (map's own,
hill climb, 24 seeded restarts as Graphviz/ELK do) each routed for real, fewest thick-arrow crossings kept: UNC overview 245 -> 130
(-47%), never worse than the map's placement; pinned groups (group_cell) stay. Proxies alone misled (straight lines: 131 then 182
with more restarts; channel paths: 192/171). Next: one engine loop for every page type (candidates, real routing, count, keep best);
the E2E column search still scores a grid estimate. UNC's own schema copy lacks the new keys. Candidates for a principled next step, not adopted:
- Graphviz dot ordering (Gansner, Koutsofios, North, Vo 1993, IEEE TSE 19(3)): weighted median plus local transpositions; crossing
  minimisation on layered graphs is NP-complete, so heuristics.
- Eclipse Layout Kernel (ELK) layered: cycle breaking, layering, crossing minimisation, node placement, orthogonal routing with port
  constraints; elkjs is its JavaScript build.
- Adaptagrams libavoid (Wybrow, Marriott, Stuckey, GD 2009): orthogonal connector routing minimising length and bends; used by Inkscape;
  libtopology for topology-preserving improvement.
- Exact one-sided crossing minimisation by ILP (Wilson et al., IEEE VIS 2024); OGDF ships Sugiyama crossing-minimisation heuristics.
Sources: https://uspto.report/patent/grant/4953106 , https://eclipse.dev/elk/blog/posts/2025/25-08-21-layered.html ,
https://www.adaptagrams.org/documentation/libavoid.html , https://www.doi.org/10.1007/978-3-642-11805-0_22 ,
https://vis.khoury.northeastern.edu/pubs/Wilson2024EvaluatingExtendingSpeedup/ , https://google-melange.com/archive/gsoc/2013/orgs/ogdf/projects/pawel_schmidt.html
