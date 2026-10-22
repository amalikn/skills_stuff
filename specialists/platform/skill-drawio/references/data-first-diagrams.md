---
Title: Data-first diagrams
Category: skill-reference
Status: current
Authority: Operator rules recorded in unified-network-controller (UNC) and enterprise-strategy, and the skill's own renderer code; the cited files win over this summary
Scope: >-
  How a project keeps a draw.io drawing as a rendering of a data map: the YAML map, its JSON Schema, the deterministic renderer, the generated banner, the
  drift check in `just check`, and the separate rule for drawings an operator edits by hand
Last reviewed: 2026-10-19
Summary: A generated drawing is rendered from a YAML map and checked for drift; an operator's hand-edited drawing is source and is only patched, never regenerated.
---

# Data-first diagrams

A drawing that explains a system (components, flows, dependencies) goes stale the moment the system changes, unless the drawing is a rendering of data that the change has to touch. This reference sets
out that pattern as UNC built it, in a form any project can copy. Claim IDs refer to [sources.yaml](../sources.yaml).

## Contents

- [The rule](#the-rule)
- [The parts](#the-parts)
- [The map](#the-map)
- [The schema](#the-schema)
- [The renderer](#the-renderer)
- [The banner and the drift check](#the-banner-and-the-drift-check)
- [Hand-edited drawings are source](#hand-edited-drawings-are-source)
- [Deciding which kind a drawing is](#deciding-which-kind-a-drawing-is)
- [Checklist for a new data-first drawing](#checklist-for-a-new-data-first-drawing)

## The rule

Flows are data first: the map is edited by hand, the drawing is rendered from it and never drawn by hand [C-D01]. A drawing someone wants changed is changed by editing the map and re-rendering. A hand
edit to a generated drawing is lost at the next render and is caught earlier by the drift check [C-D02].

The opposite case is a drawing an operator has edited in draw.io themselves. That file is the source; it is never regenerated over, only patched or appended to, with a backup kept [C-D03].

## The parts

```text
+--------------------+     validate      +------------------+
| map (YAML)         | ----------------> | schema (JSON)    |
| edited by hand     |                   | + reference check|
+--------------------+                   +------------------+
          |
          | render (deterministic)
          v
+--------------------+     compare       +------------------+
| drawing (.drawio)  | <---------------- | drift check      |
| GENERATED banner   |   byte for byte   | in `just check`  |
+--------------------+                   +------------------+
```

| Part            | UNC file                                          | Skill module                                         | Role                                                        |
| --------------- | ------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------- |
| Map             | `docs/flows/flows.yaml`                           | none                                                 | Source of truth: components, flows, steps, dependencies     |
| Schema          | `docs/flows/flows.schema.json`                    | `scripts/schema_lite.py`                             | Shape of the map; a stdlib subset of JSON Schema 2020-12    |
| Reference check | inside the renderer                               | `scripts/code_refs.py`                               | Every `path[:symbol]` a step cites exists in the repository |
| Renderer        | `render_flowmap.py` + the map's `drawing:` block    | `scripts/flowmap/`, `scripts/drawio/mxfile.py` | Map to uncompressed `.drawio`, deterministic                |
| Audits          | inside the renderer                               | `scripts/drawio/audit.py`                            | Layout faults a reviewer must never see ([layout-audits.md](layout-audits.md)) |
| Drift check     | `check_flow_map` in `scripts/check_governance.py` | the renderer's `evaluate()`                          | Fails when the file on disk differs from a fresh render     |

The skill's modules are being refactored while this is written; module names may change, and the table names what was present on 2026-10-19.

## The map

YAML, not JSON or TOML: YAML keeps comments, reads well in a diff, and nests ordered steps legibly; JSON loses the comments and TOML makes nested steps hard to read [C-D01]. The map has a stable name
(it is a living map, not a dated report), an `updated` field saying when it was last checked against the code, and the project's CHANGELOG records each change.

UNC's map holds two lists:

- **components**: every host, container, platform feature, service unit, code module, store, credential (by name only), remote-access hop and device kind, each with an id, a kind and a group.
- **flows**: each with a trigger, where it runs, an owner, a runtime budget, dependencies, and ordered steps; each step names its actor, action, reads, writes, transport, the code path
  (`path[:symbol]`), its failure modes and where to look when it fails.

A drawing then becomes a troubleshooting aid: find the flow, read its steps in order, follow each step's "look" entries. The map is also what an agent reads first when troubleshooting, because it is
text.

## The schema

The schema rejects unknown keys, bad enum values and missing fields. Beyond the schema, the renderer checks what a schema cannot [C-D02]:

- every component and flow id is unique;
- every actor, runs-on, owner and dependency names a known id;
- every `code` entry names a file that exists and, after a colon, a symbol defined in it (a Python def or class, a shell function, a constant, a YAML key or a just recipe), so a rename breaks the
  check rather than leaving the map stale.

`schema_lite.py` supports type, enum, pattern, minLength, minItems, items, required, properties, additionalProperties and `$ref` to `#/$defs/<name>`, and ignores any other keyword. Keep a map's schema
to those keywords, and keep a contract test that proves the subset is enough for that map.

## The renderer

The renderer must be deterministic: no timestamps, no unordered iteration, cells added in a fixed order, numbers printed the same way every run [C-D02]. Then the rendered file changes only when the
map does, and a byte-for-byte comparison is a valid drift check.

- Write uncompressed XML (`compressed="false"`), so the drawing diffs in review ([file-format.md](file-format.md)).
- Route every edge yourself with explicit waypoints; static export does not route around shapes ([layout-and-routing.md](layout-and-routing.md)).
- Run the layout audits on every routed page in the renderer's tests and assert every list is empty ([layout-audits.md](layout-audits.md)).
- Give the command line three modes, as UNC does: no flag validates and reports drift (exit 1 on a problem or stale file); `--write` renders; `--list` prints one line per flow and writes nothing.

> **Learned 2026-10-21** · Options page · VERIFIED_PRIMARY · Source: `scripts/flowmap/options.py`, `tests/test_options_page.py` · Falsifier: a map without `options` whose drawing changes, or an Options page audit fault
> A map may carry an optional `options` block (schema `$defs/options`): groups (one question each, an optional `decision`) of options (status
> `chosen`, `evaluate`, `open` or `rejected`; `steps`, `pros`, `cons`) plus free `decisions`. It renders as the page after the Overview: a colour legend, a decision column chained
> top to bottom beside one row per group, a green arrow from each decision to its chosen option, each option's steps as a routed chain, pros and
> cons aligned across the row. Maps without the block render byte-identical. Asked for by smc-resiliency's operator (update and recovery choices,
> trade-offs and decisions on one page). Screenshot: `references/screenshots/20261021-options-page/`.
>
> ```python
> # scripts/flowmap/options.py (_group_row), skill-drawio, 2026-10-21
> heads_top, band = y + gh + HEAD_GAP, y + gh + HEAD_GAP / 2
> dec = _decision_box(page, g, number, y, gh + HEAD_GAP)
> _chain_arrow(page, prev, dec)
> head_h = max(_height(_head_lines(o), BOX_CHARS) for o in g["options"])
> bottom = max(_option_chain(page, g["id"], o, x0 + i * (COL_W + GAP), heads_top, head_h) for i, o in enumerate(g["options"]))
> for i, o in enumerate(g["options"]):
>     if g.get("decision") and o["status"] == "chosen":   # through the gap between the question and the option heads, then down
>         cx = x0 + i * (COL_W + GAP) + COL_W / 2
>         page.route(f"{dec}-to-{o['id']}", dec, f"opt-{g['id']}-{o['id']}-head", [(MARGIN + DEC_W, band), (cx, band), (cx, heads_top)],
>                    DEC_ARROW, klass="thick", ignore=(f"opt-{g['id']}",))
> ```


> **Learned 2026-10-21** · option pages by subject · VERIFIED_PRIMARY · Source: `scripts/flowmap/model.py` (`option_blocks`, `option_groups`), `scripts/flowmap/pages.py`, `tests/test_options_page.py` · Falsifier: a map with `options` whose drawing changes, or two option pages sharing an id passing validation
> One Options page grew to nine questions; smc-resiliency's operator asked for it split by subject with no "Options" in the tab. A map may now carry
> `option_pages` (schema `$defs/option_page`): a list of blocks shaped like `options` plus an `id`; each draws as page `options-<id>` named by its
> title, linked from the Overview's index in map order. Group and page ids are unique across all pages. The single `options` block still draws as
> "Options: <title>" byte-identical (smc-resiliency and unified-network-controller re-checked without `--write`). Screenshot:
> `references/screenshots/20261021-option-pages/`.
>
> ```python
> # scripts/flowmap/model.py, skill-drawio, 2026-10-21
> def option_blocks(data: dict) -> list[tuple[str, str, dict]]:
>     found = [("options", f"Options: {data['options']['title']}"[:60], data["options"])] if data.get("options") else []
>     return found + [(f"options-{b['id']}", b["title"][:60], b) for b in data.get("option_pages", [])]
> ```

> **Learned 2026-10-21** · map parts and status · VERIFIED_PRIMARY · Source: `scripts/flowmap/model.py` (`expand_includes`, `stray_parts`, `status_text`, `status_style`), `tests/test_map_parts.py`, `tests/test_status.py` · Falsifier: a split map whose drawing differs from the unsplit one, or a stray part not reported
> A long map splits into parts (asked by smc-resiliency's operator on 2026-10-21, after unified-network-controller split its catalog): the master
> keeps the `drawing:` block and `#@include parts/<file>.yaml` lines, each part written without its parent's indentation. Proof that a split is
> safe: run the drift check without `--write` after splitting; smc-resiliency's drawing stayed byte-identical. Every component, flow and step may
> carry `status: {state, since, evidence}` so a reader tells an idea from a proven or built thing: proposed and designed draw dashed.
>
> ```python
> # scripts/flowmap/model.py (expand_includes), skill-drawio, 2026-10-21
> for line in path.read_text(encoding="utf-8").splitlines():
>     m = INCLUDE.match(line)
>     if not m:
>         out.append(line)
>         continue
>     part = (path.parent / m.group(2)).resolve()
>     if part in used:
>         raise ValueError(f"{path.name}: {m.group(2)} is included twice")
>     used.append(part)
>     pad = m.group(1)
>     out += [pad + x if x.strip() else x for x in expand_includes(part, used).splitlines()]
> ```

> **Learned 2026-10-21** · assembled maps and the look block · USER_STATED · Source: smc-resiliency operator, 2026-10-21 ("for catalog.yaml it was being built by the individual files, it was not using pointers"; "have the capability on the YAML file to define these things"); `scripts/assemble_flowmap.py`, `scripts/flowmap/profile.py` (`DEFAULT_LOOK`) · Falsifier: a project reading parts through pointers, or a look choice that cannot be set in the map
> A split map keeps its source in `parts/` (`master.yaml` with the `drawing:` block and `#@include` lines, one file per component group and
> flow section; part headers are `#%` lines) and `flows.yaml` is **generated** from them, complete, with a banner and no pointers
> (`assemble_flowmap.py`; `just flows` assembles, then renders; the project check fails on a hand edit or a stray part). Every aesthetic
> choice is a `drawing.look` key with the reviewed choice as its default: `group_fill`, `shapes`, `step_width`, `decision_width`,
> `step_chars`, `back_arrows`, `action_bullets`. A project lists them **commented** under `look: {}` in its master, so they are seen in the
> YAML yet keep following the skill's defaults; an uncommented line is a deliberate pin (a side agent, accepted by the operator, 2026-10-21).
> `render_flowmap.py --write` prints what is pinned and warns about a pin equal to today's default.

## The banner and the drift check

`drawio.mxfile.banner()` writes an XML comment between the declaration and `<mxfile>` naming the generator, the source map, the command that regenerates the file and the check that fails when it is out
of step [C-D02]:

```xml
<!-- GENERATED by <generator> from <map>; do not edit by hand. Change the map and run `<command>`; `<check>` fails when this file is out of step. -->
```

The drift check renders the map in memory and compares the text with the committed file. Wire it into the project's `just check` so it runs before every commit. A failed check means either the map
changed without a render (run the render) or someone edited the drawing (move the edit into the map, then render).

## Hand-edited drawings are source

When an operator edits a drawing in draw.io, the file becomes the source and is never regenerated [C-D03]. In enterprise-strategy on 2026-10-12, a solution diagram was generated, redrawn twice on
feedback, then edited by the operator in draw.io; the CHANGELOG records that "the .drawio is now the hand-edited source and is not regenerated".

Working on such a file:

1. Read the current file first, and decompress its pages if needed ([reading-drawings.md](reading-drawings.md)).
2. Keep a backup copy (in the session scratchpad or beside the file, outside version control if the project prefers) before any change.
3. Change only what was asked: append new cells, replace specific strings, or move only the cells you own (identify them by an id prefix you used).
4. Assert that everything before an append point is byte-identical to the original.
5. Export and review the result ([export-and-self-review.md](export-and-self-review.md)), and state exactly which cells were touched.

Never rebuild a hand-edited file from a script: that silently throws away the operator's layout and wording.

## Deciding which kind a drawing is

| Sign                                                | Kind               | Treatment                           |
| --------------------------------------------------- | ------------------ | ----------------------------------- |
| Starts with a GENERATED banner                      | Generated          | Edit the map, re-render             |
| Named as a render output in a check or recipe       | Generated          | Edit the map, re-render             |
| The operator says they edited it                    | Hand-edited source | Patch or append only, keep a backup |
| A CHANGELOG entry says it is now hand-edited        | Hand-edited source | Patch or append only, keep a backup |
| Neither, and it came from a vendor or a site record | Evidence           | Read only ([reading-drawings.md](reading-drawings.md)) |

When the signs disagree (a banner on a file the operator says they edited), stop and ask; do not guess.

## Checklist for a new data-first drawing

- [ ] Map in YAML with a stable name, an `updated` field and comments where a value needs a reason.
- [ ] Schema in the `schema_lite` subset, with a test that a deliberately bad map fails.
- [ ] Reference check for every code path the map cites.
- [ ] Deterministic renderer writing uncompressed XML with the GENERATED banner.
- [ ] Every edge routed with waypoints; layout audits run in tests on the real map.
- [ ] Drift check in `just check`; a test that writes then evaluates and sees no drift.
- [ ] The project's AGENTS.md (or equivalent) says the drawing is generated and names the command.

> **Learned 2026-10-21** · a gate's `next` order carries its meaning · VERIFIED_PRIMARY · Source: `scripts/flowmap/routing.py` (`branch_label`), `schemas/flowmap.schema.json` (`next`) · Falsifier: a two-way gate whose first `next` target is its failure path, drawn as a green Yes
> Since branch labels arrived, a two-way gate's first `next` is drawn as Yes (green) and its second as No (red); a map written before then may list
> them the other way. On adoption every two-way gate was checked against its gate text: smc-resiliency's six are right, unified-network-controller has
> none. Write the passing branch first, or name each case with `when`.

> **Learned 2026-10-22** · status dates · VERIFIED_PRIMARY · Source: unified-network-controller flow map (a side agent's note accepted by the operator, 2026-10-22); `schemas/flowmap.schema.json` (`$defs.status.since`) · Falsifier: a reader who takes a `since` date for a verification date, or a map whose live items all share the audit day
> `status.since` is the day the item reached its state: for `live`, when it went into service (its first deploy, unit or commit date from the
> project's records), never the day an agent checked it. Stamping every live item with the audit day made month-old services read as new on a
> drawing meant for the team and management. Keep the check in `evidence` ("... ; verified live <date>"); an item that predates the project says
> so and uses the project's start date. Proposed and designed items keep the day they were recorded.
