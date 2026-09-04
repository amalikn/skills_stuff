# Changelog — Agent Stack

## 20260904_1630 — Provenance detail section added to the phased implementation plan, at operator request

### Added

- docs/reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md: a new "Provenance detail — feature, pick, effect, benefit" section, one prose block per repo across all
  17 rows of the existing "Tool and feature provenance" table. Operator found the single-line table (necessarily terse, per its own 200-character wrap-safety convention) did not answer what each
  source repo is actually known for, what narrow feature is being taken from it, whether the result enhances an existing Agent Stack surface or adds a new one, and what the end benefit is. A literal
  four-column table extension was considered and rejected: cramming four substantive answers into table cells would either be too terse to answer the question or long enough to trip the same
  wrap-corruption bug the existing table already guards against (see the 20260904_1208 entry below). Used prose blocks instead, organised under the same five phase headings as the rest of the
  document. No new information beyond what the reliability adaptation proposal's own comparison table and adaptation map already state — this restates their content per-repo, next to the phase it
  belongs to.
- Contents block and anchor updated to match (the project's own PostToolUse hook auto-syncs Contents to real headings, confirmed by watching a manually-added Contents entry get silently stripped until
  the matching heading existed).

Verified: `just governance` (1111 checks) and `just preflight` (51 tests) both green after the addition.

## 20260904_1230 — Scoped staleness re-audit: two path defects fixed, prior 20260903_2200 register re-verified

### Fixed

- skills/tailwind-v4-shadcn/SKILL.md: 5 occurrences of the singular "reference/" corrected to the real "references/" directory (common-gotchas.md, dark-mode.md), matching the 9 already-correct
  occurrences in the same file.
- docs/routing-evaluation/routing-failure-classification-20260901_1842.md:10 no longer links to agent-stack-capability-taxonomy-and-scoring.md, an untracked Baseline-v2-era draft one level above this
  repository that was never migrated in. Rewrote as prose naming what it is and pointing at Rule 0007 and routing.toml as what actually stands now. This resolves the residual the 20260904_0737
  docs-reorg entry explicitly left alone ("a known residual from an earlier phase, not something this reorganisation should paper over") — that entry's relative-path correction stands; this pass gives
  the underlying dead reference its actual resolution rather than leaving it dead indefinitely.

### Changed

- SCRATCHPAD.md: added a dated addendum under the existing 20260903_2200 residual-risk register (not a rewrite — history stays as written) recording this scoped re-audit's findings: the prior
  register's six items re-verified unchanged, the two fixes above, and today's own new reliability-adaptation documents' forward-looking file mentions classified EXEMPT (prospective, not yet built)
  rather than defects.

Run via skill-staleness-audit's own scripts (snapshot, coverage manifest, claim scan) as part of an operator-queued sequence. Explicitly scoped: full materiality-ranked treatment was given to this
project's own core surfaces; the pre-existing ~89 `skills/` path findings and ~163 manual-verification claims were sampled to confirm the existing register's characterisation still holds, not
re-triaged individually. The audit skill's completeness gate was not run to a PASS claim on that basis — this is a stated partial pass, snapshot and receipts kept intentionally, not a clean exit.
Verified: `just governance` (1111 checks) and `just preflight` (51 tests) both green after the fixes.

## 20260904_1208 — Phased implementation and self-verification plan added, inert pending an operator-named trigger

### Added

- docs/reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md: for each of the five phases in the reliability adaptation proposal, fixes the exact implementation
  steps, the self-verification checklist to run afterward, and the revert behaviour on a failed check. Written at operator request after raising a felt gap (orchestrator routing quality, personas not
  coordinating hand-offs) that the project's own evidence store (6 field-log entries, 0 capability gaps) does not yet substantiate. The document changes no code and authorises no phase on its own —
  each phase still requires the operator to name its evidence trigger and approve that phase individually, per the proposal's existing decision.
- A "Tool and feature provenance" table added to the same document at operator request: all 17 mechanisms named across the five phases, each row naming the exact source repo, file/symbol, and what it
  becomes in Agent Stack. Authored as single-line, unpadded rows kept under 200 characters per row, following the survey document's own established convention, after the project's automatic prose-wrap
  hook mis-wrapped a first draft of the table across physical rows (cosmetic column padding is fine; a wrapped, multi-line-per-row table is not — verified the fix by re-reading the file and checking
  no row spans more than one physical line).
- Catalogued in docs/README.md's Reliability adaptation table.

## 20260904_1155 — Sentry Skills / Prompt Optimizer row upgraded from recommendation to adopted record

### Changed

- docs/routing-evaluation/token-optimization-tools-and-strategy.md's Sentry Skills / Prompt Optimizer row changed from ADAPT the method, not the tool (an open recommendation) to ADOPTED, as method —
  ADAPTED (a record), pointing at accepted rule 0013. Same treatment the Token Optimizer row already got when that recommendation was acted on.

## 20260904_1150 — Six proposed archcore documents accepted by the operator

### Changed

- Operator accepted all documents that were still carrying Status: proposed: rules 0012 (gate flags advisory) and 0013 (trim against the frozen corpus), specs 0006 (runner qualification), 0007
  (gate-only evaluation), 0008 (replay corpus contract), and plan 0003 (Holdout 2 protocol). Each file's header now reads Status: accepted with an Accepted: 20260904_1150 by operator line alongside
  its original Proposed line, matching the convention already used by rule 0011 and the earlier 29-document batch. The 20260902_0300 "29 documents" acceptance count in .archcore/README.md is left
  untouched as a dated historical fact (count:asat), not restated to a new total.
- .archcore/README.md's Rules, Contracts and Plans tables had their *(proposed)* tags removed for all six; the Holdout 2 protocol plan row now reads "Approved" to match plan 0001's existing style.

## 20260904_1145 — Rule 0013 proposed: adapt Sentry's prompt-optimizer removal method to the frozen corpus; Mem0 row corrected

### Added

- **Rule 0013 (proposed)** at .archcore/rules/0013-trim-against-the-frozen-corpus-as-a-gate.md: any SKILL.md/persona/routing.toml edit made to cut token cost gets bracketed by evaluate_routing.py
  against the frozen 60-case corpus (spec 0005), comparing hard invariants only, before and after. This is getsentry/skills' prompt-optimizer meta-optimization loop adapted per the token-optimization
  doc's own verdict on that row (ADAPT the method, not the tool) — no new tool, evaluate_routing.py already does the check; the rule says when to run it. Registered in .archcore/README.md's Rules
  table.
- The rule's reflective-memory round log is specified as append-only (never edited or pruned in place), matching this project's own count:asat convention in AGENTS.md. That refinement came from
  verifying Mem0's current algorithm rather than trusting the prior summary: Mem0's April 2026 release dropped write-time ADD/UPDATE/DELETE conflict resolution for single-pass ADD-only extraction with
  conflicts resolved at retrieval time (multi-signal ranking plus temporal reasoning), not the write-time "retrieve-don't-dump" behaviour the doc previously attributed to it.

### Fixed

- docs/routing-evaluation/token-optimization-tools-and-strategy.md's Mem0 row corrected — the description no longer claims Mem0 sells write-time retrieve-don't-dump; it cites the verified April 2026
  algorithm change instead. Verdict (SKIP as a tool) is unchanged; only the described mechanism was stale.

## 20260904_0833 — Token Optimizer installed for Claude Code and Codex; a real content-loss bug found and fixed

### Added

- **Token Optimizer actually installed on this machine**, at the operator's request, for both Claude Code and Codex. Neither install ran the project's raw install.sh (1,639 lines, read in full first —
  confirmed it has no `--codex` path at all); both went through each CLI's own native, trusted plugin manager instead.
  - Claude Code: `claude plugin marketplace add alexgreensh/token-optimizer` + `claude plugin install token-optimizer@alexgreensh-token-optimizer` (scope `user`, applies to every session). `claude
    plugin details` confirmed all 10 declared hooks are registered immediately — no separate setup step was needed, contrary to the README's "run `/token-optimizer` once" instruction.
  - Codex: `codex plugin marketplace add alexgreensh/token-optimizer` + `codex plugin add token-optimizer@alexgreensh-token-optimizer`, then one hook-wiring step run from the installed plugin's own
    cache path: `TOKEN_OPTIMIZER_RUNTIME=codex python3 ./skills/token-optimizer/scripts/measure.py codex-install --global --profile balanced`, which writes directly to `~/.codex/hooks.json`. Before
    running it, read codex_install.py (577 lines) in full and checked for network calls or credential access — none found. Verified afterward with the tool's own `codex-doctor`: 14 OK, 2 WARN (both
    benign), 0 FAIL.
- **The doc's Token Optimizer row rewritten from a recommendation to an installation record** — exact commands, hook list, doctor output, and the measured always-on cost (~406 tokens per session, up
  to ~7.1k when its audit skill fires), plus a note that a Hermes integration exists (beta) for this operator's own eval-runner harness but was not installed.

### Fixed — a real content-loss bug in the rewrite, found by the operator reading the rendered file

- **A Python block-replacement script located its start anchor with `next(i for i, l in enumerate(lines) if l.startswith("| Token Optimizer"))`.** The same prefix existed in an earlier, separate
  2-column reference table in the same document. `next()` matched that earlier occurrence instead of the intended one, and the script's end-marker search then walked forward past that table's
  remaining 8 rows, past the `## 22. Source Verification and Adaptation Feasibility` heading and its intro paragraph, and past the real target row — replacing all of it with just the rebuilt row.
- **Every automated check passed anyway.** Line count grew (looked like a normal edit), pipe-count-per-row matched on every surviving row, and `just preflight` was clean — none of those checks can
  detect "an entire section vanished," because they verify row structure, not section presence. The defect was caught only because the operator read the rendered file and reported missing column
  headers.
- **Restored** the deleted section-21 rows (Sentry Skills/Prompt Optimizer, LLMLingua, context-mem, Mem0, Letta, Zep, Skill Optimizer, Prompt Cache) and the section-22 heading, intro paragraph, and
  table header/separator, from content already read earlier in the session. Verified by grepping for both section headings and both table headers by name, not just re-checking pipe counts — the gap in
  what the earlier checks could catch is the actual lesson.
- **Recorded as a new, distinct entry in the personal auto-memory `feedback_table_authoring_reflow_script`**, alongside the tool-corruption bug and the unescaped-pipe bug: a non-unique anchor string
  in a block-replacement script is the most dangerous of the three failure modes found this session, because it deletes content rather than merely misformatting it, and nothing in this project's own
  governance checks is positioned to catch it.
- `just preflight` clean after the restoration: 51 tests, 1,100 governance checks, exit 0.

## 20260904_0751 — token-optimization guide added and source-verified

### Added

- **[Token-efficient AI agent architecture](docs/routing-evaluation/token-optimization-tools-and-strategy.md)**, filed under `docs/routing-evaluation/` at operator request. A four-class information
  taxonomy (contractual / operational / procedural / ephemeral) with a treatment rule per class, an 8-phase implementation sequence that puts lossy compression last, and a validation-metrics table
  (requirement recall, constraint adherence, false-retrieval rate) rather than raw token-count reduction alone.
- **Given frontmatter and a Contents TOC** matching this project's own documentation convention — the document as received had neither, despite being 906 lines.
- **A new `## 22. Source Verification` section, added in this pass**: every one of the 9 tools/frameworks cited in the final reference table was checked directly against GitHub (description, license,
  star count, last-push date), not repeated from the brief that produced the document. All 9 confirmed real and active.
- **One correction found and recorded**: Zep's cited repository (getzep/zep) is GitHub's own description "Examples, Integrations, & More" — it is the examples/integrations repo, not the core memory
  engine. Zep's actual product is a hosted service (`help.getzep.com`) with client SDKs (`zep-python`, `zep-js`, `zep-go`) in sibling repositories, not a self-hostable open-core engine in the cited
  repo. Treat it as a hosted option, not a drop-in open-source alternative to Mem0/Letta.
- **One earlier-draft reference confirmed fabricated and left out**: "BM629 token-optimization skill" returns zero results on a GitHub search and does not correspond to any findable project — the same
  defect class as two names in the earlier vertical-agent survey, except this one has no real project hiding behind it at all.
- **LightRAG, named in the fact-check request but not in the document's own reference list, confirmed to exist** (HKUDS/LightRAG, EMNLP2025, 39,365 stars) and recorded as a legitimate scope decision
  to exclude, not an oversight — this document's scope is memory/retrieval and compression tooling, not RAG-indexing frameworks.
- **The `docs/README.md` index entry** under Routing evaluation.
- `just preflight` passed clean: 51 tests, 1,097 governance checks, exit 0.

### Changed — feasibility verdicts merged into the verification table

- **`## 22. Source Verification` retitled `## 22. Source Verification and Adaptation Feasibility`** and given a sixth column judging each option against Agent Stack's own architecture, rather than
  adding a separate third table that would have repeated the same 9 rows. The judgement is explicit: a static, symlink-installed prompt layer with no runtime of its own, and a safety model that
  excludes autonomous loops and implicit persistent state.
- **Only two options verdicted adoptable as-is**: Token Optimizer as an external audit tool (no integration needed, run it against installed skill/persona files) and Skill Optimizer as a cautious
  pilot (directly targets `SKILL.md`, but the tool itself is 0-star and unproven — gate any output through Agent Stack's own eval corpus, not the tool's own benchmark).
- **Most of the memory frameworks verdicted SKIP or DEFER, not because they are poor projects, but because they conflict with Agent Stack's own constraints**: Mem0 and Letta are mature and
  substantial, but an always-on memory injector conflicts with the no-implicit-persistent-state rule, and Letta's "learn and self-improve over time" framing is autonomous-loop by its own description.
  Zep's correction (examples repo, not the core engine) compounds into a second reason to skip it: adopting the actual product means depending on an external hosted service, which needs explicit
  operator authority under this project's own safety model.
