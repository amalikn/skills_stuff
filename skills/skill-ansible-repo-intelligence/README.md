# skill-ansible-repo-intelligence

> Alias: **`skill-ari`**

## Governance pointers

- Agent contract: [SKILL.md](SKILL.md) · Local rules: [AGENTS.md](AGENTS.md) · [CLAUDE.md](CLAUDE.md)
- AI navigation: [AI_NAVIGATION.md](AI_NAVIGATION.md) · Machine routing: [context-map.yaml](context-map.yaml)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md) · Conventions: [CONVENTIONS.md](CONVENTIONS.md)
- Status: [ROADMAP.md](ROADMAP.md) · [SCRATCHPAD.md](SCRATCHPAD.md) · History: [CHANGELOG.md](CHANGELOG.md)
- Tasks: `just --list` ([justfile](justfile)) · Reports: [docs/reports/](docs/reports/)
- Parent area: [../../AGENTS.md](../../AGENTS.md) · Canonical governance: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)

Deterministic, offline, FOSS static intelligence for Ansible repositories. Turns
a large Ansible repo into a lean, bounded, source-traceable graph so AI agents
retrieve relevant logic without re-reading the whole repository.

> High-coverage **static** understanding of repository structure and statically
> resolvable relationships, with explicit identification of dynamic and
> unresolved behaviour. **Not** complete runtime understanding.

## Install

```bash
# runtime is pinned to Python 3.14 via .mise.toml; venv lives in the skills
# working-cache (outside this source tree)
python -m pip install -e .
```

Dependencies (all FOSS, offline): `ruamel.yaml`, `jsonschema`, `jinja2`
(parse-only), `networkx`.

## Quick start

```bash
ansible-repo-intelligence scan --repo /path/to/ansible-repo --output .ai-context --offline
ansible-repo-intelligence validate --context .ai-context
```

Read `.ai-context/ANSIBLE_REPO_MAP.md` first. Do **not** load `graph.yaml` in
full unless auditing the whole repo.

## Lean output (exactly these)

| File | Purpose |
|---|---|
| `manifest.yaml` | freshness, versions, fingerprints, output hashes, context integration |
| `ANSIBLE_REPO_MAP.md` | compact first-read orientation (≤1000 lines) |
| `graph.yaml` | the single canonical machine-readable graph |
| `diagnostics.yaml` | unresolved / dynamic / duplicate / security findings |
| `cache/scan-state.yaml` | incremental scanner state (do not read unless troubleshooting) |

No per-role indexes, no diagrams, no duplicate persistent indexes — a hard
design requirement enforced by the validator.

## What it extracts

- Playbooks, plays, roles, tasks (with `notify`/`register`/`set_fact`/`when`/
  `loop`/tags/`delegate_to`), blocks/rescue/always
- Includes/imports (static vs **dynamic** templated targets), role dependencies
- Handlers with `name`/`listen`; notify→handler resolution, duplicates,
  unresolved notifications
- Variables by precedence class; potential precedence conflicts (ARI006)
- Templates via **parse-only** Jinja AST (never rendered); consumed variables
- Inventory scoped by **flavor + environment**, discovered generically (works
  for no-inventory, single-file, standard `production/staging`, and multi-flavor
  layouts alike)
- Collections: FQCN usage tracked; **vendored third-party trees excluded** from
  first-class indexing by default
- Custom vars plugins: detected via static `ast`, **never executed**, modelled
  as dynamic variable sources

## Resolution & significance

Every node/edge carries `resolution: {status, confidence, reason}` where status
is `resolved | partially_resolved | unresolved | dynamic`. Significance
(`critical|high|normal|low`) is **configuration-driven** via
`config/significance_rules.yaml` (schema-validated), and each node records the
winning `significance_rule_id`.

## Security model

Never: executes repo scripts, renders Jinja, decrypts Vault, exposes secret
values, follows external symlinks (unless opted in), invokes lookups, or
contacts remote hosts. Secret-looking variable **names** are flagged; **values**
are never emitted. Inventory execution (`--run-inventory`) is strictly opt-in.

## Determinism

Stable IDs, sorted collections, normalized (LF/BOM-invariant) content hashes, no
timestamps inside content-derived hashes. Two scans of unchanged sources produce
byte-identical `graph.yaml`, `ANSIBLE_REPO_MAP.md`, and `diagnostics.yaml`.

## Relationship to other tooling

- **skill-smc** — ansible-wifi operational/domain knowledge.
- **mcp-smc** — LIVE `ansible-inventory` host/flavor blast-radius (this skill is
  static/offline; different purpose).
- **graphify-out / Repomix** — generic, non-Ansible-aware; not authoritative.

## Status / limitations

**Phases 1–3 implemented and verified** against a 94-role production repo:
scan/validate/clean, canonical graph, bounded map, schema validation, security,
determinism (Phase 1); bounded `query`/`impact` + incremental reparse (Phase 2);
token-efficiency `benchmark` harness (Phase 3). All CLI commands are implemented
(`scan`, `validate`, `clean`, `query`, `impact`, `explain`, `benchmark`).

**Verdict: role-level digest efficiency VALIDATED (Gate A); general claim still
gated on Experiment 2.**
The harness's deterministic proxy (96.7% fewer files, 100% recall) is measured
against *naive keyword search*, not a real agent. The external blind-graded run
(real LLM agents, 2026-07-03 16:40) initially did **not** meet the targets
versus a capable agent: 19% fewer files (target ≥60%), +8% tokens (target
−40%), correctness 21/22 vs 22/22, +1 unsupported claim. Cause: a strong agent
already navigates directly to the right role, so the naive-proxy's
file-reduction edge shrinks and CLI overhead added tokens.

That was **remediated** (17:10) with a managed-resource fact digest
(`--view actions`): Experiment 1 rerun showed **0 source files opened, 78.8k
tokens (below the 79.1k direct baseline)**, and fixed the one wrong answer
(Asterisk install mechanism). The sole remaining miss (q21, a variable-origin
question) was a routing failure, fixed with a deterministic router
(`ansible-repo-intelligence route`) and confirmed via an isolated 3-agent
retest (17:36): **22/22 correct both runs, 0 unsupported claims, 0 source
files/map/graph reads on the digest workflow — Gate A PASS.**

Full analysis:
[`docs/reports/benchmark-external-grading-20260703_1640.md`](docs/reports/benchmark-external-grading-20260703_1640.md),
[`docs/reports/ari-efficiency-experiment1-20260703_1710.md`](docs/reports/ari-efficiency-experiment1-20260703_1710.md),
[`docs/reports/ari-experiment1-routing-retest-20260703_1736.md`](docs/reports/ari-experiment1-routing-retest-20260703_1736.md).

Position the tool as deterministic **navigation & relationship intelligence**
(handler chains, `impact`, `explain`, source-traceable graph) with a confirmed
role-digest efficiency win — a *general* token-savings claim still requires
Experiment 2 (relationship-heavy questions) before Regular Skills promotion.
