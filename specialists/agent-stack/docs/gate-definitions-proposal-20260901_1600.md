# Gate Definitions — Proposal

> **SUPERSEDED 2026-09-01 — APPLIED, then twice revised. This document is a record of the proposal, not a live instruction.**
>
> The gates described here **were applied** to `routing.toml` on 2026-09-01, so the unapplied status it originally carried is history. Two later changes moved past this document:
>
> 1. **`critic-gate` no longer sets `persona_mandatory = true`.** No gate is unconditionally mandatory; each escalates only on its own `persona_mandatory_when_tags`. The version here would
> contradict the corpus on direct-skill cases.
> 2. **`satisfied_by_skills` no longer exists.** Gates resolve through `required_capability` + `minimum_strength` against capabilities declared on each skill and persona.
>
> **What in this document still stands:** the capability model itself (gate = obligation, capability = what discharges it, persona = mandatory only where independence is the point), the corpus-derived
> trigger conditions, and the settled policy on when each gate fires. Those were adopted and remain current.
>
> **Owner of the replacement:** [routing.toml](routing.toml) `[[gates]]` and `[[capabilities]]` are authoritative. See [MEMORY.md](MEMORY.md) for why each decision was made.

Status: **APPLIED 2026-09-01, then twice revised — see the supersession banner above.** When written, this document's status field recorded the gates as unproposed-and-unapplied, and said that
`routing.toml`, `scripts/evaluate_routing.py`, and `skills/orchestrator/SKILL.md` were unchanged. That was true on the morning of 2026-09-01 and is no longer true of any of the three.

