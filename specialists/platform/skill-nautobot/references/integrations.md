---
Title: Nautobot integrations
Category: skill-reference
Status: current
Authority: >-
  Installed Nautobot 3.2.3 and app source (pynautobot 3.2.0, nautobot_golden_config 3.0.7, nautobot_plugin_nornir 3.2.4, nornir-nautobot 4.4.2) and tagged
  upstream source for components not installed (diffsync 2.2.3, nautobot-app-ssot 4.7.0, nautobot-ansible 6.3.0); the cited lines win over this summary
Scope: >-
  pynautobot client patterns, SSoT/DiffSync reconciliation, Git repositories as data sources, export templates and Jinja filters, the Ansible collection's
  inventory plugins and modules, the Nornir inventory, and Golden Config settings, compliance and remediation
Last reviewed: 2026-10-05
Summary: Nine verified integration recipes for Nautobot 3.2.3, each with a gotcha and a source line; SSoT, DiffSync and the Ansible collection are checked against tagged source because they are not
installed.
---

# Nautobot integrations

Verified against: Nautobot 3.2.3 and the apps installed in a 3.2.3 container, plus tagged GitHub source for components not installed, checked 2026-10-05.

Installed in the inspected image: `pynautobot` 3.2.0, `nautobot_golden_config` 3.0.7, `nautobot_plugin_nornir` 3.2.4, `nornir-nautobot` 4.4.2, `nornir` 3.6.0, `netutils` 1.18.0. **Not installed:**
`nautobot_ssot`, `diffsync`, the `networktocode.nautobot` Ansible collection, Device Lifecycle Management. For those, sources are the release tags `networktocode/diffsync@v2.2.3`,
`nautobot/nautobot-app-ssot@v4.7.0` (requires `nautobot >=3.1.0,<4.0.0`) and `nautobot/nautobot-ansible@v6.3.0` (requires `ansible >=2.17.0`, `pynautobot >=3.0.0`); paths below for those are
repository-relative at that tag. In `curl` examples `${H[@]}` is the token and version header array from the operations cookbook, section 2.

## Summary

