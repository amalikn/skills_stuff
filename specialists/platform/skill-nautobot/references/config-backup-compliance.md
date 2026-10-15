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

> **Learned 2026-10-15 (j)** · Nautobot 3.2.3, Golden Config 3.0.7 · VERIFIED_PRIMARY · Source: installed `nautobot_golden_config/models.py:476-487` and `views.py:164-170` read in the running image; `reverse()` and `device.goldenconfig` checked in `nautobot-server nbshell` on one live 3.2.3 instance, 2026-10-15; device list `?location=<site>` returned units held in child Locations on the same instance · Falsifier: a GC release that adds `related_name` to `GoldenConfig.device`, renames the `backup` action, or a Nautobot release whose device `location` filter stops including descendants
> Golden Config gives a Device only its "Configuration Compliance" tab (hidden while the device has no compliance rows); the full backup is the GoldenConfig record's `backup` action. `GoldenConfig.device` is a OneToOneField without `related_name`, so the reverse accessor is `device.goldenconfig`; the record's page is `get_absolute_url()` (`/plugins/golden-config/golden-config/<pk>/`) and the backup view reverses as `plugins:nautobot_golden_config:goldenconfig_backup` (`.../<pk>/backup/`), which renders `backup_config` as "cli" text. A backup fed through the REST API (PATCH `backup_config` with `backup_last_attempt_date`/`backup_last_success_date`) needs no Platform driver, Nornir or backup repository, and an app can show it in its own Device tab (DistinctViewTab plus an ObjectView extending `dcim/device.html`) gated on `nautobot_golden_config.view_goldenconfig`. The device list's `location` filter includes child Locations (towers, premises), so a per-site run needs no tree walk.

UNC's fingerprint helper uses keyed HMAC-SHA256 truncated to 16 hex digits (64 bits) for equality without disclosing the value. The key must be protected and
consistent for comparisons; key rotation changes digests. A 64-bit tag has collision risk, especially over many comparisons, and HMAC does not supply identity,
authorization or restore completeness. For a low-entropy secret, the key is the protection; plaintext hashes would invite guessing. When the key is unavailable, the
project path leaves data redacted rather than emitting plaintext. No reusable executable helper is included here. Read [apps, Jobs and validation](apps-jobs-validation.md)
for worker prerequisites and [upgrade and troubleshooting](upgrade-and-troubleshooting.md) for migration checks.

> **Learned 2026-10-15 (o)** · Golden Config 3.0.7, Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: Django test client against a deployment's `/plugins/golden-config/config-compliance/` and GC's `views.py` (`ConfigComplianceUIViewSet.alter_queryset` pivots by device) · Falsifier: the list showing rows for `?location_id=<site>`
> The Config Compliance list cannot be linked to by location: with `location_id` (or `feature`, `compliance`) it reports "No config compliances
> found" while `ConfigCompliance.objects.filter(device__location__in=...)` holds 71 rows, because the list pivots by device after filtering. GC's own
> Location panel (`ConfigComplianceLocationCheck`, plain badges) offers no link either. To send a user from a count to the matching results, build a
> small list view over `ConfigCompliance` filtered by location subtree, feature slug and compliance, and link each row to the device's compliance tab
> (`plugins:nautobot_golden_config:configcompliance_devicetab`, `?tab=nautobot_golden_config:1`).
