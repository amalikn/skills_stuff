---
Title: Nautobot operations cookbook
Category: skill-reference
Status: current
Authority: Installed Nautobot 3.2.3 source and version-matched official documentation; the cited lines win over this summary
Scope: Exact, version-matched syntax for Nautobot GraphQL, REST, Dynamic Groups, computed and custom fields, Config Contexts, Secrets, webhooks and events, approvals, data validation, permissions and change log, nautobot-server, Jobs and Circuits
Last reviewed: 2026-10-05
Summary: Twelve verified recipes with a gotcha and a source line each, cited to the installed 3.2.3 source and its bundled docs; re-verify on any version change.
---

# Operations cookbook

Verified against: Nautobot 3.2.3 (installed source and v3.2 docs), checked 2026-10-05.

Source paths below are relative to the installed package root (`site-packages/`), read in a 3.2.3 container. Doc citations name the local snapshot in [documents/](../documents/readme.md), which
records each page's archive URL (`https://archive.docs.nautobot.com/projects/core/en/v3.2.3/...`) and checksum. Placeholders: `https://nautobot.example`, `$NAUTOBOT_TOKEN`, `<uuid>`. Re-verify line
numbers after any upgrade.

## Summary

| Job                             | Use                               | Key syntax                                             | Trap                                                        | Section |
| ------------------------------- | --------------------------------- | ------------------------------------------------------ | ----------------------------------------------------------- | ------- |
| Read across related models      | GraphQL (read-only)               | `POST /api/graphql/`, `cf_`/`rel_`/`cpf_` fields       | No `count`/`next`; unordered offsets skip or repeat rows    | [1](#1-graphql) |
| Write, or page a set to act on  | REST                              | `Authorization: Token`, `?sort=`, follow `next`        | `STRICT_FILTERING`: unknown filter is 400, not "none found" | [2](#2-rest-api) |
| Reusable member set             | Dynamic Group (filter, set        | `/api/extras/dynamic-groups/`, `/members/`             | Member cache is stale until refreshed                       | [3](#3-dynamic-groups-and-saved-views) |
|                                 |   or static)                      |                                                        |                                                             |         |
| Derived value or                | Computed field / custom field     | `?include=computed_fields`; `multi-select` value is    | A broken template silently shows `fallback_value`           | [4](#4-computed-fields-custom-fields-config-contexts) |
|   extra attribute               |                                   |   a list                                               |                                                             |         |
| Scoped structured data          | Config Context (+ schema)         | weight wins; dicts merge                               | Lists are replaced, not appended                            | [4](#4-computed-fields-custom-fields-config-contexts) |
| Credentials for Jobs or devices | Secrets Group                     | `get_secret_value(access_type, secret_type, obj)`      | Secret editors can read any env var or file                 | [5](#5-secrets-and-secrets-groups) |
| Tell another system of a change | Webhook, Job Hook or event broker | `snapshots`/`prechange` carry the deleted object       | `nbshell` and non-logged writes fire nothing                | [6](#6-webhooks-job-hooks-job-buttons-event-brokers) |
| Hold a change for sign-off      | Approval workflow (core in 3.x)   | definitions by model + constraints + weight;           | No matching definition: nothing starts, nothing errors      | [7](#7-approval-workflows) |
|                                 |                                   |   stages approve                                       |                                                             |         |
| Field rules and audits          | Data Validation / Compliance      | `/api/data-validation/regex-rules/` etc.               | Old records fail only on their next save; audit first       | [8](#8-data-validation-and-data-compliance) |
|                                 |   (core in 3.x)                   |                                                        |                                                             |         |
| Who may do what                 | ObjectPermission with constraints | keys AND, list items OR, permissions OR                | —                                                           | [9](#9-permissions-tokens-statuses-roles-change-log) |
| Undo a deletion                 | Change log (`ObjectChange`)       | `?action=delete&changed_object_type=...`; recreate     | Built-in Statuses/Roles are not recreated by `post_upgrade` | [9](#9-permissions-tokens-statuses-roles-change-log) |
|                                 |                                   |   with old `id`                                        |                                                             |         |
| After an image change           | `nautobot-server post_upgrade`    | then `validate_models`, `health_check`                 | `invalidate` is gone; `clear_cache` replaces it             | [10](#10-nautobot-server-operations-commands) |
| Run automation                  | Job                               | `POST /api/extras/jobs/<id>/run/`; `job_kwargs`        | 201 is queued, not done; no worker on the queue = `PENDING` | [11](#11-jobs) |
|                                 |                                   |   from 3.2                                             |                                                             |         |
| WAN uplink                      | Circuit + Circuit Termination     | `term_side` A at the Location; speeds in Kbps          | Termination needs exactly one of location /                 | [12](#12-circuits-for-wan-uplinks) |
|                                 |                                   |                                                        |   provider network                                          |         |

## Contents

- [Summary](#summary)
- [1. GraphQL](#1-graphql)
- [2. REST API](#2-rest-api)
- [3. Dynamic Groups and Saved Views](#3-dynamic-groups-and-saved-views)
- [4. Computed fields, custom fields, Config Contexts](#4-computed-fields-custom-fields-config-contexts)
- [5. Secrets and Secrets Groups](#5-secrets-and-secrets-groups)
- [6. Webhooks, Job Hooks, Job Buttons, event brokers](#6-webhooks-job-hooks-job-buttons-event-brokers)
- [7. Approval workflows](#7-approval-workflows)
- [8. Data Validation and Data Compliance](#8-data-validation-and-data-compliance)
- [9. Permissions, tokens, Statuses, Roles, change log](#9-permissions-tokens-statuses-roles-change-log)
- [10. nautobot-server operations commands](#10-nautobot-server-operations-commands)
- [11. Jobs](#11-jobs)
- [12. Circuits for WAN uplinks](#12-circuits-for-wan-uplinks)

## 1. GraphQL

Decision: use GraphQL for one read that spans several related models; use REST for writes, paging large sets with `next`, and anything needing ordering. GraphQL is read-only.

```bash
curl -s -X POST https://nautobot.example/api/graphql/ \
  -H "Authorization: Token $NAUTOBOT_TOKEN" -H "Content-Type: application/json" \
  -d '{"query": "query ($loc: [String]) { devices(location: $loc, limit: 50, offset: 0) { name status { name } primary_ip4 { address } cf_my_field } }",
       "variables": {"loc": ["site-a"]}}'
```

```python
import pynautobot
nb = pynautobot.api("https://nautobot.example", token=TOKEN)
rec = nb.graphql.query(query="query { locations(name: \"site-a\") { name devices { name } } }")
print(rec.json["data"])
```

- Endpoints: `/api/graphql/` (token auth, JSON `{"query", "variables"}`) and `/graphql/` (GraphiQL UI).
- List fields take the model's filterset filters plus `limit` and `offset`; an invalid filter raises a GraphQL error naming it.
- Custom fields appear as `cf_<key>` (or all in `custom_field_data`), relationships as `rel_<key>`, computed fields as `cpf_<key>`.
- Saved queries: `POST /api/extras/graphql-queries/<uuid>/run/` with variables as the JSON body.

Gotcha: `limit`/`offset` slice the queryset with no ordering guarantee and return no `count` or `next`, so offset paging over a changing set can skip or repeat rows. New `cf_`/`rel_`/`cpf_` fields
appear only after the web service restarts. Objects the token cannot view come back as `null` or are left out, with no error.

Source: `nautobot/core/api/urls.py:65`, `nautobot/core/urls.py:63`, `nautobot/core/graphql/generators.py:376-377,434-472`; `pynautobot/core/graphql.py:61-63` (pynautobot 3.2.0 in the container);
`nautobot-core-3.2.3-graphql.html`.

## 2. REST API

Decision: REST is the write path and the only paged read with `count`/`next`. Always send an explicit `sort` for paged reads you plan writes from.

```bash
H=(-H "Authorization: Token $NAUTOBOT_TOKEN" -H "Accept: application/json; version=3.2")
curl -s "${H[@]}" "https://nautobot.example/api/dcim/devices/?location=site-a&location=site-b&name__ic=ap&status__n=Decommissioning&sort=name&limit=200&depth=0"
curl -s "${H[@]}" "https://nautobot.example/api/dcim/devices/<uuid>/?include=config_context&include=computed_fields&include=relationships&exclude_m2m=false"
# Bulk PATCH / DELETE on the list endpoint: a JSON list, each item carrying "id"; all-or-none.
curl -s -X PATCH "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/dcim/devices/ \
  -d '[{"id": "<uuid1>", "description": "x"}, {"id": "<uuid2>", "status": "Active"}]'
curl -s -X DELETE "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/dcim/devices/ -d '[{"id": "<uuid1>"}]'
```

| Item            | 3.2.3 behaviour                                                                                                                   |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Auth header     | `Authorization: Token <40-char key>`; tokens may carry `expires` and `write_enabled`                                              |
| API version     | `Accept: application/json; version=3.2` or `?api_version=3.2`; both given and different = 400; default is the running major.minor |
| Multiple values | repeat the parameter: OR within one filter (`?location=a&location=b`), AND for multi-valued fields such as `tag`                  |
| Lookups         | `__n` (not), `__ic`/`__nic`, `__isw`, `__iew`, `__ie`, `__re`, `__isnull`, `__gt/__gte/__lt/__lte` (by field type)                |
| Ordering        | `?sort=<field>` / `?sort=-<field>` (DRF `ORDERING_PARAM` is `sort`)                                                               |
| Paging          | `?limit=&offset=`, follow `next`; capped by `MAX_PAGE_SIZE` (default 1000); `limit=0` = all only if the cap is 0                  |
| Nesting         | `?depth=0..10`, GET only; writes always use depth 0                                                                               |
| Opt-in fields   | `?include=computed_fields`, `relationships`, `config_context` (Device and VM only)                                                |
| M2M             | excluded by default in 3.x except `tags`, `content_types`, `object_types`; `?exclude_m2m=false` brings them back                  |
| Related refs    | on write, a UUID, an API URL, or a natural-key string (`"status": "Active"`); `users.Group` takes its id or name |

Gotcha: `STRICT_FILTERING` is on by default, so an unknown filter returns 400 instead of being ignored. Not every model has a filter for every field: the custom-fields endpoint has no `key` filter, so
a lookup by `?key=` fails rather than returning nothing (seen in practice). Treat a 400 as an error, never as "not found".

Source: `nautobot/core/settings.py:375-417`, `nautobot/core/api/versioning.py` (`NautobotAPIVersioning`), `nautobot/core/api/authentication.py:10-26`, `rest_framework/authentication.py:161`,
`nautobot/core/api/constants.py:1-12`, `nautobot/core/api/serializers.py:55-120,804,932`, `nautobot/dcim/api/serializers.py:582`, `nautobot/core/api/views.py:90-175,226-241`, `nautobot/core/api/fields.py:134-145,234-237`,
`nautobot/extras/filters.py:586` (CustomField filter fields); `nautobot-core-3.2.3-rest-api-overview.html`, `-rest-api-filtering.html`, `-rest-api-authentication.html`.

## 3. Dynamic Groups and Saved Views

Decision: a Dynamic Group is a named, reusable member set (for Config Contexts, Jobs and permissions); a Saved View is only a remembered list-view layout.

```bash
# group_type: "dynamic-filter" (filter JSON), "dynamic-set" (group of groups), "static" (explicit members)
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/extras/dynamic-groups/ \
  -d '{"name": "site-a devices", "content_type": "dcim.device", "group_type": "dynamic-filter", "filter": {"location": ["site-a"]}}'
curl -s "${H[@]}" https://nautobot.example/api/extras/dynamic-groups/<uuid>/members/
# static membership is one row per object
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/extras/static-group-associations/ \
  -d '{"dynamic_group": "<group-uuid>", "associated_object_type": "dcim.device", "associated_object_id": "<device-uuid>"}'
# Saved View: owner, name, view (e.g. "dcim:device_list"), config, is_shared, is_global_default
curl -s "${H[@]}" "https://nautobot.example/api/extras/saved-views/?view=dcim:device_list"
```

Gotcha: filter and set group members are cached. Saving the group or opening its detail view refreshes the cache; changing a candidate object does not. Refresh with `nautobot-server
refresh_dynamic_group_member_caches` or the "Refresh Dynamic Group Caches" system Job, which you can schedule. Content type and group type are effectively fixed after creation. Use `nautobot-server
audit_dynamic_groups` to find groups whose filter data is invalid. Config Contexts can target Dynamic Groups only when `CONFIG_CONTEXT_DYNAMIC_GROUPS_ENABLED` is set (default False).

Source: `nautobot/extras/choices.py:200-208`, `nautobot/extras/models/groups.py:46-64,435-445,1261-1271`, `nautobot/extras/api/views.py:572-574`, `nautobot/extras/api/urls.py:37-45`,
`nautobot/extras/models/models.py:890-904` (SavedView), `nautobot/core/jobs/groups.py:8`, `nautobot/core/settings.py:92`; `nautobot-core-3.2.3-dynamic-groups.html`, `-saved-views.html`.

## 4. Computed fields, custom fields, Config Contexts

Decision: a computed field shows a value derived from data already stored (rendered on every read, never stored). A custom field stores data Nautobot does not model. A Config Context merges structured
data by scope and weight.

```json
{"key": "mgmt_label", "label": "Mgmt label", "content_type": "dcim.device",
 "template": "{{ obj.name }}_{{ obj.location.name | upper }} {{ obj.cf.my_field }}", "fallback_value": "n/a"}
```

```json
{"key": "uplink_roles", "label": "Uplink roles", "type": "multi-select", "content_types": ["dcim.device"]}
{"custom_fields": {"uplink_roles": ["primary", "backup"]}}
```

```json
{"name": "ntp-region", "weight": 1000, "data": {"ntp-servers": ["192.0.2.10", "192.0.2.11"]},
 "locations": ["<uuid>"], "config_context_schema": "<schema-uuid>"}
```

- Computed field: POST `/api/extras/computed-fields/`. Read it with `?include=computed_fields`, or in GraphQL as `cpf_<key>`. The template context is `obj` (custom fields via `obj.cf.<key>`). Any
  render exception logs a warning and returns `fallback_value`.
- Custom field types: `text`, `integer`, `boolean`, `date`, `datetime`, `url`, `select`, `multi-select`, `json`, `markdown`. A multi-select value is always a list. Choices are separate rows at
  `/api/extras/custom-field-choices/`, and a default must match an existing choice.
- Config Context: higher weight overrides lower; dictionaries merge, but a list value is replaced, not appended. Scopes include locations, roles, device types, device families, platforms, tenants,
  tags and (with the setting) Dynamic Groups. Each context validates against its own schema on save; the rendered result is not validated. Per-object data goes in `local_config_context_data` plus
  `local_config_context_schema`.

Gotcha: a failing computed-field template does not fail loudly; it shows `fallback_value` (empty by default), so test templates against a real object.

Source: `nautobot/extras/models/customfields.py:174,199-204`, `nautobot/extras/choices.py:114-131`, `nautobot/extras/models/models.py:117,174-179,209`; `nautobot-core-3.2.3-computed-fields.html`,
`-custom-fields.html`, `-config-contexts.html`, `-config-context-schemas.html`.

## 5. Secrets and Secrets Groups

Decision: devices and Jobs receive credentials through a Secrets Group, never through custom fields or Job variables. A Secret is a pointer: a provider plus parameters.

```json
{"name": "Device password", "provider": "environment-variable", "parameters": {"variable": "DEVICE_PASSWORD"}}
{"name": "Per-device key", "provider": "text-file", "parameters": {"path": "/opt/nautobot/secrets/{{ obj.name }}.txt"}}
```

```python
group = SecretsGroup.objects.get(name="Device SSH")
pw = group.get_secret_value(access_type="SSH", secret_type="password", obj=device)
```

- Endpoints: `/api/extras/secrets/`, `/api/extras/secrets-groups/`, `/api/extras/secrets-groups-associations/`. An association carries `access_type` and `secret_type`, a pair unique within the group.
- Access types: `Generic`, `Console`, `gNMI`, `HTTP(S)`, `NETCONF`, `REST`, `RESTCONF`, `SNMP`, `SSH`.
- Secret types: `authentication-key`, `authentication-protocol`, `key`, `notes`, `password`, `private-algorithm`, `private-key`, `secret`, `token`, `url`, `username`.
- The built-in providers are `environment-variable` and `text-file`. The Secrets Providers app (4.0.1) adds `hashicorp-vault`, `aws-secrets-manager`, `aws-sm-parameter-store`, `azure-key-vault`,
  `delinea-tss-id`, `delinea-tss-path` and `one-password`; each needs its own `PLUGINS_CONFIG` block.

Gotcha: anyone who can create or edit a Secret can read any environment variable or nautobot-readable file through it, because parameters are Jinja2. Object-permission constraints on `parameters__...`
are guardrails, not a security boundary. The value is never returned over REST.

Source: `nautobot/extras/choices.py:557-592`, `nautobot/extras/models/secrets.py:63,116`, `nautobot_secrets_providers/providers/*.py` (`slug =` lines); `nautobot-core-3.2.3-secrets.html`.

## 6. Webhooks, Job Hooks, Job Buttons, event brokers

Decision: use a webhook to push to an HTTP receiver with no code in Nautobot; a Job Hook to run Nautobot-side logic on change; a Job Button for an operator-pressed action on one object; an event
broker (Redis Pub/Sub or syslog) for a stream of every change.

```json
{"name": "device-changes", "content_types": ["dcim.device"], "type_create": true, "type_update": true, "type_delete": true,
 "payload_url": "https://receiver.example/hook", "http_method": "POST", "http_content_type": "application/json", "secret": "<hmac-key>", "ssl_verification": true}
```

```python
from nautobot.apps.jobs import JobHookReceiver, JobButtonReceiver, register_jobs

class OnDeviceChange(JobHookReceiver):
    def receive_job_hook(self, change, action, changed_object):  # action: create/update/delete; change is the ObjectChange
        self.logger.info("%s %s", action, change.object_repr)

class Resync(JobButtonReceiver):
    def receive_job_button(self, obj):
        self.logger.info("resync %s", obj)

register_jobs(OnDeviceChange, Resync)
```

```python
# nautobot_config.py
EVENT_BROKERS = {
    "redis": {"CLASS": "nautobot.core.events.RedisEventBroker", "OPTIONS": {"url": "redis://redis.example:6379/0"},
              "TOPICS": {"INCLUDE": ["nautobot.create.*", "nautobot.update.*", "nautobot.delete.*"]}},
}
```

- Webhook payload keys: `event` (`created`/`updated`/`deleted`), `timestamp`, `model`, `username`, `request_id`, `data`, and `snapshots` (`prechange`, `postchange`, `differences`). HMAC-SHA512 goes in
  `X-Hook-Signature` when `secret` is set. Delivery is a Celery task; a non-2XX is a failure.
- Event topics are `nautobot.<create|update|delete>.<app>.<model>`, plus user-login and Job started/completed topics. The payload carries `context` (user_name, timestamp, request_id, change_context),
  `prechange`, `postchange` and `differences`.
- Delete events: the webhook `snapshots.postchange` and the event `postchange` are null; read the object from `prechange`. A delete that cascades to association rows records a change only for the
  deleted object, so the other side's hooks do not fire.

Gotcha: a Job Hook runs only if the user who made the change may run the target Job (`extras.run_job`), and the Job must be enabled. Changes made in `nbshell` or scripts outside a change-logging
context (`web_request_context`) record no change, so no webhook or hook fires. Webhook targets are checked against `WEBHOOK_ALLOWED_SCHEMES`, `WEBHOOK_ALLOWED_HOSTS` and
`WEBHOOK_ADDITIONAL_BLOCKED_NETWORKS`. Other webhook fields: `additional_headers`, `body_template` (Jinja2), `ca_file_path`.

Source: `nautobot/extras/models/models.py:997-1044`, `nautobot/extras/models/jobs.py:466-476`, `nautobot/extras/jobs.py:1129-1173`, `nautobot/core/events/__init__.py:22-60`,
`nautobot/core/events/base.py:9`, `redis_broker.py:37`, `syslog_broker.py:10`, `nautobot/core/settings.py:123,337-355`; `nautobot-core-3.2.3-webhooks.html`, `-events.html`, `-job-hooks.html`,
`-job-buttons.html`, `-change-logging.html`, `-settings.html` (EVENT_BROKERS).

## 7. Approval workflows

Decision: approvals are in core in 3.x. Use them to hold a ScheduledJob, or any model with `ApprovableModelMixin`, until a group approves it. Job `approval_required` was removed in 3.0.

```bash
# definition: model + ORM constraints + weight (highest matching weight wins); then ordered stages
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/extras/approval-workflow-definitions/ \
  -d '{"name": "Bulk delete review", "model_content_type": "extras.scheduledjob", "model_constraints": {"job_model__name": "Bulk Delete Objects"}, "weight": 20}'
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/extras/approval-workflow-stage-definitions/ \
  -d '{"approval_workflow_definition": "<def-uuid>", "sequence": 1, "name": "Ops lead", "min_approvers": 1, "approver_group": "<group-id>"}'
# act on a pending stage (user must be in the stage's approver group)
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/extras/approval-workflow-stages/<uuid>/approve/ -d '{"comments": "ok"}'
#   .../deny/   .../comment/   ; cancel: POST /api/extras/approval-workflows/<uuid>/cancel/
```

- Models: `ApprovalWorkflowDefinition` → `ApprovalWorkflowStageDefinition` (template); `ApprovalWorkflow` → `ApprovalWorkflowStage` → `ApprovalWorkflowStageResponse` (instance).
- An approvable object calls `begin_approval_workflow()`; core does this for ScheduledJob. On the final state the workflow calls the object's `on_workflow_approved`, `on_workflow_denied` or
  `on_workflow_canceled`; `on_workflow_initiated` runs on start.
- A Job run via REST that matches a definition returns `201 {"scheduled_job": {...}, "job_result": null}` and waits. Dry runs skip approval. A Job with `has_sensitive_variables=True` that matches a
  definition is refused.
- App pattern (a local custom app, 0.5.x): `OnboardingDecision(ApprovableModelMixin, PrimaryModel)` calls `begin_approval_workflow()` in `save()` when new, applies the change in `on_workflow_approved` inside
  `transaction.atomic()`, and records denied or canceled outcomes. Its bulk approval writes one `ApprovalWorkflowStageResponse` per decision, so each approval stays an individual record.

Gotcha: with no matching definition, `begin_approval_workflow()` returns None and no workflow starts; nothing errors. Weight picks one definition; definitions do not stack. Before
upgrading 2.x to 3.x, `check_job_approval_status` (2.x command, absent from 3.2.3) flags approval-required jobs.

Source: `nautobot/extras/models/mixins.py:15-60`, `nautobot/extras/models/jobs.py:1455`, `nautobot/extras/api/views.py:318-346,351,455-520,995-1022`, `nautobot/extras/api/urls.py:8-11`,
`wc_ownership/models.py:168,213-250`, `wc_ownership/bulk_approval.py:1-50`; `nautobot-core-3.2.3-approval-workflow.html`, `-job-structure.html` (approval_required removed).

## 8. Data Validation and Data Compliance

Decision: since 3.0 the former Data Validation Engine app is core (`nautobot.data_validation`); do not install the app. Use rules for simple field constraints, and a `DataComplianceRule` class in code
or a Git repo for audits that are logic, not one field.

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/data-validation/regex-rules/ \
  -d '{"name": "device-name", "content_type": "dcim.device", "field": "name", "regular_expression": "^[a-z0-9-]+$", "enabled": true}'
# also: /api/data-validation/min-max-rules/, /required-rules/, /unique-rules/ (max_instances), and /data-compliance/ (audit results)
```

- Rule types: regular expression (optional Jinja2 context processing with `obj`), min/max, required, unique (with `max_instances`). Rules apply on every save, in the UI and the API alike.
- Audits: the system Job "Run Registered Data Compliance Rules" runs `DataComplianceRule` classes (from apps or a Git repo's `custom_validators/`) and stores results in `DataCompliance` rows.
  "Validate Model Data" runs `full_clean()` over chosen content types (read-only).

Gotcha: an existing record that breaks a newly added rule is not flagged until it is next saved or audited, and then the save fails. Run an audit before enabling a rule on live data.

Source: `nautobot/core/api/urls.py:47`, `nautobot/data_validation/api/urls.py:9-17`, `nautobot/data_validation/models.py:109-333`, `nautobot/data_validation/custom_validators.py:44,154-165,240-303`,
`nautobot/core/jobs/__init__.py:447,539`; `nautobot-core-3.2.3-data-validation.html`.

## 9. Permissions, tokens, Statuses, Roles, change log

Decision: grant access with ObjectPermissions on groups, scoped by constraints. Treat built-in Statuses and Roles as data you must not delete. Use the change log as the restore source.

```json
{"name": "ops-devices-change", "object_types": ["dcim.device"], "groups": [<group-id>], "actions": ["view", "change"],
 "constraints": [{"location__name": "site-a"}, {"status__name": "Planned"}], "enabled": true}
```

```bash
# Who deleted what: action is create|update|delete (the GraphQL doc example's "created" is wrong for the filter)
curl -s "${H[@]}" "https://nautobot.example/api/extras/object-changes/?action=delete&changed_object_type=extras.role&sort=-time&limit=100"
```

- Permissions: `/api/users/permissions/`. Actions are `view`, `add`, `change`, `delete` plus custom ones such as `run` on Jobs. Keys inside one constraint object are ANDed; objects in a list are ORed;
  multiple permissions are ORed. Users `/api/users/users/`, groups `/api/users/groups/`, tokens `/api/users/tokens/` (40-char `key`, `expires`, `write_enabled`).
- Statuses and Roles are rows with M2M `content_types`. Model FKs to them are `PROTECT`, so one in use cannot be deleted. Defaults are created only by data migrations (`populate_status_choices` /
  `populate_role_choices`), which already ran. A deleted built-in is not recreated by `migrate` or `post_upgrade`.
- Restore from the change log: each `ObjectChange` keeps `object_data` (Django serializer, flat field values) and `object_data_v2` (nullable, so absent on old rows; REST serializer, depth 1). Re-create with the original
  `id` from `object_data_v2`, mapping nested refs back to IDs, and re-add `content_types`.
- Retention: `CHANGELOG_RETENTION` (default 90 days, env `NAUTOBOT_CHANGELOG_RETENTION`, also a Constance setting; 0 = keep forever). The "Logs Cleanup" system Job enforces it.

> **Learned 2026-10-05** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: nautobot/core/api/serializers.py line 158 in the installed source · Falsifier: a 3.2.x POST with an explicit id that returns a different id
> REST create accepts a client-supplied `id` (`UUIDField(read_only=False, default=CreateOnlyDefault(uuid4))`), so a restore can `POST /api/extras/roles/` with `{"id": "<original uuid>", ...}` and keep every reference intact; no shell access is needed. Found by the 2026-10-05 skill evaluation.

Gotcha: a delete record is your only copy once retention purges it; export the delete records before any cleanup script runs. Restoring by name alone breaks anything that references the old UUID.

Source: `nautobot/users/models.py:243-245,283-318`, `nautobot/users/api/urls.py:8-15`, `nautobot/extras/models/statuses.py:47`, `nautobot/extras/models/roles.py:37`,
`nautobot/extras/management/__init__.py:107-170`, `nautobot/extras/models/change_logging.py:43-46,86-109`, `nautobot/core/models/utils.py:99,140-150`, `nautobot/extras/filters.py:1444-1480`,
`nautobot/extras/choices.py:467-469`, `nautobot/core/jobs/cleanup.py:27-105`, `nautobot/core/settings.py:87-88,858`; `nautobot-core-3.2.3-object-permissions.html`, `-change-logging.html`,
`-settings.html`.

## 10. nautobot-server operations commands

Decision: `post_upgrade` after every image change; read-only checks first (`validate_models`, `audit_dynamic_groups`, `health_check`).

```bash
nautobot-server post_upgrade        # migrate, clear_cache, trace_paths, collectstatic, remove_stale_contenttypes, clearsessions,
                                    # send_installation_metrics, refresh_content_type_cache, refresh_dynamic_group_member_caches
nautobot-server post_upgrade --no-send-installation-metrics --no-collectstatic
nautobot-server migrate [--plan]
nautobot-server nbshell             # shell_plus with models imported; ORM writes here are NOT change-logged
nautobot-server runjob --username <user> [--local] [--data '{"var": 1}'] <module_name>.<JobClassName>
nautobot-server collectstatic --no-input
nautobot-server health_check [-s SUBSET]
nautobot-server validate_models [app_label.ModelName ...] [--save]
nautobot-server check                # Django system checks
nautobot-server fix_custom_fields [app_label.ModelName ...]   # only after a custom-field Job failed
nautobot-server refresh_dynamic_group_member_caches
nautobot-server audit_dynamic_groups ; nautobot-server audit_graphql_queries
nautobot-server remove_stale_scheduled_jobs
```

Gotcha: `invalidate` (django-cacheops) no longer exists. Clearing the cache is `clear_cache` (django-extensions), which `post_upgrade` runs since 3.0.10. `runjob --data` defaults to `{}` from 3.2.0,
and `null` is now an error. `init` and `--version` belong to the `nautobot-server` wrapper, not Django subcommands.

Source: `nautobot-server help` and `help post_upgrade|runjob|validate_models|fix_custom_fields|health_check` in the 3.2.3 container; `nautobot/extras/management/commands/runjob.py:20,69-72`;
`nautobot-core-3.2.3-nautobot-server.html`.

## 11. Jobs

Decision: write Jobs with keyword-only `run()` arguments and `register_jobs()`, and start them with `job_kwargs` (required from 3.2.0). Poll the JobResult; never assume a 201 means the work is done.

```python
from nautobot.apps import jobs
from nautobot.dcim.models import Location

class SyncThing(jobs.Job):
    site = jobs.ObjectVar(model=Location)
    dryrun = jobs.DryRunVar()
    class Meta:
        name = "Sync thing"
        has_sensitive_variables = False
        task_queues = ["default"]        # Job Queue names; default_job_queue on the Job model is used when none is given
        soft_time_limit = 300
    def run(self, *, site, dryrun):
        self.logger.info("site=%s dryrun=%s", site, dryrun)

jobs.register_jobs(SyncThing)
```

```bash
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" https://nautobot.example/api/extras/jobs/<uuid-or-name>/run/ \
  -d '{"data": {"site": "<uuid>", "dryrun": true}, "job_queue": "default"}'
# -> 201 {"scheduled_job": null, "job_result": {"id": ..., "status": "PENDING", ...}}
curl -s "${H[@]}" https://nautobot.example/api/extras/job-results/<id>/          # status: PENDING|STARTED|SUCCESS|FAILURE|REVOKED|RETRY
curl -s "${H[@]}" https://nautobot.example/api/extras/job-results/<id>/logs/       # or /api/extras/job-logs/?job_result=<id>
```

```python
JobResult.enqueue_job(job_model=Job.objects.get_for_class_path("my_app.jobs.SyncThing"), user=user, job_kwargs={"site": site.pk, "dryrun": True})
```

Gotcha: a Job must be enabled before it runs. A worker must listen on the chosen queue, or the result sits `PENDING` forever. `task_queue` and `job_queue` must agree when both are sent (`task_queue`
is deprecated). A run that matches an approval definition returns a `scheduled_job` and no `job_result`.

Source: `nautobot/extras/api/serializers.py:896-910`, `nautobot/extras/api/views.py:843,995-1022,1165`, `nautobot/extras/filters.py:1248-1259`, `nautobot/extras/choices.py:289-297`, `nautobot/extras/models/jobs.py:1019`,
`nautobot/apps/jobs.py:3`; `nautobot-core-3.2.3-job-structure.html`, `-job-execution.html`, `-jobs-running.html`, `-job-queues.html`.

## 12. Circuits for WAN uplinks

Decision: model each uplink as a Circuit (Provider + Circuit Type + `cid`), with an A-side Circuit Termination at the site's Location. Put speeds on `commit_rate` and the termination's
`port_speed`/`upstream_speed` (Kbps), and anything else (such as primary/backup) in a custom field.

```bash
B=https://nautobot.example/api/circuits
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" $B/providers/ -d '{"name": "Example ISP"}'
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" $B/circuit-types/ -d '{"name": "Internet"}'
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" $B/circuits/ \
  -d '{"cid": "SITE-A-WAN1", "provider": "<prov-uuid>", "circuit_type": "<type-uuid>", "status": "Active", "commit_rate": 100000,
       "custom_fields": {"uplink_priority": "primary"}}'
curl -s -X POST "${H[@]}" -H "Content-Type: application/json" $B/circuit-terminations/ \
  -d '{"circuit": "<circuit-uuid>", "term_side": "A", "location": "<location-uuid>", "port_speed": 1000000, "upstream_speed": 100000}'
```

Gotcha: a termination must attach to exactly one of `location`, `provider_network` or `cloud_network`; none, or two, is a validation error. `cid` is unique per provider, not globally. Provider and
Circuit Type are `PROTECT`ed while circuits use them.

Source: `nautobot/circuits/models.py:60-78,96-103,123-177,192-247`, `nautobot/circuits/api/urls.py:8-15`; `nautobot-core-3.2.3-circuits.html`, `-circuit-terminations.html`.
