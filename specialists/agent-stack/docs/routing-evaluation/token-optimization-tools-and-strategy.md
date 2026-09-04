Title: Token-efficient AI agent architecture
Category: evidence-and-proposal
Status: current
Scope: An architecture and implementation guide for reducing token consumption in multi-agent systems (Claude Code, Codex, local/API models, reusable skills, project knowledge) without losing
  requirements, knowledge, or decision quality; every named tool or framework has been source-verified rather than repeated from the original brief
Last reviewed: 20260904_0815
Summary: Token efficiency should target unnecessary context injection, not the underlying information — preserve intelligence in storage, minimise only what is active in the context window. All 9
  cited tools/frameworks are confirmed real and active; one earlier draft's reference ("BM629 token-optimization skill") was removed after returning zero search results and could not be verified;
  Zep's cited repository is an examples/integrations repo, not its core engine, which is now a hosted product. Each option now also carries an adaptation-feasibility verdict against Agent Stack's own
  architecture — only two are worth adopting as-is (Token Optimizer as an external audit, Skill Optimizer as a cautious pilot); most of the memory frameworks conflict with the safety model's
  no-implicit-persistent-state and no-autonomy rules rather than fitting a static, runtime-free prompt library.

# Token-Efficient AI Agent Architecture

## Reducing Context Cost Without Losing Requirements, Knowledge, or Decision Quality

**Primary use case:** Multi-agent systems using Claude Code, Codex, local/API models, reusable skills, project knowledge, and long-running technical/business work
**Objective:** Reduce token consumption and context waste while preserving requirements, constraints, evidence, project intelligence, and auditability.

## Contents

