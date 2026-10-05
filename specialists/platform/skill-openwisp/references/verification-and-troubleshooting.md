# Verification and troubleshooting

## Processing chain and independent consumers

First trace the common data path: offline mapping → API acceptance → background worker processing → Metric metadata → fresh time-series point. From a fresh point,
**health evaluation and graph presentation are separate consumers**. Neither consumer's success proves the other. Start at the first unproven shared stage; once
storage is fresh, inspect the failing consumer directly. Operational acceptance additionally requires sustained results and the operator's stated use case.

| Rung                      | Direct proof                                  | Failure clue                                        | Inspect next                             | Does not prove          |
| ------------------------- | --------------------------------------------- | --------------------------------------------------- | ---------------------------------------- | ----------------------- |
| API accepted              | Response and validated request record         | HTTP error or validation rejection                  | Payload/schema/identity                  | Worker processing       |
| Worker processed          | Task log/result for the same identity         | Queue backlog, task exception, or missing           | Worker image, settings,                  | Metric persistence      |
|                           |   and timestamp                               |   consumer action                                   |   queue, dependency                      |                         |
| Metric metadata           | Matching Metric record                        | Record absent or wrong identity/type                | Registration, mapping, transaction       | Fresh time-series point |
| Recent time-series point  | Query returns a point within                  | Old timestamp, wrong unit, retention or             | Timestamp, backend, retention, sampling  | Health evaluation       |
|                           |   declared freshness                          |   storage delay                                     |                                          |                         |
| Health evaluated (branch) | Policy evaluated the intended fresh point     | Stale/unknown state or policy not run               | Threshold, freshness, check schedule     | Graph rendering         |
| Operator-visible          | Authorized UI/API view renders                | Empty chart or wrong filter                         | Consumer query, permissions,             | Health or               |
|   graph (branch)          |   expected series                             |                                                     |   chart config                           |   broader acceptance    |

HTTP 200 is therefore insufficient. A worker can accept a task but fail before useful storage; a Metric object can exist while its time-series data is stale; a fresh point can miss a health policy;
and a healthy state can still have no rendered graph. These are diagnostic distinctions, not a claim that each stage passed for observed Monitoring 1.3.

> **Learned 2026-10-05** · OpenWISP images 26.09.0 · VERIFIED_PRIMARY · Source: /opt/openwisp/init_command.sh lines 77-123 in the image, plus a read-only probe that found no worker while every container showed Up · Falsifier: an image whose worker runs in the foreground, so the container exits when the worker dies
> Celery workers start with `--detach` and the container's foreground process is `tail -f` on the logs, so a container shown Up proves nothing about the worker rung. Prove it with `ps` and `celery -A openwisp inspect ping` ([operations cookbook](operations-cookbook.md) section 5); in the probe, the newest stored point was a week old.

## Troubleshooting discipline

Correlate every inspection by stable identity, metric name/type, source timestamp, and worker/request trace. Check version and effective settings across API and worker processes before changing a
mapping. Timestamp normalization or freshness errors can produce misleading health, and graph absence can be downstream of successful persistence. Record the first failed rung, evidence, falsifier,
and next safe action; do not promote a lower rung to a higher one. Claims O-C03 and O-C12.

## Read-only discriminators (synthetic, target API must be version-checked)

| Stage           | Bounded inspection                                                             | Expected evidence and next check if absent                                                        |
| --------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| Offline mapper  | Run credential-free fixture/schema test                                        | Identity, units, source time and metric-producing field; fix mapper before POST                   |
| API             | Inspect request ID/status and validated response, without logging key/body     | Accepted identity/time; if rejected, inspect schema/registration/permission                       |
| Worker          | Read task/queue log for same identity and time window                          | Consumed task and no exception; if absent inspect queue binding, image, settings and              |
|                 |                                                                                |   worker reachability                                                                             |
| Metric metadata | Authorized read-only device metric listing (26.09 docs                         | Expected key/type; if absent inspect worker mapping and DB transaction                            |
|                 |   describe `/api/v1/monitoring/device/{pk}/metric/`)                           |                                                                                                   |
| Time series     | Bounded query for key and source-time range in configured store                | Point with value/unit and timestamp; if old, inspect backfill time, retention and storage writer  |
| Health branch   | Read policy, last evaluation and device/metric health                          | Evaluation of fresh point; if absent inspect check registration/schedule/window                   |
| Graph branch    | Read chart API/view as authorized user with same metric/time range             | Series rendered; if empty inspect chart registration, query filters and permissions               |

Case A: POST accepted at 10:05, no Metric row by bounded deadline. Do not blame the graph; correlate task ID and inspect monitoring worker queue/log and effective
settings. Case B: Metric row exists from yesterday but no point in the last hour. The object proves only metadata; query source-time storage, backfill format and
worker write errors before health or graph conclusions. Case C: point at 10:00 is present, graph empty, health correct. Inspect chart consumer registration/filter/
permission; changing health thresholds is irrelevant. Reverse case: graph shows fresh data but health unknown; inspect check schedule/window, not chart code.
Read [customisation and upgrades](customisation-and-upgrades.md) when worker/API settings differ and [health, alerts and notifications](health-alerts-notifications.md)
when the health branch is at fault. Never print a per-device key in a diagnostic artifact.
