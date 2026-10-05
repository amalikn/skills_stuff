---
Title: OpenWISP connections, commands and firmware upgrades
Category: skill-reference
Status: current
Authority: Installed OpenWISP 26.09.0 image source (controller 1.3 connection app, firmware-upgrader 1.3) and the versioned 26.09 docs; cited lines win
Scope: Credentials, DeviceConnection, the command API, config push over SSH, connection failures, firmware categories, builds, images, upgrades, the firmware queue and safety
Last reviewed: 2026-10-05
Summary: How OpenWISP reaches a device over SSH to run commands, trigger config fetches and reflash firmware, verified against the installed 26.09.0 source, with the safety rails each step has.
---

# OpenWISP connections, commands and firmware upgrades

Verified against: OpenWISP images 26.09.0 (openwisp-controller 1.3, openwisp-firmware-upgrader 1.3, paramiko 5.0.0, scp 0.16.1, celery 5.6.3), checked 2026-10-05.

Module status in the checked install: `openwisp_controller.connection` and `openwisp_firmware_upgrader` are in `INSTALLED_APPS`; `USE_OPENWISP_FIRMWARE=True`, `USE_OPENWISP_CELERY_FIRMWARE=True` and
`USE_OPENWISP_CELERY_NETWORK=True`. Enabled is not running: at the check the `celery` container had no worker process and `celery -A openwisp inspect ping` got no reply, so every task below would
queue and wait (read-only `ps` and `inspect ping`, 2026-10-05).

Citations name the installed file as `$P/<module>/<file>:<line>`, where `$P` is `/usr/local/lib/python3.14/site-packages` in `openwisp-dashboard:26.09.0`; image files are under `/opt/openwisp/`.
Anything not read from source or a versioned 26.09 page is marked UNVERIFIED.

## Summary

