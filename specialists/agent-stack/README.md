# Agent Stack

Agent Stack is the reusable, English-only extraction of Auto Company’s personas and skill library. It intentionally excludes Auto Company’s autonomous loop, consensus mechanism, daemon, and other
no-human-gate operating patterns.

## Contents

- [Use](#use)
- [Upstream refresh](#upstream-refresh)
- [Safety model](#safety-model)
- [Intelligent routing](#intelligent-routing)
- [Governance pointers](#governance-pointers)
## Use

Agent Stack is canonical source material under `specialists/`. Its default delivery path is a global, symlink-only install for Claude Code, Codex, and compatible agents that discover
`~/.agents/skills`. Do not copy its contents.

```bash
cd /path/to/agent-stack
just global-dry-run
just global-install install
```

This links personas into Claude Code and skills into `~/.claude/skills`, `~/.codex/skills`, and `~/.agents/skills`. The last target is for compatible agents that explicitly discover that standard
path; it is not a claim that every agent does. The installer never copies source content or overwrites a pre-existing global entry. Agent Stack’s duplicate `skill-creator` remains excluded by default;
pass `--include skill-creator` only after deliberately reconciling it.

The original per-project directory-symlink arrangement remains available for a project that explicitly needs a fixed shared library. Do not replace existing project-local directories without operator
approval.

### Orchestrator

`skill-agent-stack` is the normal single entry point for Agent Stack. Give the task to it; do not first decide which specialist to call. It selects the smallest useful roles and skills, separates evidence
from inference, highlights disagreement, and returns one synthesis. The installed specialist skills remain its internal library. Call one directly only when you explicitly want a narrow,
single-specialist task.

`orchestrator-follett` is the companion persona for runtimes that support persona discovery. Neither starts a background process, makes material decisions for you, or persists cross-project state.

### Other agents and `.agents`-compatible projects

For an agent that documents global discovery at `~/.agents/skills`, the default global install covers it. For an agent that documents project-local discovery from `.agents/skills`, link the canonical
skill directory directly when that project does not already own the directory:

```bash
mkdir -p <project>/.agents
ln -s /path/to/agent-stack/skills <project>/.agents/skills
```

`.agents` has no universal persona-discovery convention. Use `skill-agent-stack` everywhere; additionally link or reference `personas/orchestrator-follett.md` only when that runtime documents a persona
path. Project-local instructions remain authoritative.

## Contents

- `personas/`: 15 on-demand specialist personas, including `orchestrator-follett`.
- `skills/`: 37 current packages, including `skill-agent-stack`, classified in `manifest.yaml` as `project_agnostic` or `tool_specific`.
- `manifest.yaml`: source paths, install convention, and the classification inventory.
- `scripts/sync_auto_company.py`: conservative upstream comparison and update tool.
- `routing.toml`: machine-readable persona/skill routing catalogue and mandatory gates.
- `evals/routing-cases.toml`: 60-case routing regression corpus covering technical, JDM/import, atar/import, business, research, and adversarial tasks.
- `ROUTING_EVALS.md` / `scripts/evaluate_routing.py`: static and real-model behavioral routing evaluation.

## Upstream refresh

The upstream source is the official `MaxMiksa/Auto-Company` repository. The sync tool uses a disposable mirror under `skills-working-cache`, never an always-on daemon.

```bash
cd /path/to/agent-stack
just upstream-status
just upstream-dry-run
just upstream-fetch-dry-run
```

The default command fetches the latest configured upstream revision and prints a classification report. The state records both the last upstream hash and the canonical English hash for every file. A
source change to a translated file always becomes `translation_required`, even if that new source happens to be English; it is never treated as a byte-for-byte replacement.

For a translated update, the existing canonical English file is the translation memory. The generated `translation-brief.md` tells the reviewer to preserve unchanged wording and translate only the
source material that changed. Its report retains the previous upstream source and the new source under `skills-working-cache`, so the change can be inspected even when both are non-English. This is
more stable than regenerating a complete file with a model; the full rules are in `translation-policy.md`.

`safe_add` and `safe_replace` are English-only changes to unadapted files that can be applied automatically. `translation_required`, `manual_merge`, and `remove_review` are written as review proposals
instead.

`upstream-status` reads only `upstream-state.json`. `upstream-dry-run` compares an existing mirror without network access. `upstream-fetch-dry-run` fetches then compares. `upstream-apply apply`
fetches and applies only eligible changes.

To apply only the safe changes, use an explicit confirmation:

```bash
just upstream-apply apply
```

Every apply creates a timestamped report under `skills-working-cache/agent-stack/update-reports/`. The baseline is stored in `upstream-state.json`; use `just record-current
<reviewed-auto-company-checkout>` only after a deliberate import review. The source must be an original upstream checkout or the working-cache mirror, never an Auto Company checkout after it has been
symlinked to Agent Stack.

## Safety model

The sync tool is report-first. It does not import autonomy infrastructure, delete canonical material, overwrite local editorial changes, or apply non-English upstream content. Review proposals before
manually translating, merging, or accepting removals.

## Intelligent routing

`skill-agent-stack` remains the normal entry point, but routing is no longer based only on a short role matrix. Root `routing.toml` defines decision ownership, task intents, skill execution class, runtime
prerequisites, safety notes, and mandatory routing gates. Persona files define the judgement contract for each specialist; skills define repeatable procedures/tools.

Since 2026-09-01 the catalogue carries four cooperating tables. `[[capabilities]]` is the single taxonomy — 20 routing capabilities, declared on the skills and personas that actually provide them,
each at `primary` or `supporting` strength. `[[gates]]` names a `required_capability` and a `minimum_strength` rather than listing satisfying skills, so a gate is an obligation on the route that any
qualifying provider discharges; no gate summons a persona unconditionally. `[[precedence]]` ranks ownership where two personas both plausibly own a decision, naming the discriminating question and
both answers. `[[route_invariants]]` states what makes a finished route **invalid** rather than merely thin. `supporting` strength never discharges a gate — that single rule is what keeps analysis
distinct from independent challenge.

The Orchestrator should choose the narrowest sufficient route: direct skill for a narrow procedure, one persona plus skills for a single-domain decision, or a small sequenced team for genuinely
cross-domain work. `evals/routing-cases.toml` provides regression scenarios for expected/forbidden routing behaviour.

Validate the catalogue and persona contracts with:

```bash
just bootstrap
just preflight
```

`just preflight` runs the resolved-runtime report, the contract validator, the governance gate, the routing-eval corpus check, and the unit tests. The individual tasks are `just check`, `just
governance`, `just routing-eval-check`, `just test`, and `just runtimes`; `just --list` shows everything. Behavioural routing evaluation against a local model is `just routing-eval <command>` — see
[ROUTING_EVALS.md](ROUTING_EVALS.md).

See [RUNTIME.md](RUNTIME.md) for the isolated virtualenv policy and tool-skill runtime rules, and [SKILL_STANDARD.md](SKILL_STANDARD.md) for the local skill-quality contract.

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Architecture overview: [ARCHITECTURE.md](ARCHITECTURE.md)
- Script and task catalog: [scripts/README.md](scripts/README.md)
- Settled decisions, baselines and traps: [MEMORY.md](MEMORY.md)
- Project change history: [CHANGELOG.md](CHANGELOG.md)
- Working state and open items: [SCRATCHPAD.md](SCRATCHPAD.md)
- Parent repo guidance: [../../AGENTS.md](../../AGENTS.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
