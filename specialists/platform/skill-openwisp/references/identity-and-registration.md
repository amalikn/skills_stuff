# Identity and registration

## Identity model

Separate logical identity, hardware identity, registration identity, and monitoring identity. A logical service can persist through a physical replacement only when the replacement mapping is explicit;
a physical serial or MAC must not be silently reused as the service identity. Choose a stable identifier, state who owns it, and determine which downstream consumers need continuity.

Registration is an adoption decision as well as a create decision. Match an existing record only with corroborated identity evidence; otherwise stage the ambiguity and stop. Duplicates, moved units,
factory-reset hardware, and a replacement can look similar to an automated client. Record whether the operation adopted, created, linked, deactivated, or rejected a record, together with the relevant
group/site mapping and rollback action.

## Worked version-bound lesson

The project OpenWISP 1.3 path used a dashless inventory UUID in `hardware_id` through server-side model operations. Its code records a local finding that its REST
surface did not supply the required hardware-identity semantics; this revision did not repeat that API probe. The UI label was not proof of the API field's meaning.
This is a worked version-specific pattern, not a universal OpenWISP registration recipe; check target model/API behavior and
effective settings before relying on it. Claim O-C11.

> **Learned 2026-10-05** · OpenWISP controller 1.3 (images 26.09.0) · VERIFIED_PRIMARY · Source: openwisp_controller/config/api/serializers.py lines 252-345 and config/settings.py lines 42-54 in the installed image · Falsifier: a 1.3 device serializer that lists hardware_id
> The REST device serializers omit `hardware_id`, so REST can neither read nor write it in 1.3; `HARDWARE_ID_ENABLED` defaults to False and `HARDWARE_ID_AS_NAME` to True. Server-side registration is required to key on it. Syntax: [operations cookbook](operations-cookbook.md) section 2.

> **Learned 2026-10-15** · openwisp-api 26.09.0 (Monitoring 1.3) · VERIFIED_PRIMARY (source read in the image; the SQL not yet run against a live database) · Source: `openwisp_monitoring/device/api/serializers.py:97-123` (`MonitoringDeviceListSerializer` fields), `openwisp_monitoring/device/api/filters.py:46-49`, `openwisp_monitoring/device/apps.py:39-40` (label `device_monitoring`) · Falsifier: a monitoring list serializer that lists hardware_id
> The monitoring device list (`/api/v1/monitoring/device/`, filter `monitoring__status`) returns id, name, mac_address, key, last_ip, management_ip and `monitoring.status`, but no `hardware_id` either, so REST cannot give hardware_id-keyed health. A reader that cannot run a Django shell in the container (a Nautobot worker) can read the same answer read-only from the database: `config_device.hardware_id` LEFT JOIN `device_monitoring_devicemonitoring` ON `device_id`, a missing row reading `unknown` (default table names of the unswapped models).

> **Learned 2026-10-15 (b)** · openwisp-api 26.09.0, PostgreSQL 15.8 (postgis image) · VERIFIED_PRIMARY (read-only on one live deployment) · Source: `information_schema.columns` and the query run as the database owner · Falsifier: a release that renames these tables or columns
> The four columns exist as named and the hardware_id query runs; a consumer needs only column-level `GRANT SELECT (id, hardware_id) ON config_device`
> and `GRANT SELECT (device_id, status) ON device_monitoring_devicemonitoring`, which keeps the device `key` (the push secret) unreadable to it.

## Acceptance and failure clues

An accepted registration request is not proof that the intended record, group mapping, monitoring identity, or deduplication policy took effect. Investigate duplicate identity, stale registration,
unexpected group, UI/API label mismatch, server-side validation, and replacement mapping separately. Acceptance requires one authoritative logical identity, explicit hardware association, idempotent
adoption/create behavior, and a reviewable replacement path. Claims O-C01 and O-C02.

## Version-bounded adoption contract

In UNC's observed Controller 1.3 implementation, `to_openwisp_hardware_id()` converts an inventory UUID to 32 lowercase hex characters; the 36-character dashed
form does not fit the inspected model field. The code searches by organisation and `hardware_id`, then only adopts a legacy record whose `hardware_id` is **NULL**
and whose normalised MAC agrees; an empty-string value is not covered by that query. Otherwise it creates. It sets display name, MAC, model, OS, management IP
and site group, calls `full_clean()`, saves, and returns the
registration ID/key to the authorized caller. **Do not log or copy that key into skill evidence.** An old MAC-only record may have checks requiring separate
deactivation. This is project code and observed 1.3 behavior, not a guarantee for later REST versions; inspect the target's model/API and constraints first.

| Synthetic evidence                                                   | Decision                                      | Reason                                      |
| -------------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------- |
| Same organisation + exact logical ID, matching hardware              | Adopt/update approved mirrored fields         | Idempotent logical match                    |
| No logical ID; one legacy unclaimed MAC match                        | Adopt after corroborating inventory and group | Avoid duplicate history                     |
| No match and approved inventory identity                             | Create with explicit organisation/group       | New monitored identity                      |
| Two records claim ID or MAC; wrong organisation; replacement unclear | Reject/hold                                   | First match is not safe identity resolution |

For a synthetic UUID `11111111-2222-3333-4444-555555555555`, the 1.3 case uses `11111111222233334444555555555555` as logical key. A physical swap
does **not** re-key that history if the service identity is intended to persist; otherwise use a new logical key and explicit history link. A supported REST path is
appropriate when the installed version exposes and validates the required identity/group fields. A server-side integration is justified only when that REST path
cannot express the contract, and then must be version-pinned, permission-scoped and regression-tested. Read [passive ingestion](passive-ingestion.md) after registration
and Nautobot [lifecycle and replacement](../../skill-nautobot/references/lifecycle-and-replacement.md) only when inventory identity changes.

> **Learned 2026-10-05** · OpenWISP 26.09.0 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a replacement policy under which a serial should become the monitoring key
> Key monitoring on the inventory's stable logical ID, not on a hardware value: serial was the strongest corroborating signal (never conflicted, 93% present) but changes on a hardware swap; MAC needs normalising and, for some families, an offset. Use serial and MAC to confirm a match, never as the key.
