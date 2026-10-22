---
Title: skill-ai-it reference: target map and plan timeline
Category: reference
Status: current
Authority: canonical
Scope: The two tracker generators this skill ships (target_map.py, plan_timeline.py) and how a project adopts them
Last reviewed: 2026-10-21
Summary: >-
  How a project keeps its goals, targets and per-criterion status in target-map.yaml and its dated plan in plan-timeline.yaml, renders both
  into trackers with drift checks, and wires them into its justfile, govcheck and commit gate. Promoted from unified-network-controller 2026-10-21.
---

# skill-ai-it reference: target map and plan timeline

Two generators, both files only, both plan-by-default (`--write` to write), both under a second. Piloted in unified-network-controller (target map from 2026-09-27, timeline from 2026-10-21) and
promoted here on 2026-10-21 when smc-resiliency adopted both (operator: "the target map is promoted into skill-ai-it first, then adopted in smc-resiliency for the stages"; "we haven't adapted the
timeline method of UNC"). The skill's `just check` does not run them; each adopting project does.

## Contents

- [Target map](#target-map)
- [Plan timeline](#plan-timeline)
- [Adopting both in a project](#adopting-both-in-a-project)
- [Learned](#learned)

## Target map

`scripts/target_map.py` validates a project-root `target-map.yaml` (goals, targets, criteria verdicts with evidence and dates) and renders the tracker at `render_to`. `--schema` prints every field
with its level (mandatory, recommended, optional, rejected) and the reason; `--init` prints a starter map from a plan, `--sync` shows (and with `--write` appends) targets a plan gained, `--show [ID]`
is the cheap read. Since the promotion:

- **Bullet-style plans.** A source may name `exit_line` and `checklist_line`: the bold-lead lines `- **Target:** ...` and `- **Completion checklist:** [x] a · [ ] b`. Each item is a criterion numbered
  from 1, cut at its first full stop; `[x]` items are recorded as ticked and the validator warns when the map's verdict disagrees. A source target whose plan writes no checklist carries `criteria:
  []`.
- **`changelog.started_only: true`** exempts `not started` targets from the change-log rule (operator, 2026-10-21: stale rule applies only to started stages).
- **`summary` is one short line of where the target stands** (operator, smc-resiliency 2026-10-22: "a summary in where it stands", not everything
  verbatim): its state and what it waits on, in about fifteen words; the account of what was done goes in the change log and the plan, never in
  `summary`, which the embedded table shows on every render.
- **`embed: [{path, heading}]`** renders the summary table (state, where it stands, blocker, next action, each id linking to its tracker section) into another page between `<!-- BEGIN GENERATED:
  target-map ... -->` and `<!-- END GENERATED: target-map -->`; text outside the markers is never touched.

## Plan timeline

`scripts/plan_timeline.py` renders a page's Timeline block from dated rows: `due` (with `week: true` the Monday of a "Wk of"), `done`, `flag` (`at_risk`, `on_track`, `ahead`) and `kind` (`plan`,
`fixed`, `extra`, `parked`). The Schedule column is computed for today (LATE with days, DUE TODAY, Done, Not yet due; a passed date beats a flag); a `parked` row needs no date and shows Parked. The
data names `render_to`, a `source` sentence, an optional `note` and the `columns` after Due and Schedule (`[{key, header}]`, default Stage, Step, Where it stands, Next with); a row field that is
neither core nor a column fails. `--data` points at another file; the BEGIN marker names it.

## Adopting both in a project

1. Recipes, calling the skill copy by path (never a copy in the project):

   ```text
   target-map *ARGS: _require-venv
       @{{py}} "{{ai_it}}/scripts/target_map.py" --project-root . --write {{ARGS}}
   plan-timeline *ARGS: _require-venv
       @{{py}} "{{ai_it}}/scripts/plan_timeline.py" --project-root . --write {{ARGS}}
   commit-gate: _require-venv
       @{{py}} "{{ai_it}}/scripts/plan_timeline.py" --project-root . --write
       just check
   ```

2. Checks: load the script by path (`importlib.util.spec_from_file_location`, registered under a prefixed name), not by putting the skill's folder on `sys.path`, where its names (`check_governance`,
   `file_headers`) could shadow the project's. Fail on `outcome.problems` and on target-map drift; treat a Timeline that only trails today as a note, and let `commit-gate` render it before each
   commit.
3. The project venv needs PyYAML. Start a map with `--init --source <plan> --heading '<regex>'` (add `--exit-line Target --checklist-line "Completion checklist"` for bullet plans), replace every
   `TODO`, then `just target-map`.

## Learned

> **Learned 2026-10-22** · smc-resiliency target map · VERIFIED_PRIMARY · Source: smc-resiliency CHANGELOG 20261022_1643 (commit 449bceb) ·
> Falsifier: a plan whose stage heading misses `target_heading` and whose checklist is not read into the target above it
> A source's `target_heading` pattern that misses a stage heading (here `^### (?P<id>S\d) — ` against `### SM — Measuring root writes`) does not
> fail: that stage is absent from the map and its `Completion checklist` line is read into the target above it (S6 showed SM's four criteria). When a
> plan adds a stage whose id is not the usual shape, widen the pattern (`S\d|SM`) and check `--show` lists every heading the plan has.

> **Learned 2026-10-21** · promotion of a project script into this skill · VERIFIED_PRIMARY · Source: unified-network-controller CHANGELOG 20261021_1809;
> this file's scripts (commit pending) · Falsifier: a pilot page that renders differently from the skill copy on the same inputs A script promoted from a project keeps its output byte for byte only if
> every project-shaped string becomes data with the pilot's value: the pilot's table headers and its explanatory sentence moved into the pilot's YAML (`note`, `columns`), and new behaviour (parked
> rows, the parked legend line) renders only when used. Proof was a render by the old and new scripts on the same inputs for three dates, plus `just target-map` and `just plan-timeline` leaving both
> pages' SHA-1 unchanged.

```python
# skill-ai-it scripts/plan_timeline.py (commit pending): the pilot's fixed header and sentence became data
cells.append((due_label(row), text, *(str(row.get(c["key"], "") or "") for c in columns)))
...
f"Dates and steps are {source}." + (f" {note}" if note else ""),
...
if states.get("parked"):
    lines.append("⏸️ Parked: waiting on a decision or on other stages, without a date; the row says why.")
```

> **Learned 2026-10-22** · a generated table that the markdown hook also formats · VERIFIED_PRIMARY · Source: unified-network-controller operator, 2026-10-22; `scripts/plan_timeline.py` (`wrap_table`), `tests/test_plan_timeline.py` (`WrapTable`) · Falsifier: the markdown hook changing a freshly rendered Timeline block, or the page check failing right after a render
> A generated block is compared byte for byte with a fresh render, so a table the hook would wrap differently can never stay wrapped: the
> hook wraps it on the next edit and the next render unwraps it. Render through the hook's own formatter with the hook's flags (table-reflow
> `--width 200 --measure-rendered`) and both agree: the Timeline now wraps, and the hook leaves it as rendered. Set `wrap_width: 0` in the
> data file for one line per row.
>
> ```python
> # scripts/plan_timeline.py (skills_stuff, 2026-10-22)
> done = runner(["node", TABLE_REFLOW, "-", "--width", str(width), "--measure-rendered"], input=table + "\n", capture_output=True,
>               text=True, timeout=REFLOW_TIMEOUT_S, check=False)
> out = done.stdout.rstrip("\n")
> return out if done.returncode == 0 and out.startswith("|") else table
> ```
