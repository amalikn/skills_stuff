# Agent Stack Revision Notes — 2026-09-01

This revision responds to the repository audit and a deeper design review focused on persona definition quality, skill execution contracts, and orchestration intelligence.

## Major changes

### Persona contracts

All 15 personas were expanded from short role prompts into operational judgement contracts. Domain personas now define mandate, use/non-use boundaries, decision lens, required questions, operating
method, preferred skills, hand-offs, boundaries, quality bar, and output contract. `orchestrator-follett` is deeper and explicitly owns task classification, routing, hand-offs, disagreement handling,
and synthesis.

### Intelligent routing

Added `routing.toml` as Agent Stack's routing catalogue:

- persona domains/intents/decision ownership;
- skill intents and likely persona consumers;
- `analysis` versus `tool` execution class;
- runtime prerequisites and safety notes;
- mandatory gates for economics, architecture, material-risk challenge, evidence-heavy work, and product experience.

Rewrote `skills/skill-agent-stack/SKILL.md` and `skills/team/SKILL.md` around decision ownership, direct-vs-orchestrated routing, minimal-team selection, tool prerequisite checks, sequence/hand-offs, gate
logic, and explicit anti-team-inflation rules.

Added `evals/routing-cases.toml` plus unit tests for representative routes.

### Skill/runtime contract

Added:

- `RUNTIME.md` — root environment and consumer-isolation policy;
- `SKILL_STANDARD.md` — local skill quality/trigger/runtime/safety contract;
- root `.mise.toml` with Python + uv + automatically created `.venv`;
- `requirements-dev.txt`;
- `scripts/validate_agent_stack.py`;
- `just bootstrap` / `just check` convenience tasks.

Tool skills with Python helpers now explicitly reference isolated runtime expectations.

### Concrete skill repairs

- `skills/skill-creator/scripts/quick_validate.py` now accepts metadata keys already used by current Agent Stack skills.
- `startup-business-models` now contains the resources/templates/data registry that its SKILL.md referenced, and its missing related-skill links were replaced with existing Agent Stack capabilities.
- `deep-research` no longer requires hidden `~/.claude/research_output` state, automatic viewer opening, forced Documents output, or continuation-agent chains under Agent Stack.
- `websh` now has an explicit Agent Stack adaptation disabling implicit background agents, eager crawling, and persistence unless explicitly authorised.

### Portability / install consistency

- README path examples are location-independent.
- Manifest install method now reflects individual symlinks.
- Global installer preserves Git primary-worktree protection when Git metadata exists, while allowing an extracted distribution archive to act as its own canonical root.

## Validation

Run:

```bash
mise install
mise run bootstrap
mise run check
mise run test
```

At packaging time:

- static Agent Stack validation: PASS;
- 32 unit tests: PASS;
- all package skills pass the revised quick validator.

## Deliberately not changed

This revision does not rewrite the upstream-sync transaction model or implement atomic sync/TOCTOU hardening from audit findings A1/A2. Those are valid maintenance-layer improvements but were kept
separate from this revision's primary goal: better personas, skill contracts, runtime hygiene, and orchestration intelligence.


## Routing evaluation expansion — 2026-09-01

- Expanded the routing corpus from 6 representative cases to 60 real-workload cases across networking/infrastructure, software/AI engineering, JDM importing, atar/general importing,
  finance/business/research, and direct/adversarial routing.
- Expanded `routing.toml` with explicit network engineering, infrastructure operations, import evidence, import economics, supply-chain/operations, current-fact and regulatory-research intents and
  gates.
- Added hard assertions for primary ownership, forbidden skills, maximum team size, Research/Critic/QA/runtime gates, plus preferred-route diagnostics.
- Added `scripts/evaluate_routing.py`, which can invoke an actual local model/agent CLI over stdin and score its routing output; this is behavioral evaluation rather than TOML-only validation.
- Added `ROUTING_EVALS.md` and `mise`/`just` entry points for corpus validation and behavioral smoke/full runs.
- Added routing profiles and preflight checks to the orchestrator for networking/infrastructure and physical-product/import workflows.
