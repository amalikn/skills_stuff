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
| Vertical swimlanes | Top to bottom, a column per actor, one stack of boxes in each                | Hand-offs between actors                   | `look.swimlanes`  |
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
- On a plain flowchart an arrow within the main column and any arrow back up leaves by the left and enters the target's left, in a channel beside the column (operator, 2026-11-02); a lane page keeps its gutters.

BPMN pages keep the step pages' colours: tasks and gateways in the actor's colours, shaded lanes, green and red branches, a red stop. BPMN mapping: start and end events, an error end event for a stop, a task for a step, a call activity for a step that runs a flow, an exclusive gateway for a decision, a sequence flow for every arrow.
Nothing the map does not state is drawn, so no message flows. A gateway keeps its question inside the diamond: BPMN allows an exclusive gateway without its X.

A step's `branches` key holds decisions its words only state, each with a `question` and tagged `outcomes` (`run: ` into the step, `skip: ` past it, `stop: ` to a stop). Charts, lanes and BPMN draw a diamond
before the step; step pages ignore the key, so their numbers and End-to-end labels stay put. Writing every decision as a real step would have renumbered 37 reviewed pages. Outcomes that all go one way draw nothing.

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

It proves every cited change was looked at, not that the words are right; an accept can be careless. Whole-file references over-flag: one edit to a shared task file raised 14 steps on smc_change, so
cite a symbol where one exists. Ansible task files have no symbol yet, because a task name holds spaces and `code_ref` does not allow them.

## Learned

> **Learned 2026-11-02** · flow maps · VERIFIED_PRIMARY · Source: skill-drawio `scripts/flowtrace/` on smc_change, 203 steps · Falsifier: a behaviour-only edit raises no finding, or a comment edit raises one
> Baseline stamped 203 steps; check 0.25 s with 608 KB of accepted source. On a copy of the role: a comment raised nothing, a task change raised 14 steps, a new helper was reported uncovered, a new
> spec action raised the step citing `:actions`.

> **Learned 2026-11-02** · layered layout · VERIFIED_PRIMARY · Source: `scripts/flowmap/flowchart/graph.py`; ELK layered overview in documents/drawio-sources-20261102/ · Falsifier: a chart of a real flow failing `page_audit`
> A flow map breaks cycles by map order (ELK's MODEL_ORDER idea), so a chart never depends on a tie-break. All 111 chart, lane and BPMN pages of 37 smc_change flows passed the audit, but the first
> render still showed a rollback drawn after the proof: an audit checks geometry, not meaning. Look at the page.

> **Learned 2026-11-02** · map accuracy · VERIFIED_PRIMARY · Source: five reviewers read 203 smc_change steps against their code, 2026-11-02; findings sampled against the code · Falsifier: a re-review that finds the map accurate without these fixes
> A map thought current had a wrong or stale claim in 94 of 203 steps, 98 branches hidden in prose, and 42 steps citing no code (now 4). The commonest error was one sentence copied across flows, so a shared fact belongs in one step that others link to.

> **Learned 2026-11-02** · swimlanes · USER_STATED · Source: operator review with a reference image, 2026-11-02 · Falsifier: the operator accepts boxes side by side in a lane
> A vertical lane holds one column of boxes. A stop goes under its step and the way on takes a gutter beside the column.

Screenshots: [references/screenshots/20261102-charts-lanes-bpmn/](screenshots/20261102-charts-lanes-bpmn/readme.md).
