---
name: skill-walk-before-run
description: >-
  Blocking gate that judges whether work about to happen is expansion sitting on an unverified
  load-bearing assumption, and if so blocks it and redirects to the cheapest real-world test.
  Use before adding a component, framework, dependency or abstraction; starting a bake-off or
  evaluation; writing a third document about one undecided thing; or when a project feels
  overwhelming. Manual invocation only.
metadata:
  aliases: skill-wbr
  version: 0.1.1
---

# Skill: Walk Before Run

Invocation: `/skill-walk-before-run` or `/skill-wbr`. Defaults to the calling project — the project of the invoking session — as the target; the assumption evaluated is about that project's proposed
expansion, never this skill's own, unless the operator names a different project explicitly. Manual only in v0.1 — do not auto-fire at session start, and never edit this file or its own logic from
ledger evidence.

Naming the project: use the matching `mcp-project-context` registered project name if one exists for the working directory; otherwise the working directory's own leaf name. Never the git repository's
top-level directory name — in this workspace unrelated projects share git roots (e.g. `apn`, `me`), so that collides. Use the same string consistently for the same project across invocations, since
Step 0's ledger check below depends on it matching.

## Contents

- [Step 0 — name the assumption (always first, fixed for the whole run)](#step-0--name-the-assumption-always-first-fixed-for-the-whole-run)
- [Verdict](#verdict)
- [Reality contact](#reality-contact)
- [The gate (RED only)](#the-gate-red-only)
- [Output](#output)
- [Stand down (state in one line, no lecturing)](#stand-down-state-in-one-line-no-lecturing)
- [Ledger (RED, waiver, or RED-to-resolved only — never GREEN or AMBER)](#ledger-red-waiver-or-red-to-resolved-only--never-green-or-amber)
- [Project write-back (RED or RESOLVED only — same condition as the ledger)](#project-write-back-red-or-resolved-only--same-condition-as-the-ledger)

---

## Step 0 — name the assumption (always first, fixed for the whole run)

Ask: what unresolved assumption, if false, would invalidate the largest amount of the work about to happen? Choose the highest-blast-radius assumption the proposed expansion MATERIALLY depends on. Do
not descend into deeper assumptions whose answer would not change whether this work should happen now. State it in one line so it can be argued with. Every signal below is evaluated against that one
assumption. If evidence found later proves it was scoped wrongly, correct it explicitly and recompute the verdict — never switch silently.

Then, not before: check `ledger.jsonl` for prior entries on the calling project — if it's missing or unreadable, fall back to that project's own `.wbr-ledger.jsonl` mirror — for an unresolved RED (no
matching RESOLVED) on *this same* assumption just named, not a different one. A project may have more than one unresolved RED open at once if the assumptions are genuinely different; only a match on
the one just named is reused. If a match exists: append a RESOLVED entry now if reality contact for it has occurred since (the `next_test` or an equivalent was actually run); otherwise surface it
as-is — this invocation is a status check, not a fresh run. If there's no match — a newly-developed assumption, even if some other RED is still open for this project — proceed normally below; a new
RED gets its own new entry. Never edit a past entry to reflect new information; append.

## Verdict

RED if any of:
1. No real-world contact has tested the assumption the current expansion depends on.
2. The unverified assumption blocks 3 or more downstream decisions.
3. Available context shows 3+ consecutive work sessions adding surface without new reality contact (unknown, not RED, if that history isn't available).
4. The core capability remains stubbed while peripheral architecture keeps expanding.

AMBER if relevant reality contact exists but doesn't yet resolve the assumption the current expansion depends on. AMBER is information, not withheld permission: expansion may proceed, but state the
unresolved assumption and its closing test. No ledger entry.

GREEN if the current expansion is downstream of sufficiently verified assumptions and no unresolved higher-blast-radius unknown is being bypassed. Adding an unintegrated component is fine; adding one
while something further upstream is untested is not. Be fast and quiet — a gate that always fires gets ignored within a week.

A signal with no available evidence is UNKNOWN and contributes nothing. Never manufacture evidence, session-tracking or counters to resolve a signal.

RED means THIS proposed expansion hasn't earned its prerequisites yet — not that the project is bad. Cite what was observed; don't just agree with whoever is talking.

## Reality contact

Counts: dated, raw output from the real target system — an authenticated API response, a real device or service returning data, a real file processed, a real user completing a task.
Does not count: a mock/fixture, vendor documentation, a plan, a passing test against code the project wrote itself, a governance check, or a model asserting something should work.

## The gate (RED only)

1. Confirm the Step 0 assumption is actually the blocking one; recompute first if not.
2. Define the cheapest real-world test of it.
3. State the disconfirming result BEFORE running it (the step most likely skipped, and the one that stops a failed test being reinterpreted as a reason to build more).
4. Run that test before adding another component, document or framework.

Never emit a plan, design doc or roadmap as the remedy — "let's design this properly first" is the exact pattern being prevented.

## Output

One screen: verdict, the assumption, cheapest test, gate status, one next action.

## Stand down (state in one line, no lecturing)

Irreversible-foundation work where a wrong foundation costs more than delayed verification; design as the deliverable with no downstream implementation to invalidate; reality contact blocked by a
third party (redirect to the cheapest available proxy); deliberate learning projects where building the scaffold is the goal; genuinely cheap throwaway work.

## Ledger (RED, waiver, or RED-to-resolved only — never GREEN or AMBER)

Append one line of JSON to `ledger.jsonl`, alongside this file, in the skill's own directory (create it if absent). Full field reference: [`schemas/ledger-entry.md`](schemas/ledger-entry.md).

On RED:

```json
{"ts":"<ISO 8601, local offset>","project":"<project>","branch":"<git branch, or \"n/a\">","verdict":"RED","assumption":"<the one line from Step 0>","reason":"<which signal(s) fired>","next_test":"<cheapest real-world test>","waiver":false,"learned":null}
```

On resolution, append instead:

```json
{"ts":"<ISO 8601, local offset>","project":"<project>","branch":"<git branch, or \"n/a\">","verdict":"RESOLVED","assumption":"<same assumption>","result":"PASS|FAIL","killed":"<what this invalidated, or none>","learned":null}
```

A waiver is allowed; record it with its reason in `learned` and set `"waiver":true`. Two waivers on the same assumption is itself a finding — say so plainly on the next invocation. `learned` is
capture only: never act on it or use it to modify this skill.

## Project write-back (RED or RESOLVED only — same condition as the ledger)

`ledger.jsonl` is the source of truth. Two appends happen on this condition, both append-only, never edited in place:

1. **Mirror, always:** if `.wbr-ledger.jsonl` exists in the target project's own root, append the same JSON line to it. If it doesn't — whether never created or deleted since — first seed it with
   every one of this project's entries already in `ledger.jsonl` (filtered by `project`), then the current one; self-healing against deletion, not just first-write. Recovery copy only — read only if
   `ledger.jsonl` itself is missing or unreadable; never treated as authoritative while `ledger.jsonl` exists.
2. **Pointer, only if the target project already has its own `SCRATCHPAD.md`:** append one line under its `## Open items` section (never create the file):

```text
- [ ] **skill-walk-before-run RED, <date>** — <the Step 0 assumption, one line>. Next test: <cheapest test, short>. Full entry: `<path to this skill>/ledger.jsonl`.
```

On resolution, append a new line rather than editing the one above:

```text
- [x] **skill-walk-before-run RESOLVED, <date>** — <same assumption>, result: PASS|FAIL. Full entry: `<path to this skill>/ledger.jsonl`.
```

If the target project has no `SCRATCHPAD.md`, skip the pointer silently — the mirror still happens regardless.
