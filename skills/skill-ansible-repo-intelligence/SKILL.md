---
name: skill-ansible-repo-intelligence
aliases: [skill-ari]
description: >-
  (alias: skill-ari) Deterministic static intelligence for Ansible repositories. Generates a lean,
  bounded, source-traceable graph (.ai-context) so agents can answer questions
  like "which playbooks reach this role", "what handlers fire when this task
  runs", or "which variables does this template consume" WITHOUT reading the
  whole repo. Use when working on any Ansible repo (roles, playbooks, inventory,
  templates, handlers, variables) and you need bounded retrieval instead of
  full-repo traversal. Complements skill-smc (ansible-wifi domain) and mcp-smc
  (live host/flavor blast-radius); this skill is static/offline.
---

# Ansible Repository Intelligence

Static, offline, FOSS. Never executes playbooks, renders Jinja, decrypts Vault,
or contacts remote hosts. Produces **high-coverage static understanding** with
explicit `resolved | partially_resolved | unresolved | dynamic` labels — it does
not claim complete runtime understanding.

## When to use this tool (honest routing)

An external blind benchmark showed the index does **not** beat ordinary
navigation for a capable agent on simple "how is X configured" questions where
the role name is obvious — a direct `Read roles/X/tasks/main.yml` is fine there.
Reach for the tool when it genuinely helps:

- **Fact digest** — one call returns a role's whole managed-resource story
  (packages, template `src→dest`, services, commands, notify) across *all* its
  task files, so you don't hunt through a multi-file role.
- **Relationship questions** — which tasks notify a handler, blast-radius
  `impact` of a file, where a variable can originate, cross-flavor scope,
  dynamic/unresolved includes. Ordinary grep answers these poorly.

Do **not** read `ANSIBLE_REPO_MAP.md` for a targeted question — it's a fixed
~26 KB tax. Query directly.

## Agent workflow

1. **Freshness**: if `.ai-context/manifest.yaml` is missing/stale, scan:
   ```bash
   ansible-repo-intelligence scan --repo . --output .ai-context --offline
   ```
2. **For "how is role X configured" / package / template / service questions** —
   one digest call, then answer from its facts:
   ```bash
   ansible-repo-intelligence query role smc_dns --view actions --context .ai-context
   ```
   The digest lists each action `[operation]` with resource facts + source
   `path:line`. **Open source only for actions flagged `⚠verify`** (free-form
   commands, Jinja-derived destinations, critical/destructive ops, custom
   modules) or when the digest is insufficient.
3. **For relationship / origin questions** — bounded `query` / `explain` / `impact`:
   ```bash
   ansible-repo-intelligence explain "Restart unbound service" --context .ai-context
   ansible-repo-intelligence impact --path roles/smc_dns --context .ai-context
   ```
   **Where does variable X come from / topology vars / dynamic vars?** →
   `query vars_plugin` or `query variable X` — NOT the role digest. A role digest
   shows what a role *does*, not where inventory/plugin variables *originate*.
   (This is the one question class the digest must not answer alone.)
4. **NEVER load `graph.yaml` in full** unless the user asks for a repo-wide audit.
5. **Verify flagged/critical claims against source.** The digest is deterministic
   parsed facts, not an LLM summary — but conditionals, Jinja values, and custom
   plugins still need the source.
6. **Record uncertainty**: dynamic includes, templated names, vars-plugin output,
   extra vars, dynamic inventory are labelled `dynamic`/`unresolved` — never guess.
7. Respect query bounds (25 nodes / 1 hop; impact 50 / 3). Refresh after changes.

## Variable-origin routing (mandatory)

The one class the role action digest must **never** answer. A role digest shows
what a role *does*, not where an inventory/plugin variable *originates*.

```text
Questions about where a variable originates, which source supplies it, its
precedence, or whether a vars plugin injects it must route to:

1. query variable <name>
2. query vars_plugin <name>          (when plugin supply is possible)
3. source verification when results are dynamic, conflicting, or unresolved

Do NOT use `query role <role> --view actions` as the authoritative source for
variable origin.
```

