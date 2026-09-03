Title: Guide 0003 — Running and reading a routing baseline
Category: operating-guide
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: MEMORY.md
Summary: Freeze the inputs, stamp provenance per row, exclude execution errors, and measure closure on stored plans before spending a live run.

# Guide 0003 — Running and reading a routing baseline

## Procedure

1. **Freeze the prompt inputs** and print their SHAs **after the last edit, not before**. Publishing them and then editing is the commonest way to invalidate a run's provenance. Record them in
   `MEMORY.md` and verify with **`just freeze-check`** before every run whose numbers will be compared to a recorded baseline or spent on a single-use holdout — it exits non-zero and names the
   artifact that moved. The freeze covers five files, including `scripts/close_route.py`, which changes the scored route without ever reaching the prompt.
2. **Smoke-test every new runner arm on one case** before spending a full set. A mis-invoked command scores 0.0 and looks like a bad model.
3. **Run per family**, and read the coverage line the harness prints — `covered X/Y cases`, with a `WARNING: partial corpus run` when `--limit` truncated a family larger than it. A partial run is a
   smoke test, never a baseline.
4. **Never edit a frozen file mid-run.** If a contradiction is found, kill the run rather than finish it; a stamp that needs an argument to defend is not doing its job.
5. **Measure closure on stored plans first** — `--rescore <glob> --repair` costs no model calls and isolates a catalogue change from a behaviour change.
6. **Read the failure-stage histogram, not its mean.** Averaging an ordinal ladder assumes stage 1→2 equals 4→5.
7. **Report both denominators** when any execution error occurred.

## The scorer is part of the freeze

A baseline is a measurement of a route BY a scorer. Changing either one changes the number, so the harness hash covers the scorer and `just freeze-check` verifies it. Fix a scoring defect **before**
authoring a single-use holdout, never after: a holdout scored under a scorer you then correct has been spent and has answered nothing. This is why the asymmetric-gate fix ([rule
0011](../rules/0011-gate-errors-are-asymmetric.md)) preceded the unseen corpus rather than following it.

## Why this is a guide and not a checklist

Every step here exists because skipping it cost a run. The `--limit` truncation produced a 53-of-60 baseline that read as complete.
