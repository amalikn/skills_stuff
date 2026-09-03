# Agent Stack — Full Project Discovery, Architecture Audit, and Improvement Review

You are acting as a senior AI-agent systems architect, software architect, security reviewer, developer-experience specialist, and repository auditor.

Your task is to perform a **complete evidence-based audit of this project**.

Do **not** start by recommending changes.

First understand the project as it actually exists.

The audit must answer:

1. What exactly has been built?
2. How does it work end-to-end?
3. What architectural principles and constraints govern it?
4. Which parts are authoritative versus derived/generated?
5. What problems is the project trying to solve?
6. What is working well?
7. What is unnecessarily complex, duplicated, fragile, inconsistent, incomplete, or poorly governed?
8. What capabilities are missing?
9. What should be improved now?
10. What should deliberately be left alone?

---

# 1. OPERATING RULES

## 1.1 Evidence first

Every material conclusion must be based on repository evidence.

For each finding, identify the supporting evidence using:

- file path
- relevant heading/function/configuration
- line range where practical

Clearly distinguish:

- **FACT** — directly demonstrated by repository contents
- **INFERENCE** — strongly implied by repository structure or behaviour
- **RECOMMENDATION** — proposed change
- **UNKNOWN** — cannot be established from available evidence

Never present assumptions as facts.

---

## 1.2 Read before judging

Do not perform a shallow README review.

Inspect the repository recursively and reconstruct the system before evaluating it.

At minimum inspect:

- root documentation
- README files
- manifest files
- personas
- skills
- orchestration logic
- scripts
- tests
- evals
- fixtures
- Justfiles / Makefiles / task runners
- installation logic
- symlinking logic
- discovery conventions
- upstream synchronisation logic
- translation/update policies
- state files
- schemas
- configuration
- templates
- examples
- generated artifacts
- caches where relevant to understanding behaviour
- Git metadata/history where useful and available

Ignore ordinary irrelevant generated dependencies such as `.git`, `node_modules`, Python virtual environments, binary caches, etc., unless their presence itself is relevant to a finding.

---

# 2. FIRST BUILD A PROJECT INVENTORY

Before analysing architecture, recursively enumerate the project.

Produce a concise structural inventory containing:

| Area | Files/components | Purpose | Authoritative? | Consumers |
|---|---|---|---|---|

Identify specifically:

- canonical source directories
- generated/derived material
- runtime-facing files
- developer tooling
- governance/documentation
- synchronization/update infrastructure
- installation infrastructure
- tests/evals
- state/cache files

Also identify anything whose ownership or authority is unclear.

---

# 3. RECONSTRUCT THE INTENDED ARCHITECTURE

From repository evidence, explain the architecture in your own words.

Determine:

### Canonical source model

- What files are canonical?
- Where should edits occur?
- What content must never be copied?
- Which locations are installed through symlinks?
- What mechanisms prevent divergence?

### Agent/persona model

Determine:

- available personas
- responsibilities of each persona
- whether personas overlap
- persona discovery conventions
- runtime compatibility assumptions
- how `orchestrator-follett` relates to `orchestrator`

### Skill model

Determine:

- number and categories of skills
- skill directory conventions
- expected skill structure
- skill metadata
- dependencies between skills
- project-agnostic versus tool-specific classifications
- duplicate or overlapping skills
- potentially obsolete skills
- missing classifications

### Orchestration model

Analyse `orchestrator` deeply.

Determine:

- how a task enters the system
- how specialists are selected
- how many specialists may be used
- how evidence is separated from inference
- how disagreements are handled
- how final synthesis happens
- whether routing is deterministic or heuristic
- whether tool-specific constraints affect routing
- failure/fallback behaviour
- how specialist proliferation is controlled

Treat the orchestrator as a critical architectural component, not simply another skill.

---

# 4. TRACE THE SYSTEM END-TO-END

Create concrete execution traces for at least these scenarios:

### Scenario A — normal user task

User → orchestrator → specialist selection → skills/personas → synthesis → response

### Scenario B — direct specialist invocation

User → specialist/skill → output

Explain when this is appropriate versus orchestration.

### Scenario C — global installation

Canonical repository → installer → symlinks → Claude Code / Codex / `.agents` compatible runtime

Trace:

- commands
- source paths
- destination paths
- collision behaviour
- overwrite protection
- idempotency
- error handling
- rollback/recovery considerations

### Scenario D — project-local installation/discovery

Trace how a project consumes Agent Stack without compromising canonical ownership.

### Scenario E — upstream refresh

Official Auto Company upstream →

fetch/mirror →

comparison →

classification →

