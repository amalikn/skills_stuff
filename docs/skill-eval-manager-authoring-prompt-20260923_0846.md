# Authoring prompt — skill-eval-manager

A prompt to hand to an AI agent so it builds a new global skill, `skill-eval-manager`: the complete package — directory tree, `SKILL.md`, references, schemas, scripts, templates and worked examples —
not a plan about one. Written 2026-09-23 after a verified survey found no FOSS tool purpose-built for managing an evaluation suite over an operational, non-ML system. Revised the same day after
external review, which sharpened the execution boundary, the data model, the verdict vocabulary, and turned staleness into validity.

Copy everything between the rulers. Everything outside them is context for the operator, not for the agent.

## Contents

- [What this prompt is for](#what-this-prompt-is-for)
- [The prompt](#the-prompt)
- [Notes for the operator](#notes-for-the-operator)

## What this prompt is for

One project on this machine already has a fully worked evaluation framework, written as a plan:
`/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/evaluation-framework-implementation-20260923_0819.md`. It defines axes, oracles, evidence altitudes, tiers, scorecards,
staleness and a fault-injection catalogue. All of that is project-specific prose. The reusable part — how to define an eval, where its evidence must be read, when a verdict stops being true, what
makes a check falsifiable — is not project-specific, and nothing in the installed skill set covers it.

The survey that produced this prompt is summarised in the prompt itself so the agent does not repeat it. The headline: the eval-management category exists but is ML-shaped, and the infrastructure
equivalents keep no run history.

## The prompt

---

You are building a new global agent skill called `skill-eval-manager`. **Deliver the complete, working skill package — every file, written in full — not a plan for one.** A short design record
accompanies it, but the skill itself is the deliverable.

### What the skill is for

A skill that helps an agent or an operator **define, manage and maintain a project's evaluation suite over time**. "Evaluation" here means: a claim about whether a system actually does what it says,
measured at a stated layer, against an independent source of truth, over a stated population, with a validity that can expire.

### The execution boundary — read this before anything else

This skill **defines, validates, records, reports and invalidates**. It **does not execute**. Execution belongs to whatever already runs in the project.

| The skill owns                                    | The project's own executors own         |
| ------------------------------------------------- | --------------------------------------- |
| eval definitions and their schema                 | pytest, unittest                        |
| well-formedness validation                        | shell scripts, CLI probes               |
| the evidence contract (oracle, layer, population) | API calls, SNMP/SSH probes              |
| verdict vocabulary and recording                  | Ansible, Playwright, SQL queries        |
| history and its retention                         | monitoring queries                      |
| reporting and scorecard rendering                 | manual operator procedures              |
| validity, expiry and change-based invalidation    | anything else that can produce a result |

An eval definition therefore names its executor rather than embedding one:

```yaml
executor:
  type: command          # command | manual | query | external
  ref: ./checks/device_metrics.py
  args: ["--type", "epmp-ap"]
```

`type: manual` must be first-class: some of the most valuable evals are an operator following a procedure and recording what they saw. A skill that cannot record a human verdict will be worked around
within a week.

If you find yourself writing a scheduler, a parallel runner, a retry policy or a plugin system for executors, stop — that is the skill becoming a test framework, which is the failure mode this section
exists to prevent.

### Why it does not already exist — verified survey, 2026-09-23

Do not re-run this survey. Treat it as given, and say so if you believe any line is wrong.

- No actively-maintained FOSS tool is purpose-built for managing an evaluation suite over a non-ML, non-cloud-config operational system. This was checked, and "none found" was the verified answer.
- The purpose-built eval-suite managers are all ML-shaped: promptfoo (MIT, YAML definitions, SQLite history, eval-vs-eval compare), Inspect AI (MIT, Python tasks), DeepEval (Apache-2.0, regression
  tracking is in the commercial product), Evidently (Apache-2.0, OSS dashboard plots a metric across saved reports over time), Langfuse (MIT core, `ee/` trees under a commercial licence).
- The infrastructure equivalents define and run checks and report, but **none keeps run history**, so "this passed 30 days ago and fails now" is not answerable by the tool: Powerpipe (AGPL-3.0, HCL
  controls, real dashboards), Conftest/OPA (Apache-2.0, Rego), OpenSCAP and ComplianceAsCode (LGPL-2.1 / BSD-3-Clause, YAML compiled to XCCDF), Chef InSpec (repo Apache-2.0 but packaged distributions
  require the Progress Chef EULA from version 5).
- Ruled out on licence: Soda Core (Elastic License 2.0), Testkube (dual MIT plus a community licence, and no OSS dashboard).
- Data-quality frameworks are the closest working analogue: Great Expectations (Apache-2.0) accumulates validation results and indexes them chronologically in Data Docs, but has no trend or regression
  query.

The gap the skill fills is therefore the **method**, plus the small amount of machinery no surveyed tool provides. If you conclude some part is better filled by adopting one of the FOSS tools above
than by writing it, say so and wire the skill to that tool instead of reimplementing it — that is a legitimate finding, not a failure.

### The core artifact model

Build to this model. It separates what is recorded from what is derived, which is the distinction that keeps a suite honest.

```
Suite
 └── EvalDefinition
      ├── claim              what is asserted, in one sentence
      ├── population         the denominator, defined independently of the system
      ├── oracle             how ground truth is established, and by what path
      ├── observation_layer  the altitude the claim is true at
      ├── executor           reference to whatever produces the result
      ├── validity           max_age plus what else invalidates it
      └── falsifiability     the evidence that this check can fail

EvaluationRun                one episode: when, by whom, against what basis
 └── Observation             one eval, one population slice, one measured value
      └── Verdict            the judgement, with its evidence pointer

HistoryStore                 append-only, canonical, the only thing written to
 └── Report / Scorecard      derived projection of latest verdicts; regenerated, never appended
```

Two rules follow, and both matter:

- **The history store is the record. The scorecard is a view.** Never append to a scorecard file; render it from history every time. A scorecard that is also the log will eventually be hand-edited,
  and then it is neither.
- **The store is append-only.** A corrected measurement is a new observation that supersedes an earlier one, not an overwrite. "What did we believe on 1 October, and were we wrong?" must stay
  answerable.

### Verdict vocabulary

Do not collapse evaluation state into pass, fail and stale. The whole point of the skill is refusing to merge states that mean different things.

**Recorded verdicts** — written to history by an actual observation:

| Verdict        | Meaning                                                                     | Why it is not FAIL                                             |
| -------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `pass`         | claim held at its stated layer                                              |                                                                |
| `fail`         | claim did not hold                                                          |                                                                |
| `inconclusive` | the eval ran, but the oracle could not establish truth                      | an unavailable oracle is ignorance, not a defect in the system |
| `error`        | the evaluator itself broke                                                  | a broken check says nothing about the system                   |
| `blocked`      | preconditions unmet — credentials absent, operator-only tier, unsafe to run | not attempted is not a result                                  |

**Derived states** — computed at read time, never stored:

| State           | Computed when                                                              |
| --------------- | -------------------------------------------------------------------------- |
| `stale`         | a recorded verdict exists but its validity has expired or been invalidated |
| `not_evaluated` | no observation exists for this eval and population slice                   |

Storing `stale` is a bug: it freezes a judgement about freshness at the moment it was written. Storing `not_evaluated` is a bug for the same reason. Your schema must make both unrepresentable as
recorded verdicts, and your validator must reject them if a project tries.

### Observation layers, and the invariant that matters

The controller project uses four layers — transport, stored, rendered, durable. Ship that as the **default vocabulary**, not as the definition. Layers are ranked and extensible:

```yaml
observation_layer:
  id: stored
  rank: 20
```

The invariant is what generalises, not the names:

> Evidence gathered at a lower-ranked layer can never prove a claim made at a higher-ranked layer.

That is the rule your validator enforces. A project in a different domain will name its layers differently — `parsed`, `posted`, `reconciled`, `signed-off` — and the invariant still holds. If you can
state the invariant without reference to the four default names, you have generalised it correctly.

### Validity: time is only one way a verdict dies

A verdict older than its window is stale. A verdict from five minutes ago may also be worthless if the thing it judged has changed since. Model both:

```yaml
validity:
  max_age: 30d
  invalidate_on:
    - implementation_change
    - config_change
    - oracle_change
    - population_change
```

For v0.1, `invalidate_on` entries are declared labels that a human or a project script raises — a recorded invalidation event against the eval. Design the schema so that a future version can attach a
computed basis:

```yaml
basis:
  implementation_ref: git:abc123
  config_hash: "..."
  oracle_version: "..."
```

but **do not build basis hashing in v0.1**. Computing a basis requires knowing, per project, what counts as the implementation and how to hash it. That is a per-project question, and guessing it now
buys a feature nobody has asked a real question of yet. Leave the field reserved, say so in `BRIEF.md`, and park it for v0.2.

### Falsifiability, not mandatory fault injection

A check that cannot fail is noise. Every eval must therefore carry evidence that it *can* fail. Fault injection is the strongest form of that evidence and the preferred one — but it is not always
available, because some systems cannot safely be broken on purpose: production financial reconciliation, certificate expiry, legal or document provenance, third-party vendor API behaviour,
verification of historical state.

Require the evidence, permit several methods:

```yaml
falsifiability:
  method: injected_fault | fixture | mutation | counterexample | historical_failure | analytical_proof
  ref: ...
  verified_at: 2026-09-23
```

`historical_failure` is worth calling out: "this check caught a real defect on this date" is genuine falsifiability evidence, and often the only kind available for a production-only eval. What your
validator must reject is an eval with **no** falsifiability evidence at all — not one that used a method other than injection.

Note that this also resolves a contradiction in the source project: its own safety rule makes fault injection lab-only and production read-only, so a mandatory-injection rule could not have been
satisfied for its production evals.

### Where it goes

**Global skill, decided by the operator.** Author it at:

```
/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-eval-manager/
```

Not in `specialists/project/`. Do not re-open the placement question. Skills are authored in `skills_stuff` and never in an install target; installs into agent homes (`~/.claude/skills/`,
`~/.codex/skills/`, `~/.hermes/skills/`) are symlinks back to the canonical directory, never copies. **Do not create those symlinks yourself** — propose the exact commands in your final report and let
the operator run them.

### Required package structure

This is the starting shape, matched to how skills in that tree are already built. Deviate where you can justify it, and say why in the design record; do not deviate silently.

```
skill-eval-manager/
  SKILL.md                    # entry point: frontmatter + the method, kept short
  README.md                   # what it is, package map, install commands, last-reviewed date
  CHANGELOG.md                # v0.1.0 entry, dated, saying what shipped and why
  BRIEF.md                    # design rationale, rejected options, items parked for v0.2
  references/
    01_overview.md            # the method in full: concepts, failure modes, worked reasoning
    02_defining-evals.md      # a well-formed eval, with good and bad examples
    03_verdicts-and-validity.md
    04_falsifiability.md      # proving a check can fail, by each permitted method
    05_reporting.md           # history, scorecards, what a report must state
  schemas/
    eval-definition.schema.json
    observation.schema.json
    falsifiability.schema.json
  templates/
    evals.yaml                # a starter suite an operator copies into a project
  scripts/
    validate_suite.py         # schema + invariant checks; exits non-zero on failure
    record_result.py          # append one observation to the history store
    render_report.py          # history -> scorecard + markdown report, computes stale/not_evaluated
    README.md                 # purpose, inputs, outputs, safety label, idempotency per script
  examples/
    network-controller/       # worked example 1
    <second-domain>/          # worked example 2, a deliberately unlike domain
```

No `scorecard` template: the scorecard is rendered, never authored. If you ship one, you have not internalised the model.

Every file listed must be written in full. An empty stub, a `TODO`, or a file whose content is a description of what it would contain does not count as delivered.

### SKILL.md contract

- YAML frontmatter with `name`, `description`, and a `metadata` block carrying `version: 0.1.0` and any `aliases`.
- `description` is the trigger — it is what an agent reads to decide whether to load the skill. Write it to fire on defining, reviewing, recording or maintaining evals, acceptance criteria or
  verification suites, and **not** to fire on ordinary unit testing, debugging, or LLM output evaluation. State in the design record what it must fire on and what it must not, and why you worded it as
  you did.
- Keep `SKILL.md` short and operational. It carries the method's spine and the workflow; the depth lives in `references/`, loaded only when needed. A long `SKILL.md` is a cost paid on every
  invocation.
- It must contain the workflow the agent follows step by step, the conditions under which the skill **refuses** and stops to ask the operator, and its own quality gate.
- The skill must not modify itself.

Read `skill-walk-before-run` in that tree before you write a line of it. It is the closest in spirit — also a discipline gate rather than a domain pack — and shows the house style for frontmatter,
aliases, references and a `BRIEF.md` parked-items section.

### The concepts the skill has to carry

These came out of real incidents. Adopt, rename, merge or reject each one with a reason recorded in `BRIEF.md` — do not simply restate them.

1. **Evidence altitude.** Every claim declares the layer it is true at, and evidence from a lower-ranked layer cannot prove it. This exists because an HTTP 201 was read as proof of monitoring while 22
   of 26 devices had never stored a metric.
2. **Oracle independence.** Ground truth must not come through the path being evaluated, or a false pass is unmeasurable by construction.
3. **Honest denominators.** Coverage is over the real population, never over the subset that happened to be processed.
4. **Falsifiability.** A check that cannot fail is noise; every eval carries evidence that it can.
5. **Validity.** A verdict dies of age or of change, and both are declared rather than assumed.
6. **State honesty.** Ignorance, breakage and blockage are not failure, and freshness is computed rather than stored.
7. **Tiering by who may run it.** Cheap offline checks an agent may run, versus live checks against real systems that only the operator runs.
8. **Depth before breadth.** One unit of one type taken to the operator-visible outcome before widening.

### Two worked examples, one deliberately unlike the other

The skill is global and must serve any project on this machine. One project has a fully worked evaluation framework already, which makes it the cheapest validation case — but it is network
infrastructure, and a method derived only from it will overfit.

Read, before writing anything:

- `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/evaluation-framework-implementation-20260923_0819.md` — 14 axes, five tiers, scorecard schema, fault-injection
  catalogue, gate rules.
- `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/docs/device-type-implementation-matrix-20260922_2220.md` — the human-facing tracker the scorecards are meant to back.
- `/Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/AGENTS.md` — the canary rule, the deletion rule, the inherited-constraints rule.

Then ship `examples/network-controller/` as a real suite file expressing that framework through your schema, and name in `BRIEF.md` anything in it your schema **cannot** express.

Ship a second example from a deliberately different domain — for example a financial reconciliation workspace where the evals are about figures agreeing across independent sources, or a documentation
and governance repo where they are about recorded claims still being true. That second domain is also the test of two things specifically: whether your layer vocabulary survives being renamed, and
whether falsifiability works without injection. Say honestly which concepts do not survive the move. A skill that only fits the project it was derived from is a template, not a skill.

### Proof it works

Before you report done:

- Run `validate_suite.py` against both example suites. Include the real output in your report. If it passes trivially because it checks nothing, that is a finding about your own validator.
- Break things on purpose in a copy of an example suite, and show the validator catching each one: a missing oracle; an outcome claimed at a layer its evidence cannot support; an eval with no
  falsifiability evidence; a recorded verdict of `stale`; an oracle that routes through the path under evaluation. A validator that has never been made to fail is exactly the noise this skill exists
  to prevent.
- Record observations through `record_result.py` and render through `render_report.py`, and show the output. The render must demonstrate `stale` and `not_evaluated` being computed rather than read.
- Show a superseded measurement: record a value, record a correction, and show that history retains both while the scorecard shows only the later one.

### Governance

- Markdown: prose wrapped at 200 columns, tables on single lines, a `## Contents` block on any file over 100 lines, time-bound filenames as `<slug>-YYYYMMDD_hhmm.md`. Fixed entrypoints (`SKILL.md`,
  `README.md`, `CHANGELOG.md`, `BRIEF.md`) keep their names.
- Verify the current date and time by running `date` before writing any timestamp. Do not infer one that looks plausible.
- `scripts/README.md` must record purpose, inputs, outputs, safety label and idempotency for every script.
- Do not create, move or delete anything outside `skill-eval-manager/` and the one design record. In particular, **do not edit the controller project** — it is a read-only input here. If you believe
  it needs changing, say so in the report.
- Work the skill quality checklist explicitly as a blocking gate before declaring done, item by item, not as a retrospective summary.

### Anti-goals — state these in the skill so they cannot drift back in

- Not an executor, scheduler or test runner. It records what executors produce.
- Not an LLM or prompt evaluator.
- Not a replacement for pytest, and not a new assertion DSL where a plain test function would do.
- Not a CI product, and not tied to any CI vendor.
- Not a monitoring or alerting system. Evals judge whether the system's own claims are true; monitoring watches the system itself.
- No dependency on a non-OSI-licensed tool.

### The design record

Alongside the package, write one markdown design record covering: the problem in your own words; an explicit judgement on whether a skill is the right shape for this at all; the concept set after your
adoption/rejection pass, each with its failure mode named; the format choices and what you rejected; what the two examples proved and what they exposed; what is deliberately deferred to v0.2,
including basis hashing; and numbered open decisions for the operator, each with options and your recommendation.

**Ask where to save the design record.** Do not assume.

### How to work

- Read the three project files named above, and at least two existing skills in the canonical tree, before writing anything.
- Verify any external claim against an official source. Label load-bearing claims verified or unverified. Record negative findings rather than omitting them.
- State assumptions that materially change the design.
- Where you disagree with anything in this prompt, say so in the design record with your reasoning. Do not silently comply.
- Report honestly at the end: what you built, what you ran, what the output actually was, what you did not do, and what remains unproven. If something failed, show it.

---

## Notes for the operator

- The prompt deliberately gives the agent the survey result so it does not spend a round re-deriving that no such FOSS tool exists. If that survey is ever refuted, update this prompt before reusing
  it.
- The three demands most likely to be skipped: naming what the controller framework *cannot* express through the new schema; breaking the validator on purpose; and shipping `type: manual` as a real
  executor rather than an afterthought.
- The execution boundary is the section that keeps v0.1 small. If the returned package contains a scheduler, a retry policy or an executor plugin system, it has drifted.
- Basis hashing is deliberately deferred. If the agent builds it anyway, that is scope it was told not to take.
- Symlink installs are deliberately withheld from the agent. It proposes the commands; you run them.
- The design record's save location is the one thing left open, because it depends on whether the record belongs beside the skill or in `skills_stuff/docs/` with this prompt.
