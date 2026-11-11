# Revision History

Change log for the `skills_stuff` parent repository.

## Policy
- Any change to specialist submodule pointers under `specialists/` must include an update to this file.
- Submodules must contain their own `REVISION_HISTORY.md`.
- Pushes should use controlled workflows so rollback points are explicit.

## 2026-11-11
- `5dc0abc` (pushed `3adefce..5dc0abc`): descriptions of `skill-pad`, `skill-eval-manager`, `skill-knowledge-curator` and `skill-network-architect` shortened to 120-130 characters, quoted for
  YAML; the full original text moved verbatim into a `## When to use` section under each H1 (Token Optimizer clean-up, operator: "Trim non-routing skills only"; routing skills such as
  skill-coder, skill-drawio, skill-nautobot and skill-openwisp left long on purpose). Record and rollback: governance `reports/token-optimizer-changes-20261111_1325.md`.
- Finding: front-matter `disabled: true` (d2d14f1, 2026-11-10) is not honoured by Claude Code: a session started on 2026-11-11 listed `doc`, `agent-watchdog`, `devops` and other flagged skills
  with full descriptions. Codex's source (`codex-rs/config/src/skills_config.rs`) switches skills only through `[[skills.config]]` in `config.toml`. The switches that work are Claude
  `skillOverrides` in `~/.claude/settings.json` and Codex `[[skills.config]] name = ... enabled = false`; on 2026-11-11 the operator chose per-tool sets there (Claude: 90 name-only;
  Codex: 27 marketing skills and `vibeshell` disabled).

## 2026-11-10
- Committed and pushed the pending tree (operator: "can you commit all the skills_stuff?"). `44aad34`: skill-knowledge-curator's 2026-11-05 UNC pilot work (status_claims, merge_labels, locate_lines
  with tests; workflow steps 3b and 3c; 152 tests pass). `d2d14f1`: `disabled: true` in the front matter of 44 skills here, 1 in `stop-slop` (8efb958) and 11 in `superpowers`, with both gitlink
  pointers bumped. Disabled here: agent-watchdog, code-review-security, cold-email-sequence-generator, community-led-growth, competitive-intelligence-analyst, content-strategy, deep-reading-analyst,
  devops, doc, email-sequence, financial-unit-economics, find-skills, frontend-design (agent-stack copy), github-explorer, internal-invoice-analysis, market-sizing-analysis, micro-saas-launcher,
  ph-community-outreach, plan-arbiter, plow-ahead, premortem, pricing-strategy, product-strategist, prompt-master, quick-recap, read-the-damn-docs, scientific-critical-thinking, security-audit,
  senior-qa, seo-audit, seo-content-strategist, skill-project-wiki-rag-bridge, startup-business-models, startup-financial-modeling, stay-within-limits, tailwind-v4-shadcn, team, user-persona-creation,
  user-research-synthesis, ux-audit-rethink, visual-plan, visual-recap, web-scraping, websh.
- Incident: the flags were already on disk when the commit was asked for; the agent committed them without asking whether the disabling was meant, and a side agent's warning that writing-plans,
  executing-plans and verification-before-completion (named in the global AGENTS.md routing) were among them arrived after the commit. Asked then; the operator kept the disabling (answer "1"), then
  had those three re-enabled ("enable them", "the 3"): superpowers `309813f`, pointer `87e8f96`. Still disabled in superpowers: finishing-a-development-branch, receiving-code-review,
  requesting-code-review, subagent-driven-development, test-driven-development, using-git-worktrees, using-superpowers, writing-skills. The other skills the global routing names (brainstorming,
  systematic-debugging, safe-change-validation, skill-coder) were never disabled. Both submodule remotes were checked as the operator's (`amalikn/`) before pushing; pushed stop-slop
  `ce2acca..8efb958`, superpowers `0b28fd3..309813f`, then this repo `470f45a..87e8f96`. Neither submodule has its own `REVISION_HISTORY.md` yet (Policy line 2): open.

## 2026-11-07
- Added the platform specialist `skill-proxmox` 0.1.0 under `specialists/platform/` (operator: "create and setup skill-proxmox like skill-nautobot"): sixteen references, claim and environment ledgers,
  sixteen scenarios, offline package contract, three stdlib-only read-only helpers with tests, 51 verbatim source captures, the skill-ai-it governance layer; symlinked into `~/.claude/skills` and
  `~/.agents/skills` as skill-nautobot is.
