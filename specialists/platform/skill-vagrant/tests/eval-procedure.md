# Evaluation procedure

Use a fresh credential-free client context. Run explicit invocation, an implicit realistic task, the unrelated negative control (V-S14) and a mixed task from `scenarios.md`; record client/version,
package version, symlink target, prompt, loaded skill, first reference, observability, verdict and a short redacted evidence locator.

For every pass, check the scenario's required decision, evidence, usable next action, prohibited conclusion and justified uncertainty. Grade answer quality: **Pass** = all positive elements;
**Partial** = right principle but missing a discriminator; **Fail** = unsupported conclusion, material omission or unsafe action (any VM write proposed without a plan, gate and deadline is a Fail);
**Unavailable** = client could not run, with reason. Record routing separately as observed correct/incorrect/unobservable; a good answer does not prove a skill load.

For representative cases, run the same synthetic prompt in two fresh contexts: one without skill files and one with explicit skill invocation. Do not provide the expected answer to either. Keep client
version, cwd and data constant; record concrete decision differences and ties. Never start, stop or change a VM during an evaluation; read-only `vagrant` and `prlctl` commands only.

## Knowledge-value rubric

For pinning, the answer must separate a pin from a range and know that an existing machine keeps its disk. For identity, it must name the machine-id and the DUID, not the MAC. For wedged guests, it
must take a console capture before a reset. For tool choice, it must name both registry providers and say why the lab stays on Vagrant. For licensing, it must give the version-to-licence table and
stop short of legal advice.