translation/manual review where required →

safe application →

state update/report

Determine every decision branch.

---

# 5. AUDIT THE UPSTREAM SYNCHRONISATION SYSTEM

This area requires a separate deep review.

Inspect:

- `scripts/sync_auto_company.py`
- `manifest.yaml`
- `upstream-state.json`
- translation policy
- translation brief generation
- update reports
- cache/mirror handling
- hash tracking
- safe-add / safe-replace rules
- manual-merge rules
- removal review
- baseline recording

Determine whether the implementation actually satisfies the stated policy.

Test conceptually or execute non-destructive commands where safe.

Specifically inspect for:

- accidental source overwrite
- incorrect canonical hash handling
- stale upstream state
- unsafe removal
- translation drift
- changed-language edge cases
- file rename handling
- path traversal possibilities
- malformed upstream data
- partial update failures
- interrupted execution
- repeated-run/idempotency behaviour
- upstream repository compromise assumptions
- TOCTOU issues
- cache poisoning possibilities
- manual-merge ambiguity

Identify where policy and implementation diverge.

---

# 6. AUDIT THE INSTALLATION MODEL

Inspect every installation path.

Determine compatibility with:

- Claude Code
- Codex
- runtimes using `~/.agents/skills`
- project-local `.agents/skills`
- persona-aware runtimes

Evaluate:

### Correctness
Does each runtime actually receive what it expects?

### Canonical ownership
Can installed material diverge from source?

### Collision handling
What happens when destinations already exist?

### Upgrade behaviour
What happens after repository updates?

### Broken symlinks
How are moved/deleted source directories handled?

### Portability
Does the project make unnecessary assumptions about:

- `/Volumes/Data`
- macOS
- shell
- GNU/BSD utilities
- Python version
- filesystem permissions

### Developer experience
Is global installation understandable and reversible?

---

# 7. PERSONA AUDIT

Inspect all personas individually.

For each persona create:

| Persona | Intended role | Unique value | Overlap | Risks | Recommendation |
|---|---|---|---|---|---|

Look for:

- overlapping responsibility
- vague boundaries
- conflicting instructions
- unnecessary personas
- missing personas
- excessively broad personas
- personas that should instead be skills
- skills that should perhaps be personas
- orchestration ambiguity caused by persona definitions

Do not recommend consolidation merely because two personas share terminology.

Only recommend consolidation when their **operational responsibilities materially overlap**.

---

# 8. SKILL LIBRARY AUDIT

Inspect every skill.

Create a skill inventory:

| Skill | Category | Purpose | Inputs | Outputs | Dependencies | Overlap | Quality |
|---|---|---|---|---|---|---|---|

Assess:

### Skill quality

- clear purpose
- trigger conditions
- boundaries
- workflow
- expected inputs
- expected outputs
- failure handling
- tool assumptions
- evidence requirements
- interaction with orchestrator

### Skill architecture

Look for:

- duplicated instructions
- contradictory instructions
- common logic that should be factored out
- inappropriate cross-skill coupling
- missing shared primitives
- excessive context size
- overly verbose skills
- hidden runtime assumptions
- stale references
- paths that no longer exist
- inconsistent terminology

### Skill discoverability

Can an orchestrator reliably tell:

- when a skill applies?
- when it does not apply?
- which of two similar skills should win?
- whether multiple skills should be composed?

---

# 9. ORCHESTRATOR AUDIT

Treat this as one of the highest-priority sections.

Determine whether `orchestrator` can reliably act as the project's **single normal entry point**.

Audit:

### Routing
- specialist selection
- skill selection
- minimal-role principle
- task decomposition
- direct-vs-multi-specialist choices

### Synthesis
- evidence aggregation
- disagreement handling
- contradiction detection
- confidence
- unresolved questions
- provenance

### Context management
- unnecessary specialist activation
- duplicated context
- token inefficiency
- repeated analysis
- recursion risks
- context pollution

### Failure behaviour
What happens if:

- no specialist fits
- several specialists fit equally
- specialists disagree
- a specialist fails
- repository knowledge is insufficient
- evidence conflicts with user assumptions

### Governance
Is orchestration behaviour encoded strongly enough to remain stable across different LLMs?

Identify where behaviour relies on model intelligence rather than explicit project design.

---

# 10. SAFETY AND HUMAN-CONTROL AUDIT

The project intentionally excludes autonomous/no-human-gate patterns.

Verify that this principle is consistently enforced.

Look for accidental introduction of:

- unattended background execution
- destructive automation
- automatic decisions with material consequences
- unrestricted recursive agents
- implicit persistence
- automatic upstream adoption
- automatic deletion
- automatic translation replacement
- silent modification of project-local content

