---
Title: Systems validation record
Category: validation-evidence
Status: current
Authority: observed-local-validation
Scope: Portable architecture skill pack version 1.0.0
Last reviewed: 2026-10-29
Summary: Executed local checks, scenario observations and explicit untested areas.
---

# Systems validation record

## Observed checks on 2026-10-29
- Official bundled skill-creator quick_validate.py accepted this skill.
- Markdown frontmatter and optional UI YAML parsed with PyYAML 6.0.3 from an existing local cache.
- Ruff 0.17.3 syntax/import/error checks passed; formatting was applied and checked again before release.
- CLI tests passed, including genuine negative inputs, malformed values, manifest tampering, missing/extra files, unsafe paths, dry-run write boundaries and symlink refusal.
- Local package checker was exercised with a missing-link fixture (nonzero) and repaired fixture (zero).
- Shared architecture, collaboration, automation, diagram, tool-selection and research references are identical across the two folders.
- All seven named optional specialist skills appear with outbound and inbound ownership contracts.
- A separate reviewer read all 62 Markdown files present before these two result records and found no actionable architecture/handoff defect after corrections.

## Arithmetic and runtime evidence
Network CLI suite: six test methods passed in 0.969 seconds; parameterized subcases cover valid IPv6, /31 and /32,
routing-scope reuse, nested/duplicate overlap, gateway semantics, invalid schema and size bounds.
Systems CLI suite: seven test methods passed in 0.803 seconds; subcases include failed-domain memory, headroom,
restore units/efficiency/fixed time, invalid numbers/references and common manifest tests.
These durations are observations of that run, not guarantees for another machine. Fresh full checks were rerun after assembly.

| Scale probe | Population | Helper-reported time | End-to-end process time | Result |
| --- | --- | --- | --- | --- |
| Network | 5,000 concrete segments | 0.020496 s | 0.0542 s | No findings, exit 0 |
| Systems | 1,000 nodes and 5,000 explicit scenarios | 0.250140 s | 0.2932 s | No modeled shortfall, exit 0 |

Authored runtime budget was 5 seconds per local command; these deterministic probes met it on this workstation.
They do not benchmark network probes, device changes, API latency or real workload scheduling.
Synthetic capacity used uniform 64 GiB nodes with 8 GiB reserve and one failed ten-node domain per scenario.
Input caps and file-size bounds remain enforced.

## Behavioral application
A fresh evaluator read both skills and applicable references, then answered two integrated requests:
1. Three-node Proxmox/rack failure plus 1 TiB recovery over a shared 1 Gbit/s link.
2. Overlapping office addressing, WireGuard, 200-device firewall rollout and pressure to use Nautobot as the architecture.
It also applied inbound handoffs from skill-smc for an undated ansible-wifi report and from skill-coder for an uncertain API write.

Observed response excerpts:
- “Lose rack A | 48 GiB | 92 GiB short.”
- “The transfer-only minimum for 15 minutes is approximately 9.77 Gbit/s, leaving no time for detection, startup or validation.”
- “Use Nautobot to represent agreed architecture and ownership.”
- “A timed-out API write has an unknown outcome.”
- “Offline without timestamps is an observation of unknown freshness, not established current device failure or retirement intent.”

Assessment against relevant case expectations: correct arithmetic, explicit feasibility limits, tool neutrality,
bounded rollout, actual-service acceptance and bidirectional ownership; no case-critical failure observed.
No aggregate numerical score is asserted. S01/S02 and N01 were tested together in the integrated prompts; N08 and S07 were applied as inbound handoffs.
The remaining cases in cases.json are authored regression scenarios, not executed passes.

## Baseline and improvement limits
A separate without-skill baseline already identified the key shortfalls and safe rollout behavior:
- “48 GiB usable after reserve ... a 92 GiB shortfall.”
- “WireGuard encryption does not resolve that ambiguity.”
Therefore this run does not establish an improvement over the baseline or prove that these safeguards depend on the skill.
The skills' broader domain coverage and future routing behavior need evaluation in actual use.

