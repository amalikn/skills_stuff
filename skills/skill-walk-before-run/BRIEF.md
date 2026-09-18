---
Title: Brief — skill-walk-before-run (v0.1)
Status: built — baseline reference, colocated with the shipped skill
Summary: Creation brief for a minimal blocking gate that stops expansion before the load-bearing assumption is tested. Deliberately small. v0.2 ideas are parked, not designed.
---

# Brief — skill-walk-before-run (v0.1)

Fed to `skill-creator` on 2026-09-16 to build the skill. Kept afterwards as the provenance record — see open decision #4 for where it lives now.

**Revision note, 2026-09-16 (pre-build).** The first version of this brief specified eight signals, six prerequisites, helper scripts, ledger analytics and cross-runtime install policy — before the
skill had been trialled even once. That made it an instance of the pattern it exists to prevent. It was cut to the minimum testable version, then revised to make the signals assumption-relative rather
than capability-relative, and finally to bound Step 0 by material relevance and make the gate deterministic. **Frozen at that point. No further design rounds before the three-project trial** — another
round is itself the thing this skill exists to stop.

**Revision note, 2026-09-16 (post-build).** During the build, the ledger path was decided as colocated (`skill-walk-before-run/ledger.md`, alongside `SKILL.md`) rather than under `skills-data`,
overriding this brief's original proposal below — see open decision #2. `SKILL.md` and `README.md` reflect the colocated path; the ledger examples further down in this brief still show the original
`skills-data` path as the historical record of what was proposed before the decision.

**Revision note, 2026-09-16 (still pre-first-write).** The ledger's own format was hardened before any entry had ever been written to it: colon-delimited text block → one JSON object per line in
`ledger.jsonl`, plus `ts` (ISO 8601, local UTC offset, replacing date-only) and `branch` fields. This touches the "Parked for v0.2" items at § "Ledger — episodes only" (`schemas/ledger-entry.md` and
"Ledger schema") and their explicit caution against adding a field mid-experiment — see open decision #5 for why this is judged pre-first-write hardening, not mid-trial schema churn, and therefore in
bounds.

**Revision note, 2026-09-16 (post-trial-round-one).** Different in kind from the notes above: this one follows real trial evidence, not a design round ahead of it. All three trial projects
(cambium-swap, japan-jdm, atar) were run for real. Two things surfaced directly from those runs, not from reading elsewhere: (1) without an explicit project name, the gate evaluated its own
construction instead of the intended target — reproduced exactly once, on the very first invocation, then fixed by telling it the project explicitly on every subsequent run; (2) all three RED verdicts
were invisible to the target project's own governance — nothing in cambium-swap's, japan-jdm's, or atar's own tracking reflected that a RED had been raised. Both fixed — see open decisions #6 and #7.
Contrast with the Teycir/Assumptions-derived items still sitting in "Parked for v0.2": those were parked specifically because they had no trial evidence behind them yet; these two do.

The load-bearing unknown for this skill is: **will a tiny blocking gate actually change behaviour at the moment scaffolding starts?** The cheapest test is a 60-100 line conversational version used on
cambium-swap plus two fresh projects. Telemetry, automation, self-evolution and `skill-ai-it` integration are parked until that returns.

The 60-100 line constraint governs `SKILL.md` only, not this brief. `SKILL.md` is loaded into context on every invocation; this brief is **not loaded at runtime at all**. It is not disposable either:
it is the provenance record for why the complexity was cut, what is parked, and what would earn each parked item back, so keep it available for the v0.2 decision. Do not shrink the brief for symmetry.

## Contents

