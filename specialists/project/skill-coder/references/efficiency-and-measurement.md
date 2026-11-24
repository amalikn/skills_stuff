---
Title: Efficiency and measurement
Category: reference
Status: current
Authority: local-supplement
Scope: Anything that runs repeatedly or at scale - jobs, collectors, loops over many items, page views over many records, check suites
Last reviewed: 2026-11-19
Summary: >-
  Runtime is an acceptance criterion: state a budget, measure per phase on a real run, design for scale in the first slice
  (reuse connections, batch per host, bounded parallelism, probe first), count failure paths and re-measure when input grows;
  a check suite has a budget and each heavy check its own, and a long job's progress is watched unfiltered.
---

# Efficiency and measurement

Source: governance `validation-and-change-discipline-guide.md` "Efficiency Is Part of Done" (operator, 2026-10-09). The cause was a scheduled job that grew from one site to 37 and from minutes to a
76-minute cycle while every check stayed green, because nothing measured runtime; after the measured fix it ran in 12.5 minutes.

## Rules

| Rule                                                                                                                               | Why                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| State a budget when building (cycle time, per-unit cost, page time); keep it in settings                                           | Without a number, "slow" is never a failure                     |
| Report the measured runtime next to the correctness evidence; green with an unmeasured or over-budget runtime is not done          | Correct and too slow is still broken                            |
| Time each phase on a real run before optimising or claiming a cost; record before and after in the change log                      | Guessing optimises the wrong phase                              |
| Reuse connections: one HTTP session, one SSH master connection, one database session per run or per host, not per item             | Set-up cost dominates small calls                               |
| Batch many reads into one session per host                                                                                         | Round trips cost more than bytes                                |
| Run independent units in parallel with a bounded worker count, and keep a serial switch for diagnosis                              | Unbounded parallelism overloads targets; serial mode makes      |
|                                                                                                                                    |   logs readable                                                 |
| Ask a cheap question before an expensive one (one probe before walking a table)                                                    | A silent unit costs one short timeout                           |
| Never start an interpreter, container exec or remote session per item when one per host or per run will do                         | Process start-up is seconds, not milliseconds                   |
| Re-measure when the input grows; report an unmeasured or over-budget job unprompted with a fix                                     | Growth is when budgets break                                    |
| A measured cause with a fix is merged or recorded as an open item with its numbers, never left only on a branch or in a report     | Findings that do not land are lost                              |
| Optimisation never drops a check, a safety guard or evidence; parallel work keeps one log block per unit and shared state under    | Fast and wrong is worse than slow                               |
|   a lock                                                                                                                           |                                                                 |

## Making it a by-product

Every front end creates a run context (run id, start time, budget); services log structured lines with the run id and time their phases; the run record carries the totals. A breach of budget raises
the project's staleness or monitoring warning. Why: when measurement is built into running, the rule needs no reviewer (a governed project's design, section 13.3 and 13.6).

## Check suites count

A governance check suite has a budget too (the skill-ai-it doctrine sets 10 seconds, with a `--timings` view per family). Why: a slow check gets skipped.

> **Learned 2026-11-06** · check suites, any language · VERIFIED_PRIMARY · Source: apn unified-network-controller
> `scripts/govcheck/checks/flows.py` `FLOW_CHECK_BUDGET_S`, skill-drawio `scripts/flowmap/render_cache.py` (skills_stuff 1a11ce2; 3 min to 11 s) ·
> Falsifier: a suite whose slowest single check stays flat as its input and the tool it calls change.