- **LLMLingua and Prompt Cache verdicted not applicable to Agent Stack specifically**, independent of their own quality: both assume a live prompt-assembly or inference pipeline that Agent Stack, as a
  static file library, does not run — whatever assembles the final prompt is Claude Code or Codex, outside this project's control. The stable-prefix-first idea behind prompt caching is a convention
  Agent Stack's persona/skill layout already follows structurally, not a tool to adopt.

### Corrected — Token Optimizer's license and mechanism were both wrong

- **License corrected from unrecorded to PolyForm Noncommercial 1.0.0**, found by opening the actual `LICENSE` file rather than stopping at description/stars/pushed-date. The license itself states
  "any noncommercial purpose is a permitted purpose"; auditing one's own coding-assistant sessions plausibly qualifies even where some of that work is commercial, since the restriction targets
  commercializing the software itself rather than gating the work done while running it as a personal dev tool — recorded as a flagged caveat, not a certified legal reading.
- **Mechanism corrected from "run periodically" to "harness-level plugin with native hooks."** It ships as a Claude Code plugin (`/plugin marketplace add` + `/plugin install`, then `/token-optimizer`
  once to wire up `SessionStart`/`UserPromptSubmit`/`PostToolUse`/`Stop` hooks) and, separately, a Codex plugin whose install writes hooks directly to `~/.codex/hooks.json` — which Codex's own docs
  state it "loads for all projects regardless of trust level." This is what actually answers "how do I make sure it always runs no matter the model": the hooks fire on harness/session events, not on
  anything the model does, so which LLM answers inside the session is irrelevant to whether the audit runs.
- **Confirmed it sits entirely outside Agent Stack's own routing.toml/personas/skills tree** — a host-level, install-once plugin, not something for Agent Stack to route to or embed.
- `just preflight` clean after the correction: 51 tests, 1,100 governance checks, exit 0.

## 20260904_0737 — docs/ reorganized into subfolders

### Changed

- **`docs/` split into four subfolders** — `audits/`, `routing-evaluation/`, `reliability-adaptation/`, `off-topic/` — once the flat list passed a dozen files and grouping by content became more
  useful than one long table, mirroring the pattern `.archcore/` already uses for its own subfolders (`adr/`, `rules/`, `specs/`, `guides/`, `plans/`).
- **`docs/README.md` rewritten** with one heading and one table per subfolder rather than a single flat table; the off-topic vertical-agent survey keeps its own section so it never blends in with
  genuine Agent Stack evidence.
- **`scripts/check_governance.py`'s `docs/README.md` catalog glob changed from `*.md` to `**/*.md`.** A non-recursive glob would have reported full coverage while checking nothing inside the new
  subfolders — the same reasoning already documented against `.archcore/README.md`'s own catalog entry, applied here for the first time since docs/ never had subfolders before.
- **Every cross-reference to a moved document updated** — 46 occurrences across `CHANGELOG.md`, `SCRATCHPAD.md`, `ARCHITECTURE.md`, `AI_NAVIGATION.md`, `MEMORY.md`, and six files under `.archcore/`.
  Parent-relative links (`../`) inside the five moved documents whose own prose links back to root-level files (`routing.toml`, `SCRATCHPAD.md`, `.archcore/` entries) were bumped one level deeper to
  `../../` and each resolution verified against the filesystem, not assumed from the edit alone.
- **One pre-existing broken link fixed in passing**: `docs/routing-evaluation/routing-failure-classification-20260901_1842.md` linked `[MEMORY.md](MEMORY.md)` with no path prefix at all — already
  broken before this move, since a bare filename inside `docs/` never resolved to the root `MEMORY.md`. Corrected to the depth-correct relative path.
- **One pre-existing broken link left alone, deliberately**: the same file's reference to agent-stack-capability-taxonomy-and-scoring.md points at a file that does not exist anywhere in the
  repository, not merely at the wrong depth. Its relative-path math was kept consistent with the move (still resolves to the project root, still missing) rather than invented a target or silently
  dropped — this is a known residual from an earlier phase, not something this reorganisation should paper over.
- `just preflight` passed clean throughout: 51 tests, 1,094 governance checks, exit 0.

## 20260903_2230 — staleness audit

Not a change-propagation pass. This one started from nothing and asked what had quietly stopped being true while 747 governance checks passed continuously.

### Fixed — the skill library was promising capabilities it does not have

- **`skills/devops/SKILL.md` named the two scripts as scripts/cloudflare-deploy.py and scripts/docker-optimize.py.** The files exist under those names with UNDERSCORES rather than hyphens — so both
  references were dead while the capability was real. The scripts' own `--help` epilogs repeated the wrong name 12 times, meaning anyone copying the printed example got "No such file or directory"
  from a script that was working fine.
- **`product-strategist` listed four reference files and four runnable scripts; the package contains only a SKILL.md.** `startup-financial-modeling` listed three references it does not have.
  `market-sizing-analysis` listed three of which one exists — and that survivor is what proves these are rotted indexes rather than illustrative lists. `scientific-critical-thinking` documented a
  schematic generator that was never imported.
