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
- [Next actions](#next-actions)
- [Memory pointers (navigation only — content is above)](#memory-pointers-navigation-only-content-is-above)

---

## Current state

**Phase:** Routing-development phase CLOSED. Deterministic closure is built and measured, the catalogue carries one persona model, the 60-case corpus is frozen, both P1 audit findings are shut, and 29
Archcore documents are accepted. The next evidence must come from outside this corpus.

**Where routing stands.** With deterministic closure the frozen 60 scores **50/60**, and live on the 20-case holdout: **Flash 13/20 (65.0%) · Pro 15/19 (78.9%) · Claude 16/20 (80.0%)** — every arm
25–40 points above the same holdout without closure, and the two production arms converged near 80%. The architecture is settled and measured rather than argued: **the model judges, the system
satisfies constraints.** Where a rule is a lookup against a finite catalogue, a program does it exactly and a model does it sometimes.

**What closed the loop.** Baseline v3 rejected prompt-only closure as a valid negative result; the three-way cross-model experiment showed the defect was model-invariant (`unsatisfied` 7/6/7); the
staleness audit then found the catalogue was asserting **two contradictory persona models at once**, which retroactively explained both the ten cross-model failures and the `atar-supplier` ownership
dispute. Resolving it, building closure, and unifying the eval contract with production were the three changes that mattered.

Agent Stack is the English-only extraction of Auto Company's personas and skill library, canonical at `/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack`. The 2026-09-01 revision expanded
all 15 personas into operational judgement contracts, added `routing.toml` as the routing catalogue, and added the `RUNTIME.md` / `SKILL_STANDARD.md` contracts. Library is 52 capabilities: 15 personas
+ 37 skill entries (36 packages plus the single-file `frontend-design`). A full repository audit sits in `docs/audit-agent-stack-full-20260901_1010.md` with a verdict of SOUND WITH MATERIAL GAPS; its
  P1
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
  = skill *or* persona, Persona = mandatory only where independence is the point). See [docs/gate-definitions-proposal-20260901_1600.md](docs/gate-definitions-proposal-20260901_1600.md) for the
  settled policy.
- [x] ~~**DECISION — `persona_mandatory`**~~ — RESOLVED 2026-09-01 in favour of capability-first. `critic-gate` dropped to `persona_mandatory = false` with escalation tags (`high-consequence`,
  `irreversible`, `security-sensitive`, `thin-evidence-high-commitment`); no gate is unconditionally mandatory any more. The paired corpus half was fixed in the SCORER rather than the corpus: the
  "direct-skill case unnecessarily selected persona" rule is gone, because a direct route's real contract is right skill / no forbidden persona / no team, all already hard-scored. Skill + one
  accountable owner is now an acceptable direct route; skill + a committee is not, and `max_personas = 1` catches that.
- [x] ~~**Tie-break rules**~~ — DONE 2026-09-01. `routing.toml` gained an `[[precedence]]` section with four rules, each naming the discriminating question and both answers: product-vs-implementation,
  artefact-vs-domain-review, component-cannot-architect-itself, research-vs-economics. Mirrored as a table in `skills/orchestrator/SKILL.md` Step 3 and enforced structurally by
  `scripts/validate_agent_stack.py` (both branches must resolve to real, *different* personas).
- [x] ~~**Harness gap: result rows carry no model/provider field**~~ — CLOSED. Rows now stamp `run.model` / `run.provider` / `run.runner` alongside the four content SHAs; pass the provider, model and
  runner labels on every scored run.
- [ ] Audit finding **A1** — upstream sync apply is non-atomic. A copy followed by report/state write can split source and state on failure, forcing `manual_merge` on recovery. Fix: stage copies,
  validate, then promote atomically.
- [ ] Audit finding **A2** — sync follows upstream and canonical symlinks through `is_file`, reads, and `copy2`; a Git-supplied or local symlink can escape the intended roots. Fix: reject symlinks,
  validate containment, write JSON atomically.
- [x] ~~Two audit documents coexist — decide supersession~~ — **the item was MIS-FRAMED and is now closed on that basis (2026-09-01).** They are not two audits. `docs/audit-agent-stack.md` is the
  *prompt* — it opens "You are acting as a senior AI-agent systems architect... Your task is to perform a complete evidence-based audit" — and `docs/audit-agent-stack-full-20260901_1010.md` is the
  *report* it produced. Neither supersedes the other; a supersession banner would have been wrong. Keep both, and read the first as the brief for the second.
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
| After-baseline      | 28/60 (46.7%), mean 80.6 — `after-<family>-20260901.jsonl` in the results dir                |
| Routing corpus      | 60 cases across 6 families in `evals/routing-cases.toml`; see `ROUTING_EVALS.md`                           |
| Eval results        | `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/routing-results/` (working cache, rebuildable) |
| Eval routes         | `just routing-eval-hermes` (cloud DeepSeek via Hermes), `routing-eval-local` (Ollama), `routing-eval-ping` |

---

## Recent decisions

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
- Wrote `docs/gate-definitions-proposal-20260901_1600.md` with triggers derived from the corpus (not invented), the two prompt fixes, and four open policy questions. Nothing applied.
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

## Next actions

The measurement contract was repaired and frozen on 2026-09-02 **before** any unseen evidence is gathered, because a holdout is single-use: scoring it under a scorer that is later corrected spends the
holdout and answers nothing. Gate over-assertion now costs 5 points, coverage is reported, and the closure module is stamped into provenance. Frozen SHA set in [MEMORY.md](MEMORY.md), verified by
**`just freeze-check`** — run it before the holdout and before any run compared to a recorded baseline. It is not in `preflight` by design.

0. ~~**Author and spend the first unseen holdout**~~ — DONE 20260902. 24 blind cases on the Claude arm: **16/19 (84.2%), mean 71.1, 5 runner failures, 0 gate false negatives, 62 gate false
   positives.** Evidence indexed in [evals/runs.toml](evals/runs.toml) as `status = "spent"`; classification in [docs/holdout24-analysis-20260902_1120.md](docs/holdout24-analysis-20260902_1120.md).
   Never unseen evidence again.
1. ~~**Run runner qualification**~~ — DONE 20260902. Claude arm passed 60/60 on trivial probes and then died on real ones; **Claude Code is retired as this project's runner**. DeepSeek Flash via
   Hermes qualified **60/60 at realistic payload** (44k-char probes, median 14.6s) and is now the default arm in the justfile.
2. ~~**Gate-only experiment A/B1/B2**~~ — DONE 20260902/03. [Full record](docs/gate-only-analysis-20260903_0030.md). Isolated gate judgement is a real classifier on two arms (PPR tracks base rate);
   integrated it is a constant at 1.00. **Gate semantics eliminated — the defect is instruction load.**
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