Classify findings:

- safe by design
- safe by convention only
- potentially unsafe
- contradictory

---

# 11. GOVERNANCE AUDIT

Determine whether the repository clearly answers:

- Who owns canonical content?
- What may be changed automatically?
- What requires human approval?
- How are upstream changes incorporated?
- How are translations maintained?
- How are skills deprecated?
- How are personas deprecated?
- How are breaking changes handled?
- How are runtime compatibility changes handled?
- How are version migrations managed?
- What constitutes a release?
- How is regression prevented?

Identify governance rules that exist only implicitly.

---

# 12. TEST AND EVAL AUDIT

Find all existing:

- tests
- evals
- smoke tests
- linting
- schema validation
- installer tests
- sync tests
- routing tests
- regression tests

Determine coverage gaps.

Pay particular attention to behavioural evals.

The project should ideally be capable of answering questions such as:

> Given this task, did the orchestrator select the correct specialist(s)?

> Did it avoid unnecessary specialists?

> Did it distinguish evidence from inference?

> Did it expose disagreement instead of hiding it?

> Did it use project instructions rather than generic model behaviour?

> Did an upstream change get classified correctly?

> Did an installer avoid overwriting an existing local entry?

Assess whether current evals provide this protection.

If not, propose a minimum viable eval suite.

---

# 13. DOCUMENTATION AUDIT

Check whether documentation accurately matches implementation.

Look for:

- README drift
- undocumented behaviour
- commands that no longer work
- inaccurate path assumptions
- undocumented dependencies
- duplicated documentation
- architecture knowledge spread across too many files
- missing operator procedures
- missing troubleshooting guidance

Do not recommend documentation merely for completeness.

Recommend it only where documentation would materially reduce operational ambiguity.

---

# 14. PORTABILITY AND RUNTIME COMPATIBILITY

Assess how strongly the repository depends on the author's current environment.

Identify:

- hard-coded paths
- filesystem assumptions
- shell assumptions
- OS assumptions
- Python assumptions
- symlink assumptions
- permission assumptions
- runtime-specific conventions

Classify each as:

- intentional
- harmless
- portability limitation
- architectural defect

---

# 15. COMPLEXITY / OVERENGINEERING AUDIT

Explicitly search for unnecessary complexity.

Ask:

- Could the same guarantees be achieved more simply?
- Is there infrastructure supporting hypothetical rather than real requirements?
- Are multiple abstractions solving essentially the same problem?
- Is the manifest carrying information derivable elsewhere?
- Are state files justified?
- Is translation machinery appropriately scoped?
- Is the number of personas justified?
- Is the number of skills justified?
- Is there excessive governance for the project's scale?
- Conversely, are critical controls missing because the design assumes disciplined human behaviour?

Do not equate sophistication with overengineering.

Identify concrete simplification opportunities only when they preserve required behaviour.

---

# 16. CAPABILITY GAP ANALYSIS

After understanding the existing system, identify capabilities that would materially improve Agent Stack.

Consider, but do not automatically recommend:

- dependency metadata between skills
- skill capability taxonomy
- explicit skill contracts
- machine-readable trigger conditions
- routing evals
- skill quality gates
- versioning
- changelog generation
- compatibility matrix
- health-check command
- install-status command
- uninstall command
- doctor/diagnostic command
- dependency validation
- broken-symlink detection
- semantic validation of skills
- duplicate detection
- prompt regression testing
- cross-runtime conformance tests
- migration tooling
- local project overrides
- project-specific skill extension mechanism
- composition rules
- provenance metadata
- specialist confidence
- specialist disagreement protocol

Only propose items justified by actual gaps.

---

# 17. COMPARE INTENT TO IMPLEMENTATION

Build this table:

| Intended principle | Evidence of intent | Actual implementation | Alignment | Gap |
|---|---|---|---|---|

At minimum evaluate:

- one canonical source
- symlink-only normal installation
- no copying
- orchestrator as normal entry point
- smallest useful specialist set
- evidence vs inference separation
- disagreement surfacing
- no autonomous daemon
- human approval for material changes
- safe upstream update handling
- preservation of canonical English material
- compatibility across agent runtimes

This section is essential.

---

# 18. FINDINGS CLASSIFICATION

Classify every meaningful issue as:

### P0 — Critical
Can corrupt canonical material, cause unsafe behaviour, fundamentally break architecture, or make the repository unreliable.

### P1 — High
Material architectural flaw, update/install correctness problem, major orchestration failure, serious governance gap.