- **`check_skill_package_references`** now reads every `SKILL.md`'s own references, in prose AND in fenced commands. Four of the sixteen findings were written as `python scripts/market_sizing.py ...`
  inside a ```bash block, which every prose-oriented scanner skips by construction. Package-relative or repo-relative both count; only a path resolving nowhere is a promise the agent cannot collect
  on.

### Fixed — an index that presented retired documents as live

- **`.archcore/README.md` listed four superseded sync documents with no indication of their state.** The banners were inside the files; the index that routes readers to them said nothing, and
  `.archcore/` is declared this project's highest authority. This is the Phase 3 defect inverted — the usual failure is a supersession recorded in a routing table that never reaches the file.
  **`check_superseded_marked_in_index`** derives the state from each document's own `Status:` line, because a hand-kept list of what is superseded drifts exactly as the thing it polices does.

### Fixed — a routing map that discarded a block without any error

- **`context-map.yaml` defined `type` and `authority` twice in the entry describing itself**: `machine_routing_map` followed immediately by `sync_translation_rules`, two lines orphaned when upstream
  sync was retired. YAML keeps the last value, so every consumer saw the file described as a sync artifact that no longer exists while the correct description was silently thrown away.
  **`check_no_duplicate_yaml_keys`** asserts on the key stream rather than on whether the load succeeds, because well-formedness proves nothing here. Stdlib-only, so the gate can never fail for an
  environment reason.

### Added — personas had no way in

- **[`personas/README.md`](personas/README.md)**, derived from each persona's own frontmatter and registered in `CATALOGS`, so a persona added without an index row fails coverage. Found by the inverse
  sweep — the pass that asks what exists that no catalog names, rather than what a catalog names that has vanished. Only the first grows while nobody is looking. It needed the same "a README is not a
  capability" exemption in **four** places (coverage catalog, manifest check, persona document contract, global installer); a fifth would mean the glob belongs in one shared helper.

### Also

- `docs/README.md` named `translation-policy.md` as a current root entrypoint six hours after it was deleted. `.archcore/README.md` described the deleted sync state files in the present tense.
  `AI_NAVIGATION.md` listed a generated artifact that has never been generated here, now marked optional.
- Governance 747 → 1,073 checks; three new families, all negative-tested by breaking the project deliberately and watching them go red.
- Gate PASSED: coverage 278 examined + 12 exempt = 290, claim matrix reconciles at 931, inverse sweep clean, `just preflight` exit 0.
- **Three fixes went upstream into the shared audit skill**, where they had survived as permanently unaccepted residuals across three audits: package-internal directories no longer report as orphans
  when an ancestor is catalogued; point-in-time backup trees are exempt from the old-value sweep, because a backup records what a file SAID on a date; and JSONC configs parse via a string-aware
  comment stripper. The first regex for that stripper ate `"@/*": ["./src/*"]` — a tsconfig path alias — and produced a parse error pointing at an innocent line, which is this skill's own warning
  about programmatic edits to structured files arriving by the short route.

### An error I made and corrected

I deleted the devops Scripts section outright after reading `find ... | head` — truncated at ten lines — as proof the scripts were absent. The package has 29 files. Caught in Phase 4, when the
per-artifact worksheet listed `skills/devops/scripts/cloudflare_deploy.py` by name; the grep-shaped question had returned a technically correct "no" to the wrong question. Restored as a two-character
fix per line. Recorded here because why a defect survived, and how a fix went wrong, is the reusable part.

## 20260903_2130

### Added — a declared gap is about this library, so this library keeps it

- **[`evals/capability-gaps.jsonl`](evals/capability-gaps.jsonl), tracked here in git.** Persona notes are written into the *consuming* project, and yesterday's gap mechanism recorded declared gaps
  only in that project's run manifest, with Agent Stack holding nothing but a `run_dir` pointer in the field log. That is not a record. The project can move, be deleted, or turn out to be a company
  repo Agent Stack must not read — and the library's own growth signal goes with it. This repo already carries the proof that pointers rot: 39 of 40 indexed runs stamp a corpus hash that no longer
  resolves, found the same day.
- **The split is deliberate.** The raw notes stay with the project because they contain that project's analysis and belong to it. A declared gap is a statement about **this library** — "no skill takes
  a duty rate as an input" — so a copy comes home. `scripts/persona_note.py` writes both at declaration time.
- **`--project` on `persona_note.py write`**, so a gap in the library's own log is attributable without having to resolve a path that may no longer exist.
- **[`scripts/propose_evolution.py`](scripts/propose_evolution.py) reads the local log first**, then still reads reachable manifests, because a run captured before this log existed is evidence too.
  Duplicates collapse on the declaration itself — `(kind, persona, text, at)` — rather than on where it was found, so the two paths merge while two genuine repeats of the same complaint stay separate
  and still reach the threshold.

### Added — the JSONL evidence contract

- **`check_jsonl_evidence_contract`** in [`scripts/check_governance.py`](scripts/check_governance.py), registering `evals/field-log.jsonl` and `evals/capability-gaps.jsonl`. These files cross a
  process boundary: one script appends, another aggregates days later. A malformed line and an under-populated line are both silent — the writer has exited and the reader skips what it cannot parse,
  so evidence goes missing with no error anywhere.
- **The colon rule is the load-bearing one.** The proposer groups `inadequate` gaps on the skill id before the colon, which is what makes that aggregation exact rather than a guess at what two
  sentences share. A declaration written without one groups under its whole sentence, can never match another, and a genuinely repeated complaint about a skill silently never reaches the threshold
  that would surface it. Negative-tested on all four failure modes: unparseable, unknown `kind`, missing key, and a colonless `inadequate`.
- Governance 707 → 715 checks.

### Changed

- **The persona tests now drive the real argument parser instead of hand-built `Namespace` objects.** The gap arguments added yesterday broke a note-writing test that constructed the old shape by
  hand, and the failure had nothing to do with the behaviour under test. Parsing argv means the tests exercise the defaults the CLI actually supplies.
- Step 7.5 of `SKILL.md` now carries the two gap flags with the rule that a gap is declared only when a persona actually hit the limit while working — a guess pollutes the evidence the thresholds
  depend on. 5,722 → 5,836 tokens.
- Suite 49 → 51 tests. The survival test was negative-tested by disabling the local-log read and watching it go red under the old pointer-only design.

## 20260903_2126 — vertical-agent framework fact-check

### Added

- **[Vertical agent framework and reference-project fact-check](docs/off-topic/vertical-agent-framework-survey-20260903_2126.md).** Off-topic for Agent Stack's own routing or safety model, filed here
  at operator request as a working-evidence artifact: a source-verified fact-check of a separate, unverified AI-generated proposal for building new Python-based vertical domain-specialist agents
  (Network, Infrastructure, Finance, Research), covering candidate frameworks (PydanticAI, LangGraph, CrewAI, AG2, smolagents) and reference projects (NetClaw, NetCopilot/ARIA, Netmiko MCP, FinRobot,
  TradingAgents, finance-mcp).
- **Corrected several claims the brief stated without verification**: AG2's "transition toward v1" is stale (v1 is the current default; the AutoGen-derived code moved to a separately maintained
  `ag2-classic` package); LangGraph's Ollama and MCP support live in separate LangChain-ecosystem packages, not the core repo; CrewAI's dedicated tools repo is archived; NetCopilot/ARIA is Business
  Source License 1.1, not free/open-source, and its agent is gated behind a hosted license key; the closest "Netmiko MCP" candidates carry no declared license and expose config-push, not read-only,
  operations.
- **The `docs/` index entry**, distinguished explicitly from every other row as off-topic-but-filed-here rather than blended in silently.

### Corrected — the survey's own first pass was wrong about two of its subjects

- **This document originally reported "Vertical AI Agent" and "OpenResearch Agent" as `UNVERIFIED / NOT FOUND`** after a genuine multi-strategy GitHub search by name and architectural description.
  Both were wrong. The operator supplied direct URLs — [chetanreddyv/vertical_aiAgent](https://github.com/chetanreddyv/vertical_aiAgent) and
  [hetu-project/openresearch-agent](https://github.com/hetu-project/openresearch-agent) — and both are real, public repositories matching the original brief's descriptions closely. The correction is
  recorded in place in the document rather than silently fixed.
- **The Together.ai dependency claim, previously reported as tracing only to an unrelated project, is CONFIRMED.** hetu-project/openresearch-agent's own README names Together.ai as its LLM integration
  and requires a `TOGETHER_API_KEY`; its three-part MCP/LLM-service/storage architecture is also confirmed against the README's own diagram. License: GPL-3.0.
- **chetanreddyv/vertical_aiAgent is the closest real match to a manager→specialist→MCP proof of concept** — a Gemini Manager decomposing requests for typed MCP-backed specialists (Email, SQL, Drive,
  Calendar, Jira, meeting-transcript search), with a human-in-the-loop gate on mutating steps. Its README carries an MIT badge that GitHub's own license API does not back with a LICENSE file — the
  same class of licensing gap already flagged against the Netmiko MCP candidates.
- **Root cause, stated for the next time this check is run**: the search agents searched by name variant and architectural description, not by exact repository slug, and both real slugs
  (`vertical_aiAgent` with an internal capital, `openresearch-agent` under an org whose name doesn't match either term) were plausible but not guessable from prose alone. A `NOT FOUND` verdict from
  this method means "not found by this method," not "does not exist" — the rest of the survey's findings are unaffected because they were verified against repositories the search agents did find,
  which is a stronger form of verification than name-guessing.

## 20260903_2000

### Added — a broken multi-persona run keeps what it already bought

- **[`scripts/persona_note.py`](scripts/persona_note.py) and Step 7.5.** A multi-persona route costs minutes and real money per analysis, and if the session dies, the context compacts, or a runner
  hits a limit — all observed today, when a session limit killed a 60-call run at call 5 — everything that already finished dies with everything that never ran. Each analysis is now written as it
  returns, with a a MANIFEST.json recording dispatched against returned.
- **The dispatch is recorded BEFORE the work**, which is the whole mechanism: without it a run that died mid-flight is indistinguishable from one that only ever wanted the personas that came back.
- **Every note carries a banner saying it is not the verdict.** A stale persona view read as the answer is the obvious trap in keeping raw analyses, and it is cheaper to label every note than to rely
  on the reader remembering.
- **Evidence retention, never resume.** Nothing re-dispatches on its own — auto-continuation is unattended work, which [rule 0001](.archcore/rules/0001-safety-model.md) excludes and which is why this
  project exists as a fork.
- Separately from crash safety, the raw notes are better evidence than the synthesis: today a CFO's postage-band arithmetic and a Critic's six-condition inversion were the most useful output of a run,
  and only a paraphrase of them survived into the report.

### Added — the measurement that decides whether resume is ever worth building

- **`--returned` on the field log**, against the existing `--dispatched`. Two counts rather than a boolean, because "2 of 4 came back" and "the run broke" are different facts and only the first says
  how much was salvaged. The report prints run completeness and, when nothing has broken, says so: *"no incomplete runs recorded — the resume mechanism has not yet been shown to be needed"*.
- **The resume mechanism was deliberately NOT built.** It is the expensive half — stale inputs, changed tasks, superseded views — and there is no measurement of how often a multi-persona run actually
  breaks. Gathering that first is the same discipline the rest of this project runs on.

### Changed

- **SKILL.md re-compressed after the two new steps ate the trim**: 6,013 → 5,722 tokens, against 6,479 before any of today's work. Reasoning for both new steps moved into
  `skills/skill-agent-stack/references/field-log.md`; the commands and operative rules stay inline.
- Three regression tests, negative-tested by forcing `complete` to true and watching two go red. Suite 46 → 49; governance 706 checks.

## 20260903_1943 — reliability adaptation proposal

### Added

- **[Agent Stack reliability adaptation proposal](docs/reliability-adaptation/agent-stack-reliability-adaptation-proposal-20260903_1943.md).** A decision-ready, non-executing proposal that compares
  all 25 externally assessed repositories, identifies the separable mechanisms worth adapting, and sequences a post-dispatch verification layer before any learning or promotion feature. It explicitly
  excludes daemons, autonomous loops, automatic retries, agent-controlled access approvals, and automatic guidance changes.
- **The `docs/` index entry** for the proposal, alongside the existing external-survey entry.
- **Corrected after project-level review.** The five mechanisms are now an evidence-triggered deferred backlog, not a delivery sequence. The proposal names the existing field log, persona run
  manifest, evolution proposer, and evaluation receipts that a future change must reuse rather than duplicate.
- **Source-level adaptation map.** Every surveyed repository now names the exact inspected source path and function, class, or section to study—or an explicit no-component finding.
- **Receipt storage clarified.** If portability evidence eventually requires a normal-work receipt, it is one JSON object per line in the existing `evals/field-log.jsonl` stream; the per-run manifest
  remains a complete snapshot rather than an event log.

## 20260903_1849 — external orchestrator and skill-library survey

### Added

- **[External orchestrator and skill-library survey](docs/reliability-adaptation/external-orchestrator-survey-20260903_1849.md).** Five parallel research agents opened and read 25 external
  repositories — Claude Code orchestrators, multi-agent SDKs, and plain skill libraries — against Agent Stack's existing routing catalogue, gate closure, and safety model, with instructions to quote
  source verbatim rather than answer from memory. evanca/skills returned a confirmed 404 and is recorded as unreachable rather than assessed from a guess.
- **The convergent finding.** Three unrelated repos independently supply one-third each of the same missing subsystem, none requiring a daemon or autonomy: MetaGPT's `_watch()` set (declare which
  upstream artifact types a role legally consumes), Squad's atomic compare-and-swap task claim with a time-boxed lease (claim a decision so two agents cannot both rule on it), and
  anytools-agent-skills' `required_model`/`actual_model` audit (verify after dispatch that a persona's output stayed inside what it was routed to do). This is the piece Agent Stack's field log
  currently lacks — it records the route and the outcome, never whether the outcome honoured the route.
- **Confirmed, not assumed, that the project's own eval harness is ahead of every eval mechanism found across all 25 repos** — every other evaluation encountered was an end-to-end task-success
  benchmark or a single manually-invoked sample document, none an asymmetric-scored frozen corpus.
- This document is evidence and a proposal only; it makes no durable decision. It became the assessment basis for the reliability adaptation proposal above.

## 20260903_1900

### Fixed — the field log asked for five of the eleven fields it accepts

- **`--tokens` and `--dispatched` were added and never requested.** The tool accepted eleven flags; Step 10's template asked for five, so `--persona`, `--skill`, `--tokens`, `--dispatched` and
  `--gates-useful` were never populated. That is why the 05:32Z entry carries no token estimate — **the skill never asked for it.** Same defect class as closure being described and never run: the
  capability existed and nothing invoked it.
- The template now passes every field, and says which are facts (all of them but one) versus the single estimate.

### Added — three fields, each answering a question the existing ones cannot

- **`route_mode`** — the dominant cost lever, in one word.
- **`gates`** — each gate the route set true. **This is the only way to see over-assertion in real use.** The eval corpus can measure it because it has expected values to compare against; the field
  has none, so recording what fired is the closest available signal. The report prints the all-four rate beside holdout 24's 19/19 and labels it suggestive, not proof.
- **`closure_changed`** — what `scripts/close_route.py --explain` printed. Free, and the direct measure of whether the repair wired in this morning does anything outside the harness.

### Notes — what was deliberately left out, and why

Recorded in the skill's `skills/skill-agent-stack/references/field-log.md`: **duration** (an agent cannot measure its own wall-clock reliably, and `dispatched` already proxies cost with a fact),
**domain tags** (derivable, and asking invites fitting the tag to the route chosen — the error rule 0006 names), **rework** (a strong signal, but only knowable later, so it belongs to a follow-up
entry), and **anything git already knows**.

**Every added field is friction, and friction kills capture.** The log had four entries when these were chosen; the stated bar for a fifth is that it answers a question the existing ones cannot.

## 20260903_1830

### Added — two precedence rules, from holdout evidence

- **`incident-explanation-vs-correction`** and **`policy-as-artefact`**, closing the two ownership boundaries the spent holdout exposed. In both, `hnet-radius-postmortem` and
  `hnet-firewall-consolidation`, the model **cited the existing rule and reached the other answer with a stated rationale** — the signature of an underdetermined rule rather than a bad route.
  Evidenced by **unseen** data, which is what makes fixing them legitimate under [spec 0008](.archcore/specs/0008-replay-corpus-contract.md) rather than corpus-fitting. Precedence rules 4 → 6.

### Added — the synthesis is written into the project

- **Step 9.5.** The most valuable thing the stack produces was evaporating unless the consuming project happened to have a convention of its own. Established by checking: `skill-agent-stack` had no
  report-persistence instruction at all, and the atar assessment of 20260903_1619 exists because the ATAR project defines a docs/reports directory, not because this skill asked for it.
- **The project decides where, not the skill**: follow an existing reports convention exactly; otherwise `docs/` and say so; never invent a parallel structure beside one that exists. Named
  `<slug>-YYYYMMDD_hhmm.md` per the operator's global convention.
- **Only when it will be referred back to** — a GO/NO-GO, preserved disagreement, evidence someone will re-check, or reasoning a later session would otherwise redo. Not for narrow work; a document per
  task is noise.
- **The report records its own route.** That connects a decision to the reasoning path that produced it, and is the only artefact that does.

### Notes — what "fix it all" could and could not honestly mean

Full classification of all 27 production-shape failures:
[docs/routing-evaluation/routing-failure-classification-20260903_1800.md](docs/routing-evaluation/routing-failure-classification-20260903_1800.md).

- **20 of 27 were already fixed** by wiring closure in earlier the same day — `gate_unsatisfied` 18 plus `strength_insufficient` 2 are exactly what it repairs.
- **10 corpus cases contradict [rule 0006](.archcore/rules/0006-required-personas-is-ownership.md)**, found by testing the whole corpus rather than the failures — and **3 of the 10 currently pass**,
  which is the evidence it was found by rule and not by score. The cause is structural: the corpus has no `tags` field, so tag-driven escalation is encoded in `required_personas` instead. **Not
  changed** — it edits a frozen corpus and rule 0006 forbids deriving tags from `required_personas`, which is the tempting shortcut. This is the decision left open on 2026-09-02.
- **Skill under-selection is a router limitation, not a discoverability defect** — verified: `financial-unit-economics` already declares the `unit-economics` and `landed-cost` intents, `devops`
  declares `cicd`. Tuning the catalogue or corpus until these pass is corpus-fitting, which [spec 0005](.archcore/specs/0005-eval-corpus-contract.md) exists to forbid. **Not done.**
- Freeze re-recorded at 20260903_1830.

## 20260903_1600

### Changed — upstream sync retired; Agent Stack is its own project

- **Operator decision: there is no upstream and no sync.** The project has evolved well past what it was extracted from — a routing catalogue, gates, deterministic closure, an evaluation harness and a
  governance layer the original never had. Removed: `scripts/sync_auto_company.py`, its 11 tests, `upstream-state.json`, `translation-memory.json`, `translation-policy.md`, the four `upstream-*`
  recipes, and the `upstream_sync` manifest block.
- **The three sync records are SUPERSEDED IN PLACE, not deleted** — report-first application, atomic promotion and symlink refusal were real decisions that were implemented, and the reasoning still
  applies to any future tool that copies files into this tree. Governance 711 → 690 checks and tests 57 → 46, both from removing real coverage of a real tool rather than from anything breaking.

### Added — the stack's own growth mechanism, and cost measurement

- **`scripts/propose_evolution.py` and `just evolve`.** Retiring sync removed the only mechanism that ever ADDED to this stack; without a replacement the library freezes at whatever it happens to
  contain while the field log accumulates evidence nobody acts on. It detects repeatedly overridden owners, routes rated *worse*, capabilities never selected, and dispatch cost that has not yet bought
  anything — and writes a dated review document.
- **It proposes and never applies, deliberately.** [Rule 0001](.archcore/rules/0001-safety-model.md) excludes material change without explicit operator authority, and field data is the weakest
  evidence in the project. A tool rewriting the catalogue from self-reported, confounded, small-n data would breach the safety model using the least trustworthy input available. The retired sync had
  the right shape — apply the safe classes, propose the rest — and it is worth keeping now the tool is gone; here nothing qualifies as safe, so everything is a proposal. Below 10 entries it proposes
  nothing and says why.
- **The field log now records cost two ways**: `tokens_estimated` (the agent's estimate, unverifiable by construction) and `dispatched` (a COUNT of subagents actually spawned, which is a fact and the
  dominant cost driver). When the two disagree, believe the count. The report splits median cost by dispatch and states the multiplier.

### Changed — SKILL.md trimmed 21%, with no capability lost

- **26,063 → 20,276 chars (~6,479 → ~5,069 tokens), paid on every single invocation.** The skill violated its own `SKILL_STANDARD.md`, which says keep `SKILL.md` procedural and put detailed knowledge
  in `references/`.
- **Rationale moved, not deleted**, into three reference files each carrying its own trigger condition so an agent loads it only when relevant: `skills/skill-agent-stack/references/gate-model.md` (why
  gates are shaped this way, the adjacent-capability trap, why closure is code), `skills/skill-agent-stack/references/domain-profiles.md` (networking and physical-product heuristics — read when the
  task is in that domain), `skills/skill-agent-stack/references/field-log.md` (why the log exists and how to read it).
- **The `eval-routing-contract` block is byte-identical** — `routing_contract()` still hashes to `d4a8b8cb7c58b945`, verified before and after, so every prior evaluation stays comparable.

### Notes

- **The closure wiring added earlier today is running in live use.** Field entry 4, written by another session at 05:32Z, records `scripts/close_route.py` being run, escalating `critic-munger` and
  `qa-bach` on production-change and high-consequence tags, and the agent honestly logging a partial follow because it held both undispatched for a design-only turn.
- Freeze re-recorded at 20260903_1600 (`orchestrator_sha` → `1369bf235408a4d1`).

## 20260903_1400

### Fixed — the field log's override statistic, caught by its own first three entries

- **A stated non-override was being counted as an override.** The first real entry ever logged carried `--overrode "none - direct route, no gates true (read-only)"` — a description of *not*
  overriding. The report read it as a change and showed **overridden on 3/3 uses**; corrected, it reads 2/3. The failure direction matters: every clean route would have inflated the override rate, so
  the log's one statistic degraded silently and flatteringly as it grew.
- **Fixed on both sides.** `skill-agent-stack` Step 10 now says to OMIT `--overrode` when the route was followed and never to pass `"none"`; `scripts/field_log.py` normalises such values on read as
  well as refusing them on write, because the file already contains one and future recorders include agents that will not have read the skill.
- **A prefix rule alone gets this wrong in both directions**, which is why change-verbs are checked first: *"none of the skills fit so I swapped owner to devops-hightower"* is a real override that
  starts with a negation, and hiding it would be the worse error — understating the defect signal rather than inflating it.
- **Two regression tests, negative-tested** across 15 boundary cases including a bare dash, the "n slash a" form, `no-override-needed` and the two "none"-prefixed opposites. Two pattern defects were
  caught by running them rather than by reading the regex: `-{1,3}\b` never matched a bare `-`, and `(?![\w-])` blocked its own match on `no-override-needed`. Suite 55 → 57.

### Fixed — a governance check that failed on fractions

- **The path check treated any backticked token containing a slash as a repo-relative path**, so the "n slash a" form and `2/3` in prose failed the build. Three false failures in one session is enough
  evidence: a token containing **no letters** is now exempt.
- **The exemption is proved unable to hide a real path**: all 287 tracked paths contain at least one letter. Negative-tested afterwards — a reference to a reference to a made-up script path still
  fails, so the check retains its actual job.

### Changed — the three existing entries migrated

- **The one affected entry was corrected in place**, and its text MOVED rather than deleted: `overrode: "none - direct route, no gates true (read-only)"` became `note: "no override: none - direct
  route, no gates true (read-only)"`. Correcting a statistic is not a licence to destroy an observation — that text says WHY nothing was changed, which is worth knowing, and this is real field
  evidence that cannot be regenerated.
