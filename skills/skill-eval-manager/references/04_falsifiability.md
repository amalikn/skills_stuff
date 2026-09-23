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