### P2 — Medium
Meaningful maintainability, usability, portability, testing, or design weakness.

### P3 — Low
Quality improvement, cleanup, documentation refinement, developer-experience enhancement.

Do not inflate severity.

---

# 19. RECOMMENDATIONS

Recommendations must be concrete.

For each recommendation provide:

| Priority | Recommendation | Problem solved | Benefit | Cost | Risk | Files affected |
|---|---|---|---|---|---|---|

Also classify each recommendation:

- **DO NOW**
- **DO NEXT**
- **OPTIONAL**
- **DO NOT DO**

The last category is important.

Explicitly identify attractive ideas that would add complexity without sufficient value.

---

# 20. PROPOSED TARGET ARCHITECTURE

Only after completing the audit, describe the architecture you believe Agent Stack should converge toward.

Prefer evolutionary improvement over rewriting.

Show:

- canonical repository layout
- persona layer
- skill layer
- orchestration layer
- runtime integration layer
- upstream-sync layer
- testing/eval layer
- governance layer

For every structural change explain why the existing structure is insufficient.

If the existing design is already good, say so.

Do not redesign for the sake of redesign.

---

# 21. IMPLEMENTATION ROADMAP

Produce a phased remediation plan.

### Phase 0 — protect existing behaviour
Regression tests/evals before modifications.

### Phase 1 — correctness
P0/P1 issues.

### Phase 2 — architecture
Structural improvements.

### Phase 3 — quality
Tests, evals, diagnostics, documentation.

### Phase 4 — optional evolution
Capabilities that can wait until justified.

Each task should specify:

- affected files
- expected change
- dependency
- acceptance criteria

---

# 22. REQUIRED FINAL REPORT

Return the audit using exactly these major sections:

## 1. Executive Assessment

Include one overall judgement:

- EXCELLENT
- SOUND
- SOUND WITH MATERIAL GAPS
- NEEDS REWORK
- FUNDAMENTALLY FLAWED

Explain why.

## 2. What Agent Stack Is

Explain the project based solely on repository evidence.

## 3. Current Architecture

Describe the actual architecture.

## 4. Repository Inventory

Important components and ownership.

## 5. End-to-End Behaviour

Normal orchestration, direct use, installation, upstream refresh.

## 6. What Is Designed Well

Specific strengths.

## 7. Architectural Findings

All architectural weaknesses.

## 8. Orchestrator Findings

Deep review of orchestration.

## 9. Persona Findings

Persona-by-persona assessment.

## 10. Skill Findings

Skill library assessment.

## 11. Installation and Runtime Compatibility

Claude Code, Codex, `.agents`, project-local use.

## 12. Upstream Sync and Translation Review

Detailed sync audit.

## 13. Safety and Governance

Human control, canonical ownership, destructive-operation protection.

## 14. Testing and Eval Coverage

Existing coverage and missing protections.

## 15. Portability and Operational Risks

Environment/runtime dependencies.

## 16. Complexity and Duplication

What should be simplified and what complexity is justified.

## 17. Missing Capabilities

Evidence-backed capability gaps.

## 18. Intent-vs-Implementation Matrix

Required comparison table.

## 19. Prioritised Findings

P0–P3 table.

## 20. Recommendations

DO NOW / DO NEXT / OPTIONAL / DO NOT DO.

## 21. Proposed Target Architecture

Evolutionary architecture.

## 22. Remediation Roadmap

Sequenced implementation plan.

## 23. Final Verdict

Answer:

1. Is Agent Stack architecturally sound?
2. Is the orchestrator model appropriate?
3. Are personas and skills separated correctly?
4. Is canonical-source ownership properly protected?
5. Is upstream synchronisation safe?
6. Is the project unnecessarily complex?
7. What are the three highest-value improvements?
8. What should explicitly **not** be changed?

---

# 23. IMPORTANT CONSTRAINTS

Do not:

- rewrite files during this audit
- delete anything
- modify repository state
- apply upstream changes
- execute destructive commands
- install anything globally
- alter symlinks
- redesign the project before understanding it
- recommend frameworks merely because they are fashionable
- reward complexity
- invent requirements not demonstrated by the repository

You MAY run read-only or non-destructive diagnostic commands where useful.

If command execution could alter state, inspect the implementation instead.

---

# 24. AUDIT STANDARD

The objective is not to find as many problems as possible.

The objective is to determine whether the current project is:

**coherent, maintainable, safe, portable, testable, extensible, and appropriately simple for its intended purpose.**

Preserve good architecture.

Remove accidental complexity.

Add controls only where they solve demonstrated problems.

Every proposed change must earn its complexity.