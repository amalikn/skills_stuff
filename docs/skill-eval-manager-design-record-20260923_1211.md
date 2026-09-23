# Design record — skill-eval-manager v0.1

The reasoning behind the skill at `/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-eval-manager/`: what problem it solves, whether a skill was the right shape for it, which concepts survived the
design pass, what the format choices cost, what the two worked examples actually proved, and what is deliberately unbuilt.

**Provenance.** The package was built on 2026-09-23 between 11:48 and 12:05 by an agent working from [the authoring prompt](skill-eval-manager-authoring-prompt-20260923_0846.md). This record was
written afterwards, at 12:11, by the session that independently verified the build — it is a reconstruction from the delivered artifacts, the prompt, and the verification run, not a transcript of the
builder's reasoning. Where it states what the builder decided, that is inferred from what shipped. Where it states a judgement, the judgement is the verifier's.

## Contents

- [The problem](#the-problem)
- [Is a skill the right shape](#is-a-skill-the-right-shape)
- [The concept set, after the pass](#the-concept-set-after-the-pass)
- [Format choices, and what they cost](#format-choices-and-what-they-cost)
- [What the two examples proved](#what-the-two-examples-proved)
- [What verification found](#what-verification-found)
- [Deliberately not built in v0.1](#deliberately-not-built-in-v01)
- [Open decisions for the operator](#open-decisions-for-the-operator)

## The problem

Projects accumulate claims about themselves — that a device is monitored, that a ledger reconciles, that a documented fact is still true — and those claims decay silently. The decay is rarely a bug in
the check. It is that the check was reported at the wrong altitude, or measured against a population chosen after the fact, or confirmed by the very system under test, or passed six weeks ago and has
not been true since.

A verified survey on 2026-09-23 established that no actively-maintained FOSS tool is purpose-built for managing that. The eval-management category exists but is ML-shaped: promptfoo, Inspect AI,
DeepEval, Evidently and Langfuse all own definitions, runner, scoring, history and dashboards, and all assume model outputs. The infrastructure equivalents — Powerpipe, Conftest, OpenSCAP, Chef InSpec
— define checks and report on them but keep no run history, so "this passed 30 days ago and fails now" is not answerable by the tool. Soda Core and Testkube were ruled out on licence.

So the gap is genuine, and it is narrow: the method, plus the small amount of machinery that no surveyed tool provides.

## Is a skill the right shape

Yes, with one qualification that shaped the whole package.

Most of the value is method, not code. Deciding that an oracle must not route through the path being evaluated, or that coverage is over the real population rather than the processed subset, is a
judgement an agent makes while writing a check. That belongs in a skill, where it is loaded at the moment the judgement is made — not in a library, where it would be loaded only by whoever already
knew to look.

The qualification: a method with no artifact is advice, and advice decays. So the skill ships three scripts — a validator, a recorder, a renderer — that make the method's rules mechanically checkable.
The validator is what stops this being another document nobody runs.

The risk in that qualification is the skill growing into a test framework. That is why the execution boundary is stated before anything else in `SKILL.md` and repeated in the anti-goals, with a named
tripwire: a scheduler, a parallel runner, a retry policy or an executor plugin system means it has drifted. An eval definition names its executor and does not embed one.

## The concept set, after the pass

Eight concepts survived. Each is listed with the failure it exists to prevent, because a concept without a named failure is decoration.

| Concept                        | Prevents                                                                               |
| ------------------------------ | -------------------------------------------------------------------------------------- |
| Evidence altitude, ranked      | Reading an HTTP 201 as proof of monitoring while 22 of 26 devices had stored no metric |
| Oracle independence            | A false pass that is unmeasurable by construction, because the system confirmed itself |
| Honest denominators            | Coverage of 4 of 4 processed, reported as coverage, when the estate is 3,096           |
| Falsifiability evidence        | A check that has never failed and cannot, sitting in the suite looking green           |
| Validity: age and change       | A verdict that was true, is stored, and has been wrong since the firmware changed      |
| State honesty                  | An unreachable oracle recorded as `fail`, making ignorance look like a defect          |
| Tiering by execution authority | An agent running a live fleet operation that only the operator should run              |
| Depth before breadth           | Five families declared working on transport-layer success, none proven end to end      |

Two changes were made to the source project's set, both from external review, and both are the reason this generalises:

**Staleness became validity.** Time is one way a verdict dies; declared change is another. `validity: {max_age, invalidate_on: [...]}` models both. A verdict from five minutes ago is worthless if the
implementation changed four minutes ago.

**Mandatory fault injection became falsifiability evidence.** Six methods are permitted — `injected_fault`, `fixture`, `mutation`, `counterexample`, `historical_failure`, `analytical_proof`. Injection
remains preferred. This resolved a contradiction the source project had not noticed in itself: its own safety rule makes injection lab-only and production read-only, so a mandatory-injection
requirement could never have been satisfied for its production evals.

A third change was made during verification review rather than accepted as proposed. External review suggested a flat seven-state verdict vocabulary. Two of those seven — `stale` and `not_evaluated` —
are not outcomes; they are expiry and absence. Recording them would freeze a judgement about freshness at the moment it was written, which is the bug the state exists to catch. So the vocabulary
splits: five recorded verdicts (`pass`, `fail`, `inconclusive`, `error`, `blocked`) and two states derived at read time. The schema makes a recorded `stale` unrepresentable and the validator rejects
it — verified.

## Format choices, and what they cost

**YAML for suites, JSONL for history, JSON Schema for both.** Suites are edited by hand and reviewed in diffs, so they need comments and readable nesting. History is appended by a script and never
edited, so a line-per-record format that cannot be half-written is right. JSON Schema was chosen over a bespoke validator because the schema files are readable by other tools, and over Rego or HCL
because neither is already in this ecosystem.

The scripts are standard-library Python. JSON-compatible YAML parses with no dependency at all; ordinary YAML needs PyYAML, which is OSI-licensed. That keeps the skill runnable in a project that has
installed nothing.

**Rejected: a scorecard file that is also the log.** The source project's plan had scorecards "appended to rather than rewritten", and a separate history store. Those are the same thing described
twice, and the version that survives contact with a human is the one that gets hand-edited. So history is the only thing written to, the scorecard is rendered from it every time, and no scorecard
template ships. If a scorecard template ever appears in this package, the model has been lost.

**Rejected: embedding executors.** An eval names `executor: {type, ref, args}` where type is `command`, `manual`, `query` or `external`. `manual` is first-class on purpose: some of the most valuable
evals are an operator following a procedure and recording what they saw, and a system that cannot record a human verdict gets worked around within a week.

**Rejected for v0.1: computed basis hashing.** See below.

## What the two examples proved

`examples/network-controller/` expresses the source project's 14 axes, its tiers, its default layers and its lab-only injection constraint. `BRIEF.md` names what the schema could not take: the
canary-selection algorithm, the fault-safety host-resolution guard, per-axis gate precedence, and the implementation-matrix cell update. That is the right answer — those are executor and project
policy, not portable evaluation contract — but it needed stating rather than quietly dropping.

`examples/financial-reconciliation/` is the generalisation test, and it passed on the two points that mattered:

- **Layers renamed and still worked.** `parsed`, `posted`, `reconciled`, `signed-off` at ranks 10/20/30/40. The invariant — evidence at a lower rank cannot prove a claim at a higher rank — is enforced
  on ranks, not on names, so the validator did not care that the vocabulary changed.
- **Falsifiability without injection.** It uses `historical_failure` and `counterexample`. Nothing is broken on purpose, because nothing in a production ledger safely can be.

If either had failed, the honest conclusion would have been that this is a network-infrastructure template wearing a skill's clothes.

## What verification found

The build was verified independently on 2026-09-23 rather than accepted on its own transcript. All five validator rules were made to fail on purpose and each produced a specific diagnostic;
supersession, declared invalidation, and the derived states were exercised end to end. Two defects were found and fixed:

1. **Every markdown file exceeded the 200-column prose rule**, and `SKILL.md`'s `description` was a single 42-word line. Reflowed; the description folded to a `>-` block matching
   `skill-walk-before-run`. Frontmatter re-parsed and the description text confirmed to round-trip unchanged.
2. **`render_report.py` collapsed two states into one reason string** — `validity expired or invalidated` covered both an aged-out verdict and a declared change. A skill whose thesis is that merged
   states hide different actions was merging two states that call for different actions: re-run it, versus find out what changed. Fixed in v0.1.1 to report `expired: older than <max_age>` and
   `invalidated: <trigger> (<reference>)` separately, and both when both apply. The four checked-in example reports were regenerated.

The second is worth recording rather than quietly fixing, because it is the most instructive thing about this build: a skill can fail its own principle in its own code while every document about it
reads correctly.

## Deliberately not built in v0.1

- **Computed basis hashing.** `validity.basis` is reserved in the schema with `implementation_ref`, `config_hash` and `oracle_version`, and nothing computes it. Computing a basis means knowing, per
  project, what counts as the implementation and how to hash it. That is a per-project question, and guessing it now would buy a feature no real question has been asked of. `invalidate_on` entries are
  declared labels raised as invalidation events, which is enough to be useful and cheap to replace.
- **A dashboard.** Markdown reports are legible in a terminal, in a diff, and in a pull request. A dashboard can be added when someone asks a question a report cannot answer.
- **Trend and regression queries.** History supports them; nothing queries it yet. Wait for a real question.
- **Any executor machinery.** Permanently out of scope, not deferred.

## Open decisions for the operator

1. **Install now, or after a first real suite?** Options: symlink into `~/.claude`, `~/.codex` and `~/.hermes` now; or run it unlinked against one real project first. **Recommendation: install now.**
   The trigger wording only gets tested by being loaded, and the skill is read-only against any project it is pointed at.
2. **Which project gets the first real suite?** Options: the network controller, whose framework is already written and whose P0/P1 work is queued; or a smaller project where a suite can be finished
   in one sitting. **Recommendation: the network controller**, because its framework already exists and the suite would otherwise be written twice.
3. **Where does the history file live in a consuming project?** Options: in the repo beside the suite, committed; or in a data directory outside it. **Recommendation: in the repo, committed.** It is
   evidence, it is small, and the diff is the audit trail.
4. **Does a `blocked` verdict satisfy a gate, or fail it?** The skill records it honestly either way, but the consuming project needs a policy. **Recommendation: `blocked` never satisfies a gate**, so
   that a check nobody can run does not read as a check that passed.
5. **Should `validate_suite.py` run in this repo's own checks?** Options: leave it to consuming projects; or wire it into a skills-level check so the shipped examples cannot rot. **Recommendation:
   wire it in**, since the examples are the only executable proof the schema still works.
6. **v0.2 trigger for basis hashing.** Options: build it when the first project asks "did this change since we measured it?" and cannot answer; or schedule it. **Recommendation: wait for the
   question**, and record it in `BRIEF.md` when it is asked.
