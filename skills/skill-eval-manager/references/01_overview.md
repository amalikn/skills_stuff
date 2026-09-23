# Evaluation suite method

## Contents

- [Purpose](#purpose)
- [Artifact model](#artifact-model)
- [Core invariants](#core-invariants)
- [Execution boundary](#execution-boundary)
- [Source status](#source-status)

## Purpose

An operational evaluation is not merely a test command. It is a falsifiable claim about a stated population, established through an independent oracle at a named layer, recorded with a verdict whose
validity expires. The method makes false confidence visible before it is reported as system truth.

## Artifact model

```text
Suite -> EvalDefinition -> EvaluationRun -> Observation -> Verdict
                                          \-> append-only HistoryStore -> derived Report/Scorecard
```

The suite is a definition, not evidence. An external executor—command, query, service, or manual procedure—produces an observation. `record_result.py` records that observation in JSONL.
`render_report.py` selects the latest observation for each declared eval/slice and calculates its current state.

## Core invariants

1. Evidence rank must be at least the claim rank. Names can change; the order cannot be bypassed.
2. An oracle must be independent and must not route through the path being evaluated.
3. Population and denominator source must be declared independently of successful processing.
4. Every eval must carry dated falsifiability evidence.
5. The only stored verdicts are `pass`, `fail`, `inconclusive`, `error`, and `blocked`.
6. History is append-only. A correction is a new observation with `supersedes`, never an edit.
7. `stale` and `not_evaluated` are report-time states, never history values.

## Execution boundary

The package validates definitions and records outcomes; it does not execute the `executor.ref`. A `manual` executor means an operator may follow a procedure and record a result. Tier and runner
communicate who is permitted to do that work. The scripts do not schedule, retry, parallelize, invoke plugins, or access a project system.

## Source status

The controller mapping is based on a read-only planning document supplied by the operator. Its own header says it is a plan rather than a record of work, so all example outcomes are marked synthetic
and no live behavior is claimed. The prompt's FOSS survey is `USER_STATED`; this package does not repeat it as independently verified research.
