Title: Spec 0006 — Runner qualification before evidence is spent
Category: design-contract
Status: proposed
Proposed: 20260902_1140 direct, per .archcore/README.md step 2
Source: docs/holdout24-analysis-20260902_1120.md
Summary: An external runner is qualified on disposable cases before any single-use corpus is run through it, and the harness must be able to describe a failure it did not cause.

# Spec 0006 — Runner qualification before evidence is spent

## Why

Holdout 24 lost **5 of 24 cases (21%)** to five consecutive `claude -p` invocations exiting 1 with empty stderr. The scorer handled it exactly right — excluded from both denominators, uncorrected
figures printed alongside, per [rule 0008](../rules/0008-execution-errors-are-not-scores.md) — but a single-use corpus cannot lose a fifth of itself and still be complete evidence. The routing system
did not fail that holdout. **The execution pipeline failed to complete it.**

Two distinct defects, and they need separating:

1. **Reliability.** A 24-call sequence against an external runner was not known to be survivable, and was not tested before being spent.
2. **Observability.** `execution-error:command exited 1:` is the entire diagnostic, because the harness records only stderr on a non-zero exit. A runner that fails silently produces evidence that
   cannot be classified as quota, transport, parse or timeout — which is the difference between a fixable fault and a mystery.

## Contract

**No single-use corpus is run through an unqualified runner.** A runner is qualified for a corpus of N cases when, immediately before the run and against DISPOSABLE cases only:

| Property             | Requirement                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Sequence reliability | ≥ N consecutive invocations complete with exit 0. Not N distinct cases — N calls, to expose quota and session limits      |
| Parse reliability    | Every reply yields a plan object the harness can extract. A reply that parses to nothing is a failure, not a bad route    |
| Failure legibility   | A deliberately induced failure produces a diagnostic naming the class. If the harness cannot describe it, it is not ready |
| Timeout behaviour    | A call exceeding the timeout is recorded as an execution error and does not stall the sequence                            |
| Labels               | provider, model and runner are supplied. An unlabelled row is not comparable to anything                                  |

Qualification is **per runner, per arm, and perishable** — it expires when the runner, its credentials, its quota state or the harness changes. It is evidence about the pipeline on a day, not a
property of the project.

## Pre-registered acceptance rule — recorded 20260902_1300, before the first real qualification

**100%, or it is not qualified.**

| Outcome class    | Permitted |
| ---------------- | --------: |
| `ok`             | N of N    |
| `silent-failure` | 0         |
| `nonzero-exit`   | 0         |
| `timeout`        | 0         |
| `unparseable`    | 0         |

Runner failures are infrastructure faults, not model-quality variance, so there is no tolerance band to argue over: a single silent failure in N calls is sufficient evidence that the execution path is
not dependable enough to spend a blind corpus through. A partial pass is a fail, and the response is to classify the failure pattern, fix the transport, session or quota condition behind it, and
**requalify from zero on N fresh disposable calls** — never to resume a part-finished sequence.

## The receipt binds to what it qualified

A receipt authorises a run only when the provider, model, runner, **command** and **`harness_sha`** all match the run being attempted, and its `qualified_for_corpus_size` is at least the corpus size.
A receipt earned with one command does not transfer to another, and a harness edit invalidates every outstanding receipt — the harness is part of the execution path being qualified, not a neutral
observer of it.

## Amendment 1 — 20260902_1330: payload size is part of what is qualified

Recorded as a dated, reasoned amendment, per this spec's own rule that a threshold may not move silently.

The first real qualification run passed **60/60 clean, median latency 9.48s** — and then measurement showed the probes were **761× smaller than a real evaluation prompt**: 64 characters against
48,730, because a real prompt pastes the entire routing catalogue. Sixty of each differ by roughly **730,000 input tokens**.

That matters because **quota exhaustion is driven by token volume, not call count**, and quota is the most likely explanation for the five consecutive silent failures in holdout 24. A trivial-probe
run therefore qualifies transport, JSON parsing, exit-code handling and session survival across a 60-call sequence — all real properties — and says essentially nothing about the failure mode that
caused the incident this spec exists to prevent.

**Amendment:** probes are padded to a real prompt's token profile by default (`--payload realistic`, which prepends the routing catalogue as explicitly ignored material — no corpus case is ever sent).
The receipt records `payload` and `probe_chars`, and a receipt earned on trivial probes **does not authorise a full-prompt run**. `--payload trivial` remains available for transport-only checks and
says so in its output.

The 20260902_0555 receipt stands as an honest record of what it tested. It no longer authorises the development-60 sweep, and the guard enforces that.

## Disposable cases only

Qualification burns calls, so it must never burn corpus. Use throwaway prompts that exercise the same path — prompt construction, invocation, JSON extraction, scoring — without consuming a case whose
independence matters. `routing-eval-ping` is the shape; qualification is the same idea run N times and counted.

## What this spec does NOT claim

It does not claim the routing architecture needs redesign. Holdout 24 scored **16 of 19** on the rows it did produce, with zero missed gates. The gap is in the evaluation pipeline's reliability and in
its ability to describe its own failures, and the fix belongs there.
