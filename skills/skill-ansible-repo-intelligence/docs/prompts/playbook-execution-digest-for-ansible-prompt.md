# Playbook Execution Digests for Ansible Repository Intelligence

You are working in:

```text
/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-ansible-repo-intelligence
```

Target Ansible repository:

```text
/Volumes/Data/_ansible/ansible-wifi
```

## Objective

Extend `skill-ansible-repo-intelligence` so it can generate compact, source-traceable **Playbook Execution Digests**.

The goal is not to create another large repository summary or duplicate the existing graph.

The goal is to let an AI agent understand how a playbook executes without:

- loading the full graph
- reading every role
- opening every task file
- reading the full repository map
- receiving verbose graph-node dictionaries
- relying on generated prose without evidence

The new feature must provide:

1. a compact playbook catalogue
2. an on-demand execution digest for one playbook
3. bounded role and task expansion
4. deterministic managed-action facts
5. handler, variable, condition and inventory relationships
6. explicit dynamic and unresolved markers
7. source paths, line numbers and hashes
8. compact output suitable for direct AI-agent consumption

The implementation must reuse the existing canonical graph and managed-resource enrichment.

Do not create a second independent parser or a competing execution model.

## Background

The first external benchmark showed that the original indexed workflow was inefficient because the agent:

1. read the repository map
2. ran multiple queries
3. received source pointers
4. opened source files anyway

The enriched action digest substantially improved the result:

```text
old indexed:
  source files opened: 29
  input tokens: 85.4k
  correctness: 21/22

new managed-action digest:
  source files opened: 0
  input tokens: 78.8k
  correctness: 21/22
```

The digest also corrected the Asterisk installation error because it exposed the actual `get_url`, command and source-compilation actions instead of allowing the agent to infer that Asterisk was package-installed.

The next step is to extend the same fact-digest approach from roles to playbooks.

## Core design principle

The new feature must follow this hierarchy:

```text
compact playbook catalogue
        ↓
select one playbook
        ↓
generate bounded execution digest
        ↓
expand one role or relationship only when needed
        ↓
verify original source only for high-risk or uncertain facts
```

Do not implement:

```text
read one giant master plan
→ load all 94 roles
→ include every task
→ duplicate graph.yaml
```

## Terminology

Use the term:

```text
Playbook Execution Digest
```

Do not use “master routing plan,” because “routing” is ambiguous and may be confused with:

- network routing
- LLM routing
- agent routing
- inventory routing

A Playbook Execution Digest is a compact representation of Ansible execution structure.

## Governance preflight

Before editing:

1. Read:
   - `AGENTS.md`
   - `SKILL.md`
   - `README.md`
   - `ARCHITECTURE.md`
   - `AI_NAVIGATION.md`
   - `context-map.yaml`
   - `ROADMAP.md`
   - `CHANGELOG.md`
   - current implementation reports
   - benchmark reports
2. Preserve the existing governance hierarchy.
3. Treat `.archcore` and existing context authority as higher-authority inputs.
4. Treat `.ai-context` outputs as derived and non-authoritative.
5. Do not rewrite unrelated sections.
6. Follow parent workspace naming and report conventions.
7. Keep generated execution digests outside authoritative source directories.

## Phase 1 — Define the playbook execution model

Create an explicit internal model for:

- playbooks
- plays
- pre-tasks
- roles
- task blocks
- post-tasks
- handlers
- imported playbooks
- included roles
- imported roles
- included task files
- imported task files
- managed actions
- variables consumed
- inventory scope
- conditions
- loops
- delegation
- dynamic references
- unresolved references

The model must preserve execution order where Ansible source order is statically knowable.

### Required playbook model

Each playbook digest must contain:

```yaml
playbook:
  id: playbook:playbooks/deploy-smc.yml
  path: playbooks/deploy-smc.yml
  name: Deploy SMC
  summary:
    plays: 3
    roles: 8
    tasks: 142
    handlers: 19
    dynamic_references: 2
    unresolved_references: 0
  source:
    path: playbooks/deploy-smc.yml
    content_hash: sha256:...
```

