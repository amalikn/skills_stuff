---
Title: OpenWISP operations cookbook
Category: skill-reference
Status: current
Authority: Installed OpenWISP images 26.09.0 (modules 1.3) and InfluxDB 1.8.10 source and version-matched official documentation; the cited lines win over this summary
Scope: Exact, version-matched syntax for OpenWISP REST auth, controller devices, monitoring pushes and backfill, InfluxDB, Celery workers, custom metrics and checks, notifications, organizations, docker-openwisp settings and management commands
Last reviewed: 2026-10-05
Summary: Ten verified recipes with a gotcha and a source line each, cited to the installed 26.09.0 image source and the versioned 26.09 docs; re-verify on any version change.
---

# Operations cookbook

Verified against: OpenWISP images 26.09.0, modules 1.3, InfluxDB 1.8.10, checked 2026-10-05.

Module detail: openwisp-controller 1.3, openwisp-monitoring 1.3, openwisp-notifications 1.3, openwisp-users 1.3.0, openwisp-network-topology 1.3, openwisp-utils 1.3, on
Django 5.2.17, djangorestframework 3.17.2, celery 5.6.3 and Python 3.14.

Citations name the installed file inside the `openwisp-dashboard:26.09.0` image as `$P/<module>/<file>:<line>`, where `$P` is `/usr/local/lib/python3.14/site-packages`; image-level files live under
`/opt/openwisp/`. Doc citations point at the versioned 26.09 pages, snapshotted in [../documents/readme.md](../documents/readme.md). Anything not read from source, a versioned page or a live read-only
probe is marked UNVERIFIED.

## Summary

