# SCRATCHPAD

Agent working memory for skills_stuff. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-04-22 from mcp-project-context (no memory-keeper entries found for channel) -->

## Contents

- [Current state](#current-state)
- [Open items](#open-items)
- [Key anchors](#key-anchors)
- [Recent decisions](#recent-decisions)
- [Session history (summaries — full detail in memory-keeper)](#session-history-summaries--full-detail-in-memory-keeper)
- [Next actions](#next-actions)
- [Memory pointers (navigation only — content is above)](#memory-pointers-navigation-only--content-is-above)

---

## Current state

**Phase:** Active maintenance — skill authoring and governance updates. <!-- KEEP -->

2026-09-01 update: Agent Stack is live at `/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack` with 52 capabilities / 37 packages, an on-demand Orchestrator, and 123 verified global
symlinks (15 Claude personas plus 36 skills each for Claude, Codex, and compatible `.agents` clients). `skill-slurp-chat` and `skill-project-coherence` are deliberately not part of Agent Stack; their
pre-existing standalone installs remain separate. <!-- KEEP -->

2026-06-19 update: eight Codex skills were installed with symlinks from `~/.codex/skills/` to canonical source folders under `skills_stuff/skills/`: `agent-watchdog`, `plan-arbiter`, `plow-ahead`,
`quick-recap`, `read-the-damn-docs`, `stay-within-limits`, `visual-plan`, and `visual-recap`. The `skills_stuff` mcp-project-context project exists as UUID `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c`; use
the UUID for writes/checkpoints when display-name lookup fails. <!-- KEEP -->

2026-08-10 update: `skill-anydoc` (documents → GFM Markdown) is built, installed to all three agents, and renamed from `anydoc` to the `skill-*` house convention. Install policy is now explicit —
symlink to canonical, never copy — and a backlog of copy-installed skills awaiting conversion is tracked under Open items. <!-- KEEP -->

skills_stuff is the canonical authoring source for Claude Code and Codex skills. Recent work: `skill-project-wiki-rag-bridge` created 2026-05-24 — a reusable multi-project bridge skill for connecting
project repos to the shared wiki and Qdrant RAG tooling with strict isolation. 48 files: SKILL.md, README, CHANGELOG, 14 templates, 10 numbered prompts, 4 schemas, 6 checklists, 7 docs, 2 example
projects (Vocus + generic). Skill registered in skills_stuff README under new "Reusable Skills — skills/" section. `_wiki/CLAUDE.md` governance wrapper created.

RAG tools infrastructure also fully operational as of 2026-05-24: Qdrant on OrbStack (localhost:6333), venv at `tools-working-cache/rag-tools/.venv`, 33 tests passing, local 384-dim embeddings
(all-MiniLM-L6-v2) confirmed.

Auto-memory consolidated: all Claude auto-memory writes go to `/Volumes/Data/_ai/claude-auto-memory/` (governed, single path, 36 files + MEMORY.md). Per-project fragmentation eliminated.

---

## Open items

- [x] **Build `skill-walk-before-run`** — done 2026-09-16. Package at `skills/skill-walk-before-run/` (SKILL.md, README.md, CHANGELOG.md, BRIEF.md — the brief moved here from `pending_skills/` as the
  colocated provenance record). Symlinked into `~/.claude/skills` and `~/.codex/skills`. Invocation is `/skill-walk-before-run` (alias `/skill-wbr`).
- [ ] **Run the `skill-walk-before-run` acceptance tests, then the three-project trial** (cambium-swap plus two not-yet-chosen fresh projects, manual invocation only — no hook, no AGENTS.md trigger,
  for any of the three). Detail in memory-keeper channel `wbr`, key `wbr.task.acceptance-tests-then-trial`.

- [ ] **Run `skill-staleness-audit` end-to-end on a project other than its originating one.** It has been unit-tested across four repos but never driven through all nine phases elsewhere.
  `apn/vocus-profitability` is the obvious first target — 932 files, 240 novel lines in its managed blocks, never swept. `KEEP`

- [ ] Convert remaining copy-installed skills to symlinks — Tier 1 (canonical source exists): `skill-commtracker`, `skill-project-coherence`, `skill-project-wiki-rag-bridge`, `skill-slurp-chat`,
  `skill-ifa`, `skill-ai-it`, `skill-smc`, `caveman`, `graphify`. Awaiting operator go-ahead. <!-- KEEP -->
- [ ] Tier 2 copies have no canonical `skills_stuff` source — needs an authoring decision, not just a link: `telco-financial-analysis`, `open-knowledge-*`, `co-design`, `parallel-task*`,
  `super-swarm*`, `swarm-planner`, `skill-creator`, `skill-installer`, `skill-mx02-migration`, plus the vendored set living only in `~/.codex/skills`. <!-- KEEP -->
- [ ] Re-point two-hop `~/.claude/skills/<skill>` → `~/.codex/skills/<skill>` links at canonical where one exists; for `doc`, `pdf`, `slides`, `spreadsheet`, `imagegen`, `screenshot` the codex dir is
  currently de-facto canonical. <!-- KEEP -->
- [ ] Verify skill-anydoc against the untested formats: `.pptx`, `.ppt`, `.epub`, `.rtf`, legacy `.doc`, ODF. <!-- KEEP -->
- [ ] Broader `~/.codex/skills` vs `~/.agents/skills` authority decision (from strategy-os governance session)
- [ ] sync-script rollback hardening (from strategy-os governance session)

---

## Key anchors

| Item                      | Detail                                                                                                                                                                   |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Authoring root            | `/Volumes/Data/_ai/_skills/skills_stuff/`                                                                                                                                |
| Installed skills (Claude) | `~/.claude/skills/`                                                                                                                                                      |
| Installed skills (Codex)  | `~/.codex/skills/` or `~/.agents/skills/`                                                                                                                                |
| Specialists dir           | `specialists/` — canonical authoring for specialist skills                                                                                                               |
| Exports dir               | `exports/` — client adapter layer                                                                                                                                        |
| skills.md                 | Skill index/registry                                                                                                                                                     |
| Swarms install            | `skills_stuff/swarms/swarms-github/` (7 skills; avoid parallel-task-tmux — Snyk Critical Risk)                                                                           |
| Installed skills (Hermes) | `~/.hermes/skills/domain/` <!-- KEEP -->                                                                                                                                 |
| Install form              | Symlink, never copy. Directory symlink by default; file symlink (`SKILL.md` only) when the canonical folder carries extra payload. Rule in `AGENTS.md` Regular Skills    |
|                           |   section. <!-- KEEP -->                                                                                                                                                 |
| Copy-install audit        | Skip when `[ -L "$dir" ]` **or** `[ -L "$dir/SKILL.md" ]` — testing the file alone misreports every directory-linked skill as a copy. <!-- KEEP -->                      |
| Genuine                   | claude 17, codex 25, hermes 3 <!-- KEEP -->                                                                                                                              |
|   copies (2026-08-10)     |                                                                                                                                                                          |
| skill-anydoc              | Canonical `skills/skill-anydoc/`; runtime `skills-working-cache/anydoc/` (npm `@firecrawl/anydoc` 0.1.7, `.mise.toml` node 26); launcher                                 |
|                           |   `skills/skill-anydoc/bin/anydoc`. Invoked as `/skill-anydoc` — renamed from `anydoc` 2026-08-10. <!-- KEEP -->                                                         |
| `~/_ai`                   | Symlink to `/Volumes/Data/_ai/` — home-path links in skill installs resolve correctly <!-- KEEP -->                                                                      |
| `skills_stuff/AGENTS.md`  | Listed in `.git/info/exclude:9` — edits never show in `git status` <!-- KEEP -->                                                                                         |
| `skill-walk-before-run`   | `skills/skill-walk-before-run/ledger.jsonl` — JSONL, one object/line, not yet created (first write pending). Field                                                       |
|   ledger                  |   reference: `skills/skill-walk-before-run/schemas/ledger-entry.md`.                                                                                                     |

---

## Recent decisions

- 2026-09-16 — `skill-walk-before-run` v0.1.1 hardened same-session: default targeting to the calling project, project write-back (mirror + SCRATCHPAD pointer), a naming rule for the `project` field
  (mcp-project-context name else leaf dirname, never git top-level — tested against real data, `apn`/`me` collide), and a ledger-check before re-deriving. Then four follow-up operator questions each
  caught a real bug in that same-session work: stale REDs never auto-resolving, no two-way sync needed (rejected, documented a manual recovery procedure instead), a deleted mirror losing history on
  next write, and a sequencing bug where the ledger-check ran before Step 0 named the current assumption. All fixed same day. `SKILL.md` now 128 lines (from a 60-100 target); `/skill-wbr` alias also
  fixed (was never registered, added to `~/.claude/CLAUDE.md`'s alias-block pattern). Full detail: memory-keeper channel `wbr`.
- 2026-09-16 — `skill-walk-before-run`: fact-checked and pushed back on a ChatGPT comparison against `github.com/Teycir/Assumptions` (verified real via `gh api`). Rejected adopting its two suggested
  additions (OBSERVED/INFERRED/UNKNOWN evidence vocabulary; Step 0 as an explicit chain diagram) now — both judged redundant with WBR's existing RED/AMBER/GREEN/UNKNOWN-signal + reality-contact model,
  and adopting either pre-trial would itself be the design-round pattern BRIEF.md prohibits before the trial. Parked all four resulting candidates (the two above, plus two self-generated ones — Output
  scope-limitation, ledger evidence-locator) in BRIEF.md's existing "Parked for v0.2" list rather than creating a new `roadmap.md`, matching that file's own precedent for refusing duplicate design
  docs. Not yet committed to git. Full detail: memory-keeper channel `wbr`.
- 2026-09-16 — `skill-walk-before-run` ledger format hardened pre-first-write (zero ledger entries existed): colon-delimited text (`ledger.md`) → one-JSON-object-per-line (`ledger.jsonl`), with `ts`
  (ISO 8601, local UTC offset) and `branch` (git branch at invocation) fields added. JSONL chosen over TOML for append-only single-writer log semantics and per-line failure isolation. New file
  `schemas/ledger-entry.md` holds the field reference — the brief's own earn-in trigger for that file fired for real. Recorded as BRIEF.md open decision #5, explicitly reconciled against the brief's
  "no fields mid-experiment" caution (judged pre-first-write, not mid-trial churn). Not yet committed to git. Full detail: memory-keeper channel `wbr`.
- 2026-09-16 — `skill-walk-before-run` v0.1 built and shipped: package at `skills/skill-walk-before-run/` is SKILL.md (88 lines) + README.md + CHANGELOG.md + BRIEF.md, symlinked into
  `~/.claude/skills` and `~/.codex/skills`. Built by hand rather than via `skill-creator`'s own instructions, which turned out to be the generic Codex-flavoured convention (`$CODEX_HOME`,
  `init_skill.py`, `agents/openai.yaml`) and contradict this repo's actual pattern.
- 2026-09-16 — Ledger path changed from the brief's original `skills-data/skill-walk-before-run/ledger.md` proposal to colocated `skill-walk-before-run/ledger.md` (operator instruction). Kept tracked
  in git, not gitignored — operator's call: "this is my personal skill and I can put my data in that." No revisit trigger; this is the final state, not a placeholder pending a decision.
- 2026-09-16 — Brief relocated from `pending_skills/skill-walk-before-run-brief-20260916_1303.md` to `skill-walk-before-run/BRIEF.md` (operator instruction), resolving the brief's own open decision
  #4. Renamed to the stable ALL-CAPS convention since it is now a permanent colocated reference, not a pending-review doc. Invocation command also renamed mid-build: `/walk-before-run` →
  `/skill-walk-before-run` (alias `/skill-wbr` unchanged).
- 2026-09-16 — `skill-walk-before-run` brief frozen at v0.1 after five review rounds, and deliberately kept small: three-file package (SKILL.md 60-100 lines, README, CHANGELOG), no
  scripts/evals/references/schemas until each earns in. Trial is manual-invocation-only across three projects so the experiment measures one intervention. Full detail in memory-keeper channel `wbr`.
- 2026-09-01 — Agent Stack remains at 52 capabilities / 37 packages; the operator explicitly excluded `skill-slurp-chat` and `skill-project-coherence` after a brief addition/revert. Orchestrator is
  the normal single entry point and selects specialists internally. <!-- KEEP -->
- 2026-08-10 — Skill installs are symlinks, never copies (operator instruction). Directory symlink is the default and matches the ~60 existing linked installs; file symlink (`SKILL.md` only) is the
  exception when the canonical folder carries payload agents should not see. `skill-anydoc` is the sole file-symlink case — its folder holds `anydoc-github/` and `bin/anydoc`. Written into `AGENTS.md`
  Regular Skills and `claude-auto-memory/feedback_symlink_skill_installs.md`. <!-- KEEP -->
- 2026-08-10 — `anydoc` renamed to `skill-anydoc` to match the house convention, but the command name (`bin/anydoc`) and the runtime cache dir (`skills-working-cache/anydoc/`) deliberately keep the
  old name — that directory is the npm package install, not the skill, so renaming it would misrepresent its contents. Both exceptions documented in `SKILL.md` so they do not read as an oversight.
  <!-- KEEP -->
- 2026-08-10 — no nested YAML in markdown frontmatter in this repo: the 200-col rewrap hook treats frontmatter as prose and flattens a nested block into one unparseable line, which breaks skill
  loading silently. Flat `key: value` only, and parse-check with `yaml.safe_load` after any hook-touched frontmatter edit. <!-- KEEP -->
- 2026-08-10 — skill-anydoc runtime installed from npm, not built from source: the Rust workspace has no `[[bin]]` target (CLI is `node/cli.js` over a napi-rs binding), so `npm install` into
  `skills-working-cache/anydoc/` was the correct path. A fixed launcher decouples the SKILL.md contract from the runtime, so npm upgrades touch no skill files. <!-- KEEP -->
- 2026-06-19 — Codex skill install method: installed `agent-watchdog`, `plan-arbiter`, `plow-ahead`, `quick-recap`, `read-the-damn-docs`, `stay-within-limits`, `visual-plan`, and `visual-recap` into
  `~/.codex/skills` as symlinks to canonical source folders, not copied directories.
- 2026-06-19 — mcp-project-context write target: `skills_stuff` already existed; use UUID `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c` for notes/checkpoints when display-name lookup fails.
- 2026-05-24 — skill-project-wiki-rag-bridge: created as reusable multi-project bridge (not Vocus-specific); flat validator keys at top of retrieval-policy.yaml for rag-tools CLI compatibility;
  `default_index: false` enforced in project-documents.yaml; collection naming `rag__project_<slug>` / `rag__wiki_<domain>` / `rag__test_<purpose>_<date>`; forbidden: 9 global patterns; authority
  order: project-local > wiki markdown > Qdrant > generated > nav YAML.
- 2026-05-24 — wiki governance: created `_wiki/CLAUDE.md` thin wrapper (`@AGENTS.md`) to fix missing governance entrypoint for the wiki vault.
- 2026-05-22 — auto-memory coherence: merged 3 governance-scan files into 1 (`feedback_governance_scan.md`); normalized frontmatter on 7 files (flat `type:` not `metadata:` nesting); renamed
  `claude_md_thin_wrapper.md` → `feedback_claude_md_thin_wrapper.md`; MEMORY.md rebuilt alphabetically (36 entries, 0 broken links, 0 duplicate name fields).
- 2026-05-22 — auto-memory relocation: `autoMemoryDirectory` → `/Volumes/Data/_ai/claude-auto-memory/`; `cleanupPeriodDays: 36500` (0 schema-rejected); CLAUDE.md governance rule added
  (capture-cache-only); 37 files migrated from per-project dirs, old files deleted.
- 2026-04-28 — graphify MCP: use uv-tool isolated Python 3.10 env (not a new venv) since graphifyy[mcp] already installed; Python 3.14 excluded by graphify's `<3.14` constraint.
- 2026-04-22 — commtracker scripts: slug uses email's own TZ (not forced AEST); reconcile tries AEST fallback for historical tracker compatibility. Scripts live at `~/.agents/scripts/commtracker/`.
- 2026-04-22 — skill-commtracker: Step 4.5 added for MIME attachment/inline image extraction; signature detection (Outlook-*.png, UUID-named, ≤200b) skips chrome by default.
- 2026-04-22 — skill-slurp-chat Step 6.5 added: slurp now updates SCRATCHPAD.md after checkpointing both backends. Tiered ownership enforced.
- 2026-04-22 — skill-ai-it created: content-aware governance bootstrap. Queries memory systems before writing SCRATCHPAD (not blank). Conditional files: ARCHITECTURE, CONVENTIONS, ROADMAP based on
  project signals.
- 2026-04-22 — SCRATCHPAD generation in skill-ai-it queries all 3 memory sources; session summaries 2-3 bullets only in SCRATCHPAD; full detail stays in memory-keeper.

---

## Session history (summaries — full detail in memory-keeper)

### 2026-09-16 (continued IV) — `skill-walk-before-run` v0.1.1: trial-driven hardening, then four self-caught bugs
- Ran all 3 trial projects for real (cambium-swap, jdm, atar — all RED). Operator overrode earlier pushback and directed default project-targeting plus project write-back; fixed the never-registered
  `/skill-wbr` alias; investigated and fixed the `project` field naming rule (git-toplevel collides in this workspace's monorepos); backfilled mirrors/pointers into all 3 target projects' own repos.
- Operator then asked four "what if" design questions in sequence, each exposing a real bug in the work just shipped: stale REDs never auto-resolving to RESOLVED, whether mirrors need two-way sync
  (rejected, recovery procedure documented instead), a deleted mirror silently losing history, and a sequencing bug where the ledger-check ran before Step 0 could name the current assumption. Fixed
  all four same session.
- `SKILL.md` grew from 89 to 128 lines across the session; each step documented in BRIEF.md's numbered open-decisions list (now #1–#12) rather than left implicit.
- Evidence basis: memory-keeper channel `wbr`, 11 new keys across 3 slurps this session. Checkpoints: `slurp-20260916-wbr-ledger-jsonl`, `slurp-20260916-wbr-teycir-review-parked`,
  `slurp-20260916-wbr-v011-hardening`.

### 2026-09-16 (continued III) — `skill-walk-before-run` Teycir/Assumptions comparison reviewed, candidates parked
- Operator had ChatGPT compare skill-walk-before-run against `github.com/Teycir/Assumptions` and recommend two adoptions. Fact-checked the repo via `gh api` first (confirmed real, every specific
  mechanism cited genuinely present) before opining.
- Agreed with ChatGPT's long reject list; pushed back on both its "adopt" recommendations as redundant with WBR's existing RED/AMBER/GREEN/UNKNOWN-signal + reality-contact model, and as themselves an
  instance of the pre-trial design-round pattern BRIEF.md prohibits.
- Operator asked where to file the resulting candidate ideas: decided BRIEF.md's existing "Parked for v0.2" list, explicitly declined a new `roadmap.md` (would duplicate structure BRIEF.md already
  refuses to duplicate for itself). Added 2 candidates from the review plus 2 self-generated ones (Output scope-limitation; ledger evidence-locator, folded into the existing Ledger-schema bullet).
- Evidence basis: memory-keeper channel `wbr`, 2 new keys. Checkpoint `slurp-20260916-wbr-teycir-review-parked`.

### 2026-09-16 (continued II) — `skill-walk-before-run` ledger format hardened to JSONL
- Reviewed the skill on operator request (design assessment: sound, two calibration risks flagged for post-trial revisit — Step 0 scoping subjectivity, signal 3 likely dead weight). Operator then
  pushed on the ledger format specifically: wanted a defined schema, local time not date-only, git branch capture, and a text-vs-TOML-vs-JSONL recommendation.
- Recommended and implemented JSONL over TOML (append-only, per-line failure isolation, trivial for the parked SessionStart hook), added `ts` (local UTC offset) and `branch` fields, and promoted the
  field reference to new `schemas/ledger-entry.md`. Updated SKILL.md, README.md, CHANGELOG.md, and BRIEF.md (new revision note, open decision #5).
- Self-correction recorded: characterized the table-reflow hook's blank-first-cell continuation rows on the new schema table as "corruption" needing a fix; this channel's own prior session already
  retracted that framing (KNOWN AND ACCEPTED, not a bug) — see `wbr.tooling.table-reflow-continuation-rows-not-a-bug-20260916`.
- Evidence basis: memory-keeper channel `wbr`, 4 new keys. Checkpoint `slurp-20260916-wbr-ledger-jsonl`.

### 2026-09-16 (continued) — `skill-walk-before-run` v0.1 built, installed, and refined
- Built the three-file-plus-brief package by hand (`SKILL.md`, `README.md`, `CHANGELOG.md`, `BRIEF.md`) after `skill-creator`'s own loaded instructions proved to be the generic Codex convention (wrong
  install root, wrong file list) rather than this repo's actual pattern — confirmed against `skill-project-coherence` and `skill-code-context-notes` first. Symlinked into `~/.claude/skills` and
  `~/.codex/skills`.
- Operator then directed two refinements: ledger path moved from the brief's `skills-data` proposal to colocated `ledger.md`, and the brief itself moved from `pending_skills/` into the skill directory
  as `BRIEF.md`, with its open decisions #2 and #4 marked decided in place. Mid-slurp, the invocation command was also renamed `/walk-before-run` → `/skill-walk-before-run`.
- Evidence basis: memory-keeper channel `wbr`, 14 keys total (6 new this session, 3 corrected in place). Checkpoint `slurp-20260916-wbr-build-shipped`.

### 2026-09-16 — `skill-walk-before-run` brief authored and frozen
- Operator named a recurring pattern (framework/design before verifying basics; JDM and ATAR abandoned that way) and asked for a skill that detects it and gates further scaffolding. Wrote the creation
  brief; skill not yet built.
- v1 of the brief was itself an instance of the pattern (8 signals, 6 prerequisites, telemetry, install policy, pre-trial) and was cut to a minimum testable v0.1: Step 0 names the assumption, four RED
  signals, scope-relative GREEN, a four-step gate, an episode-only ledger.
- Corrected my own account twice while verifying: `gfm_anchor` does not collapse whitespace runs (my re-implementation was the defect, and auto-memory already said not to re-implement it), and table
  continuation rows come from `table-reflow`, not `rewrap.py`, and are an accepted operator trade-off rather than a bug.
- Evidence basis: memory-keeper channel `wbr` (7 keys), checkpoint `slurp-20260916-wbr-brief-frozen`.

### 2026-09-01 — Agent Stack global installer and Orchestrator <!-- KEEP -->
- Added the English Orchestrator persona/skill and safe symlink-only global installation workflow; verified 123 managed links across Claude, Codex, and compatible `.agents` clients. <!-- KEEP -->
- Preserved the existing `skill-creator`; a temporary addition of `skill-slurp-chat` and `skill-project-coherence` was fully reverted at the operator's request. <!-- KEEP -->
- Evidence basis: memory-keeper `agent-stack.global-install` and `agent-stack.scope-decision`; project-context note and checkpoints recorded on 2026-09-01. <!-- KEEP -->

### 2026-08-12 — `skill-staleness-audit` authored, tested across four project shapes, installed `KEEP`
- **New skill**: repo-wide audit for facts that have quietly stopped being true. 24 files — 9 phases, 9 `patterns/`, 4 `templates/`, 6 enforcing `scripts/` + a `justfile`. Symlinked into all four
  agent targets. Extracted from a `me/japan/tracks/jdm` (then `me/jdm`) audit where two documents filed with a licensing authority stated a superseded gate **while 592 governance checks passed
  continuously**.
- **Design decision to carry to other skills**: scripts enforce, prose advises. Each phase writes a **receipt recording what it measured**, and the exit gate does arithmetic on those receipts —
  because nothing else distinguishes *"I did Phase 4"* from *"I said I did Phase 4"*. Phases needing judgement are deliberately left un-automated.
- **Generality tested rather than assumed**, at the operator's insistence. Running the scripts on four structurally different repos found **six defects in the scripts themselves**, including 120 false
  BROKEN paths on the first pass. Rule that came out of it: **a scanner with a ~50% false-positive rate is worse than none** — people stop reading its true positives too.
- Evidence basis: memory-keeper `skills_stuff.skill-staleness-audit.created-20260812`, `skills_stuff.skill-authoring.generality-testing-lesson-20260812`


### 2026-08-10 — skill-anydoc rename to house convention <!-- KEEP -->
- Renamed `anydoc` → `skill-anydoc`: canonical folder `skills/skill-anydoc/`, frontmatter `name: skill-anydoc`, old install dirs removed and re-linked in all three targets as file symlinks, each
  verified by reading the name back through the link. References updated in SKILL.md, README.md, `AGENTS.md` (Regular Skills row + file-symlink rule), SCRATCHPAD anchors, and auto-memory; residual
  grep empty. Launcher re-smoke-tested via stdin CSV. Command name and runtime cache dir kept as `anydoc` on purpose.
- Two silent-failure gotchas: the rewrap hook flattened nested `metadata:` frontmatter into one unparseable line (would have broken skill loading with no error); and `[ -e "$link" ]` dereferences, so
  the first cleanup pass saw all three dangling old links as absent and left them behind — `[ -L ]` is the correct test.
- Checkpoints: MK `96183925`, PC `f5358ce8-a67f-4858-9d2e-f51cfc88a53e`.

### 2026-08-10 — anydoc skill build/install + symlink install policy <!-- KEEP -->
- Built and installed `anydoc` (documents → GFM Markdown, upstream firecrawl/anydoc): npm runtime in `skills-working-cache/anydoc/`, bash launcher, canonical SKILL.md + workspace README, registered in
  `AGENTS.md`. Verified live on CSV (path + stdin), `.docx`, text-layer `.pdf`, `.xlsx`.
- Operator set install policy: symlink to canonical, never copy three separate files. Converted anydoc's three installs to symlinks and wrote the rule (both link forms + audit snippet) into
  `AGENTS.md` and auto-memory.
- Corrected my own audit: the first pass tested `-L "$dir/SKILL.md"` and wrongly reported ~160 skills as copies; inside a directory symlink that file is regular. True counts are 17/25/3. Surfaced two
  open structural issues — two-hop claude→codex links, and vendored skills with no canonical source.
- Checkpoints: MK `1072287f`, PC `175df7b4-3897-4aa5-af13-aa46060b2ebb`.

### 2026-06-19 — Codex skill symlink install + persistence repair <!-- KEEP -->
- Installed eight skills into `~/.codex/skills` using symlinks to canonical source folders; verified each link and `SKILL.md` visibility through the Codex install path.
- Resolved mcp-project-context project identity: `skills_stuff` project UUID is `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c`; added missed progress note and checkpoints after display-name writes failed.
- Slurped the UUID-resolution delta to memory-keeper and project-context; checkpoints: MK `b142dccb`, PC `38998ec4-9c06-4e7c-acd7-15c2918cc789`.

### 2026-05-24 — skill-project-wiki-rag-bridge creation + RAG tools infra <!-- KEEP -->
- Created `skill-project-wiki-rag-bridge`: 48 files covering full bridge lifecycle (wiki setup → domain creation → RAG validation → project bridge → policy validation → indexing → retrieval validation
  → troubleshooting); multi-project capable; conservative/audit-first; registered in skills_stuff README
- Validated RAG tools infrastructure: Qdrant on OrbStack operational, venv confirmed, 33 tests passing, embedding smoke test passed; UV_PROJECT_ENVIRONMENT pattern established over deprecated --venv
  flag
- Created `_wiki/CLAUDE.md` governance wrapper; false positive on "index all wiki" phrase in SKILL.md safety rules resolved (prohibitive clause, not instruction)

### 2026-05-22 — Auto-memory governance and coherence <!-- KEEP -->
- Relocated Claude auto-memory to `/Volumes/Data/_ai/claude-auto-memory/`; `autoMemoryDirectory` + `cleanupPeriodDays: 36500` in settings.json; CLAUDE.md governance rule added; 37 files migrated from
  15 per-project dirs, old files deleted
- Audited all 38 memory files: found 3-way name collision on governance-scan rule, scope mismatch in skill-smc entry, hardcoded project reference in general rule, inconsistent frontmatter, broken
  naming convention
- Fixed all issues: merged 3→1, normalized 7 frontmatter blocks, renamed `claude_md_thin_wrapper.md`, rebuilt MEMORY.md (36 entries, alphabetical, verified 0 broken links, 0 duplicate names)

### 2026-04-28 — graphify MCP install <!-- KEEP -->
- Added graphify MCP server to `~/.claude/settings.json` using uv-tool Python at `/Users/malik.ahmad/.local/share/uv/tools/graphifyy/bin/python`
- graphify requires Python >=3.10,<3.14; graphifyy[mcp] already installed via uv tool (no new venv needed)
- MCP serves `graphify-out/graph.json` relative to CWD; run `/graphify .` in a project first to generate graph

### 2026-04-22 — skill-commtracker attachment capture + Python scripts
- Added MIME attachment/inline image extraction to skill-commtracker (Steps 3/4/4.5/6 + quality checklist); both SKILL.md files updated
- Built `extract.py`, `reconcile.py`, `toc.py` under `~/.agents/scripts/commtracker/` (stdlib-only, Python 3.14)
- Validated on aurukun-fni (7 real images extracted, 36 signatures skipped) and of-si (40 signatures all skipped correctly)

### 2026-04-22 — skill-slurp-chat SCRATCHPAD step
- Added Step 6.5 to skill-slurp-chat: update SCRATCHPAD.md after checkpoints, before closeout
- Updated both installed (`~/.claude/skills/skill-slurp-chat/SKILL.md`) and authoring source
- Evidence basis: mcp-project-context `skills_stuff.skill-slurp-chat.scratchpad-step-20260422`

### 2026-04-22 — skill-ai-it creation and installation
- Created skill-ai-it: 5-phase content-aware governance bootstrap (Inventory→Understand→Infer→Generate→Update Parent)
- Always creates: README, AGENTS, CLAUDE, SCRATCHPAD (populated from memory); conditionally: ARCHITECTURE, CONVENTIONS, ROADMAP
- Tested on aurukun-fni (full bootstrap) and of-si (update pass)
- Evidence basis: mcp-project-context note `skill-ai-it created and installed`

### 2026-04-20 — swarms skill pack
- Installed am-will/swarms: 7 skills including co-design, parallel-task, swarm-planner, super-swarm
- Avoid parallel-task-tmux (Snyk Critical Risk)
- Evidence basis: mcp-project-context note

---

## Next actions

- `skill-walk-before-run`: the 3-project trial has run (cambium-swap, jdm, atar — all RED, all well-formed per review), but acceptance tests 2/3/4/5 (negative control, adversarial, Step-0 visibility,
  assumption stability) were never separately validated, and there are 0 RESOLVED entries yet — the real hypothesis (does RED change behaviour) isn't tested until the 3 named cheap tests actually get
  run and logged. That's the next real action, not more invocations.
- Decide whether to convert the Tier 1 copy-installed skills to symlinks (9 skills, canonical source exists for each) <!-- KEEP -->
- Optionally commit `skills/skill-anydoc/` — currently untracked; decide whether `anydoc-github/` becomes a submodule or is excluded <!-- KEEP -->
- Restart Codex and Hermes so they pick up the `skill-anydoc` name (Claude Code already re-registered it live) <!-- KEEP -->
- First real test of skill-project-wiki-rag-bridge: run `prompts/06-post-index-retrieval-validation.md` against Vocus project + `rag__wiki_nbn` collection (already indexed)
- Respond to any follow-up on skill-commtracker, helper scripts, or skill-slurp-chat behavior
- Resolve `~/.codex/skills` vs `~/.agents/skills` authority question when prioritized
- Monitor auto-memory: verify new session writes land in `/Volumes/Data/_ai/claude-auto-memory/` (not per-project dirs)

---

## Memory pointers (navigation only — content is above)

- memory-keeper channel `wbr` (2026-09-16), 27 keys total: original 8 + 6 from the build session (see prior checkpoints below) + 4 from the ledger-JSONL session + 2 from the Teycir/Assumptions review
  + 7 new from the v0.1.1 hardening session (`wbr.error.skill-wbr-alias-never-registered-20260916`, `wbr.decision.v011-default-targeting-and-writeback-20260916`,
  `wbr.decision.ledger-check-before-rederiving-20260916`, `wbr.decision.project-naming-rule-and-jdm-fix-20260916`, `wbr.decision.resilience-mirror-20260916`,
  `wbr.progress.backfill-target-projects-20260916`, `wbr.decision.stale-red-and-sync-questions-20260916`). Checkpoints, both backends: `slurp-20260916-wbr-brief-frozen` (MK `df575ee5`, PC
  `ba6b9ec8-62d6-4e29-9d24-b5fb0808a3ab`), `slurp-20260916-wbr-promotion-and-scratchpad` (MK `1154a452`, PC `03ed00d7-504b-4173-8c16-8986a121a144`), `slurp-20260916-wbr-build-shipped` (MK `461cd6d3`,
  PC `bac99a7b-1684-44e7-847c-d8927eb7c2d0`), `slurp-20260916-wbr-ledger-jsonl` (MK `389da624`, PC `19997b84-5741-4301-9113-f1e2c7f7df48`), `slurp-20260916-wbr-teycir-review-parked` (MK `f629015a`, PC
  `1a15dad2-054d-4f21-a61f-59aa86a32906`), and `slurp-20260916-wbr-v011-hardening` (MK `66306bf8`, PC `7336bb20-7a49-4a7c-9f0a-f2df03c39c40`). Project `skills_stuff`, channel `wbr`.
- Trial project ledgers (outside skills_stuff): `.wbr-ledger.jsonl` + `SCRATCHPAD.md` § Open items pointer in each of `project_stuff/apn/cambium-swap`, `project_stuff/me/uae/atar`,
  `project_stuff/me/japan/tracks/jdm` — all uncommitted in their own repos as of 2026-09-16.
- memory-keeper channel `agent-stack`: `agent-stack.global-install`, `agent-stack.scope-decision`; checkpoint `slurp-20260901-agent-stack` (ID: `8ddf5b1c`). <!-- KEEP -->
- mcp-project-context project `skills_stuff`, channel `agent-stack`: checkpoint `slurp-20260901-agent-stack` (ID: `d0385431-ef7b-4306-ad9a-59ff4543d75f`). <!-- KEEP -->
- memory-keeper channel: `skills-stuff` / keys (2026-08-10): `skills_stuff.anydoc.install-20260810`, `skills_stuff.skill-install.symlink-policy-20260810`,
  `skills_stuff.skill-install.audit-method-bug-20260810`, `skills_stuff.skill-install.copy-conversion-backlog-20260810`
- MK checkpoint: `slurp-20260810-anydoc-symlink-policy` (ID: 1072287f) — PC checkpoint same name (ID: 175df7b4-3897-4aa5-af13-aa46060b2ebb)
- memory-keeper channel: `skills-stuff` / keys (2026-08-10, rename pass): `skills_stuff.skill-anydoc.rename-20260810`, `skills_stuff.frontmatter.rewrap-hook-flattens-nested-yaml-20260810`,
  `skills_stuff.skill-install.dangling-symlink-test-bug-20260810`
- MK checkpoint: `slurp-20260810-skill-anydoc-rename` (ID: 96183925) — PC checkpoint same name (ID: f5358ce8-a67f-4858-9d2e-f51cfc88a53e)
- memory-keeper channel: `skills-stuff` / keys: `skills_stuff.project_context_uuid_resolution_2026-06-19`, `skills_stuff_codex_skill_symlink_install_2026-06-19`,
  `skills_stuff.graphify.mcp-install-20260428`, `skills_stuff.skill-commtracker.attachment-capture-20260422`, `skills_stuff.commtracker-scripts-20260422`,
  `skills_stuff.skill-slurp-chat.scratchpad-step-20260422`
- project-context project ID: `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c`
- PC checkpoint: `slurp-20260619-skills-stuff-project-context-id` (ID: 38998ec4-9c06-4e7c-acd7-15c2918cc789)
- MK checkpoint: `slurp-20260619-skills-stuff-project-context-id` (ID: b142dccb)
- PC checkpoint: `slurp-20260524-skill-project-wiki-rag-bridge` (ID: 53f7a401)
- PC checkpoint (tools_stuff): `slurp-20260524-rag-tools-operational` (ID: ef31d3c2)
- MK checkpoint: `slurp-20260428-graphify-mcp` (ID: 85a20c64) [prior]
- PC checkpoint (prior): `slurp-20260428-graphify-mcp` (ID: 1a531e71)