### Required play model

```yaml
plays:
  - id: play:playbooks/deploy-smc.yml:0:0
    order: 1
    name: Configure SMC hosts
    hosts_expression: smc
    become: true
    gather_facts: true
    strategy: linear
    serial: null
    inventory_scope:
      flavors:
        - rct
        - wh
      groups:
        - smc
    source:
      path: playbooks/deploy-smc.yml
      line_start: 2
      line_end: 45
```

### Required execution sections

Each play must expose, in order:

```yaml
pre_tasks: []
roles: []
tasks: []
post_tasks: []
handlers: []
```

Do not merge these into one unordered task list.

## Phase 2 — Build the compact playbook catalogue

Implement a compact catalogue derived from `graph.yaml`.

Preferred command:

```bash
ansible-repo-intelligence list playbooks \
  --context .ai-context \
  --output concise
```

Alternative acceptable command:

```bash
ansible-repo-intelligence query playbook \
  --view catalogue
```

Do not create a new command if an existing command can support the feature cleanly.

### Catalogue output

The catalogue must include only high-level selection information:

```yaml
playbooks:
  - id: playbook:playbooks/deploy-smc.yml
    name: Deploy SMC
    path: playbooks/deploy-smc.yml
    plays: 3
    roles:
      - smc_base
      - smc_network
      - smc_dns
      - smc_asterisk
    inventory_flavors:
      - rct
      - wh
    purposes:
      - operating-system baseline
      - network configuration
      - DNS services
      - voice services
    dynamic_references: 2
    unresolved_references: 0
```

### Catalogue constraints

The catalogue must:

- not include task bodies
- not include all variables
- not include every handler
- not duplicate action digests
- remain under a configurable line and byte limit
- state exact omitted counts if truncated
- include a command showing how to retrieve omitted entries

Recommended limits:

```yaml
playbook_catalogue:
  max_entries: 100
  max_lines: 300
  max_output_bytes: 65536
  require_truncation_summary: true
```

The current repository has approximately 23 playbooks, so the default catalogue should include all of them without truncation.

## Phase 3 — Implement `explain playbook --view execution-plan`

Implement:

```bash
ansible-repo-intelligence explain playbook <playbook> \
  --context .ai-context \
  --view execution-plan
```

Example:

```bash
ansible-repo-intelligence explain playbook playbooks/deploy-smc.yml \
  --context .ai-context \
  --view execution-plan
```

Support lookup by:

- exact relative path
- playbook ID
- unambiguous basename
- unambiguous display name

If the name is ambiguous, return candidates and do not guess.

## Execution-plan output

The digest must show:

1. playbook metadata
2. plays in source order
3. pre-tasks in source order
4. roles in source order
5. role purpose and entry point
6. role actions in execution order
7. explicit tasks in source order
8. post-tasks in source order
9. handler relationships
10. variables consumed
11. inventory scope
12. conditions and loops
13. dynamic or unresolved references
14. source provenance
15. verification recommendations

### Example

