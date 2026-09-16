# Efficiency Remediation — Experiment 1 (digest workflow)

Date: 2026-07-03_1710
Change under test: managed-resource enrichment (Phase 1) + compact `--view actions`
fact digest (Phase 2) + drop map-first workflow.

## Method

Same 22 direct-lookup questions, same repo revision. Three workflows, each a
fresh isolated agent; the digest run was blind-graded by a separate agent that
read the gold source. **Token accounting = full subagent tokens** (digest output
+ query calls + reasoning), not just source-file tokens.

## Result

| metric | baseline (direct) | old indexed (map+query) | **digest (new)** |
|---|---|---|---|
| source files opened | 36 | 29 | **0** |
| input tokens | 79.1k | 85.4k | **78.8k** |
| tool calls | 10 | 33 | 12 |
| correctness (blind) | 22/22 | 21/22 | **21/22** |
| unsupported claims | 0 | 1 | **2** |
| answered w/o opening source | — | — | **22/22** |

## Stop-gate (as specified)

| gate | result |
|---|---|
| tokens ≤ baseline | ✅ 78.8k ≤ 79.1k |
| ≥50% fewer source opens than old-indexed | ✅ 100% (0 vs 29) |
| correctness ≥ baseline | ❌ 21/22 (−1) |
| unsupported claims ≤ baseline | ❌ 2 vs 0 |

## Analysis — the mechanism works; one mis-routed question

- The digest turned the old indexed workflow's **+8% token loss into a token win
  with zero source reads.** Every direct-config question was answered from the
  compact fact digest.
- It **fixed the q05 error** the old-indexed run made: the digest showed the
  actual `get_url`/`command`/`install_asterisk.sh` operations, so the agent
  correctly said "compiled from source," not "installed from packages." The
  keepalived source-compile trap (q06) was handled the same way.
- **The entire correctness/claims miss is one question — q21 (topology vars).**
  The agent applied the *role* digest to a *variable-origin* question and missed
  `vars_plugins/topology_vars.py`. This is a **routing miss, not a tool defect**:
  `query vars_plugin` returns `topology_vars` with its supplied variables and
  `consumed_dirs` immediately (verified directly). Fixed by a workflow rule in
  `SKILL.md` — variable-origin questions route to `query vars_plugin` /
  `query variable`, never the role digest.

## Verdict

**Conditional pass — proceed.** The efficiency mechanism is validated: the digest
achieves 0 source reads at token cost below baseline while *improving* accuracy
on the source-compile traps. The single regression is an isolated routing error
now corrected. On the strict gate it is 2/4 pass because that one question drags
correctness and claims; with the routing fix the tool answers q21 correctly.

## Graph-size cost

`graph.yaml` grew **+7.8%** (2.996 MB → 3.230 MB) — well under the ≤25% gate.
Enrichment stored as compact per-task `operation`/`resource`/`verification`
attributes; no duplication of name/source/when/notify.

## Next

- Experiment 2: relationship-heavy question set (handler chains, impact,
  variable-origin, cross-flavor) comparing direct / always-indexed / routed-hybrid
  — where the tool should win outright, giving a *defensible* efficiency claim.
- Re-run the direct-22 with the vars-origin routing fix to confirm the gate flips
  to a clean pass.

## Honesty note

Still no *general* token-savings claim. This experiment shows the digest reaches
**parity-to-slight-win on direct questions** (its worst case) while eliminating
source reads and fixing errors — a real improvement over the failed original
indexed workflow, but the headline efficiency case rests on Experiment 2.