- **Verified byte-identical on everything else**: three rows, same order, same timestamps, entries 2 and 3 unchanged in content. The report moved from `overridden on 3/3 uses` to `2/3`.
- **The write side now moves such text to `note` too** rather than dropping it, so a future recorder that ignores the instruction loses nothing either. An existing `--note` is never clobbered.

### Notes

- **The three real entries are the first field evidence this project has.** One direct read-only route followed clean; one where the agent ran the CTO and critic passes inline rather than dispatching
  personas, judging dispatch cost above benefit; and one **correcting that entry** — the critic gate was dispatched after all, and found three defects the inline pass missed while overturning one of
  its findings. The agent logged its own correction rather than leaving the flattering record standing, which is exactly what Step 10 asks for and the only reason the log is worth anything. n=3, one
  project, self-reported: an anecdote, and the report says so in its own output.
- Freeze re-recorded 20260903_1400 (`orchestrator_sha` → `ef66ffacb2918e6d`). 711 governance checks, 57 tests, freeze PASS.

## 20260903_0330

### Changed — the `orchestrator` skill package is now `skill-agent-stack`

- **Renamed for the surface it is actually used from**: Claude Code's skill list, where `orchestrator` said nothing about which stack it belonged to. The identity changed in the four places that
  define it — the package directory, the `SKILL.md` frontmatter `name`, `routing.toml`'s `id` and `default_entry`, and the `manifest.yaml` registration — plus every path reference and the live
  install.
- **Two things deliberately NOT renamed.** The `orchestrator-follett` persona is a different capability and keeps its name. The `orchestrator_sha` provenance stamp keeps its name too: it appears in 40
  indexed runs and in every stored result row, so renaming the field would break their comparability to record a cosmetic change. It names the routing-contract file, whatever that file is called.
- **Dated audit documents under `docs/` keep the old id in their prose.** They are point-in-time records of what the skill was called when they were written; only their path references were updated.

### Fixed — a status check that reported false confidence

- **`install_global.py --status` gained orphan detection.** The rename left three broken symlinks — one per client — and `just global-status` reported **123 correct without mentioning them**, because
  a status report built only from *declared* links cannot see a link nothing declares any more. That is the exact shape of a false-confidence check, and the project's own rule is to fix the check
  rather than the symptom.
- Orphans are read with `os.readlink` rather than `resolve()`, because **a broken symlink still has a target and that target is what identifies it as ours**. They are reported alongside the declared
  links rather than folded into the same counts, so a clean report stays unambiguous.
- **The first implementation was wrong and the negative test caught it**: `CLIENT_ROOTS[client]` is a `{purpose: path}` mapping, so iterating it yielded keys and the check looked in `~/skills`, which
  does not exist. It reported nothing and would have passed review as working. Fixed to iterate values; re-tested by recreating a stale link and watching `orphan-broken` appear, then removing it.

### Notes

- Freeze re-recorded at 20260903_0330: `routing_catalogue_sha`, `orchestrator_sha` and `harness_sha` all moved. Validator PASS (52 capabilities, 15 personas, 37 skills), corpus PASS (60), 707
  governance checks, 55 tests, run index 40/40 verified, 123/123 links correct with zero orphans.

## 20260903_0230

### Changed — field capture happens in the skill, not in a chore

- **The orchestrator skill gained Step 10 — Record the Route.** When Claude Code invokes the skill in any project, the agent logs the route itself at the end of the task: what the work was, who it
  named as owner, whether it followed its own route, and what it used instead. One stdlib-only command, absolute path, no operator involvement. Operator decision 20260903: the `just` recipes would not
  have been run, and a capture mechanism nobody runs collects nothing.
- **`--helped` is now operator-only and optional.** An agent must not self-assess whether its own routing helped — that is the one field where the recorder has an interest in the answer. Absent is the
  honest default, and the report prints *"none rated — this field is operator-supplied"* rather than showing a blank column that reads as missing data.
- **`--followed` and `--overrode` stay with whoever did the work**, because only they know what was actually used. The skill says explicitly to record a departure as readily as a kept route: a
  departure is the valuable entry, and hiding it makes the log worthless.
- **The skill also carries the standing caveat at the point of use** — trust owner and skill selection, treat the gate flags as advisory noise ([rule
  0012](.archcore/rules/0012-gate-flags-are-advisory-until-localised.md)).

### Notes

- **Step 10 sits at line 285, far below the `eval-routing-contract` block that ends at line 47**, so evaluation prompts are unchanged — verified by hashing `routing_contract()` directly. The live
  install picked the change up immediately, the install being symlinks rather than copies.
- **Freeze re-recorded at 20260903_0230**; `orchestrator_sha` `283664a753137a61` → `ebb6872c60f95444`. Recorded alongside it, a known imprecision left deliberately unfixed: that stamp hashes the whole
  skill file while only the marked block is a prompt input, so an edit elsewhere trips `freeze-check` for a change that cannot affect a measurement. Stamping the block would be more precise and would
  make new stamps incomparable to every one already recorded. **Over-coverage produces false alarms; the alternative risks false confidence.** Governance 704 → 707 checks.

## 20260903_0200

### Added — field use, the measurement no corpus can make

- **[`scripts/field_log.py`](scripts/field_log.py), `just used` and `just field-report`.** Records what the router actually did on real work: the route it gave, whether it was followed, whether it
  helped, and — the load-bearing field — **what was overridden and why**. Appends to `evals/field-log.jsonl`, tracked in the repo, because a re-run regenerates an eval and nothing regenerates a day of
  real use.
- **The report is honest about its own weakness.** The data is observational, self-reported, confounded by task difficulty and by whatever the operator was going to do anyway; it cannot establish
  causation. Below n=10 the report prints that in the output rather than leaving the reader to remember it. What it can surface is a pattern too consistent to be noise — the report flags any owner
  overridden three or more times.
- **[Spec 0008 — replay corpus contract](.archcore/specs/0008-replay-corpus-contract.md)** (proposed). Written before any mining, because the failure mode is fatal and quiet: a replay case labelled
  from an opinion about who should have owned it is the author's routing judgement in a costume, and running the router against it measures agreement between two guesses while looking like a result.
  Every assertion must cite an artifact that exists; omission is the correct answer for anything unevidenced.

### Changed — priorities

- **Field use is now the live item; replay, shadow-mode and Holdout 2 are parked behind it.** Operator decision, and the right one: two days of measurement tested whether the router agrees with a
  corpus, which is necessary and not sufficient. A route can be perfectly corpus-correct and still not make the work better, and the corpus cannot detect that because it is the thing being agreed
  with.
- **Shadow-mode is largely subsumed by field use**, which collects the same disagreement signal during real work rather than as a separate exercise nobody has time to run.
- **Holdout 2 is now conditional on the field result.** If routing genuinely helps, it is worth the tokens. If the routes are fine but the personas add little, that is a more important finding than
  another 24 cases would have produced — and only field use can produce it.

### Notes

- **Install verified live at the decision point: 123/123 symlinks correct** across `~/.claude`, `~/.codex`, `~/.agents`. Nothing to install; the stack is usable as it stands.
- **Standing guidance for that use** ([rule 0012](.archcore/rules/0012-gate-flags-are-advisory-until-localised.md)): trust the owner and skill selection, override the gate flags. Governance 698 → 704
  checks.

## 20260903_0030

### Added — the gate question is answered

- **A / B1 / B2 run to completion on DeepSeek Flash** ([full record](docs/routing-evaluation/gate-only-analysis-20260903_0030.md), [`scripts/gate_eval.py`](scripts/gate_eval.py)). **Isolated gate
  judgement is a real classifier on two model tiers** — predicted-positive rate 0.48/0.37/0.20 on Flash against base rates 0.50/0.37/0.22, and 0.37/0.53/0.38 on Claude — while the **integrated router
  sits at 1.00 on all four gates**. The gate-semantics hypothesis is dead: the definitions are learnable, and judging them while constructing a route is what destroys the signal.
- **The aggregate result is misleading and the conditional breakdown reverses it.** B2 beats B1 by +9 cases and +5.38 mean, which reads as "gate errors contaminate routing". Split by stage-A error
  type: correct 17% B1-failure, **over-asserted 30% (n=10), under-asserted 100% (n=11), both 100% (n=3)**. Where stage A was right, B1 30/36 versus B2 29/36 — indistinguishable. `missing gate` hard
  failures: B1 17, B2 1. **Over-assertion is not detectably costly; under-assertion is fatal.**
- **Production makes only the harmless error**, because an always-true router has recall ~1.0 and zero false negatives by construction. For production's error profile this is spec 0007's **B1 ≈ B2**
  row, reached conditionally. The collapse costs tokens, team size and operator signal — not accuracy — and drops down the queue.
- **Recorded as a standing warning: the naive fix is dangerous.** "Make the router less trigger-happy" trades precision for recall, swapping a free error for a fatal one. Any calibration work must
  hold recall at 1.0.
- **[Rule 0011](.archcore/rules/0011-gate-errors-are-asymmetric.md) independently confirmed.** Its −20 hard / −5 soft split was chosen on judgement before any of this was measured; the measured
  downstream ratio is 100%-failure against indistinguishable-from-baseline.

### Changed — Claude Code retired as this project's runner

- **`claude -p` is session-limited, not token-metered.** A full routing prompt is ~49,000 characters, so a sweep dies after roughly five calls. Measured twice: holdout 24 lost 5 of 24 silently, and
  gate-only B1 lost **55 of 60** — named this time, because the harness now reports stdout: `You've hit your session limit`. Default arm is now `deepseek-v4-flash` via Hermes, with the reason recorded
  inline in the justfile.
- **Flash qualified 60/60 at realistic payload** (44,066-char probes, median 14.6s). Across 120 routing calls its only faults were 5 transient parse failures, all of which succeeded on retry.
- **[Spec 0006 Amendment 1](.archcore/specs/0006-runner-qualification.md) was validated by events within the hour.** Written on theoretical grounds — that trivial probes are 761× smaller than a real
  prompt and so never test quota headroom — it then described the live Claude failure exactly.

### Fixed

- **Recipe quoting defect, caught by qualification before it reached a corpus.** `qualify-runner` interpolated `{{command}}` inside double quotes, so a `$(cat)` in the command expanded against the
  recipe's own empty stdin: 0/60 calls, one identical 0.34s failure signature. Had this shipped into a sweep, 60 cases would have scored 0.0 and the arm would have looked dead rather than mis-invoked.
  Fixed in `qualify-runner` and `holdout`.
- **`scripts/gate_eval.py` gains `--case` + `--merge-into`** for targeted repair of a sweep that lost cases, **recording the repair** in the artifact's provenance so a merged artifact can never read
  as a single clean sweep. Used twice: B1 (2 parse faults) and B2 (3).
- **All output flushed per line.** B1 ran 40 minutes completely dark because ~2 KB of output sat under Python's 8 KB buffer; during the Claude collapse, per-case failures only surfaced after 55 had
  burned.

### Notes

- **Ownership is now the leading open routing defect.** B1 and B2 both carry ~10 `missing required persona` failures, unchanged between them — untouched by gates, and the same class as all three
  holdout 24 failures. Evidence must come from replay or shadow-mode, never from the spent 24. Governance 672 → 692 checks.

## 20260902_1240

### Added — the runner is now qualified before it carries evidence

- **[`scripts/qualify_runner.py`](scripts/qualify_runner.py) and `just qualify-runner`.** Sends N disposable prompts down the same path a real run uses — stdin, invoke, the harness's own
  `extract_json` — and names every outcome: `ok`, `timeout`, `nonzero-exit`, `silent-failure`, `unparseable`. Five checks, **each negative-tested against a fake runner**: a silent-failing runner fails
  sequence reliability, a prose-returning runner fails parse reliability, an unlabelled run fails labels. The failure-legibility probe is offline (`exit 7`) and costs no model call.
