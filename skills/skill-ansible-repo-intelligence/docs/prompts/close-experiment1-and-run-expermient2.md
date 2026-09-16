# Close Experiment 1 and Run Relationship Benchmark Experiment 2

You are working in:

```text
/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-ansible-repo-intelligence
```

Target repository:

```text
/Volumes/Data/_ansible/ansible-wifi
```

## Objective

Do not build the proposed full Playbook Execution Digest subsystem yet.

The immediate objective is to complete the existing evidence loop:

1. Fix and verify the single routing failure from Experiment 1.
2. Rerun the original 22-question direct-lookup benchmark.
3. Run a new relationship-heavy Experiment 2 using the current implementation.
4. Determine from measured evidence whether any playbook-level digest or new feature is actually required.

Follow the established development loop:

```text
small change
→ isolated benchmark
→ identify exact failure
→ smallest remediation
→ rerun benchmark
```

Do not implement speculative features before the current tool is benchmarked against relationship-heavy questions.

## Current evidence

Experiment 1 results:

```text
                          direct baseline   old indexed   new action digest
source files opened       36                29            0
input tokens              79.1k             85.4k         78.8k
correctness               22/22             21/22         21/22
unsupported claims        0                 1             2
```

The new action digest:

- opened zero source files
- used slightly fewer tokens than the direct baseline
- fixed the Asterisk source-compilation error
- kept graph growth to approximately 7.8%

The only correctness and unsupported-claim failure came from question q21, which asked about topology variable origins.

The agent incorrectly used a role action digest for a variable-origin question.

The existing tool can answer the question correctly through:

```bash
ansible-repo-intelligence query variable <name>
ansible-repo-intelligence query vars_plugin <name>
```

This is therefore a routing failure, not a parser or graph defect.

## Constraints

- Do not build a playbook catalogue.
- Do not build a new execution model.
- Do not add permanent per-playbook digest files.
- Do not add caching.
- Do not add numerous new views.
- Do not expand graph structure unless a benchmark demonstrates a specific missing relationship.
- Do not hide or reinterpret prior failed benchmark results.
- Do not self-grade benchmark outputs.
- Preserve source provenance, bounds, determinism, and security controls.
- All existing tests must remain green.

# Part 1 — Verify and harden the q21 routing fix

## Required routing rule

Variable-origin, variable-precedence, or vars-plugin questions must never be answered from the role action digest alone.

Add or verify the following rule in `SKILL.md` and any active agent-routing documentation:

```text
Questions about where a variable originates, which source supplies it, its
precedence, or whether a vars plugin injects it must route to:

1. query variable <name>
2. query vars_plugin <name>, when plugin supply is possible
3. source verification when results are dynamic, conflicting, or unresolved

Do not use role --view actions as the authoritative source for variable origin.
```

## Required question patterns

The rule must cover questions such as:

```text
Where does topology_site_id come from?
Which file defines dns_servers?
Does topology_vars.py inject this variable?
Which value wins for this variable?
What are the possible origins of this variable?
Is this variable set by inventory, role defaults, set_fact, or a vars plugin?
```

## Required deterministic routing behaviour

If a routing helper exists, ensure these patterns classify as:

```text
relationship_query
```

with a more specific subtype such as:

```text
variable_origin
variable_precedence
vars_plugin_origin
```

The result should recommend:

```text
query variable
query vars_plugin
```

The router must not execute either query automatically.

## Required tests

Add tests for:

- variable-origin question routes to `query variable`
- vars-plugin question routes to `query vars_plugin`
- precedence question does not route to role actions
- role configuration question still routes to action digest
- ambiguous variable question returns both relevant query recommendations
- routing output includes rule ID and reason
- routing does not execute tools

# Part 2 — Rerun Experiment 1

Rerun the same original 22 direct-lookup questions.

Do not modify the questions, gold answers, model, system instructions, repository revision, or grading criteria.

## Required isolation

Use independent contexts:

### Run A — direct baseline

A fresh agent uses ordinary repository navigation.

### Run B — digest workflow

A separate fresh agent uses:

- role action digest for role-local configuration questions
- variable and vars-plugin queries for variable-origin questions
- no mandatory map read
- no full graph read

### Run C — blind grader

A third independent grader:

- is not told which run is baseline or digest
- reads the gold source
- scores correctness
- counts unsupported claims

The coordinator may orchestrate the runs but must not grade them.

## Required measurements

Record:

```text
source files opened
input tokens
tool calls
time to first relevant fact
correctness
unsupported claims
query types used
map reads
full graph reads
verification-trigger count
```

## Experiment 1 clean-pass gate

The rerun passes only if:

```text
source files opened: 0 or no worse than prior digest result
input tokens: no higher than direct baseline
correctness: 22/22
unsupported claims: 0
no mandatory map read
no full graph read
q21 answered from variable or vars-plugin evidence
```

If correctness remains below 22/22:

1. identify the exact question
2. determine whether it is:
   - routing failure
   - extraction failure
   - rendering failure
   - agent reasoning failure
   - benchmark ambiguity
