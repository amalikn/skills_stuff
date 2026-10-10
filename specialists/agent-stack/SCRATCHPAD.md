---
Title: Scratchpad
Category: working-state
Status: current
Summary: Current working state, newest first per section; superseded entries rotate to docs/history (search with --find).
Kind: state
Keep: Next actions=1, Memory pointers=1, Session history=2, Current state=3, Recent decisions=3
Open items tracker: docs/trackers/open-items-20261010_1821.md
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261010_1822
---

# SCRATCHPAD

Agent working memory for Agent Stack. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 20260901_1240 from memory-keeper + mcp-project-context + claude-mem -->

## Contents

- [Current state](#current-state)
- [Open items](#open-items)
- [Key anchors](#key-anchors)
- [Recent decisions](#recent-decisions)
- [Session history (summaries — full detail in memory-keeper)](#session-history-summaries--full-detail-in-memory-keeper)
- [Residual risk — staleness audit 20260903_2200](#residual-risk--staleness-audit-20260903_2200)
- [Next actions](#next-actions)
- [Memory pointers (navigation only — content is above)](#memory-pointers-navigation-only--content-is-above)

## Current state

**Phase (20260903):** FIELD-USE phase. Every capture and self-improvement mechanism is now built and gated; none of it has consumed real evidence yet — the field log holds 6 entries and
[evals/capability-gaps.jsonl](evals/capability-gaps.jsonl) is empty. That emptiness is the current state, not an oversight: the loop is instrumented and waiting on actual use. Upstream sync is retired
and the project is maintained on its own.

**External reliability survey (20260903).** The 25-repository survey is now normalised in
[docs/reliability-adaptation/agent-stack-reliability-adaptation-proposal-20260903_1943.md](docs/reliability-adaptation/agent-stack-reliability-adaptation-proposal-20260903_1943.md). Its five
mechanisms are a deferred, evidence-triggered backlog—not a delivery plan. A future normal-work receipt, if field evidence proves one necessary, is one JSON object per line in the existing
`evals/field-log.jsonl` entry; the project-local run manifest remains the complete snapshot. `KEEP`

**Phased implementation plan authored, still inert (20260904).** After the operator raised a felt gap (routing quality; personas not coordinating hand-offs) and asked for an implementation +
verification plan,
[docs/reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md](docs/reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md) fixes the
exact steps and self-verification checklist per phase, plus a 17-row source-provenance table. It authorises nothing on its own — the evidence-gate rule above still applies. `KEEP`

**The evolution loop, end to end.** A persona that hits a limit while working declares it (`--gap-missing` / `--gap-inadequate` on Step 7.5); the declaration is written BOTH into the consuming
project's run manifest and into this repo's own tracked gap log; `just evolve` aggregates repeats into proposals and **never applies them**. Gaps come home because a gap is a statement about *this
library* — a record living only in a consuming repo dies when that repo moves, is deleted, or turns out to be one Agent Stack must not read.

**Phase (superseded 20260902):** Routing-development phase CLOSED. Deterministic closure is built and measured, the catalogue carries one persona model, the 60-case corpus is frozen, both P1 audit
findings are shut, and 29 Archcore documents are accepted. The next evidence must come from outside this corpus.

**Where routing stands.** With deterministic closure the frozen 60 scores **50/60**, and live on the 20-case holdout: **Flash 13/20 (65.0%) · Pro 15/19 (78.9%) · Claude 16/20 (80.0%)** — every arm
25–40 points above the same holdout without closure, and the two production arms converged near 80%. The architecture is settled and measured rather than argued: **the model judges, the system
satisfies constraints.** Where a rule is a lookup against a finite catalogue, a program does it exactly and a model does it sometimes.

**What closed the loop.** Baseline v3 rejected prompt-only closure as a valid negative result; the three-way cross-model experiment showed the defect was model-invariant (`unsatisfied` 7/6/7); the
staleness audit then found the catalogue was asserting **two contradictory persona models at once**, which retroactively explained both the ten cross-model failures and the `atar-supplier` ownership
dispute. Resolving it, building closure, and unifying the eval contract with production were the three changes that mattered.

Agent Stack is the English-only extraction of Auto Company's personas and skill library, canonical at `/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack`. The 2026-09-01 revision expanded
all 15 personas into operational judgement contracts, added `routing.toml` as the routing catalogue, and added the `RUNTIME.md` / `SKILL_STANDARD.md` contracts. Library is 52 capabilities: 15 personas
+ 37 skill entries (36 packages plus the single-file `frontend-design`). A full repository audit sits in `docs/audits/audit-agent-stack-full-20260901_1010.md` with a verdict of SOUND WITH MATERIAL
  GAPS; its P1
findings A1 (non-atomic sync) and A2 (symlink escape) were deliberately deferred out of the revision and remain open.

On 2026-09-01 the governance layer was bootstrapped and a confirmed storage-routing violation fixed: `.mise.toml` was creating the maintenance venv inside the source repo, hidden by `.gitignore`. A
later pass applied the routing-evals delta update (50 files) and re-applied the governance deltas the update overwrote, then made interpreter resolution explicit throughout: recipes now address the
venv Python by path via `{{py}}` with a `_require-venv` guard, replacing an implicit `mise exec -- python` that resolved correctly but hid the dependency at every call site.

---

## Open items

- Older open items are tracked in [open-items-20261010_1821.md](docs/trackers/open-items-20261010_1821.md).

- [x] ~~**NEXT PHASE — evidence from outside the frozen 60**~~ — FIRST EVIDENCE IN, 20260902. The 24-case holdout is authored, executed and SPENT: 16/19 passed, 5 runner failures, 0 missed gates, 62
  over-asserted ones. Replay and shadow-mode remain. Superseded detail: Author an unseen holdout of 20–30 cases without reference to the development corpus; replay real historical project tasks; then
  shadow-mode routing alongside normal work. Only after that decide whether more routing taxonomy or personas are needed. See [plan 0001](.archcore/plans/0001-next-evaluation-phase.md).
- [x] ~~**`policy_guard.py enforce` pre-commit hook blocks every commit in `skills_stuff`**~~ — RESOLVED 2026-09-04 (later same day), in `scripts_stuff` not here: the required governance phrases
  (Commit Message Governance, Tier 1/2/3, etc.) all genuinely exist, but only in ~/.agents/AGENTS.playbook.md, the on-demand file the thin global `AGENTS.md`/`CLAUDE.md` deliberately split this
  content into — the checker's `@`-import resolver never followed the markdown-link reference to it, so it predated that architecture split. Fixed the checker (not the files, avoiding the content
  duplication that would have re-created) in `scripts_stuff`, commit `df86024`, not this repo. `policy_guard.py enforce` now reports 130/130 PASS. No more `--no-verify` judgment call needed.

No model set the gate flags reliably, and the strongest model still missed `critic_required` on an architecture decision. **Root cause found 2026-09-01 — it is not model capability. See the next
item.**

So a model is scored on hard assertions for four concepts the catalogue it was handed never specifies. Two aggravating factors in the prompt builder:
  - `PLAN_SCHEMA` shows all four flags as `false`, anchoring the answer toward false before the model reasons at all.
  - The only instruction is one line — "Flags describe whether the route requires that gate/runtime class" — naming no criteria and pointing at no section of the catalogue.

Fix the contract, not the score: define the four gate classes in `routing.toml` with the conditions that trigger each (`economics-gate` and `import-economics-gate` ids already exist there, so there is
a shape to follow), then reference them from the prompt rules. Until that is closed, the behavioural scores measure the gap rather than routing quality and must not be published as a baseline.

---

## Key anchors

| Item                | Detail                                                                                                     |
| ------------------- | ---------------------------------------------------------------------------------------------------------- |
| Canonical root      | `/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack`                                           |
| Maintenance venv    | `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/venv` (never in-repo)                          |
| Upstream source     | `MaxMiksa/Auto-Company` (GitHub), mirrored disposably under `skills-working-cache`                         |
| Library size        | 52 capabilities — 15 personas, 37 skill entries                                                            |
| Live global install | 123 symlinks — 15 persona links + 36 skill links across 3 clients (skill-creator excluded)                 |
| Install targets     | `~/.claude/agents`, `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`                              |
| Excluded by default | `skill-creator` (duplicate); pass `--include skill-creator` only after reconciling                         |
| Git remote          | `https://github.com/amalikn/skills_stuff.git` (operator-owned)                                             |
| Validation          | `just bootstrap` then `just preflight` (runtimes, check, governance, routing-eval-check, test)             |
| After-baseline      | 28/60 (46.7%), mean 80.6 — `after-<family>-20260901.jsonl` in the results dir                              |
| Routing corpus      | 60 cases across 6 families in `evals/routing-cases.toml`; see `ROUTING_EVALS.md`                           |
| Eval results        | `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/routing-results/` (working cache, rebuildable) |
| Eval routes         | `just routing-eval-hermes` (cloud DeepSeek via Hermes), `routing-eval-local` (Ollama), `routing-eval-ping` |

---

## Recent decisions

- **2026-09-07 — Recommended operator keep using Hermes Agent personally rather than switch to OpenFang; not an Agent Stack change.** Operator confirmed the question was prompted by OpenFang's GitHub
  star count (18k+), not a concrete Hermes pain point. Reasoning: high switching cost (months of accumulated Hermes cron/gateway/config investment, no migration tooling from Hermes to OpenFang, only
  OpenClaw→OpenFang exists); Hermes's self-improving skill loop has no OpenFang equivalent (Hands are static); OpenFang's Rust-vs-Python resource edge doesn't matter for personal use bound by LLM API
  latency. Flagged star count itself as weak evidence — correlates with launch attention as much as adoption on a young (551-commit) repo, doesn't measure stability or fit to an existing setup. `KEEP`
- **2026-09-05 — Recommended against forking OpenFang (RightNow-AI) to "tame" it into an autonomy-free Agent Stack base; not actioned.** Operator asked directly. Reasoning: (1) OpenFang's value is
  concentrated exactly in the parts that would need stripping — kernel scheduler/RBAC/budget, autonomous "Hands" lifecycle, P2P wire protocol, credential vault, 40 channel adapters; what remains (Rust
  runtime + 3 LLM drivers + 53 tools + MCP/A2A) is less than `routing.toml` + personas already provide, at the cost of maintaining 137K lines of foreign Rust. (2) autonomy is load-bearing through its
  kernel/memory/channels, not a bolt-on toggle — taming it would be a permanent re-suppression tax on every upstream merge, the same class of problem this project's own safety-adaptation clause
  already names for imported skill instructions, but at whole-codebase scale. (3) different problem shape — Agent Stack routes/judges inside human-driven coding-harness sessions; OpenFang is a
  standalone always-on runtime built to replace the human-driven session. Alternative offered instead: study OpenFang's HAND.toml manifest schema (identity/tool-grant + typed `[[settings]]` config +
  declared `dashboard.metrics` + embedded system prompt, one file per agent) as a design idea, not the codebase — flagged as a gap to raise next time the `routing.toml`/`SKILL.md` split comes up (see
  Next actions and Memory pointers below). `KEEP`
- **2026-09-04 — Don't backtick an external repo/org/file name in a governance "surface" file; backtick only the code symbol.** `scripts/check_governance.py`'s `check_referenced_paths()` scans every
  backticked token in the six SURFACES files (README.md, AGENTS.md, CLAUDE.md, SCRATCHPAD.md, CHANGELOG.md, SKILL.md) and fails if a path-like token doesn't resolve on disk — it cannot tell an
  external GitHub org/repo name (has a slash) or an external filename with a tracked suffix apart from a real local path. Hit writing a CHANGELOG.md entry for the best-of-agent-harnesses survey,
  naming the source list's own org/repo path and its data-file name in prose — both are external, neither is a local path. Fixed by not backticking either external name, matching the file's own
  existing precedent of backticking only a bare function like `_watch()`, never the repo name it belongs to. Working documents under `docs/` are unaffected — they aren't in SURFACES. `KEEP`

---

## Session history (summaries — full detail in memory-keeper)

- **20260907 (twelfth segment) — Personal-tooling follow-up: keep Hermes over OpenFang, star-count skepticism. KEEP.** Operator asked directly whether to keep using Hermes or switch to OpenFang;
  confirmed the trigger was OpenFang's star count, not a Hermes pain point. Recommended keeping Hermes on switching-cost, capability-gap (Hermes's self-improving skill loop has no OpenFang
  equivalent), and irrelevant-resource-edge grounds, and separately flagged GitHub stars as weak evidence for a young, high-autonomy-surface repo. Personal decision, not an Agent Stack change — no
  files touched. Separately, closed out the eleventh segment's pending item: committed and pushed the `skills/skill-creator/scripts/quick_validate.py` agentskills.io fix as `1189965` (scoped `git add`
  to exactly the three touched files; repo root carries unrelated dirty state from concurrent work, left untouched), pre-commit governance hook full PASS, pushed to origin/main (`79b6731..1189965`).
- **20260905 (eleventh segment) — External agent-OS landscape check (OpenFang, Hermes), agentskills.io compatibility confirmed + one real gap fixed, HAND.toml studied, no-fork decision. KEEP.**
  Operator asked for a read on RightNow-AI/openfang, then a head-to-head against Hermes Agent (the operator's own live daily-driver at `~/.hermes`, not a survey candidate). Both are "always-on Agent
  OS" products — scheduled/unattended agents, persistent cross-session memory, multi-channel messaging gateways — directly opposite this project's safety model (no daemons, no autonomous loops, no
  implicit persistent state). Verdict on both: WATCH-at-most as landscape reference, nothing STEAL/ADAPT-worthy in their runtime mechanisms. Operator then asked whether Agent Stack's own `SKILL.md`
  format is compatible with the `agentskills.io` open standard Hermes cites (originally Anthropic's, now open). Fetched the actual specification and confirmed Agent Stack is a compliant superset —
  same six spec fields plus 13 local extension fields — with one real gap: `skills/skill-creator/scripts/quick_validate.py` never checked the spec's MUST that `name` match the parent directory. Fixed
  it, validated against every skill directory in the repo (zero false positives) plus `just preflight` (1119 checks, 51 tests, green), and logged it in `CHANGELOG.md`. **Committed and pushed 20260907
  as `1189965` (see twelfth segment below).** Operator then asked whether forking OpenFang and disabling its autonomy could get Agent Stack where it's trying to go; recommended against it (see Recent
  decisions) and instead pulled the actual HAND.toml manifest from OpenFang's `researcher` Hand to study as a design idea: one file couples tool-permission grant + typed `[[settings]]` config schema +
  `dashboard.metrics` declarations + the full system prompt, versus Agent Stack's current split across `routing.toml` and each skill's own `SKILL.md` with no typed-settings or metrics-declaration
  convention. Operator explicitly asked that this single-file-coupling contrast be raised in the next Agent Stack architecture discussion — logged as a high-priority task in both memory backends, not
  actioned this session. `just governance` (1119 checks) green after the validator fix; no other files touched.

- Promoted that lesson into the canonical `skill-ai-it` at `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it` — a SKILL.md rule plus checklist item, the justfile template's
  RUNTIME PINNING header, and a new Tier 2 `check_interpreter_pinning` in its checker template, so every future bootstrapped project inherits it.

## Residual risk — staleness audit 20260903_2200

A clean gate is not a verified project. What this audit did **not** settle:

- **89 broken path claims remain inside `skills/`**, down from 114. They are dominated by references to a repository layout Agent Stack does not have — paths of the shape
  ../../tools/integrations/sendgrid.md and similar — inherited at import from a stack whose skills lived beside a `tools/` tree. Not introduced here. `check_skill_package_references` now covers the
  class that matters most (a skill promising its own scripts or references), and deliberately does not police references *outside* a package, where the correct target is a judgement call rather than a
  lookup.
- **`skills/websh/state/*.md` is runtime cache**, not authored content; its broken claims are URL routes (`/front`, `/ask`) that a path scanner reads as paths. Left alone — rewriting a cache to
  satisfy a scanner is the anti-pattern this skill names.
- **147 claims need manual verification** (48 counts, 99 uniqueness). The uniqueness claims are the live risk: they were true when written and falsify silently when a second instance appears, leaving
  nothing to grep for. Not individually re-enumerated this run.
- **The field log and the gap log are nearly empty** — 6 entries and 0. Every mechanism this project has built for learning from real use is unexercised, so no claim about the router's field behaviour
  rests on anything but corpus evidence.
- **39 of 40 indexed runs stamp a corpus hash that no longer resolves.** Known, recorded, and unfixable retrospectively — those runs are not reproducible against today's corpus file.
- **`graphify-out/GRAPH_REPORT.md`** is named in AI_NAVIGATION's generated-context table and has never been generated here. Marked optional rather than removed, because the tooling exists and the row
  is a pointer to a capability rather than a claim that a file is present.

### My own error in this audit

I removed a real capability section from `skills/devops/SKILL.md` after reading `find ... | head` — truncated at ten lines — as proof the two scripts did not exist. They exist, with underscores where
the SKILL.md wrote hyphens; the package has 29 files. Caught in Phase 4 when the artifact worksheet listed `skills/devops/scripts/cloudflare_deploy.py` by name, and restored as a two-character fix per
line. **`| head` on a discovery command is not evidence of absence**, and absence was the whole basis of the finding. Every other package edited was re-verified against a complete listing afterwards.

### Re-audit 20260904 — scoped pass, register re-verified, two new defects fixed

Run as part of a queued operator request ("staleness-audit in detail"), immediately after the reliability-adaptation gap-mapping work above. Snapshot, coverage manifest (296 files: 280 examined, 16
exempt, reconciles) and a full claim scan ran via the skill's own scripts. Scope decision, stated up front rather than discovered at the end: given three more queued tasks (project-coherence,
commit+push, slurp close), this pass re-verified the existing 20260903_2200 register and gave full materiality-ranked treatment only to claims inside this project's own core surfaces (`routing.toml`,
`evals/`, `.archcore/`, `docs/`, `SCRATCHPAD.md`, `CHANGELOG.md`, `MEMORY.md`, `scripts/`) rather than re-triaging all ~89 pre-existing `skills/` path findings from scratch — those were sampled
(websh, tailwind) to confirm the prior register's characterisation still holds, not re-litigated line by line. The audit skill's own completeness gate (verify-completeness) was not run to a PASS claim
on that basis; this is a scoped, honest FAIL/incomplete state, not a clean run.

**Confirmed still valid, unchanged:** all six 20260903_2200 residual-risk items above — the `skills/` inherited-layout paths, `websh/state/*.md` runtime-cache URL routes, the manual-verification
backlog (now ~163 claims, up slightly — this session added two new documents), the empty field/gap logs, the 39 unreproducible run hashes, and the optional `graphify-out/GRAPH_REPORT.md` reference.

**Two new, genuine defects found and fixed this pass (materiality G — governance/navigation drift, cheap and unambiguous):**
- `skills/tailwind-v4-shadcn/SKILL.md` used the singular form of its own references directory name in 5 places (a typo: "reference" instead of "references") while the real directory is plural,
  confirmed by 9 correct occurrences in the same file. Fixed all 5 to match. A skill-internal path defect, not the inherited-layout class above.
- `docs/routing-evaluation/routing-failure-classification-20260901_1842.md:10` linked to a sibling file named agent-stack-capability-taxonomy-and-scoring.md two directories up — a Baseline-v2-era
  draft that was never migrated into this repository and sits untracked at the `specialists/` level, superseded in substance by Rule 0007 and the current capability model in `routing.toml`. Rewrote
  the reference as prose naming what it is and pointing at what actually stands now, rather than leaving a dead link a reader could follow expecting a governing document.

**New findings this pass classified EXEMPT, not defects (naturally arising from today's own new documents, not previously seen):** the phased-implementation-and-self-verification-plan and
reliability-adaptation-proposal docs' mentions of a future harness-capability registry, a future execution-receipt object, and future scripts named for the audit-route and hand-off-validation work are
all explicitly prospective — artifacts the documents themselves say would be created only if a phase is triggered, never claimed as currently existing. Same treatment for the survey/off-topic docs'
external-repo paths (MetaGPT, AutoGen, the vertical-agent-framework survey's own named files) — descriptions of other repositories' structure, not local links. The `.archcore/` ADR/rule/guide
references to the retired upstream-sync tooling already carry proper "SUPERSEDED 20260903" banners (Phase 3 discipline already applied in an earlier session); the two `docs/audits/` reports
referencing the same retired tooling are dated point-in-time reports, exempt as MARKED-HISTORICAL the same way this project already excludes `CHANGELOG.md` entries from candidate inspection.

Verified: `just governance` and `just preflight` both green after the two fixes (see check-count line below). Snapshot and `.staleness-audit/` receipts kept, per the gate's own FAIL-state behaviour,
since this pass is explicitly scoped and incomplete rather than a clean exit.

### Re-audit 20260904 (tenth segment) — scoped to this session's own new content, three defects found and fixed

Run as part of the same queued sequence ("staleness-audit in detail"), immediately after creating the best-of-agent-harnesses-survey document (see Session history, tenth segment). Scope: rather than
re-running the whole-project machinery a second time in one day, verified every checkable claim the new document (and everything it was propagated into — CHANGELOG.md, this file, docs/README.md, and
both memory backends) actually made, against its real source. This is exactly the class of defect a "the checks pass" mindset misses: `just governance` and `just preflight` were green throughout, on
every version of the document below, including the wrong one.

**Three defects found and fixed, all materiality G (governance/navigation drift — wrong but cheap, unambiguous, no money or filing involved):**
- **A summed-total arithmetic error, restated identically wrong across six surfaces.** The document's own category counts (8+22+17+12+18 in-lane, 10+25+19+5+4+5+15 out-of-scope) were each individually
  correct, but the two totals stated from them — "78 of 160 in-lane" / "82 out of scope" — were wrong: the real sums are **77** and **83**. Re-verified by script against the source's own external
  harnesses.json data file, not by re-adding by hand a second time. Present in the document's own frontmatter Summary (twice) and its Category-by-category verdict section (twice), CHANGELOG.md,
  SCRATCHPAD.md's tenth-segment bullet, and both the memory-keeper entry and the mcp-project-context note — six surfaces citing the same wrong pair of numbers because each was typed from the same
  wrong mental arithmetic, not independently miscounted. Fixed in the four repo files directly (same edit repeated, not derived); memory-keeper corrected via a same-key overwrite (it supports in-place
  update); mcp-project-context corrected via an addendum note (it does not support edits or deletes).
- **A citation off by one line.** The omnigent finding cited its alpha-status badge at `README.md:11`; the actual badge is at `README.md:12` (line 11 is a Discord badge one line above it). Caught by
  re-opening the cached fetch and counting lines directly rather than trusting the number written down during the original research pass. Fixed in the document and the memory-keeper entry; noted as an
  addendum in the project-context note.
- **An approximation ("roughly 30 projects") that undercounted its own table by a third.** Script-parsed the findings table's own rows rather than re-estimating by eye: 40 distinct projects are named
  and individually reasoned about, not ~30 — the undercount excluded the SKIP-verdicted group rows even though the document's own sentence explicitly lists SKIP as one of the verdicts these projects
  received. Fixed in the same four surfaces plus both memory backends, same pattern as the first defect.

**A fourth finding, in the *existing* 2026-09-01 residual register rather than in anything created today:** re-verifying the standing residual list (this audit's own "confirmed still valid" step)
found `personas/README.md` — described there as absent, with "adding a README failed `just governance` immediately" — now genuinely exists (commit `c623350`, 2026-09-03) and is registered in
`scripts/check_governance.py`'s `CATALOGS`. The 2026-09-01 finding was true when written; it stopped being true two days later, and the register was never updated to say so — the exact "old material
keeps reading as current by design" failure mode this skill exists to catch, just inside this project's own audit trail rather than its subject matter. Per Phase 3 (make supersession visible, don't
rewrite history), the original 2026-09-01 paragraph is left as written with a `RESOLVED 2026-09-03` note appended in place, not silently corrected — see the annotation above under "The audit's exit
gate FAILED on two items." The Open Items checkbox above was updated from "two residuals" to "one," since the tsconfig JSONC item is the only one still genuinely open.

**Not re-run this pass:** the coverage manifest, claim scan, and inverse sweep scripts — the prior same-day scoped pass already ran them against the whole project and nothing structural changed
between the two passes (no files added or removed outside `docs/reliability-adaptation/` and the four index/log surfaces already covered above). Verified: `just governance` (1117 checks, up from 1115
before this pass's own fixes) and `just preflight` (51 tests) both green. Snapshot and `.staleness-audit/` receipts left untouched — they belong to the prior pass's own FAIL-state record and are not
this pass's to clear; the tsconfig JSONC residual is still open, so a full audit would still refuse to start clean regardless.

## Next actions

**The live item is unchanged and now unblocked: use Agent Stack on real projects and read what it records.** Every mechanism is built; none has evidence. Three things are waiting on the operator
rather than on work:

- **Raise the HAND.toml single-file-coupling contrast next time `routing.toml`/`SKILL.md`'s split comes up (operator request, 20260905).** OpenFang's Hand manifest couples tool-permission grant +
  typed `[[settings]]` config schema + `dashboard.metrics` declarations + the full system prompt in one file; Agent Stack has no typed-settings-schema or metrics-declaration convention today. Two
  schema-only (no-runtime) ideas already sketched: a `[[settings]]`-style typed config block a persona/skill could declare instead of freeform prose, and a `dashboard.metrics`-style declared
  metric-name convention for routing-eval output. Not actioned — discussion input only. Detail: `agent-stack.gap-hand-toml-single-file-coupling-20260905` /
  `agent-stack.hand-toml-manifest-structure-20260905`.

The measurement contract was repaired and frozen on 2026-09-02 **before** any unseen evidence is gathered, because a holdout is single-use: scoring it under a scorer that is later corrected spends the
holdout and answers nothing. Gate over-assertion now costs 5 points, coverage is reported, and the closure module is stamped into provenance. Frozen SHA set in [MEMORY.md](MEMORY.md), verified by
**`just freeze-check`** — run it before the holdout and before any run compared to a recorded baseline. It is not in `preflight` by design.

**The routing-development phase stays closed.** The open question is narrower than routing quality: *can the model discriminate gate truth at all when gate classification is isolated from routing?* If
it cannot, some gates should stop being model judgement and become deterministic.

Do **not** tune against the frozen 60. Add a case only to cover a new routing concept.

---

## Memory pointers (navigation only — content is above)

**Added 20260907 (twelfth segment, closeout) — keep-Hermes decision, quick_validate.py fix committed and pushed.** memory-keeper channel `agent-stack`:
`agent-stack.decision-keep-hermes-over-openfang-20260907` (decision) · `agent-stack.session-commit-20260907-quick-validate-fix` (progress) ·
`session.closeout.20260907.openfang-hermes-quick-validate-commit` (progress, high, full closeout template). Project-context: 3 notes (twelfth segment) on channel `agent-stack` of parent `skills_stuff`
(b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c). Checkpoints: memory-keeper `slurp-20260907-keep-hermes-decision` (09153220) and `slurp-20260907-close-openfang-hermes-commit` (c9d0a55f) · mcp-project-context
`slurp-20260907-keep-hermes-decision` (0988f691-29b5-464e-b006-297c17dcc4eb) and `slurp-20260907-close-openfang-hermes-commit` (b4bc1894-8185-403a-8e26-6afc6496498a). Committed as `1189965` (pushed,
`79b6731..1189965`).

**Added 20260905 (eleventh segment) — OpenFang/Hermes landscape check, agentskills.io compatibility + fix, HAND.toml study, no-fork decision.** memory-keeper channel `agent-stack`:
`agent-stack.openfang-research-20260905` (note) · `agent-stack.openfang-vs-hermes-20260905` (note) · `agent-stack.agentskills-io-compatibility-20260905` (note) ·
`agent-stack.quick-validate-directory-name-fix-20260905` (progress, high) · `agent-stack.hand-toml-manifest-structure-20260905` (note) · `agent-stack.gap-hand-toml-single-file-coupling-20260905`
(task, high — the flagged next-discussion item) · `agent-stack.decision-no-openfang-fork-20260905` (decision). Project-context: 7 notes (eleventh segment) on channel `agent-stack` of parent
`skills_stuff` (b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c). Checkpoints: memory-keeper `slurp-20260905-openfang-hermes-agentskills` (ae284972) · mcp-project-context
`slurp-20260905-openfang-hermes-agentskills` (a14feb08-8500-407c-881a-f1d1f54fa065). Committed as `1189965` 20260907 (see twelfth segment above).

**Added 20260904 (tenth segment) — best-of-agent-harnesses survey, staleness audit, coherence pass.** memory-keeper channel `agent-stack`: `agent-stack.best-of-agent-harnesses-survey-20260904`
(progress) · `agent-stack.governance-false-positive-backticked-external-refs` (error) · `agent-stack.staleness-audit-20260904-tenth-segment` (progress) ·
`agent-stack.project-coherence-20260904-tenth-segment` (progress) · `session.closeout.20260904.best-of-agent-harnesses-survey` (progress, high, full closeout template). Project-context: 5 notes (tenth
segment) on channel `agent-stack` of parent `skills_stuff` (b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c). Checkpoints: memory-keeper `slurp-20260904-best-of-agent-harnesses-survey` (6201f9c4) ·
mcp-project-context `slurp-20260904-best-of-agent-harnesses-survey` (436582c9-f592-4cc5-9226-726fb5624355). Committed as `17d73a4` (pushed, `4662762..17d73a4`).

**Added 20260904 (ninth segment) — provenance detail, three diagrams, coherence review.** memory-keeper channel `agent-stack`: `agent-stack.phased-plan.provenance-detail-and-diagrams-20260904`
(progress) · `agent-stack.phased-plan.current-state-diagram-added-20260904` (progress) · `agent-stack.phased-plan.coherence-review-20260904` (progress) · `agent-stack.contents-autosync-hook-behavior`
(note). Project-context note (ninth segment) on channel `agent-stack` of parent `skills_stuff` (b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c). Checkpoints: memory-keeper
`slurp-20260904-phased-plan-provenance-diagrams-coherence` (cf71dd21) · mcp-project-context `slurp-20260904-phased-plan-provenance-diagrams-coherence` (77d19978-0e2f-4f0a-85c2-d7a12ce06513). Committed
as `415a478`, `79c154c`, `8776f95`, `73b1a1d`, `213a80d` (all pushed).

**Added 20260904 (closeout) — staleness audit, coherence pass, cross-repo governance fix, commits.** memory-keeper channel `agent-stack`: `agent-stack.staleness-audit-and-coherence-pass-20260904`
(progress) · `agent-stack.global-governance-checker-fix-cross-repo` (decision, high) · `agent-stack.session-commits-20260904-1230` (progress) ·
`session.closeout.20260904.agent-stack-gap-audit-and-commit` (progress, high, full closeout template). Project-context note (eighth segment) on channel `agent-stack` of parent `skills_stuff`
(b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c). Checkpoints: memory-keeper `slurp-20260904-close-staleness-coherence-commit` (a17a96bb) · mcp-project-context `slurp-20260904-close-staleness-coherence-commit`
(0f164b9b-8eaa-47e8-8188-28edb5fca10c). Committed as `a393c75` (pushed) and, in `scripts_stuff`, `df86024` (not pushed).

**Added 20260904 (later same day) — gap evidence audit and phased plan.** memory-keeper channel `agent-stack`: `agent-stack.reliability-gap-evidence-audit-and-repo-mapping` (decision, high) ·
`agent-stack.phased-implementation-plan-authored` (progress, high) · `agent-stack.provenance-table-formatter-bug-recurrence` (error, high). Project-context note (seventh segment) on channel
`agent-stack` of parent `skills_stuff` (b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c). Checkpoints: memory-keeper `slurp-20260904-phased-plan-and-gap-mapping` (2d4ccdf7) · mcp-project-context
`slurp-20260904-phased-plan-and-gap-mapping` (68e00410-86ed-47e7-adf9-44af3e69dcad). Not yet committed.

**Added 20260904 — rule 0013 and six-document acceptance.** memory-keeper channel `agent-stack`: `agent-stack.rule-0013-trim-gate-and-batch-acceptance` (decision) ·
`agent-stack.global-governance-hook-blocks-commits` (error, still open). Project-context notes on channel `agent-stack` of parent `skills_stuff` (b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c). Checkpoints:
memory-keeper `slurp-20260904-rule0013-and-acceptance` (d997eef4) · mcp-project-context `slurp-20260904-rule0013-and-acceptance` (79bf5239-97a7-40dd-95ea-4c9363f4923c). Committed as `aa52305`.

**Added 20260903 — external reliability adaptation assessment.** memory-keeper key `agent-stack.reliability-adaptation-proposal`; project-context note on channel `agent-stack`; checkpoints:
memory-keeper `slurp-20260903-reliability-adaptation` (18ab6888) and project-context `slurp-20260903-reliability-adaptation` (7542bfc4-b7a3-4b2-96dd-5e277e80df94). `KEEP`

**Added 20260903 (rename pass)**, memory-keeper channel `agent-stack`: `agent-stack.skill-rename-and-orphan-check` — the `orchestrator` → `skill-agent-stack` rename, the three things deliberately not
renamed and why, and the false-confidence status check it exposed. Checkpoints: memory-keeper `slurp-20260903-skill-rename` (33bf03af) · mcp-project-context `slurp-20260903-skill-rename` (999bcf1a),
with an addendum note on the same channel. **Every memory entry written before 20260903 calls the entry-point package `orchestrator`; it is now `skill-agent-stack`.**

**Added 20260903**, memory-keeper channel `agent-stack`: `agent-stack.asymmetric-gate-scoring` (rule 0011, coverage reporting, closure_sha, the freeze made checkable) · `agent-stack.holdout24-spent`
(blind authoring, 16/19, the three ownership failures, status drift caught) · `agent-stack.gate-collapse-finding` (system-wide over-assertion, A/B1/B2, the conditional breakdown that reverses the
aggregate) · `agent-stack.runner-qualification-and-claude-retirement` (spec 0006 + Amendment 1, session limits, Flash 60/60, the recipe quoting defect) · `agent-stack.field-use-and-governance-infra`
(run index, docs reorg, field use, spec 0008, the pivot).

Checkpoints: memory-keeper `slurp-20260903-holdout-gatecollapse-fielduse` (cb446cde) · mcp-project-context `slurp-20260903-holdout-gatecollapse-fielduse` (1023b9ad). Project-context ninth-pass note on
channel `agent-stack` of parent `skills_stuff` (b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c).

**Added 2026-09-02**, memory-keeper channel `agent-stack`: `agent-stack.deterministic-closure` (the module, its two self-caught defects, the denominator fix and the re-report) ·
`agent-stack.baseline-v4-and-eval-contract` (three-arm results, the contract unification, the trap walked twice) · `agent-stack.routing-rules-resolution-and-policy` (P1, the declined recommendation
with its evidence trail, the corpus policy decisions) · `agent-stack.sync-hardening-and-archcore` (A1/A2 implementation detail and the full Archcore cycle).

Checkpoints: memory-keeper `slurp-20260902-closure-v4-archcore` (470d8835) · mcp-project-context `slurp-20260902-closure-v4-archcore` (f96635f4). Durable decisions now live in
[.archcore/README.md](.archcore/README.md) — 29 accepted documents, highest authority. Measured figures and traps stay in [MEMORY.md](MEMORY.md); the two do not overlap by design.

Checkpoints added: memory-keeper `slurp-20260901-v2-v3-crossmodel` (4483c2b0) and `slurp-20260901-closeout-audit-coherence` (d18c54bc); mcp-project-context `slurp-20260901-v2-v3-crossmodel` (591942fd)
and `slurp-20260901-closeout-audit-coherence` (ba9e835b). Audit and closeout keys: `agent-stack.staleness-audit-20260901`, `session.closeout.20260901.routing-baselines`. Result sets, working cache and
rebuildable: `routing-results/baseline3-<family>-20260901.jsonl`, `holdout20-pro-*.jsonl`, `holdout20-claude-*.jsonl`.

- memory-keeper channel: `agent-stack` / keys, newest first: `agent-stack.genuine-failure-analysis` (the 21 non-gate failures, grouped), `agent-stack.routing-after-baseline` (28/60 + failure-class
  shift), `agent-stack.gate-implementation` (what was applied and why), `agent-stack.routing-baseline-20260901` (the before run), `agent-stack.gate-definition-gap` (root cause),
  `agent-stack.full-corpus-baseline-run`, `agent-stack.behavioural-eval-connectivity`, `agent-stack.routing-evals-update`, `agent-stack.governance-bootstrap`, `agent-stack.global-install`,
  `agent-stack.scope-decision`
