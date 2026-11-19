---
Title: Ascii Diagrams reference: Checking diagrams
Category: reference
Status: current
Authority: >-
  skill-ascii-diagrams canonical reference; claims carry evidence labels and cite sources.yaml
Scope: Check diagrams and read the findings
Last reviewed: 2026-11-19
Summary: >-
  The findings `just ascii-fix` reports and what each means: broken edges (with fan-out branches told apart), arrows that miss their box, wide characters and
  tabs in drawn blocks; what a ```text block of command output is not; `ascii-fix --check` as a read-only gate in a project's closing check.
---

# Checking diagrams

## Scope

What the checks report and how to act on each finding. Repairing: [fixing-diagrams.md](fixing-diagrams.md). Not covered here: see the non-goals in [SKILL.md](../SKILL.md#role-and-non-goals).

## Contents of this reference

- [Decision rules](#decision-rules)
- [Worked example](#worked-example)
- [Further reading](#further-reading)

## Decision rules

- **Edge rule.** A box's side edges run in the corner columns down to a bottom border; a box that loses an edge or never closes is reported "not fixed" and is redrawn with the renderer.
  `VERIFIED_PRIMARY`.
- **Branch lines are not boxes.** A border-like run whose legs end having held nothing between them is a fan-out branch (`+---+---+` over bare `|` legs), not a broken box; an edge checker that reads
  it as a box reports false positives. `VERIFIED_PRIMARY` (two such false positives found in a design document).
- **An arrow must reach its box.** An arrowhead `v` whose next row is a box border outside that box's corners is reported. `VERIFIED_PRIMARY`.
- **Wide characters and tabs** (emoji, CJK, a tab) break monospace alignment and cannot be fixed by moving edges: replace them. They are reported only in blocks that draw a box: a ```text block of
  command output (a firmware listing with tabs) is not a diagram. `VERIFIED_PRIMARY`; check ported in idea from ilia-pluzhnikov/box-diagram `validate.py` (MIT).
- **A finding the projects' older edge checker misses** (a box whose border carries an arrow or a tee) is still a finding: trust the pack's check. `VERIFIED_PRIMARY`.
- **Gate it in the project's closing check.** `ascii-fix --check <files>` writes nothing and exits 1 when a diagram would change or a finding is left, so a
  crooked diagram cannot be committed unnoticed; run it over the project's Markdown in `just check`. `USER_STATED` (a side review, 2026-11-17: the fixer
  only helped when run by hand, and the older edge check missed boxes with connectors in their borders).

## Worked example

```text
        |
   +----+----+          a branch: legs hold nothing, no finding
   |         |
  one       two

+--------+
| text   |              a broken box: "loses an edge" at row 3
| more
+--------+
```

## Further reading

- `scripts/ascii/checks.py` (snapping and checks, including `edge_issues()`).
- ilia-pluzhnikov/box-diagram `skills/box-diagram/validate.py` (MIT, Copyright (c) 2026 Ilya P), verbatim in `documents/ascii-sources-20261117/`.
