# Falsifiability evidence

## Contents

- [Rule](#rule)
- [Methods](#methods)
- [Safety](#safety)
- [What does not count](#what-does-not-count)
- [What it does not establish](#what-it-does-not-establish)

## Rule

An eval with no evidence that it can fail is noise. The suite must name a permitted method, a durable reference, and the date that evidence was verified. The validator requires evidence; it does not
demand destructive testing.

## Methods

`injected_fault` deliberately creates a safe, scoped fault and observes the expected failure. `fixture` supplies captured bad input. `mutation` changes an input or implementation condition in a
controlled test. `counterexample` demonstrates a known case that must be rejected. `historical_failure` points to a real defect the eval caught. `analytical_proof` records a reviewable argument
showing a countercondition is rejected.

For production financial reconciliation, legal provenance, external API behavior, and historical evidence, a historical failure or counterexample can be more honest and safer than injection. State the
environment and approval conditions in the referenced artifact.

## Safety

Never turn falsifiability into authorization to disturb production. An injected fault must name the approved environment and a rollback/recovery path in its referenced procedure. When live access is
operator-only, the suite tier must say so and an agent must stop rather than run it.

## What it does not establish

Falsifiability evidence proves the **measure**. It does not prove the **binding** between that measure and the live
source it will be pointed at, and a suite can hold valid, dated, well-chosen evidence while its production numerator
is silently wrong.

Seen 2026-09-23, in the first recorded observation of a network-controller coverage eval. Its `counterexample`
fixture was well made: fed by CSV, it caught all three ways the arithmetic can go wrong, including the subtle one
where an out-of-population device that still reports inflates the numerator to a false full pass. The fixture read
correctly throughout. The live numerator was wrong twice anyway:

- A status row's timestamp was read as the time of the last stored metric. It was the device's health row, whose
  timestamp moves when the status changes — reporting two covered devices on a fleet whose health sync showed
  forty-four healthy.
- The identifier column holding the text of a UUID was looked up with UUID objects. Every row missed, and the eval
  reported zero coverage against several hundred stored metrics.

Neither was reachable from the fixture, because a CSV-fed counterexample cannot exercise a query against a live
store. Both were caught only by disbelieving a number that disagreed with something else already known about the
system.

Two consequences for method:

1. When the fixture is fed from static data, its evidence covers the computation and not the source binding. Say so
   in the referenced artifact rather than letting the reader assume the whole path was proven.
2. A first observation deserves a sanity check against an independent known quantity before it is recorded — a count
   from another part of the system, an operator's expectation, anything not produced by the same query. The
   verdict's honesty depends on it, and neither the validator nor the falsifiability evidence can supply it.

This is not a new falsifiability method; `counterexample` was the right choice. It is a limit on what any of the six
establish on its own.

## What does not count

“It passed once,” unreferenced confidence, a test that only reaches the same path it evaluates, or a fault that an operator cannot safely reproduce do not establish falsifiability.

Nor does "the command exited 0 and printed something". A lab suite passed on non-empty output from a CLI subcommand that did not exist in
the pinned release: the tool printed its unknown-command text and exited 0. An interface reported up passed while the policy that had to
survive a restart was never restarted. Assert on specific content the feature alone produces, check the exit code and the owning daemon's
log (no error lines), and exercise the condition the claim is about; a counterexample that removes the feature must turn the eval red
(2026-10-29 harvest).

> **Learned 2026-11-01** · pass marks and answer keys · VERIFIED_PRIMARY (a curation tool's recall gate, measured) · Source: skill-knowledge-curator `references/evaluation.md`, Gate 0 result · Falsifier: a probe built from the feature's
> own assumption that predicts the result of a blind labelled set
> A hand-built probe inherits the assumption under test. A recall probe gave both claims one topic, passed, and opened a gate; agents working apart shared 1 of 245 topics, and a blind labelled set then scored 44.4% against an 80% mark.
> Commit the mark before measuring, have an agent write the answer key without seeing the tool's output, score each stage separately, and keep the mark when it fails. Report any kinder reading as secondary, beside the result and never in place of it.

> **Learned 2026-11-01 (b)** · filters and their measures · VERIFIED_PRIMARY (blind shuffled sample of 80 kept and cleared findings) · Source: skill-knowledge-curator `references/evaluation.md`, Third attempt result · Falsifier: a filter whose recall measure rose or held after it removed labelled items while a blind audit found wrong removals
> A noise filter needs three measures from one blind pass: precision of what is kept, error rate of what is cleared, and recall counted without the cleared items, or a filter cannot lose. Mix kept and cleared cards so the judge cannot tell them apart. Dry-run on the tuning sample first: the first rules cleared 7 of 11 real findings. Then judge on a sample the tuning never saw. Also check the answer key and the judge share one definition: a labelled history change was a real conflict to one and noise to the other.

> **Learned 2026-11-02** · briefing outside researchers · VERIFIED_PRIMARY (four external reports read against the brief) · Source: skill-knowledge-curator `docs/research/readme.md` · Falsifier: outside reports that keep an ambiguous measured figure's meaning across several independent runs
> When a brief hands measured figures to an outside reader, say what each count counts. "11 of 40 real, and 10 of the 11 share one cause" sat beside a line on noise, and three of four reports turned it into "10 of 11 false positives", then built plans on it. Treat outside reports as unverified, compare them with each other and with your own measures, and keep them verbatim so the misreading stays visible.
