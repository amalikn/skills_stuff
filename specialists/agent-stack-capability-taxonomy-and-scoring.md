# Agent Stack Capability Taxonomy, Failure Classification, and Scoring Rules

## Purpose

This document defines the next routing layer for Agent Stack after Baseline v2.

Current routing results show:

- gate recognition is largely working;
- ownership routing is improving;
- persona inflation is under control;
- skill selection usually occurs;
- the main bottleneck is now **capability satisfaction**.

Baseline v2:

```text
33/60 PASS (55.0%)
mean score: 81.6

Hard-failure concentration:
unsatisfied gate: 22
  - 15: skills selected, but none counted as satisfying the gate
  - 5: no skills selected
```

Core architecture:

```text
Task
  ↓
Intent / mode / tags
  ↓
Decision ownership
  ↓
Gate obligations
  ↓
Personas + skills
  ↓
Capability validation
  ↓
Runtime prerequisite validation
  ↓
Final route
```

Core principle:

```text
Gate       = obligation
Capability = what can satisfy the obligation
Persona    = mandatory only when independence/escalation requires it
Skill      = reusable execution/reasoning capability
```

---

## 1. Capability Taxonomy Design

### 1.1 Design goals

The taxonomy should:

1. eliminate duplicated gate satisfier lists;
2. make skill-to-gate relationships explicit;
3. support deterministic validation;
4. preserve the smallest-useful-team principle;
5. distinguish analytical work from independent challenge;
6. avoid giving broad skills credit for capabilities they only weakly support;
7. remain compact and understandable;
8. be extensible without forcing router-prompt rewrites.

Create a capability only when multiple skills/personas can provide it, or a gate/routing rule needs to reason about it.

### 1.2 Recommended initial taxonomy

#### Gate-facing core capabilities

| Capability | Meaning | Typical gate |
|---|---|---|
| `research` | Acquire external evidence not already supplied | research |
| `independent-challenge` | Deliberately challenge assumptions/conclusions | critic |
| `validation` | Test, verify, review, or establish fitness | QA |
| `tool-execution` | Requires executable runtime/tool environment | runtime |

#### Supporting routing capabilities

| Capability | Meaning |
|---|---|
| `architecture-analysis` | Technical architecture, boundaries, trade-offs |
| `implementation` | Build or modify code/config/artifacts |
| `code-quality-review` | Correctness/maintainability review of code |
| `security-review` | Security posture, threats, controls |
| `risk-analysis` | Identify operational/business/technical risks |
| `financial-analysis` | Unit economics, margin, ROI, landed cost |
| `market-analysis` | Market size, demand, competition |
| `regulatory-analysis` | Laws, compliance, import rules, policy |
| `operations-design` | Workflows, sourcing, logistics, process |
| `product-definition` | Requirements, user workflow, scope |
| `commercial-strategy` | Pricing, channel, business model |
| `evidence-critique` | Evaluate quality/strength of supplied evidence |
| `source-validation` | Corroborate, triangulate, authenticate sources |
| `release-readiness` | Rollout, rollback, acceptance, ship/no-ship |
| `migration-planning` | Staged technical transition |
| `network-analysis` | Routing/switching/protocol/network behaviour |

### 1.3 Skill capability schema

Capabilities should live on the skill, not inside every gate.

```toml
[[skills]]
id = "premortem"
execution = "analysis"

primary_capabilities = [
  "independent-challenge",
  "risk-analysis",
]

supporting_capabilities = [
  "evidence-critique",
]
```

```toml
[[skills]]
id = "market-sizing-analysis"
execution = "analysis"

primary_capabilities = [
  "market-analysis",
  "research",
]

supporting_capabilities = [
  "source-validation",
  "financial-analysis",
]
```

```toml
[[skills]]
id = "code-review-security"
execution = "analysis"

primary_capabilities = [
  "code-quality-review",
  "validation",
]

supporting_capabilities = [
  "security-review",
]
```

```toml
[[skills]]
id = "websh"
execution = "tool"
requires_any = ["websh"]

primary_capabilities = [
  "research",
]

supporting_capabilities = [
  "source-validation",
]
```

### 1.4 Gate schema

Gates should reference capabilities, not enumerate skill IDs.

```toml
[[gates]]
id = "research-gate"
flag = "research_required"
required_capability = "research"
minimum_strength = "primary"
default_persona = "research-thompson"
persona_mandatory = false
```

