# Health, alerts and notifications

## Separate controls

Observed metric values, freshness/staleness, health derivation, threshold policy, alert state, suppression/correlation, and notification transport are different controls. A transport integration can
deliver a notification without deciding the correct threshold; a metric may be fresh but outside policy; a stale metric may be operationally more important than a low value.

Define the owner of each policy, its freshness window, threshold/tolerance, escalation, acknowledgement, and suppression rules before selecting a module or external engine.
Treat root-cause
correlation separately from presentation: suppressing downstream symptoms is safe only when the likely upstream cause and recovery behavior remain visible.

## Project-derived diagnostic lesson

The project observed that collector or transport failure can produce fleet-wide symptom noise. Its host-side cause-aware alarm design is a worked architecture pattern, not an OpenWISP requirement.
The reusable lesson is to distinguish transport/collector evidence from device symptom evidence and avoid declaring every downstream device independently broken. Claim O-C14.

## Acceptance

Test current and stale data, threshold crossing, recovery, duplicate suppression, root-cause visibility, notification delivery failure, and operator acknowledgement independently.
A delivered message is
not proof that health was computed correctly, and a critical state is not proof that the transport succeeded. Claim O-C06.

## Cause, suppression and recovery worked case

UNC's settings disabled centrally originated Ping/Configuration Applied checks and used `data_collected` for freshness, because central reachability did not match
the site's network path. Its Step 2 work observed that stock `data_collected` problem notifications did not fire correctly once that metric itself made a device
critical; a host-side alarm engine therefore correlates cause and uses OpenWISP Notifications as delivery. This is a **local observed interaction** in Monitoring 1.3,
not a guarantee of every release or a reason to disable notifications elsewhere. Its per-family AlertSettings convergence is dry-run-first and applies only to
existing metric keys. Operator thresholds and one-week acted-on soak remain project policy/pending acceptance.

Synthetic incident: 20 devices show stale `data_collected` after 10:00; the collector run log shows one expired transport credential, while no device-local
down evidence exists. Classify a collector/transport root cause, retain the 20 suppressed symptom IDs in an audit record, send one cause notification and verify its
delivery. Do **not** silently suppress independent device-down evidence. After credential repair by an authorized operator, require a successful collector run,
fresh stored points and health re-evaluation; close the cause alert once and check that symptoms clear without duplicate recovery notices. If notification delivery
fails, keep the cause visible in local state/log and report delivery failure separately.

Mirroring health into inventory should write only dedicated observation fields with source/evaluation time and stale/unknown semantics; never turn monitoring
`critical` into an inventory lifecycle Status. Read Nautobot [authority and modeling](../../skill-nautobot/references/authority-and-modeling.md) only when the task
changes that mirror. For an empty graph with healthy data, go to [verification](verification-and-troubleshooting.md), not alert policy.

> **Learned 2026-10-07** · openwisp-config (any release with `verify_ssl`) · UNVERIFIED · Source: cross-platform incident, skill-smc `references/13_known-issues.md` 2026-10-07 (fluent-bit, not OpenWISP); `verify_ssl '1'` in [configuration management](configuration-management.md) · Falsifier: a lab device with `verify_ssl '1'` keeps applying configuration and pushing monitoring data after the controller's certificate expires
> An agent that verifies TLS stops reporting when the server certificate expires, and the server sees only absence: in the cross-platform case, log volume dropped to near zero for 25 days, nothing alerted, and buffered data was not replayed. If OpenWISP devices run with `verify_ssl '1'`, expect every device to go stale at once. Classify that as a transport cause (worked case above), not device-down. Alert on the controller certificate's expiry and on a fleet-wide `data_collected` freshness drop, separately from per-device health.
