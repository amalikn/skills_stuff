---
name: skill-repomix
description: Safely scopes, packages, compresses, validates, and routes repository context using Repomix CLI and Repomix MCP for Codex, Claude Code, local LLMs, audits, reviews, and reusable reference workflows.
version: 0.2.0
license: Apache-2.0
---

# Skill: Repomix Workflow

## Purpose

Use Repomix to create the smallest safe repository context needed for a task.

Supported outputs:

- Repomix MCP for dynamic repository discovery
- XML for structured static snapshots
- Markdown for human review
- JSON for pipelines
- compressed packs for architecture discovery and constrained local models
- pinned remote repository reference packs

## Audience and Authority

- `SKILL.md` is the authoritative behavioural contract for AI agents.
- `README.md` is the human-facing installation and operation guide.
- `AGENTS.md` governs maintenance of the skill package.
- Scripts and templates provide reusable supporting mechanics.
- Repository-specific governance overrides generic defaults in this skill.
- When agent behaviour conflicts with human installation guidance, `SKILL.md` governs agent behaviour.

## Trigger Conditions

Use this skill for:

- repository onboarding
- architecture analysis
- code-review context
- current-state snapshots
- change-review packs
- security-review packs
- remote FOSS repository inspection
- token reduction
- Repomix configuration
- Repomix MCP routing
- language-specific repository packaging

## Non-Trigger Conditions

Do not use Repomix as a replacement for:

- semantic code editing
- test execution
- runtime debugging
- Git mutation
- current package documentation
- static security analysis
- durable project memory

## Mandatory Workflow

1. Read project governance files.
2. Identify the exact task.
3. Detect repository language and type.
4. Select the smallest applicable profile.
5. Determine the token budget for the selected profile.
6. Apply project-specific include overrides.
7. Apply security exclusions.
8. Inspect projected token usage against the budget.
9. Apply the threshold decision from Token-Budget Thresholds.
10. Choose MCP or static output.
11. Choose compression or full source.
12. Generate the pack.
13. Validate security and output.
14. Execute the retry strategy if the output exceeds the budget.
15. Split the output or abort if retry attempts are exhausted; emit the prescribed run report.

## Routing Decisions

| Situation | Preferred route |
|---|---|
| Broad discovery with an MCP-capable client | Repomix MCP |
| Audit, handoff, or reproducible evidence | Static XML pack |
| Human and AI review | Markdown |
| Programmatic processing | JSON |
| Local LLM with constrained context | Targeted compressed XML |
| Exact implementation review | Full, uncompressed source |
| Remote FOSS reference | Pinned revision, compressed by default |

## Token-Budget Thresholds

Evaluate projected or actual token usage against the selected profile budget.

| Budget utilisation | Required action |
|---|---|
| 0–60% | Continue with the selected scope |
| 61–80% | Continue, but remove non-essential examples, broad documentation, and unrelated tests where safe |
| 81–100% | Narrow the pack to the directly relevant subsystem before final generation |
| Above 100% | Do not deliver the pack; execute the pack-too-large retry strategy |
| Unknown | Run token inspection or generate a narrowly scoped diagnostic pack first |

Budget utilisation = actual or estimated tokens / selected profile token budget × 100.

Thresholds apply to the configured budget of the selected profile, not to the model context window.

Compression MUST NOT be enabled solely because the budget is exceeded when exact implementation logic is required.

## Pack-Too-Large Retry Strategy

When projected or generated output exceeds the token budget:

1. Remove generated, archived, historical, example, fixture, and unrelated test content.
2. Restrict scope to the affected package, service, module, or subsystem.
3. Retain governance files and directly relevant dependency manifests.
4. Remove unrelated language ecosystems from mixed-repository profiles.
5. Enable compression only when exact implementation bodies are not required.
6. Recalculate or regenerate the pack.
7. Repeat for a maximum of three attempts.
8. If still over budget:
   - split the output into explicitly named logical packs; or
   - stop and report that the requested scope cannot fit safely.

The agent MUST NOT:

- silently truncate output;
- silently exceed the token budget;
- remove authoritative governance files;
- compress implementation-sensitive code merely to make it fit.

## Ambiguous Routing

When more than one route is valid:

1. Prefer the route with the smallest safe context footprint.
2. Prefer static output when reproducibility is required.
3. Prefer MCP when scope is unknown and interactive discovery is available.
4. Prefer full source over compression when implementation correctness matters.
5. Prefer project-specific governance over skill defaults.
6. If ambiguity materially affects safety, cost, privacy, or correctness, ask the user.
7. Otherwise, choose the safest route and record the decision.

The user or project owner is the escalation authority. The skill must not invent an additional approval authority.

## Compression

Use compression for:

- architecture discovery
- external repository research
- broad structural review
- constrained local models

Do not use compression for:

- debugging
- SQL correctness
- financial logic
- validation code
- security-sensitive implementation details
- exact error handling
- authentication or authorisation review

## Safeguards

MUST NOT:

- disable Repomix security scanning
- include `.env` files, credentials, private keys, tokens, databases, logs, caches, runtime state, archives, backups, or rollback data
- trust remote repository Repomix configuration
- silently follow a remote default branch
- package `/`, `$HOME`, or another over-broad path
- recursively include generated Repomix output
- treat compressed output as source-equivalent
- claim validation that was not executed

## Required Run Report

Every completed Repomix workflow MUST produce this structure.

### Repomix Execution Summary

| Field | Value |
|---|---|
| Task | |
| Repository | |
| Selected profile | |
| Repository type | |
| Output mode | MCP / static |
| Output format | XML / Markdown / JSON / plain |
| Included scope | |
| Excluded scope | |
| Compression | Enabled / disabled |
| Compression justification | |
| Token budget | |
| Estimated or actual token count | |
| Budget utilisation | |
| Retry attempts | |
| Output path | |
| Security scan | Pass / fail / not executed |
| Validation | Pass / fail / partial |
| Remaining risks | |

### Scope Decisions

- Authority files used:
- Included:
- Excluded:
- Assumptions:
- Routing decision:
- Retry actions:

### Result

State whether the generated pack is:

- safe to use;
- within budget;
- suitable for the intended consumer;
- complete enough for the requested task.

Do not report a security or validation pass unless the check was executed.