```toml
[[gates]]
id = "critic-gate"
flag = "critic_required"
required_capability = "independent-challenge"
minimum_strength = "primary"
default_persona = "critic-munger"
persona_mandatory = false
persona_mandatory_when_tags = [
  "high-consequence",
  "irreversible",
  "security-sensitive",
  "thin-evidence-high-commitment",
]
```

```toml
[[gates]]
id = "qa-gate"
flag = "qa_required"
required_capability = "validation"
minimum_strength = "primary"
default_persona = "qa-bach"
persona_mandatory = false
persona_mandatory_when_tags = [
  "release-readiness",
  "security-sensitive",
  "irreversible-rollout",
  "production-change",
]
```

```toml
[[gates]]
id = "runtime-gate"
flag = "runtime_required"
required_capability = "tool-execution"
computed = true
```

### 1.5 Persona capability schema

Personas can advertise capabilities too.

```toml
[[personas]]
id = "critic-munger"

primary_capabilities = [
  "independent-challenge",
  "risk-analysis",
  "evidence-critique",
]
```

```toml
[[personas]]
id = "research-thompson"

primary_capabilities = [
  "research",
  "source-validation",
]

supporting_capabilities = [
  "market-analysis",
  "regulatory-analysis",
]
```

A persona should not automatically satisfy every gate in its domain. Capability declaration remains explicit.

---

## 2. Primary vs Supporting Capability Semantics

### 2.1 Primary capability

A skill/persona has a **primary capability** when that capability is one of its explicit operating purposes.

Examples:

```text
premortem       → independent-challenge = primary
deep-research   → research = primary
senior-qa       → validation = primary
```

A primary capability may satisfy a gate by itself.

### 2.2 Supporting capability

A supporting capability is incidental or secondary.

Examples:

```text
market-sizing-analysis    → financial-analysis = supporting
financial-unit-economics  → risk-analysis = supporting
code-review-security      → security-review = supporting
```

Supporting capability should normally improve route quality and ranking, but **not automatically satisfy a hard gate** unless the gate explicitly allows supporting strength.

### 2.3 Why the distinction matters

Without strength, a normal analytical skill can accidentally be treated as independent challenge.

Protect this invariant:

```text
analysis ≠ independent challenge
```

---

## 3. Scoring Rules for Primary / Supporting Capabilities

### 3.1 Strength values

```text
none       = 0
supporting = 1
primary    = 2
```

### 3.2 Hard gate satisfaction

Default:

```text
route capability strength >= gate.minimum_strength
```

Example:

```toml
required_capability = "research"
minimum_strength = "primary"
```

The route passes only if a selected skill/persona provides `research` at primary strength.

### 3.3 Recommended scoring

| Condition | Score impact |
|---|---:|
| Required gate capability satisfied at primary | no penalty |
| Mandatory persona present when escalation requires it | no penalty |
| Only supporting capability present | hard fail: `capability-strength-insufficient` |
| No satisfying capability | hard fail: `gate-unsatisfied` |
| Unnecessary duplicate satisfying persona | team-inflation penalty |
| Runtime prerequisite unmet | hard fail |
| Model runtime flag differs from computed runtime | diagnostic only |

### 3.4 Gate satisfaction precedence

For each triggered gate:

```text
1. Check already-selected skills/personas.
2. If a primary satisfying capability already exists: gate satisfied.
3. Otherwise add the narrowest skill with the required primary capability.
4. Add the default persona only if:
   a. independence is mandatory; or
   b. no suitable skill exists.
5. Never add both skill and persona unless they serve distinct purposes.
```

### 3.5 Critic-specific rule

Keep `independent-challenge` narrow.

Recommended initial primary providers:

```text
critic-munger
premortem
scientific-critical-thinking
```

Do **not** mark ordinary analytical skills as `independent-challenge` merely because they assess risk or produce recommendations.

They may advertise:

```text
risk-analysis
evidence-critique
```

as supporting capabilities instead.

---

## 4. 22-Failure Classification Template

Use this before changing capability mappings.

The purpose is to distinguish:

1. real routing defect;
2. capability-mapping defect;
3. gate-trigger defect;
4. corpus defect;
5. scoring defect.

### 4.1 Per-case template

