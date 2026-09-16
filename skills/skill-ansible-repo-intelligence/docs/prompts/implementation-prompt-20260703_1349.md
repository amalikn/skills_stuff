# Codex Implementation Prompt: Ansible Repository Intelligence Skill

You are implementing a production-quality, fully local and FOSS skill named:

`skill-ansible-repo-intelligence`

## Objective

Build a deterministic Ansible repository analysis tool that scans a potentially large Ansible repository containing:

- multiple playbooks
- approximately 94 roles in the current target repository, with support for larger repositories
- nested task files
- handlers
- templates
- files
- defaults
- role variables
- inventory variables
- `group_vars`
- `host_vars`
- role dependencies
- repository-authored collections and collection usage metadata
- vendored third-party collections, classified separately and excluded from first-class graph traversal by default
- custom modules
- custom vars plugins
- vars-plugin configuration from `ansible.cfg` and plugins

The tool must generate compact, structured repository intelligence that allows Codex, Claude Code and local LLM agents to understand and retrieve relevant Ansible logic without repeatedly reading the entire repository.

The generated context must remain traceable to original source files and must never replace source-code verification.

The implementation must optimize for:

1. minimal generated noise
2. bounded retrieval
3. low token consumption
4. deterministic outputs
5. explicit uncertainty
6. source traceability
7. high-coverage static understanding

The implementation must not claim complete runtime understanding of the repository.

## Core design

Implement this primarily as:

1. A deterministic local CLI
2. An agent skill describing how and when to invoke it
3. YAML-based generated artifacts
4. JSON Schema Draft 2020-12 schemas written in YAML
5. Optional adapters for external tools such as `ansible-playbook-grapher`

Do not implement an MCP server in this phase.

The CLI and generated files must work independently of Codex, Claude Code or any particular LLM.

## Phased implementation contract

Implement this work in three mandatory phases. Do not begin a later phase until the current phase passes all of its gates.

### Phase 1 — Discovery, parsing, canonical graph and repository map

Implement only:

- repository discovery
- `ansible.cfg` parsing and path-resolution configuration
- vendored collection detection and exclusion
- custom vars-plugin detection and dynamic-source modelling
- multi-flavor inventory discovery
- integration with the repository's existing AI-context authority order
- safe YAML parsing
- parse-only Jinja expression analysis
- static playbook, role, task, handler, variable, template and inventory-source extraction
- stable node and edge identifiers
- canonical `graph.yaml`
- `manifest.yaml`
- `diagnostics.yaml`
- bounded `ANSIBLE_REPO_MAP.md`
- schema validation
- security controls
- deterministic hashing and ordering

Phase 1 gates:

1. All Phase 1 tests pass.
2. Generated YAML validates.
3. Repeated scans are semantically identical.
4. Source provenance exists for all source-derived nodes.
5. Dynamic references are labelled, not guessed.
6. The repository map remains within budget.
7. No redundant persistent indexes are generated.
8. Vendored collection source is excluded from first-class graph nodes.
9. Custom vars-plugin outputs are represented as dynamic.
10. `ansible.cfg` path and Jinja-extension settings are honoured.
11. Existing `.ai-context` authority and bootstrap order are preserved.

### Phase 2 — Query, impact and incremental scanning

Implement only after Phase 1 passes:

- bounded query engine
- bounded impact traversal
- incremental scan state
- dependency-aware reparse logic
- concise output rendering
- traversal consistency tests

Phase 2 gates:

1. Query defaults enforce 25 nodes and one hop.
2. Impact defaults are bounded.
3. Query and impact use the same traversal implementation.
4. Incremental and full scans produce equivalent semantic output.
5. All Phase 2 tests pass.

### Phase 3 — Benchmark, documentation and implementation report

Implement only after Phase 2 passes:

- reproducible benchmark harness
- benchmark question set
- independent answer grading workflow
- README, SKILL, AGENTS and architecture documentation
- implementation report
- final READY/PARTIAL/NOT READY verdict

Phase 3 gates:

1. Benchmark methodology is reproducible.
2. Correctness grading is not self-scored by the same agent session.
3. Token and file-open measurements are captured from actual runs.
4. Governance files are bootstrapped through `skill-ai-it`.
5. Final report includes exact evidence for every readiness claim.

If the current environment cannot execute independent baseline, indexed and blind-grading sessions, do not self-grade. Complete the benchmark harness, fixtures, gold answers and runbook, then report `PARTIAL` with the exact missing external execution evidence.

Stop after any phase whose mandatory gate fails. Do not stub later phases merely to satisfy the final file tree.

A phase is a delivery boundary, not a single-session expectation. Phase 1 may require multiple Codex sessions and intermediate commits. Use each phase gate as the natural checkpoint and commit boundary, and preserve resumable state between sessions.

## Required technology constraints

Use only FOSS dependencies.

Preferred implementation:

- Python 3.14+
- `ruamel.yaml` for safe YAML loading and line-aware parsing
- `jinja2` for parse-only AST inspection of Jinja expressions and templates; never render templates or execute lookups
- `jsonschema` for schema validation
- `networkx` only if graph algorithms materially simplify implementation
- standard-library modules wherever practical
- Ansible CLI tools where available
- optional `ansible-playbook-grapher` integration

Do not require:

- a paid API
- cloud services
- hosted embeddings
- a vector database
- an LLM during index generation

The deterministic indexer must function without network access.

## Required package structure

Create:

