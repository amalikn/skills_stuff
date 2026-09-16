# Codex Remediation Prompt: Make skill-ansible-repo-intelligence Efficient in Real Agent Workflows

You are working in:

```text
/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-ansible-repo-intelligence
```

## Objective

Remediate the skill so it is efficient for real AI-agent usage.

The external blind-graded benchmark proved that the current always-on indexed workflow does not improve ordinary Ansible repository navigation for a capable agent:

```text
files opened:       baseline 36    indexed 29     → only 19% fewer
input tokens:       baseline 79.1k indexed 85.4k  → 8% more
correctness:        baseline 22/22 indexed 21/22
unsupported claims: baseline 0     indexed 1
```

The tool remains valuable for deterministic Ansible relationship intelligence:

- handler `notify` / `listen` chains
- static impact and reachability
- variable-origin and precedence analysis
- dynamic or unresolved includes
- inventory-flavor scope
- custom vars-plugin modelling
- vendored collection modelling
- source-traceable graph relationships

The remediation must stop treating the skill as the default navigation path or as a general token-saving mechanism.

## Required final positioning

Position the skill as:

> An on-demand deterministic Ansible relationship-intelligence and static-impact tool for cross-file questions that ordinary source navigation handles poorly.

Do not position it as:

- a universal first-read layer
- a default workflow for every Ansible question
- a guaranteed token saver
- a replacement for direct source navigation
- a source of runtime truth

## Governance preflight

Before editing:

1. Read the repository's `AGENTS.md`, `SKILL.md`, `README.md`, `ARCHITECTURE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `ROADMAP.md`, `CHANGELOG.md`, and current reports.
2. Preserve the existing governance structure.
3. Follow the parent `skills_stuff` naming, report, runtime, and documentation policies.
4. Do not rewrite unrelated content.
5. Treat original Ansible source as authoritative and generated `.ai-context` files as derived.

## Phase 1 — Correct agent routing

Update `SKILL.md` so it no longer instructs agents to scan or read `ANSIBLE_REPO_MAP.md` for every Ansible question.

Implement three explicit routes.

### Route A — direct source lookup

This must be the default for local questions likely answerable from one role, task file, template, handler file, or variable file.

Examples:

- How is Asterisk installed?
- Which package does this role install?
- Which template creates this file?
- Where is this service configured?
- What does this task do?
- Which default value does this role use?

Required workflow:

1. Locate the likely source directly.
2. Open the minimum required files.
3. Verify the answer against source.
4. Do not scan or query the graph unless direct navigation fails or the question becomes relational.

### Route B — relationship intelligence

Invoke the tool only when the question requires cross-file relationships.

Examples:

- Which tasks can notify this handler?
- Which playbooks can reach this role or task?
- What is the static impact of changing this template?
- Where can this variable originate?
- Which definitions may conflict by precedence?
- Which inventory flavors may be affected?
- Which include targets are dynamic or unresolved?
- Which services are indirectly affected through handler chains?

Required workflow:

1. Check whether `.ai-context/manifest.yaml` is fresh.
2. Refresh incrementally only when stale or missing.
3. Run the narrowest bounded query first.
4. Do not read the full repository map by default.
5. Use `ANSIBLE_REPO_MAP.md` only for repository-wide orientation or when the query target is unknown.
6. Never load `graph.yaml` in full unless the user explicitly requests a repository-wide audit.
7. Open only the original source files returned by the query.
8. Verify all material conclusions against source.
9. Report dynamic and unresolved results as uncertainty.

### Route C — live operational blast radius

Use `mcp-smc`, not this skill, for:

- current host state
- live inventory-resolved values
- host/flavor operational blast radius
- live `ansible-inventory --host` questions

Document the split:

```text
mcp-smc topology_impact
  = live operational scope by flavor and host

ansible-repo-intelligence impact
  = offline static code and relationship reachability
```

## Phase 2 — Reduce query overhead

Audit the current query, explain, impact, and map workflows.

Implement these efficiency rules:

1. Do not scan solely because the repository is Ansible-based.
2. Reuse a fresh index across questions.
3. Query before reading the map.
4. Do not run multiple overlapping queries unless the prior result is insufficient.
5. Stop once sufficient source paths have been identified.
6. Prefer concise output.
7. Return source paths before verbose node attributes.
8. Keep one-hop traversal as the default.
9. Preserve current hard bounds:
   - query: 25 nodes, one hop, 65,536 bytes
   - impact: 50 nodes, three hops, 131,072 bytes
10. Report truncation explicitly.
11. Never include the full generated graph in an answer unless required.
12. Final answers should cite original source files, not generated graph metadata alone.

Add or verify CLI support for a compact source-path-first mode, for example:

```bash
ansible-repo-intelligence query role smc_dns \
  --context .ai-context \
  --output concise \
  --fields id,name,source,resolution \
  --limit 10 \
  --max-depth 1
```

If equivalent controls already exist, document and test them rather than creating duplicate options.

## Phase 3 — Add a routing decision function

Implement a deterministic, non-LLM routing helper.

Suggested command:

```bash
ansible-repo-intelligence route-question \
  --question "Which playbooks can reach the smc_dns role?"
```

It must return one of:

```text
direct_source
relationship_query
live_operational
repository_wide_audit
```

The router must use explicit auditable rules, not an LLM.

Example rules:

