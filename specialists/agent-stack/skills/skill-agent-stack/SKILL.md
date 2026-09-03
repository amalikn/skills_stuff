---
name: skill-agent-stack
description: Use as the normal Agent Stack entry point when a request needs intelligent selection or sequencing of personas and skills, spans multiple domains, contains a material decision, or would benefit from one integrated evidence-aware synthesis. Do not use a large team for a narrow task that a single skill or persona can complete.
---

# Orchestrator — Intelligent Agent Stack Router

Use `personas/orchestrator-follett.md` as the coordination persona when personas are supported. Read project-local instructions first. Then read root `routing.toml`; it is the routing catalogue for
persona ownership, skill intent, runtime constraints, and mandatory gates.

## Contents

- [Core Contract](#core-contract)
- [Step 1 — Frame the Work](#step-1-frame-the-work)
- [Step 2 — Decide Direct vs Orchestrated Routing](#step-2-decide-direct-vs-orchestrated-routing)
- [Step 3 — Select the Primary Persona](#step-3-select-the-primary-persona)
- [Step 4 — Add Necessary Supporting Personas](#step-4-add-necessary-supporting-personas)
- [Step 5 — Select Skills](#step-5-select-skills)
- [Step 6 — Apply Mandatory Gates](#step-6-apply-mandatory-gates)
- [Step 7 — Sequence Hand-offs](#step-7-sequence-hand-offs)
- [Step 8 — Handle Disagreement](#step-8-handle-disagreement)
- [Step 9 — Synthesize and Stop](#step-9-synthesize-and-stop)
- [Routing Self-Check](#routing-self-check)
- [Orchestration Brief](#orchestration-brief)
- [Domain Routing Profiles](#domain-routing-profiles)
- [Routing Preflight](#routing-preflight)

---

## Core Contract

<!-- BEGIN eval-routing-contract --> <!-- This block is READ VERBATIM by scripts/evaluate_routing.py and sent to the model. It is the single source of the routing principles the behavioural evaluation
states. Before 2026-09-02 the evaluator carried its own copy, which meant the eval could score a contract production did not use and no check would notice — an eval that drifts from the thing it
measures is worse than no eval, because it reports confidence about the wrong artefact. Edit the principles here and the eval changes with them. Keep it short: it is prepended to every case. -->

Routing principles:

- Take the smallest sufficient route. A direct skill for a narrow procedure; one persona plus skills for a single-domain decision; a small team only for genuinely cross-domain work.
- Personas own judgement; skills provide procedures and tools. Do not add a persona to perform a procedure.
- A gate is an obligation on the route, not an instruction to add a persona. It is discharged by any selected skill or persona declaring the gate's `required_capability` at its `minimum_strength`.
- A `supporting` capability never discharges a gate. Analysis is not independent challenge.
- Where two personas both plausibly own a decision, apply the catalogue's `[[precedence]]` rules rather than inferring ownership from overlapping `owns` prose.
- Current or external evidence routes to Research; material economics to CFO; architecture and security posture to CTO; release confidence to QA; and a consequential or hard-to-reverse decision
  warrants independent challenge.
- Report the task's characteristics — security-sensitive, release-readiness, production-change, irreversible, high-consequence, thin-evidence-high-commitment — because those judgements are what
  escalate a gate from any qualifying provider to a specific persona.
<!-- END eval-routing-contract -->


The operator should normally give the task to the Orchestrator without choosing specialists. The Orchestrator determines whether the task needs:

- a single procedural skill;
- one primary persona plus one or more skills;
- a small multi-persona sequence; or
- an independent critic/gate before recommendation.

**Personas own judgement. Skills provide procedures/tools.** Do not select either merely because its name shares keywords with the request.

## Step 1 — Frame the Work

Extract, without asking questions unless genuinely blocking:

- requested outcome or decision;
- decision owner;
- task mode: `research`, `decision`, `design`, `implementation`, `review`, `operations`, or `mixed`;
- affected domains;
- evidence already available and evidence still required;
- constraints, runtime/tool availability, and project-local rules;
- reversibility, cost, external commitment, security/safety sensitivity;
- useful completion criteria.

If the user asks for a finished artifact, completion means the artifact plus validation, not merely advice about how to create it.

## Step 2 — Decide Direct vs Orchestrated Routing

Use the narrowest path that can produce a correct answer.

### Direct skill

Use one skill without a team when all are true:

1. the requested outcome is procedural and narrow;
2. one skill's intent directly matches it;
3. no material cross-domain judgement is required;
4. its runtime prerequisites are available;
5. no independent gate is required.

Examples: pre-mortem only; SEO audit only; browser automation only; test-suite scaffolding only.

### One persona + skills

Use one primary persona when one decision domain clearly owns the answer but repeatable procedures are needed. Example: CFO + unit-economics + pricing-strategy.

### Multi-persona orchestration

Use multiple personas only when different decision owners provide non-duplicative inputs. Normal range: 2–4 domain personas plus the Orchestrator.

## Step 3 — Select the Primary Persona

Read `routing.toml` and identify the persona whose `owns` field best matches the requested decision/output.

Selection priority:

1. explicit decision ownership;
2. direct `intent` match;
3. required downstream hand-off;
4. relevant domain;
5. stylistic similarity — **never sufficient by itself**.

There should normally be one primary owner for each decision. If two personas appear to own the same decision, narrow the decision or assign one as independent reviewer rather than co-owner.

### Ownership precedence

Where two personas both plausibly own a decision, `routing.toml` `[[precedence]]` names the discriminating question and both answers. Apply the rule rather than inferring ownership from overlapping
`owns` prose — the whole point is that the same task shape resolves the same way every time. The losing persona normally stays in the route as a consulted participant; precedence assigns
accountability, it does not exclude expertise.

| Situation                                          | Discriminator                                             | Owner                                                             |
| -------------------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------- |
| Decide what to build **and** implement it              | Are the requirements still open?                          | Open → Product; settled → Full-Stack                              |
| Review an artefact inside another technical domain | Is code quality or design/posture being judged?           | Code quality → Full-Stack; architecture or security posture → CTO |
| Architect or review the orchestration machinery    | Is the candidate owner the component under review?        | Always CTO; Orchestrator participates, never owns the verdict     |
| Select a supplier on evidence **and** landed cost      | Is the deliverable the evidence or the financial verdict? | Evidence → Research; financial verdict → CFO                      |

Artefact responsibility outranks domain context, and a component does not own architectural review of itself. Security posture is the one thing that stays with CTO however code-shaped the artefact is:
a focused secure-code review of authentication or secrets handling asks whether the system is safe, which is an architectural verdict, not a code-quality one.

## Step 4 — Add Necessary Supporting Personas

Add a supporting persona only if its contribution changes correctness or a decision gate.

Common patterns:

| Need                            | Primary/support pattern                                   |
| ------------------------------- | --------------------------------------------------------- |
| Market evidence before strategy | Research → CEO/Product/Marketing                          |
| Business viability              | Research as needed → CFO → CEO/Operations                 |
| Product definition              | Research → Product                                        |
| User workflow                   | Product → Interaction                                     |
| Visual interface                | Product/Interaction → UI                                  |
| Technical architecture          | CTO → Full-Stack/DevOps as needed                         |
| Implementation                  | Full-Stack → QA/Security; DevOps only if delivery changes |
| GTM                             | Research → Marketing or Sales → CFO if economics matter   |
| High-risk decision              | Domain owner(s) → Critic                                  |

Do not add CEO to every business task, CTO to every code task, QA to every analysis, or Critic to every reversible low-risk decision.

## Step 5 — Select Skills

For each concrete subtask, find the narrowest skill in `routing.toml` whose `intents` match the work.

A skill is justified only when:

- it has a concrete subtask;
- its output is consumed by the final result or next persona;
- tool/runtime prerequisites can be met safely;
- it does not duplicate another selected skill;
- project-local safety/governance permits it.

When two skills overlap, prefer the more specific skill. Use the broader skill only if it adds a distinct method or evidence layer.

### Environment-aware routing

For `execution = "tool"` skills:

1. inspect declared `requires_any` and the skill's own compatibility/setup instructions;
2. prefer the repository's `mise`/`.venv` environment for Python helpers;
3. do not install system/global dependencies silently;
4. if a prerequisite is absent, either use an available safe alternative or report the blocker;
5. skill-local instructions never override Agent Stack's no-background/no-implicit-persistence safety model.

## Step 6 — Apply Mandatory Gates

### Gate classes

`routing.toml` defines four gate classes in its `[[gates]]` section. Evaluate each against the task and record which are true and why. This is the same contract the behavioural evaluation scores, so
the runtime and the eval cannot drift apart.

| Gate                | True when                                                                                                                                                                      |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `research_required` | Further **external** evidence must be acquired — current prices, regulation, vendor documentation, availability, market data. False when the evidence needed is already in the     |
|                     |   task or the artefact under review.                                                                                                                                           |
| `critic_required`   | The route reaches a consequential or hard-to-reverse conclusion: a GO/NO-GO or commitment with material cost, an architecture decision with an expensive failure mode,         |
|                     |   security-sensitive or irreversible work, or thin evidence relative to the commitment.                                                                                        |
| `qa_required`       | Code, configuration, or a release is created, changed, or judged fit to ship — including a design that commits to a rollout or change-validation mechanism.                    |
| `runtime_required`  | **Computed, never judged.** True if and only if a selected skill declares `execution = "tool"`.                                                                                    |

### A gate is an obligation, not a persona

Satisfy each true gate with the **cheapest sufficient** means, stopping at the first that works:

1. **Already selected?** If any skill or persona in the route declares the gate's `required_capability` in its `primary_capabilities`, the gate is met. Add nothing.
2. **Otherwise add the narrowest skill** whose `primary_capabilities` include it. A `supporting_capabilities` entry does **not** discharge a gate.
3. **Add the gate's persona only where independence is the deliverable** — `persona_mandatory`, or a task tag matching `persona_mandatory_when_tags`.
4. **Never add a persona because it is the gate's `default_persona`.**

**Do not inflate the team to satisfy a gate.** Why each rule is shaped this way, and the adjacent-capability trap that caused every gate failure in one baseline:
[references/gate-model.md](references/gate-model.md).

### Closure is performed by the system, not remembered by you

`scripts/close_route.py` adds the minimum provider for an open gate, escalates to the gate's persona on task tags, and recomputes `runtime_required`. **You still judge which gates are true and who
owns the decision** — closure never overrules those; it only discharges obligations you asserted.

### RUN IT. Do not simulate it.

Once you have judged owner, personas, skills and gates, pipe the draft route through closure and **use what comes back**:

```bash
echo '{"route_mode":"...","primary_owner":"...","personas":[...],"skills":[...],
       "research_required":false,"critic_required":false,"qa_required":false,"runtime_required":false,"reason":"..."}' \
  | python3 /Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/scripts/close_route.py --explain
```

`--max-personas N` caps the team; `--tag security-sensitive` (repeatable) passes each characteristic you judged; `--explain` prints what changed, to stderr.

**Reading this and satisfying the gates yourself is not the same thing, and the difference is measured** — see [references/gate-model.md](references/gate-model.md). Fast, deterministic, no model call.

### Satisfaction is an invariant, not a step

`routing.toml` `[[route_invariants]]` states this as a property of the finished route, not a stage in this procedure:

> For every gate the route sets true, some selected skill or persona declares that gate's `required_capability` at its `minimum_strength`.

**A route that breaks this is invalid** — as invalid as one naming a skill that does not exist. Walk the gates you set true before returning, and repair any that is open. **Check the declaration, not
the resemblance**: the adjacent-capability trap and its measured cost are in [references/gate-model.md](references/gate-model.md).

### Domain gates

Still apply where relevant, and on the same obligation-not-persona basis:

- **CFO:** economic viability, material pricing/capital decisions.
- **CTO:** architecture, migration, system-boundary decisions.
- **DevOps:** deployment/operational readiness when runtime delivery changes.

### Runtime prerequisites

For every selected `tool`-class skill, check its `requires_any` prerequisites before offering the route. If they are unavailable, route to a safe alternative or report the blocker.

A gate may return HOLD/NO-GO. Do not force a positive recommendation.

## Step 7 — Sequence Hand-offs

Give each persona/skill a bounded assignment containing:

- required outcome;
- relevant evidence/context;
- explicit non-scope;
- expected output;
- who consumes the output next.

Default to dependency order rather than parallelism when one result materially changes another's work. Parallelise only independent analyses.

## Step 8 — Handle Disagreement

Do not average conflicting specialist views.

For each material disagreement:

1. identify the proposition;
2. label it factual vs trade-off/value disagreement;
3. compare evidence/assumptions;
4. identify evidence that could resolve factual conflict;
5. expose unresolved trade-offs to the operator.

## Step 9 — Synthesize and Stop

Return one operator-facing answer. Separate:

- verified facts/evidence;
- assumptions and inference;
- specialist disagreements;
- recommendation or blocker;
- risks and required approvals;
- next action.

Stop when the completion criteria are met or when further work cannot change the decision without new evidence/operator authority. Never create self-perpetuating loops or background continuation.

## Step 10 — Record the Route

**Do this yourself, at the end of the task. Never ask the operator to run it.** One command, no dependencies beyond the standard library, works from any project:

```bash
python3 /Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/scripts/field_log.py add \
  "<one line: what the work actually was>" \
  --project <repo or project name> \
  --owner <primary_owner you named> \
  --followed full|partial|no \
  --overrode "<what you actually used instead, and why>"
```

### Why this exists

Corpus agreement is necessary and not sufficient; only real use shows whether a correct route made the work better. Full rationale and how to read the log: [references/field-log.md](references/field-log.md).

### What to record, and what not to

- **`--followed` and `--overrode` are yours** — you did the work. Record a route you DEPARTED from as readily as one you kept; a departure is the valuable entry.
- **If you followed the route, OMIT `--overrode`.** Never pass `"none"` — it counts as a change and inflates the one statistic the log exists to produce.
- **Never fill in `--helped`** about your own work. It is operator-only.
- **Correcting an earlier entry is itself a valid entry.**

### Standing caveat while using the route

Trust owner and skill selection — that is the part with unseen-holdout evidence behind it. **Treat the gate flags as advisory noise**: measured predicted-positive
rate is 1.00 on all four, so a broad or all-true gate set is not authority to expand the team. See
[rule 0012](/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack/.archcore/rules/0012-gate-flags-are-advisory-until-localised.md).

## Step 9.5 — Persist the Synthesis Into the Project

**When the route produced a verdict, an assessment or a decision the project will refer back to, write it into the project as a file.** Not for narrow or
routine work — a usability list or a config fix does not need a document, and producing one for every task is noise.

Do it when any of these hold: the output is a GO/NO-GO or a recommendation; personas disagreed and the disagreement is part of the answer; the finding rests on
evidence someone will want to re-check; or a later session would otherwise have to redo the reasoning.

**Where — look before you write. The project decides, not this skill.**

1. If the project already has a reports convention, follow it exactly (`docs/reports/`, `reports/`, or whatever its `AGENTS.md` names).
2. Otherwise put it in `docs/` and say in your answer that you created that location.
3. Never invent a parallel structure beside one that already exists.

**Name it** `<slug>-YYYYMMDD_hhmm.md` — the operator's global convention.

**Contents that make it usable as a reference later**, rather than a transcript:

- the verdict or recommendation in its own sentence, first;
- what the finding rests on, with figures and their source, separated from inference;
- **disagreement preserved, not averaged** — where two personas reached different conclusions, record both and what each turned on;
- what would change the answer, stated concretely enough to act on;
- the route that produced it: the primary owner, the personas and skills used, and which gates fired.

That last line matters more than it looks. A report that records its own route can be re-read later against what the router did, and is the only artefact that
connects a decision to the reasoning path that produced it.

## Routing Self-Check

Before finalising, verify:

- Is every selected persona necessary?
- Does each selected skill have a concrete job?
- Is one owner clear for each material decision?
- Were runtime/tool prerequisites checked for tool skills?
- Were mandatory domain/critic gates applied?
- **Is every gate set true actually closed by a declared `primary_capabilities` entry on a selected skill or persona?** An open gate makes the route invalid, not merely thin.
- Is evidence distinct from inference?
- Are disagreements visible?
- Did the route avoid unnecessary context and duplicated work?

## Orchestration Brief

When useful, expose this compact summary:

```markdown
- Task mode / decision owner:
- Primary persona:
- Supporting personas:
- Skills:
- Why this route:
- Evidence / prerequisites:
- Gates:
- Sequence:
- Completion condition:
```

## Domain Routing Profiles

Networking/infrastructure and physical-product/import work each carry routing heuristics distilled from evaluation, including two known ambiguous ownership boundaries. **Read
[references/domain-profiles.md](references/domain-profiles.md) when the task is in either domain**; skip it otherwise.

## Routing Preflight

Before dispatching work, verify:

1. Every selected persona has one unique contribution or gate.
2. Every selected skill produces an output consumed by the route.
3. One persona owns each material decision domain.
4. Current/external factual claims have Research when they determine correctness.
5. Economic GO/NO-GO claims have CFO when money/viability is material.
6. High-risk or irreversible commitments have an independent Critic gate.
7. QA is used for release/behaviour confidence, not as a generic reviewer.
8. Tool skills have an available runtime or a declared blocker/alternative.
9. Team size is no larger than required for correctness.
10. A narrow direct-skill task has not been inflated into orchestration.

For regression testing of these decisions, see `ROUTING_EVALS.md` and `scripts/evaluate_routing.py`.