- **`just holdout` now depends on `_require-qualified` as well as `_require-freeze`**, and the receipt records `qualified_for_corpus_size`. Verified: with no receipt the run refuses; with a receipt
  covering 5 calls it refuses a 24-case run with `receipt covers 5 calls, this run needs 24`. Qualification is perishable — it expires when the runner, its credentials, its quota state or the harness
  changes.
- **The observability half of the defect is fixed** ([plan 0003](.archcore/plans/0003-holdout-two-protocol.md) precondition 2). `run_command` now reports **both** streams on a non-zero exit, and says
  so explicitly when both are empty: `both streams empty — the runner exited without explaining itself (quota, session limit or transport are the usual causes)`. Holdout 24's five losses produced
  `command exited 1:` with nothing after the colon, which is not a diagnostic.

### Changed

- **[Spec 0007](.archcore/specs/0007-gate-only-evaluation.md) refined to three measurements**: A (gates alone), B1 (route with the model's own gates), B2 (route with ground-truth gates), with an
  interpretation matrix mapping each outcome pattern to a located defect. The row worth stating in advance is **B1 ≈ B2**: gate over-assertion may be real, measurable and cost the route nothing
  downstream, in which case the finding is recalibrated rather than acted on.
- **Thresholds pre-registered before any run**: per-gate recall ≥ 0.80, precision ≥ 0.75, specificity ≥ 0.80, macro F1 ≥ 0.78. A gate missing any threshold fails, and a failing gate fails the
  measurement — no aggregate may rescue it, because aggregate F1 is exactly what would hide a classifier that is constant on one gate. Moving a threshold after seeing a result requires a dated,
  reasoned amendment recorded before the next run.
- **Predicted-positive rate added as the anti-degeneracy check.** It is the one number class imbalance cannot flatter; it must sit strictly inside (0.05, 0.95) on every gate, and outside that the run
  fails regardless of the other four metrics. On holdout 24 it was **1.00 on all four gates**.
- **Runner qualification sequenced ahead of the gate-only sweep**, even though the development 60 cannot be spent: an execution error is excluded from the denominators, so an unstable runner silently
  changes which cases precision and recall are computed over, and a metric on a shifting subset cannot be judged against a pre-registered threshold.
- **Freeze re-recorded at 20260902_1240** — `harness_sha` `5f15fb18ffed3f3b` → `f4e9a470c84e2a6a` for the both-streams fix. `freeze-check` refused the holdout in between, as designed. Governance 657 →
  672 checks.

### Notes

- **Nothing in the routing catalogue, the gates, the precedence table, the closure module, the scorer or any case was changed.** The routing-development phase stays closed. The open question is
  narrower than routing quality: can the model discriminate gate truth when gate classification is isolated from routing? If it cannot, some gates should stop being model judgement.

## 20260902_1215

### Added — status is derived now, not restated

- **`evals/runs.toml` and [`scripts/index_runs.py`](scripts/index_runs.py)**: one record per evaluation run, **40 backfilled** from the stored rows. Every metric is computed — counts, pass rate, mean,
  gate error classes, a failure-class histogram, and the five provenance hashes the rows already stamp. The authored fields (`purpose`, `status`, `interpretation`, `supersedes`, `notes`) are written
  by a person and verified to survive regeneration.
- **`just runs-check` re-derives everything and fails on drift**, and is now part of `preflight`. Negative-tested: changing one recorded metric produces `index says 12, evidence says 62`; an unindexed
  result file is reported too. Because results live in the rebuildable working cache, a record whose evidence is absent is reported **UNVERIFIABLE** rather than failed — verified by pointing the tool
  at an empty directory, which exits 0 and names every unverifiable run.
- **The index resolves each run's corpus from its stamped hash**, and says so when it cannot: **39 of 40 runs stamp a corpus hash that no longer resolves to any file in the tree**, because the
  development corpus has been edited repeatedly since. That is not a defect — it is the honest statement that those runs are not reproducible against today's file, and it was previously invisible.
- **[Spec 0007 — gate-only evaluation and precision/recall scoring](.archcore/specs/0007-gate-only-evaluation.md)** (proposed). Separates gate classification from route construction so the collapse
  can be localised: if gate-only is also all-true the defect is in the gate semantics, if gate-only is good the defect is instruction load. Scores precision, recall, F1 and specificity per gate,
  because pass/fail is the wrong instrument for a classifier — an always-true router scores recall 1.0, precision ~0.25, **F1 ~0.40**, and only a discriminating one scores well.

### Changed

- **Interpretation of every baseline from `v1 after gate defs` onward is formally superseded**, in place, with the measurements left untouched. Gate recall in all of them was bought by destroying gate
  precision, so **v4's 79–80% is not evidence of balanced gate routing** — it is good ownership and skill selection plus a gate classifier that always answers yes. Ownership/skill findings and gate
  findings are reported separately from here on.
- **`holdout24-claude-20260902` recorded as `status = "spent"`** with its purpose and interpretation authored, and its three evidence paths (JSONL, log, freeze receipt) recorded.

### Notes

- **The run index is the durable fix for the drift this session hit**: holdout 24 produced evidence while three hand-maintained surfaces still called it unexecuted. A status restated in three places
  drifts; a status derived from rows and checked in `preflight` does not. Governance 646 → 657 checks.

## 20260902_1140

### Changed — Holdout 24 executed and SPENT

- **16/19 passed (84.2%), mean 71.1, five runner failures excluded.** Claude arm, `--repair` on, freeze verified and captured immediately before launch at git HEAD `1201e42`. Evidence in the working
  cache: `routing-results/holdout24-claude-20260902.{jsonl,log,freeze.txt}`. Full classification:
  [docs/routing-evaluation/holdout24-analysis-20260902_1120.md](docs/routing-evaluation/holdout24-analysis-20260902_1120.md).
- **Nothing was changed in response to the result.** No expectation, catalogue entry, gate, precedence rule, closure behaviour, scorer or case was edited. The three ownership failures stand exactly as
  authored, including `hjdm-workshop-channel`, which was pre-registered as ambiguous before the run and failed in precisely the predicted direction.
- **Status reconciled.** `MEMORY.md` and `SCRATCHPAD.md` described the holdout as unexecuted while the result files proved otherwise — the same class of defect as a stale constant, a claim nothing
  verifies. Both now record the result, the evidence paths and the spent status.

### Added

- **The finding that matters: gate judgement has collapsed to always-true across every arm.** All 19 scored cases set all four gates true. Re-analysing every stored result set — no model calls, the
  exact use [rule 0011](.archcore/rules/0011-gate-errors-are-asymmetric.md) was built for — shows `full` (before gates were defined) at **0/60** all-true with 41 missed gates, and everything after it
  at 53–58/60 all-true with 2.4–3.3 false positives per row, on Flash, Pro and Claude alike. Defining the gates on 2026-09-01 converted a systematic false-negative problem into a systematic
  false-positive one, and it stayed invisible for a day because the scorer penalised only one direction. The v4 79–80% headline measured a router that discriminates ownership and skills well and does
  not discriminate gates at all.
- **[Spec 0006 — runner qualification](.archcore/specs/0006-runner-qualification.md)** (proposed). No single-use corpus goes through an unqualified runner. Five consecutive `claude -p` calls exited 1
  with empty stderr, costing 21% of a one-shot corpus to a fault the evidence cannot even classify. Requires sequence reliability at corpus size, parse reliability, legible failures, timeout behaviour
  and labels — all on disposable cases.
- **[Plan 0003 — Holdout 2 protocol](.archcore/plans/0003-holdout-two-protocol.md)** (proposed). Preconditions before a second blind corpus, and what the spent 24 may and may not be used for.
- **`docs/` and its index**, registered in `CATALOGS` and negative-tested in both halves. The project root now carries governance and contract entrypoints only; audits, proposals, classifications and
  evaluation records live in `docs/`. Path resolution caught all ten references broken by the move, which is the check behaving exactly as its rule promises. Governance 599 → 643 checks.

### Notes

- **The pass rate is the least informative number in the run.** 84.2% sits in the pre-registered strong band, but it survives only because over-assertion is soft by design; the mean of 71.1 against a
  ceiling of ~90 is the honest summary. Read the mechanism, not the headline.
- **All three genuine failures are ownership**, and two cite the precedence table and reach a different answer from the author with a stated rationale. That is a contract question, not a routing
  defect. `hnet-radius-postmortem` exposes a boundary the table does not cover at all: incident root-cause versus operational corrective action.

## 20260902_1015

### Added — the unseen holdout, authored and frozen, NOT executed

- **`evals/holdout-cases.toml`: 24 cases** — 5 networking-infrastructure, 5 jdm-import, 4 software-ai-engineering, 4 atar-import, 3 business-research, 3 direct-adversarial. Authored blind to the
  frozen 60. The only thing read from that corpus was its SCHEMA — key names, the six `mode` values, the observed `max_personas` range — printed by a script that displayed no task, no id and no route
  expectation, so the prompt shape matches the development corpus without any case reaching the author.
- **Task text first, expectations second.** Every case was written as work that would plausibly arrive from this operator, then had ownership, gates and capabilities assigned from the task as written.
  No case was built backwards from a route worth testing.
- **Gate coverage was not balanced deliberately** and came out lopsided: 13 of 24 assert no gate at all, 6 research, 4 critic, 1 QA, 6 runtime. Forcing an even spread would measure the router against
  a design instead of against the job, and 13 no-gate cases is a stronger over-routing test than a balanced set would have been.
- **`--cases` on the evaluator**, so the holdout is scored by exactly the scorer the baselines were scored by rather than a forked harness. The stamped `eval_corpus_sha` follows the flag, so a holdout
  row can never be mistaken for a development-corpus row.
- **`just holdout`**, guarded by `_require-freeze` and refusing to run without provider/model/output labels — an unlabelled holdout row is not comparable to anything, and the corpus is single-use.
- **Three integrity tests over the holdout**, negative-tested: the declared shape and resolvable references, `runtime_required` earned in BOTH directions, and every asserted gate closable by the
  case's own required + preferred contract. Suite 52 → 55; governance 589 → 598 checks.

### Changed

- **Freeze re-recorded at 20260902_1015** and extended to six artifacts. `harness_sha` moved for the `--cases` flag; `holdout_corpus_sha` is new and is hashed locally by `scripts/check_freeze.py`
  rather than stamped by a run, because until the holdout is executed no result row carries it.
- **The under-statement direction of `runtime_required` is now a defect too.** Spec 0005 required an asserted flag to be earned; since gate over-assertion started costing 5 points, a case asserting
  `false` while expecting a tool-class provider penalises the route for an error the case itself caused. Both directions are asserted for all 24.

### Notes

- **`just freeze-check` caught the `--cases` edit against the 0935 record before anything ran** — the exact drift guide 0003 step 1 describes, and the first time here that a tool rather than an
  agent's memory caught it. The freeze was then re-recorded after the last edit, which is what step 1 actually asks for.
- **Nothing was executed.** No model was called against any holdout case. `just --dry-run holdout` was used to verify the recipe's interpolation and guard ordering without spending the corpus.

## 20260902_0950

### Added — the freeze is now checkable

- **`scripts/check_freeze.py` and `just freeze-check`.** Recomputes the five stamped hashes and compares them to the table `MEMORY.md` records, printing per-artifact OK/drift and exiting non-zero with
  the artifact that moved. Negative-tested by appending a comment to `scripts/close_route.py`: the run went red naming `closure` alone, and green again on restore.
- **It imports `run_provenance` from the evaluator rather than hashing the files itself.** A second implementation would drift from the stamping one and could then verify a freeze that no result row
  was ever measured against.
- **It parses `MEMORY.md` rather than a second data file.** `.archcore/README.md` gives `MEMORY.md` ownership of measured figures; duplicating the hashes into a machine-readable copy would create two
  records of one fact and let the human-readable one go stale while the check passed. The row pattern anchors on `^\|\s*` so the mandated table formatter's alignment padding cannot break it.
- **`_require-freeze`**, a private justfile guard for recipes that record a comparable run. Depend on it from a baseline or holdout recipe; never from a smoke recipe.
- **Two tests covering the RECORD, not the verdict** — five well-formed stamps, and every stamp still one the harness actually writes. Asserting the checkout currently matches the freeze would put a
  drift failure inside `preflight`, which is the coupling this design exists to avoid. Negative-tested by renaming a stamp in the record. Suite 50 → 52.

### Changed

- **[Rule 0011](.archcore/rules/0011-gate-errors-are-asymmetric.md) accepted by the operator**, `proposed` → `accepted`, stamped `Accepted: 20260902_0950 by operator`.
- **[Guide 0003](.archcore/guides/0003-running-a-routing-baseline.md)** now names `just freeze-check` in step 1, describes the coverage line in step 3, and gains a section stating that the scorer is
  part of the freeze — fix a scoring defect BEFORE authoring a single-use holdout, never after, because a holdout scored under a scorer you then correct has been spent and has answered nothing.

### Notes

- **`freeze-check` is deliberately absent from `preflight`.** Preflight answers "is this repository internally valid"; freeze-check answers "does it match one particular evaluation snapshot". A
  legitimate catalogue change must be able to pass the first while failing the second — wiring them together would convert a historical reference into a standing prohibition on ever changing the
  catalogue, which this project's rule against enforcing history forbids. Governance 573 → 587 checks.

## 20260902_0935

### Changed — measurement integrity, before any unseen holdout is authored

- **Gate scoring is now asymmetric**, negative-tested in both directions. A false negative (case requires the gate, route omits it) stays a hard `-20` that decides pass/fail; a false positive (route
  fires a gate the case does not require) is a soft `-5` that never does. Until now over-assertion cost **nothing**, so "set all four flags true" was a free strategy that beat honest routing on every
  case with a required gate — Claude did exactly that on `market-size` in Baseline v4 and paid no penalty. Measured on that case: an all-gates-true route scored 90.0 before and scores 80.0 now, while
  an honest route is unmoved at 90.0. See [rule 0011](.archcore/rules/0011-gate-errors-are-asymmetric.md), status `proposed`.
- **The two classes are counted separately**, not folded into one gate-error total: `gate_false_negatives` and `gate_false_positives` land in every stored result row and are totalled in the run
  summary, so a stored baseline can be re-analysed for over-assertion without calling a model again.
- **Coverage is reported rather than inferred.** Every run prints `covered X/Y cases` measured against the pool BEFORE `--limit` applies, plus `WARNING: partial corpus run` when the limit truncated
  it. The first Baseline v2 pass ran `--limit 10` per family, covered 53 of 60 because two families are larger than 10, and printed per-family lines that read as complete.
- **`GATE_FLAGS` is named once** and consumed by both use sites in the evaluator. The tuple was previously restated at each one, which is how a flag quietly stops being covered at one site while the
  others still cover it.

### Added

- **`closure_sha` in the run provenance stamp.** `scripts/close_route.py` rewrites the route before scoring under `--repair` — measured at +13 cases on the frozen 60 — and was covered by no hash at
  all, so a repaired run was not reproducible from its own row. It is stamped but deliberately absent from `prompt_inputs`: it reaches the score, not the prompt. Same reasoning as [rule
  0009](.archcore/rules/0009-provenance-covers-inputs.md), found while freezing the measurement contract rather than by a check.
- **Four regression tests**, each verified to go red against a deliberate break: the `-5` per surplus gate, over-assertion never flipping the verdict, a missing gate still failing hard, and
  `select_cases` reporting the pool it drew from. Suite 46 → 50; governance 566 → 570 checks.

### Notes

- **Baselines measured before this change are not comparable to ones measured after**, for any case where a route over-asserted. Compare stored rows by re-scoring them with `--rescore`, never by
  putting the two published means side by side.
- **`runtime_required` cannot be over-asserted.** It is scored against the computed value — true exactly when a selected skill declares `execution = "tool"` — so a model reporting it without selecting
  a tool skill is corrected, not penalised. Only the three judged gates carry the soft penalty.

## 20260902_0300

### Changed

- **All 29 `.archcore/` documents accepted by the operator.** `Status: proposed` → `accepted`, each stamped `Accepted: 20260902_0300 by operator`. `.archcore/` is now the highest-authority statement
  of what this project has decided, and `AI_NAVIGATION.md`, `context-map.yaml` and `.archcore/README.md` say so.
- **A new check keeps the status field honest**, negative-tested in both halves: every `.archcore/` document must declare a status in `{proposed, accepted, superseded}` and carry a `Source:` line
  naming what it was promoted from. Without it, "accepted" is a word nothing verifies and a document's provenance can be lost by a careless edit. Governance 502 → 560 checks.

### Notes

- **`superseded` is deliberately in the allowed set.** An accepted document is superseded **in place** with a dated banner naming what replaced it and what still stands — never deleted, because the
  superseded reasoning is usually the part a later reader needs. [ADR 0009](.archcore/adr/0009-sync-apply-is-atomic.md) is the worked example: it supersedes a deferral recorded in `REVISION_NOTES.md`
  and says so in the document.

## 20260902_0245

### Added — Archcore promotion

- **29 `.archcore/` documents promoted**: 9 decisions, 10 rules, 5 contracts, 3 guides, 2 plans, each with a provenance header and `Status: proposed`. `.archcore/README.md` is the durable index and
  carries the never-promote table out of the candidate queue.
- **The candidate queue was REGENERATED before promoting, not promoted as found.** The 20260901_1255 queue predated the capability registry, ownership precedence, route invariants and deterministic
  closure — it contained zero mentions of any of them. Promoting it would have written the architecture as it stood before the work that defines it. Regenerating surfaced three concrete errors it
  would otherwise have carried in: a rule quoting the superseded `mise exec --` interpreter form, a deferral of atomic sync work that had been implemented hours earlier, and a never-promote entry
  saying the audit-prompt/audit-report supersession was unresolved when it had been resolved.
- **`ARCHCORE_PROMOTION_CANDIDATES.md` deleted**, as `promote` requires — it is a proposal queue, not a record. It was already registered in the checker's `CONDITIONAL_PATHS` at bootstrap, so
  historical mentions in this file still resolve.
- **Catalog coverage for `.archcore/`**, negative-tested: an uncataloged document there now fails the build. The glob is `**/*.md` deliberately — the documents live in subfolders, and a non-recursive
  glob would have reported full coverage while checking nothing. Governance 441 → 501 checks.

### Changed

- `AI_NAVIGATION.md` and `context-map.yaml` route to `.archcore/README.md` as **highest authority** and no longer mention the candidate queue.

### Notes

- **The division of labour with `MEMORY.md` is stated in the index rather than left implicit**, because duplicating it is the two-taxonomies problem this project already paid for once with
  `satisfied_by_skills`. `.archcore/` holds decisions, rules and contracts — the shape of the system; `MEMORY.md` holds measured baselines, metric definitions and traps. **Every measured figure is on
  the never-promote list**: a re-run moves it, and a promoted copy would be stale within a day and would then contradict its source. The test applied to each candidate: *would it still read as true
  after the next three baselines?*
- Generated by `skill-ai-it` in `promote` mode, following a `refresh`-style regeneration of the queue in the same session.

## 20260902_0130

### Changed — one persona model, relaxed contracts, corpus frozen

- **P1 RESOLVED: `routing.toml` now carries ONE persona model.** All twelve `[[routing_rules]]` are explicitly advisory keyword hints; the seven that used `require_personas` now use `prefer_personas`.
  `economics-gate` and `import-economics-gate` are renamed `economics-owner` / `import-economics-owner` so nothing in that table pretends to be a gate. Mandatory-ness now lives in exactly three
  places: `[[gates]]` (what the route owes), `[[precedence]]` (who owns a contested decision), `[[route_invariants]]` (what makes a route invalid). **Two validator guards, both negative-tested**,
  reject a `require_personas` or a `*-gate` id in that table, so the contradiction cannot return.
- **`required_personas` is for mandatory ownership, not an ideal team** — policy now stated in the corpus header. Three cases relaxed under it: `net-security-review` keeps `cto-vogels` (the
  deliverable IS security posture) but drops `qa-bach`, because the case already requires `security-audit`, which provides validation at primary strength; `python-feature` is ordinary implementation
  against settled criteria, so a validation capability suffices; `jdm-portal-build` keeps `product-norman` ("define and build" means requirements are open) and drops the rest of its four-persona team
  to preferred.
- **The 60-case corpus is FROZEN as a development set**, with the reasoning in an in-file banner. It took routing from a specification failure through ownership precedence to a measured architecture,
  and proved deterministic closure worth +25 to +40 points across three models. Past this point a better score on these 60 is evidence of fitting the corpus, not of better routing. Next evidence must
  come from an unseen holdout and real-task replay.
- **P2: audit receipts archived out of the repository** to the working cache under audit-archive/20260901 with a README recording that the gate ended FAILED and why. They were blocking the next audit
  run, which is correct behaviour — so they moved rather than being deleted. The now-stale `.gitignore` entry is removed.

### Notes

- **A recommendation was declined on evidence, not preference.** The advice to give `atar-supplier` to `cfo-campbell` rested on all three arms independently choosing CFO — true of the pre-closure
  runs. Since closure and the shared contract landed, **all three arms choose `research-thompson` and pass** (v4 ×3 and v5). The earlier disagreement looks like a symptom of the `routing_rules`
  contradiction: `economics-owner` was *requiring* `cfo-campbell` on any keyword match, and "landed cost" is such a match. Changing the corpus now would break a case four consecutive runs agree on.
  Raised rather than executed.
- Static effect of the relaxations, measured with closure and no model calls: stored v3 routes **47/60 → 50/60**, v4 Claude holdout **16/20 → 19/20**. Stated plainly: that gain is a contract decision
  about what the corpus asserts, not an improvement in routing capability.

## 20260902_0015

### Added — Baseline v4, and the eval now measures the contract production uses

- **Baseline v4: the same 20-case holdout, all three arms, live, with deterministic closure.** Flash **13/20 (65.0%)** mean 85.7 · Pro **15/19 (78.9%)** mean 89.1 · Claude **16/20 (80.0%)** mean 89.2,
  against 40.0 / 50.0 / 40.0 without closure. **Every arm gains 25–40 points**, every mean rises to ~89, and the two production arms converge near 80%. Model tier still matters, but far less once
  closure is deterministic.
- **The behavioural eval now builds its prompt from the PRODUCTION orchestrator skill.** A marked `eval-routing-contract` block in `skills/skill-agent-stack/SKILL.md` is read verbatim by
  `scripts/evaluate_routing.py`; the routing principles that were a literal inside the evaluator are gone. Until now the eval could have scored a contract production did not use, and **no check would
  have noticed** — an eval that drifts from the artefact it measures is worse than no eval, because it reports confidence about the wrong thing. Prompt version `AGENT_STACK_ROUTING_EVAL_V3`.
- **A validator guard, negative-tested**, refuses a missing or renamed contract block, so the arrangement cannot be silently undone. Missing markers raise rather than fall back to a default: a silent
  fallback would restore exactly the drift this removes.
- **Provenance now distinguishes inputs from neighbours.** Rows carry `prompt_inputs`, naming which stamped files actually reach the model. `orchestrator_sha` previously recorded a file the prompt
  never read — it raised an alarm while proving nothing; it is now a genuine input.

### Changed

- **Tags and `required_personas` are formally separated in `routing.toml`, and neither is derived from the other.** Tags are semantic characteristics of the task, judged by the model, and say *why* a
  generic policy applies. `required_personas` is a case-specific expectation and says *what* this route must contain. Deriving tags from the expected answer would destroy the corpus's ability to test
  task understanding separately from route correctness. Tags stay a judgement because a pattern-match over task text agreed with the corpus on only 5 of 21 cases.

### Notes

- **I walked a recorded trap a second time.** The v4 frozen set was published, then `skills/skill-agent-stack/SKILL.md` was edited mid-run — the exact failure MEMORY.md already lists. It changed the
  stamp, not the experiment, because that file was not a prompt input at the time, and all three arms stamp identical provenance so the comparison is internally valid. Knowing the rule did not prevent
  it; the per-row stamp did, by making the drift visible in seconds. The stamp being wrong in *design* — covering a neighbour rather than an input — is fixed above.
- Static regression after the contract move: closure on the stored v3 routes is unchanged at 34/60 → 47/60, confirming the refactor moved the source of the text and nothing else.

## 20260901_2130

### Added

- **`scripts/close_route.py` — deterministic route closure, and it works.** The model proposes owner / personas / skills / gates; the system then adds the minimum provider declaring each unmet
  `required_capability` at the required strength, escalates to the gate's persona where the task's tags demand independence, recomputes `runtime_required` from the selected skills, reports unmet tool
  prerequisites, and refuses to breach the team cap rather than trade one hard failure for another. It never overrules a judgement — it does not set `primary_owner`, does not decide which gates are
  true, and removes nothing.
- **Measured on the stored v3 routes with no model calls: 34/60 → 47/60 (78.3%), zero regressions.** On the 20-case holdout: Flash 8→14, Pro 10→15, Claude 8→15. The two production arms land
  identically and the model spread narrows from 10 points to 5. This clears the ≥70% target that prompt-based closure missed by thirteen points, and it settles the v3 null result: the fix was real,
  the mechanism was wrong.
- **`--repair` on `scripts/evaluate_routing.py`**, in both live and rescore modes, so closure can be measured on already-stored routes before being trusted in a live run.
- **`default_skill` on each judged gate** — the canonical general-purpose provider. Without it closure chose lexicographically among equally-qualified providers and reached for `code-review-security`
  where `senior-qa` was plainly meant.
- **Nine regression tests** for closure (46 total, up from 37), each tied to an observed defect or a promise the module makes rather than restating the implementation.

### Changed

- **The execution-error denominator is fixed.** Scored cases are valid parsed results only; execution errors are counted separately, with the uncorrected figure printed beside the corrected one so
  published numbers stay reconcilable. Re-reporting every run under both denominators shows the correction bites in exactly one place — **v2, whose published mean of 81.6 was depressed by its own
  `ui-only` timeout; corrected it is 83.0, identical to v3's.** That *strengthens* the v3 null result: on corrected means the two baselines are exactly equal, and v3's apparent +1.4 was a v2 artefact.
- **`runtime_required` assertions must be earned, and 4 of 7 were not.** The flag is computed from the selected skills, so asserting it hard while only preferring the tool skill that causes it is a
  case contradicting itself — and it made `net-dns-migration` unfixable by any route the case permitted. `net-dns-migration` and `net-monitoring-stack` are planning and design tasks and now assert
  false; `net-ansible-automation` and `jdm-auction-data` genuinely need the tool and now require it. A validator check enforces the invariant, proven able to fail.

### Notes

- **Tags stay a model judgement, deliberately.** Closure implements the gates' `persona_mandatory_when_tags` escalation, but the corpus carries no tags and a pattern-match over task text agrees with
  human judgement on **only 5 of 21** cases — `auth` matching "authoritative", and so on. Deriving tags from `required_personas` would have been fitting tags to the answer, so it was not done. The
  outstanding operator decision is whether to author tags per case or relax the four `required_personas` that the escalation would otherwise satisfy.
- **Six of the ten contract cases survive closure** and are the genuine ambiguities: `atar-supplier` (both production models overrule the research-vs-economics precedence rule), `jdm-portal-build`,
  `net-security-review`, `python-feature` (all three want the QA persona where a capability would do), and `release-readiness` (now resolved by `default_skill`). Four were resolved by closure alone.

## 20260901_2015

### Changed — staleness audit

- **Seven staleness defects found and fixed.** Three materially misleading: `MEMORY.md`'s baselines table still read `v3 | in flight` after v3 completed (the worst thing a designated truth document
  can do); its "what is still open" section posed the v3 question as unanswered; and `docs/routing-evaluation/gate-definitions-proposal-20260901_1600.md` still carried `Status: proposal, not applied`
  months of work after the gates were applied. Two enforcement-level: `docs/routing-evaluation/routing-failure-classification-20260901_1842.md` recommended the route invariant as the fix **after**
  that fix had been built and measured ineffective, and `ARCHITECTURE.md` described a gate model that predates the four-flag capability system. Two governance: a stale `Last reviewed` on `AGENTS.md`,
  and a long-carried open item that was simply **mis-framed** — `docs/audits/audit-agent-stack.md` is the audit *prompt*, not a duplicate report, so no supersession was ever needed.
