# Routing Evaluations

Agent Stack treats routing as a behaviour that must be regression-tested, not merely described in prose.

## Contents

- [What is covered](#what-is-covered)
- [What each case can assert](#what-each-case-can-assert)
- [Gate scoring is asymmetric](#gate-scoring-is-asymmetric)
- [Static validation](#static-validation)
- [Behavioral evaluation](#behavioral-evaluation)
- [Coverage is reported, never inferred](#coverage-is-reported-never-inferred)
- [Behavioral output contract](#behavioral-output-contract)
- [Why not require one exact route?](#why-not-require-one-exact-route)
- [The unseen holdout](#the-unseen-holdout)
- [Adding cases](#adding-cases)

## What is covered

`evals/routing-cases.toml` contains 60 representative cases across six workload families:

| Family                    | Cases | Coverage                                                                                                                                |
| ------------------------- | ----: | --------------------------------------------------------------------------------------------------------------------------------------- |
| networking-infrastructure | 15    | BGP/OSPF/PPPoE/RADIUS/DNS, migrations, automation, observability, security, NAS/Linux operations                                        |
| software-ai-engineering   | 10    | repository audits, Python/API work, security review, agent routing, skill creation, GitHub research, UX/UI, release readiness           |
| jdm-import                | 12    | demand, landed economics, GO/NO-GO, import eligibility, customs/GST research, auction data, sourcing, pilot, warranty, channels, portal |
| atar-import               | 8     | demand, landed economics, suppliers, import/compliance research, pilot, positioning, pricing, generic import opportunity                |
| business-research         | 8     | pricing, forecasting, business models, market sizing, competitors, sales/content, current LLM market research                           |
| direct-adversarial        | 7     | narrow direct-skill routing, team-inflation prevention, weak evidence, current regulation, ambiguous product recommendations            |

These are **routing contracts**, not expected final answers to the domain tasks.

## What each case can assert

A case may define:

- `required_personas`
- `preferred_personas`
- `forbidden_personas`
- `required_skills`
- `preferred_skills`
- `forbidden_skills`
- `primary_owner`
- `max_personas`
- `research_required`
- `critic_required`
- `qa_required`
- `runtime_required`

Required/forbidden/ownership/team-size assertions are hard requirements. Preferred selections improve the diagnostic score but do not make a route fail; this avoids overfitting the orchestrator to one
exact valid team. Gate assertions are hard in one direction only — see below.

## Gate scoring is asymmetric

The four gate flags are scored differently depending on which way the route is wrong.

| Case says | Route says | Class                 | Cost      | Decides pass/fail |
| --------- | ---------- | --------------------- | --------- | ----------------- |
| `true`    | `false`    | `gate_false_negative` | -20, hard | Yes               |
| `false`   | `true`     | `gate_false_positive` | -5, soft  | No                |

A false negative is an omitted obligation: the case requires the gate and the route does not carry it. A false positive is over-routing: wasteful, but the work still gets done. Weighting them equally
would make a cautious route indistinguishable from one that skipped a required gate; weighting the false positive at zero — which is what the scorer did before 2026-09-02 — makes "set every flag true"
a free strategy that beats honest routing on every case with a required gate. Claude did exactly that on `market-size` in Baseline v4, and paid nothing for it.

Both classes are counted per case, stored in every result row as `gate_false_negatives` / `gate_false_positives`, and totalled in the run summary, so a stored baseline can be re-analysed for
over-assertion without calling a model again.

`runtime_required` participates in both directions but is scored against the **computed** value — true exactly when a selected skill declares `execution = "tool"` — so a model that reports it without
selecting a tool skill is corrected rather than penalised. Only the three judged gates can be over-asserted.

## Static validation

No model is called:

```bash
mise run routing-eval-check
# or
python scripts/evaluate_routing.py --validate-only
```

This verifies the corpus, IDs, ownership references and contradictions.

## Behavioral evaluation

`scripts/evaluate_routing.py` can invoke a **real local agent/model CLI**. The command must accept the evaluation prompt on standard input and return a JSON routing plan on standard output (wrapping
CLI noise is tolerated when a JSON object can be extracted).

```bash
python scripts/evaluate_routing.py \
  --command '<your local agent CLI command>' \
  --family jdm-import \
  --output routing-results/jdm.jsonl
```

Or configure an environment-specific command without placing it in repository policy:

```bash
export AGENT_STACK_EVAL_COMMAND='<your local agent CLI command>'
mise run routing-eval-smoke
```

Agent Stack deliberately does **not** hard-code Claude Code, Codex, DeepSeek, or another provider's CLI syntax. CLI interfaces change and different operators use different frontends. The evaluator
owns the input/output contract; an environment-specific command is the adapter.

Useful selectors:

```bash
# One workload family
python scripts/evaluate_routing.py --command '<cmd>' --family networking-infrastructure

# Particular cases
python scripts/evaluate_routing.py --command '<cmd>' --case net-bgp-flap --case jdm-landed-cost

# Cheap smoke run
python scripts/evaluate_routing.py --command '<cmd>' --limit 6
```

## Coverage is reported, never inferred

Every run prints the pool it drew from before any `--limit` applies:

```text
covered 12/12 cases (family jdm-import)
```

and, when truncated:

```text
WARNING: partial corpus run - 10/12 cases evaluated; --limit 10 truncated the family jdm-import. Not a baseline.
```

This exists because the first Baseline v2 pass ran `--limit 10` per family and covered 53 of 60 — `networking-infrastructure` has 15 cases and `jdm-import` 12 — while printing per-family lines that
read as complete. A partial run is a smoke test. It is never a baseline.

## Behavioral output contract

The evaluated model is asked **not to execute the task**. It must return only a routing plan:

```json
{
  "route_mode": "direct-skill | single-persona | multi-persona",
  "primary_owner": "persona-id-or-null",
  "personas": ["persona-id"],
  "skills": ["skill-id"],
  "research_required": true,
  "critic_required": false,
  "qa_required": false,
  "runtime_required": false,
  "reason": "brief rationale"
}
```

The harness scores what the model actually selected against the case contract.

## Why not require one exact route?

Several tasks legitimately admit more than one good supporting team. The test therefore separates:

1. **hard invariants** — who/what must or must not be selected, decision ownership, gates and team-size limits;
2. **preferred composition** — useful supporting personas or skills that are context-sensitive.

This tests routing intelligence without reducing orchestration to a static lookup table.

## The unseen holdout

`evals/holdout-cases.toml` holds **24 cases authored 20260902 blind to the development 60** — 5 networking, 5 JDM, 4 software, 4 atar, 3 business-research, 3 direct-adversarial. Nothing was read from
the frozen corpus while authoring but its schema: the key names, the six `mode` values and the observed `max_personas` range, printed by a script that displayed no task, no id and no expectation.

Task text was written first and in full; ownership, gates and capabilities were assigned afterwards from the task as written. Gate coverage was **not** balanced deliberately — 13 of the 24 assert no
gate at all, 6 research, 4 critic, 1 QA, 6 runtime. That distribution is what plausible work produced, not a target, and it is the point: a corpus balanced for gate coverage measures the router
against a design rather than against the job.

Run it through the guarded recipe, never by hand:

```bash
HOLDOUT_PROVIDER=anthropic HOLDOUT_MODEL=claude-opus-5 HOLDOUT_RUNNER=claude-code \
  HOLDOUT_OUT="$RESULTS/holdout24-claude-20260902.jsonl" just holdout 'claude -p'
```

`holdout` depends on `_require-freeze`, so a drifted checkout refuses to spend it, and it demands provider/model/output labels because an unlabelled holdout row cannot be compared to anything later.

**It is single-use.** Once executed the 24 are spent: tuning anything against their failures converts them into development cases and destroys the only property that makes them worth running. If a
case turns out to be wrong *on its own terms* — self-contradictory, or asserting something the catalogue cannot express — retire it explicitly and record why. Never quietly re-tune it into agreement
with the router.

## Adding cases

Add a case when one of these is true:

- a real task exposed a routing mistake;
- a new domain becomes common enough to deserve regression coverage;
- a new persona/skill changes routing boundaries;
- the same unnecessary persona repeatedly appears;
- a material gate such as Research/CFO/CTO/QA/Critic is missed.

Prefer real operator tasks over synthetic permutations. Keep the suite representative rather than exhaustive.
