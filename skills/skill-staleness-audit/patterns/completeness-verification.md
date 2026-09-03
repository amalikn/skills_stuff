# Completeness verification

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

The exit gate. Phases 0–7 *find and fix*; this phase **proves nothing was left**, and states precisely what kind of staleness cannot be proven absent from inside the project.

Without this, the audit ends on an assertion. The whole point of the skill is that assertions nobody checked are how the defects got there.

## Contents

- [The guarantee, stated honestly](#the-guarantee-stated-honestly)
- [Claim inventory](#claim-inventory)
- [The verification matrix](#the-verification-matrix)
- [Running the sweep](#running-the-sweep)
- [History is preserved, not deleted](#history-is-preserved-not-deleted)
- [The four residual classes](#the-four-residual-classes)
- [Exit criteria](#exit-criteria)

---

## The guarantee, stated honestly

After a completed run, this holds:

> **Every checkable claim in the project has been verified against its source, or is explicitly marked as historical, or is listed in the residual-risk register as unverifiable from inside the
> project.** There is no fourth state.

Read what that does and does not promise.

**It does promise:** no self-contradicting figures; no count, date, path or cross-reference that disagrees with the filesystem; no superseded position presented as current; no verdict corrected in
prose but not in data; no derived artifact whose generator still emits the old model; every restated threshold agreeing with its owner.

**It does not promise that a claim about the external world is true.** Whether a market price, a regulation, a vendor's SLA, or a third-party API's behaviour is still accurate cannot be established by
reading the project. What the audit guarantees there is narrower and still valuable: **every such claim is labelled with its provenance and its as-at date**, so a reader knows what to re-check and
when it was last checked.

Say this distinction out loud in the report. An audit claiming more than it can prove is itself the defect.

## Claim inventory

The verification sweep is not "grep for the old values again" — that only finds what you already knew to look for. It is: **enumerate every checkable claim, then verify each one.**

A claim is checkable when something in the project or the filesystem can contradict it.

| Claim form | Example | Verified against |
|---|---|---|
| **Count** | "27 files", "56 checks", "N sites" | Recount from the thing counted |
| **Date** | "Last reviewed", "as at", "snapshot" | Newest relevant change |
| **Path / reference** | Any link, import, or `see X` | Filesystem |
| **Threshold** | Any gate, limit, rate, cap | The owner |
| **Verdict / status** | "recommended", "deprecated", "production" | Every store of it, prose *and* data |
| **Derivation** | "generated from X", "derived from Y" | Regenerate and diff |
| **Provenance** | "verified", "observed", "measured" | The record it claims |
| **Capability** | "supports X", "handles Y" | The code or a test |
| **Quantity relation** | "double", "half", "the only one that…" | Recompute |

**"The only one that…" deserves special attention.** Uniqueness claims are quietly the most fragile thing in any corpus: they were true when written, and adding a second instance falsifies them
silently, with nothing to grep for. Enumerate and recount every one.

## The verification matrix

Each claim ends in exactly one cell. The three counts must reconcile against the total.

| State | Meaning | Evidence required |
|---|---|---|
| **VERIFIED** | Checked against its source this run | The command or comparison that checked it |
| **MARKED-HISTORICAL** | A dated record of what was true then | The marker that exempts it, e.g. `count:asat` |
| **RESIDUAL** | Cannot be verified from inside the project | An entry in the residual-risk register naming what would settle it |

Anything not in one of those three is unexamined, and the audit is not finished.

## Running the sweep

Run **after** Phase 5, so the checks written there participate.

```bash
# 1. The suite, in full. Report the count before and after the audit.
<project check command>

# 2. Regenerate every derived artifact; the diff must be only what you intended.
<each generator>; git diff --stat

# 3. Every old value, repo-wide, excluding audit-trail surfaces by design.
grep -rn '<old-value-1>\|<old-value-2>' --include='*.md' --include='*.py' --include='*.yaml' . \
  | grep -v 'archive/\|CHANGELOG\|\.git/'

# 4. Every link and path reference resolves.
# 5. Every count claim recomputed.
# 6. Structured config parsed and inspected — not read as text.
# 7. Evidence byte-compared against committed.
```

**A clean grep is necessary and nowhere near sufficient.** It proves the strings you thought of are gone. Steps 1, 2, 6 and 7 are what catch the rest, and Phase 4's reasoning is what catches
assumptions that were never strings at all.

### The inverse sweep

Then check the direction that grows silently: **does anything exist that no catalog names?**

- A file in a catalogued directory that the catalog omits.
- A script absent from the task runner, or a runner recipe with no script.
- A surface restating a registered threshold without being registered.
- A new document not in the index.

*Catalog names something that vanished* and *something exists that no catalog names* are different defects. Only the second grows while you are not looking.

## History is preserved, not deleted

"No stale information" does **not** mean "no old information". The two are opposites in a project that keeps records.

| Content | Treatment |
|---|---|
| A live claim that is now false | **Correct it** |
| A dated record of what was true then | **Keep verbatim.** Mark it exempt |
| Superseded reasoning behind a decision | **Keep.** Usually the most useful part |
| An accepted decision later contradicted | **Mark in place.** Never rewrite |
| A prior version of a figure, in a change log | **Keep.** Audit trails are supposed to contain superseded figures |
| An external source capture | **Keep byte-identical.** Re-capture instead of editing |

The test: **would a reader mistake this for a current assertion?** If yes, it needs a marker. If it is plainly dated and plainly historical, it is evidence, and rewriting it to satisfy a linter
destroys the record.

## The four residual classes

Some staleness genuinely cannot be resolved from inside the project. Name each instance in the residual-risk register rather than leaving it implied.

1. **External-world facts** — market prices, regulations, vendor terms, third-party behaviour. Verify the *label and as-at date*, not the fact.
2. **Unset parameters** — a threshold the project acknowledges it has not decided. Not stale; **undecided**, and must not be silently treated as a value.
3. **Structural limitations** — a collector that cannot capture a field the rules now require. Declare it in the artifact itself, not only in the report.
4. **Thin evidence** — a figure resting on too few observations to carry the weight placed on it. Record the count; state what would settle it.

## Exit criteria

All must hold. Any failure means the audit is incomplete — say so rather than closing.

- [ ] **Coverage accounting reconciles** — examined + exempt + out-of-scope = total files
- [ ] **Claim matrix reconciles** — verified + marked-historical + residual = total claims
- [ ] Full check suite passes; count reported before and after
- [ ] Every derived artifact regenerated; diffs are only what was intended
- [ ] Old-value sweep clean outside audit-trail surfaces
- [ ] Inverse sweep clean — nothing exists that no catalog names
- [ ] Every structured config parsed and inspected, not read as text
- [ ] Evidence byte-compared against committed
- [ ] Every new check negative-tested in both directions
- [ ] Residual-risk register written, including errors made during the audit
- [ ] The report states **what could not be verified from inside the project**

**Do not report "no stale information remains" without this gate.** Report what was verified, how, and what remains — which is a stronger claim, because it can be checked.
