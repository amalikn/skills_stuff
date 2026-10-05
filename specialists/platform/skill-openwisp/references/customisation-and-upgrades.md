# Customisation and upgrades

## Effective configuration

Record Django settings, custom metric registration, notification types, import order, extension registration, worker configuration, image tag, installed module versions, migrations, and process
state. Verify the effective settings in every process that uses them; a dashboard and worker can start with different settings, a stale process, or a different import path. Where process identifiers
or pidfiles are available, use them as diagnostic evidence, not as a universal deployment requirement.

The observed image tag and installed Python module versions are separate coordinates. A running image proves only its observed identity, not that custom ingestion, settings propagation, or graphing
works. Claim O-C15.

Version trigger: when the installed version differs from the `Verified against:` line of [the operations cookbook](operations-cookbook.md), re-verify each cookbook
section the task relies on against the new installed source or versioned docs, then update that line and `compatibility.yaml`. Until then the cookbook is the old
version's syntax.

## Upgrade path

Prefer settings and supported add-ons, then narrow overlays/shims. Treat direct core patches as explicit debt with original base, affected behavior, migration/import consequences, tests, rollback,
and a retirement condition. On upgrade, compare upstream behavior and extension APIs; re-register custom metrics/notifications where needed; migrate; test API and worker paths; verify the
operator-visible outcome; and retain rollback.

If upstream supersedes a patch, test the replacement and retire the patch with history. If a patch remains necessary, review and rework it against the new code rather than replaying it. Import/start
success is not functional compatibility, and functional compatibility is not operator-visible acceptance. Claims O-C04 and O-C09.

## Process-consistency check

| Component         | Effective configuration to compare                                              | Observable failure                                                  |
| ----------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Dashboard/web     | Mounted Django settings, apps, metric and notification registration             | UI lacks custom chart/type or displays stored notification as error |
| API               | Same mount/import order, schema, registration model, permissions                | POST accepted/rejected differently from expectation                 |
| General worker    | Image/module versions, queue binding, settings and task imports                 | Task queued but not consumed or unknown task                        |
| Monitoring worker | Monitoring metric/check registration, store connection, queue and process state | HTTP accepted but no new Metric/point                               |
| Scheduler/beat    | Check schedule, window and settings                                             | Fresh point exists but health never re-evaluates                    |

UNC mounts custom settings into each Django process, registers metric schemas and a notification app, and checks effective registration and baseline counts with
`check_platform_customisations.py`. A mounted file's presence is not proof its imports ran. Compare effective settings, image identity and installed module versions
per process; 26.09.0 image tags and 1.3 module metadata are different coordinates. A stale monitoring-worker pidfile was one observed cause of accepted pushes
without processing. Diagnose it only after task/queue/process evidence shows the worker is absent or stale; inspect the process supervisor and pid ownership before
any cleanup. Never recommend deleting a pidfile solely from a missing graph.

Synthetic upgrade register row: `OW-EX-1`, custom metric `peer_quality`, supported settings/registration seam, old image/module 26.09.0/1.3, candidate version
unverified, source and owner in project, test = payload accepted → worker writes fresh point → chart displays it, rollback = prior pinned image and settings mount.
Before upgrade, check release notes and whether upstream now offers the metric. Rehearse migrations, mount/import order, queue routing and each process; preserve a
core patch's base tag only if a real patch exists. Read [verification](verification-and-troubleshooting.md) for stage-specific proof.
