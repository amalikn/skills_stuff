# Agent Stack — Current-State Architecture, Routing, Eval, Governance, and Production-Readiness Audit

You are acting as a senior AI-agent systems architect, software architect, evaluator, safety reviewer, and repository auditor.

Audit the **current state** of this Agent Stack repository as it exists now.

Do not rely on previous audit conclusions. Reconstruct the current implementation from repository evidence and determine what is true **today**.

The repository has evolved substantially, including routing taxonomy, personas, skills, deterministic route closure, behavioral evals, governance rules, provenance/freeze controls, and a blind holdout phase. Your job is to establish the actual current state and identify what remains before the stack can reasonably be called production-ready.

Do not modify files during this audit.

---

# 1. Audit principles

## Evidence first

Every material finding must identify repository evidence:

- file path
- relevant section/function/key
- line numbers where practical

Classify statements as:

- **FACT** — directly evidenced
- **INFERENCE** — strongly implied
- **FINDING** — identified defect/gap
- **RECOMMENDATION** — proposed action
- **UNKNOWN** — cannot be established

Do not inherit conclusions from old audit reports merely because they exist.

Historical audit reports are evidence of prior state only.

---

# 2. Establish repository authority and scope

First determine:

- canonical source directories
- generated/derived files
- archived audit material
- working cache
- runtime-facing files
- governance files
- eval corpora
- scripts/tooling
- state/provenance records
- installation artifacts

Explicitly identify what is authoritative versus derived.

Confirm whether archived audit receipts can influence current-state audits.

---

# 3. Inventory the current Agent Stack

Produce a current inventory for:

## Personas
For every persona record:

| Persona | Role | Ownership domain | Primary capabilities | Supporting capabilities | Boundaries | Key skills |
|---|---|---|---|---|---|---|

Assess whether persona definitions are now sufficiently operational rather than generic descriptions.

Look for:

- vague boundaries
- overlapping ownership
- contradictions
- personas that are too broad
- personas that exist but are effectively unused
- missing hand-off rules

## Skills
For every skill record:

| Skill | Purpose | Execution class | Primary capabilities | Supporting capabilities | Runtime requirements | Persona associations | Issues |
|---|---|---|---|---|---|---|---|

Confirm the advertised skill count against actual repository contents.

---

# 4. Audit the routing architecture

Treat routing as a critical subsystem.

Reconstruct the routing flow from source.

Determine whether the architecture actually behaves like:

```text
Task
  ↓
task classification
  ↓
ownership / precedence
  ↓
gate judgement
  ↓
personas + skills proposed
  ↓
deterministic capability closure
  ↓
strength validation
  ↓
runtime prerequisite closure
  ↓
final route
```

Confirm from code rather than documentation alone.

---

# 5. Audit routing.toml as the routing source of truth

Inspect all routing structures, including:

- persona definitions
- skill definitions
- capability registry
- routing rules
- gates
- precedence rules
- route invariants
- execution classes
- runtime prerequisites
- tags
- ownership rules

Specifically verify that the previous “two persona models” problem is actually gone.

Confirm that:

- `[[routing_rules]]` are advisory only
- they contain no mandatory `require_personas`
- advisory rule IDs do not masquerade as `*-gate`
- mandatory behavior lives only where intended
- precedence rules yield real, distinct ownership outcomes
- gates express obligations, not unconditional persona summoning

Identify any remaining duplicate routing semantics.

---

# 6. Capability taxonomy audit

Determine whether the capability taxonomy is coherent.

Confirm:

- capability registry exists and is authoritative
- all skills declare capabilities
- all personas declare capabilities
- gates reference `required_capability`
- old `satisfied_by_skills` duplication is gone
- primary/supporting capability semantics are consistently applied
- capability strength is enforced
- `tool-execution` agrees with execution class
- no persona improperly advertises `tool-execution`

Assess whether the taxonomy is:

- too broad
- too narrow
- overfit to eval cases
- internally contradictory
- semantically ambiguous

Pay special attention to `independent-challenge`.

Verify that ordinary analytical skills have not been incorrectly promoted to primary independent-challenge merely to improve eval scores.

---

# 7. Gate audit

Audit all gate behavior.

For each gate provide:

| Gate | Trigger meaning | Required capability | Strength | Persona escalation | Deterministic? | Risks |
|---|---|---|---|---|---|---|

Confirm current semantics of:

- `research_required`
- `critic_required`
- `qa_required`
- `runtime_required`

Verify:

### Research
Means additional external evidence still needs to be acquired, not merely that the answer rests on evidence.

### Critic
Tracks consequential / hard-to-reverse judgement, with independent persona escalation only where policy requires it.