3. make only the smallest justified fix
4. rerun only the affected question first
5. rerun the full set only after the targeted fix passes

Do not broaden scope without evidence.

# Part 3 — Design Experiment 2

Experiment 2 must test the current tool's actual differentiators.

Do not build new playbook functionality before running this benchmark.

## Question-set composition

Create at least 24 questions:

```text
6 handler notify/listen chain questions
5 static impact or graph-reachability questions
5 variable-origin or precedence questions
3 cross-flavor inventory-scope questions
3 dynamic include / custom plugin / unresolved-reference questions
2 ordinary direct role-lookup control questions
```

## Required question properties

Every question must have:

```yaml
id: string
category: handler_chain | impact | reachability | variable_origin |
          precedence | inventory_scope | dynamic_reference | direct_control
question: string
gold:
  required_source_files: []
  required_relationships: []
  required_facts: []
  acceptable_phrasings: []
  disallowed_claims: []
  runtime_uncertainties: []
```

The gold answer must distinguish:

- statically proven facts
- inferred facts
- dynamic or unresolved behaviour
- runtime-only facts

## Suggested question types

### Handler chains

Examples:

- Which tasks can notify `Restart unbound`?
- Which handler does the Stubby template ultimately trigger?
- Which roles can cause the Asterisk service to restart?
- Does a handler use `listen`, and which notifications resolve to it?
- Are any handler notifications unresolved or ambiguous?
- Where are handlers flushed explicitly?

### Impact and reachability

Examples:

- Which playbooks can reach `roles/smc_dns/templates/unbound.conf.j2`?
- What static services may be affected if the DNS role changes?
- Which roles and tasks are reachable from a selected playbook?
- What is the static impact of changing a shared task file?
- Which templates and handlers are downstream of a role dependency?

### Variable origins and precedence

Examples:

- Where can `topology_dns_servers` originate?
- Which vars plugin supplies `topology_*` variables?
- Which definitions of a selected variable may overlap?
- Can the runtime winner be determined statically?
- Which roles consume a selected topology variable?

### Cross-flavor inventory scope

Examples:

- In which inventory flavors does a selected group appear?
- Which playbooks target groups existing in multiple flavors?
- Where do same-named groups remain flavor-scoped?

### Dynamic and unresolved relationships

Examples:

- Which includes depend on Jinja expressions?
- Which role or task targets cannot be resolved statically?
- Which custom plugin outputs are marked dynamic?

### Direct controls

Include two simple questions such as:

- How is Asterisk installed?
- Which template configures Unbound?

These controls verify that the relationship workflow does not unnecessarily invoke expensive graph traversal for local questions.

# Part 4 — Run Experiment 2

Run three separate workflows.

## Workflow A — direct navigation

A fresh agent uses ordinary repository navigation only.

It may use:

- search
- grep
- file reads
- repository navigation

It must not use:

- `.ai-context`
- ARI query
- ARI impact
- ARI explain
- generated digests

## Workflow B — always-indexed

A separate fresh agent uses ARI for every question.

It may use:

- action digest
- query
- impact
- explain
- variable and vars-plugin queries

Do not require a map read unless needed.

This workflow measures the cost of indiscriminate index use.

## Workflow C — routed hybrid

A third fresh agent follows explicit routing:

```text
direct local question
  → action digest or direct source, whichever routing policy specifies

handler/impact/reachability question
  → bounded ARI query or impact

variable-origin question
  → query variable and query vars_plugin

live operational question
  → mcp-smc when available

repository-wide unknown target
  → map or catalogue only when necessary
```

The hybrid must avoid unnecessary:

- map reads
- scans
- overlapping queries
- source reads
- full graph reads

## Blind grading

Use a fourth independent context as the blind grader.

The grader must:

- receive anonymized outputs
- not know which workflow produced each answer
- use the gold source and gold relationships
- score correctness
- count unsupported claims
- score uncertainty handling
- score relationship completeness

The coordinator must not grade.

# Part 5 — Metrics

Record per question and per category:

```text
source files opened
input tokens
output tokens
total tokens
tool calls
ARI query calls
impact calls
map reads
full graph reads
scans
time to first relevant fact
correctness
unsupported claims
relationship recall
uncertainty correctness
routing correctness
truncation events
verification-trigger count
```

## Category-level reporting

Report separately:

```text
handler chains
impact and reachability
variable origins and precedence
inventory scope
dynamic and unresolved references
direct controls
```

Do not report only one aggregate score.

## Required comparisons

```text
direct vs always-indexed
direct vs routed-hybrid
always-indexed vs routed-hybrid
```

# Part 6 — Decision gates

## Gate A — Experiment 1

Experiment 1 must achieve:

```text
correctness: 22/22
unsupported claims: 0
tokens: no higher than direct baseline
no mandatory map read
q21 routed correctly
```

If it does not, do not start speculative feature development.

## Gate B — Experiment 2 relationship efficiency

For relationship-heavy categories, routed hybrid should achieve:

```text
correctness no worse than direct
unsupported claims no worse than direct
relationship recall at least 95%
at least 50% fewer source-file opens than direct
lower token use than always-indexed
no mandatory map read
no full graph read
```

The 60% file and 40% token targets may be reported, but do not declare failure solely because an arbitrary global threshold is missed if the category-level evidence shows a meaningful, repeatable improvement.

## Gate C — direct controls

For direct/local controls:

```text
correctness parity
unsupported-claim parity
token parity or better
no unnecessary relationship queries
```

## Gate D — playbook digest decision

Do not build a Playbook Execution Digest unless Experiment 2 demonstrates at least one repeated measurable gap such as:

```text
multiple queries required to reconstruct one playbook
high token cost combining role digests
incorrect role or task execution ordering
excessive source reads for playbook-level relationships
missing pre-task/post-task/import context
inability to answer playbook-to-role reachability efficiently
```

If no such repeated gap exists:

```text
Playbook Execution Digest: DEFERRED — not justified by benchmark evidence
```

If a gap is proven, define the smallest spike that addresses only that gap.

# Part 7 — Optional playbook spike

Run this only if Gate D is triggered.

Limit the spike to:

```bash
ansible-repo-intelligence explain playbook <one-playbook> \
  --view actions
```

Use one representative multi-role playbook.

Do not initially build:

- a playbook catalogue
- permanent digest files
- caching
- multiple views
- a new graph model
- additional graph duplication
- a large test matrix

Ask three to five questions that specifically failed in Experiment 2.

Compare:

```text
current ARI queries
direct source navigation
playbook actions spike
```

Continue only if the spike materially improves:

- correctness
- relationship completeness
- source-file opens
- token use

# Part 8 — Tests

Add or update tests for:

## Routing

- role-local configuration routes correctly
- variable-origin routes to variable query
- vars-plugin origin routes to vars-plugin query
- handler-chain routes to relationship query
- impact routes to impact command
- live host scope routes to mcp-smc
- ambiguous questions return alternatives
- routing does not execute commands

## Digest and queries

- action digest remains compact
- source paths and lines are preserved
- literal operations remain accurate
- source-compilation operations are not classified as package installation
- variable-origin output includes vars-plugin supply
- bounded query limits remain enforced
- bounded impact limits remain enforced
- no mandatory map dependency

## Benchmark assets

- every question has a category
- every question has gold source files
- every question defines required relationships
- every question defines disallowed claims
- category counts meet the required composition
- blind grading runbook enforces isolation
- anonymization does not reveal workflow identity

All existing tests must remain green.

# Part 9 — Documentation updates

Update only after benchmark results are available.

Required documents:

- `SKILL.md`
- `README.md`
- `ROADMAP.md`
- `CHANGELOG.md`
- active implementation report
- benchmark reports

Document:

- corrected q21 routing
- Experiment 1 rerun result
- Experiment 2 design
- direct vs always-indexed vs hybrid results
- category-level findings
- whether playbook digest is justified
- exact remaining limitations

Do not claim:

- universal token savings
- universal superiority over direct navigation
- readiness based only on naive grep
- playbook-level benefits that were not benchmarked

# Required reports

Create:

```text
docs/reports/ari-experiment1-routing-retest-20260703_<HHMM>.md
```

and:

```text
docs/reports/ari-experiment2-relationship-benchmark-20260703_<HHMM>.md
```

## Experiment 1 report must include

- routing change
- affected files
- test results
- benchmark isolation
- full scorecard
- q21 answer and evidence
- correctness result
- unsupported-claim result
- token result
- final pass/fail verdict

## Experiment 2 report must include

- question composition
- gold-answer methodology
- workflow definitions
- isolation evidence
- blind-grading method
- per-question results
- per-category results
- aggregate results
- routing accuracy
- source-file counts
- token counts
- relationship recall
- unsupported claims
- uncertainty handling
- playbook-digest decision
- limitations

# Final verdicts

Report separate verdicts:

```text
Role action digest: READY | PARTIAL | NOT READY
Variable-origin routing: READY | PARTIAL | NOT READY
Experiment 1 direct-question efficiency: VALIDATED | PARITY | FAILED
Relationship-query correctness: READY | PARTIAL | NOT READY
Experiment 2 relationship efficiency: VALIDATED | NOT VALIDATED | FAILED
Routed hybrid workflow: READY | PARTIAL | NOT READY
Playbook Execution Digest: JUSTIFIED | DEFERRED | NOT JUSTIFIED
General token-savings claim: VALIDATED FOR SPECIFIC CLASSES | NOT VALIDATED | FAILED
```

# Final constraints

- Do not build the large playbook execution subsystem before Experiment 2.
- Do not treat one routing miss as justification for parser expansion.
- Do not alter benchmark questions during a rerun.
- Do not self-grade.
- Do not hide failed metrics.
- Do not combine category results in a way that conceals regressions.
- Do not require the map for targeted questions.
- Do not load the full graph.
- Do not execute Ansible, plugins, templates, or repository scripts.
- Preserve all security and determinism guarantees.
- Prefer the smallest evidence-backed change.