```text
skill-ansible-repo-intelligence/
├── SKILL.md
├── README.md
├── AGENTS.md
├── AI_NAVIGATION.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── context-map.yaml
├── config/
│   ├── significance_rules.yaml
│   └── variable_precedence_rules.yaml
├── .mise.toml
├── pyproject.toml
├── src/
│   └── ansible_repo_intelligence/
│       ├── __init__.py
│       ├── cli.py
│       ├── app_config.py
│       ├── discovery.py
│       ├── ansible_config.py
│       ├── collections.py
│       ├── vars_plugins.py
│       ├── inventory_flavors.py
│       ├── context_integration.py
│       ├── yaml_loader.py
│       ├── parser.py
│       ├── resolver.py
│       ├── graph.py
│       ├── traversal.py
│       ├── variables.py
│       ├── handlers.py
│       ├── inventory.py
│       ├── templates.py
│       ├── renderer.py
│       ├── validator.py
│       ├── diagnostics.py
│       ├── query.py
│       ├── benchmark.py
│       └── models.py
├── schemas/
│   ├── manifest.schema.yaml
│   ├── graph.schema.yaml
│   ├── diagnostics.schema.yaml
│   ├── significance_rules.schema.yaml
│   └── variable_precedence_rules.schema.yaml
├── templates/
│   └── ANSIBLE_REPO_MAP.md.j2
├── scripts/
│   ├── ansible-repo-intelligence
│   └── validate-generated-context
├── tests/
│   ├── fixtures/
│   │   ├── minimal_repo/
│   │   ├── multi_role_repo/
│   │   ├── dynamic_include_repo/
│   │   ├── handler_repo/
│   │   └── variable_precedence_repo/
│   ├── unit/
│   ├── integration/
│   └── benchmark/
└── examples/
    └── .ai-context/
```

Module ownership must be fixed before implementation:

- `app_config.py`: tool CLI/config-file parsing and defaults
- `ansible_config.py`: parsing effective repository `ansible.cfg` values
- `variables.py`: repository variable definitions, references and precedence analysis
- `vars_plugins.py`: custom vars-plugin discovery and dynamic-source modelling only
- `inventory.py`: inventory parsing and graph extraction
- `inventory_flavors.py`: flavor discovery, namespacing and orchestration only
- `graph.py`: canonical node/edge model and serialization
- `traversal.py`: shared bounded traversal for query and impact
- `context_integration.py`: existing `context-map.yaml` authority integration only

Query and impact must not duplicate traversal logic.

Governance files must not be created manually as an ad hoc first step.

Before creating or updating `README.md`, `SKILL.md`, `AGENTS.md`, `AI_NAVIGATION.md`, `ARCHITECTURE.md`, `CHANGELOG.md` or `context-map.yaml`:

1. Run the existing `skill-ai-it` bootstrap workflow for this skill directory.
2. Preserve the generated governance structure.
3. Layer only skill-specific content into the bootstrapped files.
4. Register this skill in the `Skill Authoring Projects` table in the parent `skills_stuff/AGENTS.md`.

Python runtime policy:

- pin Python 3.14 in `.mise.toml`
- place the virtual environment under `skills-working-cache/skill-ansible-repo-intelligence/venv/`
- do not create a repository-local `.venv`
- document the canonical runtime path

## CLI contract

Implement this command:

```bash
ansible-repo-intelligence scan \
  --repo /path/to/ansible-repo \
  --output /path/to/ansible-repo/.ai-context
```

Support:

```bash
ansible-repo-intelligence scan
ansible-repo-intelligence validate
ansible-repo-intelligence query
ansible-repo-intelligence impact
ansible-repo-intelligence explain
ansible-repo-intelligence benchmark
ansible-repo-intelligence clean
```

### Required scan options

```text
--repo PATH
--output PATH
--config PATH
--inventory PATH
--inventory-flavor NAME=PATH
--inventory-root PATH
--all-inventory-flavors
--exclude-inventory-glob PATTERN
--playbook PATH
--include PATTERN
--exclude PATTERN
--follow-symlinks
--max-file-bytes INTEGER
--strict
--fail-on-warning
--offline
--incremental
--force
--format yaml
--log-level LEVEL
```

YAML is the authoritative generated format.

JSON output may be supported as an optional serialization, but it must not be required.

The current target repository contains multiple inventory flavors. The CLI must support either:

- a single inventory path
- repeated named `--inventory-flavor NAME=PATH` arguments
- automatic flavor discovery below `--inventory-root`
- `--all-inventory-flavors` to scan all discovered flavors

Inventory results must remain flavor-scoped. Do not merge host or variable state across flavors without preserving provenance.

## Generated output structure

Generate a lean, non-duplicative context set:

```text
.ai-context/
├── manifest.yaml
├── ANSIBLE_REPO_MAP.md
├── graph.yaml
├── diagnostics.yaml
└── cache/
    └── scan-state.yaml
```

Responsibilities:

- `manifest.yaml`: freshness, tool/schema versions, configuration fingerprint, source fingerprint, output hashes, parser capabilities and external-tool provenance.
- `ANSIBLE_REPO_MAP.md`: compact first-read orientation for an AI agent.
- `graph.yaml`: the single canonical machine-readable source for nodes, edges, provenance, retrieval topics, variables, handlers, templates, files, tags, inventory relationships and impact paths.
- `diagnostics.yaml`: unresolved, dynamic, malformed, unsupported and security-related findings.
- `cache/scan-state.yaml`: incremental scanner state. Agents must not read this unless troubleshooting scanner freshness.

The target repository already has an existing `.ai-context/` directory governed by `context-map.yaml` and linked to a companion local-knowledge repository.

Before writing any output:

