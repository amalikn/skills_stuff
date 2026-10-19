---
Title: Refactoring and promotion
Category: reference
Status: current
Authority: local-supplement
Scope: Changing structure without changing behaviour, moving code with shims, and promoting project code into a reusable skill
Last reviewed: 2026-10-19
Summary: >-
  A refactor changes no behaviour and proves it with a before-and-after comparison; moved code leaves a shim and a
  moved-paths entry; scripts carry a promotion status and reusable ones move to a skill as a tested engine behind a thin wrapper.
---

# Refactoring and promotion

## Contents

- [Refactoring](#refactoring)
- [Moving code](#moving-code)
- [Promotion](#promotion)

## Refactoring

Martin Fowler defines a refactoring as "a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior"
(VERIFIED_PRIMARY). So:

- A refactor changes no behaviour and carries a characterisation comparison: the same inputs, run before and after, give the same output (byte-identical where the output is text). Why: "it still
  passes the tests" is weak when tests are thin.
- A behaviour change is a separate change, named and tested. Why: mixing the two hides the behaviour change inside a large diff.
- Refactor in small steps, each one green. Why: a failing step is cheap to find.
- Use the read-only or dry-run mode of the program for the comparison. Why: it exercises the real path without writing.

## Moving code

When a module or script moves:

1. Leave a shim at the old path that imports or calls the new one, so existing callers keep working.
2. Add an entry to a moved-paths record (old path, new path, date) that a check reads.
3. Update every string reference too: path literals passed to runners, scheduler wrappers, usage lines in docstrings, task-runner recipes and documentation. Why: an import check and a faked subprocess
   test do not see string paths (a governed project's staleness audit, 2026-10-05).
4. Remove the shim and the entry when no caller remains.

## Promotion

Code grows in the projects that use it and moves to a shared skill when it has earned it. The global policy says every script judged likely to be reused is promoted, in the same session, without being
asked (operator, 2026-10-07).

**The register.** A project keeps a register of its scripts, each with one status:

| Status         | Meaning                                                   |
| -------------- | --------------------------------------------------------- |
| `project_only` | Depends on this project; stays here (one line saying why) |
| `candidate`    | Could be reused; names what it still needs                |
| `promoted`     | Moved to a skill; the project keeps a thin wrapper        |

**When to promote.** The behaviour holds for any deployment, it imports nothing project-specific, and its engine can be pure or read-only with I/O injected by the caller.

**How.**

1. The engine goes to the skill's `scripts/` with generic inputs, offline tests, a docstring header, an entry in that folder's README and a task-runner recipe.
2. The project script becomes a thin wrapper that keeps its command line and defaults and loads the engine through one seam (one module that knows where the skill lives). Why: one place to change when
   the skill moves or its revision pin changes.
3. Before-and-after outputs of the read-only or dry-run modes must match. Why: promotion is a refactor.
4. A write path is tested offline with recorded responses and live only on a disposable instance.
5. The skill's change log names the source project and script; the project's register flips to `promoted`.
6. If no skill fits, promote into the project's own shared `scripts/` the same way. A scratchpad copy is not durable.

Engines a project imports run in the project's interpreter and the project pins the skill revision; see [runtime-boundaries.md](runtime-boundaries.md).
