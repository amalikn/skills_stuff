Title: External orchestrator and skill-library survey
Category: evidence-and-proposal
Status: current
Scope: A source-verified survey of 25 external agent-orchestration and skill-library repositories, assessed against Agent Stack's existing routing catalogue, gate closure and safety model
Last reviewed: 20260903_1849
Summary: No external repo beats Agent Stack's combination of a declarative routing catalogue, deterministic gate closure and an asymmetric-scored eval harness, but six repos each solve one piece of a
  problem this project has not solved — most convergently, verifying that a dispatched persona stayed inside its declared `owns` after the fact.

# External orchestrator and skill-library survey

## Contents

- [Why this document exists](#why-this-document-exists)
- [Method](#method)
- [The question this survey actually answers](#the-question-this-survey-actually-answers)
- [Findings table](#findings-table)
- [The convergent finding: post-dispatch verification](#the-convergent-finding-post-dispatch-verification)
- [Per-repo notes](#per-repo-notes)
- [Skip list, confirmed not guessed](#skip-list-confirmed-not-guessed)
- [Proposed next step](#proposed-next-step)
- [What this document is not](#what-this-document-is-not)

## Why this document exists

The operator asked, off a list of 25 GitHub repositories surfaced in an unrelated broader search, whether any of them beat what Agent Stack is building. This followed directly from a same-session
read-only assessment of Agent Stack's own routing correctness and persona-boundary enforcement (see [MEMORY.md](../../MEMORY.md) and the memory-keeper entry
`agent-stack.boundary-enforcement-assessment`), which had already found the project's one real gap: three layers enforce persona boundaries at route-selection time — declarative `owns`, the
`[[precedence]]` discriminators, and `close_route.py`'s gate-strength closure — and nothing enforces them after a persona is dispatched. That gap is the lens this survey was run through.

## Method

Five parallel research agents each took five repos, briefed with the same Agent Stack baseline (routing catalogue, gates, deterministic closure, precedence rules, eval harness, governance checks) and
the same hard constraint: Agent Stack deliberately excludes autonomous loops, daemons, unattended background agents and consensus mechanisms, so a mechanism requiring any of those is not importable
as-is. Each agent was instructed to open the actual repository and quote load-bearing claims verbatim with file and line, not to answer from memory — several of the smaller repos are recent enough,
and two of the mature frameworks (AutoGen, Microsoft Agent Framework) have re-architected recently enough, that a remembered summary would be invention rather than evidence. One repo, evanca/skills,
returned a confirmed 404 on both the repo path and the raw file path, and is recorded as `UNREACHABLE` rather than assessed from a guess.

## The question this survey actually answers

Not "is any of these 25 repos bigger, more popular, or more capable than Agent Stack" — several are (Agent Zero has 19k stars, wshobson/agents has 39k). The question that matters for a prompt-layer
routing system with no execution runtime of its own is narrower: **has any of these repos solved, in a way that survives being stripped of its execution engine, a problem Agent Stack has not solved?**
Three sub-questions were seeded into the batches that cover the closest competitors: (a) deciding which agent owns a decision when two plausibly could, and preventing both from ruling on it; (b)
verifying after the fact that an agent stayed inside its declared remit; (c) evaluating routing quality against a corpus without the eval becoming circular. Batch 3's agent confirmed independently
that Agent Stack's 60-case frozen corpus with asymmetric gate scoring is ahead of every eval mechanism found across all 25 repos on question (c) — every other eval encountered was either an end-to-end
task-success benchmark or a single sample document with manual invocation.

## Findings table

NOTE: this table is hand-padded, not processed by `table-reflow` — that tool reproducibly corrupted this exact table three times (duplicating the file's frontmatter into every row while reporting
success). If this table is ever edited, unwrap by hand and re-pad by hand; do not run `mdtable wrap` or `table-reflow` on it. See the personal auto-memory `feedback_table_authoring_reflow_script` for
the full failure signature.

| repo                         | category                        | verdict                    | the one thing worth knowing                                                                            |
| ---------------------------- | ------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------ |
| Squad (mco-org/squad)        | Claude Code orchestrator        | STEAL                      | atomic compare-and-swap task claim with a time-boxed lease, daemon-free by explicit design             |
| anytools-agent-skills        | delegation skill pack           | ADAPT                      | required_model vs actual_model audit closes a route from "what was routed" to "what was honoured"      |
| MetaGPT                      | multi-agent SDK                 | STEAL (idea only)          | roles declare a consumes set of upstream artifact types; dormant project, scavenge the field           |
| AutoGen                      | multi-agent SDK                 | STEAL (idea only)          | two static graph validators plus candidate-set narrowing before the model chooses; project frozen in   |
|                              |                                 |                            |   maintenance mode                                                                                     |
| wshobson/agents              | multi-harness skill marketplace | STEAL                      | declarative per-harness capability matrix, catches a currently-silent defect class in our symlink-only |
|                              |                                 |                            |   install                                                                                              |
| Agency Swarm                 | multi-agent SDK                 | ADAPT                      | per-edge required-payload contract on a handoff, a gate class we do not have                           |
| AWS CLI Agent Orchestrator   | orchestrator                    | ADAPT                      | tiered outcome-to-profile promotion ladder, gives our field log a destination                          |
| Podiom                       | orchestration daemon            | ADAPT (narrow)             | typed capability access-request taxonomy with agents structurally barred from deciding their own       |
|                              |                                 |                            |   requests                                                                                             |
| gAIOS                        | skill template repo             | ADAPT (one clause)         | a reversibility/externality gate axis, distinct from our capability-strength axis                      |
| backnotprop/orchestrator     | CLI orchestrator                | ADAPT                      | runtime/model discovery with a declared fallback precedence ladder for requires_any                    |
| SuperClaude Framework        | Claude Code plugin              | ADAPT (cheap)              | Will / Will Not as an explicit declared negative-scope field, currently unenforced even in their hands |
| Agent Zero                   | autonomous agent framework      | SKIP                       | total autonomy dependency, the exact excluded category                                                 |
| Agent Deck                   | web orchestrator daemon         | SKIP                       | only novel field is a per-run dollar budget cap                                                        |
| BMAD Method                  | workflow skill installer        | SKIP                       | zero boundary declarations anywhere in the repo, weaker routing layer than ours                        |
| Claude Squad (smtg-ai)       | tmux TUI                        | SKIP                       | pure workspace management, no routing concept                                                          |
| LangGraph                    | graph runtime                   | SKIP                       | no role concept at all, entirely a runtime                                                             |
| CrewAI                       | role-play orchestrator          | ADAPT (cheap)              | expected_output as a required per-task output contract, bounded LLM-judge retry                        |
| Claude Flow / Ruflo          | Claude Code meta-harness        | SKIP                       | strictly poorer role schema than ours, plus every excluded autonomy class at once                      |
| Microsoft Agent Framework    | production SDK                  | ADAPT                      | declared directed handoff graph, permissive mesh-by-default is the failure mode to avoid               |
| Microsoft AutoGen            | see above                       | see above                  | see above                                                                                              |
| evanca/skills                | skill pack                      | UNREACHABLE                | confirmed 404 on repo and raw file path, not assessed                                                  |
| alirezarezvani/claude-skills | skill library, 25.4k stars      | coverage gaps + convention | SLO/observability and migration skills we lack; golden-file testing worth adopting                     |
| joeblackwaslike/agent-skills | skill library                   | convention only            | stamped doc-wrapper pipeline (source, fetched_at, sha256, PINNED_VERSION plus CI freshness check)      |
| heyimcarlos/agent-skills     | skill library                   | convention only            | writing-for-agents doctrine, sharper than our current SKILL_STANDARD description guidance              |
| fdarkaou/agent-skills        | skill library                   | thin                       | our exports layer already covers its one convention                                                    |
| carlkibler/agent-skills      | skill library                   | coverage gaps              | remote-host-verifier, dependency-pinning, agent-log-forensics                                          |

## The convergent finding: post-dispatch verification

Three unrelated repos, found by three different agents working from three different briefs, independently supply one-third of the same missing subsystem, and none of the three pieces requires a
daemon, a runtime this project does not control, or anything the safety model excludes.

1. **Declare the legal edge.** MetaGPT's `_watch({WritePRD})` (`architect.py:52`, `project_manager.py:41`, `qa_engineer.py:59`) declares which upstream artifact types a role consumes — pure data,
   checkable without a runtime. Agent Stack's personas declare `owns` (what they produce and decide) but nothing equivalent for what they may legitimately consume or hand off to.
2. **Claim it atomically.** Squad's `src/store.rs` performs the claim as `UPDATE tasks SET status=?1, lease_owner=?2, lease_expires_at=?3 WHERE id=?5 AND status=?6 AND assigned_to=?2`, checking the
   row count afterward (`ensure_task_updated`): zero rows updated means someone else already owns it, and the claim fails loudly rather than silently. Squad's own README states the constraint this
   project shares: "No daemon, no background processes — every command is a one-shot operation." `assigned_to` (the routing decision) is stored separately from `lease_owner` (execution ownership),
   which is precisely the distinction Agent Stack's `owns` (declared) and a dispatched persona's actual output (unverified) currently collapse into one thing.
3. **Verify it was honoured.** anytools-agent-skills closes a route from "what was routed" to "what was honoured" through a five-stage audit: baseline measurement, written instruction, sandboxed
   execution, file-manifest cross-check, full diff review, ending in one `required_model`/`actual_model` JSONL log line, with a read-only `--audit-all` mode. This is the piece Agent Stack's field log
   is currently missing — it records the route and the outcome, never whether the persona's output actually stayed inside what it was dispatched to do.

Two secondary mechanisms strengthen the same subsystem without being load-bearing on their own: AutoGen's `candidate_func` (`_selector_group_chat.py:180-193`) narrows the legal choice set
deterministically before the model chooses and then hard-fails if the pick is outside that set — the same discipline `close_route.py` already applies at repair time, applied instead at selection time
— and Agency Swarm's per-edge `extra_params_model` (`send_message.py`) puts required typed fields on a handoff payload, a gate class distinct from the capability gates Agent Stack already has.

## Per-repo notes

Full per-repo findings, including maturity signals, autonomy-dependency classification and verbatim quotes with file and line, are preserved in the five research-agent transcripts from the session
that produced this document (2026-09-03) rather than duplicated here. This document states the synthesis; the underlying evidence trail is the agent outputs themselves, referenced in `memory-keeper`
under the channel `agent-stack` if the raw per-repo detail is needed again.

## Skip list, confirmed not guessed

Agent Zero, Agent Deck, Claude Flow/Ruflo, BMAD Method, Claude Squad (smtg-ai) and LangGraph were each opened and read, not assumed. Each is either total-autonomy-dependent in a way with no separable
non-autonomous core (a daemon, a consensus mechanism, or a background swarm is the product itself), or has a role/routing model strictly poorer than Agent Stack's own. `evanca/skills` returned a
confirmed 404 on both `github.com/evanca/skills` and the raw `graph-orchestrator/SKILL.md` path, and is recorded as unreachable rather than assessed from a same-named guess.

## Proposed next step

This document is evidence and a proposal, not a decision. The concrete, buildable addition it points toward is a small extension to the existing routing catalogue and field-log machinery, not an
adoption of any external framework:

1. Add a `consumes` (or equivalent hand-off-legality) declaration alongside each persona's existing `owns` in `routing.toml`, in the spirit of MetaGPT's `_watch` set.
2. Give `persona_note.py`'s output-persistence step an atomic claim step modelled on Squad's compare-and-swap-with-lease, so two personas cannot both be recorded as having ruled on the same
   declaration.
3. Extend the field log's schema with a routed-vs-honoured verification pass modelled on anytools' `required_model`/`actual_model` audit, so a persona's actual output can be checked against its
   declared `owns` after the fact, rather than trusted on the strength of the prompt alone.

Whether to build this, and in what order relative to the field-use item already open in `SCRATCHPAD.md`, is an operator decision. A follow-on proposal document
([agent-stack-reliability-adaptation-proposal-20260903_1943.md](agent-stack-reliability-adaptation-proposal-20260903_1943.md)) has since sequenced these mechanisms as a phased, evidence-gated backlog.
This document does not itself make that call.

## What this document is not

This is not a durable architectural decision — those live in [`.archcore/`](../../.archcore/README.md), which remains this project's highest authority. It is not a record of measured figures — those
live in [`MEMORY.md`](../../MEMORY.md). It records what a source-verified survey found and proposed at 2026-09-03 18:49, and stands as evidence until superseded, per this working-documents folder's
own convention.