| Job                      | Use                          | Key syntax                                 | Trap                                    | Section |
| ------------------------ | ---------------------------- | ------------------------------------------ | --------------------------------------- | ------- |
| Script reads and writes  | pynautobot                   | `nb.dcim.devices.filter(...)`              | `filter()` loads every page into a list | [1](#1-pynautobot) |
| Bulk write               | pynautobot                   | `create([...])`, `update([...])`           | `retries` also retries POST             | [1](#1-pynautobot) |
| Reconcile another source | SSoT + DiffSync              | `diff_to()`, `sync_to()`                   | unmatched target rows are deleted       | [2](#2-ssot-and-diffsync-reconciliation) |
| Config data in Git       | GitRepository                | `provided_contents`, `/sync/`              | sync runs repo code on the worker       | [3](#3-git-repositories-as-data-sources) |
| Render an object list    | Export template              | `{% for o in queryset %}`                  | custom field is `obj.cf.<key>`          | [4](#4-export-templates-and-jinja-filters) |
| Ansible inventory        | `inventory`, `gql_inventory` | `plugin: networktocode.nautobot.inventory` | `query_filters` are OR, not AND         | [5](#5-ansible-collection) |
| Nornir inventory         | `NautobotInventory`          | `filter_parameters={...}`                  | hosts keyed by name; duplicates collide | [6](#6-nornir-inventory) |
| Intended and compliance  | Golden Config settings       | SoTAgg query `query ($device_id: ID!)`     | highest-weight setting wins per device  | [7](#7-golden-config-settings-and-sotagg) |
| Compliance rules         | ComplianceRule, Remediation  | `match_config`, `config_type`              | parser comes from `network_driver`      | [8](#8-golden-config-compliance-and-remediation) |

## Contents

- [Summary](#summary)
- [1. pynautobot](#1-pynautobot)
- [2. SSoT and DiffSync reconciliation](#2-ssot-and-diffsync-reconciliation)
- [3. Git repositories as data sources](#3-git-repositories-as-data-sources)
- [4. Export templates and Jinja filters](#4-export-templates-and-jinja-filters)
- [5. Ansible collection](#5-ansible-collection)
- [6. Nornir inventory](#6-nornir-inventory)
- [7. Golden Config settings and SoTAgg](#7-golden-config-settings-and-sotagg)
- [8. Golden Config compliance and remediation](#8-golden-config-compliance-and-remediation)

## 1. pynautobot

Decision: use pynautobot for scripts outside Nautobot; inside Nautobot (Jobs, apps) use the ORM. Read with `filter`/`get`/`count`, write in bulk with a list.

```python
import os
import pynautobot
from pynautobot.core.query import RequestError

nb = pynautobot.api("https://nautobot.example", token=os.environ["NAUTOBOT_TOKEN"],
                    api_version="3.2", threading=True, max_workers=4, retries=3, exclude_m2m=True)
nb.http_session.verify = "/etc/ssl/certs/ca.pem"          # or a custom requests.Session

devs = nb.dcim.devices.filter(location=["site-a", "site-b"], status="Active")   # list, all pages fetched
one = nb.dcim.devices.get(name="sw1", location="site-a")   # None if absent; ValueError if more than one
n = nb.dcim.devices.count(role="Access Switch")            # one request with limit=1
page = nb.dcim.devices.filter(limit=100, offset=200)       # exactly one page when offset is given

created = nb.ipam.vlans.create([{"vid": 30, "name": "wifi", "status": "Active", "vlan_group": "<uuid>"}])
nb.dcim.devices.update([{"id": "<uuid1>", "serial": "A1"}, {"id": "<uuid2>", "serial": "A2"}])  # one PATCH
dev = nb.dcim.devices.get("<uuid>"); dev.serial = "A3"; dev.save()   # PATCHes only changed fields
nb.dcim.devices.delete(["<uuid1>", "<uuid2>"])                        # one bulk DELETE
try:
    nb.dcim.devices.create(name="x")
except RequestError as e:
    print(e.req.status_code, e.error)        # e.error is the response body text
```

| Behaviour (3.2.0)                                                                                                                                | Source                                            |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| `filter()`/`all()` follow `next` until done and return a list; with `limit` and no `offset` they still fetch every page (`limit` sets page size) | `core/query.py:318-350`                           |
| `threading=True` fetches remaining pages concurrently by offset; results arrive in completion order                                              | `core/query.py:306-316,352-368`                   |
| `retries=N` mounts `urllib3.Retry(total=N, backoff_factor=1, allowed_methods=None, status_forcelist=[429,500,502,503,504])`                      | `core/api.py:106-116`                             |
| `get(<id>)` returns None on 404; other HTTP errors raise `RequestError`; non-JSON raises `ContentError`                                          | `core/endpoint.py:108-171`,                       |
|                                                                                                                                                  |   `core/query.py:33-70,268-304`                   |
| `pk` is a reserved filter kwarg (`ValueError`); use `id`                                                                                         | `core/query.py:25`, `core/endpoint.py:214`        |
| `max_workers` defaults to 4 (the docstring's "number of CPU cores" is wrong)                                                                     | `core/api.py:84-93`                               |

Gotcha: `allowed_methods=None` makes retries apply to POST too, so a timed-out create can be sent twice; make writers idempotent (look up before create). Threaded results are unordered, so sort before
diffing. Pin `api_version` so a server upgrade cannot change payload shapes under the script.

Source: `pynautobot/core/api.py`, `core/endpoint.py:85-560`, `core/query.py`, `core/response.py:432-466` (pynautobot 3.2.0 in the container).

## 2. SSoT and DiffSync reconciliation

Decision: for a recurring sync between Nautobot and another system, build a `nautobot_ssot` DataSource or DataTarget Job from DiffSync models and two adapters; the Job gives dry run, diff storage,
sync logs and scheduling. **`nautobot_ssot` and `diffsync` are not installed in the inspected deployment.**

```python
from typing import Optional
from diffsync import Adapter
from nautobot.apps.jobs import register_jobs
from nautobot.extras.jobs import Job
from nautobot.ipam.models import VLAN
from nautobot_ssot.contrib import NautobotAdapter, NautobotModel
from nautobot_ssot.jobs import DataSource

class VLANModel(NautobotModel):
    _model = VLAN
    _modelname = "vlan"
    _identifiers = ("vid", "vlan_group__name")      # fields that match a row on both sides
    _attributes = ("name", "description")           # fields compared and synced
    vid: int
    vlan_group__name: Optional[str] = None
    name: str
    description: Optional[str] = None

    @classmethod
    def get_queryset(cls):                         # scope what Nautobot loads, so out-of-scope rows are not deleted
        return VLAN.objects.filter(vlan_group__name="site-a")

class NautobotSide(NautobotAdapter):
    vlan = VLANModel
    top_level = ("vlan",)

class RemoteSide(Adapter):
    vlan = VLANModel
    top_level = ("vlan",)
    def __init__(self, *args, client, job=None, **kwargs):
        super().__init__(*args, **kwargs); self.client = client; self.job = job
    def load(self):
        for row in self.client.vlans():
            self.add(self.vlan(vid=row["id"], vlan_group__name="site-a", name=row["name"], description=""))

class RemoteVLANs(DataSource, Job):
    class Meta:
        name = "Remote VLANs to Nautobot"
    def load_source_adapter(self):
        self.source_adapter = RemoteSide(client=make_client(), job=self); self.source_adapter.load()
    def load_target_adapter(self):
        self.target_adapter = NautobotSide(job=self); self.target_adapter.load()

register_jobs(RemoteVLANs)
```

| Control                                                                        | Meaning                                                                            |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| `dryrun` Job input (`DryRunVar`)                                               | loads both adapters and stores the diff; skips `execute_sync()`                    |
| `self.diffsync_flags` (default `CONTINUE_ON_FAILURE \| LOG_UNCHANGED_RECORDS`) | passed to `diff_to()` and `sync_to()`                                              |
| `DiffSyncFlags.SKIP_UNMATCHED_DST`                                             | never delete target rows missing from the source (an "add and update only" policy) |
| `DiffSyncFlags.SKIP_UNMATCHED_SRC`                                             | never create target rows that exist only in the source                             |
| `DiffSyncModelFlags.IGNORE` on a model                                         | neither diffed nor changed                                                         |
| `SKIP_CHILDREN_ON_DELETE`, `NATURAL_DELETION_ORDER`                            | model flags for parent/child deletion                                              |

Gotcha: with default flags, a row in the target that the source lacks is deleted; scope `get_queryset()` or set `SKIP_UNMATCHED_DST` before the first real run, and run dry first. The upstream example
omits `register_jobs()`, which Nautobot 2+ requires. Do not override `run()` unless adding Job variables; then pass `*args, **kwargs` through.

Source: `diffsync/enum.py:20-105`, `diffsync/__init__.py:60-150,430-440,563-700`; `nautobot_ssot/jobs/base.py:134-215,515-536,630-640,702-730`, `nautobot_ssot/contrib/model.py:36-66`,
`docs/dev/jobs.md:20-95,166`, `docs/user/modeling.md:172-195` (tags above).

## 3. Git repositories as data sources

Decision: keep config contexts, schemas, export templates and Jobs in Git when they need review and history; Nautobot clones the repository under `GIT_ROOT` and imports what `provided_contents` lists.

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/extras/git-repositories/ \
  -d '{"name": "nautobot-data", "slug": "nautobot_data", "remote_url": "https://git.example/net/nautobot-data.git", "branch": "main",
       "secrets_group": "<uuid>", "provided_contents": ["extras.configcontext", "extras.configcontextschema", "extras.exporttemplate", "extras.job"]}'
curl -s -X POST "${H[@]}" https://nautobot.example/api/extras/git-repositories/<uuid>/sync/
```

| Content                        | Layout in the repository                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------------------------- |
| Config contexts, explicit      | `config_contexts/*.yaml` with a `_metadata` key (`name`, `weight`, `is_active`, scope lists)      |
| Config contexts, implicit      | `config_contexts/<filter>/<object name>.yaml`, e.g. `config_contexts/locations/site-a.yaml`       |
| Local context per device or VM | `config_contexts/devices/<device name>.yaml`, `config_contexts/virtual_machines/<name>.json`      |
| Config context schemas         | `config_context_schemas/*.yaml`                                                                   |
| Export templates               | `export_templates/<app_label>/<model>/<file>`, named `<repo name>: <file>`                        |
| Jobs                           | `jobs/__init__.py` plus modules, or `jobs.py` at the root                                         |
| Golden Config                  | `nautobot_golden_config.backupconfigs`, `.intendedconfigs`, `.jinjatemplate`, `.pluginproperties` |

Gotcha: syncing imports Job code on the worker, so `extras.add_gitrepository`/`change_gitrepository` amount to code execution; sync needs those permissions, not `run_job`. Private repositories need a
Secrets Group with access type HTTP(S) and secret type Token (and Username where the host needs it). Device-local contexts from Git fail for device names that are not globally unique. A new repository
does not sync until `/sync/` is called.

Source: `nautobot/extras/api/views.py:695-700`, `nautobot_golden_config/datasources.py:238-280`; `docs/user-guide/platform-functionality/gitrepository.html`.

## 4. Export templates and Jinja filters

Decision: an export template renders a filtered object list to any text format; use it for files other systems read (DNS zones, monitoring hosts, CSV variants). In 3.x the list export runs as the
system Job "Export Object List".

```jinja
{# content type dcim.device, mime_type text/plain, file_extension cfg #}
{% for d in queryset %}{% if d.primary_ip4 %}
host {{ d.name }} address {{ d.primary_ip4.address.ip }} owner {{ d.cf.owner_team | default("none") }} site {{ d.location.name | slugify }}
{% endif %}{% endfor %}
```

Filters available in Nautobot-rendered Jinja (export templates, computed fields, custom links, Golden Config): every netutils function (for example `ipaddress_network`, `bits_to_name`,
`encrypt_type7`), and Nautobot built-ins `as_range`, `bettertitle`, `divide`, `fgcolor`, `get_item`, `humanize_speed`, `hyperlinked_object`, `meta`, `percentage`, `placeholder`, `render_json`,
`render_markdown`, `render_yaml`, `settings_or_config`, `slugify`, `split`, `tzoffset`, `viewname`, `validated_viewname`. Apps add more through `jinja_filters.py` (`@library.filter`).

Gotcha: custom fields are `obj.cf.<key>`; computed fields need `obj.get_computed_field("<key>")`. The export runs with the requesting user's object permissions on `queryset`, so a narrow token yields
a short file, not an error.

Source: `nautobot/core/jobs/__init__.py:132-166,183-192` (permission check and `restrict`), `nautobot/extras/models/models.py:397-422`; `docs/user-guide/platform-functionality/exporttemplate.html`,
`docs/user-guide/platform-functionality/template-filters.html`, `docs/development/apps/api/platform-features/jinja2-filters.html`.

## 5. Ansible collection

Decision: `networktocode.nautobot.inventory` (REST) for ordinary grouping by role, platform, location or tag; `gql_inventory` when one GraphQL query should choose the host variables. **The collection
is not installed in the inspected image; facts are from tag v6.3.0.**

```yaml
# nautobot_inventory.yml   (token comes from NAUTOBOT_TOKEN, URL may come from NAUTOBOT_URL)
plugin: networktocode.nautobot.inventory
api_endpoint: https://nautobot.example
api_version: "3.2"
validate_certs: true
config_context: false
group_by: [locations, platforms, tags]
query_filters:
  - role: access-switch
device_query_filters:
  - has_primary_ip: "true"
compose:
    ansible_network_os: platforms[0]     # host var platforms = [platform.network_driver]
```

```yaml
# gql_inventory.yml
plugin: networktocode.nautobot.gql_inventory
api_endpoint: https://nautobot.example
query:
  devices:
    location: name
    platform: [name, network_driver]
    tags: name
group_by: [location.name]
```

Key options, `inventory`: `api_endpoint`, `api_version`, `validate_certs`, `config_context`, `flatten_config_context`, `flatten_custom_fields`, `computed_fields`, `interfaces`, `services`, `group_by`,
`group_names_raw`, `query_filters`, `device_query_filters`, `vm_query_filters`, `compose`, `timeout` (60), `max_uri_length` (4000), `fetch_all` (true). `gql_inventory`: `query`, `group_by`,
`page_size` (0), `default_ip_version` (IPv4), `saved_query`. Lookups: `query('networktocode.nautobot.lookup', 'devices', api_endpoint=..., api_filter='role=leaf')` and `lookup_graphql`. Modules (104)
follow the object names: `device`, `device_interface`, `ip_address`, `ip_address_to_interface`, `prefix`, `vlan`, `location`, `cable`, `platform`, `tag`, `custom_field`, `dynamic_group`,
`secrets_group`, `query_graphql`, each with `state: present|absent`.

Gotcha: `query_filters` entries are ORed (the plugin's own example says so), and the same filter repeated means OR within that filter on the REST side. `gql_inventory` sets `ansible_network_os` from
`platform.napalm_driver` mapped through netutils, not from `network_driver`, and logs an error if the query lacks `napalm_driver`. The `inventory` plugin sets `ansible_host` from the primary IP and
a `platforms` host variable holding the platform's `network_driver` (`platform` with `plurals: false`), but no `ansible_network_os`; compose it as above.

Source: `nautobot-ansible` v6.3.0 `plugins/inventory/inventory.py` (DOCUMENTATION and EXAMPLES, `:362`, `:483-510`, `:586-588`, `:830-833`, `:1405-1435`), `plugins/inventory/gql_inventory.py`
(`:149`, `:300-356`),
`plugins/lookup/lookup.py`, `plugins/modules/device.py:255-270`, `galaxy.yml:12`, `meta/runtime.yml:2`, `requirements.txt:3`.

## 6. Nornir inventory

Decision: outside Nautobot, use `nornir-nautobot`'s `NautobotInventory`; inside Nautobot, `nautobot_plugin_nornir` builds the inventory from the ORM and supplies credentials (Golden Config uses it).

```python
from nornir import InitNornir
nr = InitNornir(inventory={"plugin": "NautobotInventory", "options": {
    "nautobot_url": "https://nautobot.example", "nautobot_token": None,     # None: read NAUTOBOT_URL / NAUTOBOT_TOKEN
    "ssl_verify": True, "filter_parameters": {"location": "site-a", "status": "Active"}, "enable_threading": True}})
```

Host mapping: `hostname` is the primary IPv4 (then IPv6, then the device name); `platform` is `platform.network_driver`; `data["pynautobot_object"]` is the pynautobot record and
`data["pynautobot_dictionary"]` its dict.

```python
# nautobot_config.py, in-app Nornir credentials (three classes ship with 3.2.4)
PLUGINS_CONFIG["nautobot_plugin_nornir"] = {"nornir_settings": {
    "credentials": "nautobot_plugin_nornir.plugins.credentials.nautobot_secrets.CredentialsNautobotSecrets",
    "runner": {"plugin": "threaded", "options": {"num_workers": 10}}}}
# alternatives: ...credentials.env_vars.CredentialsEnvVars (NAPALM_USERNAME, NAPALM_PASSWORD, DEVICE_SECRET)
#               ...credentials.settings_vars.CredentialsSettingsVars
```

Gotcha: hosts are keyed by device name, so two devices with the same name at different Locations overwrite each other silently; filter to one Location or make names unique.
`CredentialsNautobotSecrets` reads the device's Secrets Group with access type Generic unless `use_config_context.secrets` selects another type per device.

Source: `nornir_nautobot/plugins/inventory/nautobot.py:20-185`, `nornir_nautobot-4.4.2.dist-info/entry_points.txt`; `nautobot_plugin_nornir/plugins/credentials/env_vars.py:7-33`,
`nautobot_secrets.py:35-61,62-160`, `settings_vars.py:8`.

## 7. Golden Config settings and SoTAgg

Decision: one Golden Config Setting per device population (a Dynamic Group), pointing at the backup, intended and Jinja repositories and at a saved GraphQL query (SoTAgg) whose result is the template
context.

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/plugins/golden-config/golden-config-settings/ \
  -d '{"name": "default", "slug": "default", "weight": 1000, "dynamic_group": "<group-uuid>", "sot_agg_query": "<graphql-query-uuid>",
       "jinja_repository": "<repo-uuid>", "jinja_path_template": "{{obj.platform.network_driver}}.j2",
       "intended_repository": "<repo-uuid>", "intended_path_template": "{{obj.location.name|slugify}}/{{obj.name}}.cfg",
       "backup_repository": "<repo-uuid>", "backup_path_template": "{{obj.location.name|slugify}}/{{obj.name}}.cfg",
       "backup_test_connectivity": false}'
curl -s "${H[@]}" https://nautobot.example/api/plugins/golden-config/sotagg/<device-uuid>/    # the context a template sees
```

```graphql
query ($device_id: ID!) {
  device(id: $device_id) { name platform { network_driver } location { name } config_context
    interfaces { name mode untagged_vlan { vid } tagged_vlans { vid } ip_addresses { address } } }
}
```

App settings (`PLUGINS_CONFIG["nautobot_golden_config"]`, defaults): `enable_backup` True, `enable_compliance` True, `enable_intended` True, `enable_sotagg` True, `enable_plan` True, `enable_deploy`
True, `enable_postprocessing` False, `default_deploy_status` "Not Approved", `jinja_env` `{"undefined": "jinja2.StrictUndefined", "trim_blocks": True, "lstrip_blocks": False}`, optional
`sot_agg_transposer` (dotted path to a function that reshapes the data). Constance: `DEFAULT_FRAMEWORK` `{"all": "napalm"}`, `GET_CONFIG_FRAMEWORK`, `MERGE_CONFIG_FRAMEWORK`. Jobs: "Backup
Configurations", "Generate Intended Configurations", "Perform Configuration Compliance", "Generate Config Plans", "Deploy Config Plans", "Sync GoldenConfig Table".

Gotcha: the saved query must start with exactly `query ($device_id: ID!)`; the template receives `data["device"]`, so top-level names are the device's fields (`name`, `interfaces`), not `device.name`.
A device in several settings' groups gets the highest `weight`. Repositories appear only if their `provided_contents` include the matching Golden Config content type.

Source: `nautobot_golden_config/__init__.py:21-60`, `models.py:28,555-663`, `utilities/graphql.py:15-50`, `utilities/helper.py:176-193`, `api/urls.py:1-40`, `jobs.py:243-638`.

## 8. Golden Config compliance and remediation

Decision: a Compliance Feature names a config area; a Compliance Rule per Platform says which lines belong to it; Golden Config then stores, per device and rule, `actual`, `intended`, `missing`,
`extra` and `compliance`.

```json
POST /api/plugins/golden-config/compliance-feature/  {"name": "ntp", "slug": "ntp"}
POST /api/plugins/golden-config/compliance-rule/
{"feature": "<uuid>", "platform": "<uuid>", "config_type": "cli", "match_config": "ntp server\nclock timezone", "config_ordered": false,
 "config_remediation": true}
POST /api/plugins/golden-config/remediation-setting/  {"platform": "<uuid>", "remediation_type": "hierconfig", "remediation_options": {}}
POST /api/plugins/golden-config/config-remove/   {"name": "drop banner", "platform": "<uuid>", "regex": "^banner .*"}
POST /api/plugins/golden-config/config-replace/  {"name": "mask keys", "platform": "<uuid>", "regex": "key \\S+", "replace": "key <removed>"}
```

`config_type`: `cli`, `json`, `xml`; `custom_compliance` hands the comparison to the function named by `get_custom_compliance`. `remediation_type`: `hierconfig` or `custom_remediation`; one
Remediation Setting per Platform. Config Remove and Config Replace apply to backups before they are stored.

Gotcha: CLI section matching uses `platform.network_driver_mappings["netutils_parser"]` and remediation uses `["hier_config"]`; a Platform whose driver has no netutils mapping gets no parser.
`match_config` lines are line starts (section parents), not regexes.

Source: `nautobot_golden_config/models.py:60-80,195-215,270-383,694-800`, `choices.py:6-28`, `nornir_plays/config_backup.py:109-120`; `netutils.config.compliance.section_config` (netutils 1.18.0,
top-level `startswith` match); `nautobot/dcim/models/devices.py:462-466`.

> **Learned 2026-10-05** · pynautobot 3.2.0 · VERIFIED_PRIMARY · Source: pynautobot/core/api.py line 111 sets the retry adapter with allowed_methods=None · Falsifier: a pynautobot release whose retries exclude POST
> pynautobot `retries` retry every method, POST included (`allowed_methods=None`), so a create that timed out after reaching the server can be sent twice. Make creates idempotent (look up first, or use a unique natural key) before enabling retries.

> **Learned 2026-10-05** · nornir-nautobot 4.4.2 · VERIFIED_PRIMARY · Source: nornir_nautobot/plugins/inventory/nautobot.py line 176 keys hosts by device.name or the id · Falsifier: a nornir-nautobot release that keys hosts by id or by name plus location
> The Nornir inventory keys hosts by device name, so two devices with the same name at different Locations overwrite each other without warning; the default device uniqueness rule allows that. Keep names unique estate-wide (a site prefix) or filter the inventory per Location.