```markdown
### Case: <case-id>

**Family:**  
<family>

**Task:**  
<task text>

**Mode:**  
<mode>

**Triggered gate:**  
<research_required | critic_required | qa_required | runtime_required>

**Selected personas:**  
- ...

**Selected skills:**  
- ...

**Current required capability:**  
<capability>

**Current satisfying providers in catalogue:**  
- ...

**Observed failure:**  
<exact hard failure>

### Classification

Choose exactly one:

- [ ] ROUTING DEFECT
- [ ] CAPABILITY-MAPPING DEFECT
- [ ] GATE-TRIGGER DEFECT
- [ ] CORPUS DEFECT
- [ ] SCORING/VALIDATOR DEFECT

### Reason

<why this classification is correct>

### Expected behaviour

<what the router should have done>

### Required change

- [ ] Add/adjust skill capability metadata
- [ ] Add/adjust persona capability metadata
- [ ] Change gate trigger
- [ ] Change eval expectation
- [ ] Change scoring logic
- [ ] No change; failure is valid

### Proposed catalogue change

```toml
# exact proposed change
```

### Confidence

- High
- Medium
- Low
```

---

## 5. Classification Rules

### 5.1 ROUTING DEFECT

Use when:

- gate was correctly triggered;
- catalogue correctly defines satisfying capabilities;
- a suitable provider exists;
- router selected something else or omitted it.

Example:

```text
critic_required = true
selected:
  financial-unit-economics

available:
  premortem

→ routing defect
```

### 5.2 CAPABILITY-MAPPING DEFECT

Use when:

- selected skill genuinely provides the capability;
- catalogue fails to declare it;
- route should pass after metadata correction.

Do not use this merely because changing metadata would improve the score.

### 5.3 GATE-TRIGGER DEFECT

Use when the route is sensible but the gate should not have triggered.

Example:

```text
critic_required = true
task = "summarise these already-supplied findings"

→ gate-trigger defect
```

### 5.4 CORPUS DEFECT

Use when catalogue and architecture are coherent but the eval expectation contradicts intended semantics.

Example:

```text
direct skill case expects primary_owner = null
router selects correct skill + one accountable owner

→ corpus defect
```

### 5.5 SCORING/VALIDATOR DEFECT

Use when route, catalogue and corpus are correct but the scorer counts the route incorrectly.

---

## 6. 22-Failure Summary Matrix

| # | Case | Family | Gate | Selected skills | Failure | Classification | Proposed fix |
|---:|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |
| 9 | | | | | | | |
| 10 | | | | | | | |
| 11 | | | | | | | |
| 12 | | | | | | | |
| 13 | | | | | | | |
| 14 | | | | | | | |
| 15 | | | | | | | |
| 16 | | | | | | | |
| 17 | | | | | | | |
| 18 | | | | | | | |
| 19 | | | | | | | |
| 20 | | | | | | | |
| 21 | | | | | | | |
| 22 | | | | | | | |

---

## 7. Recommended Analysis Order

### 7.1 Research failures

Ask:

```text
Did the selected skill actually acquire external evidence?
Did it validate sources?
Was it merely analysis of supplied information?
```

If it truly acquires outside evidence:

```toml
primary_capabilities += ["research"]
```

### 7.2 QA failures

Ask:

```text
Did the skill explicitly verify correctness/readiness?
Was it implementation only?
Was validation incidental or a first-class workflow?
```

Typical mapping:

```text
test/review/security-validation skill
→ validation primary

implementation skill that merely self-checks
→ validation supporting
```

### 7.3 Critic failures

Review last and conservatively.

Ask:

```text
Did the skill challenge assumptions independently?
Did it actively search for failure modes?
Did it construct adversarial alternatives?
Or did it merely analyse the task normally?
```

Only the first class should gain:

```toml
primary_capabilities = ["independent-challenge"]
```

---

## 8. Validator Changes

`validate_agent_stack.py` should enforce:

1. every capability referenced by a gate exists;
2. every skill capability exists in the registry;
3. every persona capability exists;
4. no duplicate capability declarations;
5. `minimum_strength` is valid;
6. every non-computed gate has at least one primary-capability provider;
7. every mandatory/default persona exists;
8. every `persona_mandatory_when_tags` tag exists;
9. tool skills have valid `requires_any`;
10. `tool-execution` is not manually assigned to analysis-only skills.

