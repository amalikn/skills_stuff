Title: Agent Stack Routing Memory
Category: project-memory
Status: current
Authority: local-supplement
Scope: Durable knowledge required before changing Agent Stack routing — architecture, settled decisions, measured baselines, metric definitions, and traps already hit
Last reviewed: 20260901_2015
Summary: What a future agent must know before touching the routing layer, including why each decision was made and which measurements are load-bearing.

# MEMORY.md — Agent Stack Routing

This is not a changelog and not a scratchpad. [CHANGELOG.md](CHANGELOG.md) records what happened on a date; [SCRATCHPAD.md](SCRATCHPAD.md) records what is live right now. **This file records what is
true and why, so that a change does not have to rediscover it.** Everything here has been measured or decided deliberately; where something is an assumption or a proxy, it says so.

## Contents

- [The routing model in four terms](#the-routing-model-in-four-terms)
- [Settled decisions and the reasoning behind them](#settled-decisions-and-the-reasoning-behind-them)
- [Measured baselines](#measured-baselines)
- [Metric definitions, and which ones have zero noise](#metric-definitions-and-which-ones-have-zero-noise)
- [Traps already hit](#traps-already-hit)
- [What is still open](#what-is-still-open)

## The routing model in four terms

Keep these distinct. Most routing defects in this project's history came from collapsing two of them.

| Term       | What it is                                                                | Where it lives                                                           |
| ---------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Gate**       | An obligation the task places on the route                                | `routing.toml` `[[gates]]`, four flags                                   |
| **Capability** | What can discharge an obligation, declared by the provider that has it    | `routing.toml` `[[capabilities]]`, referenced by skills, personas, gates |
| **Persona**    | Judgement ownership; mandatory only where independence is the deliverable | `routing.toml` `[[personas]]`, `personas/*.md`                           |
| **Skill**      | A repeatable procedure or tool                                            | `routing.toml` `[[skills]]`, `skills/*/SKILL.md`                         |

Three relationships follow, and each was a defect before it was written down:

1. **A gate is not a persona.** "This task needs research evidence" and "this task needs an independent Research persona" are different claims. Collapsing them causes persona inflation, which the
   `direct-adversarial` eval family exists to catch.
2. **A capability is declared once, on its provider.** Gates name a `required_capability`; they do not enumerate skills. The earlier `satisfied_by_skills` lists were a second copy of the taxonomy and
   could drift from the first.
3. **`primary` may discharge a gate; `supporting` never does.** This single rule is what keeps `analysis != independent challenge` true. Without it every skill that touches risk eventually reads as a
   critic and `critic_required` stops meaning anything.

Route validity is stated separately in `[[route_invariants]]`: a route that sets a gate true and closes it with nothing is **invalid**, not merely thin.

## Settled decisions and the reasoning behind them

Do not reopen these without new evidence. Each cost a measurement to settle.

| Decision                                                             | Why                                                                                                                           |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| No gate sets `persona_mandatory` unconditionally                     | The catalogue and the corpus instructed opposite behaviour on ~7 cases. Capability-first resolves it; escalation is per-gate  |
|                                                                      |   via `persona_mandatory_when_tags`                                                                                           |
| The scorer does not penalise a direct route for naming an owner      | A direct route's real contract is right skill / no forbidden persona / no team, all already hard-scored. The extra rule       |
|                                                                      |   punished one accountable owner as harshly as a committee                                                                    |
| Ownership ties are resolved by `[[precedence]]`, not by reading      | Overlapping ownership is normal for mixed work; what was missing was a discriminator. Encoded as a question plus both answers |
|   `owns` prose                                                       |   so the same task shape resolves the same way every time                                                                     |
| Security **posture** stays with CTO however code-shaped the artefact     | Corpus assigns `security-code-scan` and `net-security-review` to `cto-vogels`, `network-code-review` to `fullstack-dhh`. An   |
|                                                                      |   earlier draft of the rule contradicted this and was caught pre-merge                                                        |
| `runtime_required` is computed, never self-reported                  | It is a lookup against each selected skill's `execution` field, not a judgement. Models do it unreliably; a program does it   |
|                                                                      |   exactly                                                                                                                     |
| `unsatisfied` is deduplicated against `missing-gate`                 | A route that never set the flag will trivially also lack the capability. Counting both dropped the mean 10 points for no new  |
|                                                                      |   information                                                                                                                 |
| Capabilities are annotated on **every** provider, not only observed ones | An un-annotated provider silently provides nothing, which reads in a report as a model error rather than a catalogue gap.     |
|                                                                      |   Partial annotation is worse than none                                                                                       |

## Measured baselines

All on Hermes / DeepSeek `deepseek-v4-flash`, 60-case corpus. Provenance is stamped per result row.

| Run                | Result                                       | Mean                            | Note                                                                                           |
| ------------------ | -------------------------------------------- | ------------------------------: | ---------------------------------------------------------------------------------------------- |
| v1 first           | 23/60 (38.3%)                                | 76.4                            | Gates asserted by the corpus were undefined in the catalogue; 43 of 62 hard failures were gate |
|                    |                                              |                                 |   misses                                                                                       |
| v1 after gate defs | 28/60 (46.7%)                                | 80.6                            | Gate definitions applied. `missing-gate` 43 → 3, replaced by a new `unsatisfied` class         |
| **v2**                 | **33/60 (55.0%)** published · **33/59 (55.9%)**      | 81.6 published · **83.0** corrected | Precedence + capability-first gates + direct-skill scorer fix. One execution error (`ui-only`) |
|                    |   corrected                                  |                                 |                                                                                                |
| v2 re-scored       | 33/59 unchanged                              | —                               | Under the capability taxonomy. Zero cases moved: the refactor is behaviour-preserving          |
| **v3**                 | **34/60 (56.7%)**                                | 83.0                            | Route invariants + capability index. Zero execution errors. **Valid NEGATIVE result — see below**  |
| v3 cross-model     | see below                                    | —                               | Flash 40.0% · Pro 50.0% · Claude 40.0% on a 20-case holdout                                    |
| **v4**                 | **Flash 13/20 · Pro 15/19 · Claude 16/20**       | 85.7 / 89.1 / 89.2              | Same holdout, end-to-end WITH deterministic closure. **+25 to +40 points on every arm**            |

> **INTERPRETATION SUPERSEDED 20260902 — every row from `v1 after gate defs` onward.** These pass rates and means remain accurate as measurements and must not be edited. What changed is what they can
> be read as evidence OF. Gate recall in all of them was achieved by destroying gate precision: 53–58 of 60 routes per run set **all four gates true**, and the scorer of the day charged nothing for
> it. **v4's 79–80% is not evidence of balanced gate routing.** It is evidence of good ownership and skill selection combined with a gate classifier that always answers yes. The two must be reported
> separately from here on; see [Gate over-assertion is system-wide](#gate-over-assertion-is-system-wide-and-predates-the-holdout) for the per-run figures. <!-- count:asat -->

`76.4` belongs to the 23/60 run, not the 28/60 one. That misattribution has already been made once.

**v2 frozen set:** routing `ed2408a5d8e36cd4` · corpus `3b936cd190b41218` · orchestrator `dd84864e3df0cb30` · harness `f692b8966db9efe1`. After the `atar` rename the same content hashes routing
`ea01bf2c24054ad0` · corpus `10451dc9fc71c942` · orchestrator `297fa237fe91e291`. **v3 frozen set:** routing `668e7fd2370db9fd` · corpus `10451dc9fc71c942` · orchestrator `e5d1b2e031a59d32` · harness
`66ca8674ffa51438`.

**Corpus SHA moved again after the v3 run, on 2026-09-01:** `10451dc9fc71c942` → `1fff2b158a2c3909`. Comment-only edit resolving a stale "KNOWN CONFLICT" note; parsed data verified byte-identical, so
v1/v2/v3 scores are unaffected. A v3 row stamps the pre-edit value; that is correct and expected.

**BASELINE v4 — closure measured END-TO-END, not just on stored routes.** The same 20-case holdout, all three arms, live, with closure applied before scoring: **Flash 13/20 (65.0%) mean 85.7 · Pro
15/19 (78.9%) mean 89.1 · Claude 16/20 (80.0%) mean 89.2**, against 40.0 / 50.0 / 40.0 without it. Every arm gains 25–40 points and every mean rises to ~89, so what survives is single-contract misses
rather than broken routes. The two production arms converge near 80%, which is the signal that the contract has become coherent enough for production-tier models to agree about it. **Model tier still
matters, but far less once closure is deterministic.** Provenance: all three arms stamp identical values; `orchestrator_sha ab86f8ea7452e0e2` (I published `e5d1b2e0` and then edited that file mid-run
— the same trap recorded below, walked a second time; it changed the stamp, not the experiment, because that file was not a prompt input at the time).

**DETERMINISTIC CLOSURE WORKS, AND IT IS THE ANSWER TO THE v3 NULL RESULT.** `scripts/close_route.py` repairs a proposed route so it satisfies the catalogue's gates: it adds the minimum provider
declaring the missing capability, escalates to the gate's persona where the task's tags demand independence, recomputes `runtime_required`, and refuses to breach the team cap. Applied to the stored v3
routes with **no model calls and nothing else changed**, it takes the corpus from **34/60 to 47/60 (78.3%)** with zero regressions, clearing the ≥70% target that prompt-based closure missed by
thirteen points. On the 20-case holdout it takes Flash 8→14, Pro 10→15, Claude 8→15 — **the two production arms land identically and the model spread narrows from 10 points to 5.** The division of
labour is now measured rather than argued: **the model judges, the system satisfies constraints.** Where a rule is a lookup against a finite catalogue, a program does it exactly and a model does it
sometimes — the same lesson `runtime_required` taught when it stopped being self-reported.

**Denominators, corrected 2026-09-01.** An execution error is an infrastructure fault and is now excluded from pass rate and mean, with the uncorrected figure printed beside it. Re-reporting every run
under both shows the correction bites in exactly one place — **v2, whose published mean of 81.6 was depressed by its own `ui-only` timeout; corrected it is 83.0, identical to v3's.** v1 (23/60, 76.4),
v1-after-gates (28/60, 80.6) and v3 (34/60, 83.0) carried no execution errors and are unchanged. **This strengthens the v3 null result rather than weakening it: on corrected means the two baselines
are exactly equal, and v3's apparent +1.4 mean was entirely a v2 artefact.**

**Baseline v3 is a VALID NEGATIVE RESULT, not a failed run.** Its +1 pass over v2 is `ui-only` recovering from a parse flake, so the true routing delta is **zero**. It rejects a specific hypothesis
cleanly, which is why it is recorded here rather than quietly superseded: *prompt-visible capability closure plus a stronger route invariant is sufficient to materially improve DeepSeek V4 Flash
routing.* Do not retry that fix. Stage-2 "no selection" more than doubled (2 to 5) — the invariant produced hesitation, not closure — and `unsatisfied` stayed at 57% of hard failures against a 40%
ceiling. **The invariant and the capability index are KEPT regardless**: they cost nothing at inference and improve the initial route, and a deterministic closure layer supplements them rather than
replacing them.

**The cross-model experiment is the most important result so far, and it exonerates the model.** A stratified 20-case holdout ran against an identical, per-row-verified frozen catalogue on three arms:
Flash 40.0% / Pro 50.0% / Claude 40.0%. `unsatisfied` was **7 / 6 / 7** — the target defect is model-invariant. Per case: **1** failure is a model-tier ceiling, **0** are DeepSeek-family, and **10
fail on both production models**, making them contract defects. Pro and Claude agree on only 7/20 routes semantically, with zero `route_mode`-only differences, so two capable models read the same
catalogue differently two thirds of the time. **Prompt-only closure is the wrong mechanism; the next work is deterministic closure — LLM for judgement, system for constraint satisfaction.**

**The v2 failure classification is the load-bearing finding.** All 22 `unsatisfied` failures are ROUTING DEFECTS — zero capability-mapping, zero gate-trigger, zero corpus, zero scoring. The router
judges the gate correctly and then finishes the route without closing the obligation. Full per-case table in
[docs/routing-failure-classification-20260901_1842.md](docs/routing-failure-classification-20260901_1842.md). Two checks were run to falsify it and did not: no case asserts a gate its own required +
preferred contract cannot satisfy (0 of 60), and no plan names a skill absent from the catalogue.

### Frozen measurement contract — 20260902_1240

Frozen BEFORE the unseen holdout is authored, so the holdout is scored once against a contract that will not move under it. Any run whose rows carry a different value in one of these is not comparable
to the holdout and must be re-scored (`--rescore`) rather than compared directly.

| Stamp                   | Value              | Covers                                                 |
| ----------------------- | ------------------ | ------------------------------------------------------ |
| `routing_catalogue_sha` | `ec907ac6af38a61b` | `routing.toml` — capabilities, gates, precedence       |
| `eval_corpus_sha`       | `cb548b83cf203346` | `evals/routing-cases.toml` — the frozen 60             |
| `orchestrator_sha`      | `283664a753137a61` | the production routing contract the prompt sources     |
| `harness_sha`           | `f4e9a470c84e2a6a` | `scripts/evaluate_routing.py` — prompt AND scorer      |
| `closure_sha`           | `bdb17d3c8fbd0e7c` | `scripts/close_route.py` — deterministic repair        |
| `holdout_corpus_sha`    | `7470773e7212933d` | `evals/holdout-cases.toml` — the unseen 24, single use |

`harness_sha` and `closure_sha` both changed on 2026-09-02 for the asymmetric-gate and coverage work. Every v1–v5 baseline predates them. `harness_sha` moved again at 20260902_1015 for the `--cases`
flag, which is what lets the holdout be scored by exactly this scorer instead of a forked one — `just freeze-check` caught that edit against the 0935 record before anything had been run, which is the
failure guide 0003 step 1 describes and the first time a tool rather than memory caught it here.

`holdout_corpus_sha` is hashed locally by `scripts/check_freeze.py` rather than stamped by a run, because until the holdout is executed no result row carries it; a run that does execute it stamps the
same hash as its `eval_corpus_sha`. **The holdout is single-use** — 24 cases authored 20260902 blind to the development 60. **It was executed on 20260902 and is now SPENT.**

### Holdout 24 — EXECUTED and SPENT, 20260902

Claude arm (`claude -p`, provider `anthropic`, model `claude-opus-5`), `--repair` on, freeze verified and captured immediately before launch at git HEAD `1201e42`.

| Measure                           | Value                                                     |
| --------------------------------- | --------------------------------------------------------- |
| Scored / authored                 | **19 / 24** — 5 excluded as execution errors                  |
| Passed                            | **16/19 (84.2%)** — pre-registered "strong" band on pass rate |
| Mean                              | 71.1                                                      |
| `gate_false_negative`             | **0**                                                         |
| `gate_false_positive`             | **62** over 19 cases (3.3/case)                               |
| Cases setting all four gates true | **19 of 19**                                                  |

Evidence, working cache and rebuildable: `routing-results/holdout24-claude-20260902.{jsonl,log,freeze.txt}`. Full classification:
[docs/holdout24-analysis-20260902_1120.md](docs/holdout24-analysis-20260902_1120.md).

**The pass rate is the least informative number here.** Every scored case asserted every gate, which is why the mean is 71.1 rather than ~88 and why the pass rate survives at all — over-assertion is
soft by design.

### Gate over-assertion is system-wide and predates the holdout

Re-analysis of every stored result set, no model calls — the exact use [rule 0011](.archcore/rules/0011-gate-errors-are-asymmetric.md) was built for:

| Result set  | Model               | Rows | All four true | FP  | FN  | FP/row |
| ----------- | ------------------- | ---: | ------------: | --: | --: | -----: |
| `full`      | pre-gate-definition | 60   | **0**             | 13  | 41  | 0.22   |
| `baseline2` | deepseek-v4-flash   | 59   | 53            | 154 | 1   | 2.61   |
| `baseline3` | deepseek-v4-flash   | 60   | 56            | 162 | 2   | 2.70   |
| `after`     | deepseek-v4-flash   | 60   | 58            | 167 | 1   | 2.78   |
| `v4`        | deepseek-v4-pro     | 19   | 17            | 46  | 0   | 2.42   |
| `v4`/`v5`   | claude-code-default | 20   | 20            | 52  | 0   | 2.60   |
| holdout 24  | claude-opus-5       | 19   | **19**            | 62  | 0   | 3.30   |

**Defining the gates on 2026-09-01 converted a systematic false-negative problem into a systematic false-positive one, on every model tier**, and it stayed invisible for a day because the scorer
penalised only one direction. `full` is the before picture. The v4 79–80% headline measured a router that discriminates ownership and skills well and does not discriminate gates at all: a route that
asserts everything can never miss a required gate, and until 2026-09-02 that cost nothing. Rule 0011 was written from one observed case and found a system-wide constant on first contact.

### Gate-only A/B1/B2 — 20260902/03, DeepSeek Flash

Full record: [docs/gate-only-analysis-20260903_0030.md](docs/gate-only-analysis-20260903_0030.md). Run under spec 0007 against the frozen 60, after a realistic-payload runner qualification passed
60/60.

| Stage                               | Result                                                                       |
| ----------------------------------- | ---------------------------------------------------------------------------- |
| A — gates alone, Flash              | macro F1 0.738; PPR 0.48 / 0.37 / 0.20 against base rates 0.50 / 0.37 / 0.22 |
| A — gates alone, Claude             | macro F1 0.782; PPR 0.37 / 0.53 / 0.38                                       |
| A — integrated router, for contrast | PPR **1.00 on all four gates**                                                   |
| B1 — route on model's gates         | 37/60 (61.7%), mean 80.74                                                    |
| B2 — route on ground-truth gates    | 46/60 (76.7%), mean 86.11                                                    |

**Isolated gate judgement is a real classifier on both arms; integrated it is a constant.** Both arms fail the pre-registered thresholds — the classifier is mediocre — but neither is degenerate. The
gate-semantics hypothesis is dead: the definitions are learnable, and something about judging them while constructing a route destroys the signal.

**The aggregate B2 − B1 gap of +9 cases is misleading, and the conditional breakdown reverses it:**

| Stage-A gates           | n   | B1 failure rate |
| ----------------------- | --: | --------------: |
| Correct                 | 36  | 17% (baseline)  |
| FP only — over-asserted | 10  | 30%             |
| FN only — missed a gate | 11  | **100%**            |
| Both                    | 3   | **100%**            |

Where A was correct, B1 30/36 versus B2 29/36 — indistinguishable. `missing gate` hard failures: B1 17, B2 1. **Over-assertion is not detectably costly; under-assertion is fatal, 14 of 14.**
Production makes only the harmless error, because an always-true router has recall ~1.0 and zero false negatives by construction. So for production's error profile this is spec 0007's **B1 ≈ B2** row.

**Consequences.** The gate collapse costs tokens, team size and operator signal — not routing accuracy — so it drops down the queue. **The naive fix is dangerous**: trading precision for recall swaps
a free error for a fatal one; any calibration work must hold recall at 1.0. And [rule 0011](.archcore/rules/0011-gate-errors-are-asymmetric.md) is independently confirmed — its -20/-5 asymmetry was
chosen on judgement before this was measured, and the measured cost ratio is 100%-failure versus indistinguishable-from-baseline.

### Claude Code is retired as this project's runner — 20260902

`claude -p` is **session-limited, not token-metered**, and a full routing prompt is ~49,000 characters, so a sweep dies after roughly five calls. Measured twice: holdout 24 lost 5 of 24 cases
(silently, before the harness reported stdout), and gate-only B1 lost **55 of 60** (named, once it did — `You've hit your session limit`). The default arm is now `deepseek-v4-flash` via Hermes, set in
the justfile. Flash qualified 60/60 at realistic payload, median 14.6s per ~44,000-character call, and its only failures across 120 routing calls were 5 transient parse faults, all of which succeeded
on retry.

### Field use begins — 20260903, operator decision

**Two days of measurement never tested usefulness.** Every eval — 60-case corpus, spent 24-case holdout, A/B1/B2 — tests whether the router picks what a corpus says it should. That is a necessary
property, and a router failing it is broken. It is not sufficient: a route can be perfectly corpus-correct and still not make the work better, and no corpus can close that gap because the corpus is
the thing being agreed with.

Install verified live at the decision point: **123/123 symlinks correct** across `~/.claude`, `~/.codex`, `~/.agents`.

Capture is [`scripts/field_log.py`](scripts/field_log.py) — `just used` / `just field-report`, appending to `evals/field-log.jsonl`, tracked in the repo because a re-run regenerates an eval and
nothing regenerates a day of real use. The load-bearing field is `--overrode`: a followed route only says the operator did not disagree, while a route CHANGED, repeatedly and the same way, is a
routing defect. Data is observational, self-reported and confounded; it cannot establish causation and the report says so below n=10.

## Metric definitions, and which ones have zero noise

Pass rate alone hides the trade that matters. These are the measures that do not.

| Metric                    | Definition                                                                      | v2 value        |
| ------------------------- | ------------------------------------------------------------------------------- | --------------- |
| unsatisfied split         | of `unsatisfied` failures, how many selected non-satisfying skills vs no skills | 15 vs 5 (of 22) |
| mean skills / personas    | per scored route                                                                | 1.35 / 1.72     |
| beyond-contract additions | selected skills outside the case's required + preferred set                     | 15 across 14    |
| critic closure efficiency | critic gates closed ÷ challenge providers selected on those routes              | 0.688 (11 ÷ 16) |
| dual-challenge rate       | critic routes carrying >1 primary `independent-challenge` provider              | 5/22 = 22.7%    |
| **ordinary dual rate**        | dual-challenge on cases that are neither high-consequence nor challenge-asking  | **0/14 = 0.0%**     |
| **ordinary critic excess**    | providers selected − gates closed, ordinary cases only                          | **0**               |

The last two are the sharpest instruments in the project, because a v2 baseline of exactly zero means **the first non-zero reading is itself a finding** — no argument about whether a rise is
meaningful. Use them to detect closure-by-accumulation: a closure rule that makes an unsatisfied gate invalid invites the router to close every gate by adding providers.

**Consequence is proxied, not tagged.** The corpus carries no consequence field. High-consequence is matched textually (go/no-go, `migrat`, `rollout`, `bid`, `invest`, `irreversible`, `launch`,
`high-risk`) and tasks that explicitly ask for challenge (`pre-mortem`, `red-team`) are bucketed separately, because carrying both `critic-munger` and `premortem` on a task that asks for a pre-mortem
is the assignment rather than redundancy. A proxy based on "the corpus names a challenger" is **degenerate** — all 22 critic cases do, so it classifies nothing.

## Traps already hit

Each of these cost real work. They are cheap to avoid twice.

- **`--limit` truncates a family silently.** `networking-infrastructure` has 15 cases and `jdm-import` 12, so `--limit 10` per family produced a 53/60 run that reported "10 passed" per family and read
  as complete. The 7 omitted cases included the three that tested that session's changes most directly. FIXED AT SOURCE 2026-09-02: the evaluator prints `covered X/Y cases` against the pre-limit pool
  and a `WARNING: partial corpus run` line when truncated. `scripts/analyze_routing_results.py` also prints corpus coverage.
- **A scorer that punishes only one direction of an error teaches the model to make the other one.** Gate over-assertion cost nothing until 2026-09-02, so all-gates-true was strictly better than
  honest routing on every case with a required gate, and Baseline v4 contains at least one route (`market-size`, Claude) that took the free points. Nothing in the output distinguished it from a good
  route. Generalise: whenever a check tests `expected and not actual`, ask what `actual and not expected` is worth, and answer it deliberately rather than by omission.
- **An input that moves the score is provenance even when the model never sees it.** `scripts/close_route.py` rewrites routes before scoring under `--repair` — worth +13 cases on the frozen 60 — and
  was stamped by no hash, so a repaired baseline could not be reproduced from its own rows. Found by hand while freezing the contract, not by any check. `closure_sha` now covers it.
- **A mis-invoked runner command scores 0.0 rather than being excluded.** `hermes -z -m MODEL "$(cat)"` fails with `expected one argument` because `-z` consumes the prompt — model flags must precede
  it. The harness labels the result `execution-error:` correctly, but still counts it in the pass rate and the mean, so an infrastructure fault reads as a bad model. Smoke-test every new runner arm on
  one case before spending a full set.
- **A provenance stamp must cover INPUTS, not neighbours.** `orchestrator_sha` recorded a file the eval prompt never read, so editing it raised an alarm that proved nothing while the real inputs were
  untouched. Worse, it hid a genuine architectural gap: the eval was scoring routing principles kept as a literal inside the evaluator, not the contract production used, and no check could have
  detected the divergence. Rows now carry `prompt_inputs`, and the orchestrator is a real input via a marked block the evaluator reads verbatim.
- **Knowing a trap does not prevent it — the instrument does.** The v4 frozen set was published and then the orchestrator skill was edited mid-run, which is the trap listed two entries above, written
  eight hours earlier by the same agent. It was caught in seconds by the per-row stamp, not by memory. Prefer a check that makes a mistake visible over a rule that asks you to remember it.
- **`--output` overwrites, it does not append.** Filling in missing cases needs separate output paths.
- **Editing a frozen file mid-run invalidates the run's provenance.** A contradiction found in a precedence rule 7 minutes into a run was fixed by killing the run, not by finishing it. A stamp that
  needs an argument to defend is not doing its job.
- **Print the frozen SHAs *after* the last edit, not before.** A set was published one docstring-width fix stale and had to be corrected.
- **Relabelling a skill to make a case pass is the cardinal sin here.** Every capability claim must describe what the skill genuinely does. `financial-unit-economics` acquires no external evidence;
  `deep-analysis` analyses what is already present; `devops` release checks are incidental. Checked and left alone deliberately.
- **Verify a taxonomy migration reproduces the old behaviour before deleting the old form.** Resolving each gate through the new capability metadata reproduced its old satisfier list exactly — nothing
  gained, nothing lost — which is what made deleting `satisfied_by_skills` safe rather than hopeful. An early draft had `security-audit` as `validation`-supporting, which would have silently narrowed
  the QA gate.
- **"Capability" now means two things in this repo.** A *manifest* capability is an installable entry (persona or skill); a *routing* capability is a taxonomy term. The governance count check knows
  the difference only because the routing sense is written with the qualifier.

## What is still open

- **The development corpus is FROZEN (2026-09-02).** With closure it scores 50/60 and production-tier models reach ~80% live. Do not tune against it further — past this point a better score on these
  60 is evidence of fitting the corpus rather than of better routing. Add a case only to cover a NEW routing concept.
- **Next evidence must come from outside it:** an unseen holdout authored without reference to these cases, and replay against real project tasks. Then shadow it on real work.
- **Audit findings A1 and A2** — upstream sync apply is non-atomic, and sync follows symlinks through `is_file`/`copy2` so a supplied symlink can escape the intended roots. Both P1 in the audit, both
  maintenance-plane rather than routing-quality, and best fixed together since both concern sync failure behaviour. Do these before calling Agent Stack broadly production-ready.
- **`atar-supplier` ownership** is settled for now — all three arms choose `research-thompson` and pass since closure landed — but the wording genuinely supports a CFO reading ("supplier selection
  materially driven by economics"). Revisit only if real-task replay shows the models drifting back to CFO.
- Two staleness-audit residuals remain formally unaccepted: a vendored TypeScript config is JSONC and unparseable by a strict loader, and the inverse sweep flags package-internal resource directories
  this project catalogues by package. Receipts are archived under the working cache.
