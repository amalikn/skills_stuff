# Configuration backup and compliance

## Separate controls

Backup collects a recoverable representation. Compliance evaluates it against an approved policy. Deployment changes a target. Restore verification proves a backup can be used safely. These are
separate capabilities with different authorization and evidence requirements. A successful backup must not automatically authorize a push; a matching comparison must not be called a restore proof.

Redact secrets before storage, reporting, and comparison. Retain enough metadata to explain collection time, target identity, scope, and failure without placing secret-bearing configuration in a
ticket or reusable skill. Golden Config or another tool may provide collection/comparison seams, but driver support, credentials, network reachability, and target behavior remain dependencies to
verify for the installed version.

## Comparison and restoration

A project worked pattern used a keyed HMAC digest for equality comparison while avoiding plaintext retention. It can show that two values produce the same keyed digest; it is not identity,
authorization, tamper proof, or a substitute for key management. Truncation, domain separation, key rotation, leakage of low-entropy inputs, and collision tolerance are project security decisions.
Do not promote that pattern into a generic helper without a cross-project consumer and security review.

Acceptance requires a redaction review, a declared comparison scope, a known restore procedure tested in an authorized environment, and a separate deployment gate with rollback. Backup success alone,
or a hash equality result alone, is insufficient. Claim N-C09.

## Worked backup decision

Synthetic source config has interface/VLAN intent, a local credential, and a management-agent token. A redacted archive can restore the non-secret interface/VLAN
portion and prove its intended structure; it **cannot** restore authentication or the agent's enrollment by itself. Record a secret manifest (names/roles, never values),
an authorized vault/source for each omitted secret, and a restore runbook that injects them under operator control. A backup is useful only when collection identity,
source time, scope, integrity, retention and an authorized restore rehearsal are evidenced. A parseable redacted text alone is not a full disaster-recovery proof.

Normalize only semantics known safe for the device family (for example order-independent sections after proving order does not matter). Keep raw restricted evidence
under project controls, never in the skill. Compare against an approved intended config with exclusions explained; do not call a stable diff compliance if the parser
dropped a critical stanza. Golden Config provides a supported backup/compliance seam in the observed UNC app set, but driver, worker reachability and installed-version
fit still need proof. UNC kept deployment off; its safe-write pipeline is project-owned and unproven as a generic device path.

UNC's fingerprint helper uses keyed HMAC-SHA256 truncated to 16 hex digits (64 bits) for equality without disclosing the value. The key must be protected and
consistent for comparisons; key rotation changes digests. A 64-bit tag has collision risk, especially over many comparisons, and HMAC does not supply identity,
authorization or restore completeness. For a low-entropy secret, the key is the protection; plaintext hashes would invite guessing. When the key is unavailable, the
project path leaves data redacted rather than emitting plaintext. No reusable executable helper is included here. Read [apps, Jobs and validation](apps-jobs-validation.md)
for worker prerequisites and [upgrade and troubleshooting](upgrade-and-troubleshooting.md) for migration checks.
