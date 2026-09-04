Title: Vertical agent framework and reference-project fact-check
Category: evidence-and-proposal
Status: current
Scope: Source-verified fact-check of a Python multi-agent framework and reference-project list, proposed as a foundation for building new vertical domain-specialist agents (Network, Infrastructure,
  Finance/Business, Research) — not related to the Agent Stack Claude Code skill library
Last reviewed: 20260903_2200
Summary: PydanticAI is the strongest verified candidate framework. NetClaw is the one genuinely substantial network reference architecture, and Vertical AI Agent (chetanreddyv) is the closest real
  manager-specialist-MCP proof of concept. This document's own first pass wrongly reported two real projects as not found; both were confirmed once the operator supplied direct links, and the
  correction is recorded in place rather than silently fixed. Several other projects carry material licensing or scope errors the original brief did not flag.

# Vertical agent framework and reference-project fact-check

## Contents

- [Why this document exists](#why-this-document-exists)
- [Correction: both projects exist — the search agents missed them, the operator found them](#correction-both-projects-exist-the-search-agents-missed-them-the-operator-found-them)
- [Frameworks for building the agents](#frameworks-for-building-the-agents)
- [Network-engineering reference projects](#network-engineering-reference-projects)
- [Finance and research reference projects](#finance-and-research-reference-projects)
- [What this changes about the original recommendation](#what-this-changes-about-the-original-recommendation)
- [Recommended next step](#recommended-next-step)

## Why this document exists

An unverified AI-generated summary proposed a stack for building new vertical domain-specialist agents — PydanticAI/LangGraph as the framework layer, NetClaw/NetCopilot/Netmiko MCP as network
reference architecture, FinRobot/TradingAgents/finance-mcp as finance reference architecture, plus two named proof-of-concept projects ("Vertical AI Agent," "OpenResearch Agent"). Per this operator's
standing source-discipline policy, no claim about third-party project behaviour, license, or existence is asserted from memory — three parallel research agents opened the actual repositories, searched
for the ones that could not be located by name alone, and verified every load-bearing claim against source, README, or LICENSE file before it is repeated here.

This document is unrelated to Agent Stack's own routing/skill-library work; it answers a different question — what to build NEW vertical agents with, not whether anything beats Agent Stack's existing
Claude Code skill catalogue. It is filed under this project's `docs/` at the operator's explicit request, as a working-evidence artifact from the same session, rather than because it bears on Agent
Stack's own routing or safety model. No dedicated repository yet exists for the vertical-agent initiative this document informs.

## Correction: both projects exist — the search agents missed them, the operator found them

The first pass of this survey reported "Vertical AI Agent" and "OpenResearch Agent" as `UNVERIFIED / NOT FOUND` after a genuine multi-strategy GitHub search. Both claims were wrong. The operator
supplied direct URLs and both projects are real, public, and match the original brief's descriptions closely. This section replaces the earlier "headline finding" rather than appending to it, because
the earlier finding is now known to be false and should not stand alongside its own correction.

**[chetanreddyv/vertical_aiAgent](https://github.com/chetanreddyv/vertical_aiAgent)** — real. GitHub's own description reads: "A Powerful Multi-Agent Orchestration System built with Pydantic AI and
Model Context Protocol (MCP) ... using a Manager-Specialist architecture." Verified directly against the README: a Gemini 2.0 Flash Manager agent decomposes a request into a structured
`ExecutionPlan`, routes each step to a specialist (Email, SQL, Drive, Calendar, TLDV meeting-transcript search, Jira, or a general-knowledge fallback), and each specialist reaches its tools through
MCP. 4 stars, last pushed 2026-02-23, Python. The README displays an MIT license badge, but GitHub's own license API reports `null` — no LICENSE file exists in the repository. This is the same class
of gap already flagged against the Netmiko MCP candidates: a claimed license that the repository does not actually carry.

**[hetu-project/openresearch-agent](https://github.com/hetu-project/openresearch-agent)** — real. This directly overturns the earlier finding on the Together.ai dependency: the README's own "Technical
Architecture" section states "**Together.ai** LLM integration for advanced language processing," and its setup instructions require a `TOGETHER_API_KEY` and name a specific model
(`Qwen/Qwen2.5-VL-72B-Instruct`). The Together.ai dependency is **CONFIRMED**, not unconfirmable. The three-part architecture the brief described — an MCP layer for academic data access, an LLM
service, and a separate data/storage layer for conversation history — is also confirmed against the README's own architecture diagram. License: GPL-3.0 (verified via GitHub's license API), which
carries copyleft obligations on redistribution that MIT/Apache-licensed alternatives do not. Maturity: thin and stale — 0 stars, 460 KB, last pushed 2025-06-20, no activity since.

**What this means about the survey's own method.** The search agents that produced the original "not found" verdict searched by architectural description and name variants, not by the exact repository
slug — and both slugs (`vertical_aiAgent` with an underscore and internal capital, `openresearch-agent` under the `hetu-project` org rather than a name-matching one) were plausible but not guessable
from the brief's prose alone. That is a real limitation of search-based verification, not a reason to trust the original brief's other unverified claims — most of which were checked against a
repository the search agents *did* find, which is a different and stronger form of verification than name-guessing. Where a search agent reports `NOT FOUND`, that means "not found by this method," not
"does not exist" — a distinction worth remembering the next time this kind of check is run.

## Frameworks for building the agents

| Project    | Repo                   | License (verified) | Verdict                      |
| ---------- | ---------------------- | ------------------ | ---------------------------- |
| PydanticAI | pydantic/pydantic-ai   | MIT                | CONFIRMED                    |
| smolagents | huggingface/smolagents | Apache-2.0         | CONFIRMED                    |
| CrewAI     | crewAIInc/crewAI       | MIT                | CONFIRMED, with a correction |
| LangGraph  | langchain-ai/langgraph | MIT                | PARTIALLY CONFIRMED          |
| AG2        | ag2ai/ag2              | Apache-2.0         | PARTIALLY CONFIRMED          |

**PydanticAI is the strongest verified candidate** for a manager→specialist local-agent architecture. Native, in-core support for all three things that matter here: Ollama as a documented
OpenAI-compatible provider, `MCPToolset` for MCP server integration, and a documented multi-agent pattern (agent-as-tool delegation, programmatic hand-off) in `docs/multi-agent-applications.md` —
nothing split across sibling packages. 19,698 stars, pushed the day of this check.

**Corrections to the original brief:**

- **AG2's "currently going through a transition toward v1" is wrong.** v1 (`import ag2`, the `Network`/Hub orchestration model) is the *current default* and a completed rewrite, not a transition in
  progress. The pre-rewrite AutoGen-derived code (`ConversableAgent`, `GroupChat`) was split into a separately maintained sibling package, `ag2ai/ag2-classic`. AG2's MCP support is real and
  substantial (`ag2/mcp/`, MCP-UI, provider-specific tests) — that part of the brief holds. Its local-LLM support could not be verified from the material fetched and should be treated as unconfirmed
  rather than assumed.
- **LangGraph's Ollama and MCP support are not native to the `langgraph` repo.** Both live in separate LangChain-ecosystem packages — `langchain-community` for Ollama, the actively-maintained
  `langchain-ai/langchain-mcp-adapters` (3,649 stars) for MCP. The brief presented this as monolithic; in practice it means an extra dependency and an extra thing to version-track. A dedicated
  `langgraph-supervisor-py` package covers the manager→specialist pattern the brief described.
- **CrewAI's dedicated `crewAI-tools` repo is archived/deprecated** — not mentioned in the original brief at all. Current MCP support (`MCPServerAdapter`, stdio and SSE) now lives inside the main
  `crewAI` monorepo.

## Network-engineering reference projects

| Project           | Found?                                               | License                              | Verdict                                       |
| ----------------- | ---------------------------------------------------- | ------------------------------------ | --------------------------------------------- |
| NetClaw           | Yes — automateyournetwork/netclaw                    | Apache-2.0                           | CONFIRMED, understated if anything            |
| NetCopilot / ARIA | Yes — AnasProgrammer2/netcopilot                     | Business Source License 1.1          | Real, but "free and open source" is wrong     |
| "Netmiko MCP"     | Not one project — several small unrelated candidates | None declared on the closest matches | Generic pattern, not a single maturity signal |

**NetClaw is the one genuinely worth studying.** 650 stars, active daily (last push the day of this check), 766 commits, 19 contributors, 5.4MB of actual Python — not a thin README. The claimed
`SOUL.md` / `SOUL-EXPERTISE.md` / `SOUL-SKILLS.md` / `TOOLS.md` persona+expertise+skills+tools separation is real and documented verbatim inside `SOUL.md` itself, which also states the persona holds
"CCIE R&S #AI-001" — a fabricated-but-declared identity, worth noting as a design choice rather than an error. The claimed vendor/tool breadth (Batfish, ThousandEyes, NSO, F5, Palo Alto, Fortinet,
Infoblox, plus more not in the original brief — Check Point, AWS/Azure, Meraki, ISE, Catalyst Center) is confirmed verbatim in the README.

**NetCopilot/ARIA is real but the brief's licensing claim is wrong.** It's a legitimate, shipped, signed Electron app that closely matches the "plans investigations, executes commands, interprets
outputs" description. But it is licensed under the Business Source License 1.1 — commercial use is prohibited until 2029-01-01 (when it converts to Apache-2.0) — and the ARIA agent itself is gated
behind a license key tied to a hosted backend, not a self-contained local agent as the brief implied. It has also gone quiet: no commits in roughly 2.5 months as of this check, single contributor.

**"Netmiko MCP" is not one project.** The closest candidates (`upa/mcp-netmiko-server`, `ntunes/netmiko-mcp-server`) carry **no declared license file at all**, and — more importantly — both expose
config-push/commit operations (`set_config_commands_and_commit_or_save`, `send_config`), not read-only access as "controlled access" implied. Neither README documents Claude Code or Cursor
compatibility; both document Claude Desktop only. Treat this as a pattern to reimplement narrowly and deliberately read-only, not an existing project to adopt.

## Finance and research reference projects

| Project                           | Found?                                             | License                        | Scale                               | Fit for AU business-feasibility work |
| --------------------------------- | -------------------------------------------------- | ------------------------------ | ----------------------------------- | ------------------------------------ |
| FinRobot                          | Yes — AI4Finance-Foundation/FinRobot               | Apache-2.0                     | 7,903 stars, academically published | Poor — markets/investment, not       |
|                                   |                                                    |                                |   (ICAIF 2024)                      |   feasibility                        |
| TradingAgents                     | Yes — TauricResearch/TradingAgents                 | Apache-2.0                     | 102,381 stars, actively released    | Poor — trading-firm simulation       |
| finance-mcp                       | Ambiguous — five unrelated repos share the name    | Apache-2.0 (best-match         | Thin — 25 stars, one release        | Unverifiable which project was meant |
|                                   |                                                    |   candidate)                   |                                     |                                      |
| Vertical AI Agent (chetanreddyv)  | Yes — found by operator after search agents missed | MIT badge claimed, no LICENSE  | 4 stars, last pushed 2026-02-23     | Architecture match, not domain match |
|                                   |   it                                               |   file (verified)              |                                     |                                      |
| OpenResearch Agent (hetu-project) | Yes — found by operator after search agents missed | GPL-3.0 (verified)             | 0 stars, stale since 2025-06-20     | Architecture match, not domain match |
|                                   |   it                                               |                                |                                     |                                      |

Both FinRobot and TradingAgents are real, substantial, and exactly as described — TradingAgents in particular is far larger than the brief implied (102k stars, GitHub-trending, backed by a published
arXiv paper), not a niche project. But both are markets/investment/trading tools: equity valuation, algorithmic trading, sentiment/technical analysis. **Neither has a feasibility, landed-cost, or
margin-analysis primitive**, which is this operator's actual recurring need (Australian business-feasibility, import-costing, pilot-programme analysis). Their transferable value is architectural —
specialist-role decomposition, and FinRobot's separation of deterministic computation from LLM narration — not their domain content.

`finance-mcp` as named is ambiguous across at least five unrelated repositories; the closest match to the brief's wording (`FlowLLM-AI/finance-mcp`) is real, functioning code but early-stage (one
v0.1.x release, 25 stars). This ambiguity should be resolved with the operator, not guessed, if this candidate is ever pursued.

**Vertical AI Agent (chetanreddyv) is the closest real match to a manager→specialist→MCP proof-of-concept** the original brief could have meant, and it is worth studying for exactly that reason — a
Gemini Manager decomposing a request into steps for typed specialist agents (Email, SQL, Drive, Calendar, Jira, meeting-transcript search), each reaching tools only through MCP, with an explicit
human-in-the-loop confirmation gate on any mutating step. It is a small, single-maintainer project (4 stars) with a license badge the repository does not actually back with a LICENSE file — study the
pattern, do not depend on the code as a supply chain.

**OpenResearch Agent (hetu-project) confirms the architecture claim and the Together.ai dependency exactly as the brief stated.** Its own README documents the three-part split (MCP data-access layer,
Together.ai LLM service, separate conversation-storage layer) and a hard `TOGETHER_API_KEY` requirement. It is GPL-3.0 licensed — a materially different obligation than the MIT/Apache projects
elsewhere in this survey — and has had no activity in over a year as of this check. Useful as an architecture reference for splitting intent analysis from response generation; not worth adopting as
code given its licensing and staleness.

## What this changes about the original recommendation

The original brief's headline architecture — PydanticAI as the primary framework, LangGraph added selectively for stateful workflows, NetClaw/NetCopilot/Netmiko MCP as network study material,
FinRobot/TradingAgents as finance study material, plus the two named proof-of-concept projects — holds up substantially better than this survey's own first pass reported. PydanticAI's advantage is
confirmed rather than assumed, and both named proof-of-concept projects turned out to be real, matching their described architecture. Two corrections stand: NetCopilot/ARIA's licensing was materially
understated (it is Business Source License 1.1, not free/open-source software), and this survey's own first pass wrongly reported two real projects as not found — a limitation of name-based search,
corrected once the operator supplied direct links, and recorded above rather than quietly fixed.

## Recommended next step

None of this should be acted on as a build decision yet — it is a fact-check of proposed inputs, not a design. If a Network Engineering specialist agent is the first one to build, the concrete,
now-verified starting point is: PydanticAI as the framework, NetClaw's `SOUL.md`/`SOUL-EXPERTISE.md`/`SOUL-SKILLS.md`/`TOOLS.md` separation as the persona-file reference architecture (not its code,
which is a full product with its own 168-MCP-server sprawl), and a purpose-built, deliberately read-only Netmiko MCP wrapper rather than either of the two unlicensed existing ones.

**This document's relevance is not limited to building a new agent.** `chetanreddyv/vertical_aiAgent`'s manager→specialist→MCP pattern, with typed per-specialist tool scopes and a human-in-the-loop
gate on mutating steps, is directly relevant prior art for Agent Stack's own proposed Phase 2 (legal hand-offs) and Phase 4 (operator-controlled action authorization) — see
[reliability-adaptation/agent-stack-reliability-adaptation-proposal-20260903_1943.md](../reliability-adaptation/agent-stack-reliability-adaptation-proposal-20260903_1943.md), which now cites it
alongside MetaGPT and Agency Swarm. This document stays filed separately because it answers a different immediate question — what to build a new agent with — not because its findings have no bearing
on Agent Stack's own evolution.
