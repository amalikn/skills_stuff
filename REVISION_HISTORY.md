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
- Front-matter `disabled: true` removed from all 53 flagged skills (operator: "Remove them"): 43 here, `superpowers` `e987f39` (8, pushed `309813f..e987f39`), `stop-slop` `f20e051` (1,
  pushed `8efb958..f20e051`), both gitlink pointers bumped; `diagram-design` (third-party clone, `cathrynlavery/diagram-design`) edited in the working copy only, its local description edit kept.
  The working switches now hold the intent: Claude `skillOverrides` gained `subagent-driven-development`, `test-driven-development`, `using-superpowers` (93 name-only); Codex disabled 15 more by
  name (`agent-watchdog`, `find-skills`, `plan-arbiter`, `plow-ahead`, `prompt-master`, `quick-recap`, `skill-project-wiki-rag-bridge`, `stay-within-limits`, `tailwind-v4-shadcn`, `team`,
  `ux-audit-rethink`, `visual-plan`, `visual-recap`, `websh`, `web-scraping`; 43 entries). Kept on in Codex by operator choice: `premortem`, `security-audit`, `code-review-security`, `senior-qa`,
  `devops`, `read-the-damn-docs`, `using-git-worktrees`, `finishing-a-development-branch`, `requesting-code-review`, `receiving-code-review`, `scientific-critical-thinking`,
  `deep-reading-analyst`, `github-explorer`. Re-enabled earlier the same day in Claude and left on: `doc`, `stop-slop`, `writing-skills`.

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
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f3a8ae9c8f0d` | skill-slurp-chat: transcript_passes lists slash commands with their arguments |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ab7c28b5e574` | skill-ai-it: pitfalls from the skill-goal-guard bootstrap; upgrader placement idea |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `47740d182401` | skill-drawio: ROADMAP design for folding long flow pages |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `585c2e2e080b` | skill-goal-guard: slurp close (late evening): findings, proposals, open decisions |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `6e00c98310b7` | skill-drawio: fold long flow pages; lane margins; quoted code excerpts restored |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `81e62a5b5a1f` | skill-goal-guard: SCRATCHPAD open items after the fold slurp |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `cdce4fa1a736` | skill-knowledge-curator: new skill (alias skill-kc), v1 kc kernel, references, tests |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7980fe622639` | skill-smc 0.9.1: tracker review, staleness audit, scripts by job |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a56dd0ee2a71` | skill-knowledge-curator: v2 spec catalogued, conflicts V1-V9 settled, v2 staged roadmap |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `64a664243ac6` | skill-ai-it: staleness audit, scripts in family folders, callers repointed, skill-coder gates |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `cbb0d7e6576d` | skill-smc 0.9.2: rct-tstik iridium change write-back |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `765c2f802981` | skill-smc 0.9.3: AVR serial collision verified on warehouse-rct01 |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0511ccee6e07` | skill-coder: process_match.py makes unanchored pgrep/pkill -f a check |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b37254b22ece` | skill-coder: ROADMAP rotation counterpart of roadmap-20261028_1311 |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8d11e65202ca` | skill-smc 0.9.4: automated AVR flash, probe self-match, resume_safe |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `6751ad6bc147` | skill-smc 0.9.5: AVR V3.07 loses the Thuraya board SIM; fleet AVR state |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `62ba5d889ad3` | skill-smc: FirmwareV2.14Test.enc is the fleet's V2.14 build (Chris Blair) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d830d2dc7037` | skill-smc 0.9.6: rct_avr_probe.sh (RCT AVR firmware per SMC) and AVR routing row |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `bc3af7a6c2b1` | skill-smc: Ansible sftp/scp transfer warnings on a satellite SMC fall back to piped |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `13eb173d091b` | skill-smc: rct AVR flash needs smc_bases_iridium as well as rct_avr_flash |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `cdb6d54c5b2c` | skill-smc: rct AVR flash skipped without the Iridium flag still passes; set the flag first |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c3e856b691cc` | skill-smc: hourly PIN funnel script and 14.9 change-or-upstream triage (Galiwinku 2026-10-28 squid fail-open) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4b61a2d8ee30` | skill-smc: pin-fleet-check one line per SMC after a change batch; 14.9 iptables/cron/conntrack ruled out |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8ee6e1c86fcf` | skill-smc 0.9.7: runtime budget counts the wait for earlier batches; CHANGELOG for pin funnel and fleet check |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7b583412e711` | skill-smc: Galiwinku stall root cause, squid intercept listener stops accepting after ORIGINAL_DST failure (upstream match) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ea85b6e7baee` | skill-smc 0.9.8, skill-coder, skill-repo-knowledge-capture 0.1.2: apt lock findings and tools |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c9a9ed19c712` | skill-coder: Learned - a symlinked source ships whatever is checked out (2026-10-28) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `13e2d999997f` | skill-coder: Learned - shared justfile recipes and the editor (2026-10-28) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `87f5356b500e` | skill-drawio: placement searches (E2E columns, overview rows, overview group grid chosen by real routed crossings); skill-coder Learned: optimise the real outcome, not a proxy |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `e7e55b639495` | skill-drawio: engine performance review (read-only; shortlist for approval) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4a6e333aa794` | skill-drawio ROADMAP: layout quality analysis (open) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3838be046577` | skill-openwisp: Learned 2026-10-29, rename the CSRF cookie too beside another Django app on one host |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `96ea159588d7` | skill-smc v0.9.9: ha capture group, -smcNN hosts and --proxy in collect-smc-evidence-full; aurukun VRRP layout learned |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b9910548c1aa` | skill-nautobot: native VRRP across boxes (Device/Interface Redundancy Groups) learned; skill-cambium: cnWave 1.2.1 SNMP identity and E430W model name learned |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `e6213cde434b` | skill-smc v0.9.10: TP-Link switch driver falls back to legacy SSH algorithms for IPSSH firmware (SG2428P 4.0.1) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4cd8d1082b79` | skill-smc v0.10.0: version corrected (0.9.10 broke the single-digit patch rule) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f823240710e4` | skill-smc v0.10.1: ssh_handshake_probe (SSH a device behind an SMC offers, no login); changelog rotated |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `12a3ad88e5f4` | skill-coder: learned, a check that skips when its tool is missing cannot fail |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `6aef689c3590` | skill-ai-it: roadmap items, rotation leaves stale Contents lines; script move broke a consumer's git hook silently (found in unified-network-controller) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7373a62d579b` | skill-cambium: schemas DIVERGENCE/README/SWEEP-LOG reviewed 2026-10-29; cnWave SNMP silence is per unit (learned) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3cce1bb4d555` | skill-smc v0.10.2: FDB and VIP placement evidence; TL- model prefix on old SG2428P firmware |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b1e1fd7c6a51` | skill-coder: patterns P-33 to P-35 (read all then write once; pick a moving leader once per cycle; place by evidence) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `245ead08f86d` | skill-ai-it: roadmap item, budget pass dropped an undecided open item (found in unified-network-controller) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `5e2eb3b21580` | skill-drawio: skip the unread crossing count on search undo (perf B; UNC 18.3 -> 14.9 s, three consumers byte-identical) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2783eba896a6` | skill-drawio: count_crossings --compare parses each file once (perf F; UNC vs res 4.1 -> 0.33 s, outputs identical) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `73017a9b9697` | skill-drawio: E2E vertical-run spans kept current in _refresh (perf C; UNC 14.9 -> 12.0 s, byte-identical; stale-cache assert never fired on 3 consumers + tests) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `10e4080cfe35` | skill-drawio: one page build serves render and audit; --write --audit in one pass (perf H; UNC write+audit 24 -> 12.3 s; renders byte-identical; audit now reads the drawn flow pages with family labels) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b0facdf37837` | skill-drawio: flow_quality defaults to the renderer's schema (failed on any map run without --schema) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `5f1d30171e75` | skill-drawio: E2E port index remembered and checked before use (perf E; UNC 12.0 -> 11.7 s, byte-identical; probe matched every lookup) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `811c9184c489` | skill-drawio: E2E crossings memoised per pair of distinct polylines (perf D; UNC 11.7 -> 9.5 s, byte-identical, 211 MB peak) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4fc3f3b2db89` | skill-drawio: revert perf E (0.3 s on UNC; e2e_grid.py back within the 400-line rule; operator: time efficiency is not the goal) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `1e6557df91bc` | skill-drawio: layout quality baseline (layout_quality.py) and real-route guards on both placement searches |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b108050a742e` | skill-drawio: schema descriptions of the three search look keys say the real-route guards |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `29b39aa93d08` | skill-coder: patterns P-37 (cache proved by a differential assert) and P-38 (estimate nominates, real measure decides), from skill-drawio |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7bc0c3e5bfce` | skill-drawio: consumer_check.py + consumers.yaml (every consumer rendered to scratch and compared; goal-guard proved identical), Learned real-route guards with UNC screenshots, ROADMAP in-group arrows, review status |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0a98dc83fbf6` | skill write-backs from unified-network-controller 2026-10-29: Nautobot relationship type-change migration, cable_peer front port, beat schedule refused, null-vs-absent; TP-Link firmware CLI dialects + LLDP off 5/6 + unknown Pi; Cambium LLDP/CDP per family; coder P-36; device-login-probe empty-user fix |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `444c3a0da990` | skill-cambium, skill-nautobot, skill-coder: write-backs from the UNC placement engine (E500 LLDP CLI, 3.2.3 filter names, pattern P-39) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ab9b2fb4a299` | skill-network-architect and skill-systems-architect v2.0.0: adopted into skills_stuff, deepened and enforced |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `6bb262eda4bc` | skill-network-architect, skill-systems-architect: scratchpad records commit and install |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a78c04ef8add` | skill-nautobot: a site's Cables read by device_id; interfaces location= is the exact Location only |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `6995542b66eb` | skill-knowledge-curator: SCRATCHPAD and changelog from the 2026-10-27 20:30 slurp (pending since then, committed as its next action asked) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ba56a3812f4b` | skill-network-architect, skill-systems-architect v2.1.0: gap closure (helpers fibre, power, restore, eol, ESP MTU, combined quorum; LIPD 6 GHz, DFS, reach and Windows dates verified; databases-and-ha, ai-inference-platforms; 9 templates; filled examples; section routing; merged link definitions repaired; fair eval rerun). skill-mikrotik: skill-smc script paths. |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `eb4baf145ef0` | skill-cambium: apn-cnmaestro01 is the only cnMaestro; cw-cnmaestro01 answers but holds no aurukun devices |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b6f399f6e4f9` | skill-slurp-chat: pass 3 reads every sub-agent (operator rule); skill-coder: know what the commit gate runs |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8ca76c011b49` | Closeout 2026-10-29: architect packs AGENTS operator rules, incidents changelog, scratchpads; skill-eval-manager blind_ab.py (blind A/B grading, just blind-ab, v0.1.10). Note: b6f399f carried this session's v2.2.0 and write-back files under a concurrent session's message. |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `06cc32392c14` | skill-commtracker: Learned 2026-10-30, Outlook desktop signature logos (image001.png with a cid) pass extract.py as substantive; judge them from the body |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `650863b00760` | skill-smc 0.10.6: apt_pin install_missing; controller lookups and pinned PHP; Teleport duplicate node after a data-dir wipe |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0e078a922607` | skill-coder: Learned 2026-10-30 (filter precedence, free-form shell splitting, import_tasks placement, pipefail with grep -q) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `102fafce1874` | skill-coder: P-46 audience words at the output boundary, with a leak guard (from unified-network-controller site workbook, 2026-10-30) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `40d82d8d12b8` | skill-smc 0.10.7: rct-tstik AVR data map and build labels, smc_change facts/conditions/when/loop, rct_avr_probe modem fields |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d84d9e9f23ff` | skill-coder: P-47 decide once from facts and persist the decision; Learned ansible (d) run_once set_fact freezes templates, (e) 2.21 Jinja quirks |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `441f6e777e65` | skill-coder P-47 and skill-smc 19: read a fact only where the step that uses it may run (local-knowledge-ansible 11348bc) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7f4d0e3621f0` | skill-coder: Learned ansible (f) non-blocking stdio in git hooks (ansible-wifi pre-push, 2026-10-30) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f1de0bb4e2d1` | skill-smc 0.10.8: porting the PHP fix to a master-based branch; pre-push traps |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0e41165d2fee` | Continuum write-backs: curator pilot findings, immutable sweep marker, gate output lesson |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7b5280a7c9be` | skill-ai-it: ROADMAP confirms check blind spot before first commit (Continuum) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `9b0c221a2f06` | skill-smc 0.10.9: overlayroot.conf vs local.conf, Teleport vars on the disable path |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `26302bc8b0d7` | skill-smc 0.10.10: one failed apt source and smc_bases; apt module versus apt-get update |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `1e57ed4c7906` | skill-slurp-chat: read every sub-agent report in full (--reports), route flagged items, reopen after later work; skill-kc P18 |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b712ba8829eb` | skill-smc 0.10.11: apt-get update fix reaches rise |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7e2720200d42` | skill-smc v0.11.0: smc_change reporting and fallback, kernel drift, stats 2.11, pre-push venv, smc_boot_kernel probe; skill-coder: Jinja and CRLF traps |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4b25becae48c` | skill-smc: kernel fix on rise 8684e5ec |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `5a7f1e739346` | skill-smc v0.11.1: changelog heading and version for the kernel fix |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a4381d78d90b` | skill-smc v0.11.2: smc_qos stays on the meta-package, why uname -r misleads |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f819ff31dee0` | skill-knowledge-curator: Continuum pilot fixes in the kernel |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `22b2129629ec` | skill-knowledge-curator: docs for the Continuum fixes, gate 0 passed, findings P19-P25 |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4ba5540b6ab3` | skill-knowledge-curator: wrap new prose at 200 columns |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3f29b6d132dc` | skill-knowledge-curator: amend docs note scratch copies need real sources |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7d0e6a1eb774` | skill-knowledge-curator: scratchpad records kc amend proven on the live Continuum ledger |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `34d20c00f252` | skill-knowledge-curator: decide refuses to revive a superseded claim (P26), P25 refined from Continuum counts |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `dc0a523e0111` | skill-knowledge-curator: decide keeps a standing successor, kc amend --set-successor repairs a link (P27) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `1af225be4190` | skill-knowledge-curator: multi-valued predicates, group review, kc drift, stale conflicts (P25, P18, P21) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `e3ecb1909f12` | skill-knowledge-curator: scratchpad records the live successor repair |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `fed597a34d54` | skill-knowledge-curator: MCP audit pilot, cross-agent recall unsolved (P28, P29) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `467a6f17fc47` | skill-knowledge-curator: subject-word groups in decision-points (P28), gate 0 reopened |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `30dc8a98dadb` | skill-knowledge-curator: ledger_diff, end-state diff for rehearsing decisions |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4567d4aa5303` | skill-knowledge-curator: gate 0 pass mark fixed before measuring |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8838ecffe545` | skill-knowledge-curator: kc aliases for consolidation, kc recall harness |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `1b0fd6db3b5b` | skill-knowledge-curator: kc topics, the relate agent's reading view |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `fd5929148c86` | skill-knowledge-curator: gate 0 failed on the labelled MCP pilot (44.4%), findings P30-P32 |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `41888c369b5a` | skill-knowledge-curator: close 2026-11-01, restate_byte_copies, relate procedure, write-backs |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `651b40405cd8` | skill-knowledge-curator: kc topics --by-file |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `914ee4ae6f90` | skill-knowledge-curator: second relate route, gate 0 still failed at 62.2 percent, stopped |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f392b8a427f4` | skill-knowledge-curator: third gate attempt, marks fixed before measuring |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ece24ba0e4e7` | skill-knowledge-curator: overtaken warnings, dated-order proposals, byte copies in views (P30-P32) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `62f0c795c967` | skill-knowledge-curator: aim is knowledge without noise, precision measured at 27.5 percent |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `246c64b433e1` | skill-knowledge-curator: triage rule, automatic resolution limits fixed before building |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `811352843921` | skill-knowledge-curator: kc sample, status-map and triage, research items B0-B2 |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `1ec0e57a71cb` | skill-knowledge-curator: third gate attempt failed, triage stays a proposal; close and write-backs |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c3c4f1bafb25` | skill-coder: rotate CHANGELOG within budget after the 2026-11-01 write-backs |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `9ee45ccb64bd` | skill-eval-manager: Learned on briefing outside researchers; CHANGELOG rotated within budget |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `162797ab8f7a` | skill-knowledge-curator: four external research reports for a later chat; close |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a7cb44b0a759` | skill-knowledge-curator: fifth external research report; mcp-data cause confirmed |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `242e81c669a3` | skill-smc v0.11.3: AVR emergency and SMS numbers; skill-coder P-48 read-modify-write for one-frame devices |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d1ab693c7903` | skill-smc v0.11.4: smc_change specs, trackers, shared scripts, AVR numbers; skill-coder EXIT trap, ruff symlink, P-49; skill-drawio audit lesson |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `43df87188656` | skill-drawio flowcharts, swimlanes, BPMN and flow trace; skill-coder engine composition |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8d0cae8c38ec` | skill-drawio charts: left-side arrows, branch swap, sideways hand-offs in lanes |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `94ec32685aa6` | skill-drawio lanes: each diamond keeps the way out that measures cleaner |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `57813b69b176` | skill-drawio lanes: column order by shortest hand-off, left exits, BPMN in the step-page colours |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ea9e5a865533` | skill-drawio: horizontal lanes and BPMN by default, :vertical per chart; lane order, left exits, step colours; review stamps say agent review |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ba6fc832fc15` | skill-drawio: fold inside a lane (fold: lane), notes stacked by column |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3086460d842f` | skill-drawio lane fold: room under a row running back; tests fixed |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3dbb05f2cc4f` | skill-drawio slurp close: engine defaults, both-side arrows, bold labels, layout rules written back; skill-coder testing lessons |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3682a0d6f65c` | skill-smc, skill-coder: update:stats cron standard, port guard after cron starts, checked crontab write |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `9b1be72c7d31` | skill-drawio: click isolation on boxes and arrows, band swap search, ground-colour label backgrounds, legend split (earlier session 2026-11-02) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2a1979ac1052` | skill-smc, skill-coder: skip, probe or force; per-SMC close; rebuild lock; -l host absent from the inventory |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `6a5a2ec88327` | skill-smc 0.11.8, skill-coder P-55: smc_change chaining, per-change state dicts, named value files (ansible-wifi 2026-11-04); skill-smc also commits the 2026-11-03 session's tsh --proxy note in 01_overview.md; skill-coder backfills four missing CHANGELOG lines and fixes two malformed 2026-11-02 headers so just test passes |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `575494adcd5f` | skill-smc: smc_change flows reviewed, chain withdrawn and archived, include plan proposed (2026-11-04) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `078ea8258308` | skill-smc 0.11.9: smc_change self-repair, every-goal rule, applies_when, trace recipe quoting; skill-coder ansible.md (h): facts persist across plays per host |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ec19686a6e9f` | skill-smc: Iridium sites flashed in advance of the hardware swap; Thuraya SIM loss accepted (2026-11-04) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `5894b29dae42` | skill-smc: smc_mark_iridium.py (+ recipe, catalogue); ref 19 batches 1-3 Iridium marks, deploy does not flash, long site names miss -l |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `700cdfccd310` | skill-smc ref 19: smc_rise_deploy now sets rct_avr_flash on the iridium import |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `055ed53a38e9` | skill-smc v0.12.0: shelfo-crossing chain canary and silent-skip failure (ref 19), smc_change_multiple.yml (ref 18), smc_mark_iridium tests and recipes |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `72b5d7c0807d` | skill-smc 0.12.1: smc_change Teleport login gate; skill-coder: run_once gate needs any_errors_fatal |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `fca8e4b8b36a` | skill-ai-it ROADMAP: budget audit reports LOST lines that are present (2026-11-05) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `e323ad86e99a` | skill-smc, skill-coder: write-backs from the 2026-11-05 slow smc_change batches |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7be9fc4cd932` | skill-smc 0.12.2: v8 resumable PCAP fetch, EFS find, Teleport path loss probe; skill-coder: Ansible find depth, async limit, extra vars |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `122ae9485bcc` | skill-smc: smc_change_parallel.sh (one run per SMC, all at once) and the cross-import fact carry-over finding |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `cfca2a5f9f4f` | skill-smc ref 09: first real v8 fetch passed (APN 202610, 17 tars, 10 GB, size-checked, gzip-valid) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a4a87fa6f1ca` | skill-smc CHANGELOG: first real v8 fetch passed (ref 09, cfca2a5) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0ed60e98b2d6` | skill-smc ref 19: cross-import carry-over covers groups too; fix held in the smc_change patch |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `900c2f8159d2` | skill-ai-it: mirror_skills install script, its test and 20261103 history rotations (left uncommitted by the 2026-11-03 session; CHANGELOG entry 20261103_1741 already committed) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `aeb52b86a5f1` | skill-ai-it: agents_chain check (AGENTS.md chains for Claude Code and Codex); skill-smc: post-run facts |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ebc6a9dbeaf5` | skill-smc, skill-coder: smc_change free strategy and carry-over write-backs; role_stale_facts.py |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `cc9a60a35c5a` | skill-smc 0.12.3: ref 09 Learned 2026-11-05 (b), DNS capture contents, gaps, measured sizes and pcapfix cost; records plan pointer |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d77ffc2e8d02` | skill-smc ref 09: v8 promoted over v6 after the 202610 process run |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ac7d7adb51a6` | skill-smc: smc_gateway_loss.sh site-link survey (4 of 20 rct sites lossy, not Sky Muster-wide); smc_change_parallel.sh checks SMCs at once with progress and a status line a minute; ref 06 entry |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `5713ce3c96b6` | skill-coder shell.md: Learned 2026-11-05 (ii), remote probe on stdin, parallel host checks with progress |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `503d1654e5e1` | skill-smc ref 13: Bitbucket SSH host change on 2026-11-12 (banner seen on gurrbalgun-smc01) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `cb7015059622` | skill-mikrotik 0.1.34: packet capture and DNS visibility in reference 08 |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `242d3430be3a` | skill-smc ref 19: change bitbucket-ssh-hostname for Bitbucket's 2026-11-12 SSH host move |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0cf176792e69` | skill-knowledge-curator: kc roots and kc verify (research B3, B4), oMLX model arm, documented-evolution |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d40e972c1d2a` | skill-ai-it: adopt_governed_files matches the check recipe by exact name |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0379df3e18c7` | skill-smc: smc_gateway_loss.sh -s (download speed, slow link vs slow destination); ref 19 rollout-audit method |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c0162a590eab` | skill-slurp-chat: commit write-backs with a pathspec in the shared skills repo |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a5277e6dcc41` | skill-knowledge-curator: citation_audit and decision_sheet from the Continuum P0 pass |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2016a8a776ed` | skill-knowledge-curator: close record; note that 0379df3 carried this session's staged close |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4ee02cf7708f` | skill-smc ref 13: Bitbucket move scope includes Jenkins ssh:// URLs and known_hosts tasks; fix branches prepared |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f8ce67763699` | skill-knowledge-curator: citation_audit handles claims with no evidence |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `996395f251a6` | skill-ai-it: a rule moved out of AGENTS.md leaves a one-line summary; ROADMAP idea for line-range moves (ansible-wifi, 2026-11-05) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `54643dcc2965` | skill-coder: Learned 2026-11-05, tracked-only checks after first commit; regex hyphen boundary |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `e822dd055098` | skill-knowledge-curator: decisions_to_adrs renders Archcore ADRs from decision chains |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `e081701a0f8b` | skill-ai-it: promote step learns quoted front matter, Last reviewed and decisions_to_adrs |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `17864a1e42fa` | skill-slurp-chat: read the post-commit check before pushing |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `01030c890ad3` | skills: write-backs from smc-resiliency S2 (2026-11-06) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `9bbcd3d5d983` | skills: write-backs from smc-resiliency S3 (2026-11-06) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `46a0697fe56f` | skill-commtracker: Learned 2026-11-06, Outlook web signature images (image.png, UUID Content-ID) pass extract.py; judge from the body |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c43643ef9086` | skill-ai-it: ROADMAP, budget audit LOST false positive seen again 2026-11-06 (enterprise-strategy) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `613c1c1348ec` | skill-smc: 19 smc_change, resumed runs keep the first start; tracker orders by attempt_start |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `1a11ce236fe7` | skill-drawio: parallel band search and render cache; write-backs from UNC 0.8.53 |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7817c86e0049` | skill-drawio profile_render; skill-coder per-check budgets; two Learned entries brought to the entry format |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3537205a4904` | skill-smc 0.12.6, skill-coder: smc_change export to a company task file; resumed runs ordered by attempt |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `477c0d1650f6` | skill-smc 19, skill-coder P-59: export backs up only when an action will change something; skill-ai-it ROADMAP: LOST audit recurred |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a680b80e4389` | skill write-backs from smc-resiliency S3/SM (2026-11-06) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0512d528cf20` | skill-drawio: crossing count through a grid index (byte-identical); SETUP variables; an entry brought to format |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4537d7a2eb2a` | skill-drawio: the 2026-11-06 column-order and cloud-text entry is UNVERIFIED until its author confirms |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8e38111f8f0b` | skill-drawio: a folded row draws only its own lanes (look.fold_lanes, default used) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `1deaf4e13c60` | skill-smc 0.12.8: ansible-wifi smc_bases on Ubuntu 24.04 and in an image build; skill-drawio: evidence label set by its author |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `005b25a1cb67` | skill-ai-it: adoption warns with the trim route when a new file budget is already exceeded |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `91bba4d16e56` | skill-drawio: close flow colours on a family page (candidate) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f9e30e8abc16` | skill-drawio: End-to-end flow colours spread by CIEDE2000 so flows sharing a box differ (on by default, consumers re-rendered); legend rows link to step pages; colour maths moved to flowmap/colour_math.py; goal-guard drawing re-rendered |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2528b67b6967` | skill-slurp-chat: red flag, a review date only after a full re-read (2026-11-06, apn unified-network-controller) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c990ca544ebe` | skill-drawio: step boxes no longer overflow (step_chars 38, shape width factors measured); a flow can pin its colour; palette_check --map; goal-guard re-rendered |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `e4a374978252` | skill-drawio: a decision diamond is twice its text's height so the text stays inside (operator, 2026-11-06); example re-rendered |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b49828817173` | skill-drawio: cloud step boxes centre their text with wider margins so it stays inside the outline; Learned entry; example and goal-guard re-rendered |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `92163b359d48` | skill-drawio SKILL.md: an engine change that alters drawings runs consumer-check and tells every consumer (2026-11-06) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `dc96e7b37939` | skill-drawio: look.step_pages (a family chained on one folded step page before its first flow page), family chain: all, look.chart_tab, refusal ends stop a chain, chained steps keep their names; SKILL.md runner fix; consumers re-rendered |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `bd1691d9a00e` | skill-proxmox and skill-vagrant 0.1.0 (new packs from the smc-resiliency labs); skill-coder: hcl.md, language_split.py (ansible and shell split into topic folders), P-61, language per environment, two-space scaffold |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8d0dcaa55f44` | skill-drawio: straight arrows to the next step first, labels by a diamond's outline and off lane edges, End-to-end left channel for first-column links; compact diamonds and store insets |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d92937f4d717` | skill-drawio: End-to-end labels that overlap are placed again, least room first (place_labels); a label with no clear spot takes the one over the fewest lines |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ec2757e386e7` | skill-proxmox and skill-coder write-backs from smc-resiliency X2 (2026-11-07): OVMF entry deletion and the watchdog deny-list, with the recreate excerpt; bpg watchdog and boot_order; skill-coder python and design-pattern notes; skill-coder SETUP.md re-read against the justfile (language-split added; nothing in setup changed) and re-dated |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `217948899838` | skill-drawio: route_probe.py (router choices and final routes for one flow page; promoted from the commission-gps debugging), justfile route-probe, catalogue rows, RouteProbeTests; ROADMAP item for a label on a run near a lane edge |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f7677a0b8eea` | skill-drawio: add scripts/route_probe.py (left out of the previous commit: an untracked file is not taken by a pathspec commit) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `cfae5e286892` | skill-proxmox SCRATCHPAD: commit item done (bd1691d); open item for the pack's failing governance check (header summaries, AI_NAVIGATION budget, archcore review dates) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d3d988fd95e6` | skill-slurp-chat: commit the parked private_commit work (scripts/private_commit.py, its test, justfile recipe, catalogue row, SKILL.md sentence; written 2026-11-05 by an earlier session, left uncommitted, 13 tests pass) and the 2026-11-07 rule that a pathspec commit skips untracked files, so a new file is added by name first |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2c713d23cabc` | skill-drawio: a step page's ‹ E2E page button to its family's End-to-end page or the full one (look back_button; e2e_family back_target, back_button); BackButtonTests; SETUP.md re-read against the justfile (route-probe added) and re-dated; example re-rendered |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3ec22cc0d757` | skill-drawio: page_audit counts note cards as boxes (NoteAuditTests); ROADMAP operator-review and notes-band items done with evidence (no consumer crosses a note; the State file and /data/confexts corridor gone with the left channel); CHANGELOG for the back button and the notes audit |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `5688025511da` | skill-goal-guard: flows drawing re-rendered with skill-drawio 3ec22cc (no page worse: crossings 29 to 25) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `38f551810c26` | skill-proxmox: Learned 2026-11-08 (iTCO_wdt on a q35 guest, explicit modprobe past Ubuntu's deny-list, a crash reset in 91.1 s, with the X1 excerpt); skill-coder: testing.md Learned 2026-11-08 (read an injected fault back; retry only the transport's failure) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2b8085d0ac76` | skill-coder: safety-and-writes Learned 2026-11-08 (write, fsync, rename is not crash-safe on FAT); skill-vagrant: parallels-prlctl Learned 2026-11-08 (prlctl exec joins arguments, Tools refusals, stdin uploads, lvextend with a read-only /etc), open item for its pack check |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `cde2ca9e0349` | skill-smc 0.12.9: Pi 4 serial console (pins, BOOT_UART, uart_2ndstage, enable_uart; Raspberry Pi docs) with the lab recorder excerpt; CHANGELOG rotated; skill-coder testing.md Learned 2026-11-08 (b): read_text hides CRLF, a raw pty for serial tests, termios without pyserial |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `9cbd227603ff` | skill-proxmox: gap review with online research and skill-ai-it refresh (2026-11-09) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `bd2a566a5ff0` | skill-proxmox: archcore review, six documents corrected and accepted (operator, 2026-11-09); version-restated check; skill-coder testing.md Learned 2026-11-09 |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `80effd6401b5` | skill-vagrant: every provider (VirtualBox, vagrant-qemu, vagrant-libvirt), 2026-11-09 research, lab-run write-backs, Archcore accepted |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `95bf5f24bb8c` | Track governance files; repo-local-guidance 0.2.0 rewrite (operator, 2026-11-09) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `600c9a50ae3e` | write-backs from unified-network-controller (audit follow-up session, 2026-11-09) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7159792947ba` | Slurp close 2026-11-09: skill-proxmox record and write-backs |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `99f2ac847a36` | skill-proxmox session record: second close (commits of the first close; pre-rule live sessions follow-up) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `553d80310985` | skill-nautobot: nautobot_template_exposure.py (read-only advisory exposure check) and Learned 2026-11-09 on app-wide extras grants |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `dd0b695cb137` | skill-proxmox: archcore promote, accept all (operator, 2026-11-09) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `81c8a7ff3cac` | skill-proxmox session record: workspace mirror, promote, push rule, pre-rule sessions messaged |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `528db8756494` | Slurp close 2026-11-09: skill-vagrant flows, code map, archive record; write-backs to skill-coder, skill-ai-it, skill-drawio |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d96baa0fde75` | skill-coder: write-back from smc-resiliency follow-up audit fixes (2026-11-09) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `432023aa66f8` | skill-vagrant session record: second close (commits and pushes of the first close, peer acknowledgement) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3dde4fafdbbf` | skill-proxmox session record: 12:00 exclude restore confirmed as the skill-vagrant session; skill-ai-it AGENTS.md review open |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3bdce078fef6` | write-backs from unified-network-controller (N01 session, 2026-11-09) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `1aa6e7f77f97` | skill-ai-it: adoption keeps a legacy-header value hard-wrapped onto an unindented line inside the fence (wrapped_continuation; 2 tests, red on the old code) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c843e7229cbf` | skill-proxmox SCRATCHPAD: read-only lab probes blocked (node unreachable from this network); probe set recorded |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f719d5d5c27c` | skill-proxmox: third slurp close (record rows 28-31; probes-blocked CHANGELOG line) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `300ec45f5d28` | skill-nautobot: narrowing a writer grant removes view too; check readers as well as writers (from unified-network-controller N01, 2026-11-09) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0595fe37bdfa` | skill-smc: smc_change rollback_over_apply, the Jinja line-break trap in value files, bitbucket-ssh-hostname canary passed (2026-11-09) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `e03de035b61e` | skill-slurp-chat, skill-ai-it: ask project-context for the detail they need |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f4b2d15a7582` | skill-coder: write-back from tools_stuff cline (P-63 agent benchmark with a real-repo and submodule watch; security: a disposable CLI config can fall back to a cloud default URL); CHANGELOG rotated within budget |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8987b843a0d7` | skill-smc 0.13.0, skill-coder: write-backs from smc-resiliency S1 bench and N03 (2026-11-09) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `fef28d305dac` | skill-systems-architect, skill-network-architect 2.3.0: smc-resiliency S1 write-back; APN operator context extended; overlap rule |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d55f5441e1ac` | skill-systems-architect 2.3.1, skill-coder: flash-step write-back from smc-resiliency (2026-11-10) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8c33b83f89c5` | skill-smc 0.13.1: Pi 4 on the fleet bootloader 2023-01-11 (autoboot.txt on GPT, tryboot chain, EEPROM update from the selected boot partition); CHANGELOG rotated |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f50418706d70` | skill-smc 0.13.2, skill-systems-architect 2.3.2: deployed Pi fleet layout and in-place conversion method (smc-resiliency, 2026-11-10) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `662b20de6fa9` | skill-systems-architect 2.3.3: measured Qwen3.8-27B on oMLX, prefill-peak rule, hybrid prefix-cache blocks (write-back from tools_stuff d88d77b) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `dc6eeef81b39` | pad: central copy of the third-party Pad skill (pad agent install layout); ~/.agents/skills/pad links here; Claude Code uses the Pad plugin |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `876be0a545ec` | write-backs from unified-network-controller Nautobot 3.2.9 upgrade (2026-11-10) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ccd6f61efae2` | skill-ai-it: open item, budget audit reports LOST for lines an earlier rotation moved (from unified-network-controller 2026-11-10) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `53528f0519a2` | pad: Claude Code uses the ~/.claude/skills/pad symlink to the central copy, not the Pad plugin (operator, 2026-11-10) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7a52988abdbd` | pad: README setting-up-a-project section (template convention conflicts, copies to delete, export in the commit gate, install roots) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2f57ab5ece42` | skill-smc: fleet survey probes, Pi bootloader census, writers probe; probe deadlines TERM then KILL; write-back (v0.14.0) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f14039eb31f8` | skill-coder: write-back from smc-resiliency: P-65 version record pins found by pattern; Go programs survive SIGALRM; stop an flock holder by taking the lock |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `e95b6d099a17` | skill-systems-architect 2.3.5, skill-network-architect 2.3.1, skill-smc: fleet survey write-backs (watchdog audit, write measurement, overlay wear, undervoltage, credentials rotation, APN fleet facts); summarise_survey MB/day and --census with tests |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `5e687439f582` | skill-pad: renamed from pad/ to specialists/project/skill-pad; conventions baseline and Pad scripts |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `470f45aa5160` | skill-pad: Learned 2026-11-10 (Pad CLI field writes, disabled items, agent install) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `da4a32810c96` | skill-smc: write-back 2026-11-10 (koonibba): stale bastion keys break the backdoor, backdoor-watch misses group_vars site IDs, url_capture prune gaps on 3 nbn_accelerate boxes, smc_system root-LV condition bug and the smc_bases always-tag hazard |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `14eabebb3dbc` | skill-smc: references/19 urlcapture-prune change (template action via include, byte-identical render, canary koonibba passed) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `77b375b9b6be` | skill-smc v0.14.1: CHANGELOG for the 2026-11-10 koonibba write-backs; 01_overview, a box missing from plain tsh ls is not offline (cluster from the profile); CHANGELOG rotated |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `82c8b2c2a1f2` | skill-systems-architect v2.3.6: edge retention deletes each period after its own upload; survey provisioning outcomes; transient units for long jobs; SSH changed host key disables reverse forwarding (from smc-resiliency 2026-11-10) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `6b8a55a4989e` | skill-coder: write-back from smc-resiliency (urlcapture-prune): a wrapper template including another, values by set, two lost newlines, prove with cmp |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `44aad34ca31f` | skill-knowledge-curator: UNC pilot learnings (2026-11-05); status_claims, merge_labels, locate_lines scripts with tests; workflow steps 3b and 3c |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d2d14f1ee1d4` | Mark 44 skills disabled: true in front matter; bump stop-slop and superpowers submodules (same change) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `87e8f9643107` | Bump superpowers: re-enable executing-plans, writing-plans, verification-before-completion |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `787e36a35100` | skills_stuff: record the 2026-11-10 commit-all (disable flags kept, three routing skills re-enabled, incident, open items) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `6a168aa03904` | skill-pad: own skill replaces Pad skill text; plugin parts rebuilt; governance scaffold |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8eeee97a18a8` | skill-pad: rewrite the Pad usage proposal after review against both workspaces |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `35c092bc5624` | skill-pad: usage proposal moved to docs/ with diagrams; push delivery limits recorded |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `447f8e6e07bb` | skill-pad: Pad data moved to tools_stuff/pad; container image facts |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `965ef4caa8d6` | skill-pad: writing standard (convention and proposal 3.3), section 3 renumbered, pad_conventions --only |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b9d9817d803f` | skill-pad: Pad usage guidelines in force (operator answered Q1 to Q6); rollout for both workspaces |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d7d908add452` | skill-pad: SETUP notes the guard for the live Pad database tracked in tools_stuff |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `984d8c46abec` | skill-pad: open Pad items rewritten to the writing standard; pad_rewrite.py; Jira-style link mapping in the guidelines |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8182762feb96` | skill-pad: pad_rewrite replaces comment text; smc-resiliency comments rewritten to the comment standard |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `33b5f39fa35f` | skill-pad: keep original comment text before reformatting; pad_rewrite retries rate-limited writes |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a28cf8074613` | skill-pad: closed Pad items on the standard; pad_rewrite flushes progress lines; seq trap recorded |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b2e2e52bc53a` | skill-pad: pad_tracker.py (trackers generated from Pad collections); pad-owned-trackers convention; smc-resiliency moved |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2943f29849ce` | skill-pad: UNC moved; trackers-truth exception for bugs, features and tech debt; guidelines updated |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `78e1acedbbaf` | skill-pad: slurp close (session record, collection schemas); write-backs to skill-coder and skill-ai-it |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b8e78522c1fd` | skill-pad: tracker import spike discounted in the trial review (operator) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `590716b5b309` | skill-smc: ref 19 names the urlcapture-prune read recipe uc-old-files (was months) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c931f50ff002` | skill-pad: link opener so repo links in Pad open in VS Code (localhost redirect to vscode://file, launchd job, pad_tracker links/import/export conversion, tests) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `f6a95de46fd8` | write-backs from smc-resiliency (session c82184a8, 2026-11-10/11) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `22047db22488` | skill-ai-it: docs/history by kind (changelog, scratchpad, roadmap, session-records, sync) with a generated index carrying a summary per file; history_migrate.py |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `21af81ea6c6f` | skill-ai-it: .archcore rules (AGENTS.md one line per rule), ruff.toml + just lint in check, code-map.toml, templates (history-readme, session-record, archcore), Pad workspace question at bootstrap/refresh |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a623b77b6b41` | write-backs from smc-resiliency (second close 2026-11-11): skill-coder P-67 (move files, repoint references by resolving links) and ruff 0.17 formats Markdown (python.md split into languages/python/ by language_split.py); skill-pad: pad workspace link shares a workspace across repos |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `a806ef42a839` | skill-ai-it: 22 docs past review approved by the operator (2026-11-11: "all 22 docs are approved"), Last reviewed set; history-readme template gets front matter, dated on use |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `be5bbe9e5991` | skill-coder: templates/ruff.toml for projects (two-space, 160 columns, the skills' rule set, existing files excluded until reformatted, Markdown excluded); python.md names it |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `3adefce425b5` | write-backs from smc-resiliency (third close 2026-11-11): skill-ai-it history_migrate --check-cmd gate (undo when red after), dirty-reference refusal, multi-project survey, rollout notes; skill-smc 0.14.3 galiwinku check; skill-pad commit-gate links step |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ec58b0886b42` | skill-smc: smc_lynis NO_PUBKEY 7A9A1D9D5B27C6D3 from the cisofy 2025 subkey; url-only apt_key does not fix it, pin the subkey id |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ed645e25cd22` | skill-ai-it, skill-pad, skill-coder, skill-drawio: central project tooling plan and write-backs (unified-network-controller session 2026-11-11) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `57b37ca359f9` | skill-ai-it: doc_freshness skips path-only dependency commits; skill-coder: enforcement open work (2026-11-11) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0fe098db6c97` | skill-smc v0.14.4: apt_key_subkey_probe.sh (read-only; does an SMC trust an apt signing subkey), CHANGELOG for the smc_lynis NO_PUBKEY entry |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2dd767c0e5d4` | skill-coder: Learned (ansible), apt_key with url and no id never refreshes a key whose primary is present; pin the new subkey id |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `5dc0abc673da` | skills: shorten 4 skill descriptions to ~120 chars; full trigger text moved to a When to use section (token optimizer, operator 2026-11-11) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `6cad51546725` | REVISION_HISTORY and SCRATCHPAD 2026-11-11: four descriptions shortened (5dc0abc); front-matter disabled flag found inert in Claude Code and Codex, open item answered |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `fa6bad862438` | Remove front-matter 'disabled: true' from 43 skills and bump superpowers and stop-slop: neither Claude Code nor Codex honours the key; intent moved to per-tool switches (operator, 2026-11-11) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `60ba9ecd7b02` | skill-smc 09: v2 URL capture now on master and rise (1ef84551, 906ee778), default v2, prune fix kept |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c306ef1411aa` | Shorten seven protected skill descriptions; skill-coder write-back |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `dd140b03e7be` | Shorten eight skill descriptions; keep full text in SKILL.md |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2b7ec51d61a0` | Restore trigger words in three short skill descriptions |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `1c1252aae37d` | skill-commtracker: folder layout standard (emails/, teams/, transcripts/, attachments/) and transcript turn layout (operator 2026-11-11); extract.py saves attachments beside the tracker from emails/ or teams/, reconcile.py reads both layouts, compact_turns.py lays out turns; 23 tests pass |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `0570859aca9a` | skill-coder: design-principles principle 4 write-back (one search-scope function for two lookups; fixtures carry every folder layout; apn cc69e7c1). skill-systems-architect v2.3.7: edge-appliances read-only root versus RAM overlay (trial catches missed writers, scheduled writers need their own run) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `ad50f0b98179` | skill-coder: promote two parked enterprise-strategy candidates (design-patterns P-68 baseline beside forecast; python learned-other: accept the decoration hand-typed lines carry) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d53c60e5cb68` | Shorten skill-ifa description; keep full text in SKILL.md |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d00ec9efc41b` | skill-drawio: lane pages search a gap's reversed track order together with the branch swap (improve_tracks; operator review 2026-11-11: two branches of one diamond crossed); an explicit label is never cut; look.e2e_tab defaults to E2E in tabs, headings and index boxes; example re-rendered; consumers: layout metrics unchanged, text differs |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `7c86de8b8f14` | skill-drawio: base layer locked by default so one click follows a box link; E2E button above the step page header; Learned header form fixed (operator review 2026-11-11) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `4266ac8ef5cc` | skill-drawio: SKILL.md standing rules: one-click navigation (base layer locked by default) and the E2E button above the step page header are standards (operator, 2026-11-11) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `8a7a2766910e` | skill-drawio: prototypes/business-views keeps the hand-drawing scripts for the enterprise-strategy business views (roadmap matrix, five views; operator: do not lose the code); step page header split into flowmap/flow_head.py so pages.py is back within its 400-line budget (7c86de8 had pushed it to 406) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `c4fedfae7c97` | skill-commtracker: Cross-reference N entry type for a communication filed in full in another tracker (SKILL.md, toc.py lists it, test_toc). skill-coder: Learned 2026-11-11, run the check as well as the tests before a commit |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `18f9e52c4167` | skill-drawio: prototypes README, all three scripts overwrite their output |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `2ed21d73e3dc` | skill-drawio prototypes: cost driver tree drawn with straight lines between spanning boxes (no shared end points); requirement tree middle row ordered by barycentre with spread end points (operator review 2026-11-11: overlaps) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `fc57576abc88` | skill-drawio prototypes: requirement tree back in Martin's order; lines routed square on tracks with own ports and jump arcs, track choice by a crossing-minimising local search (upper gap 138 -> 94 crossings, no shared segments), gaps sized 14 px a track (operator review 2026-11-11) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `170a9f18ffc3` | skill-drawio prototypes README: routing learnings from the operator's review of the two trees (spanning boxes; tracks and crossing search 138 -> 94; reorder judged worse; untried exit-order idea) |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `08cc6cd9a3ff` | skill-commtracker: Teams multi-turn entries carry no trailing backslashes (operator, 2026-11-12); matches the Transcript turn layout |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `d3132c2dd510` | skill-ai-it: new-skill mode (intake, research briefs, seed, scaffold, pack check) and the skill-presentation seed |
| 2026-11-12T05:35:40.342975+00:00 | main | origin | `b89bbcbaa8db` | skill-coder: write-back from enterprise-strategy (skill-ai-it new-skill): P-69 seed, plan-first scaffold and guard on the shared output; python learned entries (load a sibling module by path; parse wrapped markdown table rows) |