- **Supersession banners** added in place on the two superseded documents, each naming what replaced it **and what still stands** — the capability model and corpus-derived triggers in the proposal;
  the classification itself in the failure analysis. Neither document is deleted; only their stale recommendations are fenced.
- **New governance check `check_status_markers_resolved`**, proven able to fail: no table row in `MEMORY.md` or `SCRATCHPAD.md` may report `in flight`, `pending`, `TBD` or `awaiting`. Narrow by design
  — prose may legitimately describe a past in-flight run, and `count:asat` lines are dated records. Governance 374 → 430 checks.

### Changed — coherence pass

- **Three routing-description surfaces still described the pre-capability model** and now name the four cooperating tables: `README.md` "Intelligent routing", the `routing.toml` row in
  `AI_NAVIGATION.md`, and the dispatch note in `context-map.yaml`. None was false; each was incomplete in the way that matters — a reader would not have learned that gates resolve by capability or
  that precedence ranks ownership.
- **`evals/routing-cases.toml` carried a `KNOWN CONFLICT (2026-09-01, unresolved)` note describing a contradiction this session resolved.** Rewritten to record the resolution. Comment-only: parsed
  data verified byte-identical, so no score is affected, but `eval_corpus_sha` moves `10451dc9fc71c942` → `1fff2b158a2c3909` and that is recorded in `MEMORY.md` so a v3 row stamping the older value
  still reconciles.

