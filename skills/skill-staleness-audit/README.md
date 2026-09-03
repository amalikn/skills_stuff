# skill-staleness-audit

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

A repo-wide audit for **facts that have quietly stopped being true**.

Not a linter, not a propagation pass. It starts from nothing and asks what the corpus is still asserting that reality has moved past — then hardens the checks so each finding cannot recur.

## Contents

- [Why it exists](#why-it-exists)
- [When to use it](#when-to-use-it)
- [Relationship to sibling skills](#relationship-to-sibling-skills)
- [Layout](#layout)
- [Install](#install)
- [Invocation](#invocation)
- [What a run produces](#what-a-run-produces)
- [Provenance](#provenance)

---

## Why it exists

A mature governed project accumulates checks that verify **the documents agree with each other**. That is a genuinely useful property, and it is not the same property as being right.

The originating run is the argument. Across a full day, **592 governance checks passed continuously** while:

- two documents filed with a licensing authority stated a **superseded profit gate**;
- a class verdict in the data layer still read `RECOMMENDED` after the prose had been reversed on real evidence;
- a **maximum auction bid** — the number an operator carries into a live auction — was back-solved against a profit floor the gate had outgrown, overstating the ceiling by ~$3,800 on a $42k vehicle;
- the project asserted **three different values** for the same check count, none of them correct.

Every one of those was invisible to a consistency check, because the copies agreed. What they needed was something that asked whether the original was still true.

## When to use it

- Nothing specific has changed, but history has accumulated.
- The project has an **append-only knowledge base**, where old documents keep reading as current by design.
- A figure, threshold, verdict or price is **restated across many surfaces**.
- **Before anything with money or legal exposure** — a purchase, a filing, a licence application, a quote.
- When "the checks pass" has started to feel like evidence of correctness.

**Do not use it** for a cosmetic sweep, a typo pass, or adding a document that changes no existing fact.

## Relationship to sibling skills

| Skill | Starts from | Asks |
|---|---|---|
| `skill-ai-it` | An ungoverned or under-governed folder | *What governance should exist here?* |
| `skill-project-coherence` | **One known change** | *What else must move so everything agrees?* |
| **`skill-staleness-audit`** | **Nothing** | *What is this corpus still asserting that is no longer true?* |
| `skill-holistic-impact-assessment` | A proposed change | *What is the blast radius before I make it?* |
| `skill-safe-change-validation` | An edit about to happen | *What is the smallest validation that proves it?* |

The distinction from `skill-project-coherence` is the one that matters in practice, and it is not a matter of degree. Coherence **pushes a known fact outward**. This skill **hunts for unknown ones**,
and its highest-value findings are the ones a coherence pass structurally cannot see — because a coherence pass trusts the fact it was handed.

## Layout

```text
skill-staleness-audit/
├── SKILL.md            # orchestrator: the standard, eight phases, anti-patterns
├── README.md           # this file
├── CHANGELOG.md        # version history and provenance
├── patterns/           # depth — load the one for the phase you are in
├── templates/          # register, banner, residual-risk and report boilerplate
└── scripts/            # snapshot_worktree.sh, stale_scan.py (+ catalog)
```

Full annotated tree: `SKILL.md` → *Skill package layout*.

## Install

Canonical source lives here. Installs are **symlinks to `SKILL.md`**, never copies — a copy drifts silently across the agents that read it.

```bash
CANON=/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-staleness-audit
for target in ~/.claude/skills ~/.codex/skills ~/.agents/skills ~/.hermes/skills; do
  [ -d "$target" ] || continue
  mkdir -p "$target/skill-staleness-audit"
  ln -sfn "$CANON/SKILL.md" "$target/skill-staleness-audit/SKILL.md"
done
```

Verify: `readlink ~/.claude/skills/skill-staleness-audit/SKILL.md` must resolve into `skills_stuff`.

## Invocation

```text
/skill-staleness-audit                      # whole project, materiality-ranked
/skill-staleness-audit docs/                # scoped to a subtree
/skill-staleness-audit --money-only         # gates, prices, verdicts, filed artifacts only
```

Scoping trades coverage for time. **Say which you did in the report** — a scoped run that reads as a full one is itself a staleness defect.

## What a run produces

1. **A defect register**, materiality-ranked, every row citing evidence.
2. **In-place supersession banners** on every superseded section, naming what replaced it *and what still stands*.
3. **New checks**, each proven able to fail by deliberate breakage in both directions.
4. **A residual-risk register** — what the audit did *not* resolve, including errors made during the audit itself.
5. **A change-log entry recording the reasoning**, not just the diff. Why a defect survived is the reusable part.
6. **Both memory backends written**, context pack rebuilt, full validation re-run with the check count reported before and after.

## Provenance

Extracted from a full-day audit of a vehicle-import project in August 2026, where the operator's standard was stated plainly: *thousands of dollars ride on these documents.* Every rule in this skill
traces to a specific defect found in that run, and several trace to mistakes made **by the auditing agent** — a destructive `git checkout`, a systematic mis-citation, a warning that read the wrong
cell and therefore never fired, and a confidently-documented protection mechanism that turned out not to exist.

Those are in here deliberately. An audit skill written only from other people's mistakes would be missing half the failure modes.
