---
Title: Errors and timeouts
Category: reference
Status: current
Authority: local-supplement
Scope: Error types, translation at seams, exit codes, timeouts on every external call, retries and failure-path cost
Last reviewed: 2026-10-19
Summary: >-
  Typed errors translated at the seam, never swallowed and never matched on a tool's message text outside its seam; a
  timeout on every network call and subprocess; bounded retries; a silent target costs one short probe.
---

# Errors and timeouts

## Errors

| Rule                                                                                                                                       | Why                                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------- |
| Define a small set of the program's own error types (unreachable, auth rejected, timeout, not found, conflict, write refused, unsupported, | Callers branch on meaning, not on text                  |
|   backend error with name and status) in the core                                                                                          |                                                         |
| Each seam translates the tool's or library's errors into those types at the boundary                                                       | Only one module knows the tool's failure shapes         |
| Never match a tool's error message text outside the seam that talks to it                                                                  | Message text changes between versions without notice    |
| No bare catch-all (`except:`, `catch (e) {}` with nothing done, `_ = err`, `.unwrap()` in library code)                                    | A swallowed error turns a failure into wrong output     |
| Services return outcome records that carry their errors; front ends map them to exit codes (CLI) or an error envelope (API)                | One place decides how a failure is shown                |
| Add context when passing an error up (what was being done, to which target), and keep the cause chained                                    | The log line alone should explain the failure           |
| Error messages name the next step where one exists                                                                                         | The reader can act without reading code                 |
| Exit non-zero on any failure; a partial success is reported as such, with counts                                                           | Automation gates on exit                                |
|                                                                                                                                            |   codes ([version-control-and-review.md](version-control-and-review.md)) |

Language idioms differ (exceptions in Python and TypeScript, error values in Go, `Result` in Rust, exit status in shell); the override files map these rules. PEP 8 also recommends against a bare
`except:` because it catches `SystemExit` and `KeyboardInterrupt` (VERIFIED_PRIMARY, PEP 8).

## Timeouts

- Every network call and subprocess has a timeout, taken from settings, not a literal at the call site. Why: a call without a timeout can hang a scheduled job forever (a governed project found 16 of
  96 calls without one; rule R15). The pack's `scripts/call_timeouts.py` finds Python calls without one.
- Size the timeout to the answer: a reachability probe is short; a bulk export is long and stated.
- A scheduled job holds a lock so a manual run cannot overlap it. Why: two runs writing the same state corrupt it.

## Retries

- Retry only operations that are safe to repeat (reads, idempotent writes), a bounded number of times with backoff, and never a login. Why: an unbounded retry loop is an outage amplifier, and a
  repeated login trips lockouts.
- Retry a single transient failure (one end-of-file, one reset) once before calling a target offline. Why: a healthy target can drop one connection.

## Failure paths cost too

A target that does not answer must cost one short timeout, not one per field or per retry. Measure failure paths along with the happy path
([efficiency-and-measurement.md](efficiency-and-measurement.md)). Why: in a scheduled collector, silent units dominated the cycle time (governance "Efficiency is part of done").

## Unknown third-party errors

On an unexpected error from a third-party tool, search its issue tracker and documentation for the exact message before any local workaround. Why: the operator had to research a known upstream bug the
agent should have found (lesson `feedback_proactive_upstream_research`).