```yaml
playbook:
  name: Deploy SMC
  path: playbooks/deploy-smc.yml

plays:
  - order: 1
    name: Configure SMC hosts
    hosts_expression: smc
    become: true

    roles:
      - order: 1
        name: smc_base
        purpose:
          - configure baseline packages
          - configure operating-system defaults
        entrypoint:
          path: roles/smc_base/tasks/main.yml

        actions:
          - order: 1
            task_name: Install base packages
            module: ansible.builtin.package
            operation: install_packages
            resources:
              packages:
                - curl
                - jq
                - rsync
            conditions: []
            notify: []
            verification:
              recommended: false
            source:
              path: roles/smc_base/tasks/main.yml
              line_start: 8
              line_end: 14
              content_hash: sha256:...

          - order: 2
            task_name: Configure sysctl
            module: ansible.builtin.template
            operation: render_template
            resources:
              src: sysctl.conf.j2
              dest: /etc/sysctl.d/99-smc.conf
            notify:
              - Reload sysctl
            verification:
              recommended: false
            source:
              path: roles/smc_base/tasks/main.yml
              line_start: 26
              line_end: 35
              content_hash: sha256:...

      - order: 2
        name: smc_dns
        purpose:
          - install DNS packages
          - configure Unbound
          - configure Stubby

        actions:
          - order: 1
            task_name: Install DNS packages
            module: ansible.builtin.apt
            operation: install_packages
            resources:
              packages:
                - unbound
                - stubby
            source:
              path: roles/smc_dns/tasks/main.yml
              line_start: 4
              line_end: 11

          - order: 2
            task_name: Configure Unbound
            module: ansible.builtin.template
            operation: render_template
            resources:
              src: unbound.conf.j2
              dest: /etc/unbound/unbound.conf
            notify:
              - Restart unbound
            variables:
              - unbound_forwarders
              - topology_dns_servers
            source:
              path: roles/smc_dns/tasks/main.yml
              line_start: 20
              line_end: 31
```

## Phase 4 — Managed-action coverage

Reuse the existing managed-resource enrichment.

Do not create another managed-resource parser.

The execution digest must support at least:

### Packages

Modules:

```text
package
apt
dnf
yum
pip
homebrew
```

Extract:

- package names
- state
- update-cache settings
- repository source where relevant

### Services

Modules:

```text
service
systemd
systemd_service
```

Extract:

- service name
- state
- enabled
- daemon reload
- masked
- scope

### Templates and files

Modules:

```text
template
copy
file
lineinfile
blockinfile
replace
assemble
```

Extract:

- source
- destination/path
- owner
- group
- mode
- state
- backup
- validation command where present

### Commands and scripts

Modules:

```text
command
shell
script
raw
```

Extract:

- command
- executable
- working directory
- creates
- removes
- stdin where safely representable

Do not execute commands.

### Downloads and archives

Modules:

```text
get_url
uri
unarchive
git
```

Extract:

- source URL or repository
- destination
- revision/version
- checksum
- archive extraction location

### Users and permissions

Modules:

```text
user
group
authorized_key
acl
```

Extract:

- user/group name
- state
- groups
- shell
- home
- key source
- permission target

### Scheduling and mounts

Modules:

```text
cron
mount
```

Extract:

- schedule
- command
- mount source
- mount destination
- filesystem
- options
- state

### Includes and imports

Extract:

- include/import type
- literal target
- dynamic target expression
- resolved targets
- unresolved reason
- conditions
- loop expansion status

### Unknown modules

Unknown modules must still produce:

```yaml
operation: invoke_module
resources:
  module: namespace.collection.module
  selected_arguments:
    key: value
```

Do not discard them.

## Phase 5 — Preserve execution semantics

Every action digest must preserve relevant semantics.

Required fields where applicable:

```yaml
conditions:
  when: []
loop:
  expression: null
  variable: null
delegate_to: null
run_once: false
become: null
tags: []
notify: []
register: null
retries: null
delay: null
until: null
changed_when: null
failed_when: null
```

Do not flatten conditions into prose.

Do not claim that a task always runs when it has a condition.

Example:

```yaml
conditions:
  when:
    - ansible_os_family == "Debian"
verification:
  recommended: true
  reason: Execution depends on runtime fact ansible_os_family
```

## Phase 6 — Handler relationships

The digest must show both:

- tasks that notify handlers
- handlers that may run

Example:

```yaml
handler_relationships:
  - notification: Restart unbound
    notified_by:
      - task: Configure Unbound
        source: roles/smc_dns/tasks/main.yml:20
    resolves_to:
      - handler: Restart unbound
        operation: restart_service
        service: unbound
        source: roles/smc_dns/handlers/main.yml:3
    resolution:
      status: resolved
      confidence: high
```

Support:

- handler `name`
- handler `listen`
- duplicate names
- unresolved notifications
- cross-role ambiguity
- `meta: flush_handlers`

Do not imply exact runtime firing order when Ansible semantics or conditions prevent static certainty.