## Corrections from review
The initial review occurred during assembly and found eval/catalogue links whose targets were not yet written.
The completed assembly includes those files and local-link checking.
The review also prompted explicit treatment of changing quorum membership and inconclusive read-after-write; both are now documented.
A second read-only pass confirmed those corrections and coherent peer/specialist ownership.

## Residual limits
No live Codex or Claude Code discovery test, local-LLM runtime test, specialist invocation, radio/server/network/controller access,
hypervisor failure, real backup restore or production deployment was performed.
The two-way protocol is available to specialist maintainers; existing specialist installations were not modified.
Apple direct retrieval was rate-limited; exact Apple implementation behavior remains unverified.
Upstream source references are dated moving branches/pages, not immutable pins.
Offline checks establish package integrity, input handling and arithmetic, not operational correctness across every domain.

## Rerun on v2.0.0, 2026-10-29

Method: every case in cases.json (both packs, 22 cases) answered twice by fresh agents of the same model: once with no skill access
(baseline), once following SKILL.md with its references and helpers. The two answers per case were shuffled and labelled X/Y; a separate agent
graded them blind against rubric.md, the expected points and the critical failures, and rechecked every calculation. The key was applied after grading.

| Pack | Baseline mean /16 | With skill mean /16 | Cases won by skill | Baseline critical failures | Skill critical failures |
| --- | --- | --- | --- | --- | --- |
| skill-systems-architect | 11.67 | 14.75 | all | see below | 0 |

Per case (baseline/skill): S01 13/15, S02 12/15, S03 10/15, S04 12/15, S05 12/14, S06 12/15, S07 12/15, S08 11/14, S09 12/15, S10 10/15, S11 13/15, S12 11/14.
No critical failure on either side in the systems cases.
Across both packs: skill 22 of 22 cases, mean 14.59 vs 11.55; 22 of 22 skill answers reach the 12/16 acceptance bar against 13 of 22 baseline.
All arithmetic in both answer sets checked out (link budget, availability, MTU/MSS, memory, restore, queueing).

Trigger proxy (evals/trigger-cases.json, both packs, 39 unique prompts): a fresh agent shown only the competing skills' descriptions chose the
expected owner for 38 of 39. Miss: "Show the pvecm command output format" went to skill-systems-architect (no Proxmox platform pack exists to
take it). This is a description-only proxy, not live host discovery.

Limits: one run per case; answerers and grader are the same model family; S01 and S02 reuse the numbers of the pack's own worked examples
(capacity-plan.json), so those two cases can be answered by copying; replace them with fresh numbers before the next run. Gaps the with-skill
agents reported are listed in SCRATCHPAD.md next actions.

## Fair rerun, 2026-10-29 (baseline given the specialist registry)

A side review pointed out that the Interfaces criterion rewards naming the operator's specialist skills, which a no-skill baseline cannot know.
Rerun: the baseline got the names and descriptions of every specialist skill (not the packs under test) and answered all 22 cases again; S01/S02
used the replaced prompts on both sides. A blind grader scored each rubric criterion separately.

| Comparison | Baseline mean /16 | Skill mean /16 | Skill wins | At or above 12/16 (baseline, skill) |
| --- | --- | --- | --- | --- |
| All criteria | 9.75 | 12.71 | 22 of 22 | 3, 17 |
| Interfaces removed | 10.10 | 13.55 | 22 of 22 | 3, 22 |

Per criterion (baseline, skill, out of 2): evidence 0.77, 1.77; operability 1.27, 1.73; validation 1.27, 1.68; tradeoffs 1.23, 1.54;
scope 1.05, 1.41; domain 1.91, 2.00; automation 1.50, 1.50; interfaces 0.95, 0.95. With the registry, interfaces no longer separates the two:
the gain is evidence handling, validation and operability. Baseline critical failures: N02, S01; skill: none. Same limits as above (one run,
same model family as grader).
