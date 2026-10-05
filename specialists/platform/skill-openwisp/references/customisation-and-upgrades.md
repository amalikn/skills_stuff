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

## Extending models upgrade-safely

Verified against: OpenWISP images 26.09.0 (openwisp-controller 1.3, swapper 1.4.0), checked 2026-10-05. Runtime check: `CONFIG_DEVICE_MODEL` resolves to `config.Device` and `EXTENDED_APPS` is
`['django_x509', 'django_loci']`, so this install swaps no model.

Decision: add a field to Device, Config or another controller model only through swapper, never by patching the installed package; prefer cheaper seams first.

| Need                                 | Cheaper seam first                                                              | Swap a model when                                     |
| ------------------------------------ | ------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Per-group data for integrations      | `DeviceGroup.meta_data`, validated by `OPENWISP_CONTROLLER_DEVICE_GROUP_SCHEMA` | The data is per device and must be queryable          |
| Per-device values used in configs    | `Config.context` variables                                                      | The value needs its own column, index or admin filter |
| Observations over time               | Custom metric and chart (settings or `register_metric`)                         | Never: time series do not belong in model columns     |
| Inventory facts another system owns  | Keep them in that system and join by ID                                         | OpenWISP must enforce or display them itself          |

Swapper names each swappable model's setting `<APP_LABEL>_<MODEL>_MODEL`, e.g. `CONFIG_DEVICE_MODEL`, `CONFIG_CONFIG_MODEL`, `GEO_LOCATION_MODEL`, `CONNECTION_CREDENTIALS_MODEL`,
`DJANGO_X509_CERT_MODEL`. The 26.09 controller guide swaps every model of an app at once:

```python
# sample_config/models.py: subclass the installed abstract bases, one class per config model
from django.db import models
from openwisp_controller.config.base.device import AbstractDevice

class Device(AbstractDevice):
    details = models.CharField(max_length=64, blank=True, null=True)

    class Meta(AbstractDevice.Meta):
        abstract = False
```

```python
# settings.py
INSTALLED_APPS = [..., "mycontroller.sample_config", ...]          # replaces "openwisp_controller.config"
EXTENDED_APPS = ("django_x509", "django_loci", "openwisp_controller.config")
CONFIG_DEVICE_MODEL = "sample_config.Device"
CONFIG_CONFIG_MODEL = "sample_config.Config"
# ...one line per model the guide lists (DeviceGroup, Template, TemplateTag, TaggedTemplate, Vpn, VpnClient, ...)
```

```sh
./manage.py makemigrations    # your app now owns the migrations of every swapped model
./manage.py migrate
```

The guide also requires an `AppConfig` subclass, admin re-registration (monkey patching, or `admin.site.unregister` then subclass), default group-permission migrations, URL and API view wiring,
and the upstream tests imported into the app. Code must load models with `swapper.load_model("config", "Device")`, never import `openwisp_controller.config.models` directly.

Upgrade cost: once swapped, upstream migrations for those models no longer run against your tables. Every release that changes an abstract base needs `makemigrations` in your app, a review of the
generated migration against upstream's, and a re-run of the imported tests (inference from migration ownership; rehearse it). The guide warns that adopting a custom module after data exists "may
be time consuming", so decide before production data accumulates. In docker-openwisp the app ships through the settings mount or a rebuilt image (`.build.env`).

Gotcha: a half-swapped `config` app leaves foreign keys pointing at stock models, so swap the whole app. Record the base tag, the swapped models and a retirement condition in the upgrade register, as
for any core patch.

Source: site-packages `openwisp_controller/config/models.py:1-35` and `swapper/__init__.py:9-21` in the dashboard image; runtime `django.conf.settings` read in the dashboard container (2026-10-05);
https://openwisp.io/docs/26.09/controller/developer/extending.html (snapshot `documents/openwisp-26.09-controller-developer-extending.html`), steps 3, 4, 11-14.