Revision 2 (2026-09-01), incorporating operator review. Triggers are derived from the 60-case corpus, not invented. Revision 1 proposed `gate → mandatory persona`; that was rejected and is replaced by
a capability model — see [What changed in revision 2](#what-changed-in-revision-2).

## Contents

- [The problem](#the-problem)
- [What changed in revision 2](#what-changed-in-revision-2)
- [Settled policy](#settled-policy)
- [Architecture: obligation, fulfilment, proof](#architecture-obligation-fulfilment-proof)
- [What the corpus says](#what-the-corpus-says)
- [Proposed routing.toml additions](#proposed-routingtoml-additions)
- [Proposed prompt changes](#proposed-prompt-changes)
- [Proposed deterministic validator](#proposed-deterministic-validator)
- [Proposed orchestrator change](#proposed-orchestrator-change)
- [Expected effect](#expected-effect)
- [Risks and what this proposal does not fix](#risks-and-what-this-proposal-does-not-fix)

## The problem

`evals/routing-cases.toml` asserts four gate flags 240 times (60 cases × 4). Every miss is a **hard** failure in `scripts/evaluate_routing.py` — `-20` points, and hard failures alone decide pass/fail.
`routing.toml`, which the prompt pastes in full as the ROUTING CATALOGUE, **defines none of them**: grepping each flag name returns 0 hits.

Measured cost in the 2026-09-01 baseline: **43 of 62 hard failures were gate misses.** Excluding them, 45/60 (75%) would pass instead of 23/60 (38.3%). The model is being scored against rules it was
never given.

## What changed in revision 2

Revision 1 wrote `requires_personas = ["research-thompson"]` into each gate. **Rejected, and rightly.** That makes a gate a persona-summoning rule, which contradicts the orchestrator's
smallest-useful-team principle and would teach the router "flag X means add persona Y".

The concrete failure it would cause: *"Check Cisco documentation for whether feature X is supported"* is legitimately

```
primary_owner: cto-vogels
skills: [deep-research]
research_required: true
```

with no second persona. Under revision 1 the gate would have forced `research-thompson` in anyway. That is persona inflation, and the corpus already punishes it — `direct-adversarial` produced 3
team-inflation failures in the baseline.

Revision 2 separates three things that revision 1 conflated:

| Concept    | What it is                                                  |
| ---------- | ----------------------------------------------------------- |
| **Gate**       | An obligation the route carries                             |
| **Capability** | What discharges the obligation — a skill *or* a persona       |
| **Persona**    | Mandatory only where **independence** of judgement is the point |

## Settled policy

Four questions were open in revision 1. All are now settled by the operator:

| Question                                                 | Decision                                                                                                   |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `critic_required` — consequence or disagreement?         | **Consequence is primary.** Disagreement is a secondary trigger, not the definition.                           |
| Does `research_required` stay true once evidence exists? | **No.** It means further external evidence must be *acquired*.                                                   |
| `qa_required` on design-only work?                       | **Only** when the design commits to rollout/change-validation, or is itself being approved for implementation. |
| Gates eval-only, or runtime?                             | **Runtime.** The orchestrator enforces them; the eval checks the same contract. One source of truth.           |

The last is the most structural. Leaving gates in the eval only produces an architecture where the harness knows rules the production router does not — the eval would be smarter than the system it
measures.

## Architecture: obligation, fulfilment, proof

The model should decide what needs judgement; the system should compute what can be computed.

```
Task
  |
  v
LLM judges — does the task TRIGGER the gate?
  research_required   (judgement)
  critic_required     (judgement)
  qa_required         (judgement)
  |
  v
Router selects personas + skills
  |
  v
Deterministic validator — does the ROUTE SATISFY the obligation?
  runtime_required        (computed from selected skills' execution field)
  capability satisfaction (is a satisfying skill or persona present?)
  persona mandatory?      (independence-critical cases only)
  prerequisites           (requires_any for tool skills)
  max team size, forbidden personas/skills
  |
  v
Final routing plan
```

Asking one LLM call to self-report all four booleans *and* route correctly is what the baseline shows it is worst at. `runtime_required` in particular is not a judgement at all: it is a lookup against
`execution = "tool"`.

## What the corpus says

Distribution of `mode` for cases that do and do not require each flag:

| Flag                | Required by | Dominant modes when TRUE                                  | Dominant modes when FALSE                   |
| ------------------- | ----------- | --------------------------------------------------------- | ------------------------------------------- |
| `research_required` | 30/60       | decision 16, research 12                                  | review 12, design 9                         |
| `critic_required`   | 22/60       | decision 14, design 4, review 4                           | research 12, review 9, design 6, decision 6 |
| `qa_required`       | 13/60       | review 5, implementation 3, decision 2, design 2, mixed 2 | —                                           |
| `runtime_required`  | 7/60        | design 2, implementation 2, research 2, decision 1        | —                                           |

Readings that matter:

- **`research_required` tracks external fact dependency, not domain.** Every `research`-mode case requires it, and 16 of 20 `decision` cases do. `review` cases mostly do not — the evidence is already
  in front of the reviewer. This is what settles the "does it stay true" question empirically.
- **`critic_required` tracks consequence.** 14 of 20 `decision` cases require it; no `research` or `implementation` case does. It fires where being wrong is expensive or hard to reverse.
- **`qa_required` tracks whether an artefact changes hands.** Every case requiring it changes an artefact, judges one for defects, or gates a rollout. The design-only split is visible:
  `infra-cicd-rollout` (design, commits to a rollout mechanism) requires it; `net-monitoring-stack` (design, chooses an approach) does not.
- **`runtime_required` is mechanically derivable.** All 7 cases select a skill already marked `execution = "tool"`.

## Proposed routing.toml additions

Appended as a new `[[gates]]` section. `required_capability` / `default_persona` / `persona_mandatory` replace revision 1's unconditional `requires_personas`.

```toml
# A gate is an OBLIGATION ON THE ROUTE, not an instruction to add a persona. "This task needs research evidence" and
# "this task needs an independent Research persona" are different claims: a CTO checking vendor documentation with a
# research skill satisfies the first without the second. Personas are mandatory only where INDEPENDENCE of judgement is
# the point.
#
#   the model judges    -> does the TASK trigger this gate?  (research, critic, qa)
#   the system computes -> does the ROUTE satisfy it?        (capability, prerequisites)
#                       -> runtime_required                   (purely mechanical)

[[gates]]
id = "research-gate"
flag = "research_required"
description = "The route depends on external facts that have not yet been gathered."
required_capability = "research"
default_persona = "research-thompson"
persona_mandatory = false
persona_mandatory_when_any = ["contested-evidence", "regulatory-research", "source-validation", "market-sizing"]
satisfied_by_skills = ["deep-research", "web-scraping", "websh", "github-explorer", "competitive-intelligence-analyst", "market-sizing-analysis"]
set_true_when_any = [
  "the answer rests on current external facts (prices, regulation, vendor documentation, availability, market data)",
  "a decision must be grounded in evidence that has not yet been gathered",
  "source validation or triangulation is part of the work",
]
set_false_when_any = [
  "all evidence needed is already contained in the task or in the artefact under review",
  "the work is implementation against agreed criteria",
]
notes = "Means 'further external evidence must be acquired'. It does NOT stay true merely because the answer rests on facts already supplied."

[[gates]]
id = "critic-gate"
flag = "critic_required"
description = "The route reaches a consequential or hard-to-reverse conclusion."
required_capability = "independent-challenge"
default_persona = "critic-munger"
persona_mandatory = true
satisfied_by_skills = ["premortem", "scientific-critical-thinking"]
set_true_when_any = [
  "a go/no-go, commitment, or selection with material cost",
  "an architecture or design decision whose failure mode is expensive or hard to reverse",
  "the task is security-sensitive or irreversible",
  "evidence is thin or contested relative to the size of the commitment",
]
set_false_when_any = [
  "the work is gathering or summarising evidence rather than committing to it",
  "the change is small, reversible, and cheap to correct",
]
notes = "Consequence is the primary trigger; disagreement is secondary. The persona is mandatory here because the value is INDEPENDENT judgement, which a skill cannot supply."

[[gates]]
id = "qa-gate"
flag = "qa_required"
description = "Code, configuration, or a release is created, changed, or judged fit to ship."
required_capability = "validation"
default_persona = "qa-bach"
persona_mandatory = false
persona_mandatory_when_any = ["release-readiness", "go-no-go", "security-sensitive", "irreversible-rollout"]
satisfied_by_skills = ["senior-qa", "code-review-security", "security-audit", "test-driven-development"]
set_true_when_any = [
  "code or configuration will be written or modified",
  "existing code, configuration, or security posture is reviewed for defects",
  "release, rollout, or migration readiness is being judged",
  "the route must state how the change is validated or rolled back",
]
set_false_when_any = [
  "the output is analysis, research, or strategy with no artefact change",
  "the design commits to no rollout or change-validation mechanism and is not itself being approved for implementation",
]
notes = "An independent QA persona is required for release, security-sensitive, and irreversible work; a validation skill suffices otherwise."

[[gates]]
id = "runtime-gate"
flag = "runtime_required"
description = "The route selects at least one skill whose execution class is `tool`."
required_capability = "tool-execution"
persona_mandatory = false
computed = true
set_true_when_any = ["any selected skill declares execution = \"tool\""]
notes = "NOT a judgement. Computed from the selected skills' `execution` field; each such skill's `requires_any` prerequisites must then be checked."
```

**Checked, and one entry is wrong.** All twelve `satisfied_by_skills` ids were verified against `routing.toml`: 11 of 12 exist. **`test-driven-development` does not** — it is a global skill available
in this session, but it is not an Agent Stack capability and is absent from the catalogue. Remove it from `qa-gate.satisfied_by_skills` before applying, leaving `senior-qa`, `code-review-security`,
`security-audit`. `scientific-critical-thinking` does exist and is fine. Had this been applied unchecked it would have shipped a dangling reference that `scripts/validate_agent_stack.py` does not
currently catch — worth adding a check that every `satisfied_by_skills` id resolves.

## Proposed prompt changes

Two edits in `scripts/evaluate_routing.py`:

1. **Stop seeding the schema all-false.** `PLAN_SCHEMA` currently shows the four flags as `False`, and that example is serialised into the prompt, anchoring the answer before the model reasons:

   ```python
   "research_required": "true|false — see [[gates]] in the routing catalogue",
   "critic_required":   "true|false — see [[gates]] in the routing catalogue",
   "qa_required":       "true|false — see [[gates]] in the routing catalogue",
   "runtime_required":  "true|false — true if any selected skill has execution=tool",
   ```

2. **Replace the single vague Rules line** (*"Flags describe whether the route requires that gate/runtime class"*):

   ```
   - Evaluate each gate in the catalogue's [[gates]] section against the task and set its flag accordingly.
   - A gate is an obligation on the ROUTE, not an instruction to add a persona. Satisfy it with a skill where a
     skill suffices; add the gate's persona only when the gate marks it mandatory, or when independent judgement
     is genuinely the point. Do not inflate the team to satisfy a gate.
   - runtime_required is not a judgement: set it true if and only if a skill you selected declares execution = "tool".
   ```

## Proposed deterministic validator

New in revision 2. In `scripts/evaluate_routing.py`, after the plan is parsed and before scoring:

- **Compute `runtime_required`** from the selected skills rather than trusting the model's self-report. Where the model disagrees with the computed value, prefer the computed value and record the
  disagreement as a diagnostic rather than a hard failure — the flag is not a judgement, so a mismatch is a prompt-following signal, not a routing error.
- **Check capability satisfaction** for each true gate: at least one `satisfied_by_skills` entry or the `default_persona` is present in the plan.
- **Check mandatory persona** only where `persona_mandatory = true`, or where the task matches `persona_mandatory_when_any`.
- **Check `requires_any` prerequisites** for every selected `execution = "tool"` skill.

This is a scorer change and will alter the numbers. Run it against the existing baseline JSONL first to see the delta before re-running the corpus — the stored plans are enough to recompute scores
without spending another 60 model calls.

## Proposed orchestrator change

`skills/orchestrator/SKILL.md` gains a gate step, so the runtime and the eval share one contract:

1. Classify the task and identify decision ownership (unchanged).
2. **Evaluate the gates in `routing.toml`; record which are true and why.**
3. Choose the narrowest sufficient route.
4. **Satisfy each true gate — prefer a skill; add the gate's persona only where mandatory.**
5. Check runtime prerequisites for any `tool`-class skill.
6. Apply existing mandatory routing rules, sequence, hand-offs, synthesis (unchanged).

## Expected effect

- Recovers up to **43 hard failures across 22 cases** on the 2026-09-01 baseline.
- Should not worsen team inflation, and may improve it: the capability model gives the router an explicit cheaper way to satisfy a gate than adding a persona. The 3 `direct-adversarial` inflation
  failures are the cases to watch.
- Leaves the **19 non-gate failures** untouched — persona ownership boundaries (`cto-vogels` vs `fullstack-dhh`, `sales-ross` vs `marketing-godin`, `qa-bach` omitted where QA is required). Separate
  fix.

Re-run for a comparable after-baseline, same route (scores are not comparable across models):

```bash
just routing-eval-hermes 60
```

## Risks and what this proposal does not fix

- **The corpus asserts `required_personas` independently of the gate flags.** Making gates capability-first improves real routing and the orchestrator, but will not by itself satisfy a case that
  explicitly requires a persona. Some of the 10 missing-required-persona failures may need the corpus and the catalogue reconciled, not just the router changed.
- **`persona_mandatory_when_any` uses intent tags the corpus does not carry.** Cases have free-text `task` and a `mode`, not tags. Those conditions are therefore judgement in practice until the corpus
  grows a tag field.
- **The validator changes scoring**, so before/after numbers are only comparable if the after-run is scored the same way. Recompute the stored baseline with the new scorer to keep the comparison
  honest.
- **No model/provider stamp in results** (tracked separately). A silent fallback would contaminate the after-baseline invisibly. Worth fixing before the re-run rather than after.
