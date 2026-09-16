---
id: benchmark-no-self-grade
type: adr
title: Benchmark never self-grades correctness
status: accepted
created: 20260703_1545
accepted: 20260703_1604
provenance: promoted by skill-ai-it from ROADMAP.md, RUNBOOK
tags: [benchmark, evidence]
---

# Benchmark never self-grades correctness

Decision: the benchmark harness computes only deterministic metrics (files opened, recall, sizes). Answer correctness and unsupported-claim counts require two isolated agent sessions + a blind grader per tests/benchmark/RUNBOOK.md and are never self-graded. The overall benchmark verdict is therefore PARTIAL by construction.