## Phase 7 — Variables and origin summaries

Add optional variable views.

Commands:

```bash
ansible-repo-intelligence explain playbook <playbook> \
  --view variables
```

```bash
ansible-repo-intelligence explain role <role> \
  --view variables
```

Output should classify variables as:

```text
role_default
role_var
inventory_group
inventory_host
play_var
task_var
block_var
include_var
set_fact
registered
vars_plugin
runtime_unknown
extra_var_unknown
```

Example:

```yaml
variables:
  consumed:
    - name: topology_dns_servers
      possible_origins:
        - kind: vars_plugin
          source: vars_plugins/topology_vars.py
          resolution:
            status: dynamic
            confidence: high
        - kind: inventory_group
          source: inventories/rct/prod/group_vars/smc.yml
          resolution:
            status: resolved
            confidence: high
      runtime_winner:
        status: unknown
        reason: Vars plugin and inventory precedence cannot be fully resolved statically
```

Variable-origin questions must never be answered from the role action digest alone.

Route them to:

```bash
query variable <name>
query vars_plugin <name>
explain playbook <name> --view variables
```

This requirement directly addresses the topology-vars benchmark miss.

## Phase 8 — Inventory scope

Add:

```bash
ansible-repo-intelligence explain playbook <playbook> \
  --view inventory-scope
```

Show:

- host expressions
- inventory flavors
- groups
- environment scope
- static host membership if available
- dynamic inventory caveats
- vars-plugin caveats
- live operational follow-up guidance

Example:

```yaml
inventory_scope:
  host_expression: smc
  flavors:
    - rct
    - wh
  groups:
    - smc
  runtime_resolution:
    status: partially_resolved
    reason: Custom vars plugin and live inventory execution may alter values
  live_follow_up:
    tool: mcp-smc
    reason: Use live operational tooling for host-level blast radius
```

Do not execute inventory unless explicitly enabled.

## Phase 9 — Digest views

Support focused views:

```text
execution-plan
roles
actions
handlers
variables
inventory-scope
dynamic-references
managed-resources
sources
summary
```

Examples:

```bash
ansible-repo-intelligence explain playbook deploy-smc.yml \
  --view roles
```

```bash
ansible-repo-intelligence explain playbook deploy-smc.yml \
  --view actions \
  --role smc_dns
```

```bash
ansible-repo-intelligence explain playbook deploy-smc.yml \
  --view handlers
```

```bash
ansible-repo-intelligence explain playbook deploy-smc.yml \
  --view dynamic-references
```

The default view must be compact.

Recommended default:

```text
summary
```

Do not default to the full execution plan for large playbooks.

## Phase 10 — Bounds and truncation

All execution digest commands must be bounded.

Required options:

```text
--limit-actions 100
--limit-roles 50
--max-depth 3
--max-output-bytes 131072
--include-low-significance
--include-attributes
--verbose
```

Recommended defaults:

```yaml
execution_digest:
  max_roles: 50
  max_actions: 100
  max_depth: 3
  max_output_bytes: 131072
  include_low_significance: false
  include_full_attributes: false
```

If truncated, output:

```yaml
truncated: true
truncation:
  reason: action_limit
  shown: 100
  omitted: 47
  next_command: >-
    ansible-repo-intelligence explain playbook deploy-smc.yml
    --view actions --offset 100 --limit-actions 100
```

Silent truncation is forbidden.

## Phase 11 — Verification policy

The digest must include verification recommendations.

### Verification normally not required

For direct literal facts such as:

- literal package name
- literal service name
- literal template source and destination
- literal file destination
- literal user/group
- literal command
- exact handler name
- exact static include

Example:

```yaml
verification:
  recommended: false
  confidence: high
  reason: Literal module argument extracted from source
```

### Verification required

For:

- destructive actions
- authentication or authorization changes
- firewall or routing changes
- kernel changes
- dynamic includes
- Jinja-derived destinations
- complex conditions
- custom modules
- custom plugins
- conflicting variables
- truncated results
- unresolved references
- low-confidence parsing