Suggested registry:

```toml
[[capabilities]]
id = "research"
description = "Acquire external evidence not already supplied."

[[capabilities]]
id = "independent-challenge"
description = "Deliberately challenge assumptions or conclusions."

[[capabilities]]
id = "validation"
description = "Verify correctness, fitness, readiness, or conformance."
```

---

## 9. Behavioral Scoring Rules

### Hard failures

```text
missing required persona
forbidden persona
missing required skill
forbidden skill
wrong primary owner
gate trigger mismatch
gate unsatisfied
capability strength insufficient
runtime prerequisite missing
team size above maximum
```

### Soft / diagnostic

```text
preferred persona missing
preferred skill missing
supporting capability absent
model/runtime flag disagreement when computed value is authoritative
one extra but non-harmful capability
non-optimal but valid owner where corpus allows multiple outcomes
```

---

## 10. Capability Resolution Algorithm

```python
def capability_strength(route, capability):
    strength = 0

    for skill in route.skills:
        if capability in skill.primary_capabilities:
            strength = max(strength, 2)
        elif capability in skill.supporting_capabilities:
            strength = max(strength, 1)

    for persona in route.personas:
        if capability in persona.primary_capabilities:
            strength = max(strength, 2)
        elif capability in persona.supporting_capabilities:
            strength = max(strength, 1)

    return strength
```

Gate satisfaction:

```python
required = {
    "supporting": 1,
    "primary": 2,
}[gate.minimum_strength]

actual = capability_strength(route, gate.required_capability)

if actual < required:
    hard_fail("gate-unsatisfied")
```

Mandatory persona escalation:

```python
if gate.persona_mandatory:
    require(gate.default_persona)

if intersects(case.tags, gate.persona_mandatory_when_tags):
    require(gate.default_persona)
```

---

## 11. Re-score Before Re-run

Do not immediately spend another 60 model calls.

Process:

```text
1. Classify all 22 unsatisfied failures.
2. Correct only proven mapping defects.
3. Add capability metadata.
4. Re-score stored Baseline v2 plans.
5. Measure how many failures disappear without changing routes.
6. Only then re-run the corpus.
```

Interpretation:

```text
passes after metadata correction
→ previous failure was taxonomy/mapping, not router behavior

still fails
→ genuine routing or gate problem remains
```

---

## 12. Acceptance Criteria Before Baseline v3

Capability taxonomy is ready when:

- all capability IDs validate;
- no gate contains raw skill-ID satisfier lists;
- every gate resolves through `required_capability`;
- every non-computed gate has at least one valid primary provider;
- all 22 unsatisfied failures are classified;
- no Critic mapping was broadened merely to improve scores;
- stored Baseline v2 has been re-scored under the new taxonomy;
- mapping-only gains are documented separately from model-routing gains.

---

## 13. Baseline v3 Success Criteria

Recommended targets:

```text
overall pass rate            >= 70%
missing-gate                 <= 3
unsatisfied gate             <= 8
wrong primary owner          <= 3
team inflation               <= 1
forbidden persona/skill      = 0
runtime prerequisite failure = 0
```

More important than aggregate pass rate:

> No single architectural failure class should dominate the suite.

If one failure class is more than 40% of hard failures, fix that class before expanding the corpus.

---

## 14. What Not to Do

Do not:

- mark ordinary analysis skills as `independent-challenge`;
- widen capability mappings solely to make cases pass;
- add dozens of micro-capabilities prematurely;
- duplicate capability lists inside gates;
- require personas where a skill already satisfies the obligation;
- rewrite the orchestrator prompt before classifying the 22 failures;
- expand beyond the current 60 evals until the capability layer stabilises.

---

## 15. Immediate Work Sequence

```text
Step 1  Classify the 22 current unsatisfied failures.
Step 2  Build the capability registry.
Step 3  Annotate only skills/personas observed in those failures first.
Step 4  Replace gate satisfier lists with required_capability.
Step 5  Extend validator.
Step 6  Re-score Baseline v2 stored plans.
Step 7  Review remaining genuine failures.
Step 8  Run clean Baseline v3.
```

Governing principle:

> **The capability taxonomy should describe what skills genuinely do, not what the eval suite wishes they had done.**

That keeps the routing layer trustworthy rather than score-optimised.