- [Why it exists](#why-it-exists)
- [The prompt](#the-prompt)
- [v0.1 decision logic](#v01-decision-logic)
- [What counts as reality contact](#what-counts-as-reality-contact)
- [The gate, on RED only](#the-gate-on-red-only)
- [What "blocking" means at v0.1](#what-blocking-means-at-v01)
- [Ledger — episodes only](#ledger--episodes-only)
- [When not to fire](#when-not-to-fire)
- [Parked for v0.2](#parked-for-v02)
- [Acceptance tests](#acceptance-tests)
- [Calibration example: cambium-swap, 2026-09-16](#calibration-example-cambium-swap-2026-09-16)
- [Open decisions](#open-decisions)

---

## Why it exists

Operator's self-diagnosed pattern: design, component selection and governance proceed before the load-bearing assumption is tested. Surface area then grows faster than validated substance, every
addition raises the fixed cost of every future change, and eventually overhead exceeds motivation and the project is dropped. JDM and ATAR both died this way. cambium-swap shows the same signature.

## The prompt

```text
Create a global skill named skill-walk-before-run, v0.1, at
/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-walk-before-run/, installed by symlink.

Purpose: stop the "build before verifying the load-bearing assumption" pattern. When invoked, judge
whether the work about to happen is expansion sitting on unverified ground; if so, block it and
redirect to the cheapest real-world test.

Build exactly this package, and nothing more:
- SKILL.md, 60-100 lines: the whole runtime decision procedure, including the ledger format.
- README.md: purpose, invocation, package map, and where the mutable state lives.
- CHANGELOG.md: behavioural revisions between versions, starting at v0.1.

The boundary is NO ADDITIONAL RUNTIME BEHAVIOUR BEYOND SKILL.md. Supporting documentation is
allowed; decision logic, measurement infrastructure and automatic behaviour are not. So: no
scripts, no telemetry, no config file, and no references/, evals/, schemas/ or docs/ directories
yet - each has a named earn-in trigger in the brief's parked list. Thresholds stay visible in
SKILL.md rather than in configuration, because externalising them implies a tunability the trial
has not yet established.

The one permitted runtime write is an append to the episode ledger, and only on RED, waiver, or
RED-to-resolved. The ledger lives outside the package, under skills-data: the package is
specification, the ledger is state.

Implement, from the accompanying brief and without additions: step 0 (name the assumption), the
RED/AMBER/GREEN logic, what AMBER does, the four-step gate, the reality-contact definition, the
ledger format, and the stand-down cases.

Hard constraints:
- Step 0 runs first, always. Every signal is evaluated against the named assumption, so a verdict
  reached without naming it is meaningless.
- The assumption is fixed for the whole run: assumption -> signals -> verdict -> gate against the
  SAME assumption. If it must change, say so and recompute the verdict. Never switch silently.
- RED means THIS PROPOSED EXPANSION has not earned its prerequisites yet. It does not mean the
  project is bad. Keep that scope-relative framing in the wording, or /skill-wbr becomes a general
  project-quality critic and gets ignored.
- Verdicts cite what was observed. A skill that just agrees with whoever is talking launders
  opinion as process.
- Output fits one screen: verdict, the assumption, cheapest test, gate status, one next action.
- NEVER emit a plan, design doc, roadmap or report as the remedy. "Let us first design X properly"
  is the failure mode being prevented.
- Never build session-tracking, counters or any other measurement infrastructure to evaluate a
  signal. If the information is not already available, the signal is unknown, not RED.
- GREEN is fast and quiet. A gate that always fires gets ignored within a week.
- Irony constraint: if SKILL.md exceeds ~100 lines, it has failed its own test.

Invocation is manual only: /walk-before-run, alias /skill-wbr. No session-start auto-fire in v0.1,
and no self-modification: the skill never edits itself or its own logic.

Conventions: YAML frontmatter with name and description, Australian spelling, prose wrapped at 200
columns. Write the description to trigger on: adding a component, framework, dependency or
abstraction; starting a bake-off or evaluation; writing a third document about one undecided thing;
a project that feels overwhelming.
```

## v0.1 decision logic

```text
STEP 0 - name the assumption (always first)

  What unresolved assumption, if false, would invalidate the largest amount of the work about to
  happen?

  Choose the highest-blast-radius assumption that the proposed expansion MATERIALLY depends on.
  Do not descend into more fundamental assumptions whose answer would not change whether this
  work should happen now.

  Every signal below is evaluated against that assumption.

RED if any of:
  1. No real-world contact has tested the assumption the current expansion depends on.
  2. One unverified assumption blocks >= 3 downstream decisions.
  3. Available context shows >= 3 consecutive work sessions adding surface without new reality
     contact. If that history is not available, this signal is unknown, not RED.
  4. The core capability remains stubbed while peripheral architecture continues to expand.

AMBER if relevant reality contact exists but does not yet resolve the assumption the current
      expansion depends on.

GREEN if the current expansion is downstream of sufficiently verified assumptions and no
      unresolved higher-blast-radius unknown is being bypassed.
```

**Step 0 is the fragile part.** Scope it too shallow and everything passes; descend too far and nothing is ever verified enough. "Config push works" leads to "the API supports it" leads to "the vendor
can manage the device" leads to "the whole replacement strategy is viable" — all deeper, but only some change whether this work should happen now. The relevance boundary is the guard. State the chosen
assumption in one line so it can be argued with.

**RED versus AMBER.** RED is *nothing* has tested the assumption. AMBER is something has, partially, and it remains open. When genuinely torn between the two, say which way you leaned and why rather
than picking silently.

**What each verdict does:**

```text
RED     -> stop expansion and verify.
AMBER   -> expansion may proceed; expose the unresolved assumption and its closing test.
GREEN   -> proceed quietly.
UNKNOWN -> a signal with no available evidence contributes nothing. Never manufacture evidence.
```

AMBER is information, not withheld permission, and writes no ledger entry. GREEN is scope-relative on purpose: adding a component that is not yet integrated is normal and healthy; what is not healthy
is adding it while something further upstream remains untested.

## What counts as reality contact

Dated, raw output from the real target system: an authenticated API response, a real device or service returning data, a real file processed, a real user completing a task.

Not: a mock or fixture, vendor documentation, a plan, a passing test against code the project wrote itself, a governance check, or a model asserting that something should work.

## The gate, on RED only

```text
G1. Confirm the Step 0 assumption is the blocking one. If evidence found while evaluating the
    signals proves Step 0 was wrongly scoped, correct Step 0 explicitly and recompute the verdict
    before continuing.
G2. Define the cheapest real-world test of it.
G3. State the disconfirming result BEFORE running it.
G4. Run that test before adding another component, document or framework.
```

The invariant matters more than any single step: **assumption, then signals, then verdict, then gate against the same assumption.** Discovering a different unknown inside the gate and quietly gating
on that instead turns the verdict into a moving target.

G3 is the step most likely to be skipped and the one that matters most: pre-registering the result that would invalidate the direction is what stops a failed test being reinterpreted as a reason to
build more.

## What "blocking" means at v0.1

Worth being honest about: at v0.1 there is no enforcement mechanism. "Blocking" means the agent refuses to proceed with expansion within the session, and the RED episode is recorded. That is weak.
Whether that weak form is enough to change behaviour at the moment of scaffolding is exactly the unknown being tested — so it should not be strengthened before the trial, or the trial proves nothing.

## Ledger — episodes only

One file, all projects: `/Volumes/Data/_ai/_skills/skills-data/skill-walk-before-run/ledger.md`. Append on RED, on waiver, and on resolution. Never on GREEN or AMBER.

```text
2026-09-16 | cambium-swap | RED
assumption=real cnMaestro auth/read works with held credentials
reason=no real-system contact
next_test=<test>
waiver=0
learned=<optional: a miss, a false positive, wording that did not land>

2026-09-17 | cambium-swap | RESOLVED
assumption=real cnMaestro auth/read works with held credentials
result=PASS
killed=<none>
```

A waiver is allowed and recorded with its reason. Two waivers on the same assumption is itself a finding, and should be stated plainly on the next invocation — that is avoidance becoming visible.

`learned=` is **capture only**. The skill never acts on it and never edits itself; the field exists so the revisit decision is driven by evidence rather than memory. Self-modification during the trial
would make the trial measure a moving target.

## When not to fire

Stand down in one line, without lecturing, on: irreversible-foundation work where a wrong foundation genuinely costs more than delayed verification; design as the deliverable, where there is no
downstream implementation to invalidate; reality contact blocked by a third party, where the question becomes "what is the cheapest available proxy?"; deliberate learning projects where building the
scaffold is the goal; and genuinely cheap throwaway work.

## Parked for v0.2

Not discarded. Each has a named trigger; revisit only after the three-project trial.

- **Evidence discipline (OBSERVED / INFERRED / UNKNOWN)** — *Parked 2026-09-16, source: comparative review against a sibling skill, Teycir/Assumptions (github.com/Teycir/Assumptions, verified real).*
  Likely redundant with what's already here: the reality-contact definition plus the RED/AMBER/GREEN/UNKNOWN-signal model already separates "no evidence" (UNKNOWN, contributes nothing) from "evidence
  exists but doesn't resolve the assumption" (AMBER, functionally INFERRED) from "evidence resolves it" (reality contact, functionally OBSERVED) — a second, parallel vocabulary for the same three
  states is accidental complexity, not new coverage. *Revisit:* only if the trial produces a real case where a verdict was miscalibrated specifically because "no evidence" and "weak/inferred evidence"
  weren't distinguishable — not on design taste alone.
- **Step 0 as an explicit assumption → evidence → consequence-if-false → falsification-test chain** — *Parked 2026-09-16, same source.* Documentation-only restatement of what Step 0's own phrasing
  ("if false, would invalidate...") and the Gate (G2 cheapest test, G3 disconfirming result) already do; changes no behaviour. *Revisit:* fold into this brief's rationale text at the next scheduled
  revision, only if real cases show newcomers misread Step 0 without the diagram — not as a standalone addition.
- **State scope / what-wasn't-checked explicitly in Output** — *Parked 2026-09-16, same source.* Signal 3 already does this narrowly ("unknown, not RED, if history isn't available"); this would
  generalise it to the one-screen Output so a reviewer can see what evidence was actually checked vs assumed, mirroring Teycir's "don't write 'none found' without saying where you looked." *Revisit:*
  after the trial, if real cases show the current Output leaves this ambiguous.
- **Self-evolution** — the skill updating its own logic from ledger evidence. *Revisit:* after the trial, using accumulated `learned=` entries. Never during it — a self-modifying skill makes the trial
  unreadable.
- **Delivery mechanism** — how `/skill-wbr` gets invoked without having to remember to type it. Two candidates: templating a trigger line into every bootstrapped project's AGENTS.md via `skill-ai-it`,
  or a hook. A hook is the better bet: AGENTS.md text is advisory and competes for attention with everything else in context, and it must be propagated into and unpicked from every project, whereas a
  hook is configured once and actually executes. Prefer a SessionStart hook that does no judging — it reads the ledger and surfaces an unresolved RED in one line. Avoid a blocking PreToolUse hook: it
  cannot distinguish a premature Write from a legitimate one, so it would fire constantly and be disabled, which is how the Stop hook died. *Revisit:* only after the trial, and only if the manual gate
  proves itself. Add neither mechanism during the trial — all three projects must stay under one condition (manual invocation only), or the experiment silently becomes "reminder plus gate" rather than
  "gate".
- **`references/`** — decision-model, reality-contact and stand-down semantics split out of SKILL.md. *Revisit:* on observed pressure of either kind: SKILL.md cannot stay within its context budget, OR
  repeated real cases show a semantic area needs more explanation than belongs in the runtime path. The second can fire while SKILL.md is still 85 lines, if three projects read "reality contact" three
  different ways.
- **`evals/`** — a cases file plus fixtures. *Revisit:* when a runner exists, or the trial has produced real cases to encode. A suite with no runner cannot fail. Synthetic fixtures become useful for
  regression and adversarial testing once grounded in real failures or boundary cases, but they are not a substitute for the initial real-project trial.
- **`references/calibration-cases.md`** — *Revisit:* at the third real case. Two is a coincidence.
- **`schemas/ledger-entry.md`** — *Revisit:* if the ledger format outgrows the roughly ten lines it currently occupies inside SKILL.md. **Actioned 2026-09-16, pre-first-write** — see open decision #5.
- **Ledger schema** — *Revisit:* after the trial, if the recorded entries cannot establish whether a RED materially changed the next action. The hypothesis under test is that a RED changes behaviour;
  the ledger currently records only that a RED happened. Do not add a field now, because that alters the trial surface mid-experiment — but at revisit time, do not read "RED recorded" as "behaviour
  changed". **Partly actioned 2026-09-16** (`ts` local-offset, `branch`) — judged pre-first-write hardening rather than the mid-experiment case this caution describes, since zero entries existed; see
  open decision #5. The caution still stands for any further field additions once real episodes exist. Candidate field if this triggers: a lightweight evidence locator on the RESOLVED entry (what
  specific evidence — date, API response, device — proved the result), per the Teycir/Assumptions comparative review, 2026-09-16.
- **`docs/design-rationale.md`** — *Revisit:* never. This brief is that document, and duplicating it creates two sources of truth.
- **Measurement extras** — stand-in expiry dates, surface budget, artifact-to-evidence trend, change-overhead ratio, component proof ratio, temporal staleness in AMBER. *Revisit:* after the trial, if
  a real miss points at one.
- **Automation extras** — ledger analytics, helper scripts, cross-runtime install policy, sibling-skill boundary docs. *Revisit:* after the trial.

The target architecture is not in dispute: `SKILL.md` as executable contract, `references/` as semantics, `evals/` as proof, `schemas/` as state format, `skills-data/` as state. Only the sequencing
is. Each piece lands when something actually presses on it, and retrofitting is cheap here precisely because nothing points at those directories yet.

## Acceptance tests

1. **Positive control** — cambium-swap as at 2026-09-16 returns RED and names the absence of real-Cambium contact as the unresolved assumption.
2. **Negative control** — a project with fresh reality contact returns GREEN in under a minute and writes nothing.
3. **Adversarial** — "let us design the plugin architecture properly first", on a project with zero contact, is refused and redirected.
4. **Step 0 visibility** — in every verdict, the assumption under test is stated explicitly and is arguable.
5. **Assumption stability** — the gate operates on the same assumption the verdict was computed from, or the verdict is visibly recomputed.

Then the actual trial: use it on cambium-swap plus two fresh projects, all three under one condition - manual invocation only - so the trial measures a single intervention. If it stops expansion at
the right moment without becoming annoying, consider the parked list. If it does not, do not add telemetry or automation. First determine whether the failure is the concept, the trigger, or the
intervention itself — three projects can falsify this intervention, not the underlying idea.

## Calibration example: cambium-swap, 2026-09-16

Zero authenticated calls to a real Cambium device, ever — every test to date ran against `cambium-mock`, written by the project. Meanwhile: roughly nineteen components specified in the candidate
stack, six controller documents including a 3,300-line scaffold, 2,240 governance checks, a ten-container lab, and a Day-0 stub at the core while the observability periphery is fully specified. Four
or more decisions wait on the one assumption. Triggers RED on signals 1, 2 and 4.

Step 0 for that project: *a real cnMaestro-managed device will authenticate and return device facts over an interface we can drive.* Everything in the candidate stack sits downstream of it. Note what
is out of scope: "the whole vendor-exit strategy is viable" is deeper, but its answer would not change whether this week's work should happen.

Correct next action was never stage 7 or the vertical slice. It was one authenticated call against one real cnMaestro-managed device — about an hour, credentials already on record as evidence E77.

Note the second-order trap this illustrates: the governance apparatus is itself surface. High quality, and still raising the fixed cost of every future change — which is also why manufacturing
measurement infrastructure to answer a signal is prohibited rather than merely discouraged.

## Open decisions

1. **Name — decided 2026-09-16:** `skill-walk-before-run`, alias `skill-wbr`. Invoked as `/skill-walk-before-run` or `/skill-wbr` (renamed from the originally proposed `/walk-before-run`, still
   visible verbatim in the fed prompt above, to match the skill's actual name).
2. **Ledger path — decided 2026-09-16:** colocated at `skill-walk-before-run/ledger.md`, alongside `SKILL.md`, rather than under the `skills-data` root proposed earlier in this brief. The package
   still separates specification from state conceptually (`SKILL.md` is versioned behaviour, `ledger.md` is an append-only log), but both now live in the same directory rather than in separate repos.
   Operator call, made at build time, in favour of simplicity over the storage-routing guide's usual persistent-state-outside-source-repo split. Revisit if this causes real friction — e.g. ledger
   entries cluttering diffs of the versioned skill — in which case move it back out to `skills-data` per the original plan.
3. **Revisit point** — after three projects, decide what if anything comes off the parked list.
4. **Where this brief lives after the build — decided 2026-09-16:** moved to `skill-walk-before-run/BRIEF.md`, colocated with the shipped skill as its baseline/provenance reference, rather than left
   in `pending_skills/`. It stays out of the runtime decision procedure (`SKILL.md` alone still carries that); it is documentation, filed the same way `README.md` and `CHANGELOG.md` are.
5. **Ledger format hardened — decided 2026-09-16, pre-first-write:** `ledger.md` (colon-delimited text) → `ledger.jsonl` (one JSON object per line), with `ts` (ISO 8601, local UTC offset, replacing
   date-only) and `branch` (git branch at invocation, `"n/a"` if not a git repo) added to the field set. Operator call, made when `ledger.jsonl` still had zero entries — no trial data existed to be
   made inconsistent by the change, so this is judged as the same class of decision as #2 (pre-first-write hardening), not the mid-experiment schema churn that § "Parked for v0.2" explicitly warns
   against. `schemas/ledger-entry.md` now carries the field reference (the earn-in trigger for that file — "outgrows roughly ten lines inside SKILL.md" — fired for real once `ts` and `branch` were
   added). JSONL chosen over TOML: append-only single-writer log, read by both a human and (once built) the parked SessionStart hook; a malformed JSONL line stays isolated, where a bad append risks a
   whole TOML document or single text block. Revisit if real episodes show JSONL is harder to skim than the old text block was — the fallback is the same append-only shape, just re-keyed.
6. **Invocation defaults to the calling project — decided 2026-09-16, post-trial-round-one:** without an explicit project name, entry 1 of `ledger.jsonl` evaluated skill-walk-before-run's own
   construction rather than any of the three trial targets, because that was the only expansion actually live in the invoking session. Reproduced once, fixed for entries 2–4 by naming the project
   explicitly on each invocation. Operator call: make that explicit-naming behavior the documented default rather than requiring it every time. `SKILL.md`'s Invocation line, `README.md`'s Invocation
   section, and `schemas/ledger-entry.md`'s `project` field description all updated. Not a mid-trial confound in the sense the "no design rounds" caution means — entries 2-4 already used explicit
   targeting in practice; this documents and defaults behavior already exercised, it doesn't change what the gate evaluates going forward for a project once named. Revisit if a session genuinely has
   no clear "calling project" (e.g. a shared root session spanning many working directories) and the default picks something the operator didn't mean — same failure mode as entry 1, just not yet
   observed under the new default.

**Amended same day:** "the calling project" was left undefined — no rule for deriving the actual string. Operator caught this by noticing entry 3 recorded `"project":"japan-jdm"`, which matches no
canonical source. Checked three candidate rules against all four real entries: git top-level directory name resolves to `apn` for cambium-swap and `me` for atar — both wrong, and both shared by
unrelated projects in this workspace's `_project/project_stuff/` monorepo layout, so rejected outright. Working-directory leaf name and the `mcp-project-context` registered name agree and are correct
for cambium-swap and atar; for jdm, `mcp-project-context` has it registered as `jdm` (not `japan-jdm`) — matching neither the leaf name theory's `jdm` nor what was actually recorded. Rule adopted:
prefer the `mcp-project-context` registered name, else the working directory's leaf name; never git top-level. **Correction, same day:** operator asked for `ledger.jsonl` entry 3 to be fixed in place
rather than left as historical record — `"japan-jdm"` → `"jdm"`. Overrides the "left as-is" plan stated here minutes earlier; the rest of that entry (assumption, reason, next_test) is untouched.
7. **Project write-back — decided 2026-09-16, post-trial-round-one:** all three trial RED verdicts were invisible to the target project's own governance surface — nothing in cambium-swap's,
   japan-jdm's, or atar's own tracking showed a RED had been raised, only `ledger.jsonl` did. Added: on RED or RESOLVED (same condition as the ledger itself), append one line under the target
   project's own `SCRATCHPAD.md` § Open items, if that file exists — never create one. `ledger.jsonl` stays the sole source of truth; the SCRATCHPAD line is a pointer only, appended not edited, so
   resolving a RED adds a second line rather than risking a fragile in-place edit against a file this skill doesn't own. Deliberately did not extend this to projects without a `SCRATCHPAD.md`, and
   deliberately did not try to tick the original checkbox on resolution — both would require guessing at or editing a governance surface this skill doesn't control. Revisit if the trial's remaining
   projects use a different tracking convention this pointer format doesn't fit.
8. **Check ledger before re-deriving — decided 2026-09-16:** operator raised a forward-looking concern — repeat invocations on the same project re-deriving Step 0 from scratch, ignoring prior
   findings. Unlike #6 and #7, no instance of this has actually happened in the trial (each of the three projects has exactly one entry). Rejected the proposed fix (a new per-project dotfile) because
   it would duplicate `ledger.jsonl` into a second, competing index — the exact anti-pattern flagged in the Teycir/Assumptions parked items. Added the cheap version instead: Step 0 now reads
   `ledger.jsonl` for the calling project first and surfaces an existing unresolved RED rather than re-deriving. Zero new files, zero new source of truth, read-only against what already exists —
   judged in-bounds despite no trial evidence yet, specifically because of that low cost/risk, not as a precedent for adding other un-evidenced ideas.
9. **Per-project mirror — decided 2026-09-16:** operator clarified the dotfile idea #8 rejected was about a different problem — not a lookup index (that's what #8 correctly rejected, since it would
   compete with `ledger.jsonl`), but resilience: every project's findings currently live in exactly one file, in one repo (`skills_stuff`) that isn't the project they're about. If that file or repo is
   ever lost, cambium-swap/atar/jdm's own findings go with it, with nothing recoverable from their own side. Added `.wbr-ledger.jsonl`, a verbatim per-line mirror written to the target project's own
   root on the same RED/RESOLVED condition as the ledger itself, created if absent (unlike the `SCRATCHPAD.md` pointer, which never creates). Explicitly a recovery copy, not a second source of truth:
   Step 0's ledger-check (#8) only falls back to it when `ledger.jsonl` itself is missing or unreadable. Distinct from #8's rejection — that was about using a dotfile as the primary read path; this
   one is read-never-under-normal-operation, write-only insurance.

**Amended same day:** operator asked whether two-way sync between `ledger.jsonl` and the mirrors is warranted. Rejected — no write path today ever causes them to diverge (canonical is always written
first, mirror second), so there's nothing to keep in sync; two-way sync would only matter for a manually-edited mirror, and conflict resolution for that is real complexity this skill shouldn't carry.
Confirmed the existing per-invocation mirror write already *is* one-way sync (skill → project); nothing new needed there. Added instead: a documented one-time manual recovery procedure in README.md —
if `ledger.jsonl` is ever actually lost, reconstruct it by concatenating every known project's `.wbr-ledger.jsonl`, sorted by `ts`. Deliberate and manual, not automatic.
10. **Ledger-check bug fix — decided 2026-09-16:** operator asked how the skill assesses whether a prior entry is still valid, and whether it adds vs edits on minor changes. Edit was never the answer
    — append-only stands, the jdm naming fix (#6's amendment) was an explicit one-off override, not a precedent. But the question exposed a real gap in #8's own logic: it only checked whether the
    assumption still matched, never whether the test had actually been run since — so a RED whose `next_test` was quietly completed would be re-surfaced as still-open forever instead of getting a
    RESOLVED entry. Fixed: Step 0 now checks that first. If the assumption itself has moved on (no longer the same or materially similar), it still isn't reused at all — falls through to a fresh Step
    0, which appends a new entry as normal.
11. **Mirror self-heals against deletion — decided 2026-09-16:** operator pointed out the mirror-write spec only covered "file absent" as "never created yet" — if the target project's own
    `.wbr-ledger.jsonl` were deleted after having real history, the next write would recreate it with just that one new line, silently losing everything earlier even though `ledger.jsonl` still has
    it. Fixed: on write, if the mirror is missing for any reason, seed it from `ledger.jsonl` filtered by `project` first, then append the current entry — same self-healing outcome whether the file
    never existed or was deleted. No new mechanism, no new field; canonical already had the data needed.
12. **Ledger-check sequencing bug — decided 2026-09-16:** operator asked what happens if a project has an existing unresolved RED but a genuinely new, different RED has since developed. Exposed a real
    bug in #8/#10's wording: the ledger-check ran "before anything else," ahead of Step 0 actually naming the current assumption — so "same or materially similar" had nothing yet to compare against,
    and an agent could plausibly treat any unresolved RED on the project as a status check without ever checking whether the current proposed work is about something else entirely. Fixed by
    reordering: Step 0 always names the current assumption first, as originally designed; the ledger-check runs after, matching only against that named assumption. Made explicit for the first time: a
    project may hold more than one unresolved RED at once if the assumptions are genuinely different — an old open RED does not block or absorb a new, different one.
13. **Multiple unresolved REDs with a genuine order — priority rule — decided 2026-09-16:** operator asked what the gate should recommend when a project holds more than one unresolved RED (per #12)
    and those REDs are not independent but form a real sequence — resolving an earlier one is a precondition for a later one being testable at all. The concern: an agent could point the "one next
    action" at a later step in that chain (e.g. step 10) because it looks more relevant to whatever prompted the current invocation, while an earlier, more foundational RED in the same chain sits
    untested. That reproduces the exact failure this skill exists to stop, just hidden inside "which open RED do I address" rather than inside Step 0 itself. Rule adopted: when unresolved REDs on the
    named assumption's chain have a genuine dependency order, the gate's next action names the earliest untested step in that order, never a later one, regardless of which step feels most relevant to
    the current expansion. This is a tie-breaking rule for the gate's output only — no new mechanism, no new ledger field; Step 0 and the ledger-check (#8, #10, #12) already surface every unresolved
    RED matching the assumption. Scope boundary: this only applies when the REDs are genuinely sequential. If they are independent, parallel assumptions with no real dependency between them, #12
    governs instead — each stands on its own and none blocks or reorders another. Revisit if a real case shows "genuine order" is itself hard to judge (e.g. two REDs that look sequential but are not),
    in which case this rule needs its own relevance boundary the way Step 0 got one.
14. **RETRACTED same day — cambium-swap `next_test` correction wrongly applied as an in-place edit:** re-verifying the still-open cambium-swap RED surfaced a real error in the recorded `next_test` (it
    assumed real cnMaestro/device access was cheaply available off the support-portal login; `SCRATCHPAD.md:36` — "No lab work and no production access yet" — shows that login only ever supplied
    documentation, never live device data) and a real rejection of a candidate fix (swapping `genieacs-sim` for `SimulaTR69`: still a simulator regardless of fidelity, and TR-069/GenieACS is scoped to
    cnPilot/CPE only per `option-3-architecture.md:142`, not the SNMP/cnMaestro-API territory the RED actually gates). Both findings were correct. The mistake was *how* they were applied: the entry's
    `next_test`/`learned` fields were overwritten in place, on the claimed authority of #6's amendment — but #6 was an operator-requested one-off fix of a pure metadata typo (a project name), not a
    precedent for rewriting an entry's substantive reasoning. Append-only means the entry is what was written at that timestamp; a later correction is new evidence and belongs in a new entry, not a
    rewrite of the old one — exactly the shape #9's mirror-resilience design and #10's "falls through to a fresh Step 0" language already assume. Caught when the operator pointed out the
    contradiction: this same brief had just described editing as the rare exception, then this decision used it as if it were the norm. Also stale in its own right — see #15. Reverted: both
    `ledger.jsonl` and the cambium-swap `.wbr-ledger.jsonl` mirror restored to their original, pre-edit text. No further action needed here — #15's proper append already carries the substance forward.
15. **cambium-swap next_test corrected via a proper append, and the "stand-down" call itself corrected — decided 2026-09-16, by direct project-side work, not this skill's own invocation:** the
    corrected reasoning in #14 additionally over-reached: "no production access" (`SCRATCHPAD.md:36`) was read as meeting the stand-down condition "reality contact blocked by a third party," but the
    operator confirmed directly that a physical bench/demo Cambium unit is available — not production, not blocked. A new ledger entry (`ts` 2026-09-16T16:32:36+10:00) was appended — not an edit — to
    both `ledger.jsonl` and the project mirror, explicitly superseding the original 14:39:57 entry and noting the stray in-place edit #14 made (by then already reverted) was itself stale the moment
    the bench unit was confirmed. Verdict still RED; `next_test` now: (a) pull real SNMP/API responses from the bench unit for the ePMP/cnMatrix/cnWave estate, (b) only if the bench unit turns out to
    be a cnPilot/CPE model, add GenieACS to `wc-lab`, smoke-test wiring with `genieacs-sim`, then repoint at the real unit for CWMP — preserving #14's still-valid finding that a simulator alone never
    substitutes for that repoint. Lesson recorded in that entry's own `learned` field: absence of a specific phrase ("no production access") in project docs is not the same as absence of all real-
    hardware access — ask the operator directly rather than inferring a stand-down from adjacent wording. Open item unchanged from #14: which device family the bench unit actually is.
16. **`scripts/append_entry.py` added, plus an OPA hard-block on any other write path — decided 2026-09-17:** a cambium-swap-side script bypassed this skill entirely, writing a RESOLVED entry straight
    into `ledger.jsonl` via a raw Python `open(...).write()` instead of invoking `/skill-wbr`. It landed at the wrong path (a `~/.claude/skills/` runtime install, not the canonical `skills_stuff`
    copy), skipped schema validation, and skipped the project mirror and SCRATCHPAD pointer entirely. This is a departure from v0.1's "no helper scripts" stance recorded in the brief's revision note
    above — that stance was about not speculatively building tooling before a first trial; this is the opposite case, a script added in direct response to an actual bypass that already happened, not a
    hypothetical. Two changes: (1) `scripts/append_entry.py` is now the only sanctioned writer — it validates against `schemas/ledger-entry.md`, appends to canonical `ledger.jsonl`, and performs the
    mirror + SCRATCHPAD write-back from the "Project write-back" section in the same call, so a valid entry can't land in the ledger without also reaching the mirror. (2) The workspace's existing OPA
    policy gate (`agent_authz.rego`, already in the PreToolUse chain for every Bash/Write/Edit call) now hard-blocks any Bash command referencing `ledger.jsonl`/`.wbr-ledger.jsonl` alongside a write
    marker (`.write(`, `>>`, `sed -i`, `tee -a`) unless the command invokes `append_entry.py`, and hard-blocks Write/Edit targeting either filename outright — this fires ahead of the "safe bash
    prefix" allowlist (which included the bare `python3 -c` prefix that let the original bypass through unprompted) and ahead of the general governed-workspace write-allow. SKILL.md's Ledger and
    Project write-back sections were rewritten to call the script instead of describing a manual append, since the manual form is now what the gate blocks. 38/38 `opa test` cases pass, including new
    cases for this rule; verified live against `opa run --watch` (already running, picked up the change without restart) that the exact incident command is now blocked and that invoking the script is
    not.
