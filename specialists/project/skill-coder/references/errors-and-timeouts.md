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

## Contents

- [Errors](#errors)
- [Timeouts](#timeouts)
- [Retries](#retries)
- [Failure paths cost too](#failure-paths-cost-too)
- [Unknown third-party errors](#unknown-third-party-errors)
- [Bounded fetching and absent values](#bounded-fetching-and-absent-values)

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
- A timeout ends everything the call started. `subprocess.run(timeout=)` kills only its own child: an `ssh` through a ProxyCommand, `scp`,
  `rsync` or a shell leaves its children running. Start such a command in its own session and end the process group on timeout. Why: proxies
  piled up on a host after each timed-out read (Learned below). The pack's `scripts/group_timeouts.py` finds the Python calls that do not.
- The same holds for a `Popen` stopped by hand at a deadline: start it with `start_new_session=True` and end the group, SIGTERM first so the child
  can close what it detached (an `ssh -f` forward leaves the group and is found only by the child's own record of it), then SIGKILL after a
  grace. `group_timeouts.py` counts a `Popen` stopped with `.kill()`/`.terminate()` that did not start its own session.
- A program stopped from outside (its SIGTERM handler about to exit) also ends the children it started in sessions of their own, which its
  caller's group kill cannot reach: keep them in a registry and end each group before cleaning up by name. Measured on a live host
  (2026-10-20): without it, one `ssh -f` still connecting at the stop outlived it; with it the handler reported "ended 1 start(s) in flight,
  closed 23 forward(s)" and nothing was left. Unified-network-controller `src/unc/drivers/transports/process.py` `end_all` (commit 3f3bfcb):

  ```python
  with _ACTIVE_LOCK:                       # run() adds each child on start and removes it on exit
      procs = list(_ACTIVE.values())
  for proc in procs:
      _signal_group(proc.pid, signal.SIGTERM)   # then SIGKILL after the grace, as end_group does
  ```

> **Learned 2026-10-20** · Python subprocess, ssh through a ProxyCommand (Teleport `tsh proxy ssh`) · VERIFIED_PRIMARY (reproduced with `ProxyCommand=sleep`: after `run(timeout=1)` the sleep was still alive; with the group runner it was gone; run on macOS and on the Linux host) · Source: unified-network-controller `src/unc/drivers/transports/process.py`, `tests/test_transport_process.py` (commit 3efcb27) · Falsifier: an ssh release that ends its ProxyCommand when ssh itself is killed with SIGKILL
> `ssh` starts the ProxyCommand as its own child; SIGKILL to ssh cannot pass anything on, so the proxy stays until its own idle exit (ten
> minutes and more seen, host load rising with each timed-out read). Start the child with `start_new_session=True`, and on timeout signal the
> group (SIGTERM, then SIGKILL after a short grace); reap the leader before testing the group, and on macOS treat EPERM from `killpg(pgid, 0)`
> as "gone" (a group holding only the leader's zombie answers EPERM). Move every such call site in one pass, and move any test that patched
> `subprocess.run` to the new seam, or it silently runs the real command.
>
> ```python
> # unified-network-controller src/unc/drivers/transports/process.py (commit 3efcb27)
> with subprocess.Popen(argv, start_new_session=True, **kwargs) as proc:
>     try:
>         out, err = proc.communicate(input, timeout=timeout)
>     except subprocess.TimeoutExpired as exc:
>         end_group(proc, grace)            # killpg SIGTERM, wait up to grace, killpg SIGKILL
>         try:                              # pipes close once the group is gone
>             out, err = proc.communicate(timeout=grace)
>         except subprocess.TimeoutExpired:
>             proc.kill()
>             out, err = exc.output, exc.stderr
>         raise subprocess.TimeoutExpired(argv, timeout, out, err) from None
> ```
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

## Bounded fetching and absent values

> **Learned 2026-10-29** · fetchers that can fan out (scrapers, API walkers) · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal research project) · Source: project_stuff/me vehicle-import track `scripts/README.md` (prestige_auction_search row); RFC 6585 section 4 (429) · Falsifier: an uncapped fetcher that has run at scale without throttling or a ban
> Any fetcher that can fan out needs, from its first version: hard caps on results and detail fetches (here 500 and 250), an explicit
> confirmation with an ETA above a threshold (here 200), jitter and paced batches (50 per batch, random 30-60 s gaps), and exponential
> backoff on 429 and 5xx. Parse the site's own vocabulary (status values) live rather than hard-coding it.

> **Learned 2026-10-29 (b)** · output of missing, zero and filtered-empty values · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal research project) · Source: project_stuff/me vehicle-import track `scripts/README.md` (fx_rate, prestige_auction_search rows) · Falsifier: a report where a missing value, a zero and an empty filter result render the same and nobody was misled
> Absent, zero and filtered-empty must never render the same. A missing rate fails rather than printing nothing or 0; a filtered query
> that returns nothing says so (and may fall back to the unfiltered set, saying it did), because "empty after the filter" is
> indistinguishable from "no data" otherwise.
