# Defect taxonomy

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

The nine patterns, ordered by how often they have been the **expensive** one rather than how often they occur. Each carries its signature, how to detect it, a real instance, and the fix that holds.

Use during **Phase 1** to seed the register, and again during **Phase 4** to check nothing string-shaped was missed.

## Contents

- [1. A threshold restated across surfaces](#1-a-threshold-restated-across-surfaces)
- [2. A verdict in prose that never reached the data layer](#2-a-verdict-in-prose-that-never-reached-the-data-layer)
- [3. A superseded figure inside a template that gets copied](#3-a-superseded-figure-inside-a-template-that-gets-copied)
- [4. A back-solve computed against a floor that has changed](#4-a-back-solve-computed-against-a-floor-that-has-changed)
- [5. Counts and dates](#5-counts-and-dates)
- [6. A machine-readable map with a misplaced key](#6-a-machine-readable-map-with-a-misplaced-key)
- [7. A generator that re-emits the old model](#7-a-generator-that-re-emits-the-old-model)
- [8. Immutable evidence silently reformatted](#8-immutable-evidence-silently-reformatted)
- [9. Inputs with no provenance label](#9-inputs-with-no-provenance-label)
- [Detection summary](#detection-summary)

---

## 1. A threshold restated across surfaces

**Signature.** One number — a gate, cap, rate, limit — legitimately restated in many documents so readers need not chase the owner. One surface moves; the rest do not.

**Detection.** Find the owning rule, extract the value, grep every active file for the old value *and* for the phrasings that introduce it. Then grep for the **words** without the number: a surface
that says "the profit gate" without stating it may still be describing the old shape.

**Real instance.** A profit gate became dual — `max($2,500, 15% × landed)` — and eleven surfaces were updated. Three were not, two of them documents filed with a licensing authority. They survived a
phrase-guard because the guard matched `profit gate $2,500` but not `$2,500 profit gate`: **it only knew the word order its author had used.**

**Fix that holds.** A registry of restating surfaces, enforced both ways — every registered surface must state the current value, and **any unregistered file matching a gate phrasing must fail**. When
adding a phrasing to the guard, add *every* word order and allow for markdown emphasis between the words and the number.

## 2. A verdict in prose that never reached the data layer

**Signature.** An analysis is reversed and the documents are corrected, but the machine-readable copy — YAML, JSON presets, a generated table — still carries the old verdict. Tools keep returning the
superseded answer while the prose says otherwise.

**Detection.** For every verdict, status or recommendation in prose, ask **where else it is stored as data**. Grep the data files for the verdict vocabulary (`RECOMMENDED`, `APPROVED`, `PASS`,
`status:`), not just the prose.

**Real instance.** A vehicle recommendation was reversed on real auction evidence — landed cost above the highest observed asking price, ROI −29.6%. Prose, flowchart and decision matrix were all
corrected the same day. `process/vehicle-classes.yaml` still read `verdict: RECOMMENDED — best risk-adjusted non-kei found`, and the preset still carried the disproven purchase price labelled merely
`ESTIMATED`.

**Fix that holds.** State the rule that **a verdict is an outcome, not an opinion**, and enumerate its storage locations in the companion-file table. Where possible, make the generated surface render
the verdict so the contest becomes visible in the runbook rather than only in the source.

## 3. A superseded figure inside a template that gets copied

**Signature.** A stale figure in an append-only document is history. The same figure in a **copy-me-per-item template** is a live operating instruction that will be followed.

**Detection.** Identify every file whose own text says *copy this*, *per class*, *per vehicle*, *per customer*. Treat their contents as code, not prose. Then find copies already taken and check them
too.

**Real instance.** A comparables template instructed `require base margin ≥ 30% and target profit ≥ $2,500`. Both limbs had been superseded — margin demoted to advisory, profit gate made dual. Anyone
copying it would have run a wrong go/no-go. The copy already taken had additionally inherited a superseded cap and an uncorrected build window.

**Fix that holds.** Amend at the **point of use**, not only in a banner at the top: strike the old line, state the current one beside it. Then reconcile every copy already taken, and note in the
template that copies made before date *X* need reconciling.

## 4. A back-solve computed against a floor that has changed

**Signature.** A tool solves backwards from a target — a maximum bid, a break-even, a required price — and the target is a constant that a gate has since outgrown. Output stays plausible and is now
wrong in the dangerous direction.

**Detection.** **This one has no stale string.** Find every back-solve, ceiling or "what do I need for *N*" computation and ask what floor it uses and whether that floor is still the gate.

**Real instance.** A scenario runner printed `Max bid AUD` back-solved against a flat $2,500 target. Below $16,667 landed the flat limb bound and the two coincided — which is exactly why it survived.
Above it they diverged: on a $42,032 vehicle the gate floor was $6,305, so the printed ceiling was ~$3,800 of profit too generous. That figure is the one an operator carries into a live auction.

**Fix that holds.** Where the target legitimately serves a different question, **do not silently redefine it** — print the divergence at the point of use: the floor, the shortfall, and the parameter
value that would be gate-consistent. Register the tool as a threshold-restating surface.

## 5. Counts and dates

**Signature.** "27 files", "56 checks", "Last reviewed: …", "snapshot: 9 August". Cheap to state, never recomputed, and quietly wrong.

**Detection.** Grep for `\d+ (files|checks|documents|surfaces|entries)` and for `Last reviewed|snapshot|as at`. Compare each against the filesystem.

**Real instance.** A project asserted **three different model-check counts** — 39 in the script's own docstring and the task runner, 57 in six other files, while the truth was 56. The damage is not
the number; it is that a reader who spots 39 ≠ 57 learns the project's stated figures cannot be trusted, **and that doubt does not stay confined to one count**.

**Fix that holds.** **Derive, never author.** The checker computes the count from the thing counted and fails any surface that disagrees. Exempt dated historical records by marker — rewriting a record
of what was true then, to satisfy a linter, is the failure the exemption exists for.

## 6. A machine-readable map with a misplaced key

**Signature.** YAML or JSON that parses cleanly and means something different from what it looks like. Structurally valid, semantically wrong, invisible to every schema check.

**Detection.** Read the parsed structure, not the file. Print it back and compare against intent. For YAML specifically, check for **duplicate keys** — the parser keeps the last and silently discards
the earlier block while it remains plainly visible in the text.

**Real instance (a).** A `subject:` key sat one entry too low in a supersession list, leaving one mapping with no subject and labelling another with the wrong one. An agent routing a cost question off
that map would have been sent to the wrong document. **Instance (b).** Appending a second top-level `update_rules:` block discarded twelve rules from the parsed view while all twelve stayed visible in
the file.

**Fix that holds.** A duplicate-key check with a strict loader, and — for any programmatic edit — a **round-trip fidelity probe** before writing: re-encode the parsed structure and require byte
identity with the original.

## 7. A generator that re-emits the old model

**Signature.** A generated file is corrected by hand. The next rebuild silently reverts it. Or the generator's own output shape encodes a superseded rule.

**Detection.** For every generated artifact, **run the generator and diff**. A clean diff proves nothing about the generator's assumptions — read what it emits, not just whether it changed.

**Real instance.** A cash-flow generator hard-wrapped its prose at ~85 columns, so every rebuild reverted the project's 200-column wrap governance. The same generator's verdict line stated a
superseded single-limb gate, which meant the defect was re-emitted into a licence-application working paper on every run.

**Fix that holds.** Wrap, TOC and formatting rules belong **in the generator**, never applied to its output. Treat a generator as a threshold surface if it prints a threshold.

## 8. Immutable evidence silently reformatted

**Signature.** A verbatim capture of an external source — a regulation, a market table, a transcript — is "tidied" by a formatter or an editor hook. The words survive; the artifact stops being
evidence of what the source said.

**Detection.** Byte-compare against the committed version. Nothing else works: word counts, link checks and diff-line counts all survive a reformat intact.

**Real instance.** A captured auction table was found with its markdown alignment row rewritten from `| --- |` to `| ---: |`. Uncommitted, unnoticed, nobody's decision — a formatter did it on save.
That edit was cosmetic; **nothing in the repo could have distinguished it from a substantive one.**

**Fix that holds.** A check asserting byte-equality with the committed bytes for everything under the evidence directory, plus an explicit exemption from formatting rules. To correct a capture, take a
**new dated capture** — the old one remains true as what the source said that day.

## 9. Inputs with no provenance label

**Signature.** A number enters the model, everything downstream computes correctly, and nobody ever checked the number. The arithmetic being right is mistaken for the answer being right.

**Detection.** For every input feeding a headline figure, ask: **what record was this checked against, and how many records were there?** An input with no answer is a defect regardless of how
reasonable it looks.

**Real instance.** Two recommendations in two days were built on purchase prices nobody had verified — one from a single auction row, one never checked at all. The second was more than double the real
grade-matched price, and it had been the project's standing recommendation. Both survived every check, because the checks validated that documents agreed and the documents agreed perfectly.

**Fix that holds.** Provenance labels **at the input**, machine-enforced — a caveat in a document nobody re-reads does not discharge it while the number lives in a preset everybody runs. Then make the
label **print at the point of use**; a label that is never surfaced is inert. See `evidence-integrity.md`.

## Detection summary

| # | Pattern | Grep can find it? | Detection method |
|---|---|---|---|
| 1 | Threshold restated | Partly | Registry + inverse phrase guard, all word orders |
| 2 | Verdict not in data layer | Partly | Grep verdict vocabulary in data files, not prose |
| 3 | Stale template | Yes | Find copy-me files, treat as code |
| 4 | Back-solve vs changed floor | **No** | Per-artifact reasoning |
| 5 | Counts and dates | Yes | Derive and compare |
| 6 | Misplaced / duplicate key | **No** | Parse and inspect structure; strict loader |
| 7 | Generator re-emits old model | **No** | Run it and read the output |
| 8 | Evidence reformatted | **No** | Byte-compare against committed |
| 9 | Unlabelled input | Partly | Enumerate inputs, demand a record count |

**Five of nine are invisible to grep.** That ratio is the argument for Phase 4, and the reason a clean grep is never a completed audit.
