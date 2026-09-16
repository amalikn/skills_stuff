# Token-Efficiency Benchmark Runbook

This runbook defines the **full** benchmark. The automated harness
(`ansible-repo-intelligence benchmark`) computes only the **deterministic**
half. The remaining metrics — answer correctness, unsupported-claim count, and
time-to-first-relevant-file — require two **isolated agent sessions** and a
**blind grader**, and MUST NOT be self-graded by the session that produced the
answers. Until that external step runs, the benchmark verdict is **PARTIAL**.

## Metrics

| Metric | Source | Automated? |
|---|---|---|
| source files opened | harness (indexed) + grep proxy (baseline) | ✅ |
| retrieval recall vs gold files | harness | ✅ |
| repository-map size | harness | ✅ |
| query-result size | harness | ✅ |
| input tokens consumed | agent session logs | ❌ external |
| time-to-first-relevant-file | agent session logs | ❌ external |
| answer correctness | blind grader vs gold | ❌ external |
| unsupported-claim count | blind grader vs gold | ❌ external |

## Deterministic half (run now)

```bash
ansible-repo-intelligence scan --repo <repo> --output <repo>/.ai-context --offline
ansible-repo-intelligence benchmark \
  --repo <repo> --context <repo>/.ai-context \
  --questions tests/benchmark/questions.ansible_wifi.yaml \
  --report benchmark-report.yaml
```

Latest run (ansible-wifi, 22 questions): baseline 3519 files vs indexed 117 →
**96.7% fewer**; indexed recall **100%**; map 415 lines; mean query ~1.3 KB.

## External half (two isolated sessions + blind grading)

### Isolation requirements

1. **Same** model, model version, system instructions, tool permissions and
   repository revision for both runs.
2. **Baseline run**: a fresh agent session with **no access** to `.ai-context/`
   and no benchmark tooling. It answers each question by ordinary repo search.
3. **Indexed run**: a separate fresh agent session that reads
   `ANSIBLE_REPO_MAP.md` and uses bounded `query`/`impact`, then opens source.
4. The **same session must not execute and grade both sides.**

### Capture per question, per run

- the prompt and final answer
- every source file opened (path list)
- every query/impact command issued
- elapsed time and input/output token counts

### Gold answers

Each question in `questions.ansible_wifi.yaml` has `gold_files` (required source
grounding) and `keywords`. Extend each with, for grading only:
`acceptable_answer_points` and `disallowed_unsupported_claims`. Keep the grading
key **separate** from the run inputs.

### Grading

Grade with EITHER:
- a human reviewer, OR
- a **separate blind** grading process that does not know which transcript is
  baseline vs indexed (shuffle + anonymise the two transcripts first).

Score: answer correctness (0/1 per question against acceptable points),
unsupported-claim count (claims not grounded in opened source / gold).

### Acceptance thresholds (empirical targets, not guarantees)

```
>= 60% fewer source files opened            (harness: 96.7% MET)
>= 40% lower input-token usage              (external; proxy strongly positive)
>= 95% retrieval recall for gold files      (harness: 100% MET)
no reduction in answer correctness          (external — REQUIRED)
no increase in unsupported claims           (external — REQUIRED)
repository map within size budget           (harness: 415/1000 MET)
query results within node/depth limits      (harness: MET)
```

If correctness drops or unsupported claims rise in the indexed run, report
`PARTIAL`/`NOT READY` and identify the cause. Do not declare `READY` on the
deterministic half alone.

## Why this is PARTIAL in a single session

A single automated session cannot run two *isolated* agent sessions and then
*blindly* grade itself without bias. Per the implementation contract, doing so
is forbidden. The harness therefore stops at the deterministic metrics and this
runbook hands the rest to an external operator.
