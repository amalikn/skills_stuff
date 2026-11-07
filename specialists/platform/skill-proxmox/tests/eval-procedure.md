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

For write-back scenarios, verify one of the six classifications and require source, product version, evidence type, falsifier, authorization and redaction. For upgrade
scenarios, verify the repository check, `apt full-upgrade` (never `apt upgrade`), the release known issues and the guest restart plan.

## Knowledge-value rubric

For access control, the response must state the intersection rule for privilege-separated tokens (ACL on user and token), the scope (pool, storages, zones) and
which privileges it keeps away from automation (`Sys.Modify`, `Permissions.Modify`, root-only operations). For VMs, it must separate PVE configuration, OVMF
behaviour and real firmware. For automation, it must name the read default, the plan, `--apply`, task-status checks and read-back. For a passed evaluation,
record which of these decision points was directly observable; a polished generic answer is not enough.