- [Reducing Context Cost Without Losing Requirements, Knowledge, or Decision Quality](#reducing-context-cost-without-losing-requirements-knowledge-or-decision-quality)
- [1. Executive Summary](#1-executive-summary)
- [2. Design Objective](#2-design-objective)
- [3. Information Classification Model](#3-information-classification-model)
- [4. Recommended Context Architecture](#4-recommended-context-architecture)
- [5. Highest-Value Optimisation Techniques](#5-highest-value-optimisation-techniques)
- [6. Progressive Disclosure for Skills](#6-progressive-disclosure-for-skills)
- [7. Retrieval-Based Knowledge Loading](#7-retrieval-based-knowledge-loading)
- [8. Memory Tiering](#8-memory-tiering)
- [9. Prompt Caching](#9-prompt-caching)
- [10. Tool Output Offloading](#10-tool-output-offloading)
- [11. Prompt Optimisation](#11-prompt-optimisation)
- [12. Skill Compression](#12-skill-compression)
- [13. Lossy Prompt Compression](#13-lossy-prompt-compression)
- [14. Recommended Tool Stack](#14-recommended-tool-stack)
- [15. Recommended Implementation Sequence](#15-recommended-implementation-sequence)
- [16. Validation Requirements](#16-validation-requirements)
- [17. Recommended Guardrails](#17-recommended-guardrails)
- [18. Target Architecture for Agent Stack](#18-target-architecture-for-agent-stack)
- [19. What Not to Optimise First](#19-what-not-to-optimise-first)
- [20. Recommended Decision](#20-recommended-decision)
- [21. Reference Projects](#21-reference-projects)
- [22. Source Verification and Adaptation Feasibility](#22-source-verification-and-adaptation-feasibility)

---

## 1. Executive Summary

Token efficiency in an AI agent system should not be approached as a simple prompt-compression problem.

The safest and most effective strategy is to reduce **unnecessary context injection**, not the underlying information itself. In other words:

> **Preserve intelligence in storage; minimise only what must be present in the active context window.**

For a system such as an Agent Stack, the largest avoidable token costs typically come from:

- repeatedly loading full persona definitions;
- loading complete `SKILL.md` files when only one procedure is needed;
- injecting entire project knowledge bases;
- carrying large conversation histories forward;
- retaining verbose tool output;
- repeating stable system instructions;
- duplicating routing, governance, and safety instructions across several layers.

The recommended architecture therefore uses five mechanisms:

1. **Context measurement and auditing**
2. **Progressive disclosure**
3. **Retrieval-based knowledge loading**
4. **Lossless caching and external state**
5. **Selective compression only for low-risk dynamic content**

Lossy compression should be the final optimisation layer, not the first.

---

## 2. Design Objective

The system should optimise for:

```text
minimum active context
while preserving
maximum recoverable intelligence
```

This requires distinguishing between:

- information that must always remain verbatim;
- information that must remain available but does not need to be loaded continuously;
- information that can be summarised or compressed;
- information that should be stored externally and reloaded only when needed.

A token-efficient architecture should therefore satisfy the following principle:

> **Nothing important is discarded merely to reduce prompt size.**

Information may leave the active prompt, but it should remain recoverable from an authoritative source.

---

## 3. Information Classification Model

All context should be classified before optimisation.

### 3.1 Contractual Information

This includes:

- safety constraints;
- mandatory requirements;
- exact formulas;
- routing invariants;
- approval gates;
- legal/compliance conditions;
- configuration schemas;
- hard thresholds;
- accepted architectural decisions;
- explicit user instructions.

**Treatment:** Never lossy-compress.

These should either remain verbatim in the active prompt or be retrieved verbatim when required.

---

### 3.2 Operational Knowledge

This includes:

- project state;
- technical documentation;
- historical decisions;
- architecture notes;
- supplier information;
- research;
- business assumptions;
- implementation guidance;
- previous findings.

**Treatment:** Preserve in full externally, retrieve only relevant sections.

This class is usually the largest source of safe token savings.

---

### 3.3 Procedural Knowledge

This includes:

- skill instructions;
- troubleshooting procedures;
- analysis methods;
- review checklists;
- workflow templates;
- implementation playbooks.

**Treatment:** Use progressive disclosure.

The model should initially receive only enough metadata to decide whether the procedure is relevant.

---

### 3.4 Ephemeral Context

This includes:

- terminal output;
- large JSON responses;
- logs;
- search-result dumps;
- test output;
- diffs;
- intermediate calculations;
- temporary reasoning artifacts.

**Treatment:** Aggressively compact or offload after extracting durable evidence.

The raw source should remain retrievable where necessary.

---

## 4. Recommended Context Architecture

A practical architecture is:

```text
                     USER TASK
                         │
                         ▼
                Context Requirement Check
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  Core Contract     Skill Metadata     Project Retrieval
  always loaded     lightweight         selective
        │                │                │
        └────────────┬───┴────────────────┘
                     ▼
              Active Task Context
                     │
                     ▼
                  Model
                     │
                     ▼
                Tool Execution
                     │
                     ▼
         Result Extraction / Compaction
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   Active Summary        External Raw Evidence
```

The key point is that the active prompt becomes a **working set**, not a complete knowledge dump.

---

## 5. Highest-Value Optimisation Techniques

### 5.1 Context Auditing

Before optimising prompts, measure where tokens are being consumed.

A useful audit should identify:

- static system instructions;
- repeated persona text;
- repeated routing text;
- loaded skill bodies;
- project knowledge;
- tool schemas;
- tool responses;
- conversation history;
- duplicated instructions;
- generated summaries.

This establishes a token budget by category.

### Recommended Tool

**Token Optimizer** GitHub: https://github.com/alexgreensh/token-optimizer

Best use:

- Claude Code configurations;
- Codex configurations;
- prompt overhead analysis;
- redundant context discovery;
- compaction opportunities.

### Why it matters

Without measurement, optimisation tends to target visible prompt text rather than the largest actual token consumers.

---

## 6. Progressive Disclosure for Skills

A large `SKILL.md` file should not automatically become part of every prompt.

Instead, each skill should be divided into two layers.

### Layer A — Discovery Metadata

Small and always available:

```yaml
name:
description:
use_when:
do_not_use_when:
capabilities:
runtime:
```

### Layer B — Full Procedure

Loaded only after the skill is selected:

```text
methodology
decision rules
examples
edge cases
formulas
references
runtime guidance
```

A further optimisation is to break large skills into referenced subdocuments:

```text
skill/
├── SKILL.md
└── references/
    ├── methodology.md
    ├── formulas.md
    ├── examples.md
    ├── edge-cases.md
    └── implementation.md
```

The active context can then load only the required section.

### Expected Benefit

This can remove a large amount of repeated procedural text without deleting any capability.

---

## 7. Retrieval-Based Knowledge Loading

Retrieval is generally safer than compression.

Instead of sending:

```text
entire project knowledge base
```

the system should send:

```text
only the sections relevant to the current question
```

The original corpus remains authoritative and complete.

### Retrieval Pipeline

```text
Task
 ↓
query expansion
 ↓
hybrid retrieval
 ↓
reranking
 ↓
relevance threshold
 ↓
selected excerpts
 ↓
model
```

A strong implementation should combine:

- lexical search such as BM25;
- semantic/vector search;
- optional graph relations;
- metadata filters;
- reranking.

### Recommended Tools

#### context-mem
GitHub: https://github.com/JubaKitiashvili/context-mem

Relevant characteristics:

- persistent memory;
- hybrid retrieval;
- graph-oriented context;
- local operation;
- MCP compatibility;
- decision-trail reconstruction.

#### Mem0
GitHub: https://github.com/mem0ai/mem0

Useful for:

- persistent user/project memory;
- selective memory retrieval;
- long-running agents.

#### Letta
GitHub: https://github.com/letta-ai/letta

Useful when memory itself is a first-class agent architecture concern.

#### Zep
GitHub: https://github.com/getzep/zep

Useful for temporal or relationship-oriented memory.

---

## 8. Memory Tiering

A useful memory model is:

### Tier 0 — Core Context

Always loaded.

Examples:

- safety rules;
- project identity;
- current objective;
- critical constraints;
- authoritative instruction hierarchy.

Target: very small.

---

### Tier 1 — Current Working State

Loaded for the active session or task.

Examples:

- current milestone;
- active decisions;
- unresolved blockers;
- immediate task dependencies.

---

### Tier 2 — Project Knowledge

Retrieved on demand.

Examples:

- architecture;
- research;
- past decisions;
- business assumptions;
- technical references.

---

### Tier 3 — Archive

Not routinely loaded.

Examples:

- old conversation logs;
- completed investigations;
- superseded proposals;
- raw historical data;
- tool transcripts.

This model allows complete retention without constant prompt injection.

---

## 9. Prompt Caching

Prompt caching is one of the safest token optimisations because it does not remove information.

Stable context should be placed before variable task content.

Recommended layout:

```text
STABLE PREFIX

system instructions
routing contract
tool definitions
shared project rules
core safety constraints

---------------------

VARIABLE CONTEXT

current task
retrieved knowledge
tool output
temporary state
```

Where the model provider supports prefix caching, repeated stable content can be processed more efficiently.

### Key Advantage

```text
same information
same behavior
less repeated processing
```

### Related Project

Prompt Cache research implementation: https://github.com/yale-sys/prompt-cache

Provider-native caching should normally be preferred where available.

---

## 10. Tool Output Offloading

Tool results frequently become one of the largest sources of wasted context.

Common examples:

- command output;
- Git diffs;
- test logs;
- search responses;
- API JSON;
- build output;
- database dumps.

The model rarely needs the entire payload after the immediate operation.

### Recommended Pattern

```text
raw result
   ↓
extract:
- conclusion
- errors
- evidence
- changed paths
- identifiers
- values needed later
   ↓
store compact result in context
   ↓
retain raw source externally
```

The raw output should remain available for reinspection.

### Principle

> **Remove data from the prompt, not from the evidence store.**

---

## 11. Prompt Optimisation

Once unnecessary context loading is eliminated, static instructions can be optimised.

### Recommended Tool

**Sentry Prompt Optimizer** Repository: https://github.com/getsentry/skills

The important design principle is that prompt optimisation should be **eval-backed**.

An instruction should only be removed when tests show that removing it does not materially degrade behavior.

### Suitable Targets

- duplicated instructions;
- repeated examples;
- explanatory prose that does not affect output;
- redundant routing descriptions;
- duplicated safety wording already enforced elsewhere.

### Unsuitable Targets

- exact decision rules;
- safety constraints;
- thresholds;
- schemas;
- legal/financial formulas.

---

## 12. Skill Compression

If skill bodies remain too large after progressive disclosure, controlled optimisation can be applied.

### Recommended Tool

**Skill Optimizer** GitHub: https://github.com/FreeAutomation-Tech/skill-optimizer

Use only where:

- the original skill remains preserved;
- an eval suite exists;
- the optimised version can be compared against the original;
- critical domain skills are excluded initially.

### Recommended Pilot

Test on 3–5 generic skills before touching:

- networking-critical procedures;
- financial rules;
- governance;
- import/compliance knowledge;
- safety-related skills.

---

## 13. Lossy Prompt Compression

Lossy compression should be considered only after the preceding layers are implemented.

### Recommended Tool

**Microsoft LLMLingua** GitHub: https://github.com/microsoft/LLMLingua

Relevant variants include:

- LLMLingua;
- LLMLingua-2;
- LongLLMLingua.

### Appropriate Content

- large research extracts;
- verbose retrieved documents;
- old conversation history;
- tool output;
- background explanatory prose.

### Content That Should Not Be Compressed

```text
safety rules
routing invariants
legal requirements
financial formulas
configuration schemas
approval gates
exact thresholds
user constraints
critical accepted decisions
```

---

## 14. Recommended Tool Stack

A practical stack for a multi-agent environment is:

### Layer 1 — Measurement

**Token Optimizer**

Purpose:

- identify real token consumers;
- quantify context overhead;
- detect repeated material.

---

### Layer 2 — Static Prompt Optimisation

**Sentry Prompt Optimizer**

Purpose:

- eliminate redundant static instructions;
- retain only instructions that demonstrate value under eval.

---

### Layer 3 — Knowledge Retrieval

Evaluate:

- context-mem;
- Mem0;
- Letta;
- Zep.

Purpose:

- preserve project intelligence externally;
- load only relevant information.

---

### Layer 4 — Skill Optimisation

**Skill Optimizer**

Purpose:

- reduce oversized procedural skill bodies;
- verify retained capability using tests.

---

### Layer 5 — Dynamic Context Compression

**LLMLingua / LLMLingua-2 / LongLLMLingua**

Purpose:

- reduce large dynamic context when retrieval and offloading are insufficient.

---

## 15. Recommended Implementation Sequence

The safest implementation sequence is:

### Phase 1 — Measure

Establish:

- average prompt size;
- tokens by context category;
- repeated static-token percentage;
- tool-output contribution;
- average skill payload;
- knowledge payload.

---

### Phase 2 — Remove Duplication

Eliminate:

- duplicate routing instructions;
- duplicated persona content;
- duplicated governance prose;
- repeated static examples.

Do not compress semantic requirements yet.

---

### Phase 3 — Introduce Progressive Disclosure

Convert skills and personas into:

```text
metadata first
full content on selection
references on demand
```

---

### Phase 4 — Introduce Retrieval

Move project knowledge out of always-loaded context.

Retrieve only:

- relevant decisions;
- relevant facts;
- relevant procedures;
- relevant evidence.

---

### Phase 5 — Offload Tool Output

Store raw output externally.

Keep only structured results in the active prompt.

---

### Phase 6 — Enable Caching

Arrange stable context as a reusable prompt prefix where supported.

---

### Phase 7 — Optimise Static Prompts

Use eval-backed optimisation.

---

### Phase 8 — Add Selective Compression

Apply LLMLingua-style compression only to low-risk dynamic content.

---

## 16. Validation Requirements

Token optimisation should be treated as an engineering change, not a writing exercise.

Each optimisation should be measured against:

| Metric                  | Purpose                                  |
| ----------------------- | ---------------------------------------- |
| Input-token reduction   | Actual efficiency gain                   |
| Output correctness      | Ensure answer quality remains intact     |
| Requirement recall      | Ensure mandatory requirements survive    |
| Constraint adherence    | Detect lost rules                        |
| Retrieval recall        | Ensure relevant knowledge is found       |
| False retrieval rate    | Prevent irrelevant context injection     |
| Tool-selection accuracy | Ensure capability routing remains intact |
| Decision consistency    | Detect semantic drift                    |
| Latency                 | Measure runtime benefit                  |
| Cost                    | Measure actual financial benefit         |

---

## 17. Recommended Guardrails

### Guardrail 1 — Never overwrite the original

Compressed or optimised content should be derived from an authoritative original.

---

### Guardrail 2 — Always preserve provenance

Retrieved or compressed context should retain:

- source document;
- section;
- version/hash where practical;
- timestamp where relevant.

---

### Guardrail 3 — Critical rules remain verbatim

No lossy transformation for contractual information.

---

### Guardrail 4 — Retrieval failure must be visible

The system should distinguish:

```text
no relevant knowledge exists
```

from:

```text
retrieval failed to find relevant knowledge
```

---

### Guardrail 5 — Compression is reversible

The model should be able to request the original source when more detail is needed.

---

## 18. Target Architecture for Agent Stack

A token-efficient Agent Stack should ideally evolve toward:

```text
                         USER
                          │
                          ▼
                    ORCHESTRATOR
                          │
                ┌─────────┴─────────┐
                │                   │
         lightweight routing   context planner
                │                   │
                ▼                   ▼
          persona metadata    project retrieval
          skill metadata      memory retrieval
                │                   │
                └─────────┬─────────┘
                          ▼
                    ACTIVE CONTEXT
                          │
                          ▼
                         LLM
                          │
                          ▼
                     TOOL LAYER
                          │
                          ▼
                 result compaction
                    /          \
                   /            \
          active summary      raw evidence store
```

The Agent Stack would retain all of its intelligence, while the model only receives the subset needed for the current task.

---

## 19. What Not to Optimise First

Avoid beginning with:

- arbitrary prompt shortening;
- summarising every knowledge file;
- compressing safety/governance rules;
- deleting detailed skill instructions;
- replacing exact project state with generic summaries;
- reducing context simply to hit a target percentage.

These approaches optimise token count rather than system quality.

---

## 20. Recommended Decision

For this environment, the priority should be:

1. **Measure token usage**
2. **Implement progressive disclosure**
3. **Add retrieval-based project memory**
4. **Offload verbose tool output**
5. **Use caching where supported**
6. **Optimise static prompt contracts**
7. **Apply lossy compression only where evidence shows it is safe**

The key architectural principle is:

> **Preserve all intelligence, but do not keep all intelligence active at the same time.**

That approach reduces token consumption while maintaining requirements, evidence, knowledge, and decision quality.

---

## 21. Reference Projects

| Project                          | Repository                                             |
| -------------------------------- | ------------------------------------------------------ |
| Token Optimizer                  | https://github.com/alexgreensh/token-optimizer         |
| Sentry Skills / Prompt Optimizer | https://github.com/getsentry/skills                    |
| Microsoft LLMLingua              | https://github.com/microsoft/LLMLingua                 |
| context-mem                      | https://github.com/JubaKitiashvili/context-mem         |
| Mem0                             | https://github.com/mem0ai/mem0                         |
| Letta                            | https://github.com/letta-ai/letta                      |
| Zep                              | https://github.com/getzep/zep                          |
| Skill Optimizer                  | https://github.com/FreeAutomation-Tech/skill-optimizer |
| Prompt Cache                     | https://github.com/yale-sys/prompt-cache               |

## 22. Source Verification and Adaptation Feasibility

Every repository named in this document, plus one named in an earlier draft, was checked directly against GitHub — description, license, star count, and last-push date pulled live, not repeated from
the brief that produced the first version of this document. The feasibility column is a judgement against Agent Stack's own architecture (a static, symlink-installed prompt layer with no runtime of
its own, and a safety model that excludes autonomous loops and implicit persistent state), not a general quality rating of the project.

| Project                                 | Verified      | License     | Stars              | Feasibility for Agent Stack | Notes                                                                     |
| --------------------------------------- | ------------- | ----------- | ------------------ | --------------------------- | ------------------------------------------------------------------------- |
| Token                                   | INSTALLED     | PolyForm    | 2,146              | ADOPTED, verified           | Installed and verified on this machine 2026-09-04. Claude Code:           |
|   Optimizer                             |               |   NC 1.0    |                    |                             |   `claude plugin marketplace add alexgreensh/token-optimizer` +           |
|   (alexgreensh/token-optimizer)         |               |             |                    |                             |   `claude plugin install token-optimizer@alexgreensh-token- optimizer`    |
|                                         |               |             |                    |                             |   (scope user, so it applies to every session, not just this repo).       |
|                                         |               |             |                    |                             |   `claude plugin details` confirms all 10 declared hooks (PreToolUse,     |
|                                         |               |             |                    |                             |   PreCompact, SessionStart, Stop, SessionEnd, StopFailure,                |
|                                         |               |             |                    |                             |   UserPromptSubmit, PostToolUse, PostCompact, CwdChanged) are registered  |
|                                         |               |             |                    |                             |   immediately — no separate setup step was needed, contrary to the        |
|                                         |               |             |                    |                             |   README's "run /token-optimizer once" instruction. Real cost, measured   |
|                                         |               |             |                    |                             |   not estimated: ~406 tokens always-on per session, up to ~7.1k when its  |
|                                         |               |             |                    |                             |   own audit skill actually fires.                                         |
|                                         |               |             |                    |                             | Codex: `codex plugin marketplace add alexgreensh/token-optimizer` +       |
|                                         |               |             |                    |                             |   `codex plugin add token-optimizer@alexgreensh-token-optimizer`, then a  |
|                                         |               |             |                    |                             |   separate one-time hook-wiring step from the installed plugin's own      |
|                                         |               |             |                    |                             |   cache path —                                                            |
|                                         |               |             |                    |                             |   `TOKEN_OPTIMIZER_RUNTIME=codex python3 skills/token-optimizer/\`        |
|                                         |               |             |                    |                             |   `scripts/\` `measure.py codex-install --global --profile balanced` —    |
|                                         |               |             |                    |                             |   which writes to `~/.codex/hooks.json` directly (Codex's own docs:       |
|                                         |               |             |                    |                             |   "loads for all projects regardless of trust level"). Verified with the  |
|                                         |               |             |                    |                             |   tool's own `codex-doctor`: 14 OK, 2 WARN (both benign — an existing     |
|                                         |               |             |                    |                             |   custom status line was left alone rather than overwritten, and          |
|                                         |               |             |                    |                             |   per-project hooks are optional once global hooks exist), 0 FAIL.        |
|                                         |               |             |                    |                             | Before running anything: read the 1,639-line `install.sh` and confirmed   |
|                                         |               |             |                    |                             |   it has no `--codex` path at all — Codex is handled entirely by its own  |
|                                         |               |             |                    |                             |   native `codex plugin` CLI plus one Python module (`codex_install.py`,   |
|                                         |               |             |                    |                             |   577 lines), which was read in full and checked for network calls or     |
|                                         |               |             |                    |                             |   credential access (none found) before executing. Neither install used   |
|                                         |               |             |                    |                             |   the raw `install.sh` script; both used each CLI's own trusted           |
|                                         |               |             |                    |                             |   plugin manager.                                                         |
|                                         |               |             |                    |                             | This plugin ships as a Claude Code AND Codex plugin with harness- level   |
|                                         |               |             |                    |                             |   hooks that fire on session/tool-use events, independent of which model  |
|                                         |               |             |                    |                             |   answers — this is what makes it genuinely model- agnostic, not a design |
|                                         |               |             |                    |                             |   choice Agent Stack has to make. License is PolyForm Noncommercial       |
|                                         |               |             |                    |                             |   1.0.0; the license itself permits "any noncommercial purpose," and      |
|                                         |               |             |                    |                             |   auditing your own coding-assistant sessions plausibly qualifies even    |
|                                         |               |             |                    |                             |   for commercial work, since the restriction targets commercializing the  |
|                                         |               |             |                    |                             |   software itself, not gating what you do while running it — flagged as a |
|                                         |               |             |                    |                             |   caveat, not a certified legal reading. Sits entirely outside Agent      |
|                                         |               |             |                    |                             |   Stack's own routing.toml/personas/skills tree: this was a               |
|                                         |               |             |                    |                             |   personal-machine install, not something Agent Stack routes to. A Hermes |
|                                         |               |             |                    |                             |   integration also exists (beta, v0.1.0) for this operator's own          |
|                                         |               |             |                    |                             |   eval-runner harness, not yet installed.                                 |
| Sentry Skills / Prompt                  | ADOPTED,      | —           | 978                | ADAPTED — method in force,  | The `prompt-optimizer` skill exists in-repo                               |
|   Optimizer (getsentry/skills)          |   as method   |             |                    |   not the tool              |   (`skills/prompt-optimizer/SKILL.md`, `SPEC.md`, `SOURCES.md`),          |
|                                         |               |             |                    |                             |   confirmed by searching the tree. Its eval-backed removal method maps    |
|                                         |               |             |                    |                             |   directly onto Agent Stack's own 60-case frozen corpus as the gate — no  |
|                                         |               |             |                    |                             |   external tool adopted. Adaptation recorded 20260904 as accepted         |
|                                         |               |             |                    |                             |   `.archcore/rules/0013-trim-against-the-frozen-corpus-as-a-gate.md`: any |
|                                         |               |             |                    |                             |   token-cost trim to a `SKILL.md`, persona file or `routing.toml` entry   |
|                                         |               |             |                    |                             |   runs `evaluate_routing.py` against the frozen 60 before and after,      |
|                                         |               |             |                    |                             |   gating on hard invariants only.                                         |
| Microsoft                               | CONFIRMED     | MIT         | 6,625              | SKIP for now                | README confirms all three variants (LLMLingua, LLMLingua-2,               |
|   LLMLingua (microsoft/LLMLingua)       |               |             |                    |                             |   LongLLMLingua), EMNLP'23/ACL'24 papers. It compresses a live            |
|                                         |               |             |                    |                             |   prompt-assembly pipeline; Agent Stack is static files with no runtime   |
|                                         |               |             |                    |                             |   of its own — whatever assembles the final prompt (Claude Code, Codex)   |
|                                         |               |             |                    |                             |   is outside this project's control.                                      |
| context-mem                             | CONFIRMED,    | —           | 18                 | DEFER                       | Matches the described hybrid-retrieval/local/MCP characteristics, but     |
|   (JubaKitiashvili/context-mem)         |   small       |             |                    |                             |   single-maintainer and small. A general retrieval layer also cuts        |
|                                         |               |             |                    |                             |   against "no implicit persistent state" unless scoped narrowly to        |
|                                         |               |             |                    |                             |   something already explicit, like the field log.                         |
| Mem0 (mem0ai/mem0)                      | CONFIRMED,    | Apache-2.0  | 64,662             | SKIP as a tool; logic       | "The Memory Layer for AI Agents," Y Combinator S24, very active — the     |
|                                         |   description |             |                    |   already applied           |   most substantial of the three memory frameworks cited. An always-on     |
|                                         |   corrected   |             |                    |                             |   memory injector conflicts with the safety model's                       |
|                                         |   20260904    |             |                    |                             |   no-implicit-persistent-state rule. Original note called its idea        |
|                                         |               |             |                    |                             |   "retrieve-don't-dump" — corrected: Mem0's April 2026 algorithm dropped  |
|                                         |               |             |                    |                             |   write-time ADD/UPDATE/DELETE conflict resolution for single-pass        |
|                                         |               |             |                    |                             |   ADD-only extraction, resolving conflicts at retrieval time via          |
|                                         |               |             |                    |                             |   multi-signal ranking plus temporal reasoning (+21 to +38 pts on         |
|                                         |               |             |                    |                             |   LoCoMo/LongMemEval/BEAM). That is append-only dated writes, recency     |
|                                         |               |             |                    |                             |   resolved on read — already this project's own `count:asat` convention   |
|                                         |               |             |                    |                             |   (AGENTS.md), now applied to the reflective-memory round log             |
|                                         |               |             |                    |                             |   in `.archcore/rules/0013-trim-against-the-frozen-corpus-as-a-gate.md`.  |
| Letta (letta-ai/letta)                  | CONFIRMED     | Apache-2.0  | 24,603             | SKIP                        | "Platform for stateful agents... that can learn and self-improve over     |
|                                         |               |             |                    |                             |   time" is autonomous-loop framing by its own description — the exact     |
|                                         |               |             |                    |                             |   category Agent Stack's safety model excludes.                           |
| Zep (getzep/zep)                        | CORRECTED     | Apache-2.0  | 4,889              | SKIP                        | GitHub's own description of this repo is "Zep \| Examples, Integrations,  |
|                                         |               |             |                    |                             |   & More" — it is the examples/integrations repo, not the core engine.    |
|                                         |               |             |                    |                             |   The product is now a hosted service (`help.getzep.com`) with client     |
|                                         |               |             |                    |                             |   SDKs (`zep-python`, `zep-js`, `zep-go`), so adopting it means depending |
|                                         |               |             |                    |                             |   on an external hosted service, which needs explicit operator authority  |
|                                         |               |             |                    |                             |   under this project's own safety model — not a drop-in open-source       |
|                                         |               |             |                    |                             |   alternative to Mem0/Letta.                                              |
| Skill Optimizer                         | CONFIRMED,    | —           | 0                  | PILOT, cautiously           | Directly targets `SKILL.md` — the exact artifact type Agent Stack authors |
|   (FreeAutomation-Tech/skill-optimizer) |   small       |             |                    |                             |   — and description matches ("reduce skill token count by 40-70           |
|                                         |               |             |                    |                             |   percent"). But zero stars, early-stage, unproven. If tried, gate any    |
|                                         |               |             |                    |                             |   output through Agent Stack's own eval corpus and governance checks, not |
|                                         |               |             |                    |                             |   the tool's own benchmark, and start on 2-3 non-critical skills per its  |
|                                         |               |             |                    |                             |   own recommended pilot in section 12.                                    |
| Prompt Cache (yale-sys/prompt-cache)    | CONFIRMED,    | —           | 114                | N/A — convention, not       | Real academic implementation, but last pushed 2024-11-09 and presented    |
|                                         |   stale       |             |                    |   a tool                    |   here as current tooling; it's a research reference. Agent Stack has no  |
|                                         |               |             |                    |                             |   inference pipeline of its own to cache — the relevant lever is          |
|                                         |               |             |                    |                             |   provider-native caching plus ordering stable content first, which its   |
|                                         |               |             |                    |                             |   persona/skill file layout already does structurally.                    |
| LightRAG — named in the fact-check      | CONFIRMED to  | MIT-style   | 39,365             | DEFER                       | The canonical project is `HKUDS/LightRAG` (EMNLP2025), large and active.  |
|   request, not in this document's own   |   exist,      |   academic  |   (HKUDS/LightRAG) |                             |   Out of scope here since this document covers memory/retrieval and       |
|   reference list                        |   correctly   |             |                    |                             |   compression, not RAG-indexing — a legitimate scope decision, not an     |
|                                         |   dropped     |             |                    |                             |   oversight. Revisit only if capability-gap or field-log evidence volume  |
|                                         |               |             |                    |                             |   grows large enough to need real semantic retrieval.                     |

**One reference from the first draft was removed and could not be verified at all**: "BM629 token-optimization skill." A GitHub search for `BM629` returns zero repositories. It does not correspond to
any findable project and is not repeated here even as a "study later" candidate — unlike LightRAG, which is real and simply out of scope, this name has no confirmed referent.

