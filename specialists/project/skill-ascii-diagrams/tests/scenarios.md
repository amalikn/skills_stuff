---
Title: skill-ascii-diagrams behaviour scenarios
Category: test-scenarios
Status: draft
Authority: canonical
Scope: Prompts and the behaviour skill-ascii-diagrams must show; run by hand or by an eval harness
Last reviewed: 2026-11-19
Summary: Acceptance scenarios from the seed, including one that must not trigger the skill and one where the agent must stop and ask; the Result column records the last run.
---

# skill-ascii-diagrams behaviour scenarios

Each scenario is a prompt and the behaviour that counts as a pass. Run them with [eval-procedure.md](eval-procedure.md) and write the date and result in the last column. A scenario that
cannot fail is rewritten, not kept.

| ID | Prompt | Expected behaviour | Result |
| --- | --- | --- | --- |
| S1 | "fix the diagrams in docs/design.md" | run `ascii-fix` (diff), read it, `--apply`, re-run until clean, report what is left for a redraw | |
| S2 | "draw the boot flow as an ASCII diagram" | write a JSON spec, render with `ascii-flow-render`, paste into a ```text block, check edges | |
| S3 | "why is the right edge of this box still ragged?" | find why the fixer skipped it (border with tees, grid, generated file) and fix the cause, not the one diagram | |
| S4 | "make a draw.io drawing of the flows" | not this skill: skill-drawio | |
| S5 | "fix the diagram in the interface document" (a generated file) | stop: find its source, fix there and regenerate, or ask | |
| S6 | "make all the boxes the same width" | style change: use `--even-widths` only because it was asked | |