### Notes

- **The most important finding is unfixed, deliberately: `routing.toml` carries two contradictory persona models at once.** Seven `[[routing_rules]]` entries **require** a persona on keyword match —
  `material-independent-challenge` → `critic-munger`, `economics-gate`/`import-economics-gate` → `cfo-campbell`, `architecture-owner`/`network-technical-owner` → `cto-vogels`,
  `import-evidence-first`/`current-facts-research` → `research-thompson` — which is exactly the gate-summons-a-persona model the capability refactor replaced, while `[[gates]]` sets `persona_mandatory
  = false`. `architecture-owner` vs `implementation-owner`, and `product-experience-chain` vs `implementation-owner`, are the same conflicts `[[precedence]]` ranks, still asserted unranked. The whole
  catalogue goes into the prompt, so the model receives both. This is a live hypothesis for the ten cases failing on both production models and for Pro/Claude agreeing on only 35% of routes. Not fixed
  here because retiring or subordinating `routing_rules` changes the catalogue the frozen baselines were measured against — an operator decision, not an audit edit.
- Found in **Phase 4**, per-artifact reasoning, from `tests/test_routing_contract.py` asserting `economics-gate` exists. No grep would have found it: nothing is stale as a string, and the suite is
  green. This is the phase that a defect-string sweep structurally cannot discharge.
- **The exit gate FAILED and is reported as such.** Two residuals, both tool-vs-project mismatches: a vendored TypeScript `tsconfig.app` config is JSONC and unparseable by a strict JSON loader, and
  the inverse sweep flags 11 package-internal resource directories plus `personas/`, all of which are correctly catalogued by this project's own contract. Engineering a pass would have been the
  defect.
- The staleness-audit inverse sweep gained `manifest.yaml` as a default catalog source — a package-structured project registers every unit by path there. That removed 44 false orphans without
  weakening the check, which still found the 12 above.
- Attempting to add a README under `personas/` was **rejected by this project's own checker** — that directory contractually holds registered capabilities only. The check was right and the generic
  heuristic was wrong.

## 20260901_1900

### Added

- **Capability registry in `routing.toml`** — 20 routing capabilities, 4 gate-facing (`research`, `independent-challenge`, `validation`, `tool-execution`) and 16 supporting. Every skill and every
  persona now declares `primary_capabilities` and `supporting_capabilities`; gates name a `required_capability` and a `minimum_strength`. The hand-maintained `satisfied_by_skills` lists are gone.
  Implements steps 2-5 of [agent-stack-capability-taxonomy-and-scoring.md](../agent-stack-capability-taxonomy-and-scoring.md).
- **Strength semantics.** `primary` means the capability is one of the provider's explicit purposes and may satisfy a gate alone; `supporting` means it is incidental and never discharges a hard
  obligation. All three judged gates require `primary`. This is what protects `analysis != independent challenge`: without it, every analytical skill drifts into `independent-challenge` and the critic
  gate stops meaning anything.
- **`--rescore '<glob>'`** on `scripts/evaluate_routing.py` — re-scores plans a previous run already produced against the current catalogue, with no model calls. It holds the routes fixed, so any
  movement is attributable to the catalogue alone. Re-running the corpus cannot answer that, because the catalogue and the model's behaviour both change at once.
- **Six validator checks**, each proven able to fail by breaking the catalogue deliberately: unknown capability referenced by a skill, persona or gate; capability declared both primary and supporting;
  `tool-execution` disagreeing with a skill's `execution` class in either direction; a persona declaring `tool-execution`; a gate whose `required_capability` no provider offers at primary strength;
  and a gate still carrying a `satisfied_by_skills` list.
- `capability-strength-insufficient` is now reported separately from `gate-unsatisfied`. They call for opposite fixes — the first says the route brought something adjacent and the strength rule
  rejected it, the second says it brought nothing.

### Notes

- **The 22 unsatisfied failures were classified before any catalogue edit** —
  [docs/routing-evaluation/routing-failure-classification-20260901_1842.md](docs/routing-evaluation/routing-failure-classification-20260901_1842.md). **All 22 are ROUTING DEFECTS. Zero
  capability-mapping, zero gate-trigger, zero corpus, zero scoring.** In every case the router judged the gate correctly and then equipped the route with neither a satisfying provider nor the gate's
  persona, while the corpus lists that persona as required or preferred.
- **Predicted re-score gain was therefore zero, and the re-score confirmed it: 33/59 before, 33/59 after, no case changed verdict.** The refactor is a maintainability change — one taxonomy instead of
  two that drift — not a scoring change. It was stated as a falsifiable prediction first so that step 6 tested the classification rather than celebrating it.
- **The annotation was verified faithful before the satisfier lists were deleted**: resolving each gate through the new capability metadata reproduces its old skill list exactly — nothing gained,
  nothing lost, on all three judged gates. That is what made the deletion safe rather than hopeful.
- Two corpus-level checks were run to try to falsify the classification and failed to: no case asserts a gate its own required + preferred contract cannot satisfy (0 of 60), and no Baseline v2 plan
  names a skill absent from the catalogue (`team` looked like a hallucination and is a real entry).
- **What actually moves the 22 is still unbuilt:** gate satisfaction is advice, not an invariant. A true gate with no primary provider and no gate persona should be an invalid route the router must
  repair before returning it.

## 20260901_1730

### Changed

- **`persona_mandatory` resolved in favour of capability-first.** `critic-gate` dropped from `persona_mandatory = true` to `false` with escalation tags (`high-consequence`, `irreversible`,
  `security-sensitive`, `thin-evidence-high-commitment`); `qa-gate` gained `production-change`. No gate is unconditionally mandatory any more. The obligation must be satisfied; a persona is not the
  only way to satisfy it.
- **The scorer no longer penalises a direct-skill route for naming an owner.** The `direct-skill case unnecessarily selected persona` hard failure is removed: a direct route's real contract is right
  skill / no forbidden persona / no team, and all three were already hard-scored. It punished one accountable owner as harshly as a four-persona committee — the opposite of what the
  `direct-adversarial` family measures.
- **Gate satisfaction is now explicitly skill-first** in both the orchestrator and the eval prompt, as an ordered four-step rule: a skill already selected satisfies it → add the narrowest satisfying
  skill → add the persona only where independence is the deliverable → never add a persona because it is the gate's `default_persona`.

### Added

- **`[[precedence]]` in `routing.toml`** — four ownership tie-breaks, each naming the discriminating question and both answers, replacing inference from overlapping `owns` prose:
  product-vs-implementation, artefact-vs-domain-review, component-cannot-architect-itself, research-vs-economics. Mirrored as a table in `skills/skill-agent-stack/SKILL.md` Step 3.
- **Structural validation of precedence rules** in `scripts/validate_agent_stack.py`: both branches must resolve to real and *different* personas, ids must be unique, and all four prose fields must be
  present. Proven able to fail by pointing both branches of `research-vs-economics` at the same persona.

### Results — Baseline v2

- **33/60 (55.0%), mean 81.6**, all 60 cases, Hermes/DeepSeek `deepseek-v4-flash`, against v1's 28/60 (46.7%) mean 80.6 (76.4 was the earlier 23/60 run, not this one). Per family, v2 vs v1:
  direct-adversarial 5/7 vs 3/7 · business-research 6/8 vs 6/8 · jdm-import 6/12 vs 6/12 · networking-infrastructure 6/15 vs 4/15 · atar-import 5/8 vs 4/8 · software-ai-engineering 5/10 vs 5/10.
- **Failure classes moved where the changes were aimed.** `wrong-owner` 6 → 3, `missing-gate` 43 → 3, team inflation 3 → 1, forbidden persona/skill 0, runtime prerequisite failures 0. The three cases
  the new rules target all resolved to the corpus owner: `network-code-review` PASS 90.0 to `fullstack-dhh`, `jdm-portal-build` correctly to `product-norman` (now failing only on a thin team),
  `agent-routing-design` no longer failing on ownership at all.
- **Removing the direct-skill persona penalty did not let committees through.** `direct-adversarial` went 3/7 → 5/7 with zero team-inflation and zero forbidden-persona failures, and
  `network-change-premortem` still fails on `team inflation: 2>1` — the genuine defect fires, the duplicate no longer does.
- **`unsatisfied` barely moved: 24 → 22, now 22 of 39 hard failures, and the root-cause split is the finding.** 15 of 22 are *skills selected but none satisfy*; only 5 are *no skills at all*. The
  router is not omitting capability — it picks skills that are not on the gate's `satisfied_by_skills` list. `critic_required` alone accounts for 11. A must-select invariant would fix the 5 and miss
  the 15; the next fix belongs in `routing.toml` visibility.
- **Run defect, recorded because it nearly shipped as a baseline.** The first pass used `--limit 10` per family and so covered 53 of 60 — `networking-infrastructure` has 15 cases and `jdm-import` has
  12. The 7 omitted included `network-code-review`, `jdm-portal-build` and `network-change-premortem`, the three cases that test this session's changes most directly. They were run separately against
the unchanged frozen set and merged.
- One row is not a routing result: `ui-only` scored 0.0 with `execution-error: no routing JSON object found in command output`, a model-side parse failure worth about 1.4 points of overall mean.

### Added

- **`scripts/analyze_routing_results.py`** and `just routing-matrix` — the failure matrix used to read Baseline v2, promoted out of scratch so the next baseline is analysed the same way. Family x
  failure class, plus the root-cause split that distinguishes a gate unsatisfied because the route selected **no** skills from one unsatisfied because it selected skills absent from that gate's
  `satisfied_by_skills` list. Stdlib-only, read-only, cataloged in `scripts/README.md`. `ROUTING_RESULTS='<glob>' just routing-matrix` analyses any other run — v1 reads back as 28/60 (46.7%) mean
  80.6.
- It prints coverage against the corpus (`corpus has 60 cases; N not present`), which is the line that would have caught the `--limit` truncation instead of leaving a 53-case run looking complete.

### Renamed

- **`attar` → `atar` throughout**, on operator instruction: the `atar-import` family, its 8 case ids, all task prose, 12 authored files, the generated context pack, and — also on instruction — the
  historical CHANGELOG and SCRATCHPAD entries and the v1/v2 result files, both their names and their row contents.
- **Provenance consequence, recorded rather than hidden.** Baseline v2 ran against the pre-rename corpus. Renamed result rows now carry `atar-*` case ids beside an `eval_corpus_sha` that stamps the
  corpus as it was at run time, so the two disagree by design. Frozen set at run time: routing `ed2408a5d8e36cd4` · corpus `3b936cd190b41218` · orchestrator `dd84864e3df0cb30` · harness
  `f692b8966db9efe1`. After the rename: routing `ea01bf2c24054ad0` · corpus `10451dc9fc71c942` · orchestrator `297fa237fe91e291` · harness unchanged. Reconcile a v2 row through this pair.

### Notes

- **A draft of `artefact-vs-domain-review` contradicted the corpus in two cases and was caught before it shipped.** Written as "code quality, correctness, maintainability *or security* → Full-Stack",
  it took ownership of `security-code-scan` and `net-security-review` away from `cto-vogels`, which the corpus assigns to CTO. The rule now splits on the deliverable: code quality is Full-Stack's;
  security *posture* is architecture and stays with CTO however code-shaped the artefact. This is why the corpus is cross-checked against a new rule before a run, not after.
- The run in flight when that contradiction was found was **killed rather than allowed to finish**. Its `routing_catalogue_sha` would have described a catalogue that was about to change, and a
  provenance stamp that needs an argument to defend is not doing its job.