1. Read the repository's existing `context-map.yaml`.
2. Detect its `authority_order`, `required_first_read`, preferred bootstrap files and generated-content rules.
3. Register `ANSIBLE_REPO_MAP.md`, `manifest.yaml`, `graph.yaml` and `diagnostics.yaml` as derived, non-authoritative artifacts.
4. Preserve existing higher-authority entries such as `.archcore` ADRs, governance packs and repository navigation files.
5. Do not create a competing first-read sequence.
6. If policy does not allow writing into the existing `.ai-context/`, fail clearly or use an explicitly configured alternative output path.

The scanner must not overwrite or reorder existing context authority without an explicit user-approved migration.

Do not generate separate persistent:

- `repository-index.yaml`
- `execution-graph.yaml`
- `variable-index.yaml`
- `handler-index.yaml`
- `inventory-index.yaml`
- `template-index.yaml`
- `file-index.yaml`
- `tag-index.yaml`
- `unresolved-references.yaml`
- per-role YAML summaries
- per-role Markdown summaries
- Mermaid diagrams

Those views must be derived on demand from `graph.yaml` through CLI queries.

This is a hard design requirement intended to avoid:

- duplicated information
- generated-file churn
- repository noise
- conflicting indexes
- excessive model context
- unnecessary token consumption

## Required repository discovery

Discover and classify:

- playbooks
- roles
- task files
- handler files
- role defaults
- role vars
- role metadata
- templates
- static files
- inventory files
- `group_vars`
- `host_vars`
- repository-authored collections and collection usage metadata
- vendored third-party collections, classified separately and excluded from first-class graph traversal by default
- custom modules
- custom vars plugins
- vars-plugin configuration from `ansible.cfg`
- filter plugins
- lookup plugins
- callback plugins
- action plugins
- module utilities
- Ansible configuration files
- effective `roles_path`
- effective collection paths such as `collections_path` or `COLLECTIONS_PATHS`
- configured vars-plugin paths
- configured Jinja extensions
- configured callback plugins and callback whitelist/enabled settings
- requirements files
- vault-encrypted files without decrypting them
- supporting shell, Python and configuration files referenced from tasks

Respect:

- `.gitignore` where practical
- configured exclusions
- `.ai-context/`
- `.git/`
- virtual environments
- caches
- generated files
- secrets
- vault data
- explicit inventory backup/archive exclusions such as `inventories/**/*.zip`
- repository-configured vendor paths
- generated graph directories such as `graphify-out/`

Never write generated context into role or playbook source directories.

## Vendored collections policy

The current target repository contains vendored third-party collections under paths such as:

```text
collections/ansible_collections/community/general
collections/ansible_collections/community/grafana
```

These trees may contain more than one thousand YAML files and must not be indexed as repository-authored first-class nodes by default.

Required behaviour:

1. Detect collection roots from `ansible.cfg` and standard collection layouts.
2. Classify collection content as `repo_authored`, `vendored_third_party`, or `unknown_origin`.
3. For `vendored_third_party` collections:
   - do not walk plugin tests, examples, docs or internal task files as first-class graph nodes
   - index only collection metadata required for resolution
   - record FQCN usage from repository-authored playbooks, roles and plugins
   - preserve collection name, version where available, source path and provenance
   - allow explicit opt-in deep indexing through configuration
4. Repository-authored collections may be indexed normally.
5. Unknown-origin collections must be reported in diagnostics and treated conservatively.

The default graph must represent calls such as `community.general.*` without ingesting the entire vendored implementation tree.

## Ansible configuration semantics

`ansible.cfg` must be parsed and its relevant settings must affect analysis.

At minimum, honour:

- `roles_path`
- `collections_path` or `COLLECTIONS_PATHS`
- vars-plugin paths and enablement
- `jinja2_extensions`
- callback-plugin paths and enabled/whitelist settings
- inventory plugin settings where statically readable

Path resolution must use the effective configured values rather than assuming only `./roles` or default collection paths.

Jinja parsing must enable the same safe parse-time extensions declared in `jinja2_extensions`, including `jinja2.ext.do` and `jinja2.ext.loopcontrols`.

Enabling an extension for parsing must not permit rendering, lookup execution or arbitrary code execution.

## Required Ansible relationships

Extract and model:

### Playbook structure

- playbooks
- plays
- target host expressions
- `gather_facts`
- `become`
- `serial`
- `strategy`
- play-level variables
- `pre_tasks`
- `roles`
- `tasks`
- `post_tasks`
- handlers

### Reuse and inclusion

- `import_playbook`
- `include_tasks`
- `import_tasks`
- `include_role`
- `import_role`
- role declarations
- `meta/main.yml` dependencies

### Task behaviour

- module/action name
- task name
- source file and line where available
- tags
- `when`
- loops
- `loop_control`
- `with_*`
- `notify`
- `register`
- `set_fact`
- `delegate_to`
- `delegate_facts`
- `run_once`
- `become`
- `environment`
- retries
- delay
- until
- changed and failed conditions
- check-mode behaviour
- blocks
- rescue
- always

### Managed resources

- template source and destination
- copied file source and destination
- service names
- package names
- users
- groups
- cron jobs
- systemd units
- repositories
- mount points
- firewall rules
- commands and scripts
- URI/API targets
- database actions where statically identifiable

### Handlers

Resolve:

- task `notify`
- handler `name`
- handler `listen`
- handler source
- duplicate names
- unresolved notifications
- cross-role notification ambiguity
- flush points using `meta: flush_handlers`

### Variables

Extract:

- definitions
- defaults
- role vars
- play vars
- task vars
- block vars
- `vars_files`
- `include_vars`
- inventory vars
- `group_vars`
- `host_vars`
- `set_fact`
- registered variables
- environment lookups
- variables injected by custom vars plugins, represented as dynamic sources
- variable namespaces and likely prefixes inferred from vars-plugin source without executing the plugin
- variable references in YAML and Jinja expressions
- variable references inside templates
- likely required variables
- defaults
- potential precedence conflicts
- sensitive-looking variable names without exposing values

Do not claim to fully calculate runtime variable precedence where dynamic inventory or runtime inputs prevent it.

Represent uncertainty explicitly.

Custom vars plugins must never be executed by the static scanner.

Required behaviour:

1. Detect `vars_plugins/` directories and vars-plugin paths configured in `ansible.cfg`.
2. Parse plugin source only for safe metadata such as class names, documented variable prefixes and literal keys where statically evident.
3. Create dynamic variable-source nodes with:

```yaml
resolution:
  status: dynamic
  confidence: high
  reason: Custom vars plugin executes during inventory loading and is not statically resolvable
```

4. Link potentially supplied variables to the plugin source when a literal name or namespace can be identified.
5. Otherwise create an unresolved dynamic namespace marker rather than inventing concrete variables.
6. Flag downstream variable conclusions that depend on vars-plugin output.

### Inventory

The current target repository contains multiple inventory flavors, including:

```text
apn
cw
nbn_accelerate
nbn_wh
rcp
rct
wh
```

Each flavor may contain independent production, staging, `group_vars`, `host_vars` and topology data.

Required behaviour:

- discover flavor boundaries deterministically
- preserve flavor name on every inventory-derived node and edge
- support per-flavor scan and all-flavor scan modes
- never collapse same-named groups or hosts across flavors without namespacing
- exclude tracked archive/backup files such as `inventories/**/*.zip` by default
- allow repository-specific exclude globs

When inventory execution is explicitly enabled:

- call `ansible-inventory --list` separately per flavor
- call `ansible-inventory --graph` separately per flavor
- capture groups and parent-child relationships
- capture host membership
- capture variable names
- redact secret-looking values
- distinguish parsed inventory output from static source inspection
- detect vars-plugin-dependent values and mark their provenance as runtime/dynamic

The tool must still work without executing inventory.

Inventory command execution must be opt-in because inventory and vars plugins may execute code or access external systems.

## Static versus dynamic resolution

Every relationship must have a resolution state:

```yaml
resolution:
  status: resolved | partially_resolved | unresolved | dynamic
  confidence: high | medium | low
  reason: string
```

Examples of dynamic cases:

- templated include filename
- computed role name
- dynamic inventory
- variable-derived template destination
- lookup plugin result
- runtime extra vars
- condition based on gathered facts

Never silently guess a concrete target.

Jinja handling must be parse-only:

- use `jinja2.Environment().parse()` with only the repository-configured safe parse-time extensions
- walk the AST to extract undeclared variables and literal references
- never call `render()`
- never execute filters, tests, lookups or custom extensions
- record parse failures as diagnostics

## Source traceability

Every extracted node must include source provenance:

```yaml
source:
  path: roles/dns/tasks/main.yml
  document: 0
  line_start: 12
  line_end: 19
  content_hash: sha256:...
```

Line numbers may be `null` if unavailable, but repository-relative paths and hashes are mandatory.

Content hashing must be cross-platform deterministic.

Before hashing source content:

1. decode using UTF-8 with BOM handling
2. record a diagnostic for unsupported encodings
3. normalize CRLF and CR line endings to LF
4. preserve all other whitespace and content exactly
5. hash the normalized UTF-8 byte sequence
6. use the same normalization for full-file and source-region hashes

Hashes must not vary solely because a repository was cloned on a different operating system.

## Stable identifiers

Generate deterministic stable IDs.

Recommended format:

```text
playbook:<relative-path>
play:<relative-path>:<document-index>:<play-index>
role:<role-name>
task:<relative-path>:<document-index>:<task-index>
handler:<relative-path>:<document-index>:<handler-index>
variable:<variable-name>:<definition-path>:<definition-index>
template:<relative-path>
inventory-group:<group-name>
inventory-host:<host-name>
```

IDs must remain stable when unrelated files change.

## Canonical graph model

`graph.yaml` is the only canonical machine-readable artifact for repository logic.

It must contain:

```yaml
schema_version: "1.0.0"
nodes: []
edges: []
retrieval_topics: []
statistics: {}
```

Every node must include:

```yaml
id: task:roles/dns/tasks/main.yml:0:3
kind: task
name: Configure systemd-resolved
significance: high
source:
  path: roles/dns/tasks/main.yml
  document: 0
  line_start: 18
  line_end: 26
  content_hash: sha256:...
resolution:
  status: resolved
  confidence: high
  reason: Static task declaration
attributes: {}
```

Every edge must include:

```yaml
id: edge:task-notifies-handler:<stable-hash>
type: notifies
from: task:roles/dns/tasks/main.yml:0:3
to: handler:roles/dns/handlers/main.yml:0:0
source:
  path: roles/dns/tasks/main.yml
  document: 0
  line_start: 18
  line_end: 26
resolution:
  status: resolved
  confidence: high
  reason: Exact handler name match
attributes:
  notification: restart systemd-resolved
```

## Significance classification

Every source-derived node must include:

```yaml
significance: critical | high | normal | low
significance_rule_id: string
```

Significance classification must be configuration-driven and auditable.

Store ordered rules in:

```text
config/significance_rules.yaml
```

Each rule must support:

```yaml
- id: destructive-shell-command
  priority: 100
  match:
    modules:
      - ansible.builtin.command
      - ansible.builtin.shell
    patterns:
      - '\brm\s+-rf\b'
      - '\bmkfs\b'
  significance: critical
  reason: Destructive command pattern
```

Required default categories:

- `critical`: destructive operations, authentication, authorization, firewalling, routing, kernel changes, data deletion and credential handling.
- `high`: templates, service restarts, package repositories, systemd units, network configuration, storage and database changes.
- `normal`: ordinary package, file, user, group and configuration operations.
- `low`: debug messages, metadata-only tasks, comments, simple assertions and non-operational bookkeeping.

Rules must be deterministic, ordered by priority, schema-validated and overridable by repository configuration.

Validate `config/significance_rules.yaml` against `schemas/significance_rules.schema.yaml` during `scan` and `validate`. Invalid rule tables must fail validation before scanning begins.

`ANSIBLE_REPO_MAP.md` should primarily surface `critical` and `high` nodes. All nodes remain queryable from `graph.yaml`.

## Repository map

Generate `ANSIBLE_REPO_MAP.md` as the primary human-readable entry point.

It must include:

- repository purpose if inferable
- scan metadata
- entry playbooks
- inventory overview
- role catalogue
- playbook-to-role relationships
- role dependencies
- key execution paths
- key handlers
- high-impact templates and files
- variable ownership
- variable conflict warnings
- important tags
- dynamic and unresolved references
- custom plugins and modules
- retrieval guidance
- source-of-truth warning

Enforce a hard size budget:

```yaml
repository_map:
  max_lines: 1000
  max_roles: 120
  max_entry_playbooks: 50
  max_execution_paths: 100
  max_diagnostics: 30
  include_task_bodies: false
  include_variable_values: false
  include_low_significance_nodes: false
  require_truncation_summary: true
```

The current target repository contains approximately 94 roles. Silent truncation is forbidden.

If any section is truncated, the map must state the exact omitted count and retrieval command, for example:

```text
42 additional roles omitted from this view. Query them with:
ansible-repo-intelligence query role --limit 120
```

Target 400–1000 lines for a repository of this scale while preserving the configured hard maximum.

Do not paste:

- task bodies
- full variable values
- full templates
- repetitive low-significance nodes
- the full graph
- large diagnostics lists

The map must orient the agent, not duplicate the repository.

## Retrieval guidance

Generate deterministic retrieval hints such as:

```yaml
retrieval_topics:
  dns:
    summary: DNS configuration and resolver behaviour
    primary_nodes:
      - role:dns
      - template:roles/dns/templates/resolved.conf.j2
    source_paths:
      - roles/dns/tasks/main.yml
      - roles/dns/handlers/main.yml
      - roles/dns/templates/resolved.conf.j2
```

Base topics on:

- role names
- task names
- tags
- templates
- managed services
- variables
- destination paths
- referenced commands

Do not use an LLM for topic generation.

## Variable precedence conflict algorithm

Potential precedence conflicts must be detected by an explicit, deterministic algorithm defined in:

```text
config/variable_precedence_rules.yaml
```

Minimum required behaviour:

1. Collect all statically discovered definitions for each variable name.
2. Assign every definition one precedence class:
   - role_default
   - inventory_group
   - inventory_host
   - play_var
   - vars_file
   - role_var
   - block_var
   - task_var
   - include_var
   - set_fact
   - registered
   - extra_var_unknown
   - environment_lookup
   - unknown_runtime
3. Flag `ARI006_POSSIBLE_VARIABLE_PRECEDENCE_CONFLICT` when:
   - the same variable is defined in two or more distinct precedence classes that can apply to the same reachable execution path, or
   - it is defined multiple times in the same precedence class for overlapping inventory or execution scope.
4. Do not flag definitions proven to be isolated to disjoint roles, plays, inventory flavors, groups or conditions.
5. Record all contributing definitions, classes, scopes, source locations and overlap reasons.
6. Never claim the winning runtime value unless all relevant higher-precedence inputs are statically known.

The precedence table and overlap rules must be documented and covered by fixtures.

Validate `config/variable_precedence_rules.yaml` against `schemas/variable_precedence_rules.schema.yaml` during `scan` and `validate`. Invalid precedence configuration must fail validation before analysis begins.

## Query command

Implement deterministic queries:

```bash
ansible-repo-intelligence query role dns
ansible-repo-intelligence query variable dns_servers
ansible-repo-intelligence query handler "restart resolved"
ansible-repo-intelligence query tag networking
ansible-repo-intelligence query file /etc/systemd/resolved.conf
ansible-repo-intelligence query service systemd-resolved
```

Queries must return:

- matching nodes
- direct relationships
- relevant source files
- confidence and unresolved states
- significance
- bounded context

Required query controls:

```text
--limit 25
--max-depth 1
--fields id,kind,name,source,resolution,significance
--output concise|yaml
--include-neighbours
--include-attributes
--max-output-bytes 65536
```

Default behaviour:

1. Return at most 25 nodes.
2. Traverse one graph hop only.
3. Return source paths before expanded attributes.
4. Do not print the full graph unless explicitly requested.
5. Require an explicit flag for deeper traversal.
6. Require an explicit flag for full attribute expansion.
7. Prefer concise output.

## Impact command

Implement static impact analysis:

```bash
ansible-repo-intelligence impact \
  --path roles/dns/templates/resolved.conf.j2 \
  --limit 50 \
  --max-depth 3 \
  --max-output-bytes 131072
```

Report:

- tasks referencing the file
- destination paths
- handlers notified
- services affected
- playbooks and roles that can reach the task
- inventory groups potentially targeted
- variables consumed
- dynamic uncertainties

