---
Title: OpenWISP deployment, backup, recovery and geo
Category: skill-reference
Status: current
Authority: Installed OpenWISP 26.09.0 images (/opt/openwisp, modules 1.3), PostgreSQL 15.8 and InfluxDB 1.8.10 tool usage, and the versioned 26.09 docs; cited lines win
Scope: docker-openwisp and ansible-openwisp2, process roles, PostGIS, Redis and InfluxDB, scaling knobs, backup, restore order and verification, and geo data
Last reviewed: 2026-10-05
Summary: What each OpenWISP process and store holds, how to back it up and restore it in a safe order, and how geo data is modelled, verified against the installed 26.09.0 images.
---

# OpenWISP deployment, backup, recovery and geo

Verified against: OpenWISP images 26.09.0 (`/opt/openwisp/openwisp/VERSION` reads `26.09.0`), modules 1.3, django-loci 1.3, PostgreSQL 15.8 with PostGIS image `postgis/postgis:15-3.4`, InfluxDB
1.8.10, Redis 7, checked 2026-10-05.

Module status in the checked install: `openwisp_controller.geo` is enabled; estimated location is off (`OPENWISP_CONTROLLER_ESTIMATED_LOCATION_ENABLED` needs WHOIS, which is off). Containers running:
dashboard, api, websocket, celery, celery-monitoring, celerybeat, nginx, db (PostGIS), redis, influxdb. Not running: freeradius, openvpn, postfix. At the check the `celery` and `celery-monitoring`
containers had no worker process (read-only `ps`, 2026-10-05).

Citations name image files as `/opt/openwisp/<file>:<line>` and module files as `$P/<module>/<file>:<line>` (`$P` = `/usr/local/lib/python3.14/site-packages`). No backup or restore was executed for
this reference: the commands are checked against the installed tools' own usage text, and the restore order is reasoned, marked UNVERIFIED where it has not been rehearsed.

## Summary

