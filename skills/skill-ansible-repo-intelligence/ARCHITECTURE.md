# Architecture — skill-ansible-repo-intelligence (skill-ari)

## Overview

A deterministic, offline CLI that scans an Ansible repository once and emits a
lean, source-traceable graph plus a bounded human-readable map. The pipeline is
strictly layered: **discover → parse/analyze → assemble graph → render → validate**.
Nothing executes repository code; Jinja is parsed (never rendered), Vault is
never decrypted, no network is touched. Query/impact operate on the *generated*
`graph.yaml`, not on a re-scan.

## Contents

- [Data flow](#data-flow)
- [Module ownership](#module-ownership)
- [Output contract](#output-contract)
- [Key decisions](#key-decisions)

## Data flow

```
scan:  app_config + ansible_config
         → discovery (walk, classify, vendored-exclude, symlink-guard)
         → parser / handlers / variables / vars_plugins / templates / inventory*
         → resolver (notify→handler, include→target, role deps, FQCN)
         → graph.build_graph (assembly orchestrator; significance applied)
         → renderer (graph.yaml, manifest.yaml, diagnostics.yaml, MAP.md, scan-state)
         → validator (schemas + structural gates)

query/impact/explain:  graph.yaml → traversal.GraphStore → bounded_bfs (shared) → shaped output
route:         question text → routing.classify_question (pure, no graph/I-O) → advisory recommendation only
benchmark:     graph.yaml + questions.yaml → deterministic metrics (never self-grades)
```

## Module ownership

Fixed boundaries — do not merge or duplicate logic across these:

| Module | Owns |
|---|---|
| `app_config.py` | tool CLI/config-file parsing, defaults, bounds |
| `ansible_config.py` | the *repository's* `ansible.cfg` (roles_path, collections_path, jinja2_extensions) |
| `hashing.py` | CRLF/BOM-invariant sha256 (cross-clone determinism) |
| `yaml_loader.py` | safe round-trip (`typ="rt"`) load with line numbers; `!vault`/`!unsafe` opaque |
| `discovery.py` | single repo walk, file classification, vendored/venv/backup exclusion, symlink-escape |
| `collections.py` | collection origin classification (repo/vendored/unknown), FQCN prefixes |
| `parser.py` | playbooks/plays/tasks, blocks/rescue/always, include/import + dynamic detection |
| `handlers.py` | handler records (name/listen) + index for resolution |
| `variables.py` | var definitions by precedence class + conflict algorithm (ARI006) |
| `vars_plugins.py` | custom vars-plugin `ast` analysis (never executes) → dynamic sources |
| `templates.py` | parse-only Jinja AST variable extraction (tolerant filter map) |
| `inventory.py` | static offline INI/YAML inventory parse, flavor+environment scoped |
| `inventory_flavors.py` | generic flavor/environment discovery + namespacing (0/1/N scopes) |
| `resolver.py` | edge construction with resolution states (shared by graph) |
| `significance.py` | config-driven significance classification (`significance_rules.yaml`) |
| `actions.py` | managed-resource extraction from task module args → compact `Action{operation, resource, verification}`; ~20 module extractors + generic fallback |
| `context_integration.py` | read existing `context-map.yaml` authority; register outputs as derived |
| `graph.py` | assembly orchestrator: nodes/edges/topics/statistics + deterministic serialization |
| `diagnostics.py` | diagnostic codes (ARI001–ARI025) + severity collector |
| `renderer.py` | deterministic emit of the 5 output files + bounded map |
| `validator.py` | schema conformance + structural gates (no redundant indexes, budget, refs) |
| `traversal.py` | **shared** bounded BFS — query, impact and explain use this; no dup reachability logic |
| `query.py` | bounded query + impact analysis + `explain` (single-node view) + `--view` fact digests; all via `traversal` |
| `routing.py` | deterministic, offline, advisory question router (`classify_question`) — recommends a command, never executes one; keeps variable-origin/precedence/vars-plugin questions off the role digest (q21 fix) |
| `benchmark.py` | deterministic efficiency metrics; hands correctness to external runbook |
| `grapher.py` | OPT-IN `ansible-playbook-grapher` adapter; supplementary only, structurally validated, scan never depends on it |
| `cli.py` | argparse wiring for scan/validate/clean/query/impact/explain/benchmark/route |

Custom plugins & modules — `callback_plugin`, `filter_plugin`, `lookup_plugin`,
`action_plugin`, `module`, `module_utils` — are emitted as first-class nodes with
`resolution: dynamic` (runtime behaviour). Callback plugins enabled in
`ansible.cfg` are flagged. Only `vars_plugin` output is modelled at the variable
level; other plugins are catalogued, not statically executed or resolved.

## Output contract

Exactly five persistent artifacts under `.ai-context/` — enforced by the
validator (no per-role indexes, no diagrams, no duplicate persistent indexes):
`manifest.yaml`, `ANSIBLE_REPO_MAP.md`, `graph.yaml`, `diagnostics.yaml`,
`cache/scan-state.yaml`. Every node/edge carries `resolution{status,confidence,
reason}` + source provenance; nodes also carry `significance` + `significance_rule_id`.

## Key decisions

- **Round-trip YAML, not safe** — `typ="rt"` is required for line numbers (`.lc`);
  still safe (no arbitrary object construction). See `yaml_loader.py`.
- **Tolerant Jinja filters** — `meta.find_undeclared_variables` codegen rejects
  unknown Ansible filters; `_TolerantMap` returns identity for missing filters so
  parsing succeeds. Identity is never invoked (parse-only). See `templates.py`.
- **Generic inventory scoping** — flavors/environments are discovered, never
  hardcoded; a repo may have 0, 1, or N scopes.
- **Shared traversal** — query and impact call one `bounded_bfs`; impact matches
  roots by exact-path/dir-prefix only (never bare basename).
- **Incremental = fingerprint short-circuit + safe full rebuild** — cross-file
  resolution needs the whole graph, so any change triggers a full deterministic rebuild.
- **Benchmark never self-grades** — deterministic half only; correctness/claims
  go to `tests/benchmark/RUNBOOK.md`. Verdict PARTIAL by construction.