Impact analysis must be bounded by default:

```text
--limit 50
--max-depth 3
--max-output-bytes 131072
```

Requirements:

1. Stop traversal when any bound is reached.
2. Return `truncated: true` and the exact truncation reason.
3. Use the same `traversal.py` implementation as `query`.
4. Require an explicit override for larger traversals.
5. Never duplicate reachability or cycle-detection logic.

Do not claim runtime certainty.

## Existing repository intelligence systems

The target repository already contains or references `.ai-context/`, `.archcore/`, `graphify-out/`, `repomix.config.json`, `AI_NAVIGATION.md` and `context-map.yaml`.

The new tool must be additive rather than competitive:

- `graphify-out/`: generic repository graphing; may be stale and does not provide authoritative Ansible-domain semantics
- Repomix: context packaging after relevant files are selected
- `.archcore`: higher-authority architectural decisions
- existing `.ai-context` governance pack: current bootstrap and navigation authority
- this skill: Ansible-domain static semantics, including handler resolution, variable-precedence diagnostics, dynamic/unresolved states, inventory-flavor scoping and significance classification

README and `ANSIBLE_REPO_MAP.md` must state this distinction explicitly. Do not ingest `graphify-out/graph.json` as authoritative source.

## Agent token-efficiency rules

The generated context is intended to reduce repository-discovery cost.

Enforce this agent workflow:

1. Read only `ANSIBLE_REPO_MAP.md` initially.
2. Never load `graph.yaml` in full unless the user explicitly requests a repository-wide audit.
3. Use bounded CLI queries to retrieve graph slices.
4. Open only the original source files required to verify the result.
5. Do not load diagrams or generated cache files into model context.
6. Expand one graph hop by default.
7. Prefer concise query output containing IDs, names, source paths, resolution and significance.
8. Treat generated context as navigation metadata, not as a substitute for source.

The normal retrieval flow must be:

```text
Question
  -> read compact repository map
  -> run bounded graph query
  -> open 3–10 relevant source files
  -> verify conclusions against source
```

The implementation must not encourage agents to read all generated artifacts.

## Incremental mode

Implement an incremental scan based on:

- relative path
- file content hash
- parser version
- configuration fingerprint
- schema version

Reparse only changed files and dependants where safe.

A full scan must remain available.

The output must be deterministic:

- stable ordering
- stable IDs
- normalized paths
- no timestamps inside content-derived hashes
- no random identifiers

## Security requirements

- never execute repository scripts
- never render arbitrary Jinja templates
- never decrypt Ansible Vault files
- never expose secret values
- redact values for variable names matching configurable patterns
- do not follow symlinks outside the repository unless explicitly enabled
- prevent path traversal
- enforce maximum input file sizes
- treat YAML tags and constructors safely
- do not use unsafe YAML loading
- do not invoke arbitrary lookup plugins
- do not connect to remote hosts
- inventory commands must be opt-in or explicitly configured

Default secret-name patterns must include:

```text
password
passwd
secret
token
api_key
apikey
private_key
credential
auth
vault
community
```

Avoid over-redacting ordinary non-secret metadata where possible.

## Validation

Validate every generated YAML artifact against its corresponding schema.

Validation must confirm:

- valid YAML
- schema conformance
- `config/significance_rules.yaml` conforms to `schemas/significance_rules.schema.yaml`
- `config/variable_precedence_rules.yaml` conforms to `schemas/variable_precedence_rules.schema.yaml`
- stable unique IDs
- valid references
- no references to missing nodes unless explicitly unresolved
- source paths remain repository-relative
- no secret values in generated outputs
- no absolute local paths unless explicitly permitted
- content hashes match expected format
- output manifest matches actual files
- `ANSIBLE_REPO_MAP.md` remains within the configured line budget
- query defaults enforce result and traversal limits
- no duplicated persistent index files exist outside the approved lean output set
- graph statistics reconcile with node and edge counts
- vendored collection file counts are reported separately and excluded from first-class node counts by default
- every inventory-derived node is flavor-scoped
- custom vars-plugin sources are marked dynamic
- truncated repository-map sections include exact omitted counts
- generated artifacts are registered as derived/non-authoritative in the existing context authority model

The scan must not report success if mandatory outputs are malformed.

## Diagnostics

Generate diagnostics with severity:

```text
info
warning
error
fatal
```

Include machine-readable codes such as:

```text
ARI001_UNRESOLVED_STATIC_INCLUDE
ARI002_DYNAMIC_INCLUDE
ARI003_UNRESOLVED_HANDLER
ARI004_DUPLICATE_HANDLER_NAME
ARI005_VARIABLE_WITHOUT_DEFINITION
ARI006_POSSIBLE_VARIABLE_PRECEDENCE_CONFLICT
ARI007_EXTERNAL_SYMLINK_BLOCKED
ARI008_UNSUPPORTED_YAML_CONSTRUCT
ARI009_SCHEMA_VALIDATION_FAILED
ARI010_SECRET_VALUE_REDACTED
ARI011_REPOSITORY_MAP_LIMIT_EXCEEDED
ARI012_QUERY_LIMIT_EXCEEDED
ARI013_GRAPH_REFERENCE_INVALID
ARI014_DUPLICATE_PERSISTENT_INDEX
ARI015_VENDORED_COLLECTION_EXCLUDED
ARI016_COLLECTION_ORIGIN_UNKNOWN
ARI017_CUSTOM_VARS_PLUGIN_DYNAMIC
ARI018_ANSIBLE_CONFIG_UNRESOLVED_PATH
ARI019_INVENTORY_FLAVOR_COLLISION
ARI020_CONTEXT_AUTHORITY_CONFLICT
ARI021_MAP_SECTION_TRUNCATED
ARI022_INVENTORY_BACKUP_EXCLUDED
```