### QA
Tracks artifact validation, release/change readiness, security-sensitive validation, etc., without automatically forcing QA persona where a capability is sufficient.

### Runtime
Is computed from selected tool-class skills rather than trusted from model self-report.

---

# 8. False-positive / false-negative gate scoring

Inspect the evaluator.

Confirm that:

```text
expected=true, actual=false
→ hard failure

expected=false, actual=true
→ soft penalty
```

Verify:

- false negatives and false positives are tracked separately
- false positives do not decide pass/fail
- runtime gate is treated separately because it is computed
- all-true gate assertion is no longer a free winning strategy

Check whether the selected penalty values are internally consistent and whether any other boolean/one-sided checks still reward maximal assertion.

Search for similar asymmetric-scoring defects elsewhere.

---

# 9. Deterministic closure audit

Inspect the route repair/closure mechanism deeply.

Determine:

- what conditions trigger repair
- what it is allowed to change
- whether it preserves model judgement where possible
- how it chooses minimal satisfying providers
- whether it enforces capability strength
- whether it enforces runtime prerequisites
- whether it can create persona/skill inflation
- whether repaired routes are revalidated
- whether repair is deterministic
- whether closure can silently alter ownership

Confirm whether the architecture now follows:

```text
model judges
system satisfies constraints
```

rather than using the deterministic layer as the primary router.

Identify any case where the repair engine is making semantic decisions that should belong to the model.

---

# 10. Route invariants audit

Inspect all `[[route_invariants]]`.

Verify that each invariant:

- expresses a property of a finished route
- maps to a real scorer violation
- has a measurable repair behavior
- cannot silently become unenforced

At minimum verify:

- gate-capability closure
- gate-strength closure
- runtime-prerequisite closure

Assess whether additional invariants are genuinely needed or would merely overconstrain routing.

---

# 11. Behavioral evaluator audit

Audit `scripts/evaluate_routing.py` end-to-end.

Reconstruct:

```text
case load
→ prompt construction
→ runner invocation
→ output parse
→ deterministic closure
→ scoring
→ provenance stamp
→ stored row
→ summary
```

Look for:

- execution failures treated as model failures
- parse failures
- denominator contamination
- partial-run ambiguity
- accidental dependence on stale globals
- scoring inconsistencies
- route mutation after provenance stamping
- scorer/closure order defects

Confirm that execution errors are:

- separately identified
- excluded from valid-result pass-rate denominator
- excluded from corrected mean
- still reported

---

# 12. Coverage / --limit audit

Confirm partial runs cannot masquerade as baselines.

Verify:

- full pool is measured before `--limit`
- selected/total coverage prints
- partial corpus execution prints an explicit warning
- baseline tooling does not silently treat partial runs as full runs

Reproduce or inspect the regression test for the historical truncated-run issue.

---

# 13. Provenance and reproducibility audit

Inspect every stamped input.

Current provenance should distinguish:

## Prompt/model inputs
Examples:
- routing catalogue
- eval corpus/case set
- production routing/orchestrator contract
- evaluator/harness prompt logic

## Score-affecting non-prompt inputs
Examples:
- deterministic closure implementation

Verify whether all files capable of changing:

- the model prompt
- selected cases
- route repair
- score
- verdict

are stamped.

Identify any unstamped score-affecting artifact.

Check whether any currently stamped artifact does **not** affect the result and therefore generates false alarms.

---

# 14. Freeze governance audit

Inspect:

- freeze record
- `just freeze-check`
- freeze parsing
- current recorded SHAs
- holdout guard
- related governance rules

Confirm:

```text
just preflight
= current repository validity

just freeze-check
= matches a historical evaluation snapshot
```

These must remain separate.

Verify `freeze-check`:

- uses the same hashing/provenance logic as evaluator
- fails non-zero on drift
- identifies exact artifact
- never mutates
- is not incorrectly enforced as a permanent global repository invariant

---

# 15. Production/eval contract unification

Verify whether the behavioral evaluator now consumes the **same routing contract** that production uses.

Determine:

- where routing principles are authored
- whether evaluation duplicates those instructions
- whether generated prompts derive from canonical production text
- whether drift between production and eval can still occur

Confirm the regression result showing the contract refactor was behavior-preserving.

Look for any remaining duplicated routing prose in scripts.

---

# 16. Development corpus audit

The frozen development corpus must now be treated as regression data, not unseen evidence.

Inspect:

- corpus size
- family distribution
- expected fields
- tags
- required/preferred/forbidden personas
- required/preferred/forbidden skills
- gate flags
- mode
- max persona constraints

Verify the documented frozen SHA.

Determine whether corpus changes after closure are clearly classified as:

- contract correction
- scorer correction
- model improvement
- actual routing improvement

Do not accept score increases caused only by relaxed expectations as model gains.