Example:

```yaml
verification:
  recommended: true
  confidence: medium
  reason: Destination is derived from a runtime Jinja expression
```

The agent workflow must open source only when:

- verification is recommended
- the user asks for proof
- the question is high-stakes
- the digest is truncated
- confidence is not high
- the result is dynamic or unresolved

## Phase 12 — Output formats

Support:

```text
concise
yaml
json
markdown
```

YAML remains authoritative.

### Concise format

Example:

```text
Playbook: deploy-smc.yml
Play 1: Configure SMC hosts [hosts=smc]

Role 1: smc_base
  [package] install curl, jq, rsync
    roles/smc_base/tasks/main.yml:8
  [template] sysctl.conf.j2 -> /etc/sysctl.d/99-smc.conf
    notify: Reload sysctl
    roles/smc_base/tasks/main.yml:26

Role 2: smc_dns
  [apt] install unbound, stubby
    roles/smc_dns/tasks/main.yml:4
  [template] unbound.conf.j2 -> /etc/unbound/unbound.conf
    notify: Restart unbound
    roles/smc_dns/tasks/main.yml:20

Dynamic references: 2
Unresolved references: 0
```

Do not print full node dictionaries in concise mode.

## Phase 13 — Caching

Do not permanently generate execution digest files for all playbooks by default.

Preferred behaviour:

- derive digest from `graph.yaml`
- render on demand
- optionally cache by:
  - graph fingerprint
  - playbook ID
  - view
  - limits
  - renderer version

Optional cache path:

```text
.ai-context/cache/playbook-digests/
```

Cache files must:

- be non-authoritative
- be ignored by default agent navigation
- invalidate when graph fingerprint changes
- not be committed unless repository policy explicitly permits it

Do not add 23 permanent digest files unless benchmark evidence shows that doing so materially improves performance.

## Phase 14 — Graph-size control

The existing graph grew by approximately 7.8% after managed-action enrichment.

Set a guardrail:

```text
Playbook-digest support must not increase graph.yaml by more than an additional 15%
without explicit evidence that the added data improves retrieval.
```

Do not duplicate:

- task name
- task source
- role source
- conditions
- notify list
- variables
- managed resources

The execution digest renderer must derive presentation from existing canonical fields.

Measure:

- raw graph size
- compressed graph size
- digest output size
- average digest tokens
- cache size if caching is enabled

## Phase 15 — Tests

Add tests for:

### Catalogue

- lists all target playbooks
- includes role summaries
- remains within bounds
- reports exact omissions
- resolves paths and names deterministically
- rejects ambiguous basename lookup

### Execution order

- preserves play order
- preserves pre-task order
- preserves role order
- preserves explicit task order
- preserves post-task order
- preserves handler declarations
- preserves include/import relationships

### Managed actions

- package extraction
- service extraction
- template source/destination
- copy source/destination
- file path/state
- command and script extraction
- user/group extraction
- lineinfile/blockinfile extraction
- get_url/unarchive/git extraction
- unknown module fallback

### Execution semantics

- conditions
- loops
- delegation
- run-once
- become
- register
- retries
- until
- changed/failed conditions
- tags
- notify

### Relationships

- task-to-handler
- handler `listen`
- duplicate handler names
- unresolved handler
- role dependency
- include role
- include tasks
- import tasks
- import playbook
- dynamic include

### Variables

- role defaults
- role vars
- inventory variables
- vars-plugin variables
- precedence conflicts
- unknown runtime winner
- variable-origin query routing

### Inventory

- flavor namespacing
- host expression
- group scope
- dynamic inventory caveat
- live-tool recommendation

### Bounds

- role limit
- action limit
- output-byte limit
- depth limit
- exact omitted counts
- continuation command

### Verification

- literal low-risk fact does not require verification
- dynamic destination requires verification
- destructive command requires verification
- authentication task requires verification
- unresolved relation requires verification
- truncated output requires verification

### Determinism