Strict mode must fail for errors and fatal conditions.

Default mode may complete with warnings and unresolved dynamic relationships.

## Understanding boundary

The implementation must never claim complete understanding of all runtime Ansible behaviour.

It may claim:

> High-coverage static understanding of repository structure and statically resolvable relationships, with explicit identification of dynamic and unresolved behaviour.

It must explicitly identify limitations involving:

- dynamic inventory
- extra vars and AWX/Tower survey inputs
- runtime facts
- templated include or role names
- lookup-plugin results
- Vault-encrypted values
- external variable sources
- custom plugin execution
- environment-specific values
- runtime failures and host state
- actual idempotency
- complete variable-precedence resolution where inputs are unavailable
- external files generated at runtime
- remote service responses

## Testing requirements

Implement unit and integration tests covering:

- basic playbook parsing
- static imports
- dynamic includes
- role dependencies
- nested task files
- blocks, rescue and always
- handler name resolution
- handler `listen`
- unresolved handlers
- template relationships
- variable definitions and references
- `set_fact`
- `register`
- inventory parsing
- group hierarchy
- secret redaction
- source hashes
- deterministic IDs
- deterministic ordering
- schema validation
- malformed YAML
- vault-encrypted files
- symlink escape prevention
- incremental rescans
- unchanged-output idempotency
- repository-map hard size limit
- default query result limit
- default one-hop traversal limit
- significance filtering
- absence of redundant generated indexes
- bounded graph-slice output
- vendored collection exclusion with FQCN usage retained
- repository-authored collection inclusion
- unknown collection origin diagnostics
- `ansible.cfg` roles-path resolution
- `ansible.cfg` collection-path resolution
- configured Jinja extension parsing for `do` and `loopcontrols`
- custom vars-plugin dynamic-source modelling
- seven-flavor inventory namespacing
- inventory ZIP backup exclusion
- repository-map truncation visibility with exact omitted counts
- existing context-map authority-order preservation
- graphify-out treated as non-authoritative comparative evidence
- mcp-smc versus static impact documentation checks
- token-efficiency benchmark harness

Required acceptance test:

```bash
ansible-repo-intelligence scan \
  --repo tests/fixtures/multi_role_repo \
  --output /tmp/ari-output \
  --offline \
  --strict

ansible-repo-intelligence validate \
  --context /tmp/ari-output

diff -ru tests/golden/multi_role_repo /tmp/ari-output
```

Normalize scan timestamps before golden comparison or exclude volatile timestamps from deterministic artifacts.

## Efficiency benchmark

Add a reproducible benchmark using a representative multi-role Ansible repository and at least 20 targeted questions.

Benchmark execution must use two isolated runs:

- baseline run: a fresh agent session without access to `.ai-context`
- indexed run: a separate fresh agent session with access to `ANSIBLE_REPO_MAP.md` and bounded CLI queries

The same session must not execute and grade both sides.

Required controls:

1. Use the same model, model version, system instructions, tool permissions and repository revision.
2. Record prompts, outputs, files opened, query commands, elapsed time and token usage.
3. Define a gold answer for each question containing required source files, required relationships, acceptable answer points and disallowed unsupported claims.
4. Grade using either:
   - a human reviewer, or
   - a separate blind grading process that does not know which run was baseline or indexed.
5. Store benchmark inputs and grading results under `tests/benchmark/`.
6. Make the harness rerunnable from one documented command.

Measure:

- source files opened
- input tokens consumed
- time to first relevant source file
- relevant-file retrieval recall
- answer correctness
- unsupported claims
- repository-map size
- query-result size

Target acceptance thresholds:

```text
at least 60% fewer source files opened for targeted questions
at least 40% lower input-token usage
at least 95% retrieval recall for known relevant files
no reduction in answer correctness
no increase in unsupported claims
repository map within configured size budget
query results within configured node and depth limits
```

Treat these as empirical targets, not guaranteed outcomes. If not met, report `PARTIAL` and include raw evidence.

## Required quality gates

The implementation is complete only when:

1. All tests pass.
2. Generated YAML validates against schemas.
3. Running the same scan twice produces semantically identical output.
4. No repository files are modified.
5. Dynamic references are labelled rather than guessed.
6. Source provenance exists for every source-derived node.
7. Secret values are absent from output fixtures.
8. The repository map points agents to relevant files without duplicating the repository and remains within its configured size budget.
9. The implementation works offline.
10. README and SKILL instructions match actual CLI behaviour.
11. Targeted queries return no more than 25 nodes and one graph hop by default.
12. No redundant persistent indexes are generated outside `manifest.yaml`, `ANSIBLE_REPO_MAP.md`, `graph.yaml`, `diagnostics.yaml` and `cache/scan-state.yaml`.
13. A benchmark demonstrates that indexed retrieval does not reduce answer correctness or increase unsupported claims.
14. The documentation describes the result as high-coverage static understanding, not complete runtime understanding.
15. The benchmark results are recorded and reproducible.
16. The full graph is never loaded by default in agent instructions.
17. Query and impact traversal share one implementation in `traversal.py`.
18. CRLF/LF and UTF-8 BOM normalization produce identical semantic hashes.
19. Significance rules are configuration-driven and schema-validated.
20. Variable precedence conflict diagnostics follow the documented overlap algorithm.
21. Benchmark grading is independent of the sessions that produced the answers.
22. Governance files were bootstrapped through `skill-ai-it` and the skill is registered in the parent project table.
23. Python 3.14 is pinned through `.mise.toml` and the virtual environment is outside the repository.
24. The default role budget covers the current approximately 94-role repository or reports exact omitted counts.
25. Vendored collection source is excluded from first-class graph nodes while FQCN usage remains resolvable.
26. Custom vars plugins are modelled as dynamic sources without execution.
27. Effective `ansible.cfg` path and Jinja-extension settings are honoured.
28. All inventory-derived nodes and relationships are flavor-scoped.
29. Existing context and graph systems remain non-conflicting and documented.
30. Offline static impact and live `mcp-smc` operational impact are clearly distinguished.
31. Both configuration rule tables validate against dedicated schemas before analysis begins.
32. If independent benchmark execution is unavailable, the result is `PARTIAL`; self-grading is forbidden.
33. Phase reports document checkpoint commits and resumable state for multi-session execution.

