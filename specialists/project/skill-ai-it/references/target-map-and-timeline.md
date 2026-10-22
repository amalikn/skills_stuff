---
Title: skill-ai-it reference: target map and plan timeline
Category: reference
Status: current
Authority: canonical
Scope: The two tracker generators this skill ships (target_map.py, plan_timeline.py), the plan tracker page they feed (plan_tracker.py) and how a project adopts them
Last reviewed: 2026-10-22
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
- [The plan tracker page](#the-plan-tracker-page)
- [Linking a tracker](#linking-a-tracker)
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
- **`summary` is one short line of where the target stands** (operator, smc-resiliency 2026-10-22: "a summary in where it stands", not everything verbatim): its state and what it waits on, in about
  fifteen words; the account of what was done goes in the change log and the plan, never in `summary`, which the embedded table shows on every render.
- **`embed: [{path, heading}]`** renders the summary table (state, where it stands, blocker, next action, each id linking to its tracker section) into another page between `<!-- BEGIN GENERATED:
  target-map ... -->` and `<!-- END GENERATED: target-map -->`; text outside the markers is never touched.

## Plan timeline

`scripts/plan_timeline.py` renders a page's Timeline block from dated rows: `due` (with `week: true` the Monday of a "Wk of"), `done`, `flag` (`at_risk`, `on_track`, `ahead`) and `kind` (`plan`,
`fixed`, `extra`, `parked`). The Schedule column is computed for today (LATE with days, DUE TODAY, Done, Not yet due; a passed date beats a flag); a `parked` row needs no date and shows Parked. The
data names `render_to`, a `source` sentence, an optional `note` and the `columns` after Due and Schedule (`[{key, header}]`, default Stage, Step, Where it stands, Next with); a row field that is
neither core nor a column fails. `--data` points at another file; the BEGIN marker names it.

A column may add `link_ids: {page, heading}`: each comma-separated id in a cell with no link yet becomes a link to the first heading of `page` whose text is `heading` with `{id}` filled in, followed
by a space or nothing (`heading: "Step {id}"` finds "Step 2 — Monitoring", never "Step 21"). The data keeps plain ids, unknown ids stay text, and a cell holding a hand-written link is left as written.

## The plan tracker page

`docs/trackers/plan-tracker.md` is the page a reader opens first (operator, smc-resiliency 2026-10-21: "difficult to know what is being followed and which of the file has the up to date plan"). Both
pilots (smc-resiliency, unified-network-controller) settled on one shape, now [templates/plan-tracker.md](../templates/plan-tracker.md):

| Section | What it holds | Kept by |
| --- | --- | --- |
| Where we are | `As of` date, one line on the live state, one numbered item per workstream led by its stage links, then what waits on the operator, a horizon line | Rewritten by hand whenever the state changes |
| Timeline (under Where we are) | The dated plan | `plan_timeline.py` from `plan-timeline.yaml` |
| What next | Ordered actions in a one-line table (owner, by, done when), each row linked to its detail block below | Hand, every pass that moves a stage |
| Which document to follow | Governing document per topic; inputs and history apart | Hand, when a document starts or stops governing |
| Decided but not yet in the designs | Decisions waiting to be folded into a design | Hand; a row clears when the design carries it |
| Stages | State, where it stands, blocker, next action per target | `target_map.py` (`embed:`) from `target-map.yaml` |
| How this page is kept | The page's own upkeep rules | Hand |

Setting it up: `just plan-tracker <project> --init` prints the starter page and `--init --apply` writes it when absent (never over an existing page); replace every `TODO`, add the two embeds
(`plan-timeline.yaml` `render_to`, `target-map.yaml` `embed:` under `## Stages`), paste [templates/AGENTS-plan-tracker-block.md](../templates/AGENTS-plan-tracker-block.md) into the project's AGENTS.md working rules, and call both checks from
`just check`:

```text
@{{py}} "{{ai_it}}/scripts/anchor_links.py" --project-root . --check --outside warn --skip docs/history/
@{{py}} "{{ai_it}}/scripts/plan_tracker.py" --project-root . --check
```

Keeping it: update the page in the same pass as a stage moving, a document starting or stopping to govern, or a decision made or folded in; every slurp checks it against SCRATCHPAD, ROADMAP and the
stage tables and fixes the page, not those. Where we are is rewritten, not appended (operator, 2026-10-22: "Adapt Where we are from UNC": item per workstream, its stage links first). `plan_tracker.py
--check` fails on a missing section, a missing `As of`, or a What next row that has no link or is split: the markdown hook splits a table row rendered wider than 200 columns, so shorten the row and put the detail in its block. A detail block without "Done when" fails; a row with no block is a note. Split rows in the
other tables, and an `As of` older than the newest CHANGELOG entry, are notes.

**What next: a summary table plus a detail block per item** (operator, 2026-10-22, smc-resiliency: "I'm still not able to understand what is
really required next and what would the done when really make sense"; "It doesn't have to be one row per item"). The table stays one line per
item (#, Next, Owner, By, Done when), and its Next cell links to a `### <n>. <action>` block under the table. Each block has four bullets:

- **What is needed:** the concrete work or choice, with the options or steps and links to the exact sections.
- **Why now:** what waits on it (a stage, a plan date).
- **In hand:** what already exists (results, proposals, evidence).
- **Done when:** a checklist a reader can verify (`[ ] ...`), naming the record that changes: the decision entry, the report, the ticked
  criterion, the re-rendered page.

A row's "Done when" cell is the one-line summary of that checklist. smc-resiliency's page is the worked example.

> **Learned 2026-10-22** · What next needs detail, not wider rows · USER_STATED · Source: smc-resiliency plan tracker (operator, 2026-10-22);
> `scripts/plan_tracker.py` (`detail_blocks`, `slug`), `tests/test_plan_tracker.py` (`test_detail_blocks`) · Falsifier: a reader who still cannot tell
> from a block what to do next or how to know it is done
> One-line rows kept the table readable but left "Done when" too terse to act on ("Review held; outcomes recorded"). Wider rows are split by
> the markdown hook, so the detail goes into a block per item; the table stays the index.

## Linking a tracker

A tracker is read to find where to start, so its hand-written sections link the nouns themselves ("the [rescue layout](...)", "[Step 2](...)") into the section that holds them, and keep each table row on one line
(operator, 2026-10-22, on unified-network-controller's plan tracker, preferring smc-resiliency's pattern to a separate "Start here" column or reference-style links). Generated blocks get their links
from the data (`link_ids`, `record`, links in `where`), never by editing the page.

`scripts/anchor_links.py` keeps those links true: every link to a `#heading` in a markdown file must land on a heading that exists. Call it from the project's `just check`:

```text
@{{py}} "{{ai_it}}/scripts/anchor_links.py" --project-root . --check --outside warn --skip docs/history/ --skip-name "prompt-*.md"
```

`--outside warn` reports a broken link into another project's file without failing, so a heading renamed by another project's session cannot block this project's commits; dot folders and `*-sources-*`
captures are always skipped.

Prose that holds links wraps by its visible width: markdown_rewrap counts a link by its label, not its target (2026-10-22, the rule tables already followed since 2026-08-28 with `--measure-rendered`),
so linked items read evenly in an editor that hides link targets.

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

> **Learned 2026-10-22** · plan trackers, any project · VERIFIED_PRIMARY · Source: scripts/plan_tracker.py (commit pending); smc-resiliency and
> unified-network-controller plan trackers, both failing the split-row rule on first run · Falsifier: a What next row the hook leaves on one line while it renders wider than 200 columns "Keep table
> rows on one line" cannot be met by formatting alone: the markdown hook splits any row whose rendered width passes 200 columns into continuation rows, which render as extra rows. Both pilot trackers
> had split rows in What next after the rule was written. The fix is content: shorten the row and move detail into Where we are. The check fails only on What next (the table a reader starts from) and
> notes the rest:
>
> ```python
> # scripts/plan_tracker.py (commit pending), check()
> for head, body in secs.items(): if any(not c[0] and any(c[1:]) for c in table_rows(body) if c): (problems if head.startswith("What next") else notes).append( f"{page}: a row in `{head}` is split
> over continuation rows (rendered wider than 200 columns); shorten it to one line")
> ```

> **Learned 2026-10-22** · smc-resiliency target map · VERIFIED_PRIMARY · Source: smc-resiliency CHANGELOG 20261022_1643 (commit 449bceb) ·
> Falsifier: a plan whose stage heading misses `target_heading` and whose checklist is not read into the target above it A source's `target_heading` pattern that misses a stage heading (here `^###
> (?P<id>S\d) — ` against `### SM — Measuring root writes`) does not fail: that stage is absent from the map and its `Completion checklist` line is read into the target above it (S6 showed SM's four
> criteria). When a plan adds a stage whose id is not the usual shape, widen the pattern (`S\d|SM`) and check `--show` lists every heading the plan has.

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
> A generated block is compared byte for byte with a fresh render, so a table the hook would wrap differently can never stay wrapped: the hook wraps it on the next edit and the next render unwraps it.
> Render through the hook's own formatter with the hook's flags (table-reflow `--width 200 --measure-rendered`) and both agree: the Timeline now wraps, and the hook leaves it as rendered. Set
> `wrap_width: 0` in the data file for one line per row.
>
> ```python
> # scripts/plan_timeline.py (skills_stuff, 2026-10-22)
> done = runner(["node", TABLE_REFLOW, "-", "--width", str(width), "--measure-rendered"], input=table + "\n", capture_output=True, text=True, timeout=REFLOW_TIMEOUT_S, check=False) out =
> done.stdout.rstrip("\n") return out if done.returncode == 0 and out.startswith("|") else table
> ```

> **Learned 2026-10-22** · plan trackers, any project · VERIFIED_PRIMARY (unified-network-controller: the page rendered from plain ids with `link_ids`
> was byte-identical to the hand-linked one, commit 6c8984f; a planted broken anchor failed `just check`) · Source: `scripts/plan_timeline.py` `link_ids`, `scripts/anchor_links.py`, skills_stuff
> fb3d4a0 and fdf90d0 · Falsifier: a retitled step heading leaves a rendered Timeline link pointing at the old anchor after `just plan-timeline`. Link ids from data, not by hand: a hand-typed link in
> the YAML breaks silently on a retitled heading, while `link_ids` looks the heading up on every render. Inline links widen a wrapped table's cells, so authored tables stay one line per row
> (table-reflow narrowed unified-network-controller's "Next" column to 25 characters when the links were inline).
>
> ```python
> # scripts/plan_timeline.py link_ids (skills_stuff fb3d4a0)
> want = spec["heading"].format(id=tok) for text, anchor in index: if text == want or text.startswith(want + " "): return f"[{tok}]({rel}#{anchor})" return tok ... if value and "[" not in value: # a cell with a
> hand-written link is left as written row[col["key"]] = "".join(p if i % 2 else one(p) for i, p in enumerate(re.split(r"(,\s*)", value)))
> ```