| Job                   | Use                                   | Key syntax                                               | Trap                                                            | Section |
| --------------------- | ------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------- | ------- |
| Choose an installer   | docker-openwisp or ansible-openwisp2  | `USE_OPENWISP_*` env vs `openwisp2_*` role variables     | Module toggles have different names in each                     | [1](#1-deployment-options) |
| Know what runs where  | Process roles                         | uWSGI 8000/8001, Daphne 8002, five Celery queues, beat   | Workers are detached: a container shown Up can have no worker   | [2](#2-process-roles) |
| Know what to protect  | Stores and volumes                    | PostGIS, InfluxDB, `media`, `private`, `.ssh`,           | The database holds private keys and device keys                 | [3](#3-data-stores-and-what-they-hold) |
|                       |                                       |   settings mount                                         |                                                                 |         |
| Add capacity          | Scaling knobs                         | `UWSGI_PROCESSES`, `OPENWISP_CELERY_*_COMMAND_FLAGS`     | uWSGI `harakiri=20` kills requests over 20 s                    | [4](#4-scaling-knobs) |
| Take a backup         | `pg_dump`, `influxd backup`,          | `pg_dump -Fc`, `influxd backup -portable -db openwisp`   | Back up the time series and SQL at the same moment              | [5](#5-backup) |
|                       |   volume tar                          |                                                          |                                                                 |         |
| Restore               | Order and verification                | stop apps, SQL, InfluxDB, files, start dashboard, verify | Django start re-creates the InfluxDB database: a later          | [6](#6-restore-order-and-verification) |
|                       |                                       |                                                          |   restore fails                                                 |         |
| Place devices on maps | Location, FloorPlan, DeviceLocation   | `/api/v1/controller/location/`,                          | Coordinates PUT with the device key creates a mobile location   | [7](#7-geo-locations-floorplans-and-the-map) |
|                       |                                       |   `.../device/<pk>/location/`                            |                                                                 |         |

## Contents

- [Summary](#summary)
- [1. Deployment options](#1-deployment-options)
- [2. Process roles](#2-process-roles)
- [3. Data stores and what they hold](#3-data-stores-and-what-they-hold)
- [4. Scaling knobs](#4-scaling-knobs)
- [5. Backup](#5-backup)
- [6. Restore order and verification](#6-restore-order-and-verification)
- [7. Geo: locations, floorplans and the map](#7-geo-locations-floorplans-and-the-map)

## 1. Deployment options

Decision: use docker-openwisp for containerised, horizontally scalable deployments; use ansible-openwisp2 for a single Debian or Ubuntu host managed as a system service.

| Concern               | docker-openwisp                                                       | ansible-openwisp2 (`openwisp.openwisp2` role)                                     |
| --------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Enable RADIUS         | `USE_OPENWISP_RADIUS=True`                                            | `openwisp2_radius: true`, `openwisp2_freeradius_install: true`                    |
| Enable firmware       | `USE_OPENWISP_FIRMWARE=True`                                          | `openwisp2_firmware_upgrader: true` (default false)                               |
| Enable topology       | `USE_OPENWISP_TOPOLOGY=True`                                          | `openwisp2_network_topology: true` (default false)                                |
| Monitoring            | `USE_OPENWISP_MONITORING=True`                                        | `openwisp2_monitoring: true` (default)                                            |
| Extra Django settings | mounted `custom_django_settings.py`                                   | `openwisp2_extra_django_settings`, `openwisp2_extra_django_settings_instructions` |
| Custom module source  | `.build.env`: `OPENWISP_CONTROLLER_SOURCE=...` and friends, rebuild   | `openwisp2_controller_version` and friends (pip specifiers)                       |
| Upgrade               | new image tag, `docker compose up`; dashboard runs `migrate` on start | `ansible-galaxy install --force openwisp.openwisp2`, re-run the playbook          |

- The role targets ansible-core 2.13+ and Debian Trixie/Bookworm or Ubuntu 22/24/26 LTS (26.09 docs).
- docker: disabling a module means removing its container and setting its `USE_OPENWISP_*` flag to False; the settings module then removes the app from `INSTALLED_APPS`.

Gotcha: the docker settings file removes `openwisp_radius`, `openwisp_firmware_upgrader` and `openwisp_network_topology` from `INSTALLED_APPS` when their flag is False, but their tables stay in
PostgreSQL. Turning a module off is not a data deletion; turning it back on finds the old rows.

Source: `/opt/openwisp/openwisp/settings.py:455-480`; https://openwisp.io/docs/26.09/docker/user/customization.html; https://openwisp.io/docs/26.09/ansible/index.html;
https://openwisp.io/docs/26.09/ansible/user/enabling-modules.html; https://openwisp.io/docs/26.09/ansible/user/role-variables.html.

## 2. Process roles

Decision: map every symptom to the process that owns it before restarting anything.

| Container (docker)  | Process                                                                                             | Owns                                                                     |
| ------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `dashboard`         | uWSGI `openwisp.wsgi:application` on 8000; on start: `migrate`, ssh key,                            | Admin UI; schema migrations                                              |
|                     |   `load_init_data.py`, `collectstatic`                                                              |                                                                          |
| `api`               | uWSGI on 8001                                                                                       | REST API and device endpoints; scale out by adding containers            |
| `websocket`         | `daphne -b 0.0.0.0 -p 8002 --proxy-headers openwisp.asgi:application` under supervisord             | Live UI updates, mobile locations, command and upgrade progress          |
| `celery`            | workers `celery@` (queue `celery`), `network@`, `firmware_upgrader@`, started `--detach`            | Config push, commands, upgrades, general tasks                           |
| `celery_monitoring` | workers `monitoring@`, `monitoring_checks@`, started `--detach`                                     | Writing metrics, running checks                                          |
| `celerybeat`        | `celery -A openwisp beat`                                                                           | `run_checks` every 5 min, RADIUS clean-up 03:30, topology, notifications |
| `nginx`             | nginx                                                                                               | TLS, routing to uWSGI and Daphne, upload size (`NGINX_CLIENT_BODY_SIZE`) |

- Queue routing is set in `/opt/openwisp/celery.py`: `openwisp_controller.connection.tasks.*` to `network`, monitoring tasks to `monitoring`, `perform_check` to `monitoring_checks`, firmware tasks to
  `firmware_upgrader`, each only when its `USE_OPENWISP_CELERY_*` flag is true.
- Each worker writes its log to `/opt/openwisp/logs/celery*.log`; the container's foreground process is `tail -f` of those logs.

Gotcha: because workers are started `--detach` and the container's PID 1 is `tail`, a dead worker leaves the container Up. Prove liveness with `celery -A openwisp inspect ping` and `ps`, not with
`docker ps`.

Source: `/opt/openwisp/init_command.sh` (module branches); `/opt/openwisp/uwsgi.ini`; `/opt/openwisp/celery.py`; `docker inspect` of the websocket container (command `supervisord ... daphne.conf`) and
its `ps` (read-only, 2026-10-05); https://openwisp.io/docs/26.09/docker/user/architecture.html (snapshot `documents/openwisp-26.09-docker-architecture.html`).

## 3. Data stores and what they hold

Decision: treat PostgreSQL, InfluxDB and three file volumes as state; treat Redis, static files and logs as rebuildable.

| Store                                         | Holds                                                                                                                   | Backup?                    |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| PostgreSQL + PostGIS (`openwisp` DB)          | Every model: devices and device keys, configs, templates, PKI CAs and certificates with `private_key`, Credentials      | Yes, secret                |
|                                               |   `params`, VPN keys, RADIUS users and accounting, geometry                                                             |                            |
| InfluxDB 1.8 (`openwisp` DB)                  | Metric time series; retention policies `autogen` (26280h, default) and `short` (24h)                                    | Yes                        |
| `media` volume (`/opt/openwisp/media`)        | Public uploads, e.g. floorplan images at `floorplans/<id>.<ext>`                                                        | Yes                        |
| `private` volume (`/opt/openwisp/private`)    | Firmware images (`FirmwareImage.file`), RADIUS batch CSV files                                                          | Yes, may be large          |
| `.ssh` volume (`/home/openwisp/.ssh`)         | The server's generated `id_ed25519` key pair                                                                            | Yes, secret                |
| Settings bind mount                           | Custom Django settings and extension apps                                                                               | Yes (in version control)   |
|   (`/opt/openwisp/openwisp/configuration`)    |                                                                                                                         |                            |
| Redis                                         | DB 0 cache (incl. config checksums, 30 days), DB 1 sessions, DB 2 Celery broker, DB 3 channel layer                     | No (queued tasks are lost) |
| `static` volume                               | `collectstatic` output                                                                                                  | No                         |

Gotcha: a database dump is a credential store (device keys, CA private keys, SSH credentials, VPN private keys); encrypt it and restrict who can read it.

Source: `/opt/openwisp/openwisp/settings.py:148-149`, `:170-185`, `:216-269`, `:312-314`; `$P/django_x509/base/models.py:181-189`; `$P/openwisp_controller/config/base/device.py:49`;
`$P/openwisp_firmware_upgrader/base/models.py:256-263`; `$P/openwisp_radius/base/models.py:982-988`; `$P/django_loci/storage.py`; `docker inspect` mounts and `influx -execute "SHOW RETENTION
POLICIES"` (read-only, 2026-10-05).

## 4. Scaling knobs

Decision: scale the API horizontally, size uWSGI per container, and give each Celery queue its own concurrency.

```text
# docker-openwisp env (values in the checked install)
UWSGI_PROCESSES=2  UWSGI_THREADS=2  UWSGI_LISTEN=100
OPENWISP_CELERY_COMMAND_FLAGS=--concurrency=1
OPENWISP_CELERY_NETWORK_COMMAND_FLAGS=--concurrency=1
OPENWISP_CELERY_FIRMWARE_COMMAND_FLAGS=--concurrency=1
OPENWISP_CELERY_MONITORING_COMMAND_FLAGS=--concurrency=1
OPENWISP_CELERY_MONITORING_CHECKS_COMMAND_FLAGS=--concurrency=1
```

```yaml
# ansible-openwisp2 equivalents (role defaults from the 26.09 variables page)
openwisp2_uwsgi_processes: 1
openwisp2_uwsgi_threads: 2
openwisp2_daphne_processes: 2
openwisp2_celery_autoscale: 4,1
openwisp2_celery_network_autoscale: 8,4
openwisp2_celery_firmware_upgrader_autoscale: 8,4
```

- Celery runs with `CELERY_TASK_ACKS_LATE = True` and `CELERY_WORKER_PREFETCH_MULTIPLIER = 1`: a worker killed mid-task leaves the task for redelivery.
- The agent's `bootup_delay` spreads registration load after a mass power-up; raise it on large fleets.

Gotcha: `uwsgi.ini` sets `harakiri=20`; any request over 20 seconds is killed, so large list exports and big uploads need paging or a longer limit through a custom uWSGI file.

Source: `/opt/openwisp/uwsgi.ini`; `/opt/openwisp/openwisp/settings.py:183-185`; container env read with `docker exec ... env` (2026-10-05); https://openwisp.io/docs/26.09/docker/user/settings.html;
https://openwisp.io/docs/26.09/ansible/user/role-variables.html.

## 5. Backup

Decision: take the SQL dump, the InfluxDB portable backup and the file volumes in one window, and label them with the image tag.

```bash
STAMP=$(date +%Y%m%d_%H%M)
# 1. PostgreSQL (custom format, restorable with pg_restore)
docker exec <db-container> pg_dump -U openwisp -d openwisp -Fc > "openwisp-db-$STAMP.dump"
# 2. InfluxDB 1.8 portable backup, run inside the influx container (RPC on 127.0.0.1:8088)
docker exec <influxdb-container> influxd backup -portable -db openwisp "/tmp/ow-influx-$STAMP"
docker cp "<influxdb-container>:/tmp/ow-influx-$STAMP" "./ow-influx-$STAMP"
# 3. file volumes
docker run --rm -v <media-volume>:/v/media:ro -v <private-volume>:/v/private:ro -v <ssh-volume>:/v/ssh:ro \
  -v "$PWD":/out alpine tar czf "/out/openwisp-files-$STAMP.tgz" -C /v .
# 4. record the versions the backup belongs to
docker exec <dashboard-container> cat /opt/openwisp/openwisp/VERSION
```

- `influxd backup` flags (installed usage): `-portable`, `-host` (default `127.0.0.1:8088`), `-db`, `-rp`, `-shard`, `-start`/`-end` (RFC3339), `-since`, `-skip-errors`.
- The 26.09 documentation index for docker and ansible has no backup page; the procedure here is assembled from the tools, not from an OpenWISP guide.

Gotcha: the backup captures `device_data` in the `short` policy only for its last 24 hours, and metrics written after the SQL dump reference objects the dump does not have; take both close together.

Source: `influxd backup -help` and `pg_dump --help` run in the installed containers (2026-10-05); https://docs.influxdata.com/influxdb/v1/administration/backup_and_restore/ (v1 page; the 1.8.10 flags
match the installed usage text); `/opt/openwisp/init_command.sh`. Not executed against this install: UNVERIFIED as a tested procedure.

## 6. Restore order and verification

Decision: restore with every Django and Celery container stopped, data stores first, dashboard last, then verify each layer.

```bash
# 0. stop: dashboard api websocket celery celery_monitoring celerybeat (keep db, influxdb, redis up)
# 1. PostgreSQL into an empty openwisp database on the same PostGIS major version
docker exec -i <db-container> pg_restore -U openwisp -d openwisp --clean --if-exists --no-owner < openwisp-db-<stamp>.dump
# 2. InfluxDB: the database must not exist; restore, or restore beside it and copy in
docker exec <influxdb-container> influx -execute 'DROP DATABASE "openwisp"'
docker cp ./ow-influx-<stamp> <influxdb-container>:/tmp/ow-influx
docker exec <influxdb-container> influxd restore -portable -db openwisp /tmp/ow-influx
# 3. files back into media, private and .ssh volumes (reverse of the tar in section 5)
# 4. clear rebuildable state: Redis cache DB 0 holds 30-day config checksums
# 5. start dashboard (runs migrate), then api, websocket, celery, celery_monitoring, celerybeat
```

```text
# alternative for step 2 when the database already exists (InfluxDB v1 docs)
influxd restore -portable -db openwisp -newdb openwisp_restore /tmp/ow-influx
SELECT * INTO "openwisp"."autogen".:MEASUREMENT FROM "openwisp_restore"."autogen"./.*/ GROUP BY *
SELECT * INTO "openwisp"."short".:MEASUREMENT FROM "openwisp_restore"."short"./.*/ GROUP BY *
DROP DATABASE "openwisp_restore"
```

Verification, in rung order: `migrate` reports nothing to apply for a same-version restore; the REST device count matches the pre-backup count; `celery -A openwisp inspect ping` answers from every
expected node; `influx -database openwisp -execute 'SHOW MEASUREMENTS'` lists the old measurements; a device chart shows points from before the backup; one device's checksum endpoint returns 200.

Gotcha: `MonitoringConfig.ready()` calls `timeseries_db.create_database()` in every Django process, and the device app re-creates the retention policies. Starting any OpenWISP container before step 2
re-creates an empty `openwisp` database, and `influxd restore -portable` then refuses with "database already exists".

Source: `$P/openwisp_monitoring/monitoring/apps.py:17-19`; `$P/openwisp_monitoring/db/backends/influxdb/client.py:74-78`; `$P/openwisp_monitoring/device/apps.py:44-45`; `influxd restore -help` and
`pg_restore --help` in the installed containers (2026-10-05); https://docs.influxdata.com/influxdb/v1/administration/backup_and_restore/ ("Restore data to an existing database"). The Redis cache step
(4) is an inference from the 30-day checksum cache in `$P/openwisp_controller/config/base/base.py:35`: UNVERIFIED by rehearsal.

## 7. Geo: locations, floorplans and the map

Decision: give every fixed device an outdoor or indoor Location; add a FloorPlan only for indoor sites where position inside the building matters.

| Model            | Key fields                                                                                          | REST                                                   |
| ---------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `Location`       | `name`, `type` (`outdoor` or `indoor`), `is_mobile`, `address`, `geometry` (required unless mobile) | `/api/v1/controller/location/`, `.../location/<pk>/`   |
| `FloorPlan`      | `location`, `floor` (integer), `image` (stored as `floorplans/<id>.<ext>` in `media`)               | `/api/v1/controller/floorplan/`, `.../floorplan/<pk>/` |
| `DeviceLocation` | `content_object` (the device), `location`, `floorplan`, `indoor` (position on the plan)             | `/api/v1/controller/device/<pk>/location/`             |

```bash
curl -s "$OW/api/v1/controller/location/geojson/" -H "Authorization: Bearer $OW_TOKEN"        # map layer
curl -s "$OW/api/v1/controller/location/<pk>/device/" -H "Authorization: Bearer $OW_TOKEN"     # devices at a location
curl -s "$OW/api/v1/controller/location/<pk>/indoor-coordinates/" -H "Authorization: Bearer $OW_TOKEN"
# device self-report (device key, no user token): creates a mobile outdoor location if none
curl -s -X PUT "$OW/api/v1/controller/device/<pk>/coordinates/?key=<device-key>" \
  -H "Content-Type: application/json" -d '{"type": "Feature", "geometry": {"type": "Point", "coordinates": [144.96, -37.81]}, "properties": {}}'
```

- The device map in the dashboard is fed by the GeoJSON endpoint; live position changes of mobile devices travel over the websocket container.
- Geocoding of addresses uses `DJANGO_LOCI_GEOCODER` (default `ArcGIS`); estimated location from public IP needs `OPENWISP_CONTROLLER_WHOIS_ENABLED` with MaxMind credentials, then
  `OPENWISP_CONTROLLER_ESTIMATED_LOCATION_ENABLED`.
- `/api/v1/controller/organization/<org-pk>/geo-settings/` holds per-organisation geo settings.

Gotcha: the coordinates endpoint authenticates with the device `key` in the query string and bypasses organisation filtering; a PUT for a device with no location creates a new mobile Location named
after the device. Restrict who holds device keys accordingly. The body is a GeoJSON Feature: `DeviceCoordinatesSerializer` is a `GeoFeatureModelSerializer` on `geometry`, which
unpacks `properties` and `geometry` on input (rest_framework_gis `to_internal_value`).

Source: `$P/openwisp_controller/geo/utils.py` (`get_geo_urls`); `$P/openwisp_controller/geo/api/views.py:45-52` (`DevicePermission`), `:107-152` (`DeviceCoordinatesView`);
`$P/openwisp_controller/geo/settings.py`; `$P/openwisp_controller/geo/api/serializers.py:135-140`; `$P/rest_framework_gis/serializers.py:196-221`; `$P/django_loci/base/models.py:17-155`;
`$P/django_loci/storage.py`; `$P/django_loci/settings.py:5-20`.