A suite budget does not protect one expensive check inside it: a drift check that re-rendered a generated drawing grew from 2.3 s to 183 s in
eleven days while the suite had no per-check number, and every commit paid it. Give each check that calls a heavy tool its own budget, printed
with the measured time when passed. When the work is a pure function of its inputs, key it by a hash of every input (the data in order, the
settings, the tool's own source, the interpreter version) and answer from the recorded output hash when the key was seen; a changed or missing
output is still a failure. Profile before fixing: `cProfile` sees only its own process, so profile with the worker pool off, or the table shows
the parent waiting in `connection.recv` instead of the work.

```python
# skill-drawio scripts/flowmap/pages.py evaluate (skills_stuff 1a11ce2)
k = render_cache.key(data, profile)            # data, profile, engine source, Python version
if not need_text:
    known = render_cache.lookup(k)
    if known is not None:                      # seen before: compare hashes, do not render
        return Outcome(drift=current is None or render_cache.text_hash(current) != known)
text = render(data, profile, built)
render_cache.record(k, text)
```

> **Learned 2026-11-09** · long jobs piped through a filter · VERIFIED_PRIMARY (observed) · Source: skill-vagrant box archive session 2026-11-09 (`python3 archive_boxes.py --apply | cut -c1-200` run in the background) · Falsifier: a progress line that reaches the log while `cut` is still reading
> A progress line flushed by the program still waits in the next pipe stage: `| cut -c1-200` held every `ok` line of a two-hour job until the
> job ended, so a monitor tailing the log saw nothing and the run looked stalled while a 9.2 GB file had already landed. Watch a long job's
> unfiltered log, or make every filter line-buffered (`grep --line-buffered`, `awk` with `fflush()`); `cut` and `head` cannot be.

> **Learned 2026-11-24** · agent work, any project · VERIFIED_PRIMARY (measured) · Source: continuum DL-213, docs/reference/efficiency-log.md (tools_stuff e6bd1b1, 8f783aa) · Falsifier: a week of the record where the agent's foreground waits and idle turns stay unseen
> Time every activity, the agent's own included, or drift stays invisible. A 30-day backfill of one project's session transcripts found
> 127 agent tool calls over 2 minutes, mostly the agent blocking in the foreground on a push gate ("Wait for ... push", about 10 min each),
> and a same-day 34-minute idle after the agent ended its turn with work waiting. Record each finished activity as one JSON line (start, end,
> seconds, actor agent|operator|project, kind, name, ref, exit, log); keep the person's time (answering, waiting) apart from agent time; budget
> per group in an authored TOML; flag drift as a 7-day median past 1.5x the 28 days before. Capture the agent through Claude Code hooks
> (PreToolUse marks the start by `tool_use_id`, PostToolUse/PostToolUseFailure emit; UserPromptSubmit and Stop give turns and waits; run them
> `async`, the hook costs about 90 ms), scripts through their run wrapper, CI through per-step timings, and past days with
> `scripts/agent_timing_backfill.py`. Long-running services are started detached with a ready wait and a status command, never as a session
> task, and their start-up has a budget while their lifetime is report only. Parallel independent CI jobs (native and Linux) cut a push from
> 438-527 s to 281-299 s with the same tests.

```python
# continuum scripts/timing/hook_timing.py (tools_stuff e6bd1b1): one hook script for every event; never blocks the tool call
if event == "PreToolUse":
  mark(key(payload), {"t": now, "tool": tool, "name": summary(tool, payload.get("tool_input"))})   # key = tool_use_id
elif event in ("PostToolUse", "PostToolUseFailure"):
  start = take(key(payload))
  if start:
    kind = "operator_answer" if tool in OPERATOR_TOOLS else "tool"            # AskUserQuestion is the person's time
    finished(start["t"], now, kind, start["name"], payload, tool=tool, ok=event == "PostToolUse")
elif event == "UserPromptSubmit":
  stop = take(f"stop-{session}")
  if stop:                                                                     # the agent had ended its turn
    finished(stop["t"], now, "operator_wait", "agent turn ended; waiting for the operator", payload)
  mark(f"turn-{session}", {"t": now})
elif event == "Stop":
  start = take(f"turn-{session}")
  if start:
    finished(start["t"], now, "turn", "prompt to stop", payload)
  mark(f"stop-{session}", {"t": now})
```
