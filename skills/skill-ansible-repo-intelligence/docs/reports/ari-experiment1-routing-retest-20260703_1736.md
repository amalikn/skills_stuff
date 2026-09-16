# Experiment 1 Routing Retest — q21 Fix Verification

Status: COMPLETE
Date: 2026-07-03
Prompt executed: `docs/prompts/close-experiment1-and-run-expermient2.md`, Parts 1–2 only
(Gate A). Part 3+ (Experiment 2 / playbook-digest decision) not run in this pass.

## Routing change

Root cause (from the original external benchmark): q21 ("Where do per-host
topology variables come from?") was answered from the role action digest
instead of variable/vars-plugin evidence — a routing failure, not a parser or
graph defect.

Fix: a new deterministic, offline question router.

- `src/ansible_repo_intelligence/routing.py` — pure function
  `classify_question(text) -> RouteResult`. No I/O, no graph load, no tool
  execution — it only *recommends* a command. Priority order checks
  variable-precedence / vars-plugin / variable-origin keyword classes **before**
  role-config keywords, so the q21 keyword shape ("topology", "configure"-style
  phrasing) can no longer fall through to the role digest.
- `ansible-repo-intelligence route "<question>"` CLI subcommand
  (`cli.py::cmd_route`) — advisory only (`executes: false` always emitted).
- `SKILL.md` — new **"Variable-origin routing (mandatory)"** section stating the
  rule verbatim, listing covered question patterns, and documenting `route`.

## Affected files

- `src/ansible_repo_intelligence/routing.py` (new)
- `src/ansible_repo_intelligence/cli.py` (new `route` subcommand + `io` import)
- `tests/unit/test_routing.py` (new, 16 tests)
- `SKILL.md` (routing rule section)

## Test results

- `tests/unit/test_routing.py`: 16/16 passed.
- Full suite: **80/80 passed**, no regressions.

## Live end-to-end proof (ansible-wifi)

```text
$ ansible-repo-intelligence route "Where do topology vars come from?"
category: relationship_query
subtype:  variable_origin
rule_id:  ROUTE-VAR-ORIGIN
recommendations:
  - query variable <name>
  - query vars_plugin <name>
executes: false

$ ansible-repo-intelligence query vars_plugin topology --context .ai-context
  - [vars_plugin] topology_vars (high, dynamic) vars_plugins/topology_vars.py
  - [variable] topology_bridges ... vars_plugins/topology_vars.py:vars_plugin
  - [variable] topology_interfaces ... vars_plugins/topology_vars.py:vars_plugin
  ...
```

Correct answer surfaced directly — no source file needed.

## Benchmark isolation

Three independent, freshly-spawned agents, no shared context:

- **Run A (direct baseline)** — ordinary repo navigation only; `.ai-context`,
  ARI CLI, and `ANSIBLE_REPO_MAP.md` explicitly forbidden.
- **Run B (digest + routing)** — mandatory workflow: `route` first, then the
  recommended `query`/`impact` command, for all 22 questions; source reads only
  for genuinely insufficient/⚠verify-flagged facts.
- **Run C (blind grader)** — independent third context, given only anonymized
  `id: answer` pairs (relabeled RunX/RunY, order randomized, no methodology
  metadata), graded against actual repo source. The coordinator did not grade.

Input to the answering agents was the 22 questions **stripped of `gold_files`**
(the gold-answer benchmark asset embeds gold source paths inline) to prevent
answer leakage.

## Full scorecard

| Metric | Direct (Run A) | Digest+routing (Run B) |
|---|---|---|
| Correctness (blind-graded) | 22/22 | 22/22 |
| Unsupported claims (blind-graded) | 0 | 0 |
| Distinct source files opened | 38 | 0 |
| Map reads | n/a (forbidden) | 0 |
| Full graph reads | n/a (forbidden) | 0 |
| Tool calls | 12 | 46 |
| Subagent tokens (proxy, not a true input-token isolate) | 131,725 | 131,795 |

q21 evidence: both runs correctly identified `vars_plugins/topology_vars.py` as
the source of per-host topology variables (blind grader confirmed explicitly).
q05 evidence: both runs correctly identified Asterisk as source-compiled
(download/build), not package-installed — the error from the original external
benchmark did not recur in either run.

## Gate A verdict (per prompt Part 2 / Part 6)

```text
correctness: 22/22                          -> PASS
unsupported claims: 0                        -> PASS
source files opened: 0 (Run B)               -> PASS (no worse than prior digest)
no mandatory map read                        -> PASS
no full graph read                           -> PASS
q21 answered from variable/vars-plugin evid. -> PASS
tokens: no higher than direct baseline       -> PARITY, not improvement (+70
                                                 tokens on Run B; within noise
                                                 of this measurement method,
                                                 not a clean win — do not claim
                                                 token savings from this rerun)
```

**Gate A: PASS.** All required correctness/routing/bounds criteria met. Token
parity is reported honestly as a tie, not a win — this rerun's token figures
use live-agent `subagent_tokens` totals (includes reasoning/tool-output
tokens), not the isolated prompt-token measurement the original Experiment 1
report used, so the two are not strictly comparable; treat the 78.8k/79.1k
figures from the original report as the reference, and this rerun's token
numbers only as a rough sanity check, not a re-validated figure.

## Limitations

- Token counts here (`subagent_tokens`) are a coarser proxy than the original
  Experiment 1's isolated input-token measurement — not apples-to-apples.
- Digest+routing workflow costs more tool calls (46 vs 12) for zero source
  reads — a real tradeoff, not hidden.
- This report closes Gate A only. Experiment 2 (relationship-heavy benchmark,
  Parts 3–6 of the prompt) has not been run; the Playbook Execution Digest
  decision (Gate D) remains open and undecided.

## Final verdicts (per prompt "Final verdicts" section — partial, Gate A scope only)

```text
Role action digest: READY
Variable-origin routing: READY
Experiment 1 direct-question efficiency: VALIDATED (correctness/files/bounds);
  token claim: PARITY, not re-validated as a savings claim by this rerun
Relationship-query correctness: not yet assessed (Experiment 2 not run)
Experiment 2 relationship efficiency: NOT YET RUN
Routed hybrid workflow: NOT YET RUN
Playbook Execution Digest: UNDECIDED — Gate D not evaluated
General token-savings claim: VALIDATED FOR SPECIFIC CLASSES (per original
  Experiment 1 report), not re-validated by this rerun's coarser token proxy
```
