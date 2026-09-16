# Routing Evaluations

Agent Stack treats routing as a behaviour that must be regression-tested, not merely described in prose.

## What is covered

`evals/routing-cases.toml` contains 60 representative cases across six workload families:

| Family | Cases | Coverage |
| --- | ---: | --- |
| networking-infrastructure | 15 | BGP/OSPF/PPPoE/RADIUS/DNS, migrations, automation, observability, security, NAS/Linux operations |
| software-ai-engineering | 10 | repository audits, Python/API work, security review, agent routing, skill creation, GitHub research, UX/UI, release readiness |
| jdm-import | 12 | demand, landed economics, GO/NO-GO, import eligibility, customs/GST research, auction data, sourcing, pilot, warranty, channels, portal |
| attar-import | 8 | demand, landed economics, suppliers, import/compliance research, pilot, positioning, pricing, generic import opportunity |
| business-research | 8 | pricing, forecasting, business models, market sizing, competitors, sales/content, current LLM market research |
| direct-adversarial | 7 | narrow direct-skill routing, team-inflation prevention, weak evidence, current regulation, ambiguous product recommendations |

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

Required/forbidden/ownership/gate/team-size assertions are hard requirements. Preferred selections improve the diagnostic score but do not make a route fail; this avoids overfitting the orchestrator to one exact valid team.

## Static validation

No model is called:

```bash
mise run routing-eval-check
# or
python scripts/evaluate_routing.py --validate-only
```

This verifies the corpus, IDs, ownership references and contradictions.

## Behavioral evaluation

`scripts/evaluate_routing.py` can invoke a **real local agent/model CLI**. The command must accept the evaluation prompt on standard input and return a JSON routing plan on standard output (wrapping CLI noise is tolerated when a JSON object can be extracted).

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

Agent Stack deliberately does **not** hard-code Claude Code, Codex, DeepSeek, or another provider's CLI syntax. CLI interfaces change and different operators use different frontends. The evaluator owns the input/output contract; an environment-specific command is the adapter.

Useful selectors:

```bash
# One workload family
python scripts/evaluate_routing.py --command '<cmd>' --family networking-infrastructure

# Particular cases
python scripts/evaluate_routing.py --command '<cmd>' --case net-bgp-flap --case jdm-landed-cost

# Cheap smoke run
python scripts/evaluate_routing.py --command '<cmd>' --limit 6
```

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

## Adding cases

Add a case when one of these is true:

- a real task exposed a routing mistake;
- a new domain becomes common enough to deserve regression coverage;
- a new persona/skill changes routing boundaries;
- the same unnecessary persona repeatedly appears;
- a material gate such as Research/CFO/CTO/QA/Critic is missed.

Prefer real operator tasks over synthetic permutations. Keep the suite representative rather than exhaustive.
