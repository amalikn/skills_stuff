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
| Renderer        | `scripts/render/flows_drawio.py`                  | `scripts/flowmap/`, `scripts/drawio/mxfile.py` | Map to uncompressed `.drawio`, deterministic                |
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