| Job                              | Use                                        | Key syntax                                                          | Trap                                                                  | Section                                                                 |
| -------------------------------- | ------------------------------------------ | ------------------------------------------------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Authenticate and list            | REST with a Bearer token                   | `POST /api/v1/users/token/`; `page`, `page_size` (max 100)          | Scheme is `Bearer`, not `Token`; oversize pages are capped silently   | [1](#1-rest-authentication-and-pagination)                              |
| Create or retire a device        | Controller REST                            | `/api/v1/controller/device/`; `.../deactivate/` then DELETE         | Delete stays 403 until the Config itself reaches `deactivated`        | [2](#2-controller-rest-devices-groups-deletion-hardware_id)             |
| Key a device on an inventory ID  | `hardware_id`, server-side                 | 32 characters; off by default                                       | Not in the REST serializers in 1.3                                    | [2](#2-controller-rest-devices-groups-deletion-hardware_id)             |
| Push or backfill metrics         | Monitoring REST with the device key        | `?key=...&time=%d-%m-%Y_%H:%M:%S.%f` (UTC)                          | 200 means queued, not stored; ISO 8601 is a 400                       | [3](#3-monitoring-rest-push-backfill-metrics-charts-health)             |
| See what was stored              | InfluxDB 1.8, read-only                    | `influx -database openwisp -execute 'SHOW ...'`                     | `device_data` lives in the 24h `short` policy                         | [4](#4-time-series-store-influxdb-18)                                   |
| Prove the workers run            | Celery inspect and `ps`                    | `celery -A openwisp inspect ping` (five nodes expected)             | Workers are detached: a container shown Up can have no worker         | [5](#5-celery-queues-workers-and-beat)                                  |
| Add a metric, chart or alert     | Settings or `register_metric`              | `OPENWISP_MONITORING_METRICS`, `..._CHARTS`                         | `AUTO_*` switches do not remove checks that already exist             | [6](#6-custom-metrics-charts-alerts-and-stock-checks)                   |
| Alert someone                    | Notification types                         | `register_notification_type` in every process                       | A type missing from one process breaks there only                     | [7](#7-notifications)                                                   |
| Scope an integration account     | Organization manager (`is_admin`)          | `/api/v1/users/organization/`                                       | A token that sees nothing is usually a member without `is_admin`      | [8](#8-organizations-and-api-scoping)                                   |
| Change behaviour                 | Env vars + mounted custom settings         | `/opt/openwisp/openwisp/configuration/custom_django_settings.py`    | The import fails silently; read the setting in each container         | [9](#9-docker-openwisp-settings-and-overrides)                          |
| One-off maintenance              | `python manage.py ...` in the dashboard    | `run_checks`, `migrate_timeseries`                                  | Both hand work to Celery and do nothing without workers               | [10](#10-management-commands)                                           |

## Contents

- [Summary](#summary)
- [1. REST authentication and pagination](#1-rest-authentication-and-pagination)
- [2. Controller REST: devices, groups, deletion, hardware_id](#2-controller-rest-devices-groups-deletion-hardware_id)
- [3. Monitoring REST: push, backfill, metrics, charts, health](#3-monitoring-rest-push-backfill-metrics-charts-health)
- [4. Time-series store: InfluxDB 1.8](#4-time-series-store-influxdb-18)
- [5. Celery queues, workers and beat](#5-celery-queues-workers-and-beat)
- [6. Custom metrics, charts, alerts and stock checks](#6-custom-metrics-charts-alerts-and-stock-checks)
- [7. Notifications](#7-notifications)
- [8. Organizations and API scoping](#8-organizations-and-api-scoping)
- [9. docker-openwisp settings and overrides](#9-docker-openwisp-settings-and-overrides)
- [10. Management commands](#10-management-commands)

## 1. REST authentication and pagination

Decision: obtain one Bearer token per service account with `POST /api/v1/users/token/`, send it as `Authorization: Bearer`, and page every list call.

```bash
OW=https://openwisp.example
OW_TOKEN=$(curl -s -X POST "$OW/api/v1/users/token/" \
  -d "username=<service-user>" -d "password=<password>" | jq -r .token)
curl -s "$OW/api/v1/controller/device/?page_size=100&page=2" \
  -H "Authorization: Bearer $OW_TOKEN"
```

- The token view is mounted only while `OPENWISP_USERS_AUTH_API` is true (default `True`) and is throttled (`AuthRateThrottle`). A `GET` on it returns `405` with `Allow: POST, OPTIONS` (live probe,
  2026-10-05).
- Protected views accept `BearerAuthentication` (keyword `Bearer`, not DRF's default `Token`) and session auth. An unauthenticated call returns `401` with `WWW-Authenticate: Bearer` (live probe on
  `/api/v1/controller/device/`).
- Pagination is page-number based: `page` and `page_size`; default 10, maximum 100, set by `OPENWISP_API_DEFAULT_PAGE_SIZE` and `OPENWISP_API_MAX_PAGE_SIZE`. A `page_size` above the maximum is
  silently capped, so loop on `next` rather than trusting one big page.
- Org scoping is implicit: the token's user sees only objects of organizations they manage (section 8). There is no org header.

Gotcha: `Authorization: Token <key>` is rejected by these views; the scheme word must be `Bearer`.

Source: `$P/openwisp_users/api/urls.py:52-54` (token path behind `USERS_AUTH_API`), `$P/openwisp_users/settings.py:8`, `$P/openwisp_users/api/authentication.py:13-14`,
`$P/openwisp_users/api/mixins.py:299-311` (auth and permission classes), `$P/openwisp_users/api/views.py:59-61`, `$P/openwisp_utils/api/pagination.py:14-19`, `$P/openwisp_utils/settings.py:21-22`;
https://openwisp.io/docs/26.09/users/user/rest-api.html.

## 2. Controller REST: devices, groups, deletion, hardware_id

Decision: create and update devices over `/api/v1/controller/device/`; keep anything the serializer does not expose (notably `hardware_id`) server-side.

```text
GET|POST          /api/v1/controller/device/
GET|PUT|PATCH|DEL /api/v1/controller/device/<uuid>/
POST              /api/v1/controller/device/<uuid>/deactivate/
POST              /api/v1/controller/device/<uuid>/activate/
GET               /api/v1/controller/device/<uuid>/configuration/
GET|POST          /api/v1/controller/group/
GET|PUT|PATCH|DEL /api/v1/controller/group/<uuid>/
GET               /api/v1/controller/cert/<common_name>/group/
```

```bash
curl -s -X POST "$OW/api/v1/controller/device/" -H "Authorization: Bearer $OW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"<device-name>","organization":"<org-uuid>","mac_address":"<mac>","group":null,"config":null}'
# retire: deactivate first, then delete
curl -s -X POST   "$OW/api/v1/controller/device/<uuid>/deactivate/" -H "Authorization: Bearer $OW_TOKEN"
curl -s -X DELETE "$OW/api/v1/controller/device/<uuid>/"            -H "Authorization: Bearer $OW_TOKEN"
```

- Writable list/detail fields: `id`, `name`, `organization`, `group`, `mac_address`, `key`, `last_ip`, `management_ip`, `model`, `os`, `system`, `notes`, `config`, plus read-only `created`/`modified`;
  detail also returns `is_deactivated`. `hardware_id` is in neither serializer, so the REST API cannot read or write it in 1.3.
- List filters include `organization`, `group`, `config__status`, `config__backend`, `config__templates` (UUID-validated).
- The whole controller API is mounted only while `OPENWISP_CONTROLLER_API` is true (default `True`).
- `OPENWISP_CONTROLLER_DEVICE_NAME_UNIQUE` default `True`: names are unique per organization, case-insensitive, enforced in the application, not the DB.
- `OPENWISP_CONTROLLER_HARDWARE_ID_ENABLED` default `False`; `HARDWARE_ID_OPTIONS` defaults to `max_length` 32, `null` True, `unique` False, `blank` = not enabled; `HARDWARE_ID_AS_NAME` default `True`
  (shows the serial instead of the name).
- Deletion: `Device.delete(check_deactivated=True)` raises `PermissionDenied` (HTTP 403) unless the device is fully deactivated. `?force=true` on the DELETE skips that check; it exists in source but
  is not in the 26.09 docs, so treat it as unsupported.

Gotcha: "fully deactivated" also needs the device's Config in status `deactivated`. `Config.deactivate()` sets `deactivating` and jumps to `deactivated` only when the cleared checksum equals the old
one (an already empty config); otherwise the delete keeps returning 403 until the device fetches its emptied config. Passive-only devices with a non-empty config never do.

Source: `$P/openwisp_controller/config/api/urls.py:46-85`, `$P/openwisp_controller/config/api/views.py:100-150`, `$P/openwisp_controller/config/api/serializers.py:252-345`,
`$P/openwisp_controller/config/settings.py:42-54`, `$P/openwisp_controller/config/base/device.py:185-220,308-313`, `$P/openwisp_controller/config/base/config.py:721-722,929-953`;
https://openwisp.io/docs/26.09/controller/user/rest-api.html, https://openwisp.io/docs/26.09/controller/user/settings.html.

## 3. Monitoring REST: push, backfill, metrics, charts, health

Decision: devices (or a collector acting for them) push NetJSON DeviceMonitoring with the device key; humans and tools read with a Bearer token.

```text
POST /api/v1/monitoring/device/<uuid>/?key=<device-key>[&time=<dd-mm-YYYY_HH:MM:SS.ffffff>][&current=true]
GET  /api/v1/monitoring/device/<uuid>/?key=<device-key>&status=true&time=1d|3d|7d|30d|365d
GET  /api/v1/monitoring/device/<uuid>/?start=YYYY-MM-DD HH:MM:SS&end=YYYY-MM-DD HH:MM:SS[&timezone=<tz>][&csv=1]
GET  /api/v1/monitoring/device/                     ?monitoring__status=critical|problem|ok|unknown  &organization_slug=<slug>
GET  /api/v1/monitoring/device/<uuid>/metric/       ?is_healthy=false
GET  /api/v1/monitoring/dashboard/                  ?organization_slug=<a>,<b>&time=7d
GET  /api/v1/monitoring/geojson/  |  /api/v1/monitoring/location/<uuid>/device/  |  /api/v1/monitoring/wifi-session/
```

```bash
curl -s -X POST "$OW/api/v1/monitoring/device/<uuid>/?key=<device-key>&time=05-10-2026_01:30:00.000000" \
  -H "Content-Type: application/json" -d @devicemonitoring.json
```

- POST returns `200` with an empty body once the payload validates; the write itself is queued as Celery task `write_device_metrics`. A `200` therefore proves acceptance, not storage. A schema failure
  returns `400` synchronously; a failure inside the task is visible only in worker logs.
- `time` must match `%d-%m-%Y_%H:%M:%S.%f` exactly (microseconds required) or the API returns `400 {"detail": "Incorrect time format"}`. It is parsed as UTC.
- A deactivated device's POST returns `404`; data is dropped.
- Device-key auth works only when `?key=` is present; otherwise safe methods fall back to Bearer/session auth.
- `/metric/` needs organization-manager rights plus Device model permissions; each item carries `name`, `key`, `is_healthy`.
- Chart reads: `time` defaults to the chart default (`OPENWISP_MONITORING_DEFAULT_CHART_TIME`, `7d`); a custom range must not exceed 365 days or end in the future.

Gotcha: the 26.09 doc says a POST without `time` uses "server local time"; the 1.3 code uses `now().utcnow()`. Always send `time` in UTC for backfill.

Source: `$P/openwisp_monitoring/device/api/urls.py:7-52`, `$P/openwisp_monitoring/device/api/views.py:82-206,345-368`, `$P/openwisp_monitoring/views.py:32-80`,
`$P/openwisp_monitoring/monitoring/api/urls.py:9`, `$P/openwisp_monitoring/settings.py:31`; https://openwisp.io/docs/26.09/monitoring/user/rest-api.html.

## 4. Time-series store: InfluxDB 1.8

Decision: read InfluxDB directly only for diagnosis; product views go through the charts API.

```python
# image settings.py, built from env INFLUXDB_*
TIMESERIES_DATABASE = {
    "BACKEND": "openwisp_monitoring.db.backends.influxdb",
    "USER": "...", "PASSWORD": "...", "NAME": "openwisp", "HOST": "openwisp-influxdb", "PORT": "8086",
}
OPENWISP_MONITORING_DEFAULT_RETENTION_POLICY = "26280h0m0s"   # env INFLUXDB_DEFAULT_RETENTION_POLICY
# OPENWISP_MONITORING_SHORT_RETENTION_POLICY default "24h0m0s"
```

```bash
IQ="docker exec <influxdb-container> influx -database openwisp -precision rfc3339 -execute"
$IQ 'SHOW DATABASES'
$IQ 'SHOW RETENTION POLICIES ON openwisp'
$IQ 'SHOW MEASUREMENTS'
$IQ 'SHOW TAG KEYS FROM ping'
$IQ 'SELECT * FROM ping ORDER BY time DESC LIMIT 1'
$IQ 'SELECT count(reachable) FROM ping WHERE time > now() - 7d GROUP BY time(1d) fill(none)'
```

Live read on 2026-10-05: database `openwisp`; retention policies `autogen` 26280h0m0s (shard 168h, default) and `short` 24h0m0s (shard 1h). Measurements are named by metric key (`ping`, `cpu`,
`memory`, `traffic`, `wifi_clients`, `data_collected`, `device_data`, plus custom keys); device series carry tags `content_type` and `object_id` (the device UUID), and per-interface or per-peer
metrics add their `main_tags` (for example `ifname`).

Gotcha: `device_data` (the raw status document) is written to the `short` policy, so it disappears after 24 hours while charts persist; query `short.device_data` explicitly. Its tag is `pk`, not `object_id`. If the InfluxDB HTTP auth
is on, add `-username`/`-password` from the environment rather than the command line.

Source: `/opt/openwisp/openwisp/settings.py:216-226`, `$P/openwisp_monitoring/device/settings.py:55-56`, `$P/openwisp_monitoring/device/utils.py:4-21`
(`SHORT_RP = "short"`, `DEFAULT_RP = "autogen"`), `$P/openwisp_monitoring/device/base/models.py:155,264` (`device_data` written with
`retention_policy=SHORT_RP` and tag `pk`); live `SHOW RETENTION POLICIES`; https://openwisp.io/docs/26.09/monitoring/user/settings.html,
https://openwisp.io/docs/26.09/docker/user/settings.html.

## 5. Celery queues, workers and beat

Decision: run every queue the routes name; after any restart, prove each worker answers before trusting a push.

| Queue               | Routed tasks                                                                            | Container (`MODULE_NAME`) and pidfile                |
| ------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `celery` (default)  | everything unrouted, including `openwisp_monitoring.device.tasks.write_device_metrics`  | `celery` → `/opt/openwisp/celery.pid`                |
| `network`           | `openwisp_controller.connection.tasks.*`                                                | `celery` → `celery_network.pid`                      |
| `firmware_upgrader` | `upgrade_firmware`, `batch_upgrade_operation`                                           | `celery` → `celery_firmware_upgrader.pid`            |
| `monitoring`        | `openwisp_monitoring.monitoring.tasks.*` (`timeseries_write`, `timeseries_batch_write`) | `celery_monitoring` → `celery_monitoring.pid`        |
| `monitoring_checks` | `openwisp_monitoring.check.tasks.perform_check`                                         | `celery_monitoring` → `celery_monitoring_checks.pid` |

Beat (`celerybeat` container, `celery -A openwisp beat`): `run_checks` every 5 minutes; topology `update_topology` every 5 minutes and `save_snapshot` 23:45; `delete_old_notifications` (90 days) at
23:00; user expiry tasks 00:01 and 00:03; `send_usage_metrics` daily unless `METRIC_COLLECTION` is false.

```bash
docker exec <celery-container> sh -c 'cd /opt/openwisp && celery -A openwisp inspect ping'
docker exec <celery-container> sh -c 'cd /opt/openwisp && celery -A openwisp inspect active_queues'
docker exec <celery-monitoring-container> ps -eo pid,etime,args | grep '[c]elery'
docker exec <celery-monitoring-container> tail -n 50 /opt/openwisp/logs/celery_monitoring.log
```

- Workers start with `--detach` and the container's foreground process is `tail -f /opt/openwisp/logs/*`. A container shown `Up` can therefore have no worker at all; `ps` and `inspect ping` are the
  only proof. With all workers present, `inspect ping` lists five nodes (`celery@`, `network@`, `firmware_upgrader@`, `monitoring@`, `monitoring_checks@`).
- Queues are created only when `USE_OPENWISP_CELERY_MONITORING`/`_NETWORK`/`_FIRMWARE` are `True`; `USE_OPENWISP_CELERY_TASK_ROUTES_DEFAULTS` gates the routing table. Concurrency comes from
  `OPENWISP_CELERY_*_COMMAND_FLAGS`.

Gotcha: a plain container restart can leave a stale `/opt/openwisp/celery*.pid`; the detached worker then refuses to start, pushes still return 200 and `write_device_metrics` piles up unprocessed.
Clearing pidfiles and restarting are writes to the running platform: get the operator's go-ahead first, then clear the pidfiles before restarting (only `celerybeat.pid` is removed by the start script). A Redis `MISCONF` (RDB snapshot cannot persist) also kills writes; check `redis-cli INFO persistence`.

Source: `/opt/openwisp/openwisp/celery.py:25-124`, `/opt/openwisp/init_command.sh:77-123`, `/opt/openwisp/openwisp/settings.py:181-185`, `$P/openwisp_monitoring/device/tasks.py:83-84`,
`$P/openwisp_monitoring/monitoring/tasks.py:36-72`; https://openwisp.io/docs/26.09/docker/user/settings.html.

## 6. Custom metrics, charts, alerts and stock checks

Decision: add metrics declaratively through `OPENWISP_MONITORING_METRICS`/`OPENWISP_MONITORING_CHARTS` in settings, or `register_metric`/`register_chart` in an `AppConfig.ready()`; never patch the
package.

```python
OPENWISP_MONITORING_METRICS = {
    "<metric-key>": {
        "label": "<label>", "name": "<name>", "key": "<metric-key>",
        "field_name": "<field>", "related_fields": ["<field2>"],
        "alert_settings": {"operator": "<", "threshold": 1, "tolerance": 0},   # optional; omit for observation-only metrics
        "charts": {
            "<chart-key>": {
                "type": "scatter", "title": "<title>", "description": "<text>", "unit": "<unit>", "order": 400,
                "summary_labels": ["<label>"],
                "query": {"influxdb": "SELECT MEAN(<field>) AS <field> FROM {key} WHERE time >= '{time}' {end_date} "
                                      "AND content_type = '{content_type}' AND object_id = '{object_id}' GROUP BY time(1d)"},
            },
        },
    },
}
# or, in code:
from openwisp_monitoring.monitoring.configuration import register_metric, register_chart
register_metric("<metric-key>", metric_config)     # raises ImproperlyConfigured if the key already exists
register_chart("<chart-key>", chart_config)
```

- `register_metric` rejects built-in keys but deep-merges a partial entry of the same key from `OPENWISP_MONITORING_METRICS`, which is how a built-in metric is overridden. It also registers the
  metric's notification types.
- AlertSettings per Metric hold `custom_operator`, `custom_threshold`, `custom_tolerance` (minutes) and `is_active`; empty fields fall back to the metric config's `alert_settings`.
  `OPENWISP_MONITORING_TOLERANCE_INTERVAL` defaults to 300.
- Stock checks and their auto-create switches: Ping `AUTO_PING` (True), Configuration Applied `AUTO_DEVICE_CONFIG_CHECK` (True), Iperf3 `AUTO_IPERF3` (False), WiFi Clients `AUTO_WIFI_CLIENTS_CHECK`
  (False), Monitoring Data Collected `AUTO_DATA_COLLECTED_CHECK` (True, 60-minute interval), each prefixed `OPENWISP_MONITORING_`.
- `OPENWISP_MONITORING_CRITICAL_DEVICE_METRICS` defaults to ping `reachable` plus `data_collected`; a device is critical when they fail. Replacing the list is how a passive deployment makes stale
  data, not ping, the reachability signal.
- `OPENWISP_MONITORING_AUTO_CLEAR_MANAGEMENT_IP` defaults to True: a critical device loses its management IP.

Gotcha: the `AUTO_*` switches only stop new Check objects from being created when a device is created; checks that already exist keep running
(`run_checks` takes every `is_active=True` check). Deactivate or delete existing checks in the admin.

Source: `$P/openwisp_monitoring/monitoring/settings.py:3-13`, `$P/openwisp_monitoring/monitoring/configuration.py:802-937`, `$P/openwisp_monitoring/monitoring/base/models.py:850-880`,
`$P/openwisp_monitoring/check/settings.py:1-66`, `$P/openwisp_monitoring/check/base/models.py:110-127`,
`$P/openwisp_monitoring/check/tasks.py:52`, `$P/openwisp_monitoring/device/settings.py:1-63`; https://openwisp.io/docs/26.09/monitoring/developer/utils.html,
https://openwisp.io/docs/26.09/monitoring/user/checks.html, https://openwisp.io/docs/26.09/monitoring/user/settings.html.

## 7. Notifications

Decision: define custom alarm types with `register_notification_type` in an app's `ready()`, and choose web and email per type.

```python
from openwisp_notifications.types import register_notification_type
register_notification_type("<type-name>", {
    "verbose_name": "<shown name>", "level": "error", "verb": "<verb>",
    "message": "[{notification.target}]({notification.target_link}) {notification.verb}.",
    "email_subject": "[{site.name}] {notification.target} <subject>",
    "web_notification": True, "email_notification": False,
})
```

```text
GET  /api/v1/notifications/notification/            POST /api/v1/notifications/notification/read/
GET  /api/v1/notifications/user/user-setting/       GET  /api/v1/notifications/organization/<uuid>/setting/
POST /api/v1/notifications/notification/ignore/
```

- Global switches: `OPENWISP_NOTIFICATIONS_WEB_ENABLED` (True), `OPENWISP_NOTIFICATIONS_EMAIL_ENABLED` (True), `EMAIL_BATCH_INTERVAL` (10800 s), `EMAIL_BATCH_DISPLAY_LIMIT` (15), `CACHE_TIMEOUT` (2
  days), `NOTIFICATION_STORM_PREVENTION`, `IGNORE_ENABLED_ADMIN`, `POPULATE_PREFERENCES_ON_MIGRATE`.
- Users override web/email per type and per organization through notification settings; the type's flags are only defaults.
- `register_notification_type` raises `ImproperlyConfigured` for a name already registered, so register once per process.

Gotcha: types registered from a module that only some processes import are missing in the others; every Django process (dashboard, api, websocket, celery, celery_monitoring, celerybeat) must load the
registering app.

Source: `$P/openwisp_notifications/types.py:72-93`, `$P/openwisp_notifications/settings.py:14-55`, `$P/openwisp_notifications/urls.py:22`, `$P/openwisp_notifications/api/urls.py:12-65`;
https://openwisp.io/docs/26.09/notifications/developer/notification-types.html, https://openwisp.io/docs/26.09/notifications/user/settings.html.

## 8. Organizations and API scoping

Decision: give each integration a non-superuser account that is organization manager (`is_admin=True` on its OrganizationUser) of exactly the organizations it serves, with Django model permissions for
the objects it touches.

- Superusers bypass organization filtering entirely (`FilterByOrganization.get_queryset`).
- Other users see objects whose `organization` is in `organizations_managed` (`...Managed` mixins) or `organizations_dict` (`...Membership`); the `Managed`/`Owned` variants also include shared objects
  (`organization IS NULL`) when the user manages at least one organization.
- Members with `is_admin=False` are end users: no admin access even when staff.
- Shared objects (templates, VPN servers, subnets and similar) have no organization and are managed by superusers.

```bash
curl -s "$OW/api/v1/users/organization/" -H "Authorization: Bearer $OW_TOKEN"   # what this token can see
```

Gotcha: a token that "sees nothing" is usually a member without `is_admin`, not a permission-group fault.

Source: `$P/openwisp_users/api/mixins.py:14-90`; https://openwisp.io/docs/26.09/users/user/basic-concepts.html.

## 9. docker-openwisp settings and overrides

Decision: change behaviour through env vars and the mounted `custom_django_settings.py`, never by editing the image.

- Image tag 26.09.0 ships module 1.3 releases (versions in the header; `/opt/openwisp/openwisp/VERSION` reads `26.09.0`).
- Every env var whose name contains `OPENWISP_` becomes a Django setting of the same name; digits become int, `True`/`False` bool, `None` None, and JSON strings are parsed.
- Feature switches: `USE_OPENWISP_MONITORING`, `USE_OPENWISP_TOPOLOGY`, `USE_OPENWISP_FIRMWARE`, `USE_OPENWISP_RADIUS`, the `USE_OPENWISP_CELERY_*` queue switches, `METRIC_COLLECTION`. Store:
  `INFLUXDB_HOST/PORT/NAME/USER/PASS`, `INFLUXDB_DEFAULT_RETENTION_POLICY`. Broker: `REDIS_*` (`CELERY_BROKER_URL` default is Redis DB 2, channels DB 3).
- Custom settings: mount a directory at `/opt/openwisp/openwisp/configuration` (with `__init__.py` and `custom_django_settings.py`) into dashboard, api, websocket, celery, celery_monitoring and
  celerybeat. The image imports it with `from .configuration.custom_django_settings import *` as the last line of settings.py, so it overrides everything above it.

```yaml
services:
  dashboard:
    volumes:
      - ./customization/configuration/django:/opt/openwisp/openwisp/configuration:ro
```

Gotcha: the import is wrapped in `try/except ImportError: pass`, so a broken or missing file fails silently; verify an override with `python manage.py shell -c "from django.conf import settings;
print(settings.<NAME>)"` in each container. The docs list five containers; mount it in the websocket container too or its settings diverge (UNVERIFIED whether websocket reads every override it needs).

Source: `/opt/openwisp/openwisp/settings.py:15-28,180-185,216-226,451-494`; https://openwisp.io/docs/26.09/docker/user/customization.html, https://openwisp.io/docs/26.09/docker/user/settings.html.

## 10. Management commands

Decision: run commands in the dashboard container from `/opt/openwisp`; prefer read-only ones in production.

```bash
docker exec -w /opt/openwisp <dashboard-container> python manage.py help
docker exec -w /opt/openwisp <dashboard-container> python manage.py run_checks
```

| Command                             | App                   | Effect                                                                       |
| ----------------------------------- | --------------------- | ---------------------------------------------------------------------------- |
| `run_checks`                        | monitoring.check      | runs all checks for all devices now (beat does it every 5 minutes)           |
| `migrate_timeseries`                | monitoring.monitoring | queues the time-series migration (retention policies, schema)                |
| `clear_last_ip`                     | controller.config     | clears `last_ip` on devices; writes                                          |
| `print_cache_dependencies`          | controller.config     | prints controller cache dependencies; read-only (UNVERIFIED beyond its name) |
| `create_notification`               | notifications         | creates a test notification; writes                                          |
| `populate_notification_preferences` | notifications         | fills missing notification settings for users                                |
| `export_users`                      | users                 | exports users to CSV                                                         |
| `save_snapshot`, `update_topology`  | network_topology      | topology snapshot and refresh, also run by beat                              |

Gotcha: `run_checks` and `migrate_timeseries` hand work to Celery; without live workers (section 5) they appear to succeed and do nothing.

Source: `ls $P/*/*/management/commands/` and `$P/*/management/commands/` in the image; https://openwisp.io/docs/26.09/monitoring/user/management-commands.html.
