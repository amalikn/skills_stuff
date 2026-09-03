# Scripts — Agent Stack

Operational catalog of every script in this folder. The canonical runner is the root [`justfile`](../justfile) — prefer `just --list` and `just <task>` over invoking a script directly.

Safety labels used below: `safe`, `review-required`, `destructive`, `external-network`, `modifies-files`, `long-running`. Treat any script not listed here as `unknown` safety until inspected.

## Contents

- [Runtime](#runtime)
- [Inventory](#inventory)
- [Task-to-script map](#task-to-script-map)
- [Review-required tasks](#review-required-tasks)

## Runtime

All scripts run on the mise-pinned Python (3.14) from the working-cache venv at `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/venv`. Never invoke a bare `python3`.

The `justfile` addresses that interpreter **explicitly** through its `{{py}}` variable, and every Python recipe depends on `_require-venv`, so a missing venv fails with a rebuild instruction rather
than silently falling through to the host interpreter. Prefer `just <task>`; to call a script directly, use the venv interpreter by path. `just runtimes` prints the declared and resolved interpreters,
which is the quickest way to confirm the pinning actually holds.

`check_governance.py` is the exception by design: it is **stdlib-only** and runs on any Python 3.11+, including the host interpreter. A governance gate that cannot run is indistinguishable from one
that passes, so it must never depend on `just bootstrap` having succeeded.

Run `just bootstrap` once before `just check` or `just test` — both need PyYAML from [`requirements-dev.txt`](../requirements-dev.txt).

## Inventory

### `validate_agent_stack.py`

- **Purpose:** static validation of the library contracts — capability inventory, routing coverage, persona contract depth, concrete local references, and skill metadata presence.
- **Run with:** `just check`
- **Inputs:** `manifest.yaml`, `routing.toml`, `personas/`, `skills/`
- **Outputs:** one-line PASS summary to stdout; non-zero exit on failure
- **Requires:** PyYAML (`just bootstrap` first)
- **Safety:** `safe` — read-only
- **Idempotent:** yes

### `check_governance.py`

- **Purpose:** governance coherence gate. Turns the project's documentation claims into assertions: path resolution, index links, count claims, catalog coverage in both directions, task-recipe
  existence, manifest/library agreement, `SKILL.md` presence, venv placement, and bare-interpreter use.
- **Run with:** `just governance`
- **Inputs:** the governance surfaces listed in its `SURFACES` registry, `manifest.yaml`, `justfile`, `.mise.toml`
- **Outputs:** `OK — N governance checks passed`, or a list of failures; non-zero exit on failure
- **Requires:** nothing beyond the Python standard library
- **Safety:** `safe` — read-only
- **Idempotent:** yes

When it fails, fix the project rather than the check. Extending its registries is part of adding a new artifact class, not a follow-up task.

### `evaluate_routing.py`

- **Purpose:** behavioural routing evaluator. `--validate-only` checks the 60-case corpus in `evals/routing-cases.toml` against `routing.toml` with no model call. `--command CMD` invokes a local
  agent/model CLI once per selected case, passing the prompt on stdin and expecting a JSON routing plan back, then scores it against the case's assertions.
- **Run with:** `just routing-eval-check` (corpus validation), `just routing-eval "<cli command>"` (behavioural run), or `mise run routing-eval-smoke` with `AGENT_STACK_EVAL_COMMAND` set
- **Inputs:** `routing.toml`, `evals/routing-cases.toml`; the operator-supplied CLI command for behavioural runs
- **Outputs:** pass/fail scoring to stdout; a JSONL result file only when `--output` is supplied
- **Requires:** standard library only (`tomllib`); a working local agent CLI for `--command` runs
- **Safety:** `safe` for `--validate-only`; `review-required` and `long-running` for `--command`, which spawns the operator-supplied CLI once per case via `subprocess` and defaults to a 180s timeout
- **Idempotent:** yes — it never installs dependencies or mutates Agent Stack state

Useful flags: `--cases` to select the corpus (defaults to the frozen development 60; `evals/holdout-cases.toml` is the unseen 24, and the stamped `eval_corpus_sha` follows the flag); `--case`,
`--family`, `--limit` to narrow the run; `--timeout` to bound each invocation. `--repair` applies deterministic closure before scoring, in both live and rescore modes. `--rescore '<glob>'` re-scores
plans a previous run already produced against the CURRENT catalogue with no model calls — it holds the routes fixed so any movement is attributable to the catalogue alone, which running the corpus
again cannot tell you because both change at once. See [ROUTING_EVALS.md](../ROUTING_EVALS.md) for the corpus structure and assertion families.

Every run prints `covered X/Y cases` against the pool BEFORE `--limit` applies, and a `WARNING: partial corpus run` line when the limit truncated it. A partial run is a smoke test, never a baseline —
the first Baseline v2 pass covered 53 of 60 behind a `--limit 10` and read as complete. Gate errors are counted in two classes, `gate_false_negative` (hard, -20, decides pass/fail) and
`gate_false_positive` (soft, -5, does not); both totals print in the run summary and both land in every stored row. See [rule 0011](../.archcore/rules/0011-gate-errors-are-asymmetric.md).

### `close_route.py`

- **Purpose:** deterministic route closure. Takes a proposed route and repairs it so it satisfies the catalogue's gates — adds the minimum provider declaring each unmet `required_capability` at the
  required strength, escalates to the gate's persona where the task's tags demand independence, recomputes `runtime_required` from the selected skills, and reports any tool prerequisite still to be
  confirmed. It never overrules a judgement: it does not set `primary_owner`, does not decide which gates are true, and removes nothing the model selected.
- **Run with:** `just routing-eval-check` exercises it indirectly; directly it reads a plan as JSON on stdin — `echo '<plan>' | python3 scripts/close_route.py --explain --max-personas 3 --tag
  security-sensitive`. Inside the evaluator it is applied by `--repair`.
- **Inputs:** a routing plan on stdin; `routing.toml`; optional `--max-personas` cap and repeatable `--tag`
- **Outputs:** the repaired plan on stdout; repair actions on stderr with `--explain`
- **Requires:** standard library only (`tomllib`)
- **Safety:** `safe` — pure function, no I/O beyond stdin/stdout, invokes no model
- **Idempotent:** yes — closing an already-closed route is a no-op

**Why it exists.** Baseline v3 tested the alternative and it failed: stating closure as a route invariant in the prompt and putting a derived capability index in front of the model moved nothing
(34/60 against v2's 33/60, the only extra pass a parse flake recovering). The three-way cross-model experiment then showed the defect is model-invariant — `unsatisfied` was 7 / 6 / 7 across DeepSeek
V4 Flash, V4 Pro and Claude. Applied to the stored v3 routes with no model calls, closure takes **34/60 to 47/60** with zero regressions. The division of labour is the point: **the model judges, the
system satisfies constraints.**

### `analyze_routing_results.py`

- **Purpose:** failure matrix for a completed routing-eval run — family x failure class, plus a root-cause split of the gate-unsatisfied cases. Separates defects that score identically but need
  opposite fixes: a gate unsatisfied because the route selected **no** skills (an omission) versus one unsatisfied because no route member declares the gate's `required_capability` at primary strength
  (a capability-visibility problem). On Baseline v2 that split was 5 against 15, which moved the next fix out of the orchestrator and into `routing.toml`.
- **Run with:** `just routing-matrix`, or `ROUTING_RESULTS='<glob>' just routing-matrix` to analyse a different run
- **Inputs:** routing-eval JSONL result files (default glob: `baseline2-*.jsonl` under the working-cache `routing-results/`); `routing.toml` and `evals/routing-cases.toml` for the gate satisfier lists
  and case-to-family mapping
- **Outputs:** matrix, root-cause breakdown, unparsed-row list and skills-free-route list to stdout; writes nothing
- **Requires:** standard library only (`tomllib`) — it runs without `just bootstrap`
- **Safety:** `safe` — read-only, invokes no model, spawns no process
- **Idempotent:** yes

It reports coverage against the corpus (`corpus has 60 cases; N not present in these results`), which is the check that would have caught the `--limit` truncation that made the first Baseline v2 pass
cover 53 of 60 silently. Rows whose case id is no longer in the corpus are listed rather than crashed on, so a renamed or retired case does not take the analysis down with it.

### `propose_evolution.py`

- **Purpose:** turns field evidence into dated **proposals** for the operator. This is what replaced the upstream sync retired on 2026-09-03 as the way the stack grows: evidence in, proposals out, you
  decide. It detects repeatedly overridden owners, routes the operator rated *worse*, capabilities never selected, and dispatch cost that has not yet bought anything.
- **Run with:** `just evolve` (stdout) or `just evolve <path>` (writes the document)
- **Inputs:** `evals/field-log.jsonl`, `routing.toml`
- **Outputs:** a review document; **it changes nothing**
- **Requires:** standard library only
- **Safety:** `safe` — read-only against the catalogue, calls no model
- **Idempotent:** yes for the same evidence

**It proposes and never applies, deliberately.** [Rule 0001](../.archcore/rules/0001-safety-model.md) excludes material change without explicit operator authority, and field data is the weakest
evidence in the project — self-reported, confounded, small-n. A tool that rewrote `routing.toml` from it would breach the safety model using the least trustworthy input available. The retired sync had
the right shape (apply the safe classes, propose the rest) and it is worth keeping now the tool is gone; here nothing qualifies as safe, so everything is a proposal.

Below 10 entries it proposes nothing and says why. That is the correct output, not a failure. It will not invent a skill or write a persona — authoring is `skill-creator`'s job.

### `persona_note.py`

- **Purpose:** stores each persona's analysis as it returns during a multi-persona route, and records which personas were dispatched against which came back, so
  a run that breaks halfway keeps what it already bought.
- **Run with:** `dispatch --run-dir D --persona X ...` before the work; `write --run-dir D --persona X` reading the analysis on stdin; `status --run-dir D` for
  what is still pending
- **Outputs:** one markdown note per persona, each carrying a banner saying it is **not the verdict**, plus a a MANIFEST.json recording dispatched against returned
- **Requires:** standard library only
- **Safety:** `safe` and `modifies-files` — it writes into the run directory it is given and calls no model
- **Idempotent:** re-writing a persona overwrites its note; the manifest never double-counts

**Evidence retention, never resume.** Nothing here re-dispatches anything or continues a broken run: auto-continuation is unattended work, which
[rule 0001](../.archcore/rules/0001-safety-model.md) excludes and which is why this project exists as a fork. Re-running is the operator's decision.

Recording the dispatch **before** the work is what makes an incomplete run visible as incomplete — otherwise it is indistinguishable from a run that only ever
wanted the personas that returned.

### `field_log.py`

- **Purpose:** records what the router actually did on **real work**, and reports the pattern. Every other measurement in this project tests agreement with a corpus — necessary, but not sufficient,
  because a route can be perfectly corpus-correct and still not make the work better. Only real use tests that, and only if it is written down at the time.
- **Run with:** normally **by the orchestrator skill itself**, at Step 10, with no operator involvement — `python3 <abs path>/scripts/field_log.py add ...`. `just used` is the operator path for adding
  `--helped` afterwards; `just field-report` reads the log.
- **Inputs / outputs:** appends to `evals/field-log.jsonl`, which is **tracked in the repo** — a re-run regenerates an eval, and nothing regenerates a day of real use
- **Requires:** standard library only
- **Safety:** `safe` and `modifies-files` — it appends one line and calls no model
- **Idempotent:** no, by design; each invocation records one event

`--followed` and `--overrode` are filled in by whoever did the work, because only they know what was actually used. **`--helped` is operator-only and an agent must never fill it in about its own
work** — self-assessed helpfulness is the one field where the recorder has an interest in the answer, so absent is the honest default and the report says so rather than showing a blank column.

**Omit `--overrode` when the route was followed.** A prose "none" or "nothing to change" would count as an override and inflate the one statistic the log exists to produce — silently, and in the
flattering direction, since every clean route would add to it. Observed on the first real entry ever logged. The tool normalises such values on read as well as refusing them on write, because the file
already contains one and future recorders include agents.

**The field that matters is `overrode`** — what you CHANGED about the route and why. A route you followed only tells you that you did not disagree. A route repeatedly overridden the same way is a
routing defect; overridden once, it is a preference. The report flags any owner overridden three or more times.

Read it honestly: the data is observational, self-reported, small-n, and confounded by task difficulty and by whatever you were going to do anyway. **It cannot establish causation** and must never be
reported as though it could. What it can do is surface a pattern too consistent to be noise. The report prints an explicit warning below n=10.

### `gate_eval.py`

- **Purpose:** the A / B1 / B2 experiment of [spec 0007](../.archcore/specs/0007-gate-only-evaluation.md). **A** judges the three gates alone; **B1** routes on the model's own gates; **B2** routes on
  ground-truth gates. Scores A as a classifier — precision, recall, specificity, F1 and predicted-positive rate per gate, against thresholds pre-registered in the spec — and B1/B2 with the production
  scorer.
- **Run with:** `python scripts/gate_eval.py --stage {A,B1,B2} --command '<runner>' --output <file>`; B1 additionally needs `--gates-from <stage-A file>`
- **Inputs:** `routing.toml`, a corpus (`--cases`, default the frozen 60), a stage-A artifact for B1
- **Outputs:** one JSON artifact per stage carrying rows, provenance, per-stage prompt-size stats, and `complete: false` when any case failed
- **Requires:** standard library only; imports `evaluate_routing.score_plan` and the production `close_route`, because a second scorer here would measure this script as much as the router
- **Safety:** `external-network`, `requires-credentials`, `long-running` — it drives the configured runner once per case
- **Idempotent:** no — each run calls a model; artifacts are timestamped per run

`--case` with `--merge-into` repairs a sweep that lost cases to a runner or parse fault: it replaces only those rows and **records the repair** in the artifact's provenance, so a merged artifact can
never be mistaken for a single clean sweep. Valid only when the freeze, qualification state, command and model are unchanged — a repair completes one measurement, it does not blend two.

Any failure marks the artifact `complete: false` and exits 2, because a sweep missing cases is not a measurement. All output is flushed per line: a 40-minute stage whose progress sits in an 8 KB
buffer is dark for its whole run, and during the Claude session-limit collapse the per-case failures only became visible after 55 had already burned.

### `qualify_runner.py`

- **Purpose:** qualifies an external runner on **disposable calls** before any corpus is measured through it. Sends N throwaway prompts down the same path a real run uses — stdin, invoke, the
  harness's own `extract_json` — and classifies every outcome by name: `ok`, `timeout`, `nonzero-exit`, `silent-failure`, `unparseable`.
- **Run with:** `just qualify-runner '<command>' <calls>`
- **Inputs:** `--command`, `--calls` (set it to the corpus size), `--timeout`, and the provider/model/runner labels
- **Outputs:** a per-call log, a five-check verdict, latency stats, and a JSON receipt recording `qualified_for_corpus_size`; exit 1 on failure
- **Requires:** standard library only; imports `extract_json` from `evaluate_routing.py` so it exercises the real extractor rather than a lookalike
- **Safety:** `external-network` and `requires-credentials` when the runner is a cloud CLI; `safe` for the offline self-tests
- **Idempotent:** yes locally — it writes only the receipt — though each run consumes calls against the runner

Five checks, each negative-tested against a fake runner: sequence reliability, parse reliability, failure legibility, timeout behaviour and labels. The failure-legibility probe is **offline** (`exit
7`) and costs no model call. `just holdout` now depends on `_require-qualified`, which refuses unless a passing receipt covers at least the corpus size — a receipt qualifying 5 calls cannot authorise
a 24-case run.

Qualification is **perishable**: it expires when the runner, its credentials, its quota state or the harness changes. It is evidence about the pipeline on a day, not a property of the project.

### `check_qualification.py`

- **Purpose:** refuses a corpus-spending run unless a receipt qualified **this** execution path. Checks four bindings: the qualification passed, it covers at least the corpus size, it was earned with
  the same command, and it was earned against the same `harness_sha`.
- **Run with:** invoked by the private `_require-qualified` justfile guard, which `just holdout` depends on
- **Inputs:** `--receipt`, `--size`, `--command`; the live hash of `evaluate_routing.py`
- **Outputs:** one line naming the receipt on success; `REFUSED:` lines on stderr and exit 1 otherwise
- **Requires:** standard library only
- **Safety:** `safe` — read-only, calls no model
- **Idempotent:** yes

A receipt is not a general certificate. It records that one command, driving one runner, against one harness, completed N consecutive disposable calls — so a receipt earned with a different command
does not transfer, and a harness edit invalidates every outstanding receipt, the harness being part of the execution path under test rather than a neutral observer of it. A receipt with no
`harness_sha` at all predates the binding and is refused rather than trusted.

### `index_runs.py`

- **Purpose:** derives `evals/runs.toml` — one record per evaluation run — from the stored result rows, and re-verifies it against that evidence. Every metric is computed: counts, pass rate, mean,
  gate error classes, the failure-class histogram and the provenance the rows already stamp. The authored fields (`purpose`, `status`, `interpretation`, `supersedes`, `notes`) are written by a person
  and survive regeneration.
- **Run with:** `just runs` (list), `just runs-index` (regenerate), `just runs-check` (verify; part of `preflight`)
- **Inputs:** `$AGENT_STACK_RESULTS` (default the working-cache results dir), `evals/*-cases.toml`, the existing index
- **Outputs:** `evals/runs.toml`; a table on stdout for `--list`; exit 1 on drift for `--check`
- **Requires:** standard library only
- **Safety:** `safe` for `--check`/`--list`; `modifies-files` when regenerating — it rewrites `evals/runs.toml` only
- **Idempotent:** yes — regenerating without new evidence reproduces the same file

It exists because executing holdout 24 produced evidence while three hand-maintained surfaces still called it unexecuted. Status restated by hand in three places drifts; status derived from rows and
checked does not. Result files live in the working cache and are rebuildable, so a record whose evidence is absent is reported **UNVERIFIABLE** rather than failed — an index outliving its evidence is
normal, and silence about it would not be.

### `check_freeze.py`

- **Purpose:** answers one question — does this checkout still match the recorded evaluation freeze? Recomputes the five stamped hashes and compares them to the table MEMORY.md records, naming any
  artifact that moved.
- **Run with:** `just freeze-check`
- **Inputs:** the frozen SHA table in `MEMORY.md`; the five stamped files
- **Outputs:** a per-artifact OK/drift report on stdout; exit 0 on match, 1 on drift, 2 when the record itself cannot be read
- **Requires:** standard library only; imports `run_provenance` from `evaluate_routing.py` so the live hashes come from the SAME code that stamps result rows — a second implementation here could
  verify a freeze no row was ever measured against
- **Safety:** `safe` — read-only, writes nothing, calls no model
- **Idempotent:** yes

**Not part of `just preflight`, deliberately.** Preflight answers "is this repository internally valid"; this answers "does it match one particular evaluation snapshot". A legitimate catalogue change
must be able to pass the first while failing the second, so making it universal would convert a historical reference into a standing prohibition on changing the catalogue. Run it before any run whose
numbers will be compared to a recorded baseline, or spent on a single-use holdout; `_require-freeze` is the private justfile guard such a recipe depends on. Smoke runs do not need it.

### `eval_model_adapter.py`

- **Purpose:** bridges `evaluate_routing.py` to any HTTP endpoint speaking the OpenAI `/chat/completions` shape. The evaluator only knows how to run a shell command, so an HTTP model needs an adapter;
  this is it. Reads the prompt on stdin, posts it, prints the message content on stdout.
- **Run with:** `just routing-eval-ping` (one-shot connectivity check), `just routing-eval-local`, `just routing-eval-remote`
- **Inputs:** prompt on stdin; `EVAL_BASE_URL`, `EVAL_MODEL`, `EVAL_API_KEY`, `EVAL_TEMPERATURE`, `EVAL_MAX_TOKENS`, `EVAL_TIMEOUT`
- **Outputs:** model response text on stdout; diagnostic on stderr with a non-zero exit
- **Requires:** standard library only (`urllib`)
- **Safety:** `external-network` — it calls whatever `EVAL_BASE_URL` points at. `requires-credentials` when that endpoint authenticates. It reads the key from the environment and never writes or
  echoes it
- **Idempotent:** yes — read-only against the endpoint, writes nothing locally

It is a **protocol** adapter, not a provider one. `ROUTING_EVALS.md` states Agent Stack hard-codes no provider's syntax, so the vendor stays configuration: the same script reaches local Ollama, a
LiteLLM gateway, or a cloud API by changing `EVAL_BASE_URL` and `EVAL_MODEL` alone.

It strips `<think>` blocks. Reasoning models such as the `deepseek-r1` family emit a scratchpad inline, and that scratchpad often contains braces and draft JSON — which is exactly what the evaluator's
JSON extractor would otherwise latch onto. An unterminated block means the model hit the token ceiling before answering; raise `EVAL_MAX_TOKENS`.

### `install_global.py`

- **Purpose:** symlink-only global installation of personas and skills into `~/.claude/agents`, `~/.claude/skills`, `~/.codex/skills`, and `~/.agents/skills`.
- **Run with:** `just global-status`, `just global-dry-run`, `just global-install install`, `just global-uninstall uninstall`
- **Inputs:** `manifest.yaml`, the canonical checkout
- **Outputs:** symlinks in the consumer directories; a status/preview report on stdout
- **Safety:** `review-required` and `modifies-files` for `--install` / `--uninstall`; `safe` for `--status` / `--dry-run`
- **Idempotent:** yes — it preflights collisions, never overwrites a pre-existing entry, and never copies source content

Uninstall removes only links that still point exactly at Agent Stack sources. `skill-creator` is excluded by default; pass `--include skill-creator` only after deliberately reconciling the duplicate.

