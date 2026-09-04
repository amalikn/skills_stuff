# SCRATCHPAD

Agent working memory for Agent Stack. Use for: draft plans, terminal output, intermediate analysis, refactor outlines. Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 20260901_1240 from memory-keeper + mcp-project-context + claude-mem -->

## Contents

- [Current state](#current-state)
- [Open items](#open-items)
- [Key anchors](#key-anchors)
- [Recent decisions](#recent-decisions)
- [Session history (summaries — full detail in memory-keeper)](#session-history-summaries-full-detail-in-memory-keeper)
- [Residual risk — staleness audit 20260903_2200](#residual-risk-staleness-audit-20260903_2200)
- [Next actions](#next-actions)
- [Memory pointers (navigation only — content is above)](#memory-pointers-navigation-only-content-is-above)

---

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

- [x] ~~**`routing_rules` contradiction — two persona models in `routing.toml`**~~ — RESOLVED 2026-09-02, the top finding of the audit. All twelve rules are now advisory; `require_personas` became
  `prefer_personas`; the two `*-gate` ids were renamed so nothing in that table pretends to be a gate. Two validator guards, both negative-tested, prevent its return. It also explained the
  `atar-supplier` disagreement.
- [x] ~~**Audit receipts blocking the next audit**~~ — archived 2026-09-02 to the working cache under an audit-archive folder dated 20260901, with a README recording that the gate ended FAILED and
  why; the stale `.gitignore` entry is removed. Not deleted: a failed gate is when the pre-audit state is worth keeping.
- [x] ~~**Audit findings A1 and A2**~~ — CLOSED 2026-09-02. Sync apply is staged-then-promoted with atomic state writes ([ADR 0009](.archcore/adr/0009-sync-apply-is-atomic.md)); symlinks are refused
  outright and containment is enforced on both source and destination ([rule 0010](.archcore/rules/0010-sync-refuses-symlinks.md)). Superseded detail: Sync apply is non-atomic, and sync follows
  symlinks through `is_file`/`copy2` so a supplied symlink can escape the intended roots. Best fixed together; do them before calling Agent Stack broadly production-ready.

- [x] ~~**`routing_rules` contradiction**~~ — RESOLVED 2026-09-02 (see the residual note below, now historical). Twelve rules made advisory, two renamed, two negative-tested guards added. It also
  explained the `atar-supplier` disagreement.
- [x] ~~**Archcore promotion**~~ — DONE 2026-09-02. Queue regenerated rather than promoted stale, 29 documents promoted, all accepted by the operator. `.archcore/` is highest authority;
  `.archcore/README.md` is the index and carries the never-promote list.
- [x] ~~**NEXT PHASE — evidence from outside the frozen 60**~~ — FIRST EVIDENCE IN, 20260902. The 24-case holdout is authored, executed and SPENT: 16/19 passed, 5 runner failures, 0 missed gates, 62
  over-asserted ones. Replay and shadow-mode remain. Superseded detail: Author an unseen holdout of 20–30 cases without reference to the development corpus; replay real historical project tasks; then
  shadow-mode routing alongside normal work. Only after that decide whether more routing taxonomy or personas are needed. See [plan 0001](.archcore/plans/0001-next-evaluation-phase.md).
- [ ] **`policy_guard.py enforce` pre-commit hook blocks every commit in `skills_stuff`** — unrelated to agent-stack: `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` are both missing required
  global-governance phrases (Commit Message Governance, Tier 1/2/3, Mandatory closeout persistence policy, Global Sub-Agent Execution Governance, etc.). Bypassed once with `--no-verify` on 2026-09-04
  as an explicit operator exception, not a standing practice. Fix the two global files (or reconcile the policy's expected-phrase list, if it is the policy that is stale) before the next commit needs
  the same judgment call.
- [ ] **Two staleness-audit residuals remain formally unaccepted** — a vendored TypeScript config that is JSONC and unparseable by a strict loader, and the inverse sweep flagging package-internal
  resource directories this project catalogues by package. Receipts are archived under the working cache; accept or resolve them before the next audit run.

### Residual risk after the 2026-09-01 staleness audit `KEEP`

- **UNRESOLVED, AND THE TOP FINDING: `routing.toml` carries two contradictory persona models at once.** Seven `[[routing_rules]]` entries **require** a persona on keyword match
  (`material-independent-challenge` → `critic-munger`, `economics-gate` and `import-economics-gate` → `cfo-campbell`, `architecture-owner` and `network-technical-owner` → `cto-vogels`,
  `import-evidence-first` and `current-facts-research` → `research-thompson`), which is exactly the gate-summons-a-persona model the capability refactor replaced — while `[[gates]]` sets
  `persona_mandatory = false`. `architecture-owner` vs `implementation-owner`, and `product-experience-chain` vs `implementation-owner`, are the same conflicts `[[precedence]]` was written to rank,
  still asserted unranked. **The whole catalogue is in the prompt, so the model receives both instruction sets.** This is a live hypothesis for the 10 cases that fail on both production models and for
  Pro/Claude agreeing on only 35% of routes. NOT FIXED HERE: retiring or subordinating `routing_rules` changes the catalogue the frozen baselines were measured against, and is an operator decision. No
  check written for it yet, because a check would have to encode the intended resolution.
- **Not verifiable from inside the project:** whether DeepSeek's published V4-Pro agent-capability figures are as reported (operator-stated, not read from the vendor's documentation this session), and
  whether `claude -p` invoked from inside a session behaves identically to a standalone invocation.
- **My own errors this session, recorded rather than quietly fixed:** published the v3 frozen SHA set one docstring edit stale and corrected it; described a mis-invoked runner as producing an
  unlabelled model failure when the harness does label it `execution-error:` (the real defect is narrower — it stays in the denominator); claimed after two families that v3 was moving failures one
  stage further through the pipeline, which the full 60 did not support.
- **The audit's exit gate FAILED on two items, both tool-vs-project mismatches, deliberately not engineered away.** (a) `skills/tailwind-v4-shadcn/templates/tsconfig.app.json` is **JSONC** — it
  carries `/* Bundler mode */` comments, which is the standard TypeScript config format and correct for its consumer, but not parseable by a strict JSON loader. (b) The inverse sweep reports 12 items:
  11 are internal resource subdirectories (`references/`, `templates/`, `resources/`, `state/`) of skill packages that ARE registered in `manifest.yaml`, where the package is the catalogued unit per
  `SKILL_STANDARD.md`; the 12th is `personas/` having no README, which this project's own checker forbids — that directory contractually holds registered capabilities only, and adding a README failed
  `just governance` immediately. All 7 genuine project defects were fixed; these 2 are the tool's heuristics meeting this project's structure.
- **The audit receipts are deliberately retained.** A failed gate keeps `.staleness-audit-snapshot-20260901_115115/` and `.staleness-audit/`. The next audit run will refuse to start until they are
  cleared — clear them once the two residuals above are accepted or resolved.
- **Thin evidence:** the high-consequence dual-challenge bucket is 6 cases; 3/6 has wide error bars and should not carry a verdict on its own. The ordinary bucket (0/14) is the trustworthy one.


- [x] ~~**Capability-mapping visibility**~~ — RESOLVED 2026-09-01 by classification, not by relabelling. All 22 were checked against what each skill actually does and none is a mapping defect:
  `financial-unit-economics` acquires no external evidence, `deep-analysis` analyses what is already present, `security-audit` and `senior-qa` are validation rather than challenge, and `devops`
  release checks are incidental. Relabelling any of them would breach the taxonomy document's own §14 and destroy the `analysis != independent challenge` invariant.
- [x] ~~**Gate satisfaction as a route invariant**~~ — BUILT AND MEASURED 2026-09-01. It did not work. Baseline v3 moved zero cases on routing merit and stage-2 "no selection" doubled. Kept anyway on
  operator decision: it costs nothing at inference and improves the initial route.
- [x] ~~**DETERMINISTIC CLOSURE**~~ — BUILT AND MEASURED 2026-09-01: `scripts/close_route.py` takes the stored v3 routes from **34/60 to 47/60** with zero regressions and no model calls; holdout Flash
  8→14, Pro 10→15, Claude 8→15. Wired into the evaluator as `--repair` and into the orchestrator as a system step. Original rationale: Model proposes owner / personas / skills / gates; a deterministic
  validator then resolves the minimum satisfying capability, enforces strength, enforces runtime prerequisites and preserves the team cap; revalidate; final route. **LLM = judgement, system =
  constraint satisfaction.** Every piece already exists: `capability_strength()` computes closure, the catalogue enumerates minimal providers, and `--rescore` proves a repair pass changes nothing
  else. Same lesson `runtime_required` taught — it became reliable the moment it stopped being self-reported.
- [x] ~~**Disambiguate the 10 contract cases**~~ — DONE 2026-09-01/02. Four resolved by deterministic closure. Six classified: `release-readiness` resolved by `default_skill`; `net-dns-migration` by
  the earned-runtime-assertion fix; `net-security-review`, `python-feature`, `jdm-portal-build` need the tags decision below; `atar-supplier` is a genuine ownership dispute where both production
  models overrule the precedence rule.
- [x] ~~**Re-run the 20-case holdout on all three arms**~~ — DONE. Baseline v4: Flash 13/20, Pro 15/19, Claude 16/20 with closure, against 8/10/8 without.
- [x] ~~**Provenance semantics**~~ — rows now carry `prompt_inputs`; the eval builds its prompt from the production orchestrator's `eval-routing-contract` block, so eval/production drift is now
  impossible rather than undetectable. Validator guard negative-tested.
- [x] ~~**tags vs `required_personas`**~~ — DECIDED 2026-09-02. `required_personas` is for mandatory ownership or independent judgement, never an ideal team; tags say why a policy applies and stay a
  model judgement; a capability suffices for ordinary fulfilment. Policy stated in the corpus header; three cases relaxed. Superseded detail: The distinction is now formalised in `routing.toml` (tags
  say *why* a policy applies and are judged by the model; `required_personas` says *what* a case must contain) and the escalation is implemented in `scripts/close_route.py`. What remains is a choice
  for three cases — `net-security-review`, `python-feature`, `jdm-portal-build`: author task tags per case deliberately, or accept that a validation capability suffices and relax those
  `required_personas`. Do not derive one from the other.
- [x] ~~**`atar-supplier` ownership**~~ — CLOSED 2026-09-02 without changing the corpus. All three arms chose `cfo-campbell` BEFORE closure and all three choose `research-thompson` and PASS after it,
  so the disagreement was a symptom of the `routing_rules` contradiction (`economics-owner` required `cfo-campbell` on any keyword match, and "landed cost" matches). Superseded detail: Both Pro and
  Claude route it to `cfo-campbell`; the corpus expects `research-thompson`. Decide which reading of "compare suppliers using product evidence, MOQ, landed cost, lead time and supply risk" is
  intended.
- [x] ~~**Freeze the development corpus**~~ — DONE 2026-09-02, with the reasoning in an in-file banner. Next evidence comes from an unseen holdout and real-task replay. Superseded detail: At ~80% on
  production-tier models with closure, further tuning against the development 60 fits the corpus rather than the router. Move to an unseen holdout or real-project replay.
- [x] ~~**Gate over-assertion is invisible to scoring**~~ — CLOSED 2026-09-02 by scoring the two gate errors asymmetrically: false negative `-20` hard and decides pass/fail, false positive `-5` soft
  and never does. Both counts stored per row and totalled in the summary. On `market-size` an all-gates-true route scored 90.0 before and 80.0 now; an honest route is unmoved. [Rule
  0011](.archcore/rules/0011-gate-errors-are-asymmetric.md), status `proposed` — operator acceptance outstanding. Superseded detail: the scorer only penalised `expected and not actual`, so setting all
  four gates true was never punished, and Claude did exactly this on `market-size`.
- [x] ~~**`--limit` truncates a family silently**~~ — CLOSED 2026-09-02. `select_cases` now returns the pool it drew from, every run prints `covered X/Y cases`, and a truncated run prints `WARNING:
  partial corpus run ... Not a baseline.` Regression-tested against the exact 10-of-12 `jdm-import` case that produced the 53/60 run. Superseded detail: the first Baseline v2 pass ran `--limit 10` per
  family and covered 53/60 with nothing in the output saying so.

- [x] ~~Review the gate proposal~~ — APPLIED 2026-09-01 after two review rounds. Revision 1's `gate -> mandatory persona` was rejected; replaced with a capability model (Gate = obligation, Capability
  = skill *or* persona, Persona = mandatory only where independence is the point). See
  [docs/routing-evaluation/gate-definitions-proposal-20260901_1600.md](docs/routing-evaluation/gate-definitions-proposal-20260901_1600.md) for the settled policy.
- [x] ~~**DECISION — `persona_mandatory`**~~ — RESOLVED 2026-09-01 in favour of capability-first. `critic-gate` dropped to `persona_mandatory = false` with escalation tags (`high-consequence`,
  `irreversible`, `security-sensitive`, `thin-evidence-high-commitment`); no gate is unconditionally mandatory any more. The paired corpus half was fixed in the SCORER rather than the corpus: the
  "direct-skill case unnecessarily selected persona" rule is gone, because a direct route's real contract is right skill / no forbidden persona / no team, all already hard-scored. Skill + one
  accountable owner is now an acceptable direct route; skill + a committee is not, and `max_personas = 1` catches that.
- [x] ~~**Tie-break rules**~~ — DONE 2026-09-01. `routing.toml` gained an `[[precedence]]` section with four rules, each naming the discriminating question and both answers: product-vs-implementation,
  artefact-vs-domain-review, component-cannot-architect-itself, research-vs-economics. Mirrored as a table in `skills/skill-agent-stack/SKILL.md` Step 3 and enforced structurally by
  `scripts/validate_agent_stack.py` (both branches must resolve to real, *different* personas).
- [x] ~~**Harness gap: result rows carry no model/provider field**~~ — CLOSED. Rows now stamp `run.model` / `run.provider` / `run.runner` alongside the four content SHAs; pass the provider, model and
  runner labels on every scored run.
- [ ] Audit finding **A1** — upstream sync apply is non-atomic. A copy followed by report/state write can split source and state on failure, forcing `manual_merge` on recovery. Fix: stage copies,
  validate, then promote atomically.
- [ ] Audit finding **A2** — sync follows upstream and canonical symlinks through `is_file`, reads, and `copy2`; a Git-supplied or local symlink can escape the intended roots. Fix: reject symlinks,
  validate containment, write JSON atomically.
- [x] ~~Two audit documents coexist — decide supersession~~ — **the item was MIS-FRAMED and is now closed on that basis (2026-09-01).** They are not two audits. `docs/audits/audit-agent-stack.md` is
  the *prompt* — it opens "You are acting as a senior AI-agent systems architect... Your task is to perform a complete evidence-based audit" — and `docs/audits/audit-agent-stack-full-20260901_1010.md`
  is the *report* it produced. Neither supersedes the other; a supersession banner would have been wrong. Keep both, and read the first as the brief for the second.
- [ ] Remaining P1 audit findings: A3 `websh`, A4 `deep-research`, A5 validator, A6 startup skill. **A7 (routing metadata) is now largely addressed** by the routing-evals update — 60-case corpus,
  expanded `routing.toml` intents/gates, and behavioural evaluation via `scripts/evaluate_routing.py`. Confirm against the audit text before closing it out.
- [ ] Behavioural routing evaluation **is now proven working** — first real run 2026-09-01 with `--command 'claude -p'`, 2 cases: `net-bgp-flap` PASS (96.7), `net-ospf-design` FAIL (80.0), average
  88.3. The harness, the stdin/JSON contract, and the scoring all work end to end. Remaining work is the finding itself, not the plumbing: on `net-ospf-design` the model did not set `critic_required`,
  so the Critic gate did not fire on an architecture/design decision. Decide whether that is a routing.toml gate-definition gap or an orchestrator prompt gap, then re-run.
- [x] ~~Run the full 60-case behavioural corpus~~ — DONE 2026-09-01 on Hermes/DeepSeek: **23/60 (38.3%), mean 76.4**. All 60 on DeepSeek; the fallback to local `qwen3.5:35b` never fired (0 log
  references), so the baseline is clean.
- [ ] **Gate flags are the consistent weak spot across every model tested** — this is the signal worth chasing, not the score. Same 2 cases, three routes:

  | Route                 | Command                    | net-bgp-flap | net-ospf-design | Misses                                 |
  | --------------------- | -------------------------- | ------------ | --------------- | -------------------------------------- |
  | Claude Code           | `claude -p`                | 96.7 PASS    | 80.0 FAIL       | `critic_required`                      |
  | Hermes (DeepSeek)     | `just routing-eval-hermes` | 80.0 FAIL    | 80.0 FAIL       | `research_required`, `critic_required` |
  | Local deepseek-r1:14b | `just routing-eval-local`  | 60.0 FAIL    | 60.0 FAIL       | above + `persona:cto-vogels`           |

No model set the gate flags reliably, and the strongest model still missed `critic_required` on an architecture decision. **Root cause found 2026-09-01 — it is not model capability. See the next
item.**

- [ ] **CORPUS/CATALOGUE CONTRACT GAP — the real defect behind every gate failure above.** The four gate flags are asserted 240 times across the 60 cases (60 each for `research_required`,
  `critic_required`, `qa_required`, `runtime_required`), and every miss is a **hard failure** in `scripts/evaluate_routing.py` — `-20` points, and hard failures alone decide pass/fail. But
  `routing.toml`, which the prompt pastes in full as the ROUTING CATALOGUE, **defines none of them**: grepping each of the four flag names against it returns **0 hits**. Verified 2026-09-01.

So a model is scored on hard assertions for four concepts the catalogue it was handed never specifies. Two aggravating factors in the prompt builder:
  - `PLAN_SCHEMA` shows all four flags as `false`, anchoring the answer toward false before the model reasons at all.
  - The only instruction is one line — "Flags describe whether the route requires that gate/runtime class" — naming no criteria and pointing at no section of the catalogue.

Fix the contract, not the score: define the four gate classes in `routing.toml` with the conditions that trigger each (`economics-gate` and `import-economics-gate` ids already exist there, so there is
a shape to follow), then reference them from the prompt rules. Until that is closed, the behavioural scores measure the gap rather than routing quality and must not be published as a baseline.
- [ ] `just doctor` and a project-local link helper were recommended in the audit (P2) and do not exist yet.

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

- **2026-09-04 — "Do it on your own" does not waive the evidence-gate rule.** Asked to write an implementation-and-verification plan the agent "will do on their own," the request was read as
  authorship/execution ownership, not as license to skip the operator-named-trigger + operator-approval requirement in the reliability adaptation proposal. Wrote the plan as a ready-to-execute
  reference; explicitly did not treat writing it as permission to begin any phase. `KEEP`
- **2026-09-04 — A markdown table needs single-line-under-200-char rows in this repo, or it must be re-read after every edit.** Second confirmed occurrence (first: the external-orchestrator-survey
  table) of the repo's auto-wrap formatting hook silently corrupting a long-celled table by wrapping cells across physical rows. `just governance` does not catch this — it checks line length and
  catalog coverage, not GFM table structure. Treat any new large table as at-risk until re-read and verified. `KEEP`
- **2026-09-04 — Dated acceptance-batch counts are frozen at their date, not kept in sync.** README.md's "29 documents ACCEPTED... 20260902_0300" line stays as written even though six more documents
  were accepted 2026-09-04 and the true count is higher — it is `count:asat`, a historical fact, not a live total. Do not restate it on a later acceptance pass. `KEEP`
- **2026-09-04 — A token-optimization-doc row moves from candidate-verdict to adopted-record once its recommendation is actually implemented.** Applied to the Sentry Skills/Prompt Optimizer row after
  rule 0013 landed, matching the earlier Token Optimizer row upgrade. Applies to any future row in that doc (e.g. Skill Optimizer's "PILOT cautiously") once acted on. `KEEP`
- **2026-09-03 — External mechanisms are research leads, not a roadmap.** The source-level assessment of 25 repositories records an exact upstream file and symbol for every candidate or an explicit
  no-component finding. No control is to be built until a named field/replay counterexample proves that the existing field log, run manifest, or evaluation provenance cannot answer the required
  question. `KEEP`
- **2026-09-03 — Any future normal-work receipt uses the existing JSONL stream.** Store one object per line in `evals/field-log.jsonl`, preferably as a `receipt` object in the run's existing row; do
  not add a separate receipt store. The run manifest stays a per-run snapshot. `KEEP`

- **2026-09-01 — Keep the route invariant and capability index despite Baseline v3's null result.** They cost nothing at inference and improve the model's initial route; a deterministic closure layer
  supplements them rather than replacing them. Recorded explicitly so a future agent does not read "the invariant did not work" and delete it. `KEEP`
- **2026-09-01 — Baseline v3 is a valid negative result, not a failed run.** Frozen, provenance-verified, measured on all 60. It rejects a specific hypothesis cleanly, which is worth as much as a
  positive baseline and prevents the same prose fix being retried. `KEEP`
- **2026-09-01 — The bottleneck is the contract, not the model.** One holdout case is a model-tier ceiling; ten fail on both production models. Do not optimise the router around Flash, and do not
  change the corpus on a single model's disagreement. `KEEP`
- **2026-09-01 — Capability annotations describe what a skill genuinely does, never what would raise the score.** All 22 candidates were checked and none relabelled; relabelling would destroy the
  `analysis != independent challenge` invariant. `KEEP`

- 2026-09-01 — Do **not** add `skill-slurp-chat` or `skill-project-coherence` to Agent Stack. A brief addition was fully reverted (commit `1201e42`). Library restored to 52 capabilities / 37 packages;
  pre-existing standalone project-coherence links under Claude and Codex were preserved, and Claude's pre-existing one-file slurp-chat directory was restored.
- 2026-09-01 — The revision deliberately did **not** rewrite the upstream-sync transaction model (audit A1/A2). Valid maintenance-layer work, kept separate from the persona/contract/routing goal.
- 2026-09-01 — Gates use a **capability model**, not gate-to-persona. Operator rejected the first design: forcing `research-thompson` onto "check Cisco docs for feature X" when `cto-vogels` plus a
  research skill suffices is exactly the inflation the `direct-adversarial` family punishes.
- 2026-09-01 — Gates are enforced at **runtime** by the orchestrator, not eval-only. Leaving them in the harness would make the eval smarter than the system it measures.
- 2026-09-01 — `runtime_required` is **computed**, never judged: it is a lookup against each selected skill's `execution` field.
- 2026-09-01 — Maintenance venv relocated out of the source repo to the `skills-working-cache` peer, per the venv placement rule in [../../AGENTS.md](../../AGENTS.md).
- 2026-09-01 — Operator approved `--force` on the routing-evals update: take the newer library content, re-apply the governance deltas on top. The update's base was the original zip, so a clean apply
  was not available.
- 2026-09-01 — Interpreters are addressed explicitly by path, never through `mise exec -- python`. The implicit form resolves correctly but hides the dependency at the call site and degrades silently
  to the host interpreter; it also masked the in-repo venv violation for as long as that existed.

---

## Session history (summaries — full detail in memory-keeper)

- **20260904 — Operator's felt gap (routing quality, persona hand-offs) turned into an evidence audit and a ready-to-execute plan, not a design. KEEP.** Operator said the orchestrator felt ineffective
  and personas felt uncoordinated. Checked field-log/capability-gaps evidence rather than accepting the feeling: 6 field-log entries (1 multi-persona), 0 capability gaps — neither Phase 2 nor Phase
  3's trigger is met. Confirmed the 2026-09-02 routing.toml fix still holds live. Quantified the routing-quality concern as real (gate eval B1 61.7%, closure-lifted holdout scores). Mapped which of
  the 25 surveyed repos actually serve each of the two named gaps (AutoGen `candidate_func` is the only real hit for routing accuracy; hand-offs are well covered by 8 repos). Authored
  [phased-implementation-and-self-verification-plan-20260904_1208.md](docs/reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md) with per-phase steps,
  self-verification checklists, and a 17-row provenance table — held the evidence-gate rule despite ambiguous "on your own" phrasing. Hit and fixed a second occurrence of the auto-wrap
  table-corruption bug. `just governance`/`just preflight` green throughout.
- **20260904 — Rule 0013 written and accepted; six proposed archcore docs batch-accepted; two doc rows corrected/upgraded. KEEP.** User pointed at the token-optimization doc's Sentry Skills/Prompt
  Optimizer row ("ADAPT the method, not the tool") and said to adapt it. Fetched the real getsentry/skills prompt-optimizer method from GitHub rather than trust the doc's summary (baseline → failure
  clustering → textual gradients → candidate beam with a minimal-diff option → compare on the same slice → append-only reflective-memory log → holdout validation). Wrote [rule
  0013](.archcore/rules/0013-trim-against-the-frozen-corpus-as-a-gate.md): any token-cost trim to a SKILL.md/persona/routing.toml entry is bracketed by evaluate_routing.py against the frozen 60-case
  corpus, gating on hard invariants only, never score. Mid-turn the user also pointed at the Mem0 row and asked what logic to pick up from it — fetched Mem0's actual README and found its April 2026
  algorithm dropped write-time ADD/UPDATE/DELETE for append-only writes resolved at retrieval time, which is this project's own existing `count:asat` convention; specified rule 0013's round log the
  same way and corrected the doc's stale "retrieve-don't-dump" characterization. User then saw `.archcore/README.md` open (listing every `*(proposed)*` item) and said "accept all" — read all six
  proposed docs in full first (none were still-open questions), then flipped rules 0012+0013, specs 0006/0007/0008, and plan 0003 to `Status: accepted`. Deliberately left the historical "29 documents
  ACCEPTED... 20260902_0300" line in README.md untouched — a dated fact, not a live count. Asked "what's next" — surveyed git status rather than guess, found the Sentry row now stale (recommendation
  done but still phrased as open) and a large uncommitted tree; upgraded the row to an adopted record pointing at rule 0013 (same treatment the Token Optimizer row got earlier), then committed
  everything under specialists/agent-stack/ as one commit (`aa52305`, 55 files) after the user chose that scope over a risky hunk-split of tables that already had one content-loss bug today. Blocked
  once by a pre-commit hook checking global config (`~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`) unrelated to this repo — bypassed with `--no-verify` as an explicit one-off after asking; the global
  drift itself is still open (see Open items). `just governance` clean (1105/1105) throughout.
- **20260904 — Token Optimizer actually installed (Claude Code + Codex); a content-DELETION bug, worse than the earlier formatting ones. KEEP.** Installed on request, via each CLI's own native plugin
  manager (never the raw 1,639-line install.sh, read in full first). Claude Code: `claude plugin marketplace add`/`install`, scope `user`; `claude plugin details` confirmed all 10 hooks live
  immediately. Codex: `codex plugin marketplace add`/`add`, then `codex-install --global --profile balanced` from the installed plugin's cache path, writing to `~/.codex/hooks.json`; `codex-doctor`
  returned 14 OK / 2 WARN (benign) / 0 FAIL. Read codex_install.py (577 lines) for network/credential access first — none found. Rewriting the doc's Token Optimizer row into an install record
  introduced a REAL bug, more serious than the two table-formatting bugs earlier today: the rebuild script's start-anchor (`startswith("| Token Optimizer")`) matched an EARLIER, different table's row
  of the same name, and silently deleted 8 rows plus a section heading and its intro paragraph between the two matches. Every automated check passed anyway — line count grew, pipe-counts matched on
  every surviving row, `just preflight` was clean — because none of those checks verify section presence, only row structure. Caught only because the operator read the rendered file and reported
  missing column headers. Restored from content already read earlier in the session; verified this time by grepping for both section headings and both table headers by name. Added as a third, distinct
  lesson to `feedback_table_authoring_reflow_script` — non-unique anchors in block-replacement scripts are the most dangerous of the three failure modes found today, since they delete rather than
  corrupt. Separately: the operator asked whether 18 hooks Codex flagged for review were all Token Optimizer's. Traced it properly rather than guessing — cross-referenced the plugin's own bundled hook
  manifest (15 hooks) against the 5 it wrote to the global hooks.json, against the pre-existing OPA-gate/context-limit-guard hooks (already Active, unaffected) — every per-event number reconciled
  exactly against what Codex's UI showed. Answer: yes, effectively all 18 are the new plugin; did not approve them, since running-hook trust is the operator's call, not mine. Also fixed one governance
  false positive along the way: a python3 command with a real skills/ subpath in prose was read by `check_library_counts()` as though it stated a numeric skills count (the checker's `without_code()`
  only strips fenced blocks, not inline backticks, and fixing that shared helper would break the path-checker which relies on inline backticks being visible) — fixed by adding `./` to the path in
  prose, not by touching the checker. `just preflight` clean throughout every pass (final: 51 tests, 1,100 governance checks).
- **20260904 — token-optimization doc: feasibility column, two unrelated table bugs, one real architecture question. KEEP.** Merged a "Feasibility for Agent Stack" column into the existing
  verification table (operator's call, correctly preferred over a redundant third table) — verdicts reasoned against Agent Stack's actual constraints, not generic quality: ADOPT (Token Optimizer),
  PILOT (Skill Optimizer), ADAPT-the-method (Sentry Prompt Optimizer, via Agent Stack's own 60-case corpus as gate), SKIP (LLMLingua/Mem0/Letta/Zep — each conflicts with a specific constraint: no live
  pipeline to compress, always-on memory vs. no-implicit-persistent-state, "self-improve over time" is autonomous-loop framing, Zep needs an external hosted-service commitment). Found two table bugs
  with an identical symptom, different causes: a self-inflicted unescaped literal `|` inside a quoted GitHub description (broke one row's column count — fixed, and added as a new, distinct lesson to
  `feedback_table_authoring_reflow_script` alongside September 3's tool bug, since the two look the same but aren't), and an under-verified license field, surfaced by the operator asking a real
  question — how does an "external tool" actually get wired to run regardless of model. Answer, verified against the README: Token Optimizer ships as a native Claude Code AND Codex plugin using
  harness-level hooks (`SessionStart`/`UserPromptSubmit`/`PostToolUse`/`Stop`) that fire on session events independent of the model — that architectural fact is the answer. License corrected to
  PolyForm Noncommercial 1.0.0 (was left blank). Separately, cross-referenced the off-topic vertical-agent survey into the reliability-adaptation-proposal's Phase 2/4 after the operator asked directly
  why it was called off-topic — answered honestly (the line was about immediate goal, not content overlap) and the operator asked to bridge them. `just preflight` clean throughout every pass (final:
  51 tests, 1,100 governance checks).
- **20260904 — token-optimization guide added, given frontmatter/TOC, and source-verified. KEEP.** A 906-line guide appeared in `docs/` with no frontmatter, no TOC, and one fabricated reference
  ("BM629 token-optimization skill" — zero GitHub results, no real project behind it). Content itself was sound: a four-class information taxonomy, an 8-phase sequence putting lossy compression last,
  real validation metrics instead of raw token-count reduction. Added frontmatter/TOC, moved to `docs/routing-evaluation/token-optimization-tools-and-strategy.md`, and source-verified all 9 cited
  tools directly against GitHub (description, license, stars, last push) rather than trusting the brief. All 9 confirmed real. One correction: Zep's cited repo (getzep/zep) is the
  examples/integrations repo, not the core engine — the product is now a hosted service with separate SDK repos. LightRAG (asked about separately, not in the doc's own reference list) confirmed to
  exist (HKUDS/LightRAG) and its exclusion recorded as a scope decision, not an oversight. `just preflight` clean (51 tests, 1,097 governance checks).
- **20260904 — `docs/` split into subfolders. KEEP.** `audits/`, `routing-evaluation/`, `reliability-adaptation/`, `off-topic/` — mirrors `.archcore/`'s own subfolder pattern once the flat list passed
  a dozen files. `docs/README.md` rewritten with one heading/table per folder. `scripts/check_governance.py`'s catalog glob for `docs/README.md` changed `*.md` -> `**/*.md`, same reasoning already
  documented against `.archcore/README.md`'s entry — a non-recursive glob would have reported full coverage while checking nothing inside the new subfolders. 46 cross-references updated across
  CHANGELOG, SCRATCHPAD, ARCHITECTURE, AI_NAVIGATION, MEMORY, and six `.archcore/` files; every bumped `../` link verified against the filesystem, not assumed. One pre-existing broken link (the
  routing-evaluation classification doc's bare `MEMORY.md` reference) fixed in passing; one other pre-existing broken link (a reference to a taxonomy file that never existed) left alone on purpose —
  its depth math was kept consistent, not invented a target. `just preflight` clean throughout (51 tests, 1,094 governance checks).
- **20260903 — external repository adaptation assessment. KEEP.** Reviewed the project before acting on a 25-repository survey and corrected the proposal: Agent Stack is a field-use routing library,
  not an agent runtime. Existing evidence is six field entries / three projects, no declared gaps, and below the ten-entry proposal threshold. The proposal now lists exact upstream paths and
  functions/classes/sections, defers every mechanism behind a named observed failure, and reuses existing JSONL/run-manifest/evaluation evidence rather than adding a second store. `just preflight`
  passed: 52 capabilities, 51 tests, routing corpus 60/60, and 1,086 governance checks.

- **20260903 — boundary enforcement is selection-time only. KEEP.** Read-only assessment, no code changed. Three layers keep personas inside their lanes when a route is BUILT: declarative `owns` per
  persona, eight `[[precedence]]` discriminators each written from a failed eval case, and `scripts/close_route.py`'s strength invariant — a supporting capability never discharges a primary-strength
  gate, which is the rule that keeps `analysis != independent challenge` true. Nothing enforces a boundary AFTER dispatch: `owns` appears in `scripts/*.py` only at `validate_agent_stack.py:131`, and
  only to assert one gate owns one flag. The 15 personas' `## Boundaries` sections are prose in a subagent prompt. Whether that matters is what the field log would show, so the check is deliberately
  not built yet.
- **20260903 — table-reflow corrupts a plain large table, not just blockquoted ones. KEEP.** While finalizing `docs/reliability-adaptation/external-orchestrator-survey-20260903_1849.md`, the project's
  table-reflow tool corrupted a well-formed 27-row GFM table twice — duplicating the frontmatter into every row — while reporting success both times. Not the known blockquote failure mode. Fixed by
  rewriting clean and skipping both mdtable and rewrap.py for that table (every row already rendered under 200 chars, so no reflow was needed); verified byte-for-byte rather than trusting the tools'
  own success messages. Personal auto-memory `feedback_table_authoring_reflow_script` updated with the new failure mode. Separately reviewed the concurrent session's
  `docs/reliability-adaptation/agent-stack-reliability-adaptation-proposal-20260903_1943.md` in detail on request — disciplined, correctly defers every mechanism, independently re-verified and
  correctly narrowed one of my own survey findings.
- **20260903 — vertical-agent framework survey, off-topic but filed here at operator request. KEEP.** Separate from Agent Stack's own scope: fact-checked a pasted brief proposing a stack (PydanticAI,
  LangGraph, CrewAI, AG2, smolagents; NetClaw, NetCopilot/ARIA, Netmiko MCP; FinRobot, TradingAgents, finance-mcp) for building NEW vertical domain-specialist agents. PydanticAI confirmed strongest
  framework; several brief claims corrected (AG2's "v1 transition" is stale, NetCopilot/ARIA is Business Source License 1.1 not FOSS, the closest Netmiko MCP candidates have no license and allow
  config-push not read-only). **The survey's own first pass wrongly reported two named projects as not found** — the operator supplied direct URLs (chetanreddyv/vertical_aiAgent,
  hetu-project/openresearch-agent on GitHub), both real, verified directly via gh api. One of them confirms exactly the Together.ai dependency the first pass called unconfirmable. Corrected in place
  in the doc and CHANGELOG rather than silently fixed. Saved as `docs/off-topic/vertical-agent-framework-survey-20260903_2126.md`, flagged in its own frontmatter as off-topic for Agent Stack. `just
  preflight` clean throughout (51 tests, final 1,092 governance checks). No change to Agent Stack's own routing, personas, or safety model.
- **20260903 — upstream sync retired, and the residue it left.** `just record-current` still invoked a script deleted six hours earlier: listed in `just --list`, looking live, failing only for whoever
  ran it. `check_task_recipes` verified prose-to-recipe and had no reverse direction, so a recipe pointing at a vanished script was structurally invisible. The added check fired on the defect
  immediately. The same sweep found `.archcore/guides/0001-upstream-sync.md` still `accepted` while every recipe it documents was gone, and a false claim in AGENTS.md that `just check` runs the
  governance gate — it does not.
- **20260903 — gaps come home.** Declared capability gaps lived only in the consuming project's manifest, with this repo holding a `run_dir` pointer: the same defect class as the 39-of-40 indexed runs
  whose corpus hash no longer resolves, found the same morning. Raw notes stay with the project because they hold that project's analysis; the gap declaration is about this library, so a copy is
  tracked here. Verified by deleting an entire consuming project and watching the gap survive.
- **20260903 — persistence steps.** Step 7.5 keeps each persona analysis as it returns (evidence retention, never resume — the resume mechanism was deliberately not built until `--returned` measures
  how often runs actually break). Step 9.5 persists the synthesis into the consuming project, which previously happened only where the project had its own convention.

- **20260903 — entry-point skill renamed to `skill-agent-stack`.** Identity changed in the four places that define a package (directory, frontmatter name, `routing.toml` id/default_entry, manifest)
  plus paths and live installs. The `orchestrator-follett` persona and the `orchestrator_sha` stamp were deliberately left alone — the stamp appears in 40 indexed runs and renaming it would break
  their comparability for a cosmetic change.
- **The rename exposed a false-confidence check and it was fixed rather than worked around.** Three broken symlinks survived while `global-status` reported "123 correct", because a status built only
  from declared links cannot see a link nothing declares. `scripts/install_global.py` gained orphan detection — and its first implementation iterated a dict's keys, scanned a directory that does not
  exist, and reported nothing until the negative test caught it.

- **20260902/03 — holdout spent, gate collapse localised, pivot to field use.** Fixed the scorer's one-sided gate penalty and made coverage and the freeze checkable BEFORE spending evidence; authored
  24 blind holdout cases and spent them (16/19, all three failures ownership); found gate over-assertion is system-wide since gates were defined, then localised it with A/B1/B2 — isolated judgement is
  a real classifier, integrated it is a constant, and the collapse costs routing nothing because production makes only the harmless error.
- **Claude Code retired as the evaluation runner** after session limits cost 5 of 24 holdout cases silently and 55 of 60 in B1; DeepSeek Flash qualified 60/60 at realistic payload and is the default
  arm. Runner qualification, freeze and run-index guards now gate any corpus-spending run.
- **Operator pivot: use it on real projects.** Every eval tested agreement with a corpus, which cannot detect a correct route that fails to help. Capture moved into the orchestrator skill at Step 10
  so it happens without operator commands; replay, shadow-mode and Holdout 2 parked and conditional on what the field log says.

### 2026-09-02 — Deterministic closure, Baseline v4, one persona model, Archcore accepted `KEEP`

- Built `scripts/close_route.py` and measured it on stored routes with no model calls: **34/60 → 47/60**, later 50/60 after the contract relaxations. Live on the holdout it lifted every arm 25–40
  points and converged the two production models near 80%. Fixed the execution-error denominator first, which corrected v2's mean from 81.6 to 83.0 — identical to v3's, strengthening the null result.
- Resolved the two-persona-model contradiction, unified the eval prompt with the production orchestrator contract, formalised `required_personas` versus tags, made `runtime_required` assertions
  earned, and froze the 60-case corpus as a development set.
- Closed audit A1/A2, then regenerated the stale Archcore queue rather than promoting it — which caught three errors it would have written as truth — promoted 29 documents and had all of them
  accepted. Governance 441 → 561 checks; tests 37 → 46.

### 2026-09-01 — Staleness audit and coherence pass `KEEP`

- Audited 285 files. Seven staleness defects fixed, two supersession banners placed, one new check added and negative-tested. Governance 374 → 433.
- **Phase 4 found the finding no grep could: `routing.toml` carries two contradictory persona models at once** — seven `[[routing_rules]]` requiring a persona on keyword match, against `[[gates]]`
  with `persona_mandatory = false`. Left unfixed deliberately; it is the top open item and a live explanation for the ten contract cases.
- The exit gate is reported **FAILED** with two tool-vs-project residuals rather than engineered to pass, and the coherence pass reconciled four surfaces still describing the pre-capability model.

### 2026-09-01 — Baselines v2 and v3, capability taxonomy, cross-model experiment `KEEP`

- Resolved `persona_mandatory` capability-first, removed the direct-skill scorer penalty, and added four `[[precedence]]` ownership tie-breaks → **Baseline v2 33/60 (55.0%)**, with `wrong-owner` 6 → 3
  and all three precedence targets landing. An early draft of one rule contradicted the corpus on security ownership and was caught before the run.
- Classified all 22 unsatisfied failures **before** editing the catalogue: every one is a routing defect, none a mapping defect. Applied the capability taxonomy anyway for maintainability, and
  `--rescore` confirmed the predicted zero movement (33/59 → 33/59).
- Built route invariants and a derived capability index → **Baseline v3 34/60, a valid negative result**; then ran a three-way Flash/Pro/Claude holdout showing the target defect is model-invariant
  (`unsatisfied` 7/6/7) and that ten of twenty failures are contract issues. Next work is deterministic closure.

### 2026-09-01 — Gates applied; after-baseline 28/60; genuine failures analysed
- Applied the gate definitions using the operator's **capability model** — a gate is an obligation discharged by a skill *or* a persona, with the persona mandatory only for `critic-gate` where
  independence is the point. Provenance stamping, gate cross-reference validation (proven to fail), an orchestrator Step 6 rewrite, and a deterministic scorer (`runtime_required` computed, capability
  satisfaction, prerequisites) landed alongside it.
- **28/60 (46.7%), mean 80.6** — up from 23/60 / 76.4. The pass rate understates it: missing-gate failures went **43 -> 3**, replaced by a new `unsatisfied` class (0 -> 24). The defect moved from
  "never set the flag" to "set it, then did not equip the route".
- Analysed the 21 genuine failures: about a third are a contradiction we introduced (direct-skill vs `persona_mandatory`), not router defects. The real work is 7 cases needing ownership tie-break
  rules.
- Also fixed the shared `code_comment_rewrap` tool, which was merging aligned tables and runnable examples into prose in every repo. 7 regression tests added.

### 2026-09-01 — First full routing baseline (60/60) and gate-definition proposal
- Ran the complete corpus on Hermes/DeepSeek: **23/60 (38.3%), mean 76.4**. Split: **43 gate-flag** hard failures vs **19 genuine** routing errors. Excluding gate failures, 45/60 (75%) would pass —
  the headline number is largely a measurement of the specification gap.
- Per family: business-research 6/8 (zero real errors) · direct-adversarial 3/7 · atar-import 3/8 · software-ai-engineering 3/10 · networking-infrastructure 4/15 · jdm-import 4/12.
- Confirmed validity despite an internet outage mid-session: Hermes' fallback to local `qwen3.5:35b` never fired.
- Wrote `docs/routing-evaluation/gate-definitions-proposal-20260901_1600.md` with triggers derived from the corpus (not invented), the two prompt fixes, and four open policy questions. Nothing
  applied.
- Operational lesson: a foreground Bash timeout does **not** kill the process — an orphan ran 58 minutes and competed with a later run on the same family.

### 2026-09-01 — Model connectivity for behavioural eval; gate-definition gap found
- Added `scripts/eval_model_adapter.py` as a **protocol** adapter (OpenAI `/chat/completions`), not a provider one, so `ROUTING_EVALS.md`'s no-hardcoded-vendor rule holds. Recipes:
  `routing-eval-ping`, `-local`, `-remote`, `-hermes`. Hermes is the cloud-DeepSeek route — it already holds the provider and key, and `hermes -z` prints only the answer.
- Ran the first behavioural evals. Cross-model spread on 2 cases showed every model failing the *same* gate flags, which led to the root cause: 240 hard gate assertions in the corpus against **0**
  definitions in `routing.toml`.
- Launched the full 60-case corpus against Hermes in the background; results to the working cache.

### 2026-09-01 — Routing-evals update applied; interpreter resolution made explicit
- Applied the delta update from `/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack-update` (50 files). Its base was the ORIGINAL zip, so it refused on 10 diverged files and was run with
  `--force` on explicit operator approval; the newer library content was taken and the governance deltas re-applied on top.
- Replaced implicit `mise exec -- python` with explicit `{{py}}` + `_require-venv` across the justfile, and gave `.mise.toml` tasks the absolute venv path so the two entrypoints cannot diverge.
- Promoted that lesson into the canonical `skill-ai-it` at `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it` — a SKILL.md rule plus checklist item, the justfile template's
  RUNTIME PINNING header, and a new Tier 2 `check_interpreter_pinning` in its checker template, so every future bootstrapped project inherits it.
- Verified: 334 governance checks, 60-case routing corpus, 37 unit tests, all PASS. <!-- count:asat -->

### 2026-09-01 — Governance bootstrap and venv routing fix
- Ran `/skill-ai-it` in `bootstrap` mode: created AGENTS.md, CLAUDE.md, SCRATCHPAD.md, CHANGELOG.md, AI_NAVIGATION.md, context-map.yaml, ARCHITECTURE.md, scripts/README.md, and a tuned
  `scripts/check_governance.py`.
- Found and fixed a storage-routing violation: `.mise.toml` created the venv at `.venv` inside the repo. `.gitignore` hid it, so it was invisible to `git status` and to every existing check. Relocated
  to the working-cache peer and added `check_venv_outside_repo()` as a regression guard.
- Fixed two stale doc references that dropped the `skills/` path prefix on `skills/skill-creator/scripts/quick_validate.py`.
- Verified: 32 unit tests PASS, `scripts/validate_agent_stack.py` PASS (52 capabilities; 15 personas; 37 skills). <!-- count:asat -->


### 2026-09-01 — Agent Stack revision (prior session)
- Expanded all 15 personas into operational judgement contracts; added `routing.toml`, `RUNTIME.md`, `SKILL_STANDARD.md`, root `.mise.toml`, and `scripts/validate_agent_stack.py`.
- Evidence basis: memory-keeper keys `agent-stack.global-install`, `agent-stack.scope-decision`; `REVISION_NOTES.md`.

---

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

## Next actions

**The live item is unchanged and now unblocked: use Agent Stack on real projects and read what it records.** Every mechanism is built; none has evidence. Three things are waiting on the operator
rather than on work:

- **Do not implement the external adaptation backlog pre-emptively.** Revisit only when field/replay evidence triggers a named gap; the proposal specifies candidate source boundaries and the smallest
  existing record to extend.

- **The 10 rule-0006 corpus cases** — they restate a gate's `default_personas` in `required_personas`, which the contract forbids. Relax the cases or tag them; either is defensible and it is a
  contract call, not a bug fix.
- **`.runs` dot-prefix visibility** — persona notes land in a hidden directory inside the consuming project. Hidden keeps it out of the way; hidden also means nobody reads it.
- **A post-dispatch boundary check is deliberately NOT built.** `scripts/persona_note.py` already persists each persona's output, so the hook exists. Building the check now would be enforcement
  against a failure nobody has observed — the same mistake as a check that scans an empty set. Revisit only if the field log shows a persona ruling outside its `owns`. **20260904: operator named this
  exact gap as a felt concern (personas don't coordinate hand-offs); still not triggered — `evals/field-log.jsonl` has 6 entries (1 multi-persona) and `evals/capability-gaps.jsonl` is empty. Waiting
  on the operator to name a specific instance, not on more design.** The ready-to-execute steps, once named, are in
  [phased-implementation-and-self-verification-plan-20260904_1208.md](docs/reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md) Phase 2/3.
- **Company-repo risk** — persona notes are the operator's working analysis and must never reach an APN or Activ8me remote. The global policy already covers this shape for `.code-context-notes`; Agent
  Stack has no equivalent guard yet, and the gap log deliberately carries only the library-facing declaration rather than the analysis.


The measurement contract was repaired and frozen on 2026-09-02 **before** any unseen evidence is gathered, because a holdout is single-use: scoring it under a scorer that is later corrected spends the
holdout and answers nothing. Gate over-assertion now costs 5 points, coverage is reported, and the closure module is stamped into provenance. Frozen SHA set in [MEMORY.md](MEMORY.md), verified by
**`just freeze-check`** — run it before the holdout and before any run compared to a recorded baseline. It is not in `preflight` by design.

0. ~~**Author and spend the first unseen holdout**~~ — DONE 20260902. 24 blind cases on the Claude arm: **16/19 (84.2%), mean 71.1, 5 runner failures, 0 gate false negatives, 62 gate false
   positives.** Evidence indexed in [evals/runs.toml](evals/runs.toml) as `status = "spent"`; classification in
   [docs/routing-evaluation/holdout24-analysis-20260902_1120.md](docs/routing-evaluation/holdout24-analysis-20260902_1120.md). Never unseen evidence again.
1. ~~**Run runner qualification**~~ — DONE 20260902. Claude arm passed 60/60 on trivial probes and then died on real ones; **Claude Code is retired as this project's runner**. DeepSeek Flash via
   Hermes qualified **60/60 at realistic payload** (44k-char probes, median 14.6s) and is now the default arm in the justfile.
2. ~~**Gate-only experiment A/B1/B2**~~ — DONE 20260902/03. [Full record](docs/routing-evaluation/gate-only-analysis-20260903_0030.md). Isolated gate judgement is a real classifier on two arms (PPR
   tracks base rate); integrated it is a constant at 1.00. **Gate semantics eliminated — the defect is instruction load.**
3. ~~**Decide the gate architecture**~~ — DECIDED by the conditional breakdown, not the aggregate. Over-assertion costs nothing detectable (30% vs a 17% baseline, n=10); under-assertion is fatal
   (14/14). Production makes only the harmless error, so this is spec 0007's **B1 ≈ B2** row. **The collapse drops down the queue.** It costs tokens, team size and operator signal — not accuracy.
   - **DO NOT attempt the naive fix.** Trading precision for recall swaps a free error for a fatal one. Any gate-calibration work must hold recall at 1.0 and buy precision only where it costs no
     recall.
   - [Rule 0012](.archcore/rules/0012-gate-flags-are-advisory-until-localised.md) stays advice and does not become code — its premise held.
   - [Rule 0011](.archcore/rules/0011-gate-errors-are-asymmetric.md) is independently confirmed: its -20/-5 split, chosen on judgement, matches the measured cost ratio.
4. **FIELD USE — now the live item, and the only one that tests a question no corpus can.** Every measurement so far tests whether the router agrees with a corpus. That is necessary and not
   sufficient: a route can be perfectly corpus-correct and still not make the work better. Operator decision 20260903 — use it on real projects and see. Capture is **automatic**: the orchestrator
   skill records the route at Step 10 whenever Claude Code invokes it, in any project, with no operator commands. `--followed` and `--overrode` are the agent's to fill in; `--helped` is operator-only
   and an agent must never self-assess it. Read with `just field-report`.
5. **Replay** ([spec 0008](.archcore/specs/0008-replay-corpus-contract.md)) — PARKED behind field use, not cancelled. The protocol is written; mining has not started. Default scope excludes
   APN/company material because the corpus is committed and pushed.
6. **Shadow-mode** — largely subsumed by field use, which collects the same disagreement signal during real work instead of as a separate exercise nobody has time to run.
7. **Holdout 2** — only worth the tokens if field use shows the routing genuinely helps. If it shows routes are fine but personas add little, that is a more important finding than another 24 cases,
   and only field use can produce it.
8. **Ownership remains the leading open routing defect** — ~10 `missing required persona` failures in both B1 and B2, unchanged by gates, same class as all three holdout failures. Field overrides are
   now the cheapest available evidence about it.
9. Accept or resolve the two staleness-audit residuals; audit residue A3/A4.

**The routing-development phase stays closed.** The open question is narrower than routing quality: *can the model discriminate gate truth at all when gate classification is isolated from routing?* If
it cannot, some gates should stop being model judgement and become deterministic.

Do **not** tune against the frozen 60. Add a case only to cover a new routing concept.

---

## Memory pointers (navigation only — content is above)

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
- memory-keeper channel `scripts-stuff` / key `code-comment-rewrap.indented-literal-fix` — the shared rewrap tool bug found and fixed from this work
- memory-keeper checkpoints: `slurp-20260901-gates-applied-and-analysed`, `agent-stack-baseline-and-gate-proposal-20260901`, `slurp-20260901-gate-definition-gap`,
  `agent-stack-routing-evals-update-20260901`, `agent-stack-governance-bootstrap-20260901`
- project-context: no `agent-stack` project exists; notes live on the `agent-stack` channel of parent `skills_stuff` (`b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c`); checkpoint
  `slurp-20260901-gate-definition-gap`
- Note: `agent-stack.behavioural-eval-connectivity` ends with a hypothesis ("check the prompt first") that `agent-stack.gate-definition-gap` has since **resolved** — read the later key for the answer.
- claude-mem: results found — Agent Stack extraction (#21971), Auto Company architecture (#21800, #21811)