- Added the platform specialist `skill-vagrant` 0.1.0 under `specialists/platform/` (operator: "create skill-proxmox and skill-vagrant based on the learnings"; "do online research to add more
  knowledge"): eleven references, claims V-C01 to V-C26, scenarios V-S01 to V-S14, offline package contract, three stdlib-only read-only helpers (lab inventory, Vagrantfile lint, copy check) with
  tests, 95 verbatim source captures, the skill-ai-it governance layer; symlinked into `~/.claude/skills`, `~/.agents/skills`, `~/.codex/skills` and `~/.hermes/skills/domain`.

## 2026-10-23
- Fix skill-commtracker `toc.py`: the Contents now lists all four entry types (Email, Teams, Call, Meeting) in file order, where Meeting and Call entries were silently dropped; a blank line is kept
  before `---`; anchors keep double hyphens for ` + ` and ` — ` and suffix repeated slugs; the block also ends at the next heading so a missing `---` cannot swallow the file. `--update` now refuses
  (exit 2) a Contents with fewer entries unless `--allow-shrink`. Five offline tests in `tests/test_toc.py` fail on the old code and pass (11 of 11 in the pack); a 16-entry tracker copy regenerates
  byte-identical to its hand-fixed Contents with every anchor resolving, in 0.04 s.
- skill-commtracker SKILL.md: Teams chats with several turns are one block per turn (no `---` between turns, no blank line after the label, lines joined by `\` hard breaks), the format the operator
  asked for on 2026-10-23 ("a lot of extra gap").

## 2026-10-16
- Extend skill-slurp-chat's existing helper for explicit Codex rollout JSONL: preserve repeated user turns, ignore mirrored messages, inventory tool names without arguments, and retain compaction/time
  filters. Five offline tests pass; the real UNC rollout smoke matches 36 messages, 388 tool envelopes and three compactions in 0.103 s against a ten-second budget.

## 2026-10-05
- Released `skill-nautobot` and `skill-openwisp` 0.4.0 after an independent assessment: eight new verified references (app development, data model, integrations, recovery; configuration management,
  connections and firmware, RADIUS, deployment and recovery), Orient sections, tested stdlib-only helpers in `scripts/`, and measured fleet lessons from the UNC capture corpus. `skill-cambium` 0.6.29
  and `skill-smc` 0.1.82 record the corpus's device facts.
- Released `skill-nautobot` and `skill-openwisp` 0.3.0: version-matched operations cookbooks with summary tables, a standing write-back contract enforced by the contract test, promoted OpenWISP
  evidence, new trap scenarios and a paired fresh-context evaluation (4 of 4 pass with the skill, controls partial).
- `skill-cambium` 0.6.28 and `skill-smc` 0.1.81 route platform questions to the two platform packs.

## 2026-10-01
- Revised both platform specialists to 0.2.0 with operational examples, source/compatibility distinctions, behavioral scenarios and corrected claim-to-scenario routing; runtime links unchanged.
- Added the canonical platform specialist packages `skill-nautobot` and `skill-openwisp` under `specialists/platform/`.
- Added their deterministic package/security contract tests, compatibility and provenance ledgers, routed references, evaluation procedures and root catalog entries.
- v0.1 uses runtime directory symlinks only; no generated exports, legacy `.codex/skills` copies, or Hermes installation were added.

## 2026-08-31
- Added `specialists/agent-stack/` as the canonical English-only pack for Auto Company-derived personas and skills.
- Adopted symlink-only installation; Auto Company's autonomous loop, consensus mechanism, daemon, settings, and prompts remain outside this pack.

## 2026-03-09
- Published initial `skills_stuff` parent repository.
- Added `specialists/project/skill-mx02-migration` as a Git submodule.
| 2026-03-09T06:42:22.260853+00:00 | main | origin | `5a6f2248b0f8` | Initial commit: skills_stuff with specialist submodule |
| 2026-03-09T06:42:22.260853+00:00 | main | origin | `2ac1f9a50eee` | chore: enforce revision history controls for living skills |
| 2026-03-09T06:43:55.457326+00:00 | main | origin | `daa0a1b34a82` | chore: ignore workspace metadata and sync specialist submodule |
| 2026-03-09T06:45:57.045216+00:00 | main | origin | `0658b98432cc` | fix(ci): fetch full history for revision guards |

## 2026-03-29
- Added top-level repository documentation for the expanded specialist and export layout.
- Added repo-local governance index material under `governance/`.
- Added new canonical project specialists and matching Codex export adapters for generator tracing, impact assessment, repo governance, repo knowledge capture, repo local guidance, and safe change
  validation.
| 2026-03-28T23:48:26.796690+00:00 | main | origin | `f1c31bf70930` | skills_stuff: publish new project specialists and codex exports |
| 2026-03-28T23:56:10.309731+00:00 | main | origin | `7447d4bbe01e` | docs(revision): record published skills_stuff checkpoint |
| 2026-03-29T00:12:51.388575+00:00 | main | origin | `d96f9ac7f92b` | skills_stuff: record follow-up parent publish checkpoint |

## 2026-05-24
- Created `skills/skill-project-wiki-rag-bridge/` — reusable multi-project bridge skill (48 files): SKILL.md, README, CHANGELOG, 14 templates, 10 numbered prompts, 4 schemas, 6 checklists, 7 docs, 2
  example projects (Vocus + generic). Governs wiki setup → domain creation → RAG tools validation → project bridge → policy validation → indexing → retrieval validation → troubleshooting.
- Updated `README.md` to add "Reusable Skills — skills/" section with table entry for `skill-project-wiki-rag-bridge`.
- Updated `AGENTS.md` Regular Skills table to register `skill-project-wiki-rag-bridge` and `skill-slurp-chat`.
- Created `_wiki/CLAUDE.md` governance wrapper (thin `@AGENTS.md` import, fixes missing entrypoint for wiki vault).

## 2026-11-09
- Governance files tracked (operator rule): the `.git/info/exclude` lines `AGENTS.md`, `.agents/`, `skills.md` removed; 22 AGENTS.md, `.agents/` and skills.md files committed (95bf5f2).
  repo-local-guidance 0.2.0 rewrite; repo-knowledge-capture 0.1.3. skill-proxmox gap review, refresh and archcore acceptance (9cbd227, bd2a566).
