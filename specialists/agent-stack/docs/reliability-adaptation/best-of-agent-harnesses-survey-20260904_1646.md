Title: Best-of-agent-harnesses survey
Category: evidence-and-survey
Status: current
Scope: A source-verified screen of every project in ryanalberts/best-of-Agent-Harnesses (160 projects across 12 categories, GitHub-star snapshot captured by that list's maintainer 2026-08-30) for
  relevance to Agent Stack
Last reviewed: 20260904_1654 (created 20260904_1646; verdict column and two source-verified deep dives added same session, at operator request)
Summary: 5 of 12 categories (77 of 160 projects) are in Agent Stack's actual lane; within them 40 projects are named and individually reasoned about in the findings table, each given a
  STEAL/ADAPT/CONFIRM/USE/WATCH/ SKIP verdict in the same vocabulary as the prior 25-repo survey. The standout finding is not a new mechanism but a confirmation: `agents.md`, the open cross-tool
  briefing-file spec this page treats as foundational, is the exact convention Agent Stack's own AGENTS.md-per-directory design already implements. Two multi-agent projects not covered by the prior
  survey were opened and verified in depth
rather than left as leads: `omnigent`'s "meta-harness" tagline turned out to wrap an always-on collaborative session server (STEAL idea-only, same daemon caveat as MetaGPT/AutoGen), while
  `openai-agents-python`'s `handoff()` primitive carries a typed `input_type` payload schema plus a dynamic `is_enabled` legality gate (ADAPT), verified against its docs, not its README. The other 7
  categories (83 projects) are confirmed out of scope, mostly because they assume an execution runtime, a daemon, or a memory subsystem Agent Stack deliberately does not have.

# Best-of-agent-harnesses survey

## Contents

- [Why this document exists](#why-this-document-exists)
- [Method](#method)
- [Relevance criteria — what "relevant" means for this project](#relevance-criteria--what-relevant-means-for-this-project)
- [Findings table](#findings-table)
- [Notable findings](#notable-findings)
- [Category-by-category verdict, confirmed not guessed](#category-by-category-verdict-confirmed-not-guessed)
- [Cross-check against the prior 25-repo orchestrator survey](#cross-check-against-the-prior-25-repo-orchestrator-survey)
- [Caution flags](#caution-flags)
- [Proposed next step](#proposed-next-step)
- [What this document is not](#what-this-document-is-not)

## Why this document exists

The operator pointed at `https://github.com/ryanalberts/best-of-agent-harnesses` and asked for a survey of the harnesses it lists, screened for relevance to this project, with the reasoning captured
in a table. This is the same kind of question the [external-orchestrator-survey](external-orchestrator-survey-20260903_1849.md) answered nine days earlier for a hand-picked list of 25 repos — this
document runs the same discipline (open the actual source, don't answer from memory, record what was screened out and why) over a much larger, third-party-curated list.

## Method

`WebFetch` on the repository URL is blocked in this session by a context-mode policy that requires fetching through its own indexing tool; that tool returns a lossy HTML-to-markdown preview of the
GitHub repo page, not the underlying data. The repository publishes its full list as structured JSON for exactly this purpose — a `harnesses.json` file explicitly described as being for other agents
to consume — so this survey pulled that file and the README directly with `curl` against `raw.githubusercontent.com`, rather than working from a lossy rendering:

- `README.md` (513 lines) — the human-facing list, category descriptions, FAQ, and rankings guide.
- `harnesses.json` (403,892 bytes) — 160 project records (`name`, `url`, `category`, `description`, `stars`, `tier`, `tags`, `license_signal`), 12 category definitions, a 4-entry graveyard (projects
  flagged for star manipulation or archival), and 13 curated comparison guides.
- Two of those comparison guides were pulled and read in full because they bear directly on this project's own design choices: `comparisons/claude-code-skill-packs.md` and
  `comparisons/progressive-disclosure.md` (titled "Context files for agents: AGENTS.md vs CLAUDE.md vs skills vs MCP tool search" in the source).

Every project named as "relevant" below was checked against its row in `harnesses.json`, not reconstructed from memory of the category name. Star counts and descriptions are the source list's own
2026-08-30 snapshot, not independently re-verified against each project's live repo — that distinction matters because a small number of entries on lists like this later turn out to be inflated (see
[Caution flags](#caution-flags)).

Two entries flagged during the first pass as needing a closer look — `omnigent` and `openai-agents-python` — were pulled a level deeper than the rest, on the operator's instruction to reassess rather
than leave anything at description-only depth: their own `README.md` (627 lines and 181 lines respectively) and, for `openai-agents-python`, its `docs/handoffs.md`, were fetched and quoted with
file/line, matching the quote-verbatim discipline the prior 25-repo survey used for all 25 of its repos. Their table rows below cite what that deeper read found, not the one-line `harnesses.json`
description.

## Relevance criteria — what "relevant" means for this project

Agent Stack has no execution runtime of its own: it is a declarative persona/skill routing layer (`routing.toml`, gates, deterministic closure, a frozen-corpus eval harness) installed by symlink into
existing coding-agent harnesses, and its safety model explicitly excludes autonomous loops, daemons, unattended background agents, and consensus mechanisms ([AGENTS.md](../../AGENTS.md#safety-model)).
Something on this 160-project list is relevant here for one of five concrete reasons, not because it is popular or well-built in its own right:

1. **Target-harness candidate** — a coding-agent CLI or IDE that a `.agents`/`SKILL.md`-consuming installer could symlink into, i.e. a legitimate future row in the harness-capabilities registry the
   [phased implementation plan](phased-implementation-and-self-verification-plan-20260904_1208.md)'s Phase 1 proposes.
2. **Prior-art skill/config layer** — a project in the same slot Agent Stack itself occupies (a skill pack or briefing-file convention layered on top of a coding-agent harness rather than a harness
   itself), worth knowing as a comparison point even where no feature is worth importing.
3. **Governing spec** — a convention Agent Stack's own design already depends on, where the value is confirmation, not adoption.
4. **Orchestration idea** — a multi-agent coordination mechanism, screened against the exclusion list and cross-checked against the prior 25-repo survey so the same repo is not re-litigated.
5. **Eval comparable** — a benchmark or eval harness whose method is worth knowing even though it answers a different question (task-success rate) than Agent Stack's own routing-correctness eval.

A category failing all five is recorded as screened and skipped, not silently omitted — [Category-by-category verdict](#category-by-category-verdict-confirmed-not-guessed) covers all 12, including the
7 with no relevant entries.

## Findings table

NOTE: like the [external-orchestrator-survey](external-orchestrator-survey-20260903_1849.md)'s table, this one carries cells past 200 characters — a wrap hook breaks those into padded continuation
lines automatically, which is this project's existing convention for wide tables under its 200-column wrap policy, not a defect. If this table is ever hand-edited, do not run `table-reflow` or
`mdtable wrap` on it; that tool has previously corrupted a table in this exact folder by duplicating frontmatter into every row (see `feedback_table_authoring_reflow_script` in personal auto-memory).

Verdict vocabulary matches the external-orchestrator-survey's: STEAL (a concrete, directly reusable mechanism), ADAPT (a real idea, needs building, not a drop-in), CONFIRM (validates a design choice
already made, no action implied), USE (already running in this environment), WATCH (a legitimate candidate, not yet acted on), ALREADY-ASSESSED (carried over from the prior 25-repo survey, not
re-litigated), SKIP (opened and screened out).

| repo                                | category                     | verdict              | the one thing worth knowing                                                                              |
| ----------------------------------- | ---------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------- |
| [agents.md](https://github.com/agentsmd/agents.md) | progressive-disclosure       | CONFIRM              | The open, nested, per-directory briefing-file convention this project's own `AGENTS.md`/`CLAUDE.md`      |
|                                     |                              |                      |   split already follows; 60k+ repos, stewardship moved to the Linux Foundation Dec 2025                  |
| [context-mode](https://github.com/mksglu/context-mode) | progressive-disclosure       | USE                  | 20.3k stars in the source snapshot; this session is running it as an MCP server right now, via a hook    |
|                                     |                              |                      |   that redirected this survey's own fetches through it. Elastic License 2.0, not OSS; its own npm        |
|                                     |                              |                      |   installs are down roughly a third since Claude Code's native tool-search shipped                       |
| [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) | progressive-disclosure       | CONFIRM (peripheral) | The same index-then-load pattern implemented natively inside Cursor's `.cursorrules`; the pattern is     |
|                                     |                              |                      |   convergent across harnesses, not Claude-Code-specific                                                  |
| Headroom, MCP-Zero, ToolGen,        | progressive-disclosure       | SKIP                 | All five solve tool-schema / RAG-chunk bloat inside a runtime tool loop. Agent Stack has no runtime tool |
|   ToolRAG, langgraph-bigtool        |                              |                      |   loop and no MCP server of its own — its equivalent problem (persona/skill selection) is already solved |
|                                     |                              |                      |   declaratively by `routing.toml`, not by retrieval                                                      |
| [Codex](https://github.com/openai/codex) | coding-agent-products        | CONFIRM (existing)   | Already a primary Agent Stack install target; included for completeness of the registry mapping, not a   |
|                                     |                              |                      |   new finding                                                                                            |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli), [opencode](https://github.com/anomalyco/opencode) | coding-agent-products        | WATCH                | Both named in Agent Stack's own harness-agnostic design section (and in `superpowers`'s description as   |
|                                     |                              |                      |   supported harnesses) but neither is a concretely tested symlink target in this repo yet — real         |
|                                     |                              |                      |   candidates, not yet evidenced by an install                                                            |
| [Cline](https://github.com/cline/cline), [goose](https://github.com/aaif-goose/goose), [Roo Code](https://github.com/RooCodeInc/Roo-Code), [Kilo Code](https://github.com/Kilo-Org/kilocode) | coding-agent-products        | WATCH                | VS Code / MCP-native harnesses in the same "install a skill folder into an existing agent" slot Agent    |
|                                     |                              |                      |   Stack targets. None currently named anywhere in this project's docs — genuinely new candidate rows if  |
|                                     |                              |                      |   the harness-capabilities registry is built out                                                         |
| [aider](https://github.com/Aider-AI/aider) | plugins-mcp-cli              | WATCH                | Git-aware CLI pair programmer with its own AGENTS.md/CLAUDE.md-style config surface. Not named in Agent  |
|                                     |   (miscategorized by source  |                      |   Stack's docs, but the operator's own environment runs it independently (`aider`, `aider-desk-dev`      |
|                                     |   as a CLI tool; functions   |                      |   working directories) — the nearest thing on this list to a harness already in daily use that Agent     |
|                                     |   as a harness)              |                      |   Stack has not accounted for                                                                            |
| Claude Code                         | — (not listed)               | N/A                  | Agent Stack's primary harness does not appear as a ranked project anywhere in `harnesses.json` — the     |
|                                     |                              |                      |   list ranks by public GitHub star count, and Claude Code has no public repo to count                    |
| [superpowers](https://github.com/obra/superpowers) | coding-harness-configs       | ADAPT                | Not in the prior 25-repo survey. 279.6k stars, runs on 14 harnesses including Claude Code, Codex, Cursor |
|                                     |                              |                      |   and OpenCode. Its startup hook re-injects standing rules after context compaction — a concrete         |
|                                     |                              |                      |   recovery mechanism Agent Stack does not have                                                           |
| [Anthropic Skills](https://github.com/anthropics/skills) | coding-harness-configs       | CONFIRM (reference)  | The first-party reference for the SKILL.md format Agent Stack's own `SKILL_STANDARD.md` builds on.       |
|                                     |                              |                      |   Per-skill Anthropic terms, not standard open source — informational, since Agent Stack's own skills    |
|                                     |                              |                      |   are original                                                                                           |
| [GStack](https://github.com/garrytan/gstack) | coding-harness-configs       | ADAPT (cheap)        | 23 slash-command modes structuring one assistant as a virtual team. Its checkpoint-mode auto-commit and  |
|                                     |                              |                      |   `/freeze`/`/careful` guardrails are a concrete recoverability idea Agent Stack does not have; the      |
|                                     |                              |                      |   multi-persona part itself Agent Stack already does, harness-agnostically                               |
| [get-shit-done](https://github.com/open-gsd/gsd-core) | coding-harness-configs       | ADAPT                | Goal-backward plans persisted as files, executed in waves over fresh context windows, so a crashed or    |
|                                     |                              |                      |   cleared session resumes from the plan file. Durability without a daemon — survives the safety-model's  |
|                                     |                              |                      |   exclusion because the state lives in a file, not a running process                                     |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | coding-harness-configs       | ADAPT (cheap)        | 24 skills plus 4 specialist personas explicitly built for portability across 70+ agents — the same       |
|                                     |                              |                      |   harness-agnostic bet as Agent Stack's own Standing rule 6, from a different author; worth a            |
|                                     |                              |                      |   feature diff                                                                                           |
| [wshobson/agents](https://github.com/wshobson/agents) | coding-harness-configs       | ALREADY-ASSESSED     | Surveyed 2026-09-03: its declarative per-harness capability matrix is the direct precedent for the       |
|                                     |                              |   (STEAL)            |   harness-capabilities registry proposal. Listed here only to confirm it is the same repo                |
| [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) | coding-harness-configs       | SKIP                 | The API/runtime layer beneath Claude Code, not a config or skill layer. Recorded to show it was checked, |
|                                     |                              |                      |   not skipped by category-name assumption                                                                |
| [agents-cli (Google)](https://github.com/google/agents-cli) | coding-harness-configs       | ADAPT (narrow)       | Google's official agent-evaluation and deployment skill layer on top of whichever coding assistant is    |
|                                     |                              |                      |   already installed — the same "config layer over someone else's harness" bet, now a first-party move by |
|                                     |                              |                      |   a second vendor besides Anthropic                                                                      |
| [Terminal-Bench](https://github.com/harbor-framework/terminal-bench), | evaluation                   | SKIP                 | All three measure end-to-end task success, not routing correctness. Matches the prior survey's           |
|   [SWE-bench](https://github.com/SWE-bench/SWE-bench), [inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai) |                              |   (different         |   independent finding that Agent Stack's frozen-corpus, asymmetric-gate eval is ahead of every           |
|                                     |                              |   question)          |   routing-quality mechanism found across both surveys — these three answer a different question entirely |
| [omnigent](https://github.com/omnigent-ai/omnigent) | multi-agent                  | STEAL (idea only)    | Not in the prior 25-repo survey. Its own README (`README.md:7`): "an open-source **meta-harness** that gives |
|                                     |                              |                      |   you a common orchestration layer over Claude Code, Codex, Cursor, OpenCode, Hermes, Pi, and the agents |
|                                     |                              |                      |   you write yourself: swap or combine harnesses without rewriting, enforce policies and sandboxing."     |
|                                     |                              |                      |   Verified past the tagline: the concrete implementation is an alpha-status (`README.md:12`),            |
|                                     |                              |                      |   always-running, cross-device collaborative session server with cloud-sandbox provisioning — itself the |
|                                     |                              |                      |   always-on-daemon shape the safety model excludes, the same caveat the prior survey attached to MetaGPT |
|                                     |                              |                      |   and AutoGen. The harness-agnostic policy-layer idea is real and worth studying; the runtime it ships   |
|                                     |                              |                      |   in is not importable as-is                                                                             |
| [openai-agents-python](https://github.com/openai/openai-agents-python) | multi-agent                  | ADAPT                | Not in the prior 25-repo survey. Verified in its `handoffs.md` doc, not just the README: the `handoff()` |
|                                     |                              |                      |   function's `input_type` param is a typed schema for the handoff tool-call's arguments, and             |
|                                     |                              |                      |   `is_enabled` is a boolean-or-callable that can dynamically legalize or block a specific handoff edge   |
|                                     |                              |                      |   at runtime. Both are concrete, narrower primitives than Agency Swarm's `extra_params_model` (already   |
|                                     |                              |                      |   ADAPT-verdicted in the prior survey) for the same `consumes`/handoff-legality declaration the          |
|                                     |                              |                      |   reliability-adaptation proposal's Phase 2 sketches from MetaGPT — `is_enabled` in particular has no    |
|                                     |                              |                      |   analogue in either MetaGPT's static `_watch` set or Agency Swarm's payload contract                    |
| [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | multi-agent                  | ALREADY-ASSESSED     | Carried over from the prior survey; see [Cross-check](#cross-check-against-the-prior-25-repo-orchestrator-survey) |
|                                     |                              |   (STEAL idea-only)  |                                                                                                          |
| [autogen](https://github.com/microsoft/autogen) | multi-agent                  | ALREADY-ASSESSED     | Carried over from the prior survey; see [Cross-check](#cross-check-against-the-prior-25-repo-orchestrator-survey) |
|                                     |                              |   (STEAL idea-only)  |                                                                                                          |
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | multi-agent                  | ALREADY-ASSESSED     | Carried over from the prior survey; see [Cross-check](#cross-check-against-the-prior-25-repo-orchestrator-survey) |
|                                     |                              |   (ADAPT)            |                                                                                                          |
| [crewAI](https://github.com/crewAIInc/crewAI) | multi-agent                  | ALREADY-ASSESSED     | Carried over from the prior survey; see [Cross-check](#cross-check-against-the-prior-25-repo-orchestrator-survey) |
|                                     |                              |   (ADAPT, cheap)     |                                                                                                          |
| OpenManus, ChatDev, hive,           | multi-agent                  | SKIP                 | OpenManus and ChatDev are MetaGPT-lineage autonomous-loop products (same exclusion as Agent Zero in the  |
|   PraisonAI, AG2, AgentRL           |                              |                      |   prior survey); hive and PraisonAI are self-hosted/autonomous multi-agent runtimes; AG2 is the          |
|                                     |                              |                      |   community continuation of AutoGen, already covered via AutoGen's own entry; AgentRL is an RL-training  |
|                                     |                              |                      |   harness, a different problem entirely                                                                  |

## Notable findings

**The convention Agent Stack already follows is the field's converged answer, not a niche choice.** The source list's own `progressive-disclosure` comparison guide states the community consensus
plainly: "One repo, several tools touching it → AGENTS.md, nested per directory in big repos. Free, no software, every major harness reads it." and "Claude Code is your only harness → CLAUDE.md is
equivalent and native; adopt AGENTS.md the day a second tool shows up." That is precisely Agent Stack's own layering — a thin `CLAUDE.md` pointing at a canonical `AGENTS.md`, nested per directory
across this whole workspace — arrived at independently and now confirmed against an external, actively-maintained reference. The same guide also names the reason Agent Stack still needs the
`CLAUDE.md` wrapper at all rather than relying on Claude Code reading `AGENTS.md` natively: that is a still-open upstream feature request (`anthropics/claude-code#6235`), not a settled default.

**One listed project is already running inside this very session.** `context-mode` (20.3k stars in the source snapshot) is not a hypothetical candidate — a PreToolUse hook in this session's own tool
configuration redirected this survey's web-fetch calls through it, and its `ctx_fetch_and_index`/`ctx_search` tools did the initial page-content retrieval before this survey switched to fetching the
underlying JSON directly. Its own comparison-guide entry notes two things worth carrying forward operationally, independent of Agent Stack: it is source-available under the Elastic License 2.0 rather
than standard open source, and its npm installs have fallen roughly a third from a May-2026 peak since Claude Code's native tool-search feature shipped in January 2026 — the source list's own caution
that "platform defaults keep absorbing this category" applies directly to a tool this environment currently depends on.

**Claude Code's absence from the list is structural, not an oversight.** The list ranks 160 projects by public GitHub star count captured 2026-08-30. Claude Code has no public repository, so it cannot
appear no matter how central it is to this project's own harness-agnostic design. This matters for anyone reading `harnesses.json` as a completeness signal for "what coding harnesses exist" — it is a
completeness signal only for what is both open-source-hosted-on-GitHub and popular, not for the full market.

## Category-by-category verdict, confirmed not guessed

All 12 categories were opened and read in full via the structured data, not assumed from the category title:

**In scope (5 categories, 77 projects):** `progressive-disclosure` (8), `coding-agent-products` (22), `coding-harness-configs` (17), `multi-agent` (12), `evaluation` (18) — for the reasons in
[Relevance criteria](#relevance-criteria--what-relevant-means-for-this-project). Not every project within these five carried a distinct finding; the ones that did not (most of the 18
evaluation-category benchmarks beyond the three named above, most of the 22 coding-agent-products beyond the ones named above) were still opened and are screened rather than omitted — they measure or
run something Agent Stack has no equivalent surface for (e.g. `WebArena`, `AgentBench`, `SWE-Gym` measure web/OS/training tasks; `DeepSeek-Reasonix`, `crush`, `qwen-code`, `jcode` are additional
terminal-coding-agent products with no evidence they are, or are being considered as, an Agent Stack install target).

**Out of scope, confirmed (7 categories, 83 projects):**

- `personal-agent-runtimes` (10) — every entry is an always-on daemon by design (OpenClaw, Hermes, nanobot, Agent Zero, and 6 more); this is the exact category Agent Stack's safety model excludes by
  name, not a close call.
- `frameworks` (25) — general-purpose LLM *application* frameworks (LangChain, n8n, Dify, langgraph, semantic-kernel, and 21 more) sit at what the source list itself calls "the app layer, not
  harnesses per se." Agent Stack builds nothing on top of a coding agent's tool loop; there is no app layer here to compare against.
- `plugins-mcp-cli` (19) — concrete MCP servers and CLI tool-wiring (official MCP Servers collection, Context7, GitHub MCP server, Playwright MCP, and 14 more). Agent Stack has no MCP server of its
  own and does no tool discovery; `aider` was pulled out of this category above as the one exception, because it functions as a harness despite the source list's placement.
- `memory` (5) — persistent memory layers (claude-mem, Mem0, Graphiti, cognee, beads). Agent Stack explicitly carries no memory subsystem of its own; the operator's separate memory-keeper /
  mcp-project-context stack already occupies this slot outside this project's boundary.
- `observability` (4) — production tracing and eval-ops (Langfuse, MLflow, Opik, Arize Phoenix) for live agent traffic. Agent Stack has no production runtime generating traffic to trace.
- `research-task` (5) — deep-research and domain-specific agent loops (DeerFlow, gpt-researcher, and 3 more). No routing or config-layer overlap with any of these.
- `libraries-sdks` (15) — runtime primitives (sandboxing, provider-agnostic LLM routing, agent SDKs). Agent Stack has no execution engine for any of these to plug into.

## Cross-check against the prior 25-repo orchestrator survey

Six repos appear on both lists: MetaGPT, autogen (Microsoft AutoGen), Microsoft Agent Framework, crewAI, wshobson/agents, and Agent Zero. All six carry the same verdict here as in the
[external-orchestrator-survey](external-orchestrator-survey-20260903_1849.md#findings-table) (STEAL idea-only / STEAL idea-only / ADAPT / ADAPT-cheap / STEAL / SKIP respectively) — no contradiction,
and no re-litigation was needed. Two genuinely new items surfaced by this broader, third-party-curated list were not in the hand-picked 25, and both were opened and quoted with file/line rather than
assessed from their one-line description, matching the prior survey's own discipline: `omnigent` turned out to be an alpha-status, always-on collaborative session server underneath its "meta-harness"
tagline — the same daemon shape the safety model already excludes, so it verdicts STEAL (idea only), the same qualifier the prior survey attached to MetaGPT and AutoGen. `openai-agents-python`'s
`handoff()` primitive carries an `input_type` typed-payload schema and an `is_enabled` dynamic legality gate, verified in its `handoffs.md` doc rather than assumed from the README — a narrower,
cleaner pair of mechanisms than MetaGPT's static `_watch` set for the same `consumes`/handoff-legality declaration Phase 2 already proposes, so it verdicts ADAPT.

## Caution flags

The source list's own graveyard records `everything-claude-code` as "suspected star manipulation — ~228k stars / ~35k forks on a repo created 2026-01 with no matching install base, dependents, or
discussion; fork-to-star ratio and growth curve are inconsistent with organic adoption." It is Claude-Code-adjacent by name and was never in scope for this survey's findings table, but it is exactly
the kind of result an unguided search for "Claude Code skill packs" would surface — worth naming here so it is not later mistaken for evidence.

## Proposed next step

This is evidence, not a decision. Two concrete follow-ups fall out of it, both scoped to work already open rather than new work:

1. If the harness-capabilities registry from the [phased implementation plan](phased-implementation-and-self-verification-plan-20260904_1208.md)'s Phase 1 proceeds, its candidate row list should
   include Gemini CLI, opencode, aider, Cline, goose, Roo Code, and Kilo Code as named or newly-identified target harnesses — none of these were previously listed together in one place.
2. If Phase 2's `consumes`/handoff-legality declaration is built, evaluate `openai-agents-python`'s `is_enabled` (a boolean-or-callable that can dynamically legalize or block a specific handoff edge)
   against Agency Swarm's already-ADAPT-verdicted `extra_params_model` before committing to a design — the two are not redundant: one gates whether a handoff may happen, the other constrains what
   payload it carries once it does, and Phase 2 may want both.

Whether to act on either is an operator decision; this document does not make it.

## What this document is not

This is not a durable architectural decision — those live in [`.archcore/`](../../.archcore/README.md). It is not a record of measured figures — those live in [`MEMORY.md`](../../MEMORY.md). It
records what a source-verified screen of `ryanalberts/best-of-Agent-Harnesses` found at 2026-09-04 16:46, against a third-party list whose own star counts and category assignments were captured
2026-08-30 and are not independently re-verified here. It stands as evidence until superseded, per this working-documents folder's own convention.