Covers questions such as: *Where does `topology_site_id` come from? Which file
defines `dns_servers`? Does `topology_vars.py` inject this? Which value wins? What
are the possible origins? Is it set by inventory, role defaults, set_fact, or a
vars plugin?*

Unsure how to route any question? Ask the deterministic router (advisory only —
it never executes a query):

```bash
ansible-repo-intelligence route "Where does topology_dns_servers come from?"
# → variable_origin | ROUTE-VAR-ORIGIN
#   query variable topology_dns_servers / query vars_plugin topology_dns_servers
```

`route` classifies into `variable_origin | variable_precedence | vars_plugin_origin
| handler_chain | impact | reachability | inventory_scope | dynamic_reference |
direct_config | live_operational | repo_wide | ambiguous`, each with a rule id +
reason. It recommends; the agent runs the command.

## Digest views

`--view actions` (managed-resource digest) · `summary` (packages/services/
templates/handlers) · `relationships` (edges) · `sources` (paths only).

## What it models

playbooks → plays → roles → tasks → handlers (notify/listen) → templates →
variables (with precedence classes) → inventory (flavor+environment scoped) →
collections (FQCN usage; vendored trees excluded) → custom vars plugins (dynamic).

## Boundaries (never claim otherwise)

Dynamic inventory, extra/survey vars, runtime facts, templated include/role
names, lookup results, Vault values, custom plugin execution, actual
idempotency, and complete runtime variable precedence are **out of static
scope**. The tool labels them; it does not resolve them.

## Relationship to other tools

- **skill-smc** — ansible-wifi operational/domain knowledge (services, comms,
  troubleshooting). Use for *what things do operationally*.
- **mcp-smc** — LIVE `ansible-inventory` queries and flavor/host blast-radius.
  Use for *current host state*. This skill is static/offline instead.
- **graphify-out / Repomix** — generic, non-Ansible-aware. This skill adds
  Ansible-domain semantics. Do not treat `graphify-out/graph.json` as source.

## Output (lean, exactly these)

`.ai-context/{manifest.yaml, ANSIBLE_REPO_MAP.md, graph.yaml, diagnostics.yaml,
cache/scan-state.yaml}`. No per-role/per-index files, no diagrams. Generated
artifacts are **derived and non-authoritative**; existing `.archcore`/context-map
authority outranks them.

## Bounded query & impact (Phase 2)

```bash
# bounded query (default 25 nodes / 1 hop)
ansible-repo-intelligence query role smc_dns --context .ai-context
ansible-repo-intelligence query handler "restart unbound" --context .ai-context
ansible-repo-intelligence query tag networking --context .ai-context

# static impact of a file or role dir (default 50 nodes / 3 hops)
ansible-repo-intelligence impact --path roles/smc_dns/tasks/main.yml --context .ai-context

# explain a single node: source, resolution+reason, significance, 1-hop neighbours
ansible-repo-intelligence explain "Restart unbound service" --context .ai-context
ansible-repo-intelligence explain role:smc_dns --context .ai-context   # exact id

# incremental refresh (no-op if nothing changed; safe full rebuild otherwise)
ansible-repo-intelligence scan --repo . --output .ai-context --offline --incremental
```

Impact reports tasks, notified handlers, reachable roles/playbooks, consumed
variables — always with a static-only caveat. It never claims runtime certainty.

## Status

Phases 1–3 implemented and verified against a 94-role repo: discovery, parsing,
canonical graph, bounded map, schema validation, determinism, security, bounded
`query`/`impact`/`explain` (shared traversal), incremental scan, and the
token-efficiency `benchmark` harness. All CLI commands are implemented — no
stubs. **Benchmark honesty:** the harness's deterministic proxy (96.7% fewer
files, 100% recall) is measured against *naive keyword search*. The external
blind-graded run (real LLM agents, `docs/reports/benchmark-external-grading-*`)
did **not** meet the efficiency targets vs a capable agent (19% fewer files,
+8% tokens, correctness flat). Treat this tool as deterministic **navigation &
relationship intelligence** (handler chains, `impact`, `explain`,
source-traceable graph), not as a token-savings guarantee. See `docs/reports/`.