## Documentation requirements

### ARCHITECTURE.md

Document:

- the fixed module ownership boundaries
- why `app_config.py` and `ansible_config.py` are separate
- why `variables.py` and `vars_plugins.py` are separate
- why `inventory.py` and `inventory_flavors.py` are separate
- why query and impact share `traversal.py`
- canonical data flow from discovery to graph to bounded retrieval

### README.md

Document:

- purpose
- installation
- dependencies
- quick start
- lean output files
- schema validation
- query examples
- bounded retrieval
- impact analysis
- offline mode
- limitations
- security model
- understanding boundary
- token-efficiency benchmark
- troubleshooting
- differentiation from `graphify-out`, Repomix, `.archcore` and existing `.ai-context` governance
- vendored collection handling
- custom vars-plugin limitations
- multi-flavor inventory usage
- static impact versus `mcp-smc` operational impact

### SKILL.md

Define the agent workflow:

1. Detect whether the repository is Ansible-based.
2. Check whether `.ai-context/manifest.yaml` exists.
3. Validate freshness using source hashes or run incremental scan.
4. Read `ANSIBLE_REPO_MAP.md`.
5. Query bounded slices from `graph.yaml` before searching broadly.
6. Never load the complete graph by default.
7. Open the original source files referenced by relevant nodes.
8. Verify all important claims against source.
9. Never treat generated context as a substitute for source.
10. Refresh the index after relevant source changes.
11. Record unresolved or dynamic logic as uncertainty.
12. Respect query limits and graph depth defaults.
13. Preserve the repository's existing context authority order.
14. Use `mcp-smc` instead for live host/flavor blast-radius questions.
15. Treat vendored collection internals as external implementation unless deep indexing is explicitly requested.
16. Treat vars-plugin-derived values as dynamic unless proven from runtime inventory output.

### AGENTS.md

Specify:

- generated context is derivative
- source files are authoritative
- no runtime execution during indexing
- no secret exposure
- no arbitrary remote access
- validation is mandatory after generation
- the full graph must not be loaded by default
- bounded retrieval is mandatory
- runtime completeness must not be claimed
- existing `.archcore` and context-map authority outrank generated repository intelligence
- vendored collections are excluded from deep indexing by default
- inventory results must remain flavor-scoped
- custom vars plugins must never be executed during static scans
- `mcp-smc` and static CLI impact have distinct purposes

## Optional integration

Support optional import of `ansible-playbook-grapher` output.

The external graph must be treated as supplementary evidence.

Do not make successful scanning dependent on that tool.

Record external-tool provenance:

```yaml
external_tools:
  ansible_playbook_grapher:
    available: true
    version: "..."
    invoked: true
    command: [...]
    exit_code: 0
    output_validated: true
```

Never trust a successful process exit alone.

Validate imported output structurally.

## Final implementation report

After implementation, produce:

```text
docs/reports/ansible-repo-intelligence-implementation-report.md
```

Include:

- files created
- dependencies selected
- CLI commands implemented
- schemas implemented
- tests executed
- exact test results
- limitations
- unresolved issues
- security review
- deterministic-output proof
- repository-map size-budget proof
- bounded-query proof
- token-efficiency benchmark results
- relevant-file retrieval recall
- baseline versus indexed source-file counts
- baseline versus indexed token counts
- total repository-authored YAML count
- total vendored YAML count excluded from first-class indexing
- collection-origin classification results
- custom vars-plugin detection results
- effective `ansible.cfg` settings used
- per-flavor inventory coverage
- context-map integration evidence
- graphify-out differentiation evidence
- mcp-smc impact-scope differentiation evidence
- repository-map omitted-count evidence, if truncation occurred
- significance-rule schema validation evidence
- variable-precedence-rule schema validation evidence
- benchmark orchestration status and, if unavailable, explicit PARTIAL rationale
- phase checkpoint and multi-session resumability evidence
- example generated output
- final verdict: READY, PARTIAL or NOT READY

Do not declare `READY` if:

- any mandatory acceptance criterion remains unproven
- the lean-output contract is violated
- the repository map exceeds its size budget
- query defaults are unbounded
- the efficiency benchmark shows worse correctness
- unsupported claims increase
- material token inflation occurs
- the implementation claims complete runtime understanding

## File naming and governance note

This prompt is a time-bound planning artifact and must use a datetime-suffixed filename, for example:

```text
implementation-prompt-20260703_1349.md
```

Before handing it to Codex:

1. verify the parent naming validator accepts it
2. register the skill in the parent `Skill Authoring Projects` table
3. retain a stable pointer only if workspace policy explicitly permits one