| Job                        | Use                            | Key syntax                                             | Trap                                                                | Section |
| -------------------------- | ------------------------------ | ------------------------------------------------------ | ------------------------------------------------------------------- | ------- |
| Store SSH access once      | Credentials, `auto_add`        | `/api/v1/controller/credential/`                       | The 26.09 docs print `/api/v1/connection/credential/`, a 404 here   | [1](#1-credentials-and-auto-add) |
| Bind a device to access    | DeviceConnection               | `/api/v1/controller/device/<pk>/connection/`           | Only `management_ip` is tried unless `MANAGEMENT_IP_ONLY` is False  | [2](#2-deviceconnection-and-reachability) |
| Run a command              | Command API                    | `POST .../device/<pk>/command/`                        | 201 is "queued"; read the Command's `status` and `output`           | [3](#3-commands) |
|                            |                                |   `{"type": "custom", ...}`                            |                                                                     |         |
| Push a config change now   | Update strategy over SSH       | automatic on `modified`                                | It signals the agent to fetch; it uploads nothing                   | [4](#4-config-push-over-ssh) |
| Diagnose a dead connection | `is_working`, `failure_reason` | DeviceConnection fields                                | Monitoring blocks push while health is `critical` or `unknown`      | [5](#5-connection-failures) |
| Organise firmware          | Category, Build, FirmwareImage | `/api/v1/firmware-upgrader/...`                        | Image `type` is the OpenWrt image file name, matched by board       | [6](#6-categories-builds-and-images) |
| Upgrade one device         | DeviceFirmware                 | `PUT .../device/<pk>/firmware/` `{"image": ...}`       | Changing the image starts the upgrade immediately                   | [7](#7-single-and-mass-upgrades) |
| Upgrade a fleet            | Batch upgrade with dry run     | `GET` then `POST .../build/<pk>/upgrade/`              | `upgrade_options` are not in the API serializer                     | [7](#7-single-and-mass-upgrades) |
| Keep upgrades safe         | Upgrader checks and options    | identity, checksum, `sysupgrade --test`, `-c` default  | No automatic return to the old image; cancel stops at 65 % progress | [8](#8-upgrade-safety-options-and-the-queue) |

## Contents

- [Summary](#summary)
- [1. Credentials and auto-add](#1-credentials-and-auto-add)
- [2. DeviceConnection and reachability](#2-deviceconnection-and-reachability)
- [3. Commands](#3-commands)
- [4. Config push over SSH](#4-config-push-over-ssh)
- [5. Connection failures](#5-connection-failures)
- [6. Categories, builds and images](#6-categories-builds-and-images)
- [7. Single and mass upgrades](#7-single-and-mass-upgrades)
- [8. Upgrade safety, options and the queue](#8-upgrade-safety-options-and-the-queue)
- [9. Closed firmware](#9-closed-firmware)

## 1. Credentials and auto-add

Decision: create one Credentials object per organisation and access method, flag it `auto_add` so every current and future device of that organisation gets a DeviceConnection.

```bash
curl -s -X POST "$OW/api/v1/controller/credential/" \
  -H "Authorization: Bearer $OW_TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "ops-ssh-key", "organization": "<org-uuid>",
       "connector": "openwisp_controller.connection.connectors.ssh.Ssh",
       "auto_add": true,
       "params": {"username": "root", "key": "<private-key-pem>", "port": 22}}'
```

| Connector (`OPENWISP_CONNECTORS`)                                    | `params` schema                                                                     | Update strategy |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------- |
| `openwisp_controller.connection.connectors.ssh.Ssh`                  | `oneOf`: `username` + `password` (min 4), or `username` + `key` (min 64); `port` 22 | Yes             |
| `openwisp_controller.connection.connectors.openwrt.snmp.OpenWRTSnmp` | `community` (default `public`), `agent`, `port` 161                                 | No              |
| `openwisp_controller.connection.connectors.airos.snmp.AirOsSnmp`     | as above                                                                            | No              |

- `auto_add` runs `auto_add_credentials_to_devices` as a Celery task on save, and adds the credential to each new device on creation.
- A shared credential (no organisation) is available to every organisation.
- The docker image also generates an ed25519 key at `SSH_PRIVATE_KEY_PATH` on first dashboard start (`ssh-keygen ... -N ""`), on the `openwisp-ssh` volume.

Gotcha: the path in the 26.09 REST page (`/api/v1/connection/credential/`) does not resolve in the installed URLconf; `/api/v1/controller/credential/` does (`connection_api:credential_list`, resolved
read-only with `django.urls.resolve` in the api container, 2026-10-05).

Source: `$P/openwisp_controller/connection/settings.py:3-13` (connectors); `$P/openwisp_controller/connection/connectors/ssh.py:20-56`; `$P/openwisp_controller/connection/connectors/snmp.py`;
`$P/openwisp_controller/connection/base/models.py:103-230` (Credentials, `auto_add`); `/opt/openwisp/init_command.sh` (key generation); https://openwisp.io/docs/26.09/controller/user/rest-api.html.

## 2. DeviceConnection and reachability

Decision: let auto-add create the DeviceConnection, and make sure the device has a `management_ip` that the server can reach.

```bash
curl -s "$OW/api/v1/controller/device/<device-uuid>/connection/" -H "Authorization: Bearer $OW_TOKEN"
```

Fields: `credentials`, `update_strategy` (inferred from the config backend through `OPENWISP_CONFIG_UPDATE_MAPPING` when blank), `enabled`, `params` (override the credential's), and read-only
`is_working`, `failure_reason`, `last_attempt`.

```python
# get_addresses(): what the connector tries, in order
[device.management_ip]                                  # always, when set
+ [device.last_ip]  # only if OPENWISP_CONTROLLER_MANAGEMENT_IP_ONLY is False and it differs
```

- `MANAGEMENT_IP_ONLY` defaults to `True` (it is `True` here): with no `management_ip`, nothing is attempted.
- SSH timeouts: `OPENWISP_SSH_CONNECTION_TIMEOUT` 5 s, `OPENWISP_SSH_AUTH_TIMEOUT` 2 s, `OPENWISP_SSH_BANNER_TIMEOUT` 60 s, `OPENWISP_SSH_COMMAND_TIMEOUT` 30 s.
- A device whose config is fully `deactivated` is refused before any SSH attempt ("Device is deactivated").

Gotcha: an update strategy can be inferred only when the device has a Config; a device without one needs `update_strategy` chosen explicitly, or validation fails.

Source: `$P/openwisp_controller/connection/base/models.py:247-277` (fields), `:330-350` (strategy inference error), `:352-366` (`get_addresses`), `:376-393` (`connect`);
`$P/openwisp_controller/connection/settings.py:29-49`; https://openwisp.io/docs/26.09/user/vpn.html (management network).

## 3. Commands

Decision: run ad-hoc device actions through the command API so each one is recorded with status and output.

```bash
curl -s -X POST "$OW/api/v1/controller/device/<device-uuid>/command/" \
  -H "Authorization: Bearer $OW_TOKEN" -H "Content-Type: application/json" \
  -d '{"type": "custom", "input": {"command": "uptime"}}'
# other stock types:
#   {"type": "reboot", "input": null}
#   {"type": "change_password", "input": {"password": "<new>", "confirm_password": "<new>"}}
curl -s "$OW/api/v1/controller/device/<device-uuid>/command/<command-uuid>/" -H "Authorization: Bearer $OW_TOKEN"
```

- Command `status`: `in-progress`, `success`, `failed`; `output` holds stdout or the connection's `failure_reason`. An optional `connection` field picks a specific DeviceConnection.
- `launch_command` runs on the `network` queue with `soft_time_limit` = `SSH_COMMAND_TIMEOUT` x 1.2.
- Add commands with `OPENWISP_CONTROLLER_USER_COMMANDS` (list of `(name, {"label", "schema", "callable"})`); restrict per organisation with `OPENWISP_CONTROLLER_ORGANIZATION_ENABLED_COMMANDS` (default
  `{"__all__": "*"}`).

```python
def ping_command_callable(destination_address, interface_name=None):
    command = f"ping -c 4 {destination_address}"
    if interface_name:
        command += f" -I {interface_name}"
    return command

OPENWISP_CONTROLLER_USER_COMMANDS = [("ping", {"label": "Ping", "callable": ping_command_callable,
    "schema": {"title": "Ping", "type": "object", "required": ["destination_address"],
               "properties": {"destination_address": {"type": "string"}, "interface_name": {"type": "string"}},
               "message": "Destination Address cannot be empty", "additionalProperties": False}})]
```

Gotcha: `custom` runs any shell string as the credential's user, and `change_password` pipes the password through `passwd`; both are writes to the device, so a project's write policy applies.

Source: `$P/openwisp_controller/connection/commands.py:9-75` (stock commands), `:105-120` (`register_command`); `$P/openwisp_controller/connection/settings.py:45-48`;
`$P/openwisp_controller/connection/base/models.py:431-470`; `$P/openwisp_controller/connection/tasks.py:71-72`; `$P/openwisp_controller/connection/connectors/openwrt/ssh.py:45-51`;
https://openwisp.io/docs/26.09/controller/user/shell-commands.html (snapshot `documents/openwisp-26.09-controller-shell-commands.html`).

## 4. Config push over SSH

Decision: rely on push only to shorten the agent's poll interval; the agent still downloads and applies the config itself.

```text
config change -> Config.status = modified -> update_config.delay(device_pk)   [network queue]
  -> wait 2 s; skip if fully deactivated, if can_be_updated() is False, or if another update_config runs for the device
  -> DeviceConnection.get_working_connection(device) -> connect -> strategy.update_config()
OpenWrt strategy:  (openwisp-config --version || openwisp_config --version)
  >= 0.6.0a: kill -SIGUSR1 <agent pid>        older: /etc/init.d/openwisp_config restart
```

- `can_be_updated()` is `config.status != "applied"`; openwisp-monitoring narrows it to also require monitoring status not `critical` or `unknown`.
- `Device.skip_push_update_on_save()` suppresses the push for one save (used when the agent itself renames a device).

Gotcha: the "push" never transfers the configuration. A device without the openwisp-config agent gains nothing from it, and a device whose agent cannot reach the controller stays `modified`.

Source: `$P/openwisp_controller/connection/tasks.py:19-68`; `$P/openwisp_controller/connection/apps.py:84-94`; `$P/openwisp_controller/connection/connectors/openwrt/ssh.py:10-43`;
`$P/openwisp_controller/config/base/device.py:476-481`; `$P/openwisp_monitoring/device/base/models.py:86-89`; https://openwisp.io/docs/26.09/controller/user/push-operations.html.

## 5. Connection failures

Decision: read `is_working` and `failure_reason` on the DeviceConnection before blaming the device; the string is the connector's exception text.

| Symptom                                     | Likely cause in the installed code                                                        |
| ------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Nothing attempted, `last_attempt` unchanged | No `management_ip` and `MANAGEMENT_IP_ONLY` True; or no worker on the `network` queue     |
| `failure_reason` "Device is deactivated"    | Config `deactivated`                                                                      |
| Timeout or "Unable to connect" text         | Address unreachable from the celery container (tunnel down, wrong `management_interface`) |
| Authentication text                         | Wrong username, password or key in Credentials or DeviceConnection `params`               |
| Push skipped silently                       | `status == applied`, monitoring `critical`/`unknown`, or `should_skip_push_update()`      |

- A change of `is_working` emits `is_working_changed`, which openwisp-monitoring and notifications consume.
- The exact exception strings come from paramiko and are not enumerated here: UNVERIFIED beyond "the text of the exception".

Gotcha: connections are made from the celery worker container, not the dashboard; test reachability from there.

Source: `$P/openwisp_controller/connection/base/models.py:376-428`; `$P/openwisp_controller/connection/tasks.py:36-68`; `/opt/openwisp/celery.py` (`openwisp_controller.connection.tasks.*` to
`network`).

## 6. Categories, builds and images

Decision: one Category per firmware line, one Build per version, one FirmwareImage per hardware image file in the build.

```bash
B="$OW/api/v1/firmware-upgrader"
curl -s -X POST "$B/category/" -H "Authorization: Bearer $OW_TOKEN" -d "name=example-ap&organization=<org-uuid>"
curl -s -X POST "$B/build/" -H "Authorization: Bearer $OW_TOKEN" -d "category=<cat-uuid>&version=1.2.0&os=OpenWrt 23.05.3"
curl -s -X POST "$B/build/<build-uuid>/image/" -H "Authorization: Bearer $OW_TOKEN" \
  -F "type=customimage-squashfs-sysupgrade.bin" -F "file=@./customimage-squashfs-sysupgrade.bin"
```

- Image `type` is a key of `FIRMWARE_IMAGE_MAP`: an OpenWrt image file name mapped to `label` and `boards`. Extend it with `OPENWISP_CUSTOM_OPENWRT_IMAGES`; docker-openwisp reads it from the env var
  of the same name as a JSON list of `{"name", "label", "boards"}`.
- Automatic detection: when a device reports a `model` that matches a board, and an image of that type exists in a build whose `os` equals the device `os`, a DeviceFirmware is created with
  `installed=True` (no upgrade).
- Files go to private storage (`PRIVATE_STORAGE_ROOT`, `/opt/openwisp/private` here); upload size is capped by `OPENWISP_FIRMWARE_UPGRADER_MAX_FILE_SIZE`, set from `NGINX_CLIENT_BODY_SIZE` in docker.

```python
OPENWISP_CUSTOM_OPENWRT_IMAGES = (
    ("customimage-squashfs-sysupgrade.bin", {"label": "Custom WAP-1200", "boards": ("CWAP1200",)}),
)
```

Gotcha: the `os` string on the Build must equal what the agent reports for detection to work; a near match does nothing.

Source: `$P/openwisp_firmware_upgrader/base/models.py:90-130`, `:256-270`; `$P/openwisp_firmware_upgrader/hardware.py:1-25`, `:700-725`; `$P/openwisp_firmware_upgrader/base/models.py:486-507`
(detection); `$P/openwisp_firmware_upgrader/settings.py:7-44`; `/opt/openwisp/openwisp/settings.py` (`OPENWISP_CUSTOM_OPENWRT_IMAGES`, `MAX_FILE_SIZE`);
https://openwisp.io/docs/26.09/firmware-upgrader/user/settings.html.

## 7. Single and mass upgrades

Decision: dry-run every mass upgrade, then narrow it by group or location; upgrade single devices through their DeviceFirmware.

```bash
# single device: set or change the image -> creates an UpgradeOperation and queues it
curl -s -X PUT "$B/device/<device-uuid>/firmware/" -H "Authorization: Bearer $OW_TOKEN" -d "image=<image-uuid>"
# mass: preview, then run
curl -s "$B/build/<build-uuid>/upgrade/?group=<group-uuid>&location=<location-uuid>" -H "Authorization: Bearer $OW_TOKEN"
curl -s -X POST "$B/build/<build-uuid>/upgrade/" -H "Authorization: Bearer $OW_TOKEN" \
  -H "Content-Type: application/json" -d '{"group": "<group-uuid>", "upgrade_all": false}'
# follow and cancel
curl -s "$B/batch-upgrade-operation/<batch-uuid>/" -H "Authorization: Bearer $OW_TOKEN"
curl -s -X POST "$B/upgrade-operation/<op-uuid>/cancel/" -H "Authorization: Bearer $OW_TOKEN"
```

| Object                  | Statuses                                                   |
| ----------------------- | ---------------------------------------------------------- |
| `UpgradeOperation`      | `in-progress`, `success`, `failed`, `cancelled`, `aborted` |
| `BatchUpgradeOperation` | `idle`, `in-progress`, `success`, `failed`, `cancelled`    |

- The batch POST accepts only `upgrade_all`, `group` and `location`. `upgrade_all` also upgrades devices with no DeviceFirmware whose model matches an image ("firmwareless").
- The dry-run GET lists DeviceFirmware objects and, for firmwareless devices, Device objects.
- `aborted` means a prerequisite failed (for example the identity check), `failed` a late-stage failure or no reconnect.

Gotcha: `upgrade_options` (the sysupgrade flags) are not fields of `BatchUpgradeSerializer` or `DeviceFirmwareSerializer`; over the API every upgrade uses the defaults (section 8). Set options in the
admin.

Source: `$P/openwisp_firmware_upgrader/api/views.py:110-135`, `:440-470`; `$P/openwisp_firmware_upgrader/api/serializers.py:81-141`; `$P/openwisp_firmware_upgrader/base/models.py:386-461`
(DeviceFirmware save), `:551-575`, `:819-845`; https://openwisp.io/docs/26.09/firmware-upgrader/user/rest-api.html (snapshot `documents/openwisp-26.09-firmware-upgrader-rest-api.html`).

## 8. Upgrade safety, options and the queue

Decision: trust the upgrader's built-in checks, keep `-c` (preserve `/etc`) on, never set `-F`, and run a dedicated `firmware_upgrader` worker.

```text
OpenWrt upgrader sequence (progress %):
 connect (10) -> uci get openwisp.http.uuid == device pk (15, else aborted)
 -> sha256(image) vs /etc/openwisp/firmware_checksum (20, equal: "upgrade not needed")
 -> free memory if needed (stop uhttpd, dnsmasq, openwisp-config; wifi down) -> upload to /tmp
 -> /sbin/sysupgrade --test <path> -> /sbin/sysupgrade -v <flags> <path> (65)
 -> sleep reconnect_delay (180 s) -> reconnect up to 35 x 20 s, write checksum (90) -> 100
```

| Option | Meaning                                                      | Default |
| ------ | ------------------------------------------------------------ | ------- |
| `c`    | Preserve all changed files in `/etc/`                        | `True`  |
| `o`    | Preserve changed files in `/` except package files           | off     |
| `n`    | Do not save configuration over reflash (not with `o` or `c`) | off     |
| `u`    | Skip backup of files equal to `/rom`                         | off     |
| `p`    | Do not restore the partition table                           | off     |
| `k`    | Save the installed package list                              | off     |
| `F`    | Flash even if image checks fail ("dangerous")                | off     |

```python
OPENWISP_FIRMWARE_UPGRADER_OPENWRT_SETTINGS = {"reconnect_delay": 180, "reconnect_retry_delay": 20,
                                               "reconnect_max_retries": 35, "upgrade_timeout": 90}
```

- Queue: docker routes `openwisp_firmware_upgrader.tasks.upgrade_firmware` and `batch_upgrade_operation` to `firmware_upgrader` when both `USE_OPENWISP_FIRMWARE` and `USE_OPENWISP_CELERY_FIRMWARE` are
  true; the worker is started detached in the `celery` container with `OPENWISP_CELERY_FIRMWARE_COMMAND_FLAGS`.
- `upgrade_firmware` retries on `RecoverableFailure` (`max_retries=4`, backoff 60-600 s) and fails at `OPENWISP_FIRMWARE_UPGRADER_TASK_TIMEOUT` (1500 s).
- Cancel is accepted only below 65 % (`CANCELLATION_THRESHOLD = REFLASHING`); after that the API answers 409.

Gotcha: there is no automatic rollback to the previous image. Once sysupgrade runs, recovery is the device's own (dual-bank or failsafe) behaviour, so canary one device per board before any batch.

Source: `$P/openwisp_firmware_upgrader/upgraders/openwrt.py:23-90` (constants, schema), `:110-128` (option rules), `:163-245`, `:331-353`, `:378-440`; `$P/openwisp_firmware_upgrader/utils.py:46-54`;
`$P/openwisp_firmware_upgrader/tasks.py:18-44`; `$P/openwisp_firmware_upgrader/settings.py:9-29`; `/opt/openwisp/celery.py`, `/opt/openwisp/init_command.sh`.

## 9. Closed firmware

Decision: for non-OpenWrt devices, treat connections and firmware upgrades as unavailable until a custom connector, update strategy and upgrader exist.

- `OPENWISP_FIRMWARE_UPGRADERS_MAP` maps an update strategy to an upgrader class; only the OpenWrt and OpenWISP 1.x upgraders ship. The 26.09 docs describe writing a custom upgrader class.
- The OpenWrt upgrader reads `uci get openwisp.http.uuid`, `/sbin/sysupgrade` and `ubus`; none exist on closed firmware, so an attempt aborts at the identity check.
- The custom command type runs a shell string; on a device whose SSH lands in a vendor CLI rather than a shell, its behaviour is UNVERIFIED.

Gotcha: an SNMP Credentials object proves only that a connector exists. In the installed monitoring (`openwisp_monitoring/check/classes/`: ping, config_applied, data_collected, iperf3, wifi_clients)
no check consumes it.

Source: `$P/openwisp_firmware_upgrader/settings.py:9-13`; `$P/openwisp_firmware_upgrader/upgraders/openwrt.py:163-198`;
https://openwisp.io/docs/26.09/firmware-upgrader/user/custom-firmware-upgrader.html.

> **Learned 2026-10-05** · OpenWISP controller 1.3 (images 26.09.0) · VERIFIED_PRIMARY · Source: django.urls.resolve in the 26.09.0 dashboard: /api/v1/controller/credential/ resolves, /api/v1/connection/credential/ is 404 · Falsifier: a 26.09.x image where the connection-prefixed path resolves
> The credential REST endpoint is `/api/v1/controller/credential/` in the 26.09.0 images; the 26.09 REST docs give `/api/v1/connection/credential/`, which returns 404. Resolve paths against the installed URLconf before trusting the docs.
