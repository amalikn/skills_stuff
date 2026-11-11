---
Title: Charts from a flow map, and keeping the map true
Category: skill-reference
Status: current
Authority: Operator requests of 2026-11-02 and the skill's own code; external sources in documents/drawio-sources-20261102/
Scope: >-
  Regular flowcharts, vertical swimlanes and BPMN pages drawn from a flow map; reading a map instead of the code; and holding a map to the code with
  review stamps, coverage and word checks
Last reviewed: 2026-11-02
Summary: >-
  One map draws four views (lanes left to right, flowchart, vertical swimlanes, BPMN). A map is trusted because a change in cited code marks its steps
  suspect until someone reviews them, and uncited code is reported.
---

# Charts from a flow map, and keeping the map true

## Contents

- [Which view](#which-view)
- [Turning a view on](#turning-a-view-on)
- [What the map must say](#what-the-map-must-say)
- [Read the map before the code](#read-the-map-before-the-code)
- [Keeping the map true](#keeping-the-map-true)
- [Adopting it in a project](#adopting-it-in-a-project)
- [What a pass does not prove](#what-a-pass-does-not-prove)
- [Learned](#learned)

## Which view

| View               | Page                                                                         | Reads best for                             | Key               |
| ------------------ | ---------------------------------------------------------------------------- | ------------------------------------------ | ----------------- |
| Step by step       | Left to right, a horizontal lane per component, a note per step              | Who does what, with reads, writes and code | default           |
| Flowchart          | Top to bottom, no lanes, a straight spine, labelled diamonds, red stop boxes | The logic: what decides what               | `look.flowcharts` |
| Swimlanes | A band per actor, left to right by default for a wide screen; `:vertical` for a tall chart | Hand-offs between actors | `look.swimlanes` |
| BPMN               | The lanes in BPMN symbols, in a pool                                         | A reader who knows BPMN, process reviews   | `look.bpmn`       |

Lanes grow wide with many actors: eight made the smc_change Apply page unreadable at a normal zoom, six read well. Use a plain flowchart for a flow with many actors.

## Turning a view on

Each key takes flow ids, `family:<id>` to join a family into one chart, or `"all"`. Off by default, so an existing drawing stays byte-identical.

```yaml
drawing:
  look:
    flowcharts: [apply, rollback, family:smsc]
    swimlanes: [family:smsc]
    bpmn: [family:smsc]
```

Lanes and BPMN run left to right by default (operator, 2026-11-02: screens are wide); an entry ending `:vertical` (`smsc-steps:vertical`, `family:hosts:vertical`) keeps that page upright.

In a family chart a flow joins the chain only if its trigger kind is `after`: a rollback has a command of its own and never follows the proof.

## What the map must say

No new data is needed; better data draws better.

- **`label`** (up to 80 characters): the box's words. Without it a box shows the gate, else the action's first clause cut short; the whole step stays in the hover text. Give charted steps a label.
- **A branch is a step, not a sentence.** "Unless the AVR already holds it" inside an action draws nothing. Write a decision step with `next` and `when` (RULE-010 in ansible-wifi, the same idea).
- **`failures`** draw as a stop: beside the step on a flowchart, under it in a lane (a lane holds one column of boxes; operator, 2026-11-02), an error end event in BPMN.
- Any step with more than one way out is a decision on a chart, gate or not.
- In a lane a plain hand-off to a lane on the right stays level and runs sideways, so a chart spans both ways (operator, 2026-11-02).
- Lane columns are ordered for the shortest hand-offs, then the fewest arrows heading left, with the starting actor leftmost (operator, 2026-11-02).
- In a lane an arrow heading to a lane on the left leaves by the box's left side, so it does not cross the step's own stop (operator, 2026-11-02).
- A diamond's arrow to the box directly below it goes straight down, whichever branch it is; on a lane page each two-way diamond is drawn both ways and keeps the one
  with fewer crossings, then bends, then length (operator, 2026-11-02).
- On a plain flowchart an arrow within the main column and any arrow back up runs in a channel beside the column. Arrows that overlap split left and right, each taking the nearer free channel (operator, 2026-11-02); a lane page keeps its gutters.
- Chart, lane and BPMN arrows carry the step pages' own bold label, on the line.

BPMN pages keep the step pages' colours: tasks and gateways in the actor's colours, shaded lanes, green and red branches, a red stop. BPMN mapping: start and end events, an error end event for a stop, a task for a step, a call activity for a step that runs a flow, an exclusive gateway for a decision, a sequence flow for every arrow.
Nothing the map does not state is drawn, so no message flows. A gateway keeps its question inside the diamond: BPMN allows an exclusive gateway without its X.

A step's `branches` key holds decisions its words only state, each with a `question` and tagged `outcomes` (`run: ` into the step, `skip: ` past it, `stop: ` to a stop). Charts, lanes and BPMN draw a diamond
before the step; step pages ignore the key, so their numbers and End-to-end labels stay put. Writing every decision as a real step would have renumbered 37 reviewed pages. Outcomes that all go one way draw nothing.

A very wide step page folds with `layout: {fold: lane, fold_after: 4}` on the flow: a run of more than four steps by one actor snakes back and forth inside that actor's lane, which grows taller, and every lane
appears once (operator, 2026-11-02). Notes keep to their step's column, stacked under the lanes. Only a flow with no branches folds this way; any other keeps its normal page. `serpentine` and `z` fold the whole flow into rows instead.

`look.label_clearance` (px, default 6) keeps a flow page's arrow labels that far from other arrows: a label stopping 1 px short of a line passes the audit but reads as overlapping. Charts, lanes and BPMN always keep 6 px.

`look.route_under` (on by default) adds, per arrow, a track just below the lowest box between its ends, which can be inside a lane. The router already scores every way out of a diamond, so a long branch takes this track, and its sibling the near exit, whenever that draws cleaner; no map names a route (operator, 2026-11-02: build this into the code, not by hand).

`look.run_spacing` (px, default 40) prices parallel arrows that sit closer than that and long runs that hug a lane boundary, so the router spreads into open space, and keeps arrows off the top and bottom corners a decision holds for its own branches.

## Read the map before the code

`trace_query.py` answers from the map and gives the code to open next. Every step shown carries its review state, because an index that hides its own staleness is worse than none.

```bash
trace_query.py --map docs/flows/flows.yaml --flow checkout            # a flow, or a family
trace_query.py --map docs/flows/flows.yaml --file tasks/verify.yml    # the steps citing a file: what breaks if it changes
trace_query.py --map docs/flows/flows.yaml --writes "run record"      # who writes something
trace_query.py --map docs/flows/flows.yaml --failure timeout --json   # for an agent
```

Read a flow, then open only the cited code. A step marked `[SUSPECT]` is a lead, not a fact: read the code it cites.

## Keeping the map true

Generating a map from code was rejected: code gives the steps and loses the why, which is what a reader comes for. The mechanism is the **suspect link** of requirements traceability: a content hash
raises a flag automatically, and only a person who looked clears it.

| Check            | Catches                                                | How                                                                           |
| ---------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Reference exists | A renamed file or symbol                               | `render_flowmap.py` (already there)                                           |
| Review stamp     | Cited code changed, nobody looked                      | `trace_sync.py`: `<map>.lock.json` holds a fingerprint per step and reference |
| Coverage         | New code no flow mentions                              | `trace.cover` globs; each file is cited or exempt with a reason               |
| Uncited ratchet  | Steps with no code at all                              | `trace.uncited_steps`, shrink-only                                            |
| Stale words      | A path or name in a step that the code no longer holds | Warning; `trace.known_words` for a name that is outside the code on purpose   |

The smarts that keep it quiet enough to be believed:

- **Symbol fingerprints.** `path:symbol` hashes that block alone (Python by ast, a shell function, a YAML key's block), so a change beside it or a move within the file raises nothing. A line-range
  anchor breaks on any edit above it.
- **Behaviour only.** Python is hashed as its syntax tree without docstrings; other files lose comments and blank lines. A reformat raises nothing.
- **A spec is cited by its key.** `spec.yml:actions` makes a new action a suspect with no extra machinery.
- **The diff is kept.** `<map>.lock.d/` holds the accepted source, so a suspect shows what changed with no git history needed.
- **Editing the words clears nothing.** Only `--accept` does; the report says the words moved, to help the reviewer. A broken reference cannot be accepted.

```bash
trace_sync.py --map docs/flows/flows.yaml --diff                  # what to review
trace_sync.py --map docs/flows/flows.yaml --json                  # the same for an agent
trace_sync.py --map docs/flows/flows.yaml --accept rollback/undo --apply   # a step, a flow, a cited file, or all
```

Accept only after reading the diff against the step. Bulk `all` is for a first baseline.

## Adopting it in a project

1. Add a `trace:` block (`flowmap.schema.json`): `cover`, `exempt`, `uncited_steps` set to today's count.
2. Fix what `trace_sync.py` reports as uncovered: cite it on the step that uses it, or exempt it with a reason.
3. Review every step against its code before the baseline. Bulk stamping is not a review: see the Learned entry below. Then `--accept all --by <who> --apply`, and commit the lock and its folder.
4. Add `trace_sync.py` and `--audit` to the project's flow check.
5. A person installs `scripts/commit_hook.sh` as `.git/hooks/pre-commit`. An agent's install of a hook is refused by auto mode, and rightly: the operator owns what runs on their commits.

## What a pass does not prove

On smc_change the stamp means an agent review: agents wrote the corrections, a script applied them, about five were re-checked in the code, and branch tags began as keyword matches. One reviewer's to-do note reached a step that way. The `by` field says so. Check the code before relying on a chart for a live change.

It proves every cited change was looked at, not that the words are right; an accept can be careless. Whole-file references over-flag: one edit to a shared task file raised 14 steps on smc_change, so
cite a symbol where one exists. Ansible task files have no symbol yet, because a task name holds spaces and `code_ref` does not allow them.

## Learned

> **Learned 2026-11-11** · lane pages, two branches of one diamond in a shared gap · VERIFIED_PRIMARY · Source: scripts/flowmap/flowchart/order.py
> `improve_tracks` and route.py `assign_tracks(reversed_gaps)`; test SharedGap in tests/test_flowchart_layout.py fails with the search off; before and after in
> screenshots/20261111-shared-gap/ · Falsifier: a diamond whose branches still cross when some combination of swap and track order would not.
> Swapping a diamond's branches is half the move: when both branches run through one gap, the gap's first-fit track order can make each order of the branches
> cross. The search therefore also tries the gap's reversed track order, alone and with the branches swapped, and keeps what scores best (crossings, bends,
> length). Five consumers re-rendered: every layout metric unchanged (layout_quality), only text differed. Two other fixes in the same pass: an explicit
> `label` is never cut (only the engine's own pick is cut at 64 characters), and `look.e2e_tab` defaults to "E2E", used in every heading and index box.
>
> ```python
> for g in shared:   # gaps two branches of this diamond both use
>     keep = (chart.reversed_gaps, two[0].index if swappable else None)
>     tries = [(True, False)] + ([(True, True), (False, True)] if swappable else [])   # reverse; reverse and swap; swap
>     for rev, swap in tries:
>         chart.reversed_gaps = keep[0] ^ ({g} if rev else set())
>         if swappable:
>             two[0].index, two[1].index = (1, 0) if swap else (0, 1)
>         now = score(draw())
>         if now < best:
>             best, keep = now, (chart.reversed_gaps, two[0].index if swappable else None)
> ```

> **Learned 2026-11-02** · flow maps · VERIFIED_PRIMARY · Source: skill-drawio `scripts/flowtrace/` on smc_change, 203 steps · Falsifier: a behaviour-only edit raises no finding, or a comment edit raises one
> Baseline stamped 203 steps; check 0.25 s with 608 KB of accepted source. On a copy of the role: a comment raised nothing, a task change raised 14 steps, a new helper was reported uncovered, a new
> spec action raised the step citing `:actions`.

> **Learned 2026-11-02** · layered layout · VERIFIED_PRIMARY · Source: `scripts/flowmap/flowchart/graph.py`; ELK layered overview in documents/drawio-sources-20261102/ · Falsifier: a chart of a real flow failing `page_audit`
> A flow map breaks cycles by map order (ELK's MODEL_ORDER idea), so a chart never depends on a tie-break. All 111 chart, lane and BPMN pages of 37 smc_change flows passed the audit, but the first
> render still showed a rollback drawn after the proof: an audit checks geometry, not meaning. Look at the page.

> **Learned 2026-11-02** · map accuracy · VERIFIED_SECONDARY · Source: five reviewer agents read 203 smc_change steps against their code, 2026-11-02; a handful of findings re-checked in the code · Falsifier: a re-review that finds the map accurate without these fixes
> A map thought current had a wrong or stale claim in 94 of 203 steps, 98 branches hidden in prose, and 42 steps citing no code (now 4). The commonest error was one sentence copied across flows, so a shared fact belongs in one step that others link to.

> **Learned 2026-11-02** · swimlanes · USER_STATED · Source: operator review with a reference image, 2026-11-02 · Falsifier: the operator accepts boxes side by side in a lane
> A vertical lane holds one column of boxes. A stop goes under its step and the way on takes a gutter beside the column.

> **Learned 2026-11-02** · layout judged by an operator · USER_STATED · Source: operator review of real smc_change pages, 2026-11-02, session record in local-knowledge-ansible `ansible-wifi/evidence/flow-review-20261102/` · Falsifier: the operator reverses a rule
> Each complaint became a rule in code, never a map edit: no two arrows share an exit or overlap; a run stays off lane edges and from other runs when room exists, and tracks spread over the free band; a label sits on its line, in the one bold style, so move the arrows, not the label; a route clears the boxes it passes, not every lane; a long lane run folds inside that lane, and notes stack by column; diamonds, lanes and sides are chosen by measuring; a crossing is worse than closeness. A rule behind a default-off key is not built in: if a setting fixes a fault, make it the default and rerender every consumer.

```python
# scripts/flowmap/flowchart/order.py: draw both ways and keep the cleaner, instead of a rule per case
for nid in graph.steps:
    out = {e.index: e for e in graph.edges if e.src == nid and e.kind != "stop"}
    if set(out) != {0, 1}:
        continue
    out[0].index, out[1].index = 1, 0
    now = score(draw())
    if now < best:
        best = now
    else:
        out[0].index, out[1].index = 0, 1
```

> **Learned 2026-11-02** · draw.io · VERIFIED_SECONDARY · Source: https://www.drawio.com/doc/faq/custom-links · Falsifier: a documented hover trigger
> Highlight is a custom-link action, so it runs on a click; nothing documented triggers it on hover. A click can light a whole arrow (`click_isolate` already isolates on click).

Open: chart-php-steps arc clash on `cli~0-close`; plain flowchart spanning and measured swap; `just check` runs no unit tests.

Screenshots: [references/screenshots/20261102-charts-lanes-bpmn/](screenshots/20261102-charts-lanes-bpmn/readme.md).

> **Learned 2026-11-06** · one step page for a family · VERIFIED_PRIMARY · Source: `scripts/flowmap/pages.py` `_chained`, `named_pages`;
> `scripts/flowmap/flowchart/graph.py` `main_path`, `stitched`; tests `test_step_page_joins_a_family_before_its_first_flow`,
> `test_a_refusal_end_does_not_lead_into_the_next_flow`, `test_chart_tab_names_the_page` · Falsifier: a joined page whose refusal end leads into
> the next flow, or that lands away from its family's first flow page
> Operator, 2026-11-06 (smc-resiliency Tech stack): "why not one tech stack step by step", then "I want serpent diagram for tech stack" and "move
> the diagram after the Box page". A flowchart page cannot fold, so `look.step_pages: [family:<id>]` draws the family's flows chained on one step
> page (lanes), folded serpentine, placed just before the family's first flow page, its tab `<look.chart_tab>: <family name>` and its header
> naming the joined flows ("16 to 19"); each flow keeps its own page. A family whose flows each have their own trigger joins with `chain: all`
> (default: only flows triggered `after` the one before). Only the end of a flow's main path (first way out from its first step) leads on: a
> refusal reached through a gate's other way ends there; before this a rejected build ran on into the approval. Chained steps keep their own
> name (`label`) in their boxes.
>
> ```python
> # scripts/flowmap/flowchart/graph.py (skill-drawio, after b498288)
> def main_path(steps):
>     index = {s["id"]: k for k, s in enumerate(steps)}
>     seen, k = set(), 0 if steps else None
>     while k is not None and steps[k]["id"] not in seen:
>         seen.add(steps[k]["id"])
>         targets = step_targets(steps, k)
>         k = index.get(targets[0]) if targets else None
>     return seen
> ```
>
> Screenshot pending: smc-resiliency page "Step by step: Tech stack" (the permission classifier refused committing screenshots this session).
