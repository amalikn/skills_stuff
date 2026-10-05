# Evaluation procedure

Use a fresh credential-free client context. Run explicit invocation, implicit realistic task, unrelated negative control and the mixed replacement task from `scenarios.md`; record client/version,
package version, symlink target, prompt, loaded skill, first reference, observability, verdict and a redacted evidence locator.

For every pass, check the scenario's required decision, evidence, usable next action, prohibited conclusion and justified uncertainty. Grade answer quality:
**Pass** = all three positive elements; **Partial** = right principle but missing a discriminator; **Fail** = unsupported conclusion, material omission or unsafe action;
**Unavailable** = client could not run, with reason. Record routing separately as observed correct/incorrect/unobservable; a good answer does not prove a skill load.
Record runtime compatibility separately from routing and answer quality. Discovery failure blocks release.

For representative cases, run the same synthetic prompt in two fresh contexts: one without skill files and one with explicit skill invocation. Do not provide the
expected answer or prior conclusions to either. Keep client version, cwd, authorization and data constant; record concrete decision differences and ties. If a
client cannot run, continue deterministic/offline review and report `Unavailable`, not a fabricated baseline. Never use credentials or live endpoints.

For write-back scenarios verify one of the six classifications and source, product/app version, evidence type, falsifier, authorization and redaction. For upgrade
scenarios verify supported-extension adjustment,
superseded patch retirement and reviewed patch rebase with rollback.

## Knowledge-value rubric

For passive monitoring, the response must distinguish offline mapping, API accepted, worker processed, Metric metadata and recent point, then inspect health and graph
as independent consumers. It must preserve closed-firmware limits, known/unknown/down semantics, and the distinction between logical and hardware identity. For a passed evaluation, record which of these
decision points was directly observable; a polished generic monitoring answer is not enough.
