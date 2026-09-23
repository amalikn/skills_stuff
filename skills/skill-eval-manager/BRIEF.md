# Brief

> Companion document: the full design record — why a skill was the right shape, the format choices and what was rejected, verification findings, and the numbered operator decisions — lives at
> `/Volumes/Data/_ai/_skills/skills_stuff/docs/skill-eval-manager-design-record-20260923_1211.md`, beside the authoring prompt that produced this package.

## Contents

- [Decision](#decision)
- [Concept decisions](#concept-decisions)
- [Format decisions](#format-decisions)
- [Examples and limitations](#examples-and-limitations)
- [Deferred to v0.2](#deferred-to-v02)
- [Trigger wording](#trigger-wording)

## Decision

This is appropriately a skill: the durable value is a cross-project method and a small, transparent record format, not a new executor or platform. The scripts prevent routine clerical drift while
external project tools remain responsible for measurement.

## Concept decisions

| Concept | Decision | Failure mode prevented |
| --- | --- | --- |
| Evidence altitude | Adopt as extensible ranked layers; retain transport/stored/rendered/durable defaults. | A low-level acknowledgement becomes a claimed user-visible outcome. |
| Oracle independence | Adopt as a required, explicit path declaration. | A system verifies itself through the path under evaluation. |
| Honest denominator | Adopt as independently sourced population and required slices. | Coverage is calculated over convenient successes. |
| Falsifiability | Adopt, broadened beyond injection to six methods. | A green check has never shown it can detect a defect. |
| Validity | Adopt age plus declared invalidation events. | Historical truth is presented as current truth. |
| State honesty | Adopt five recorded verdicts and two derived states. | Ignorance, evaluator breakage, or staleness is misreported as system failure/pass. |
| Tiering | Adopt as project-declared execution authority. | An agent runs an unsafe live check. |
| Depth before breadth | Adopt as a workflow rule, not a schema field. | A wide suite hides whether any path reaches its intended outcome. |

## Format decisions

Suite files are YAML, with JSON-compatible YAML supported without dependencies. JSONL is the canonical append-only history because individual records can be appended and audited without a database.
Markdown reports are generated projections. SQLite was rejected for v0.1 because it adds a concurrency/migration surface without improving the core method; git history was rejected as the sole store
because it does not give structured per-run/slice queries or preserve uncommitted local observations.

## Examples and limitations

The network-controller example maps the source plan's A1–A14 axes, tiers, default layers, independent oracles, and lab-only injection constraint. It cannot express the source plan's full
canary-selection algorithm, fault-safety host-resolution guard, per-axis gate precedence, or matrix-cell update because those are executor/project policies, not portable evaluation contracts.

The financial-reconciliation example renames layers to parsed/posted/reconciled/signed-off and uses `historical_failure` and `counterexample` rather than injection. It demonstrates that names and
falsifiability methods generalize. It does not automate ledger extraction, accounting judgement, or a sign-off process.

## Deferred to v0.2

`validity.basis` is schema-reserved but not computed, hashed, compared, or invalidated automatically. Per-project decisions about implementation boundaries, configuration scope, and oracle versions
must precede basis hashing. Also deferred: concurrent-writer coordination, database back ends, history retention policy, dashboards, notifications, and any executor integration.

## Trigger wording

The description fires for defining, reviewing, recording, or maintaining operational evaluation, acceptance, and verification suites because those tasks need evidence contracts and durable truth. It
excludes routine unit tests, debugging, CI configuration, and LLM/prompt evaluation: those are either executors or a separate evaluation domain and would turn this skill into an overbroad test
framework.
