Title: Governance Coherence Checks
Category: pattern
Status: current
Authority: skill-module
Scope: Generating and maintaining a project-local `scripts/check_governance.py`
Last reviewed: 2026-08-11
Summary: How to infer, generate, and continuously extend an executable coherence checker so a project's governance claims stay true as the project grows.

# Governance Coherence Checks

## Contents

- [Why an executable checker](#why-an-executable-checker)
- [The harness contract](#the-harness-contract)
- [Tier model](#tier-model)
- [The seven check families](#the-seven-check-families)
- [Coverage self-policing](#coverage-self-policing)
- [Inference table — artifact observed to check generated](#inference-table--artifact-observed-to-check-generated)
- [Maintenance triggers](#maintenance-triggers)
- [Sizing and rollout](#sizing-and-rollout)
- [Anti-patterns](#anti-patterns)

---

## Why an executable checker

Governance documents make **claims about the project** — "the knowledge base holds 26 files", "every script is cataloged", "the profit gate is $2,500", "this parquet is derived from the newest
snapshot". Every one of those claims is true when written and decays silently afterwards. Prose review does not catch decay, because the reviewer reads the claim and the claim reads fine.

A coherence checker converts those claims into assertions that fail. It is the difference between governance that describes the project and governance that is *tested against* the project.

Three properties make it work, and all three are non-obvious:

1. **It counts up, not down.** The checker reports `OK — 41 governance checks passed`, not `OK`. A growing number is visible evidence that coverage grew with the project; a bare `OK` hides a checker
   that quietly stopped covering anything.
2. **It gates the task runner.** `just check` must run it and stop on failure. A checker nobody runs is a document with a `.py` extension.
3. **It polices its own coverage.** The hardest failure mode is not a check that breaks — it is a new file nothing checks. The checker must therefore fail on *uncovered* surfaces, not only on
   *incorrect* ones. This is what makes the checker self-extending rather than a snapshot of the day it was written.

---

## The harness contract

Every generated checker uses the same skeleton, regardless of project. Keep it stdlib-only so the checker never fails for environment reasons — a coherence gate that needs a dependency install is a
gate that gets skipped.

```python
failures: list[str] = []
checks_run = 0

def fail(check: str, detail: str) -> None:
    failures.append(f"{check}: {detail}")

# Each check function increments checks_run once per assertion actually evaluated,
# not once per function. A function that evaluates nothing must add nothing.
```

Rules the skeleton must honor:

- **`checks_run` increments per assertion evaluated, never per function called.** A check that finds no candidates contributes zero. This is what stops a silently-inert check from inflating the count
  and reading as coverage.
- **Deduplicate before reporting** (`sorted(set(failures))`). One defect matched by two patterns is one defect; a doubled count erodes trust in the number.
- **Exit 1 on any failure.** No warning tier at the top level — a finding the runner tolerates is a finding that survives forever. Where a check is genuinely advisory, say so in its message text and
  still fail, or do not generate it.
- **Print every failure, never truncate.** The operator fixes what they can see.

---

## Tier model

| Tier | What it is | When generated |
|---|---|---|
| **T1 — universal** | Checks valid for any governed project: referenced paths resolve, index links resolve, count claims match reality, catalog coverage. | Always, at bootstrap, from `templates/check_governance.py`. |
| **T2 — conditional** | Checks that apply when a trigger artifact exists: task-runner recipes, archcore document contract, frontmatter vocabulary, supersession targets. | When Phase 1 inventory finds the trigger artifact. |
| **T3 — inferred** | Checks encoding *this project's* domain invariants: derived-artifact provenance, duplicated-constant sync, evidence-to-assertion matching, schema conformance. | Authored by the agent from Phase 3 inference. Never guessed — each must trace to a stated project rule. |

T1 and T2 are mechanical. T3 is the reason this pattern exists: a project's real integrity risks are domain-shaped, and a generic linter cannot see them. The agent's job in Phase 3 is to read the
project's own rules and ask, for each, *what observable state would prove this rule was violated?*

---

## The seven check families

Every T2 and T3 check reduces to one of seven families. When inferring a new check, name its family first — if it fits none of them, question whether it is checkable at all.

### 1. Count-claim

**Catches:** prose asserting a quantity that the filesystem or a data file contradicts. "26 documents", "five ADRs", "three snapshots".

**Why it matters more than it looks:** count claims are the most common thing an agent updates a document *around* without updating. They are also trivially verifiable, which makes them the cheapest
true statement in the whole governance surface.

**Historical-fact exemption:** a count stated as a record of a past moment ("as of 2026-08-09, 228 checks passed") is not a live claim and must not be enforced. Mark those lines with an inline marker
(`<!-- count:asat -->` or equivalent) and have the check skip marked lines. Without the exemption the checker forces agents to falsify history to make the build green.

### 2. Link and path resolution

**Catches:** any repo-relative path named in a governance surface that does not exist — moved files, renamed folders, aspirational references to files that were planned and never written.

**Discrimination is the whole difficulty.** Prose is full of tokens that look like paths and are not: URLs, absolute host paths, identifiers with dots, glob patterns, shell fragments, `README.md`
meaning "the concept". Generate an explicit allow/ignore policy — path-like character set, known repo suffixes, ignore prefixes, ignore-exact set — and tune it against the real corpus until it is
quiet. A noisy path check gets disabled, and a disabled check is worse than none.

### 3. Contract conformance

**Catches:** structured documents violating their own declared schema — filename form, required frontmatter keys, status vocabulary, ID format, required sections.

**Trigger:** the project has a class of documents with a stated contract (ADRs, specs, runbooks, trackers, dated captures). If the contract is stated in prose but not enforced, the third document
already deviates.

### 4. Derived-artifact staleness

**Catches:** a generated output older than its input, or built from a source that is no longer the newest — stale generated markdown, a cached query layer rebuilt from an outdated capture, an export
whose generator has since changed.

**Two distinct assertions, and most implementations only write the first:**

- **Freshness** — `mtime(output) >= mtime(input)`. Cheap, catches "forgot to regenerate".
- **Provenance** — the output records *which* input it was built from, and that input is still the one it should have been built from. Catches the worse case: a rebuild that ran, succeeded, and used
  the wrong source. Freshness alone passes that.

Generate provenance whenever the generator can stamp its source into the output. If it cannot, say so in the check's message rather than implying coverage you do not have.

### 5. Duplicated-fact sync

**Catches:** a fact deliberately restated across many surfaces — a threshold, a rate, a deadline, a canonical path — drifting in one of them.

**This family is the most valuable and the most often skipped**, because the correct response to "this constant appears in 14 files" looks like "stop duplicating it". Usually you cannot: the whole
point of a governance surface is that the operator reads the number *there*, at the moment of decision, without following a pointer. So the duplication stays and the sync gets enforced.

The implementation has two halves and needs both:

- **Drift detection** — every registered surface states the fact, and states it identically (all limbs, all values).
- **Orphan detection** — no *unregistered* file states the fact. This is the half that makes the check self-extending: adding a fifteenth surface fails the build until it is registered.

Pair the registry with a spec document explaining why the duplication is intentional, so the next agent extends the registry instead of "fixing" the duplication.

### 6. Table grain

**Catches:** an append-only table that has lost the ability to say which of its rows is current.

Promoted from a governed project on 2026-08-28, where twelve rows stood for eight entities and the supersession was recorded only in a prose note. Append-only is the right design — a re-measurement
adds a row rather than overwriting one, so the earlier measurement survives to be argued with. It is also useless on its own. Without a column that ORDERS the passes, nothing can compute which row is
current, and every aggregate over the table double-counts whatever was re-measured.

Two assertions, and the second is the one that is usually missing:

- **Every row stamps its pass.** A row with an empty pass column cannot be ordered against any other row.
- **No pass records the same entity twice.** A repeat means one pass measured one thing twice, so every count over the table is wrong by however many rows were duplicated.

Neither failure surfaces on its own: the table still parses, the report still renders, and the numbers still look like numbers. Register the table in `APPEND_ONLY_TABLES` and the grain becomes an
assertion rather than an intention.

### 7. Evidence provenance

**Catches:** a capture that nobody can re-open — no source URL, no retrieval date, no record of whether the fetch actually succeeded.

The existence of a capture FILE is not evidence. It proves somebody wrote something down. In the project this was promoted from, a capture with no recorded HTTP status backed a `VERIFIED` cost row,
and the only fetch behind it had returned 403 — the failure was invisible precisely because the file existed and read plausibly.

This family is where the global source-discipline policy meets the checker: a `VERIFIED` label is a claim that someone else can re-open the source, and only a provenance header makes that claim
falsifiable. The check pairs with a **corrections registry** rather than an ignore-list. A capture predating the rule is accepted only while it NAMES the later capture that supplies its provenance,
and only while that capture is on disk — so where captures are immutable, the sole way to clear an entry is to take the correcting capture. An entry removed without its correction existing turns the
check red. That is deliberate: the registry cannot be emptied by deletion, only by doing the work.

---

## Coverage self-policing

This is the mechanism that satisfies "continuously fine-tuned as more files are added". The checker must fail when the project grows past it, not merely when the project contradicts it.

Generate a coverage check for every catalog the project maintains:

| Catalog | Orphan condition that must fail |
|---|---|
| `docs/README.md` index | A file exists in `docs/` that the index does not link |
| `scripts/README.md` catalog | A script exists that the catalog does not describe, or the catalog names a script that no longer exists |
| Task runner | A recipe is referenced in prose but absent from the runner, or a script has no runner entry |
| Constant registry | A file restates a registered constant without being registered |
| Archcore / structured-truth index | A document exists that no index references |

The asymmetry matters: a *missing* file (catalog names something that vanished) and an *uncataloged* file (something exists that no catalog names) are different defects, and only the second one grows
silently. Both must fail.

**Coverage checks are what make the checker intelligent over time.** Without them, the checker measures the project as it was on generation day. With them, every new file either gets registered
somewhere or turns the build red — so the checker's own extension becomes a blocking condition rather than a good intention recorded in a document.

---

## Inference table — artifact observed to check generated

Use during Phase 3. Left column is what the inventory found; right column is the check to write.

| Observed in the project | Check to generate | Family |
|---|---|---|
| Prose stating a file/document/item count | Count claim vs actual, with historical-fact marker exemption | 1 |
| An index or README linking siblings | Every link resolves; every sibling is linked | 2 + coverage |
| Backtick or markdown-link paths in governance prose | Path tokens resolve on disk | 2 |
| A task runner (`justfile`, `Makefile`, `Taskfile.yml`, npm scripts) | Recipes named in prose exist in the runner; scripts have runner entries | 2 + coverage |
| A class of documents with declared filename/frontmatter rules | Filename form, required keys, status vocabulary | 3 |
| A generator script plus its output committed to the repo | Output not older than generator or inputs; output records its source | 4 |
| A cache, parquet, export, or flattened view over raw captures | Built from the newest capture; provenance recorded per row or in a header | 4 |
| A threshold, rate, deadline, or limit stated in more than one file | Registry of surfaces; all state it identically; no unregistered file states it | 5 |
| A supersession chain ("doc 14 supersedes doc 05 §10") | Every supersession target exists and is reachable | 2 |
| Assertions in a config file backed by captured evidence files | Every asserted value traces to a capture; every capture is accounted for | 3 |
| Dated immutable captures (`*-YYYYMMDD_hhmm.*`) | Naming form valid; no capture edited after creation where a hash or manifest allows checking | 3 |
| A schema or contract spec document plus instances | Instances conform to the spec's stated fields | 3 |
| An append-only table with a pass, run, or `*_at` stamp column | Every row stamps its pass; no pass records the same entity twice | 6 |
| A folder of dated evidence captures backing labelled figures | Every capture states URL, retrieval date and fetch status, or names the capture correcting it | 7 |
| Symlinked or copied installs of a canonical source | Install target still resolves to canonical; no silent copy drift | 4 |

Two discipline rules when using this table:

- **Every T3 check must cite the project rule it enforces.** Put the rule's location in the check's docstring or failure message. A check whose justification nobody can find is a check the next agent
  deletes when it becomes inconvenient.
- **Do not generate a check for a rule the project has not stated.** Inventing invariants during bootstrap manufactures governance the operator never agreed to. If an invariant looks worth having,
  report it as a proposal instead.

---

## Maintenance triggers

These belong in the target project's `AGENTS.md` as a managed block (see `templates/AGENTS-governance-checks-block.md`), because the obligation must live where the agent doing the work will read it.

| Change made | Required checker update |
|---|---|
| Add a document to a cataloged folder | None if a coverage check exists — it will fail until the index links it. That is the intended workflow. |
| Add a script or task | Catalog it; the coverage check fails until then |
| Add a new *class* of artifact (new folder, new document type) | Add a coverage check for it, plus a contract check if it has a declared form |
| Add a generated artifact | Add a staleness check, and a provenance check if the generator can stamp its source |
| Add an append-only table, or add a re-measurement pass to one | Register it in `APPEND_ONLY_TABLES`; reuse of an existing pass id fails the grain check |
| Add a capture predating the provenance rule | Take the correcting capture and register the pair; an unaccompanied entry fails |
| State a threshold or constant in a new file | Register the surface; the sync check fails until then |
| Change a threshold's value | Update the owning rule, then every registered surface, in one pass; the sync check verifies the pass was complete |
| Rename or move a file | Nothing — path resolution catches every stale reference |
| Retire a check | Record why in `CHANGELOG.md`. A silently deleted check is indistinguishable from a check that never existed |

Also state the inverse obligation explicitly: **when a check fails, fix the project, not the check.** Weakening an assertion to make the build green converts a real finding into a permanent blind
spot, and the next agent has no way to know it happened.

---

## Sizing and rollout

Do not generate a large checker at bootstrap. A project with four documents does not need coverage policing on a folder that does not exist yet.

- **Bootstrap:** T1 only — path resolution, index links, count claims, catalog coverage for whatever catalogs exist. Typically 10–40 assertions.
- **As structure appears:** add T2 checks when their trigger artifacts appear, not in anticipation of them.
- **As rules appear:** add T3 checks when the project states a rule worth enforcing. This is the layer that grows for the life of the project.

The assertion count is a coverage signal, not a score. Prefer one check that can genuinely fail over five that scan an empty set — and if a check's count drops after a refactor, find out why before
accepting it.

---

## Anti-patterns

- **Checks that cannot fail.** A check scanning a set that is always empty, or asserting a condition the code structurally guarantees. Verify by deliberately breaking the project and confirming the
  check goes red. An untested check is an assumption.
- **Phrase-grep standing in for semantic verification.** Grepping for a threshold's *text* does not prove the surrounding logic implements it. Real case: a script's output text was updated to state a
  dual gate while the code still evaluated only one limb — every text-matching check passed. Where a check must verify behavior, execute the behavior and assert on the result.
- **Weakening the gate to pass.** Broadening an ignore-list to silence a true positive, or exempting the file that failed. Fix what the check compares, never what it tolerates.
- **Silent skip on missing input.** A check whose input file is absent must fail or report explicitly — never return quietly. Absence is usually the defect.
- **A checker not wired into the task runner.** If `just check` does not run it, it does not run.
- **Enforcing history.** Past-tense records of counts and states are evidence, not claims. Exempt them by marker, and never edit history to satisfy a linter.