## 20260901_1600

### Added

- First complete behavioural routing baseline — all 60 corpus cases against Hermes/DeepSeek: **23/60 (38.3%), mean 76.4**. Results (6 files, 60 rows) in
  `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/routing-results/`, which is working-cache and rebuildable; the repo carries the findings, not the result sets.
- `docs/routing-evaluation/gate-definitions-proposal-20260901_1600.md` — proposed `[[gates]]` definitions for the four flags, with triggers **derived from the corpus** rather than invented, the two
  `scripts/evaluate_routing.py` prompt fixes, expected effect, and four open policy questions. **Nothing applied** — the trigger conditions encode policy and need an operator call.

### Notes

- Generated by `skill-ai-it` in `refresh` mode; gate green at 360 checks. <!-- count:asat -->
- **The headline pass rate mostly measures the specification gap, not routing quality.** Of 62 hard failures, 43 are gate-flag misses against flags `routing.toml` never defines; excluding them, 45/60
  (75%) would pass. The 19 remaining are genuine: 10 missing-required-persona, 6 wrong-primary-owner, 3 team-inflation on direct-skill cases.
- Per family, pass / mean / gate / non-gate: business-research 6/8 88.4 (2/0) · direct-adversarial 3/7 82.1 (3/2) · atar-import 3/8 78.1 (6/2) · software-ai-engineering 3/10 75.0 (7/4) ·
  networking-infrastructure 4/15 71.7 (15/5) · jdm-import 4/12 71.1 (10/6). `business-research` has zero genuine routing errors; the real ones cluster where persona ownership overlaps.
- **Baseline validity checked, not assumed.** The operator's internet dropped mid-session. Hermes' fallback chain is `deepseek-v4-flash` → `qwen3.5:35b` (local), and `qwen3.5` appears zero times in
  Hermes logs across 13:00–15:30, so the fallback never fired and all 60 came from DeepSeek. The outage killed only the first `jdm-import` attempt, which produced no results and was re-run cleanly.
- **Harness gap found:** result rows carry no model/provider field, so a silent fallback would contaminate a baseline undetectably. Recorded as an open item; stamp model+provider per row before the
  next run.
- **Operational lesson:** a foreground Bash tool timeout does not kill the process. The first `jdm-import` run kept running 58 minutes after its call "timed out" and competed with a later background
  run on the same family. Long foreground work needs an explicit `pkill` after a timeout.

## Contents

- [20260904_1630 — Provenance detail section added to the phased implementation plan, at operator request](#20260904_1630-provenance-detail-section-added-to-the-phased-implementation-plan-at-operator-request)
- [20260904_1230 — Scoped staleness re-audit: two path defects fixed, prior 20260903_2200 register re-verified](#20260904_1230-scoped-staleness-re-audit-two-path-defects-fixed-prior-20260903_2200-register-re-verified)
- [20260904_1208 — Phased implementation and self-verification plan added, inert pending an operator-named trigger](#20260904_1208-phased-implementation-and-self-verification-plan-added-inert-pending-an-operator-named-trigger)
- [20260904_1155 — Sentry Skills / Prompt Optimizer row upgraded from recommendation to adopted record](#20260904_1155-sentry-skills-prompt-optimizer-row-upgraded-from-recommendation-to-adopted-record)
- [20260904_1150 — Six proposed archcore documents accepted by the operator](#20260904_1150-six-proposed-archcore-documents-accepted-by-the-operator)
- [20260904_1145 — Rule 0013 proposed: adapt Sentry's prompt-optimizer removal method to the frozen corpus; Mem0 row corrected](#20260904_1145-rule-0013-proposed-adapt-sentrys-prompt-optimizer-removal-method-to-the-frozen-corpus-mem0-row-corrected)
- [20260904_0833 — Token Optimizer installed for Claude Code and Codex; a real content-loss bug found and fixed](#20260904_0833-token-optimizer-installed-for-claude-code-and-codex-a-real-content-loss-bug-found-and-fixed)
- [20260904_0751 — token-optimization guide added and source-verified](#20260904_0751-token-optimization-guide-added-and-source-verified)
- [20260904_0737 — docs/ reorganized into subfolders](#20260904_0737-docs-reorganized-into-subfolders)
- [20260903_2230 — staleness audit](#20260903_2230-staleness-audit)
- [20260903_2130](#20260903_2130)
- [20260903_2126 — vertical-agent framework fact-check](#20260903_2126-vertical-agent-framework-fact-check)
- [20260903_2000](#20260903_2000)
- [20260903_1943 — reliability adaptation proposal](#20260903_1943-reliability-adaptation-proposal)
- [20260903_1849 — external orchestrator and skill-library survey](#20260903_1849-external-orchestrator-and-skill-library-survey)
- [20260903_1900](#20260903_1900)
- [20260903_1830](#20260903_1830)
- [20260903_1600](#20260903_1600)
- [20260903_1400](#20260903_1400)
- [20260903_0330](#20260903_0330)
- [20260903_0230](#20260903_0230)
- [20260903_0200](#20260903_0200)
- [20260903_0030](#20260903_0030)
- [20260902_1240](#20260902_1240)
- [20260902_1215](#20260902_1215)
- [20260902_1140](#20260902_1140)
- [20260902_1015](#20260902_1015)
- [20260902_0950](#20260902_0950)
- [20260902_0935](#20260902_0935)
- [20260902_0300](#20260902_0300)
- [20260902_0245](#20260902_0245)
- [20260902_0130](#20260902_0130)
- [20260902_0015](#20260902_0015)
- [20260901_2130](#20260901_2130)
- [20260901_2015](#20260901_2015)
- [20260901_1900](#20260901_1900)
- [20260901_1730](#20260901_1730)
- [20260901_1600](#20260901_1600)
- [20260901_1420](#20260901_1420)
- [20260901_1315](#20260901_1315)
- [20260901_1240](#20260901_1240)

---

## 20260901_1420

### Added

- `scripts/eval_model_adapter.py` — stdlib-only adapter bridging `scripts/evaluate_routing.py` to any OpenAI-compatible `/chat/completions` endpoint. The evaluator can only run shell commands, so an
  HTTP model needed an adapter. Written as a **protocol** adapter rather than a provider one, so `ROUTING_EVALS.md`'s "no hard-coded provider syntax" rule still holds: local Ollama, a LiteLLM gateway,
  and cloud APIs differ only by `EVAL_BASE_URL` / `EVAL_MODEL`. Strips `<think>` blocks, because reasoning models emit scratchpad containing draft JSON that the evaluator's extractor would otherwise
  pick up.
- `just` recipes: `routing-eval-ping` (connectivity check before spending a corpus run), `routing-eval-local`, `routing-eval-remote`, and `routing-eval-hermes` (routes through the Hermes runtime,
  which already carries its own DeepSeek provider and key — `hermes -z` prints only the final response, matching the evaluator's contract).
- `scripts/README.md` — cataloged the adapter and all five new recipes with safety labels.

### Changed

- `justfile` — replaced deprecated `env_var_or_default` with `env`, and documented the `$(cat)` quoting trap on the generic `routing-eval` recipe: because `{{command}}` interpolates inside double
  quotes, a stdin-to-argument bridge is expanded by the recipe's shell instead of the evaluator's and the CLI receives an empty prompt. The purpose-built wrappers avoid it by single-quoting.

### Notes

- Generated by `skill-ai-it` in `refresh` mode; gate green at 357 checks. <!-- count:asat -->
- **Behavioural finding, now recorded in `SCRATCHPAD.md`:** across three routes (Claude Code 96.7/80.0, Hermes-DeepSeek 80.0/80.0, local `deepseek-r1:14b` 60.0/60.0) no model set the routing gate
  flags reliably, and the strongest still missed `critic_required` on an architecture decision. A failure surviving three very different models points at the gate definitions in `routing.toml` or the
  orchestrator prompt, not at model capability.
- Only 2 of the 60 cases have been run on any model; these are smoke results, not a baseline.

## 20260901_1315

### Added

- Applied the routing-evals delta update (`/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack-update`, 50 files verified). New: `ROUTING_EVALS.md`, `scripts/evaluate_routing.py`,
  `tests/test_routing_behavior.py`, and the `routing-eval-check` / `routing-eval` / `routing-eval-smoke` tasks. `evals/routing-cases.toml` expanded from 6 representative cases to 60 real-workload
  cases across six families (`networking-infrastructure`, `software-ai-engineering`, `jdm-import`, `atar-import`, `business-research`, `direct-adversarial`); `routing.toml` gained network,
  infrastructure, import-evidence, import-economics, supply-chain, current-fact and regulatory-research intents and gates.
- `scripts/README.md` — cataloged `scripts/evaluate_routing.py` with safety labels. The coverage check caught the new script and failed the gate until it was cataloged, which is the intended workflow.

### Changed

- **Interpreter resolution made explicit.** The `justfile` now defines `py := <working-cache venv>/bin/python` and every Python recipe addresses `{{py}}` by path and depends on `_require-venv`;
  `.mise.toml` tasks carry the absolute venv path too, so the two entrypoints cannot resolve differently. Previously every recipe used `mise exec -- python`, which *did* resolve to the venv — but only
  implicitly, via `_.python.venv` activation. That form hides the dependency at the call site and degrades silently to the host interpreter if activation stops applying; it also made the in-repo venv
  violation invisible at every call site while it existed.
- `scripts/check_governance.py` — `check_no_bare_interpreter` replaced by `check_interpreter_pinning`, which now also fails an implicit `mise exec -- python`. Proven to fail by deliberate breakage.
  `ROUTING_EVALS.md` and `ARCHITECTURE.md` added to `SURFACES`.
- Re-applied after the update overwrote them: the venv path in `.mise.toml`, the governance recipes and pointers in `justfile` and `README.md`, and the `skills/` path prefix in `SKILL_STANDARD.md` and
  `REVISION_NOTES.md`.
- `AI_NAVIGATION.md`, `context-map.yaml`, `ARCHITECTURE.md`, `repomix.config.json` — routed for the new routing-eval surface.

### Notes

- Generated by `skill-ai-it` in `refresh` mode.
- The update package's base was the ORIGINAL `agent-stack.zip`, so it validated 10 files as diverged and refused to apply. Run with `--force` on explicit operator approval, taking the newer library
  content and re-applying the governance deltas on top. Update backups: `.agent-stack-update-backups/20260901_130323/`; pre-update copies of the five files I had modified:
  `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/_pre-update-mine-20260901/`.
- The lesson above was promoted into the canonical skill: `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it` gained the implicit-resolution rule in `SKILL.md` (runtime isolation
  section, conventions, and quality checklist), in that skill's `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/templates/justfile` RUNTIME PINNING header, and as a new Tier 2
  `check_interpreter_pinning` in its `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/templates/check_governance.py`, so every future bootstrapped project inherits the rule.
  Both template paths are relative to the skill package directory named above, not to this repo.
- Verified: `just preflight` green — interpreter resolving to the working-cache venv (3.14.5), contract validation PASS (52 capabilities; 15 personas; 37 skills), 334 governance checks PASS, routing
  corpus PASS (60 cases), 37 unit tests PASS. The suite grew from 32 to 37 with the update's routing-behaviour tests. <!-- count:asat -->


## 20260901_1240

### Added

- Initial governance scaffold: `AGENTS.md`, `CLAUDE.md`, `SCRATCHPAD.md`, `CHANGELOG.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `ARCHITECTURE.md`, `scripts/README.md`, `repomix.config.json`.
- `scripts/check_governance.py` — stdlib-only governance coherence gate, wired into `just governance` and `just preflight`. Six project-specific Tier 3 checks beyond the universal set:
  - `check_manifest_paths_exist` — every `manifest.yaml` capability path resolves.
  - `check_manifest_covers_library` — nothing in `personas/` or `skills/` is missing from the manifest (the orphan direction).
  - `check_package_skills_have_skill_md` — every `package` capability carries a `SKILL.md`, per `SKILL_STANDARD.md`.
  - `check_library_counts` — prose counts of skills and capabilities match the manifest.
  - `check_venv_outside_repo` — regression guard for the venv placement rule below.
  - `check_no_bare_interpreter` — no `justfile` recipe calls a bare `python`/`node`.
- `just` recipes: `governance`, `runtimes`, `preflight`, `context-pack`, `audit-scripts`.

### Changed

- `.mise.toml` — maintenance venv moved from `.venv` (inside the repo) to `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/venv`. Required by the venv placement rule in
  [../../AGENTS.md](../../AGENTS.md) rule (2026-04-23), which forbids a venv inside `skills_stuff/<skill>/`. The in-repo venv was hidden by `.gitignore`, so it was invisible to `git status` and to
  every existing check; the new `check_venv_outside_repo` assertion is what makes the rule observable.
- `SKILL_STANDARD.md`, `REVISION_NOTES.md` — corrected two references to `skills/skill-creator/scripts/quick_validate.py` that dropped the `skills/` path prefix and therefore resolved to nothing.
- `README.md` — added a Governance pointers section and validation-command update.

- Initialized `.archcore/` (settings only — no content documents written) and emitted `ARCHCORE_PROMOTION_CANDIDATES.md` listing 22 candidates across adr/rules/specs/guides/plans, plus a *never
  promote* table. Run `/skill-ai-it promote` to authorize writing Archcore content.

### Notes

- Generated by `skill-ai-it` in `bootstrap` mode.
- Verified at time of writing: 32 unit tests PASS; `scripts/validate_agent_stack.py` PASS (52 capabilities; 15 personas; 37 skills); `scripts/check_governance.py` PASS. <!-- count:asat -->
- Audit findings A1 (non-atomic sync apply) and A2 (symlink escape in sync) remain open and are tracked in `SCRATCHPAD.md`. This run did not touch the sync transaction model.
