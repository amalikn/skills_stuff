@/Volumes/Data/_ai/_skills/skills_stuff/AGENTS.md

Title: skill-ansible-repo-intelligence Agent Policy
Category: agent-governance-guide
Status: current
Scope: Repo-local agent behaviour for this skill's authoring surface
Last reviewed: 2026-07-03

# AGENTS.md

Deterministic static Ansible repository intelligence skill. Phases 1–3
implemented, verified, and remediated (q21 routing fix + Gate A retest PASS,
2026-07-03); see `ROADMAP.md` for the Experiment 2 gate before promotion.

## Invariants (do not violate)

- **Generated context is derivative.** Source files are authoritative; never
  treat `.ai-context/*` as a substitute for reading source.
- **No runtime execution during indexing.** Never execute playbooks, render
  Jinja (`.parse()` only), decrypt Vault, run lookups, or contact remote hosts.
- **No secret exposure.** Redact secret-looking variable VALUES; only names and
  a `sensitive_name` flag may appear. Never emit Vault ciphertext.
- **Bounded retrieval is mandatory.** The full `graph.yaml` must not be loaded
  by default in agent instructions; queries default to 25 nodes / 1 hop.
- **Runtime completeness must not be claimed.** Label dynamic/unresolved; do not
  guess concrete targets.
- **Existing `.archcore` and context-map authority outrank generated context.**
  Register outputs as derived; never create a competing first-read sequence.
- **Inventory results stay flavor+environment scoped.** Never merge across
  flavors without namespacing.
- **Custom vars plugins are never executed** — modelled as dynamic sources.
- **`mcp-smc` (live) and this CLI (static) have distinct purposes.**
- **Validation after generation is mandatory**; a scan must not report success
  if mandatory outputs are malformed.

## Runtime

- Python 3.14 pinned via `.mise.toml`; venv lives OUTSIDE this tree at
  `/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-repo-intelligence/venv/`.
- Config rule tables in `config/` are schema-validated before any scan.

## Module ownership (fixed)

See `ARCHITECTURE.md`. Key separations: `app_config.py` (tool config) vs
`ansible_config.py` (repo ansible.cfg); `variables.py` vs `vars_plugins.py`;
`inventory.py` vs `inventory_flavors.py`; query/impact share `traversal.py`
(Phase 2). `routing.py` is advisory-only (never executes a query) — do not
duplicate its classification logic elsewhere. Do not duplicate traversal logic.

<!-- BEGIN skill-ai-it:navigation -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [SKILL.md](SKILL.md) (agent contract), [AI_NAVIGATION.md](AI_NAVIGATION.md)
   (router), [ARCHITECTURE.md](ARCHITECTURE.md) (module map), and
   [context-map.yaml](context-map.yaml) (machine routing).
2. Check [SCRATCHPAD.md](SCRATCHPAD.md) for current state / open items (`KEEP`).
3. Read recent [CHANGELOG.md](CHANGELOG.md) entries and any `.archcore/` documents.
4. Before running scripts, prefer `just --list` then `just <task>`. Runtime venv
   is **external** (`skills-working-cache/.../venv`); never create a repo-local `.venv`.
5. If sources conflict, stop and report — do not silently merge.
6. After durable changes, update the governance file the change touches and append
   `CHANGELOG.md` (see the update table in `AI_NAVIGATION.md`).

<!-- END skill-ai-it:navigation -->

## Canonical governance linkage

- Parent area guidance: [../../AGENTS.md](../../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
