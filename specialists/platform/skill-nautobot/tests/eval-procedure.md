# Evaluation procedure

Use a fresh credential-free client context. Run explicit invocation, implicit realistic task, unrelated negative control and the mixed lifecycle task from `scenarios.md`; record client/version,
package version, symlink target, prompt, loaded skill, first reference, observability, verdict and short redacted evidence locator.

For every pass, check the scenario's required decision, evidence, usable next action, prohibited conclusion and justified uncertainty. Grade answer quality:
**Pass** = all three positive elements; **Partial** = right principle but missing a discriminator; **Fail** = unsupported conclusion, material omission or unsafe action;
**Unavailable** = client could not run, with reason. Record routing separately as observed correct/incorrect/unobservable; a good answer does not prove a skill load.
Record runtime compatibility separately from routing and answer quality. A discovery failure blocks release.

For representative cases, run the same synthetic prompt in two fresh contexts: one without skill files and one with explicit skill invocation. Do not provide the
expected answer or prior conclusions to either. Keep client version, cwd, authorization and data constant; record concrete decision differences and ties. If a
client cannot run, continue deterministic/offline review and report `Unavailable`, not a fabricated baseline. Never use credentials or live endpoints.

For write-back scenarios, verify one of the six classifications and require source, product/app version, evidence type, falsifier, authorization and redaction. For upgrade scenarios, verify supported-extension
adjustment, superseded core patch retirement and reviewed core-patch rebase with rollback rather than replay.

## Knowledge-value rubric

For onboarding, the response must distinguish observation, candidate identity, corroboration, ambiguity, Staged review, and promotion; one identifier must not be treated as sufficient. For topology,
it must state what LLDP/CDP, FDB, ARP, DHCP, API/SSH, and inventory can and cannot prove. For writers, it must name stable ordering, repeated/changing-page failure, ownership, dry-run, and
fail-closed behavior. For a passed evaluation, record which of these decision points was directly observable; a polished generic answer is not enough.