---

# 17. Historical baseline reconstruction

Using stored result files if available, reconstruct the major measured arc.

At minimum distinguish:

### Prompt-only routing baseline(s)

### Capability/gate refactor

### Route-invariant experiment

### Deterministic closure experiment

### Production-contract unification

Summarize:

| Baseline | Model | Corpus | Closure? | Pass | Mean | Key interpretation |
|---|---|---|---|---:|---:|---|

Verify rather than copy old summaries blindly.

Important historical conclusions to confirm or reject from current evidence:

- prompt-only closure did not materially improve routing
- deterministic closure materially improved all tested model arms
- stronger production-tier models reached roughly ~80% on tested holdout subset
- development corpus reached roughly high-70s after closure/contract corrections
- some historical gains were contract corrections rather than model improvements

---

# 18. Cross-model experiment audit

Inspect the stored Flash / Pro / Claude comparison.

Verify:

- identical case IDs
- identical frozen routing/corpus/harness/closure inputs
- correct provider/model/runner labels
- execution errors excluded appropriately
- case-by-case comparability

Reconstruct:

```text
Flash vs Pro
→ model-tier effect

Pro vs Claude
→ provider/model-family difference

Flash vs Claude
→ total practical difference
```

Assess whether the conclusion:

> deterministic closure matters more than model tier, though model tier still matters

is actually supported.

---

# 19. Holdout audit

Inspect the unseen holdout corpus without using it to tune anything.

Confirm:

- authored blind to development corpus contents
- same six families
- task text authored before route expectation
- naturally unbalanced gate distribution
- not executed before freeze
- distinct corpus SHA
- evaluator uses same scorer/harness
- holdout command requires freeze check

Inventory the holdout:

| Family | Count |
|---|---:|
| networking-infrastructure | |
| software-ai-engineering | |
| jdm-import | |
| atar-import | |
| business-research | |
| direct-adversarial | |

Use **atar**, not “attar”.

Determine whether the holdout has already been executed.

If it has:

- report results
- treat it as spent unseen evidence
- do not recommend modifying it based on observed failures

If it has not:

- state clearly that it remains unspent

---

# 20. Real-world evaluation readiness

Determine whether the next phase is correctly defined as:

1. unseen holdout
2. replay of historical real tasks
3. shadow-mode routing beside normal work

Assess whether tooling exists to support these without contaminating evidence.

Recommend the minimum needed for:

### Historical replay
Use actual prior tasks from:
- networking/infrastructure
- software/AI projects
- JDM/import
- atar/import
- business/research

The router should choose a route before comparing it with what actually happened.

### Shadow mode
Router proposes:

- owner
- personas
- skills
- gates
- repaired final route

but drives no action.

---

# 21. Audit open legacy findings

Revisit old audit findings from current source rather than assuming they remain open.

At minimum inspect:

## A1/A2
Upstream synchronization:
- atomicity/state consistency
- path/symlink containment

## A3
`websh`

Verify whether inherited background/persistence behavior still contradicts Agent Stack’s human-gated safety model.

## A4
`deep-research`

Verify whether background continuation/state/viewer behavior is now appropriately constrained.

## A5
Validator

Determine whether the original validator defect is still open after the extensive validator work.

## A6
Startup skill

Verify missing resources/references are actually resolved.

## A7
Routing behavioral evals

This is likely closable if the current routing eval system now satisfies the original finding. Confirm from the original finding text and current implementation.

For each:

| Finding | Current status | Evidence | Close? | Remaining action |
|---|---|---|---|---|

Use:

- CLOSED
- PARTIALLY CLOSED
- OPEN
- OBSOLETE

---

# 22. Environment/runtime audit

Review current runtime guidance.

Inspect:

- `.mise.toml`
- venv handling
- `uv`
- runtime documentation
- Python dependencies
- tool availability
- environment bootstrapping

Determine whether skills that execute code/tools clearly state:

- expected runtime
- isolation requirements
- prerequisite binaries
- environment discovery
- failure behavior

Look specifically for inconsistent `mise` / `.venv` assumptions across skills.

---

# 23. Installation / symlink audit

Recheck:

- global install
- project-local install
- symlink-only canonical model
- collision behavior
- archive/ZIP behavior
- portability
- uninstall/recovery

Verify whether previously improved archive-mode canonical behavior remains correct.

Assess whether the missing:

```text
just doctor
```

and link helper are now materially needed.

If still absent, classify them appropriately rather than automatically making them P1.

---

# 24. Governance audit

Inspect governance mechanisms:

- rules
- guides
- negative-tested validators
- path/reference validation
- counts
- change logs
- scratchpad/memory ownership
- working-cache rules
- audit archive

Look for:

- governance that enforces historical state instead of current validity
- rules whose violation cannot be measured
- duplicate policies
- stale references
- governance that has become more complex than the risk it controls

Determine whether governance is now proportionate or overengineered.

---

# 25. Audit staleness residuals

Explicitly inspect the two known residual classes:

- JSONC `tsconfig` handling
- inverse-sweep package-internal directories

Determine whether these are:

- actual defects
- accepted limitations
- stale audit receipts
- false positives

State what must happen before the next audit can honestly start clean.

---

# 26. Test and governance coverage

Report current:

- unit/integration test count
- governance check count
- routing corpus validation
- preflight
- freeze-check
- negative-tested guards

Do not treat raw check count as quality by itself.

Assess what important behaviors remain untested.

---

# 27. Overengineering / simplification review

After understanding the current system, explicitly ask:

- Is routing.toml now too large or complex?
- Are capabilities, gates, precedence and invariants all earning their complexity?
- Is deterministic closure appropriately scoped?
- Are governance checks proportionate?
- Is there duplicated state?
- Could anything be removed without weakening guarantees?

Do not simplify merely because the system is sophisticated.

Recommend deletion only where evidence shows accidental complexity.

---

# 28. Current production-readiness assessment

Provide separate readiness ratings for:

| Area | Rating |
|---|---|
| Persona model | |
| Skill model | |
| Routing contract | |
| Gate logic | |
| Capability taxonomy | |
| Deterministic closure | |
| Behavioral evaluation | |
| Holdout methodology | |
| Governance | |
| Runtime/tooling | |
| Installation | |
| Upstream sync | |
| Safety/human control | |

Use:

- READY
- READY WITH MINOR GAPS
- MATERIAL GAPS
- NOT READY

---

# 29. Prioritised findings

Classify remaining findings:

### P0 — Critical
Unsafe/corrupting/fundamentally unreliable.

### P1 — High
Material production-readiness blocker.

### P2 — Medium
Important maintainability, operational, or evaluation weakness.

### P3 — Low
Cleanup or developer-experience improvement.

Do not preserve historical severity if the underlying problem has changed.

---

# 30. Required final report structure

Return exactly these major sections:

## 1. Executive Assessment

Overall verdict:

- PRODUCTION-READY
- PRODUCTION-READY WITH MINOR GAPS
- SOUND WITH MATERIAL GAPS
- NEEDS REWORK
- FUNDAMENTALLY FLAWED

## 2. What Agent Stack Is Now

Current architecture only.

## 3. Canonical Sources and Repository Inventory

## 4. Persona Architecture

## 5. Skill Architecture

## 6. Routing Architecture

## 7. Capability Taxonomy

## 8. Gates and Gate Scoring

## 9. Precedence and Ownership

## 10. Deterministic Closure

## 11. Route Invariants

## 12. Eval Harness and Scoring

## 13. Provenance and Freeze Model

## 14. Development Corpus Status

## 15. Historical Baseline Reconstruction

## 16. Cross-Model Results

## 17. Unseen Holdout Status

## 18. Real-World Evaluation Readiness

## 19. Runtime and Environment

## 20. Installation and Symlink Model

## 21. Safety and Human Control

## 22. Governance

## 23. Legacy Audit Findings A1–A7

## 24. Staleness Residuals

## 25. Test and Governance Coverage

## 26. Complexity / Overengineering Review

## 27. Remaining P0–P3 Findings

## 28. Production-Readiness Matrix

## 29. Recommended Next Actions

## 30. Final Verdict

Answer explicitly:

1. Is the current Agent Stack architecturally sound?
2. Is the routing model now coherent?
3. Is deterministic closure correctly separated from model judgement?
4. Are personas and skills sufficiently defined?
5. Are routing evals trustworthy?
6. Has the development corpus been overfit?
7. Is the unseen holdout methodology valid?
8. What remains before broad production readiness?
9. Which old audit findings can now be closed?
10. What should explicitly **not** be changed?

---

# 31. Audit constraints

Do not:

- modify files
- run destructive commands
- apply upstream changes
- install globally
- alter symlinks
- rewrite eval expectations
- tune against holdout results
- treat archived audit findings as current facts
- reward higher test/check counts without inspecting coverage
- recommend more routing prose merely because routing is imperfect

Read-only diagnostics are allowed.

Where a command might mutate state, inspect source instead.

---

# 32. Audit standard

The audit should determine whether Agent Stack is now:

**coherent, reproducible, measurable, maintainable, minimally routed, runtime-safe, human-controlled, and capable of generalising beyond its development eval corpus.**

The key question is no longer:

> “Does the router pass its development cases?”

It is:

> **“Have we built a routing system whose behavior can be trusted, measured, reproduced, and challenged on unseen real work?”**