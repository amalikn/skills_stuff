# Falsifiability evidence

## Contents

- [Rule](#rule)
- [Methods](#methods)
- [Safety](#safety)
- [What does not count](#what-does-not-count)

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

## What does not count

“It passed once,” unreferenced confidence, a test that only reaches the same path it evaluates, or a fault that an operator cannot safely reproduce do not establish falsifiability.