- repeated digest output is byte-identical
- LF/CRLF/BOM variations produce identical semantic output
- catalogue ordering remains stable
- playbook lookup remains stable

All existing tests must remain green.

## Phase 16 — Benchmark

Run a focused benchmark after implementation.

### Benchmark A — playbook understanding

Select at least three playbooks:

1. one simple playbook
2. one large multi-role deployment playbook
3. one playbook using topology or inventory variables

For each playbook, ask questions covering:

- play purpose
- role order
- package installation
- template destinations
- service changes
- handler effects
- variable origins
- inventory scope
- dynamic references

Compare:

```text
direct source navigation
existing role digest
new playbook execution digest
```

### Benchmark B — relationship-heavy workload

Use questions involving:

- handler chains
- cross-role reachability
- playbook-to-role reachability
- template impact
- variable origins
- cross-flavor inventory scope
- dynamic includes
- vars plugins

Use isolated sessions and blind grading.

### Metrics

Measure:

- source files opened
- input tokens
- tool calls
- output bytes
- time to first relevant fact
- correctness
- unsupported claims
- verification-trigger rate
- graph size delta
- digest cache size
- truncation rate

### Required result reporting

Report separately:

```text
direct/local questions
playbook-level questions
relationship questions
mixed workload
```

Do not collapse all categories into one headline number.

### Acceptance targets

For playbook and relationship questions:

```text
correctness no worse than direct source navigation
unsupported claims no worse than direct source navigation
at least 50% fewer source-file opens
lower total token usage than the old indexed workflow
no mandatory map read
no full graph read
```

For simple direct role questions:

```text
no worse than token parity
no worse than correctness parity
no increase in unsupported claims
```

If the result does not meet these targets, preserve the feature as an optional view but do not promote it as the default workflow.

## Phase 17 — Documentation

Update:

- `SKILL.md`
- `README.md`
- `ARCHITECTURE.md`
- `AI_NAVIGATION.md`
- `ROADMAP.md`
- `CHANGELOG.md`
- active implementation report

Document:

- playbook catalogue
- playbook execution digest
- available views
- output bounds
- truncation behaviour
- verification policy
- caching policy
- graph-size limits
- direct versus relationship use cases
- `mcp-smc` operational split
- benchmark evidence

### Required agent rule

Add:

```text
For a targeted playbook question, query the playbook digest directly.
Do not read ANSIBLE_REPO_MAP.md first.
Use the repository map only when the relevant playbook is unknown or for a
repository-wide audit.
```

## Phase 18 — Final report

Create:

```text
docs/reports/ari-playbook-execution-digest-20260703_<HHMM>.md
```

Include:

- files changed
- internal model changes
- CLI commands and views
- action extractors added
- schemas changed
- tests added
- exact test results
- graph-size before and after
- catalogue size
- digest sizes
- benchmark methodology
- benchmark results by question class
- correctness results
- unsupported-claim results
- source-file-open results
- token results
- limitations
- unresolved cases
- final verdict

Use separate verdicts:

```text
Playbook catalogue: READY | PARTIAL | NOT READY
Playbook execution digest: READY | PARTIAL | NOT READY
Direct-question efficiency: VALIDATED | PARITY | FAILED
Playbook-question efficiency: VALIDATED | NOT VALIDATED | FAILED
Relationship-question efficiency: VALIDATED | NOT VALIDATED | FAILED
Default workflow suitability: READY | SELECTIVE ONLY | NOT READY
```

## Final constraints

- Do not create a giant master Markdown file.
- Do not duplicate the canonical graph.
- Do not create permanent per-playbook files by default.
- Do not require the repository map before targeted queries.
- Do not emit unsupported prose summaries.
- Do not hide dynamic or unresolved behaviour.
- Do not claim exact runtime execution order when it is not statically knowable.
- Do not execute repository code, plugins, templates, inventories or lookups.
- Do not weaken source provenance.
- Do not optimize only for file count while increasing total tokens.
- Do not promote the feature without blind-graded benchmark evidence.
- Prefer compact deterministic facts over verbose generated explanations.