```yaml
direct_source:
  patterns:
    - "how is .* installed"
    - "where is .* configured"
    - "which package"
    - "what does this task"
    - "which template creates"

relationship_query:
  patterns:
    - "which playbooks.*reach"
    - "what.*notifies"
    - "handler chain"
    - "static impact"
    - "where can .* variable.*come from"
    - "precedence conflict"
    - "dynamic include"
    - "unresolved reference"

live_operational:
  patterns:
    - "which hosts"
    - "current value"
    - "live inventory"
    - "blast radius by flavor"
    - "ansible-inventory --host"

repository_wide_audit:
  patterns:
    - "audit the entire repository"
    - "all unresolved references"
    - "full relationship map"
```

Requirements:

- rule table must be configuration-driven
- rule matches must include the rule ID and reason
- ambiguous matches must return the safest recommendation with alternatives
- the router must not execute scans or queries automatically
- document that agents may override the recommendation when justified

A simpler documented decision table is acceptable if a new CLI command would add more maintenance cost than value. Do not build unnecessary machinery.

## Phase 4 — Correct all efficiency claims

Update:

- `SKILL.md`
- `README.md`
- `ROADMAP.md`
- `ARCHITECTURE.md`
- `AI_NAVIGATION.md`
- implementation report
- benchmark documentation
- any other active documentation containing efficiency claims

Required wording:

- external blind grading did not validate general token savings
- the indexed workflow used 8% more tokens in the current benchmark
- file reduction was 19%, not the 60% target
- correctness was 21/22 versus 22/22 baseline
- the 96.7% reduction figure is only a naive-grep proxy
- the tool should be used selectively for relationship-heavy questions

Remove or qualify claims such as:

- "without reading the whole repo"
- "reduces tokens"
- "faster for AI agents"
- "preferred first read"
- "always read the map first"
- "use for any Ansible question"

Do not delete the benchmark evidence. Preserve the failed result prominently.

## Phase 5 — Benchmark v2

Create a second benchmark that tests the tool's actual differentiators.

Do not replace or rewrite the original benchmark. Add a new benchmark set and report.

Minimum 22 questions:

```text
5 handler notify/listen chain questions
5 static impact or reachability questions
4 variable-origin or precedence questions
3 cross-flavor inventory questions
3 dynamic include / plugin / unresolved-reference questions
2 ordinary direct role-lookup control questions
```

Run three workflows:

### Workflow A — direct navigation

A fresh agent uses ordinary repository tools only.

### Workflow B — always-indexed

A fresh agent always begins with the ARI index.

### Workflow C — routed hybrid

A fresh agent follows the new routing policy:

- direct source for local questions
- ARI for relationship questions
- mcp-smc for live operational questions where available

Use the same:

- model and model version
- system instructions
- repository revision
- tool permissions
- question set
- token accounting method

Use a separate blind grader.

Measure:

- source files opened
- input tokens
- time to first relevant source
- correctness
- unsupported claims
- relationship recall
- unnecessary ARI invocations
- unnecessary map reads
- unnecessary scans
- routing accuracy

Required comparisons:

```text
hybrid vs direct
hybrid vs always-indexed
always-indexed vs direct
```

Primary success criterion:

> The routed hybrid must preserve correctness and unsupported-claim performance while reducing unnecessary index use and total token cost relative to always-indexed operation.

Do not require the tool to beat direct navigation on every local question.

Secondary benchmark:

Run the same relationship-heavy subset with one smaller local model, if an appropriate configured model is available. If unavailable, document it as not run rather than fabricating results.

## Phase 6 — Tests

Add or update tests for:

- direct-source route selection
- relationship-query route selection
- live-operational route selection
- ambiguous route handling
- rule ID and reason output
- no automatic scan from routing
- source-path-first concise query output
- query bound enforcement
- impact bound enforcement
- map not required for narrow queries
- documentation contains no general token-saving claim
- documentation preserves failed benchmark results
- benchmark v2 question-category coverage
- hybrid benchmark runbook isolation

All existing tests must remain green.

## Acceptance gates

The remediation is complete only when:

1. `SKILL.md` defaults to direct source navigation for local questions.
2. The graph is invoked selectively for relationship-heavy questions.
3. `ANSIBLE_REPO_MAP.md` is no longer mandatory first-read material.
4. Existing efficiency overclaims are removed or qualified.
5. The failed external benchmark remains visible.
6. Query and impact remain bounded.
7. The router is deterministic and auditable.
8. The router does not execute tools automatically.
9. Benchmark v2 includes relationship-heavy and control questions.
10. Benchmark v2 compares direct, always-indexed, and hybrid workflows.
11. Blind grading remains isolated.
12. All tests pass.
13. No claim of general token savings is made without new evidence.
14. The final verdict distinguishes:
    - core relationship engine readiness
    - hybrid-routing efficiency
    - general token-savings status

## Required final report

Create:

```text
docs/reports/ari-efficiency-remediation-20260703_<HHMM>.md
```

Include:

- files changed
- routing policy implemented
- CLI changes
- documentation claims removed or corrected
- tests added
- exact test results
- benchmark v2 design
- benchmark v2 results, if executed
- direct versus indexed versus hybrid comparison
- limitations
- remaining hypotheses
- final verdicts:

```text
Core relationship engine: READY | PARTIAL | NOT READY
Selective routing workflow: READY | PARTIAL | NOT READY
General token-savings claim: VALIDATED | NOT VALIDATED | FAILED
```

## Final constraints

- Do not weaken source verification.
- Do not hide or reinterpret the failed benchmark.
- Do not make the index mandatory for simple questions.
- Do not optimize only for lower file counts while increasing tokens.
- Do not self-grade benchmark outputs.
- Do not claim READY for efficiency if the hybrid workflow has not been independently tested.
- Prefer a smaller, clearer skill over adding more graph features.
