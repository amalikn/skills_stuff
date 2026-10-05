This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, README.md, ARCHITECTURE.md, architecture.md, CONVENTIONS.md, ROADMAP.md, roadmap.md, SCRATCHPAD.md, CHANGELOG.md, SKILL.md, sources.yaml, compatibility.yaml, references/**/*.md, tests/*.md, context-map.yaml, scripts/README.md, scripts/**, justfile, Justfile, Taskfile.yml, Makefile, package.json, memory-bank/**/*.md, .archcore/**/*.md, docs/**/*.md
- Files matching these patterns are excluded: node_modules/**, .git/**, dist/**, build/**, cache/**, runtime/**, __pycache__/**, .venv/**, graphify-out/**, .ai-context/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
````
.archcore/
  adr/
    governance-checker-in-test-suite.adr.md
    independent-platform-pack.adr.md
  plans/
    live-probes-then-client-matrix.plan.md
  rules/
    capability-search-order.rule.md
    changelog-version-of-record.rule.md
    memory-channel-name.rule.md
  index.guide.md
references/
  api-and-writers.md
  app-development.md
  apps-jobs-validation.md
  authority-and-modeling.md
  capability-extension.md
  config-backup-compliance.md
  data-model.md
  discovery-and-topology.md
  evolution-and-write-back.md
  integrations.md
  lifecycle-and-replacement.md
  operations-and-recovery.md
  operations-cookbook.md
  staged-onboarding.md
  upgrade-and-troubleshooting.md
scripts/
  check_governance.py
  nautobot_ipam.py
  nautobot_linkage.py
  nautobot_masks.py
  nautobot_paging.py
  README.md
tests/
  eval-procedure.md
  scenarios.md
AGENTS.md
AI_NAVIGATION.md
CHANGELOG.md
CLAUDE.md
compatibility.yaml
context-map.yaml
justfile
Justfile
README.md
SCRATCHPAD.md
SKILL.md
sources.yaml
````

# Files

## File: .archcore/adr/governance-checker-in-test-suite.adr.md
````markdown
---
title: Governance checker runs inside the test suite
type: adr
status: accepted
tags: [governance, tests]
created: 2026-10-05
---

# ADR: Governance checker runs inside the test suite

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `SCRATCHPAD.md` (KEEP, Recent decisions).

## Context

The skill-ai-it bootstrap (2026-10-05) added `scripts/check_governance.py`. The package contract (`tests/test_package_contract.py`) requires every `scripts/*.py` to be stdlib-only and named in
`tests/test_helpers.py`, so the checker could not sit in `scripts/` untested.

## Decision

`tests/test_helpers.py` runs the checker as a subprocess (`Governance.test_governance_claims_hold`) and proves it can fail on a copy of the pack with a broken reference
(`Governance.test_a_broken_reference_fails_the_gate`). `just test` is therefore the single completion gate; `just check` runs the checker alone.

## Consequences

- A governance drift (an uncataloged helper, an unrouted reference, a stale path) turns the pack's tests red, not just a side command.
- Trade-off: work that adds a helper is red until it is cataloged in `scripts/README.md`. Observed on 2026-10-05 while a parallel session added helpers; this is the intended behaviour.

Confidence: medium — new; revisit if the coupling blocks legitimate in-progress work more than it catches drift.
````

## File: .archcore/adr/independent-platform-pack.adr.md
````markdown
---
title: Independent Nautobot platform pack
type: adr
status: accepted
tags: [pack-boundary, nautobot]
created: 2026-10-05
---

# ADR: Independent Nautobot platform pack

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `SCRATCHPAD.md` (KEEP, Recent decisions).

## Context

Nautobot knowledge was first gathered inside project work and the equipment packs (`skill-smc`, `skill-cambium`). On 2026-10-01 the operator stated (USER_STATED, memory-keeper
`unc.nautobot-openwisp-skill-operator-contract.20261001_1724`) that Nautobot and OpenWISP deserve separate, reusable, evolving skills rather than sections of those packs, learning from
each engaging project while preserving evidence, project boundaries and permission limits.

## Decision

`skill-nautobot` is a standalone, cross-project pack for intended network source of truth (inventory, IPAM, lifecycle, Jobs/apps, integration APIs). It is not a section of `skill-smc` or `skill-cambium`, and it is separate from its counterpart `skill-openwisp`.

## Consequences

- The primary pack for a task is chosen by the object being changed; the other pack is read only for its contract (`SKILL.md`, Route the task).
- Customer, site and equipment specifics stay in the engaging project; vendor commands and OIDs stay with the equipment packs.
- Every engagement owes a write-back here (`references/evolution-and-write-back.md`), which is what keeps a separate pack from going stale.

Confidence: high — operator-stated, and the pack has shipped four releases on this basis.
````

## File: .archcore/plans/live-probes-then-client-matrix.plan.md
````markdown
---
title: Live probes, then the client evaluation matrix
type: plan
status: accepted
tags: [evaluation, compatibility]
created: 2026-10-05
---

# Plan: Live probes, then the client evaluation matrix

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `SCRATCHPAD.md` (KEEP, Open items); origin memory-keeper `unc-platform-skills-0-2-0-posthook-handoff-20261002`.

## Goal

Raise release claims from PARTIAL to evidenced by testing behaviour on a real install and the pack on every target client.

## Steps

1. Stand up a disposable, version-pinned Nautobot matching a `compatibility.yaml` row. Never a production instance.
2. Run the behavioural probes for that row and move its `validation_layer` above `observed_install` only with a `test_id`, as the contract requires.
3. With operator-controlled authentication, run the full client matrix in `tests/eval-procedure.md` (Claude Code, Codex; with and without the skill).
4. Record results in `compatibility.yaml`, `sources.yaml` and a CHANGELOG line; widen release claims only for what passed.

## Exit criteria

Every claimed environment row has live evidence at the layer it claims, and every client in the matrix has a recorded with/without result.

## Blockers

Client authentication and a disposable install are operator-controlled.
````

## File: .archcore/rules/capability-search-order.rule.md
````markdown
---
title: Capability search order
type: rule
status: accepted
tags: [capability, extension]
created: 2026-10-05
---

# Rule: Capability search order

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate sources: `AGENTS.md` (Working rules), `SKILL.md` (Search before building). USER_STATED 2026-10-01.

## Rule

Before building anything for Nautobot, search in this order and state at each step why the previous level cannot meet the acceptance test:

1. Existing Nautobot core capability.
2. Installed or maintained provider apps/modules and relevant NTC tooling.
3. Supported extension points of those components.
4. Compatible external FOSS and its supported seams.
5. A from-scratch component, only when the acceptance test still cannot be met.

Prefer add-ons. Log every core patch so it is reapplied, adapted or retired after an upgrade, with a regression test on the behaviour it relies on.

## Enforcement

Judgement, applied at design time; no automated check. `SKILL.md` (Search before building) restates the order for the agent at the point of decision; this document is the durable source.
````

## File: .archcore/rules/changelog-version-of-record.rule.md
````markdown
---
title: CHANGELOG release heading is the version of record
type: rule
status: accepted
tags: [versioning, governance]
created: 2026-10-05
---

# Rule: CHANGELOG release heading is the version of record

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `AGENTS.md` (Working rules).

## Rule

The pack version is the newest release heading in `CHANGELOG.md` (`## x.y.z — date`). No other pack file restates it. Unreleased work, including every write-back line, goes under
`## Unreleased` until release reconciliation (`references/evolution-and-write-back.md`).

## Why

The package contract forbids a manifest JSON file, so there is no second metadata surface; restating the version elsewhere would create one by hand, and it would drift.

## Enforcement

The contract test requires a version-shaped heading in `CHANGELOG.md`. Restatement elsewhere is not yet checked: the candidate is a `CONSTANT_SURFACES` entry in
`scripts/check_governance.py` registering `CHANGELOG.md` as the only surface for this pack's version string.
````

## File: .archcore/rules/memory-channel-name.rule.md
````markdown
---
title: Memory channel is exactly nautobot
type: rule
status: accepted
tags: [memory]
created: 2026-10-05
---

# Rule: Memory channel is exactly `nautobot`

Status: accepted (operator, 2026-10-05)

Promoted by `skill-ai-it promote` on 2026-10-05 from `ARCHCORE_PROMOTION_CANDIDATES.md` (now deleted); operator authorized promotion of all candidates. Candidate source: `AGENTS.md` (Working rules). USER_STATED 2026-10-01.

## Rule

memory-keeper entries about this pack use the channel `nautobot` — exactly that string, no prefix or suffix. Project-specific engagement notes may also go to the engaging project's channel.

## Why

The operator named the channels explicitly so that recall for Nautobot work is one query across projects.

## Enforcement

None automated. memory-keeper truncates channels to 20 characters and normalises underscores to hyphens; `nautobot` is unaffected by either.
````

## File: .archcore/index.guide.md
````markdown
---
title: Archcore index — skill-nautobot
status: accepted
tags: [index]
---

Durable index of everything promoted into `.archcore/` for skill-nautobot. Written by `skill-ai-it` in `promote` mode on 2026-10-05 from the candidates queue, which was then deleted: it was a
proposal queue, not a record. This index is the record.

Promotion wrote every document as `status: proposed`. **The operator accepted all 6 on 2026-10-05.** They are now the highest-authority statement of what this pack has
decided. Supersede an accepted document in place with a dated note naming its replacement rather than deleting it; a document's own Confidence line says what remains open.

## adr/

| Document | Status |
|---|---|
| [independent-platform-pack.adr.md](adr/independent-platform-pack.adr.md) | accepted |
| [governance-checker-in-test-suite.adr.md](adr/governance-checker-in-test-suite.adr.md) | accepted |

## rules/

| Document | Status |
|---|---|
| [capability-search-order.rule.md](rules/capability-search-order.rule.md) | accepted |
| [changelog-version-of-record.rule.md](rules/changelog-version-of-record.rule.md) | accepted |
| [memory-channel-name.rule.md](rules/memory-channel-name.rule.md) | accepted |

## plans/

| Document | Status |
|---|---|
| [live-probes-then-client-matrix.plan.md](plans/live-probes-then-client-matrix.plan.md) | accepted |

## Never promoted, and why

| Candidate area | Reason |
|---|---|
| specs/ — claim and environment ledger schemas | Already specified executably by `tests/test_package_contract.py`; a prose spec would be a second, unenforced copy |
| guides/ — write-back procedure | Lives in `references/evolution-and-write-back.md`, which the contract test enforces and every engagement already loads |
| Rules from the parent `AGENTS.md` and the global policy | Governed upstream; restating them here would duplicate policy |

## Proposing another

Run `/skill-ai-it refresh`; it re-scans the governance files and writes a new `ARCHCORE_PROMOTION_CANDIDATES.md`. Check the table above first so a rejected area is not re-proposed.
````

## File: references/api-and-writers.md
````markdown
# API and writers

## Reader contract

The project experienced unordered pagination that produced a distorted, incomplete object set. Stable ordering is therefore a tested reusable pattern, not decorative API hygiene. Ask the source API
for a unique stable order or use its documented cursor/snapshot guarantee, follow only its returned continuation, impose a finite page bound, and record page identity plus stable object identity.

Sorting does not create a snapshot. Stop and report ambiguity when a continuation repeats, a page fails to advance, an expected identity repeats, an identity disappears between pages, a page is empty
before completion, or the source changes during traversal. Blind deduplication can hide both missing and duplicated data, so it does not prove completeness. Retrying may be appropriate only for named,
idempotent read failures; it cannot repair changing-data semantics.

## Writer contract

Keep readers and writers separately identifiable. The caller owns authentication, authorization, base URL, retry policy, and secret delivery; reusable guidance must not embed them. A writer should
declare its service identity and owned fields, read enough existing state to decide idempotence, produce a reviewable plan, support dry-run without mutation, and report an ownership conflict rather
than overwriting another authority.

Before a write ask: Which object identity is authoritative? Which fields may this identity own? Does the desired state already exist? Does a partial failure have a safe retry? Is a mutation allowed
by the governing project? If any answer is missing, fail closed with diagnostics that distinguish authentication, permission, model validation, ownership conflict, pagination ambiguity, and transport
failure. Do not treat a successful request as evidence that downstream workers or external devices changed.

Relationship serialization, query depth, permissions, pagination, and Job/API details vary by release and query options. Confirm the exact endpoint and product version before integration code relies
on a response shape. Acceptance means the read set is complete under its stated contract and every planned write has explicit authority, identity, idempotence, and an observable outcome. Claims N-C03
and N-C13.

## Reader algorithm and failure example

UNC's `nautobot_paging.listing()` sets `limit` and `sort=id` on the first request; callers follow returned `next`. Its regression test proves those two operations,
**not** a generic snapshot or duplicate detector. Before using a list to plan writes, enforce the extra reader contract:

```text
Pseudocode, not an executable Nautobot client:
seen_urls = {}; seen_ids = {}; pages = 0
request first URL with verified unique ordering (or documented cursor)
while URL exists:
    reject repeated URL; increment pages; reject pages > finite bound
    GET; retry only named transient read errors, with capped attempts/backoff
    require complete response shape; reject missing or repeated stable IDs
    append results; follow the returned next exactly
compare count/identity manifest if available; otherwise label snapshot completeness unproved
```

Synthetic failure: page 1 yields `a,b` and `next=offset=2`; page 2 yields `b,c`. Four rows are not four objects: reject repeated `b`, do not silently
deduplicate to `a,b,c`, since `d` may have been skipped. A repeated continuation, missing `results`, premature empty page with `next`, or page-bound overflow is an
error. Sorting alone cannot prevent concurrent insert/delete from moving an offset boundary; use a documented cursor/snapshot, or re-read against a stable manifest and
state remaining uncertainty. No mutation may rely on ambiguous traversal.

## Writer decision and observable result

Match by immutable authoritative identity before mutable name/address. Dry-run output should give action, matched ID and corroboration, before/after **owned fields**,
unchanged fields, conflicts and dependent links. Reject ambiguous matches and missing ownership. On apply, validate server-side, record per-object success/failure,
re-read affected objects and relationships, and distinguish an API save from a downstream Job/device outcome. A partial batch is not success: retry idempotent records
only after re-reading current state and expose compensation/rollback. Verify exact relationship serialization in the target version's schema or a disposable fixture;
this reference promises no one shape. Read [authority and modeling](authority-and-modeling.md) and [staged onboarding](staged-onboarding.md) for combined tasks.
````

## File: references/app-development.md
````markdown
---
Title: Nautobot app development
Category: skill-reference
Status: current
Authority: Installed Nautobot 3.2.3 source and its bundled documentation; the cited lines win over this summary
Scope: >-
  Writing a Nautobot 3.2 app: NautobotAppConfig, the nautobot.apps import namespace, base models and migrations, filtersets, forms, tables, REST serializers and
  viewsets, UI viewsets and the UI component framework, URL registration, navigation, template extensions, custom validators, signals, Jobs in apps, settings,
  testing and packaging
Last reviewed: 2026-10-05
Summary: Twelve verified recipes and a minimal working app skeleton for Nautobot 3.2.3 app development, each with a gotcha and a source line.
---

# Nautobot app development

Verified against: Nautobot 3.2.3 (installed source in a 3.2.3 container, and the docs bundled in the package), checked 2026-10-05.

Source paths are relative to `site-packages/`. `docs/...` means the page bundled under `nautobot/project-static/docs/`, also published at
`https://archive.docs.nautobot.com/projects/core/en/v3.2.3/<same path>/`. Placeholders: package `my_app`, model `Widget`, base URL `my-app`. Apps seen installed for comparison:
`nautobot_golden_config` 3.0.7, `nautobot_plugin_nornir` 3.2.4, `nautobot_secrets_providers` 4.0.1, `nautobot_dns_models` 2.3.0, `nautobot_design_builder` 3.1.2 (all enabled);
`nautobot_capacity_metrics` 4.1.1 is installed but not in `PLUGINS`.

## Summary

| Job               | Use                        | Key syntax                        | Trap                                   | Section |
| ----------------- | -------------------------- | --------------------------------- | -------------------------------------- | ------- |
| Declare the app   | `NautobotAppConfig`        | `config = MyAppConfig`            | required setting ignores its default   | [1](#1-app-config-and-settings) |
| Import APIs       | `nautobot.apps.*`          | `nautobot.apps.models`            | `nautobot.core.*` is internal          | [2](#2-the-nautobotapps-import-namespace) |
| Add a model       | `PrimaryModel`             | `makemigrations my_app`           | `BaseModel` has no change log or tags  | [3](#3-models-and-migrations) |
| Filter everywhere | `NautobotFilterSet`        | `SearchFilter(...)`               | drives UI, REST and GraphQL filters    | [4](#4-filtersets-forms-and-tables) |
| REST endpoint     | `NautobotModelViewSet`     | `api/urls.py` `urlpatterns`       | lives under `/api/plugins/<base_url>/` | [5](#5-rest-api) |
| UI pages          | `NautobotUIViewSet`        | `NautobotUIViewSetRouter`         | needs queryset, serializer and table   | [6](#6-ui-viewsets-and-the-ui-component-framework) |
| Menu entry        | `navigation.py`            | `menu_items = (NavMenuTab(...),)` | docs example says `menu_tabs`          | [7](#7-navigation-menu) |
| Add to core page  | `TemplateExtension`        | `object_detail_panels`            | `left_page()` deprecated since 2.4     | [8](#8-template-extensions) |
| Enforce a rule    | `CustomValidator`          | `self.validation_error({...})`    | bare ORM `.save()` skips it            | [9](#9-custom-validators-and-signals) |
| Seed on install   | `nautobot_database_ready`  | `connect(fn, sender=self)`        | reruns on every migrate                | [9](#9-custom-validators-and-signals) |
| Ship Jobs         | `jobs.py`                  | `register_jobs(*jobs)`            | unregistered Job is invisible          | [10](#10-jobs-in-apps) |
| Test              | `nautobot.apps.testing`    | `nautobot-server test my_app`     | `integration` tag excluded by default  | [11](#11-testing) |
| Install           | `PLUGINS` + `post_upgrade` | `PLUGINS = ["my_app"]`            | web, worker and beat all need it       | [12](#12-packaging-and-installation) |

## Contents

- [Summary](#summary)
- [1. App config and settings](#1-app-config-and-settings)
- [2. The nautobot.apps import namespace](#2-the-nautobotapps-import-namespace)
- [3. Models and migrations](#3-models-and-migrations)
- [4. Filtersets, forms and tables](#4-filtersets-forms-and-tables)
- [5. REST API](#5-rest-api)
- [6. UI viewsets and the UI component framework](#6-ui-viewsets-and-the-ui-component-framework)
- [7. Navigation menu](#7-navigation-menu)
- [8. Template extensions](#8-template-extensions)
- [9. Custom validators and signals](#9-custom-validators-and-signals)
- [10. Jobs in apps](#10-jobs-in-apps)
- [11. Testing](#11-testing)
- [12. Packaging and installation](#12-packaging-and-installation)
- [13. Minimal working skeleton](#13-minimal-working-skeleton)

## 1. App config and settings

Decision: every app is one `NautobotAppConfig` subclass exported as `config` from the package `__init__.py`; its settings come from `PLUGINS_CONFIG[<name>]`.

```python
# my_app/__init__.py
from nautobot.apps import NautobotAppConfig
class MyAppConfig(NautobotAppConfig):
    name = "my_app"                    # import path, also the app label
    verbose_name = "My App"
    description = "Example app"
    version = "0.1.0"
    author = "Example"
    author_email = "dev@example.invalid"
    base_url = "my-app"                # UI /plugins/my-app/, API /api/plugins/my-app/
    default_settings = {"enforce": False}
config = MyAppConfig
```

Code-location attributes (defaults; override only to move a file): `jobs = "jobs.jobs"`, `menu_items = "navigation.menu_items"`, `template_extensions = "template_content.template_extensions"`,
`custom_validators = "custom_validators.custom_validators"`, `datasource_contents = "datasources.datasource_contents"`, `jinja_filters = "jinja_filters"`, `graphql_types =
"graphql.types.graphql_types"`, `filter_extensions`, `table_extensions`, `secrets_providers`, `homepage_layout`, `banner_function`, `metrics = "metrics.metrics"`, `override_views =
"views.override_views"`.

Gotcha: a key in both `required_settings` (or `constance_config`) and `default_settings` ignores the default. Read `settings.PLUGINS_CONFIG["my_app"]` at call time, not at import time, or settings
overrides in tests are not seen.

Source: `nautobot/extras/plugins/__init__.py:50-104` (attributes), `:113-127` (URL mounting); `nautobot/core/settings.py:209-210`; `docs/development/apps/api/nautobot-app-config.html`.

## 2. The nautobot.apps import namespace

Decision: import only from `nautobot.apps` and its submodules, the documented surface for apps.

`nautobot.apps`: `NautobotAppConfig`, `nautobot_database_ready`, `ConstanceConfigItem`; `nautobot.apps.models`: `BaseModel`, `OrganizationalModel`, `PrimaryModel`, `StatusField`, `extras_features`,
`CustomValidator`; `nautobot.apps.filters`: `NautobotFilterSet`, `SearchFilter`, `NaturalKeyOrPKMultipleChoiceFilter`, `StatusModelFilterSetMixin`; `nautobot.apps.forms`: `NautobotModelForm`,
`NautobotFilterForm`, `NautobotBulkEditForm`, `TagFilterField`, `TagsBulkEditFormMixin`; `nautobot.apps.tables`: `BaseTable`, `ToggleColumn`, `ButtonsColumn`, `TagColumn`, `LinkedCountColumn`;
`nautobot.apps.api`: `NautobotModelSerializer`, `NautobotModelViewSet`, `TaggedModelSerializerMixin`, `OrderedDefaultRouter`; `nautobot.apps.views`: `NautobotUIViewSet`, the `Object*ViewMixin`
classes, `ObjectView`, `GenericView`; `nautobot.apps.ui`: `NavMenu*`, `NavigationWeightChoices`, `ObjectDetailContent`, `ObjectFieldsPanel`, `Tab`, `TemplateExtension`; `nautobot.apps.jobs`: `Job`,
`register_jobs`, the `*Var` classes, `JobHookReceiver`, `JobButtonReceiver`; `nautobot.apps.testing`: `TestCase`, `ViewTestCases`, `APIViewTestCases`, `FilterTestCases`, `AssertNoRepeatedQueries`.

Gotcha: `NavigationWeightChoices` comes from `nautobot.apps.ui`, not from `nautobot.apps` as one docs warning says. Core apps import from `nautobot.core.apps`.

Source: the `__all__` tuples at `nautobot/apps/__init__.py:7`, `apps/models.py:62`, `apps/filters.py:48`, `apps/forms.py:109`, `apps/tables.py:21`, `apps/api.py:51`, `apps/views.py:55`,
`apps/urls.py:5`, `apps/ui.py:84`, `apps/jobs.py:36`, `apps/testing.py:67`.

## 3. Models and migrations

Decision: `PrimaryModel` for things on the network, `OrganizationalModel` for categories; `BaseModel` only when no extensibility is wanted.

| Feature                                                                                      | Base | Organizational | Primary |
| -------------------------------------------------------------------------------------------- | ---- | -------------- | ------- |
| UUID pk, natural key, object permissions, `validated_save()`, object metadata                | yes  | yes            | yes     |
| Change log, contacts/teams, custom fields, Dynamic Groups, notes, relationships, Saved Views | no   | yes            | yes     |
| Tags                                                                                         | no   | no             | yes     |

```python
from django.db import models
from nautobot.apps.models import PrimaryModel, extras_features

@extras_features("graphql", "custom_links", "export_templates", "webhooks")
class Widget(PrimaryModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["name"]
```

Generate migrations with `nautobot-server makemigrations my_app` (the app must already be in `PLUGINS`) and apply them with `nautobot-server migrate my_app`, or `post_upgrade` in deployment.

`extras_features` also takes `cable_terminations`, `dynamic_groups`, `locations`, `statuses` and others (list at `extras/constants.py:5-21`); a model needs `statuses` before a Status can list its
content type.

Gotcha: commit migrations with the code; never generate them at deploy time. Expose GraphQL either with `@extras_features("graphql")` or a hand-written type in `graphql/types.py`, never both.

Source: `nautobot/core/models/generics.py:19-67`, `nautobot/core/models/__init__.py:38,147`, `nautobot/extras/constants.py:5-21`, `nautobot/extras/utils.py:344`;
`docs/development/apps/api/models/index.html`, `docs/development/apps/api/models/graphql.html`.

## 4. Filtersets, forms and tables

Decision: one `NautobotFilterSet` per model; the REST API, the UI list filter and GraphQL list arguments all use it.

```python
import django_tables2 as tables
from django import forms
from nautobot.apps.filters import NautobotFilterSet, SearchFilter
from nautobot.apps.forms import NautobotFilterForm, NautobotModelForm, TagFilterField
from nautobot.apps.tables import BaseTable, ButtonsColumn, TagColumn, ToggleColumn
class WidgetFilterSet(NautobotFilterSet):
    q = SearchFilter(filter_predicates={"name": "icontains", "description": "icontains"})
    class Meta:
        model = Widget
        fields = "__all__"
class WidgetForm(NautobotModelForm):
    class Meta:
        model = Widget
        fields = ["name", "description", "tags"]
class WidgetFilterForm(NautobotFilterForm):
    model = Widget
    q = forms.CharField(required=False, label="Search")
    tags = TagFilterField(model)
class WidgetTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    tags = TagColumn(url_name="plugins:my_app:widget_list")
    actions = ButtonsColumn(Widget)
    class Meta(BaseTable.Meta):
        model = Widget
        fields = ("pk", "name", "description", "tags", "actions")
        default_columns = ("pk", "name", "description", "actions")
```

A bulk edit form (`TagsBulkEditFormMixin, NautobotBulkEditForm`, a hidden `pk` field and `Meta.nullable_fields`) set as `bulk_update_form_class` enables bulk edit; the core pattern is
`circuits/forms.py:66-80`. Gotcha: with `STRICT_FILTERING` on (default) a parameter the filterset lacks is a REST 400, not ignored. `NautobotFilterSet` already adds `created`/`last_updated`, `cf_*`
custom-field and relationship
filters.

Source: `nautobot/extras/filters.py:607-620`; the core pattern at `nautobot/circuits/filters.py:31-72`, `circuits/forms.py:38-91`, `circuits/tables.py:52-75`; `nautobot/data_validation/filters.py:36`
(`fields = "__all__"` in core).

## 5. REST API

Decision: `NautobotModelSerializer` + `NautobotModelViewSet` give custom fields, relationships, notes, `?depth` and bulk operations.

```python
# api/serializers.py
from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin
class WidgetSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    class Meta:
        model = Widget
        fields = "__all__"
# api/views.py
from nautobot.apps.api import NautobotModelViewSet
class WidgetViewSet(NautobotModelViewSet):
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer
    filterset_class = WidgetFilterSet
# api/urls.py (must define urlpatterns)
from nautobot.apps.api import OrderedDefaultRouter
router = OrderedDefaultRouter()
router.register("widgets", WidgetViewSet)
app_name = "my_app-api"
urlpatterns = router.urls
```

Gotcha: the endpoint is `/api/plugins/my-app/widgets/`, reverse name `plugins-api:my_app-api:widget-list`. Nautobot imports `<app>.api.urls.urlpatterns` and `<app>.urls.urlpatterns` by name; any
other module is silently not mounted. Since 2.4 the viewsets add `select_related`/`prefetch_related`
themselves, but annotations such as counts are still yours to add to `queryset`.

Source: `nautobot/extras/plugins/__init__.py:113-122`, `nautobot/core/api/urls.py:68`, `nautobot/core/urls.py:81`, `nautobot/core/api/serializers.py:973`, `nautobot/extras/api/views.py:263`,
`nautobot/core/api/routers.py:10`, `nautobot/circuits/api/urls.py:1-20`; `docs/development/apps/api/views/rest-api.html`.

## 6. UI viewsets and the UI component framework

Decision: `NautobotUIViewSet` provides list, detail, edit, delete, bulk edit/delete/rename, change log, notes and Data Compliance views; declare the detail page with `object_detail_content` (UI
component framework) instead of an HTML template.

```python
# views.py
from nautobot.apps.ui import ObjectDetailContent, ObjectFieldsPanel, SectionChoices
from nautobot.apps.views import NautobotUIViewSet
class WidgetUIViewSet(NautobotUIViewSet):
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer
    table_class = WidgetTable
    form_class = WidgetForm
    filterset_class = WidgetFilterSet
    filterset_form_class = WidgetFilterForm
    object_detail_content = ObjectDetailContent(
        panels=(ObjectFieldsPanel(section=SectionChoices.LEFT_HALF, weight=100, fields="__all__"),),
    )
# urls.py
from nautobot.apps.urls import NautobotUIViewSetRouter
app_name = "my_app"
router = NautobotUIViewSetRouter()
router.register("widgets", WidgetUIViewSet)
urlpatterns = router.urls
```

Route names are `plugins:<app>:<model>_<action>` (`widget_list`, `widget`, `widget_add`, `widget_edit`, `widget_delete`). To drop bulk views, inherit only the `ObjectListViewMixin`,
`ObjectDetailViewMixin`, `ObjectEditViewMixin` and `ObjectDestroyViewMixin` you need; the router then publishes no bulk routes. A custom `@action(detail=True)` needs a template
`my_app/widget_<action>.html` and, by default, the permission `my_app.<action>_widget`.

Gotcha: `queryset`, `serializer_class` and `table_class` must be set or most actions fail. `lookup_field` defaults to `pk`; another value can hide the edit and delete buttons. `bulk_rename` is added
automatically for a model with an editable `name`.

Source: `nautobot/core/views/viewsets.py:4-22`, `nautobot/core/views/routers.py:4`, `nautobot/circuits/views.py:157-184`; `docs/development/apps/api/views/nautobotuiviewset.html`,
`docs/development/apps/api/views/nautobotuiviewsetrouter.html`.

## 7. Navigation menu

Decision: add items to an existing tab by repeating its `name`, `weight` and `icon`; add a new tab only for a substantial app.

```python
# navigation.py: the loader reads the variable menu_items
from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab, NavigationIconChoices, NavigationWeightChoices
menu_items = (
    NavMenuTab(name="Devices", icon=NavigationIconChoices.DEVICES, weight=NavigationWeightChoices.DEVICES, groups=(
        NavMenuGroup(name="Widgets", weight=950, items=(
            NavMenuItem(link="plugins:my_app:widget_list", name="Widgets", permissions=["my_app.view_widget"],
                        buttons=(NavMenuAddButton(link="plugins:my_app:widget_add", permissions=["my_app.add_widget"]),)),
        )),
    )),
)
```

Gotcha: the docs example assigns `menu_tabs = (...)`, but `menu_items` defaults to `"navigation.menu_items"`, so that name is never loaded. Buttons are hidden when the user lacks the item's own
permission. Core weights are multiples of 100; offset from `NavigationWeightChoices`, never hard-code.

Source: `nautobot/extras/plugins/__init__.py:100`, `nautobot/circuits/navigation.py:1-50`; `docs/development/core/navigation-menu.html`.

## 8. Template extensions

Decision: inject panels, tabs or buttons into a core model's pages with a `TemplateExtension`, using the 2.4+ attributes.

```python
# template_content.py
from nautobot.apps.ui import ObjectTextPanel, SectionChoices, TemplateExtension
class DeviceWidgetPanel(TemplateExtension):
    model = "dcim.device"
    object_detail_panels = (
        ObjectTextPanel(weight=100, label="Device comments", section=SectionChoices.LEFT_HALF,
                        render_as=ObjectTextPanel.RenderOptions.MARKDOWN, object_field="comments"),
    )
template_extensions = [DeviceWidgetPanel]
```

Also available: `object_detail_tabs` (`Tab`, `DistinctViewTab`), `object_detail_buttons`, and `list_buttons()`. `self.context` holds `object`, `request`, `settings` and `config` (this app's
`PLUGINS_CONFIG`). `RenderOptions`: `PLAINTEXT`, `JSON`, `YAML`, `MARKDOWN`, `CODE`, `HYPERLINKED_OBJECT`.

Gotcha: `left_page()`, `right_page()`, `full_width_page()`, `buttons()` and `detail_tabs()` are deprecated since 2.4. In `list_buttons()`, `object` is the model class, not an instance.

Source: `nautobot/extras/plugins/__init__.py:291-395`, `nautobot/core/ui/object_detail.py:2067-2084`; `docs/development/apps/api/ui-extensions/object-views.html`.

## 9. Custom validators and signals

Decision: a `CustomValidator` enforces a rule on every write path that calls `clean()` (UI, REST, Jobs using `validated_save()`); for field-only rules prefer core Data Validation, which needs no code.

```python
# custom_validators.py
from nautobot.apps.models import CustomValidator
class DeviceSerialRequired(CustomValidator):
    model = "dcim.device"
    def clean(self):
        obj = self.context["object"]        # self.context["user"] is set for web, API and Job writes (2.4.4+)
        if obj.status.name == "Active" and not obj.serial:
            self.validation_error({"serial": "Active devices need a serial"})
custom_validators = [DeviceSerialRequired]
# signals.py, connected in MyAppConfig.ready():
#     super().ready(); nautobot_database_ready.connect(ensure_statuses, sender=self)
def ensure_statuses(sender, apps, **kwargs):
    Status = apps.get_model("extras", "Status")
    ContentType = apps.get_model("contenttypes", "ContentType")
    status, _ = Status.objects.get_or_create(name="Active")
    status.content_types.add(ContentType.objects.get_for_model(sender.get_model("Widget")))
```

Gotcha: `nautobot_database_ready` fires on every `migrate` and `post_upgrade`, so the handler must be idempotent and may recreate rows an operator deleted. Without `sender=self` it runs once per
`ready()` call. A bare ORM `.save()` skips custom validators.

Source: `nautobot/extras/plugins/__init__.py:719,783`, `nautobot/core/signals.py:13`; `docs/development/apps/api/platform-features/custom-validators.html`,
`docs/development/apps/api/platform-features/prepopulating-data.html`.

## 10. Jobs in apps

Decision: ship operator-run automation as Jobs in the app's `jobs.py`; the Job API is the same as for Git or `JOBS_ROOT` Jobs.

```python
# jobs.py
from nautobot.apps.jobs import Job, ObjectVar, register_jobs
from nautobot.dcim.models import Device
name = "My App"   # grouping shown in the Jobs list
class AuditWidgets(Job):
    device = ObjectVar(model=Device)
    class Meta:
        name = "Audit widgets"
    def run(self, *, device):
        self.logger.info("Checked %s", device, extra={"object": device})
jobs = [AuditWidgets]
register_jobs(*jobs)
```

Gotcha: since 2.0 a Job not passed to `register_jobs()` cannot run, even if listed in `jobs`. A new Job record is created disabled (`enabled` defaults to False) until an administrator enables it.
Workers import the app, so the worker image needs the same package version.

Source: `nautobot/apps/jobs.py:36`, `nautobot/extras/models/jobs.py:148`, `nautobot_golden_config/jobs.py:54,630-638` (an installed app doing the same);
`docs/development/apps/api/platform-features/jobs.html`.

## 11. Testing

Decision: use Nautobot's runner and the base classes in `nautobot.apps.testing`; they create the user, token and statuses the views expect.

Run `nautobot-server test my_app` (`--keepdb` reuses the test DB, `--parallel N`); integration tests need `nautobot-server test --tag integration my_app`.

```python
from nautobot.apps.testing import APIViewTestCases
class WidgetAPITest(APIViewTestCases.APIViewTestCase):
    model = Widget
    create_data = [{"name": "w1"}, {"name": "w2"}]
    bulk_update_data = {"description": "bulk"}
    choices_fields = []
    @classmethod
    def setUpTestData(cls):
        for n in ("a", "b", "c"):
            Widget.objects.create(name=n)
```

`FilterTestCases.FilterTestCase` takes `queryset`, `filterset` and `generic_filter_tests = [["name"], ["description"]]`. `AssertNoRepeatedQueries(self, threshold=10)` fails a block that repeats one
SQL shape more than `threshold` times (an N+1 detector).

Gotcha: `NautobotTestRunner` excludes the `integration` and `migration_test` tags unless named with `--tag`. `ViewTestCases.PrimaryObjectViewTestCase` reads `form_data`, optional `update_data`, and
`bulk_edit_data`; check each inherited class for its required attributes.

Source: `nautobot/core/settings.py:329,332`, `nautobot/core/tests/runner.py:48-71`, `nautobot/core/testing/api.py:168,337,855,1499`, `nautobot/core/testing/filters.py:29-91`,
`nautobot/core/testing/views.py:155,532,691,1602,2534`; `nautobot-server help test`; `docs/development/apps/api/testing.html`.

## 12. Packaging and installation

Decision: an app is an ordinary Python package; no entry point is needed, only its import name in `PLUGINS`.

```bash
pip install my-app                  # into the web, worker and scheduler images or venvs
# add "my_app" to PLUGINS (and PLUGINS_CONFIG) in nautobot_config.py
nautobot-server post_upgrade        # migrate, trace_paths, collectstatic, stale content types, caches
# restart web, worker and scheduler; Apps > Installed Apps then lists it
```

Gotcha: run `post_upgrade` after every app install or upgrade. Templates and static files must be package data or they are missing from the wheel. For `pyproject.toml` bounds, a maintained example is
`nautobot-app-ssot` 4.7.0: `python = ">=3.10,<3.15"`, `nautobot = ">=3.1.0,<4.0.0"`.

Source: `nautobot/core/management/commands/post_upgrade.py:101-158`; `docs/user-guide/administration/installation/app-install.html`, `docs/development/apps/api/setup.html`;
`https://github.com/nautobot/nautobot-app-ssot/blob/v4.7.0/pyproject.toml` lines 31-33.

## 13. Minimal working skeleton

```text
my-app/pyproject.toml
my_app/__init__.py  models.py  migrations/__init__.py           (sections 1, 3)
my_app/filters.py  forms.py  tables.py                          (section 4)
my_app/api/__init__.py  serializers.py  views.py  urls.py       (section 5)
my_app/views.py  urls.py  navigation.py                         (sections 6, 7)
my_app/tests/__init__.py  test_api.py                           (section 11)
```

Build order: config, model, `makemigrations`, filterset, serializer, API viewset and `api/urls.py`, forms and table, UI viewset and `urls.py`, navigation, tests. Check each step with `nautobot-server
check`, then `nautobot-server test my_app`. Each file's content is the block in the named section, with the model imported (`from my_app.models import Widget`) where the blocks use it.
````

## File: references/apps-jobs-validation.md
````markdown
# Apps, Jobs and validation

## Choose the execution seam

Use core behavior when it meets the acceptance test and ownership boundary. Use a maintained app when it is version-compatible and operationally reachable. Use a supported custom app or API extension
when the domain model or permissions belong inside Nautobot. Use a Job for an operator-triggered or schedulable task whose worker can safely reach every required dependency. Keep execution outside
Nautobot when the network path, credentials, retry model, or operational blast radius cannot be safely provided to its workers.

The project Device Onboarding, SSoT, and DiffSync assessment is an example, not a blanket verdict: a feature is not a valid solution merely because Nautobot supports its model if the worker cannot
reach the network or device path required to execute it. Reassess reachability, driver fit, and authority in each deployment. Claim N-C16.

## Validation and diagnostics

UI execution and worker execution may differ in settings, permissions, environment variables, queues, network route, database transaction, and extension registration. Test the path the operator will
actually use. A validator must deliberately fail open or fail closed: fail-open permits questionable data under an outage; fail-closed can stop legitimate work. State which result is acceptable and
how it is surfaced.

Diagnose by asking whether the Job was registered, queued, claimed, able to authenticate, able to resolve its dependencies, authorized to write the target field, and able to return a visible result.
Service writers need least-privilege permissions and an explicit field-ownership contract. A UI success is not proof of a worker success.

Nautobot 3.2 changed Job invocation patterns; import or startup success does not prove functional compatibility, and functional compatibility does not prove an operator-visible outcome. Upgrade tests
must exercise the exact Job, validator, queue, and rollback path. Claim N-C08.

## Follow the actual execution path

| Stage                    | Failure signature                   | Next discriminating check                                        | Evidence of success                           |
| ------------------------ | ----------------------------------- | ---------------------------------------------------------------- | --------------------------------------------- |
| App/Job registration     | Missing in UI/API                   | Installed app config, imports and registration on web **and worker** | Same Job ID/version visible to both           |
| Scheduling/queue         | Click accepted; no run              | JobResult and queue/routing, scheduled kwargs                    | One task enqueued on intended queue           |
| Worker consumption       | Pending forever                     | Worker subscribed queue, process image/settings and task log     | Same task ID claimed                          |
| Credentials/reachability | Task starts, no source data         | Secret provider resolution from worker and network vantage       | Bounded read to dependency succeeds           |
| Permissions/ownership    | Read succeeds; save rejected        | Writer identity, model permissions, field validator              | Intended field transition accepted            |
| Validation/transaction   | Some records vanish or rollback     | `full_clean`, exception and transaction boundary                 | Object count and relationships re-read        |
| Visible result           | Job green, operator sees no outcome | UI query, cache/index and downstream consumer                    | Operator sees named target and expected state |

Synthetic case: a Job appears in the UI and enqueues, but worker log shows no route to a site-side collector. Device Onboarding app support is not the issue; the
execution vantage is. Keep collection in a reachable external adapter or provide an approved worker route, then rerun a synthetic Job that produces a visible Device
candidate. UNC rejected Device Onboarding **locally** for transport/driver/approval fit, not because the app is generally defective. SSoT/DiffSync was optional, not
adopted; Nornir installed as a dependency did not establish device reachability. Nautobot 3.2's versioned release notes specifically require explicit `job_kwargs`
for `create_schedule`, `enqueue_job`, `execute_job` and `run_job_for_testing`; scheduled Jobs with `kwargs=None` need recreation. Check warnings and the target
version before changing call sites. Read [upgrade and troubleshooting](upgrade-and-troubleshooting.md) for the full seam register.
````

## File: references/authority-and-modeling.md
````markdown
# Authority and modelling

## Decision model

Treat Nautobot as the record of accepted intent, not an unfiltered event store. For each object and field, name the authority, writer, evidence class, and review path before deciding where it lives.
Useful state classes are intended state, observed state, and evidence about an observation. A collector may propose an observation; it does not acquire authority to redefine intent.

Location describes physical geography and hierarchy. Tenant describes an administrative or service ownership boundary when that boundary matters. Namespace is the IPAM uniqueness boundary; it is not a
substitute for either geography or tenancy. Namespaces allow otherwise overlapping address records, and a site-scoped Namespace was a tested project solution for genuinely independent address domains,
not a universal default. Claim N-C02 is the documented model principle; the concrete split needs local justification.

## Modelling choices

Use Devices, Interfaces, Prefixes, and IP Addresses for their native meanings. A project-derived rule retained the narrowest containing Prefix mask on an address rather than defaulting every address to
`/32`; that preserves the usable routing fact but still requires validation against the local IPAM design. Do not use a host route merely to make an import convenient. Claim N-C14 is this worked
pattern, not a core Nautobot guarantee.

Use a Relationship for a durable fact between existing objects. Use a custom field for a bounded attribute whose lifecycle belongs to its existing object. Consider a custom model only when the concept
has its own identity, lifecycle, permissions, relations, and query needs. The project Wireless Link object is a worked case: native models did not adequately represent its durable semantics. It does
not prove that every radio association needs a custom model. Keep physical topology, logical service topology, and transient telemetry separate.

Keep Device Status as an approved lifecycle state. Health, freshness, signal, and reachability are observations or policy outputs; a critical observation does not silently turn an Active device into
a retired or failed lifecycle object. An explicit policy may create a review task or a controlled transition, but telemetry alone does not decide it.

Do not put secrets, raw polling payloads, high-rate time series, uncorroborated neighbour claims, or an external system's entire schema into Nautobot merely because it has an extension seam. Preserve
only the durable intent or the bounded evidence needed to govern it.

## Failure clues and acceptance

Conflicting writers, a Location used to dodge IP uniqueness, a custom field carrying an independent lifecycle, and a monitoring process overwriting Status are modelling failures. Before acceptance,
verify the object owner, write permissions, uniqueness boundary, parent Prefix/mask, relationship cardinality, lifecycle policy, and the version-specific model/API behavior actually relied on.
Claims N-C01, N-C02, and N-C14.

## Ownership is a contract, not automatically enforcement

Record each field's authority, permitted writer, evidence source, transition rule and actual enforcement hook separately. A catalog documents ownership; it does not
block an API client. In the UNC worked app, an ownership catalog supplies classes while `wc_ownership` loads it at import and CustomValidators compare stored and
incoming Device/Interface data on UI/API validation. It guards configured classes and custom-field keys on **updates**, not creation. A named writer or group may
bypass the guard; acknowledged replacement is a separate exception. Applicability also checks creation, but is disabled by default there. An unreadable catalog
returns no guarded fields and logs an error; unknown device types do not trigger applicability refusal. Direct writes that skip model validation require a separate
test. Thus a green catalog check or registered validator does not prove every write path is protected.

| Synthetic field     | State                     | Authority and writer           | Required transition evidence                             |
| ------------------- | ------------------------- | ------------------------------ | -------------------------------------------------------- |
| `service_role`      | Intent                    | Service owner; operator writer | Reviewed change; collector edit refused                  |
| `reported_serial`   | Hardware observation      | Device read; collector writer  | UI/API human edit refused; replacement exception audited |
| `monitoring_health` | Observation               | Monitoring; sync writer        | Source time retained; never changes lifecycle Status     |
| `rack_position`     | Hardware-dependent intent | Facilities; operator writer    | Applicable device type; create/update validation         |

If ownership information is absent, stale or contradictory, stop the proposed write. Inspect the *effective loaded* catalog and process restart state; compare it with
registered validators and permissions. A fail-open validator preserves availability but degrades the control, so alert on it and block automated writes until repaired.

Synthetic modeling decision: two independent sites both use `192.0.2.10` inside approved `192.0.2.0/27` Prefixes. If their address spaces are genuinely independent,
use separate Namespaces; Locations identify geography and Tenants administrative ownership, neither substitutes for IP uniqueness. Link each address to its site's
interface and retain `/27`, the narrowest containing Prefix. If one site has a more-specific approved `/28`, confirm it is the interface's intended network before
selecting that mask. Failure case: forcing `/32` to avoid a duplicate or selecting the wrong overlapping Prefix hides a routing/design conflict. A Relationship suits a
durable association between existing objects; a custom field a bounded attribute; a custom model a concept with independent identity, lifecycle and permissions.
Read [staged onboarding](staged-onboarding.md) for promotion and [API and writers](api-and-writers.md) before automating updates.

> **Learned 2026-10-05** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: nautobot/extras/management/__init__.py lines 107-170 and extras/models/roles.py line 37 in the installed source · Falsifier: a 3.2.x post_upgrade or migrate run that recreates a deleted default Role
> Default Statuses and Roles are created only by data migrations that have already run, so a deleted built-in is never recreated by `migrate` or `post_upgrade`. Treat them as shared taxonomy: a cleanup script reports candidates and stops, and recovery is from the change log ([operations cookbook](operations-cookbook.md) section 9).

> **Learned 2026-10-05** · Nautobot 3.2.3 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a fleet with a duplicated non-empty serial
> Serial may be legitimately empty (7% of units, concentrated in a few models whose SNMP returns none) but was unique whenever present (0 duplicates in 3,043). Enforce uniqueness only for non-empty values and let the identity source fill the gap later.

> **Learned 2026-10-05** · Nautobot 3.2.3 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a fleet whose device-reported names are unique and descriptive
> Do not name or key devices on SNMP sysName: one family returned a generic default on 349 units, default-pattern names repeated across sites, and 11 duplicate-name groups existed inside single sites. DNS A records named 98% of live units; 13% of in-subnet records pointed at nothing, so a dangling record is a warning, not an error.
````

## File: references/capability-extension.md
````markdown
# Capability extension

## Decision rubric

Start with an observable operator outcome and its acceptance test. Evaluate, in order: (1) Nautobot core, (2) a maintained Nautobot app, (3) an NTC library or supported integration seam, (4) a
supported custom app, Job, or API extension, (5) complementary external FOSS, and (6) a narrow custom component. At every step state why the prior option cannot meet the test; this prevents a new
framework becoming the default answer.

For every candidate assess maintenance and licence, supported Nautobot and Python versions, upgrade cadence, network reachability, source-of-truth semantics, permissions, data-model fit,
operational load, testability, rollback, and the cost of replacement. A model that fits data but cannot reach the network is not operationally fit. A tool that can collect data but overwrites intent
without ownership boundaries is not source-of-truth fit.

## Starting map, not recommendation list

Useful investigation starting points include Golden Config, Nornir, Secrets Providers, DNS Models, Design Builder, SSoT, Device Onboarding, Device Lifecycle Management, Capacity Metrics, netutils,
diffsync, schema-enforcer, pynautobot, nautobot-ansible, nornir-nautobot, ntc-templates, Netdisco, LibreNMS, OpenNMS, and lldpd. Their presence here is task-indexed awareness, not endorsement;
verify maintenance, licence, compatibility, and supported seams at the target version before selecting one.

Edit a declared source and render derived artifacts rather than editing a generated catalog. The project catalog workflow is a tested source-of-truth pattern, not a requirement of Nautobot itself.
Acceptance includes the source/derived boundary, chosen seam, permissions, upgrade test, and an operator-visible outcome. Claim N-C10 and N-C17.

## Choose by task, not by installed name

| Operator problem         | Candidate seam                                                     | Prerequisite and UNC disposition                                                                     |
| ------------------------ | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Enforce                  | Nautobot 3.x core validation/compliance; custom validator for      | Verify model validation covers every write path; UNC needed `wc_ownership` for transition-aware      |
|   model/value rules      |   transition-sensitive rule                                        |   field ownership                                                                                    |
| Backup/compliance        | Golden Config with Nornir/Secrets Providers integration            | Driver and worker path; UNC uses backup/compliance, deploy off                                       |
| DNS intent               | DNS Models plus project site/zone relationships                    | Confirm authority and zone writer; UNC installed, RPZ writer policy remains local                    |
| Repeated object design   | Design Builder or Job/API                                          | Test migrations and operator result; UNC lab design rehearsal, not new-site acceptance               |
| Source reconciliation    | SSoT/DiffSync or thin external mapper                              | Source reachability and delete/dry-run semantics; UNC did not install SSoT                           |
| Device discovery         | Device Onboarding or external site collector                       | Worker route, vendor driver and ambiguity review; UNC rejected the app for its local path            |
| Lifecycle/EOL            | Device Lifecycle Management                                        | Vendor/CVE coverage and maintained version; UNC proposed a trial, not adoption                       |
| Parsing/normalization    | netutils, ntc-templates, PyNTC                                     | Match vendor/OS and Python version; UNC used a thin netutils mapper when no suitable parser fit      |
| Independent discovery    | Netdisco, LibreNMS, OpenNMS or `lldpd`                             | Collector vantage, provenance and authority handoff; no blanket adoption                             |

At selection time open the candidate's current official docs/repository and check licence, release maintenance, Nautobot/Python matrix and target network path. An
installed Nornir dependency is not a deployed Nornir workflow, and a commercial app catalog does not prove a candidate is FOSS. Example source/render contract:
`catalog/master.yaml` includes `vendors/example/device-types.yaml` → renderer produces `catalog.yaml` → seed reads the rendered file. Modify the vendor part,
re-render, inspect the diff and run a drift check; never patch the rendered catalog. UNC implements this pattern; other deployments may have a different source.
Read [apps, Jobs and validation](apps-jobs-validation.md) for execution fit and [discovery and topology](discovery-and-topology.md) for observed edges.
````

## File: references/config-backup-compliance.md
````markdown
# Configuration backup and compliance

## Separate controls

Backup collects a recoverable representation. Compliance evaluates it against an approved policy. Deployment changes a target. Restore verification proves a backup can be used safely. These are
separate capabilities with different authorization and evidence requirements. A successful backup must not automatically authorize a push; a matching comparison must not be called a restore proof.

Redact secrets before storage, reporting, and comparison. Retain enough metadata to explain collection time, target identity, scope, and failure without placing secret-bearing configuration in a
ticket or reusable skill. Golden Config or another tool may provide collection/comparison seams, but driver support, credentials, network reachability, and target behavior remain dependencies to
verify for the installed version.

## Comparison and restoration

A project worked pattern used a keyed HMAC digest for equality comparison while avoiding plaintext retention. It can show that two values produce the same keyed digest; it is not identity,
authorization, tamper proof, or a substitute for key management. Truncation, domain separation, key rotation, leakage of low-entropy inputs, and collision tolerance are project security decisions.
Do not promote that pattern into a generic helper without a cross-project consumer and security review.

Acceptance requires a redaction review, a declared comparison scope, a known restore procedure tested in an authorized environment, and a separate deployment gate with rollback. Backup success alone,
or a hash equality result alone, is insufficient. Claim N-C09.

## Worked backup decision

Synthetic source config has interface/VLAN intent, a local credential, and a management-agent token. A redacted archive can restore the non-secret interface/VLAN
portion and prove its intended structure; it **cannot** restore authentication or the agent's enrollment by itself. Record a secret manifest (names/roles, never values),
an authorized vault/source for each omitted secret, and a restore runbook that injects them under operator control. A backup is useful only when collection identity,
source time, scope, integrity, retention and an authorized restore rehearsal are evidenced. A parseable redacted text alone is not a full disaster-recovery proof.

Normalize only semantics known safe for the device family (for example order-independent sections after proving order does not matter). Keep raw restricted evidence
under project controls, never in the skill. Compare against an approved intended config with exclusions explained; do not call a stable diff compliance if the parser
dropped a critical stanza. Golden Config provides a supported backup/compliance seam in the observed UNC app set, but driver, worker reachability and installed-version
fit still need proof. UNC kept deployment off; its safe-write pipeline is project-owned and unproven as a generic device path.

UNC's fingerprint helper uses keyed HMAC-SHA256 truncated to 16 hex digits (64 bits) for equality without disclosing the value. The key must be protected and
consistent for comparisons; key rotation changes digests. A 64-bit tag has collision risk, especially over many comparisons, and HMAC does not supply identity,
authorization or restore completeness. For a low-entropy secret, the key is the protection; plaintext hashes would invite guessing. When the key is unavailable, the
project path leaves data redacted rather than emitting plaintext. No reusable executable helper is included here. Read [apps, Jobs and validation](apps-jobs-validation.md)
for worker prerequisites and [upgrade and troubleshooting](upgrade-and-troubleshooting.md) for migration checks.
````

## File: references/data-model.md
````markdown
---
Title: Nautobot core data model
Category: skill-reference
Status: current
Authority: Installed Nautobot 3.2.3 source and its bundled documentation; the cited lines win over this summary
Scope: >-
  Modelling decisions and REST payloads for Locations and Location Types, tenancy, Platforms and network_driver, Manufacturers, Device Families and Device
  Types, Interfaces and VLAN modes, VLANs and VLAN Groups, Prefix types, IP assignment, Virtual Chassis, Modules, Cables and paths, Contacts and Teams,
  Statuses, Roles and Tags, Software Versions and Image Files
Last reviewed: 2026-10-05
Summary: Twelve verified modelling recipes for the Nautobot 3.2.3 core data model, each with the rule the model enforces, a payload, a gotcha and a source line.
---

# Nautobot core data model

Verified against: Nautobot 3.2.3 (installed source in a 3.2.3 container, and the docs bundled in the package), checked 2026-10-05.

Source paths are relative to `site-packages/`; `docs/...` is the page under `nautobot/project-static/docs/` (published at `https://archive.docs.nautobot.com/projects/core/en/v3.2.3/<same path>/`).
Payloads go to `https://nautobot.example/api/<path>` with `Authorization: Token $NAUTOBOT_TOKEN`; related objects may be given as UUID or natural-key string (see the operations cookbook, section 2).
Device Lifecycle Management is not installed; its software models are in core since 2.2.

## Summary

| Job                   | Model                       | Key rule                            | Trap                                | Section |
| --------------------- | --------------------------- | ----------------------------------- | ----------------------------------- | ------- |
| Site hierarchy        | LocationType, Location      | type tree + `nestable`              | type of a Location can never change | [1](#1-locations-and-location-types) |
| Who owns it           | Tenant, TenantGroup         | groups nest; tenant name unique     | tenant is part of Device uniqueness | [2](#2-tenancy) |
| How to talk to it     | Platform `network_driver`   | netutils maps to each library       | NAPALM driver is a separate field   | [3](#3-platforms-and-network_driver) |
| What it is            | Manufacturer, DeviceType    | `model` unique per manufacturer     | family is optional grouping only    | [4](#4-manufacturers-device-families-device-types-devices) |
| Ports                 | Interface                   | `mode` gates VLAN fields            | tagged VLANs need `mode: tagged`    | [5](#5-interfaces-modes-vlans-and-lags) |
| Layer 2               | VLAN, VLANGroup             | unique vid and name per group       | one VLAN per site, unless stretched | [6](#6-vlans-and-vlan-groups) |
| Address space         | Prefix `type`               | container / network / pool          | hierarchy is advisory, not enforced | [7](#7-prefix-types-and-namespaces) |
| Addresses on ports    | IPAddressToInterface        | many-to-many, flags per assignment  | every IP needs a parent Prefix      | [8](#8-ip-addresses-and-interface-assignment) |
| Switch stacks         | VirtualChassis              | members need `vc_position`          | interfaces are not renumbered       | [9](#9-virtual-chassis) |
| Line cards and optics | Module, ModuleBay           | installed in a bay or at a Location | never both bay and location         | [10](#10-modules-and-module-bays) |
| Physical links        | Cable                       | `Connected` status makes a path     | renaming `Connected` breaks tracing | [11](#11-cables-and-paths) |
| People and labels     | Contact, Team, Status, Role | content types gate choices          | a Status must list the model        | [12](#12-contacts-teams-statuses-roles-tags-software) |

## Contents

- [Summary](#summary)
- [1. Locations and Location Types](#1-locations-and-location-types)
- [2. Tenancy](#2-tenancy)
- [3. Platforms and network_driver](#3-platforms-and-network_driver)
- [4. Manufacturers, Device Families, Device Types, Devices](#4-manufacturers-device-families-device-types-devices)
- [5. Interfaces: modes, VLANs and LAGs](#5-interfaces-modes-vlans-and-lags)
- [6. VLANs and VLAN Groups](#6-vlans-and-vlan-groups)
- [7. Prefix types and Namespaces](#7-prefix-types-and-namespaces)
- [8. IP addresses and interface assignment](#8-ip-addresses-and-interface-assignment)
- [9. Virtual Chassis](#9-virtual-chassis)
- [10. Modules and module bays](#10-modules-and-module-bays)
- [11. Cables and paths](#11-cables-and-paths)
- [12. Contacts, Teams, Statuses, Roles, Tags, software](#12-contacts-teams-statuses-roles-tags-software)

## 1. Locations and Location Types

Decision: define a short Location Type tree first (for example Region > Site > Building); mark a type `nestable` for variable depth instead of adding parallel branches. Each type lists the content
types (devices, prefixes, VLAN groups, racks) allowed at that level.

```json
POST /api/dcim/location-types/
{"name": "Site", "parent": "Region", "nestable": false, "content_types": ["dcim.device", "ipam.prefix", "ipam.vlan", "ipam.vlangroup", "dcim.rack"]}
POST /api/dcim/locations/
{"name": "site-a", "location_type": "Site", "parent": "<region-uuid>", "status": "Active", "tenant": "<tenant-uuid>"}
```

Rules enforced: a Location's type must match its parent's type (or the type's parent); a root type's Locations have no parent; names are unique per parent (`unique_together = [["parent", "name"]]`); a
Device at a Location whose type lacks `dcim.device` fails with "Devices may not associate to locations of type".

Gotcha: a Location's `location_type` can never be changed, a type with Locations cannot change parent, and a nestable type cannot be made non-nestable while nested Locations exist. Plan the tree
before loading data. `LOCATION_LIST_DEFAULT_MAX_DEPTH` limits the default list view for deep trees.

Source: `nautobot/dcim/models/locations.py:34-48,81-101,126,218,272-333`, `nautobot/dcim/models/devices.py:755`, `nautobot/dcim/api/serializers.py:242-251`;
`docs/user-guide/core-data-model/dcim/locationtype.html`, `docs/user-guide/core-data-model/dcim/location.html`.

## 2. Tenancy

Decision: a Tenant is who the object is for (customer, programme, business unit); Tenant Groups form a tree for grouping tenants. Use Tenant, not a tag, when permissions or uniqueness should follow
ownership.

```json
POST /api/tenancy/tenant-groups/   {"name": "Customers", "parent": null}
POST /api/tenancy/tenants/         {"name": "customer-a", "tenant_group": "<group-uuid>"}
```

Gotcha: with the default `DEVICE_UNIQUENESS = "location_tenant_name"`, two Devices may share a name if their Location or Tenant differs, so a name alone does not identify a Device. Other values:
`"name"` (globally unique) and `"none"`. It is a Constance setting (Admin > Config) as well as a config key.

Source: `nautobot/tenancy/models.py:18,40-55`, `nautobot/dcim/choices.py:164-175`, `nautobot/core/settings.py:863-869`, `nautobot/dcim/models/devices.py:700-712`.

## 3. Platforms and network_driver

Decision: set `network_driver` to the netutils normalised name (Netmiko-style, for example `cisco_ios`) on every Platform; consumers read the per-library name from `network_driver_mappings`, so one
field serves Ansible, NAPALM, Netmiko, Scrapli, pyATS, ntc-templates and hier_config.

```json
POST /api/dcim/platforms/
{"name": "Cisco IOS", "manufacturer": "Cisco", "network_driver": "cisco_ios", "napalm_driver": "ios"}
```

netutils 1.18.0 maps `cisco_ios` to: `ansible` `cisco.ios.ios`, `napalm` `ios`, `netmiko` `cisco_ios`, `scrapli` `cisco_iosxe`, `pyats` `iosxe`, `ntc_templates` `cisco_ios`, `netutils_parser`
`cisco_ios`, `hier_config` `ios` (137 normalised names in all).

| Consumer                       | What it reads                                                                       |
| ------------------------------ | ----------------------------------------------------------------------------------- |
| Golden Config 3.0.7 compliance | `platform.network_driver_mappings["netutils_parser"]` to parse config sections      |
| Golden Config remediation      | `network_driver_mappings["hier_config"]`                                            |
| Golden Config Jinja path       | `jinja_path_template`, e.g. `{{obj.platform.network_driver}}.j2`                    |
| nornir-nautobot 4.4.2          | inventory sets Nornir `platform` to `platform.network_driver`; dispatcher by driver |
| Ansible `inventory` plugin     | `platforms` group names from each platform's `network_driver`                       |

Unknown or vendor-private drivers: add them with the `NETWORK_DRIVERS` setting (also editable in Admin > Config), keyed by tool:

```python
NETWORK_DRIVERS = {"netmiko": {"vendor_os": "linux"}, "netutils_parser": {"vendor_os": "linux"}}
```

Gotcha: `napalm_driver` and `napalm_args` are stored on the Platform and are not derived from `network_driver`. A driver missing from netutils returns an empty mapping silently, so Golden Config then
has no parser for that platform.

Source: `nautobot/dcim/models/devices.py:421-477`, `nautobot/dcim/utils.py:89-123`, `nautobot/core/settings.py:936-945`; `nautobot_golden_config/models.py:72,205,605`;
`nornir_nautobot/plugins/inventory/nautobot.py:29`; `nautobot-ansible` 6.3.0 `plugins/inventory/inventory.py:830-833`; `netutils.lib_mapper.NAME_TO_ALL_LIB_MAPPER` read in the container;
`docs/user-guide/core-data-model/dcim/platform.html`.

## 4. Manufacturers, Device Families, Device Types, Devices

Decision: one Device Type per orderable hardware model (`model` is unique per Manufacturer); Device Family is an optional grouping of related types; Role and Status say what a Device does and where it
is in its life.

```json
POST /api/dcim/device-types/
{"manufacturer": "Cisco", "model": "C9300-48P", "device_family": "Catalyst 9300", "u_height": 1}
POST /api/dcim/devices/
{"name": "sw1", "device_type": "<uuid>", "role": "Access Switch", "status": "Active", "location": "<site-uuid>",
 "platform": "Cisco IOS", "serial": "FOC0000X000", "software_version": "<version-uuid>"}
```

Gotcha: Device needs `device_type`, `role`, `status` and `location`. `primary_ip4` can only be set to an address already assigned to one of the device's interfaces ("is not assigned to this device").
Interface templates on the Device Type are copied only when the Device is created.

Source: `nautobot/dcim/models/devices.py:164-215` (DeviceType), `:495-652` (Device fields), `:825-848` (primary IP checks), `:916-935` (components created only when new);
`docs/user-guide/core-data-model/dcim/devicefamily.html`,
`docs/user-guide/core-data-model/dcim/devicetype.html`.

## 5. Interfaces: modes, VLANs and LAGs

Decision: `type` says what the port is (`1000base-t`, `10gbase-x-sfpp`, `ieee802.11ax`, `virtual`, `lag`, `bridge`); `mode` says how it carries VLANs: `access`, `tagged` or `tagged-all`.

```json
POST /api/dcim/interfaces/
{"device": "<uuid>", "name": "Port-channel1", "type": "lag", "status": "Active"}
POST /api/dcim/interfaces/
{"device": "<uuid>", "name": "GigabitEthernet1/0/1", "type": "1000base-t", "status": "Active", "lag": "<lag-uuid>",
 "mode": "tagged", "untagged_vlan": "<vlan-uuid>", "tagged_vlans": ["<vlan-uuid>", "<vlan-uuid>"], "mac_address": "00:00:5E:00:53:01"}
```

| Rule                                                                | Enforced by          |
| ------------------------------------------------------------------- | -------------------- |
| `untagged_vlan` needs some `mode`                                   | model `clean()`      |
| `tagged_vlans` need `mode: tagged`; clear them before changing mode | REST serializer      |
| A VLAN must be global or at the device's Location or an ancestor    | serializer and model |
| LAG members on the same device, or the same Virtual Chassis         | model `clean()`      |
| Only physical interfaces take cables, `port_type`, `duplex`         | model `clean()`      |
| `speed` is Kbps; not valid on LAG, virtual or wireless types        | model `clean()`      |

Gotcha: `tagged-all` carries every VLAN, so do not also list `tagged_vlans`. An Interface belongs to a Device or a Module, never both.

Source: `nautobot/dcim/choices.py:778-850,1147-1156`, `nautobot/dcim/models/device_components.py:1037-1074,1197-1440`, `nautobot/dcim/api/serializers.py:712-768`;
`docs/user-guide/core-data-model/dcim/interface.html`.

## 6. VLANs and VLAN Groups

Decision: per the docs, model a distinct VLAN per Location when sites reuse the same VID for the same purpose; one VLAN linked to several Locations only for a genuinely stretched layer 2. A VLAN Group
(optionally at one Location) enforces unique VID and name and can constrain `range`.

```json
POST /api/ipam/vlan-groups/  {"name": "site-a", "location": "<site-uuid>", "range": "1-999"}
POST /api/ipam/vlans/        {"vid": 30, "name": "wifi", "status": "Active", "vlan_group": "<group-uuid>", "location": "<site-uuid>"}
POST /api/ipam/vlan-location-assignments/  {"vlan": "<vlan-uuid>", "location": "<other-site-uuid>"}
GET  /api/ipam/vlan-groups/<uuid>/available-vlans/      (POST with name and status creates the next free VID)
```

Gotcha: `locations` is read-only on the VLAN serializer; `location` is a write-only shortcut for one Location, and reading `vlan.location` raises when there are several. A VLAN Group's Location type
must allow `ipam.vlangroup`.

Source: `nautobot/ipam/models.py:1049-1063,2270-2321,2354,2478-2483`, `nautobot/ipam/api/serializers.py:118-140`; `docs/user-guide/core-data-model/ipam/vlan.html`,
`docs/user-guide/core-data-model/ipam/vlangroup.html`.

## 7. Prefix types and Namespaces

Decision: `container` for aggregates that group subnets, `network` (default) for real subnets with hosts, `pool` for ranges inside a network where every address is usable. Prefixes are unique per
Namespace; the default Namespace is `Global`.

```json
POST /api/ipam/prefixes/  {"prefix": "198.51.100.0/24", "type": "container", "status": "Active", "namespace": "Global"}
POST /api/ipam/prefixes/  {"prefix": "198.51.100.0/26", "type": "network", "status": "Active", "location": "<site-uuid>"}
```

| Type      | First and last IPv4 address usable | Utilisation counts |
| --------- | ---------------------------------- | ------------------ |
| container | no                                 | child prefixes     |
| network   | no                                 | IP addresses       |
| pool      | yes                                | IP addresses       |

Gotcha: "Nautobot does not strictly enforce this hierarchy": a network inside a network is accepted. CSV import ignores `vrfs` and `locations` columns; use `prefix-location-assignments` or the VRF
assignment endpoints afterwards.

Source: `nautobot/ipam/choices.py:31-40`, `nautobot/ipam/models.py:189-194,643-662,1622-1652`, `nautobot/ipam/api/serializers.py:198-221`; `docs/user-guide/core-data-model/ipam/prefix.html`.

## 8. IP addresses and interface assignment

Decision: an IP Address lives in a Namespace under its closest parent Prefix; attach it to interfaces through `ip-address-to-interface`, which is many-to-many and carries per-assignment flags.

```json
POST /api/ipam/ip-addresses/            {"address": "198.51.100.10/26", "status": "Active", "type": "host", "namespace": "Global"}
POST /api/ipam/ip-address-to-interface/ {"ip_address": "<ip-uuid>", "interface": "<interface-uuid>", "is_primary": true}
PATCH /api/dcim/devices/<uuid>/         {"primary_ip4": "<ip-uuid>"}
```

IP `type`: `host`, `dhcp`, `slaac`. Assignment flags: `is_source`, `is_destination`, `is_default`, `is_preferred`, `is_primary`, `is_secondary`, `is_standby`. Use `vm_interface` instead of `interface`
for virtual machines.

Gotcha: every IP needs a parent Prefix; without one the create fails with "No suitable parent Prefix ... exists in Namespace". Create needs `namespace` or `parent`. Keep the address mask equal to the
subnet's mask; Nautobot stores what it is given.

Source: `nautobot/ipam/models.py:115-132,1684,1715,1823-1842,1913-1950`, `nautobot/ipam/choices.py:93-101`, `nautobot/ipam/api/serializers.py:315-336`;
`docs/user-guide/core-data-model/ipam/ipaddress.html`.

## 9. Virtual Chassis

Decision: use a Virtual Chassis when several boxes share one control plane (a switch stack); use a Device Redundancy Group when each keeps its own; use modules for a chassis with line cards.

```json
POST /api/dcim/virtual-chassis/  {"name": "stack-1", "domain": ""}
PATCH /api/dcim/devices/<uuid>/  {"virtual_chassis": "<vc-uuid>", "vc_position": 1, "vc_priority": 15}
PATCH /api/dcim/virtual-chassis/<vc-uuid>/  {"master": "<device-uuid>"}
```

Gotcha: a member needs `vc_position` (unique within the chassis); the master must already be a member. Interfaces are not renumbered when a device joins: member 3 still shows `.../1/0/x` until
bulk-renamed. A LAG may span members of one Virtual Chassis.

Source: `nautobot/dcim/models/devices.py:651-652,712,879-881,1248-1265`; `docs/user-guide/core-data-model/dcim/virtualchassis.html`.

## 10. Modules and module bays

Decision: model removable hardware (line cards, supervisors, transceivers) as Modules in Module Bays; a Module Type's component templates create its interfaces, which may use the bay `position` in
their names.

```json
POST /api/dcim/module-bays/  {"parent_device": "<device-uuid>", "name": "Slot 1", "position": "1"}
POST /api/dcim/modules/      {"module_type": "<type-uuid>", "parent_module_bay": "<bay-uuid>", "status": "Active", "serial": "ABC123"}
POST /api/dcim/modules/      {"module_type": "<type-uuid>", "location": "<store-uuid>", "status": "Active"}
```

Gotcha: a Module has either `parent_module_bay` (installed) or `location` (spare in stock), never both. A bay assigned a Module Family accepts only Module Types of that family.  A Module Bay has
`parent_device` or `parent_module`.

Source: `nautobot/dcim/models/devices.py:1981-2022,2120-2138`, `nautobot/dcim/models/device_components.py:1985-1999`; `docs/user-guide/core-data-model/dcim/module.html`,
`docs/user-guide/core-data-model/dcim/modulebay.html`.

## 11. Cables and paths

Decision: a Cable joins two physical terminations (interface, front/rear port, console, power, circuit termination); Nautobot traces end-to-end paths through patch panels and circuits from cables
whose status is `Connected`.

```json
POST /api/dcim/cables/
{"termination_a_type": "dcim.interface", "termination_a_id": "<uuid>", "termination_b_type": "dcim.interface", "termination_b_id": "<uuid>",
 "status": "Connected", "type": "cat6"}
POST /api/dcim/cables/   (3.2 shape, also for breakout cables)
{"terminations": {"a1": {"object_type": "dcim.interface", "id": "<uuid>"}, "b1": {"object_type": "dcim.interface", "id": "<uuid>"}}, "status": "Connected"}
```

Gotcha: a path is reachable only if every cable on it is `Connected`; do not rename or delete that Status. Virtual and wireless interfaces cannot be cabled. After bulk imports, `nautobot-server
trace_paths` rebuilds missing paths (`post_upgrade` runs it).

Source: `nautobot/dcim/models/cables.py:471`, `nautobot/dcim/api/serializers.py:896-1110`, `nautobot/core/management/commands/post_upgrade.py:119`; `docs/user-guide/core-data-model/dcim/cable.html`.

## 12. Contacts, Teams, Statuses, Roles, Tags, software

Decision: attach people with Contact or Team associations rather than free-text fields; keep Statuses for lifecycle and Roles for function; Tags for cross-cutting labels only.

```json
POST /api/extras/contact-associations/
{"contact": "<contact-uuid>", "associated_object_type": "dcim.location", "associated_object_id": "<uuid>", "role": "<role-uuid>", "status": "Active"}
POST /api/extras/statuses/  {"name": "Staged", "color": "2196f3", "content_types": ["dcim.device"]}
POST /api/extras/roles/     {"name": "Access Switch", "color": "4caf50", "content_types": ["dcim.device"]}
POST /api/dcim/software-versions/  {"platform": "Cisco IOS", "version": "17.9.4", "status": "Active", "long_term_support": true}
POST /api/dcim/software-image-files/  {"software_version": "<uuid>", "image_file_name": "image.bin", "status": "Active"}
```

Gotcha: a Status, Role or Tag must list the model's content type or it is rejected for that model. A Contact Association takes exactly one of `contact` or `team`, with a role and status.
 Software Image File also takes `image_file_checksum`, `hashing_algorithm`, `image_file_size`, `default_image` and `external_integration`.

Source: `nautobot/extras/models/contacts.py:49-125`, `nautobot/extras/models/statuses.py:23-46`, `nautobot/extras/models/roles.py:21`, `nautobot/extras/models/tags.py:32,53`,
`nautobot/dcim/models/devices.py:1401-1433,1500-1514`; `docs/user-guide/core-data-model/extras/contact.html`, `docs/user-guide/core-data-model/dcim/softwareversion.html`,
`docs/user-guide/core-data-model/dcim/softwareimagefile.html`.
````

## File: references/discovery-and-topology.md
````markdown
# Discovery and topology

## Evidence is not topology authority

Represent an observation with source, capture time, vantage point, endpoint identities, confidence, parser or collector version where material, conflict state, and freshness. The same link seen from
two ends is stronger evidence than a single assertion, but it is still observed state until a governed review promotes it.

| Source              | Useful for                                 | Cannot prove alone                                  |
| ------------------- | ------------------------------------------ | --------------------------------------------------- |
| LLDP/CDP            | A neighbour report from a specific vantage | An end-to-end physical path or both ends' agreement |
| FDB                 | A learned MAC on a port                    | Direct attachment or a stable cable                 |
| ARP/neighbour state | An IP/MAC sighting                         | A physical link or current ownership                |
| DHCP                | A recent lease association                 | Present topology or device identity                 |
| Device API or SSH   | A vendor-owned association                 | Cross-device physical truth                         |
| Inventory           | Approved intended arrangement              | Current observation                                 |

SNMP, DNS, and CLI evidence fit the same contract: state what was observed and from where, rather than turning a parser result into a permanent edge. Parallel links, asymmetric reports, and an
identity collision must remain explicit candidates, not collapsed into one attractive graph edge.

## Promotion and modelling

Keep physical topology, logical service topology, and monitoring association separate. A conflicting observation can indicate stale state, a one-sided report, a collector fault, a changed path, or a
real intent drift. Investigate those possibilities before changing accepted inventory. A custom Relationship is suitable for a durable relation between existing objects; the project's Wireless Link
object is a worked example where the native model was insufficient, not a product-wide prescription. Claim N-C15.

The project Step 9 correlator and rendering slice remain proposed architecture only. An installed model, a discovery feed, or a drawn graph does not prove reconciliation is implemented. Acceptance is
a traceable observation, conflict handling, reviewer decision, and separately recorded intended edge. Claim N-C07.

## Conflict and Wireless Link worked case

Synthetic observations at 10:00 UTC: switch `sw-a` reports LLDP peer `ap-1` on port 7; its FDB learns `ap-1` on port 8 at 09:52; an SMC ARP entry maps the
same IP to a different MAC at 09:40. Do not select port 7 by protocol prestige or rewrite a Cable. Verify endpoint identity and collection clocks; repeat
fresh observations from both ends; check whether port 8 is a trunk/bridge and whether ARP is stale. Store three candidate edges with source, vantage, timestamp
and conflict flag. Promotion to accepted intent requires a reviewed explanation and post-change consistency, not a majority vote.

UNC's implemented Wireless Link custom model represents a durable radio edge with A/Z Device endpoints, optional interfaces, band, planned channel, reported channel,
frequency, per-end and derived width, Status and source. Its validation rejects self-links, interfaces owned by the wrong Device, incompatible widths/channels and
duplicate endpoint pairs in the same band. These are **UNC model semantics**, not built-in Nautobot Wireless Link fields; read its model/design before copying them.
Native Cable/Interface models fit physical terminations, and a Relationship may suffice for a simple durable link between existing objects. A
Wireless Link-like model is justified only if the edge itself needs identity, status/lifecycle, endpoint relations and attributes that cannot be represented honestly by
those native objects. A live association-table sighting is **observation**, not an accepted Wireless Link. The UNC feed/reconciliation and Step 9 collector/rendering
remain proposed. A central collector unable to reach site protocols must use a justified site vantage; SNMP/ICMP and TCP forwarding are not interchangeable.
Vendor OIDs, commands and RF interpretation belong to equipment/transport expertise. For a graph consumer read OpenWISP
[topology and FOSS](../../skill-openwisp/references/topology-and-foss.md) only when the request crosses into presentation.

> **Learned 2026-10-05** · Nautobot 3.2.3 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a multi-site estate whose management addresses are globally unique
> Expect overlapping address space in multi-site estates: 773 of 1,309 live management addresses appeared at more than one site, and the site router's own address at all 43. Model one Namespace (or VRF) per routing domain and never key on an address. Exclude the sweeping host itself from candidates.

> **Learned 2026-10-05** · Nautobot 3.2.3 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a DHCP lease that proves a unit is currently present
> DHCP leases are not liveness: 275 of 486 leased candidates were in state free, and every cross-site duplicate MAC came from lease-only rows. Drop lease-only rows (no ARP, no ping) before duplicate detection, and keep an explicit bucket for hosts whose banner or OUI matches no known signature (14% of hosts stayed unidentified).
````

## File: references/evolution-and-write-back.md
````markdown
# Evolution and write-back

## Standing write-back contract

This skill is a cross-project source of Nautobot knowledge. Invoking it carries the obligation, in any project, to write back what the engagement taught: a new fact,
a version change in behaviour, a fix, a root cause, or a correction. Write it before the session ends when the active task permits edits to this skill's canonical
source; skill use alone never authorizes a live-platform action. Read the edited file back in the same session: a scratchpad note or a timestamp is not proof.

Classify every engagement at closeout, one sentence in the reply:

| Class                        | Action                                                                                          |
| ---------------------------- | ----------------------------------------------------------------------------------------------- |
| `no_new_reusable_learning`   | Nothing to write; say so                                                                        |
| `verified_reusable_update`   | Add a Learned entry to the focused reference and one CHANGELOG line under `## Unreleased`       |
| `reusable_candidate`         | Same, with evidence `UNVERIFIED` and a falsifier that would settle it                           |
| `contradicts_existing_claim` | Add a Disputed entry beside the old text; never delete or silently rewrite it                   |
| `project_only`               | Write it in the engaging project's docs, not here                                               |
| `equipment_only`             | Write it in the equipment skill (for example skill-cambium or skill-smc), not here              |

## Entry format

Put the entry in the reference a future reader would open for that task (the routing table in `SKILL.md`), at the end of the relevant section. Two lines minimum:

```text
> **Learned 2026-10-05** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: <doc URL, or file:line in the installed source> · Falsifier: <observation that would prove it wrong>
> <the fact, generic: no customer names, hostnames, addresses, keys or credentials>
```

A contradiction uses `> **Disputed YYYY-MM-DD**` with the same fields plus `Conflicts: <claim ID or section>`. The evidence label is one of `VERIFIED_PRIMARY`,
`VERIFIED_SECONDARY`, `UNVERIFIED` or `USER_STATED`. The CHANGELOG line names the reference file and the same date. `tests/test_package_contract.py` fails on a
malformed entry, or on an entry with no matching CHANGELOG line, so a write-back is checked the next time anyone runs the tests.

If this skill's source cannot be written (read-only path, no authorization), put the same entry in the engaging project's governed docs under a heading naming this
skill, and link it from that project's index; the next engagement with write access promotes it.

## Release reconciliation

Learned entries are cheap on purpose. At a release, the maintainer: promotes each still-valid Learned entry into the reference prose; adds a `sources.yaml` claim
only when the fact is load-bearing (a decision depends on it); adds or updates a `compatibility.yaml` row when the evidence came from a new version or a live rung;
adds a scenario when a no-skill agent would plausibly get the fact wrong; moves `## Unreleased` under the new version; and reruns the tests.

## Promoting a project script

Code grows in the projects that use this skill and moves here when it has earned it. A project keeps a register of its scripts (UNC:
`scripts/promotion-register.json`, enforced by its governance check) marking each `project_only`, `candidate` with what it still needs, or `promoted`.
Promote when the script's behaviour holds for any deployment of the platform, it imports nothing project-specific, and its engine can be pure or
read-only with I/O injected by the caller. Then: the engine goes to `scripts/` with offline tests in `tests/test_helpers.py` (stdlib only, enforced by
the contract test); the project script becomes a thin wrapper that keeps its CLI and defaults; before-and-after outputs of its read-only or dry-run
modes must match; and the CHANGELOG names the source project and script. A write path is tested offline with recorded responses and live only on a
disposable instance.

## Keeping it current

Each `operations-cookbook.md` names the version it was verified against. When the installed version changes, re-verify every section whose syntax the task relies on,
then update that line and `compatibility.yaml`; until then, treat the cookbook as the old version's syntax. A single success is a candidate, not a rule: label it
`UNVERIFIED` until a second environment, the official documentation or the installed source agrees. Claim N-C12.
````

## File: references/integrations.md
````markdown
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
````

## File: references/lifecycle-and-replacement.md
````markdown
# Lifecycle and replacement

## Decision model

Separate the logical service position from the physical asset that currently occupies it. A Device record may represent one or the other only when that choice is explicit; otherwise model the
relationship and replacement history so a hardware swap does not accidentally become a new service, or erase the history of the old asset.

Plan the replacement before changing status: identify the outgoing and incoming assets, their authoritative identities, custody state, location, service relationship, monitoring identity, dependent
interfaces/IPs, and the acknowledgement that makes cutover complete. A physical move to warehouse or another site is a custody/location question, not proof of lifecycle retirement.

## Identity and audit

Preserve a stable monitoring or consumer identity only when the system's policy says it represents the logical service rather than the physical hardware. Record a replacement mapping and audit trail
instead of reusing a hardware identifier. Capture who performed or approved the handoff through the project's authenticated actor control. A QR label is an efficient lookup aid, not authentication;
a scanned label alone cannot authorize custody or lifecycle change.

## Common mistakes and acceptance

Common mistakes are overwriting the old serial, using a label as proof of actor identity, retaining stale links without an acknowledgement, and declaring a warehouse move a replacement. Acceptance is
an auditable chain from outgoing asset through custody and replacement decision to incoming asset, with downstream service/monitoring behavior verified and a rollback or exception path documented.
Claim N-C06.

## Synthetic replacement walk-through

Service position `POP-EDGE-1` is currently occupied by asset `A-17` (serial `SYN-17`); asset `A-42` (`SYN-42`) is the approved spare. First verify which
record represents the logical position: if the Device is the physical asset, preserve both Device records and use a Relationship/custom model for occupancy history;
if the Device is the logical position, preserve its logical identity but record old/new hardware identities in a separate auditable asset or replacement record. Never
overwrite `SYN-17` and thereby erase who owned the former unit.

Dry-run the transition: identify actor and custody acknowledgement; capture outgoing interface/IP assignments, circuit/service links and monitoring identity; mark
which references follow the service position and which follow the physical unit. On authorized cutover, detach or retire old physical links, attach the new unit,
validate address uniqueness and management reachability, then verify the monitoring mapping still points to the intended logical service **only if continuity is the
approved identity policy**. Record both asset identities and timestamps. A QR label locates `A-42`; it does not prove who accepted custody. If the incoming unit is
unreachable or monitoring binds to the wrong history, hold the replacement in exception state, restore the old linkage where safe, and retain both attempted and
rollback audit entries. Acceptance requires physical custody, logical service continuity, correct IP/interface and monitoring link, and an operator-visible result.
For a cross-platform monitoring identity, read OpenWISP [identity and registration](../../skill-openwisp/references/identity-and-registration.md) only when that link
actually changes.
````

## File: references/operations-and-recovery.md
````markdown
---
Title: Nautobot operations and recovery
Category: skill-reference
Status: current
Authority: Installed Nautobot 3.2.3 source, its bundled documentation, and the PostgreSQL 16 client tools; the cited lines win over this summary
Scope: >-
  Backing up and restoring the Nautobot database and file stores, restore rehearsal, health checks, Prometheus metrics, logging, performance, security
  settings, authentication backends, tokens, and Celery worker and scheduler inspection
Last reviewed: 2026-10-05
Summary: Nine verified operations recipes for running and recovering Nautobot 3.2.3, each with a gotcha and a source line; restore ordering is labelled as practice where Nautobot documents none.
---

# Nautobot operations and recovery

Verified against: Nautobot 3.2.3 (installed source and bundled docs), `django-health-check` 3.20.8, `django-prometheus` 2.5.0, Celery 5.6.3, PostgreSQL 16.15 client tools, checked 2026-10-05.

Source paths are relative to `site-packages/`; `docs/...` is the page under `nautobot/project-static/docs/`. Commands run inside the Nautobot or database container (`docker exec <container> ...`) or
the Nautobot venv. Placeholders: `https://nautobot.example`, `$NAUTOBOT_TOKEN`, `$NAUTOBOT_DB_NAME`.

## Summary

| Job                   | Use                              | Key syntax                              | Trap                                                               | Section |
| --------------------- | -------------------------------- | --------------------------------------- | ------------------------------------------------------------------ | ------- |
| Back up               | `pg_dump -Fc` + file stores      | `pg_dump -Fc -f nautobot.dump`          | `dumpdata` is a migration tool, not a backup                       | [1](#1-backup) |
| Restore               | `pg_restore` into an empty DB    | `pg_restore --no-owner -d ...`          | same Nautobot and app versions first                               | [2](#2-restore-and-rehearsal) |
| Is it up              | `/health/`, `health_check`       | `curl .../health/?format=json`          | HTTP check and CLI check differ                                    | [3](#3-health-checks) |
| Metrics               | `METRICS_ENABLED`                | `/metrics/`                             | guide says `METRICS_AUTHENTICATION`; it is `METRICS_AUTHENTICATED` | [4](#4-prometheus-metrics) |
| Logs                  | `LOGGING` dict                   | `"nautobot"` logger                     | worker stdout is captured at WARNING                               | [5](#5-logging) |
| Slow pages or Jobs    | depth, page size, ORM hints      | `select_related`, `prefetch_related`    | N+1 in Jobs is invisible until scale                               | [6](#6-performance) |
| Lock it down          | core security settings           | `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` | `EXEMPT_VIEW_PERMISSIONS` opens to anonymous                       | [7](#7-security-settings) |
| Sign-in and tokens    | SSO, LDAP, Token                 | `AUTHENTICATION_BACKENDS`               | `ObjectPermissionBackend` must stay                                | [8](#8-authentication-and-tokens) |
| Workers and scheduler | `nautobot-server celery inspect` | `inspect ping --destination ...`        | no reply is not proof of no worker                                 | [9](#9-workers-and-scheduler) |

## Contents

- [Summary](#summary)
- [1. Backup](#1-backup)
- [2. Restore and rehearsal](#2-restore-and-rehearsal)
- [3. Health checks](#3-health-checks)
- [4. Prometheus metrics](#4-prometheus-metrics)
- [5. Logging](#5-logging)
- [6. Performance](#6-performance)
- [7. Security settings](#7-security-settings)
- [8. Authentication and tokens](#8-authentication-and-tokens)
- [9. Workers and scheduler](#9-workers-and-scheduler)

## 1. Backup

Decision: the database is the system of record; back it up with PostgreSQL's own tools. Then copy the file stores that live outside it.

```bash
# database: custom format, compressed, restorable selectively and in parallel
pg_dump -Fc -h "$DB_HOST" -U "$DB_USER" -d "$NAUTOBOT_DB_NAME" -f "nautobot-$(date +%Y%m%d_%H%M).dump"
pg_restore --list nautobot-*.dump > /dev/null && echo "dump readable"
# file stores (defaults under NAUTOBOT_ROOT, normally /opt/nautobot)
tar -czf nautobot-files-$(date +%Y%m%d_%H%M).tgz -C "$NAUTOBOT_ROOT" media jobs nautobot_config.py
```

| Store                     | Default                                      | Back up?                                                          |
| ------------------------- | -------------------------------------------- | ----------------------------------------------------------------- |
| PostgreSQL database       | `NAUTOBOT_DB_NAME` (`nautobot`)              | yes: all objects, change log, Job results, Job input/output files |
| `MEDIA_ROOT`              | `$NAUTOBOT_ROOT/media`                       | yes: image attachments and other uploads (`FileSystemStorage`)    |
| `JOBS_ROOT`               | `$NAUTOBOT_ROOT/jobs` (`NAUTOBOT_JOBS_ROOT`) | yes, unless the Jobs there are deployed from version control      |
| `GIT_ROOT`                | `$NAUTOBOT_ROOT/git` (`NAUTOBOT_GIT_ROOT`)   | optional: rebuilt by re-syncing each Git repository               |
| `STATIC_ROOT`             | `$NAUTOBOT_ROOT/static`                      | no: rebuilt by `collectstatic` (`post_upgrade` runs it)           |
| `nautobot_config.py`, env | config path                                  | yes, without secrets in clear text; keep `SECRET_KEY` with it     |
| Redis                     | cache and Celery broker                      | no: transient                                                     |

Gotcha: Job input and output files use `db_file_storage` (the `nautobotjobfiles` storage), so they are in the database dump, not in `MEDIA_ROOT`. `nautobot-server dumpdata` is documented for moving
between PostgreSQL and MySQL (with `--exclude auth.permission`, and warnings against `--natural-primary` and `--natural-foreign`); it is slow, large, and not a substitute for `pg_dump`. Nautobot's own
backup page only refers to the PostgreSQL and MySQL manuals.

Source: `nautobot/core/settings.py:54,137,150,307-321,618,771`; `docs/user-guide/administration/upgrading/database-backup.html`,
`docs/user-guide/administration/migration/migrating-from-postgresql.html`; `pg_dump --help`, `pg_restore --help` (PostgreSQL 16.15).

## 2. Restore and rehearsal

Decision: restore onto the same Nautobot version and the same app versions that wrote the dump, into an empty database, with web, worker and scheduler stopped. Rehearse on a scratch host on a
schedule; a backup never restored is unproven.

```bash
# 1. stop web, worker, scheduler; keep postgres and redis running
# 2. recreate an empty database owned by the Nautobot role
dropdb --if-exists "$NAUTOBOT_DB_NAME" && createdb -O "$DB_USER" "$NAUTOBOT_DB_NAME"
# 3. restore
pg_restore --no-owner --exit-on-error -j 4 -d "$NAUTOBOT_DB_NAME" nautobot-YYYYMMDD_hhmm.dump
# 4. file stores
tar -xzf nautobot-files-YYYYMMDD_hhmm.tgz -C "$NAUTOBOT_ROOT"
# 5. bring the schema to the running code and rebuild derived state
nautobot-server showmigrations | grep '\[ \]'      # anything unapplied?
nautobot-server post_upgrade                       # migrate, trace_paths, collectstatic, stale content types, caches
# 6. verify, then start web, worker, scheduler
nautobot-server validate_models
nautobot-server health_check
```

Rehearsal checks (practice, not a Nautobot procedure): object counts per key model match the source (`GET /api/dcim/devices/?limit=1` `count`); the latest change-log entry is the expected time; a Git
repository re-syncs; one read-only Job runs to `SUCCESS`; an API token from the source still authenticates.

Gotcha: restoring a dump from a newer Nautobot or app version into older code fails or leaves unknown tables; upgrade the code first. `pg_restore -1` (single transaction) cannot be combined with `-j`.
Scheduled Jobs resume as soon as the scheduler starts, so disable them on a rehearsal copy that can reach production devices.

Source: `nautobot/core/management/commands/post_upgrade.py:101-158`; `nautobot-server help` (lists `validate_models`, `health_check`, `showmigrations`); `pg_restore --help` and its refusal "cannot
specify both --single-transaction and multiple jobs" (PostgreSQL 16.15). The step order is UNVERIFIED as a Nautobot-documented procedure; it follows the commands' documented effects.

## 3. Health checks

Decision: probe each component separately: web over HTTP, the app's dependencies with the CLI, workers with Celery ping, beat with its heartbeat file.

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://nautobot.example/health/          # 200 healthy, 500 any check failed
curl -s "https://nautobot.example/health/?format=json"                            # per-check detail
nautobot-server health_check                                                       # exit 0 when healthy; -s/--subset to narrow
nautobot-server celery inspect ping --destination celery@$HOSTNAME                 # worker liveness
[ $(find "$NAUTOBOT_CELERY_BEAT_HEARTBEAT_FILE" -mmin -0.1 | wc -l) -eq 1 ] || false   # beat liveness
pg_isready; redis-cli ping
```

`/health/` passes when the server runs, reaches the database, has applied all migrations, reaches Redis, can write to storage, and is not too busy to answer. `health_check` checks the same
dependencies but not the web server. Worker file probes: set `CELERY_HEALTH_PROBES_AS_FILES = True` with `CELERY_WORKER_HEARTBEAT_FILE` and `CELERY_WORKER_READINESS_FILE`.

Gotcha: `/health/` returning 200 says nothing about workers; Jobs can sit `PENDING` with a healthy web tier. `redis-cli ping` can answer before Redis has loaded its data.

Source: `nautobot/core/urls.py:86`, `health_check/views.py:88-110`, `health_check/urls.py`, `nautobot/extras/health_checks.py:19-126`, `nautobot/core/settings.py:669-674,1083-1099`; `nautobot-server
help health_check`; `docs/user-guide/administration/guides/health-checks.html`.

## 4. Prometheus metrics

Decision: enable metrics on the web tier for request, database and cache figures; worker Job counters come from the worker processes.

```python
# nautobot_config.py (or env NAUTOBOT_METRICS_ENABLED / NAUTOBOT_METRICS_AUTHENTICATED)
METRICS_ENABLED = True
METRICS_AUTHENTICATED = True              # require login or API token on /metrics/
METRICS_DISABLED_APPS = []                # app names whose custom metrics to skip
CELERY_WORKER_PROMETHEUS_PORTS = [8080]   # worker metrics HTTP port; a range when several workers share a host
```

```bash
curl -s -H "Authorization: Token $NAUTOBOT_TOKEN" https://nautobot.example/metrics/ | grep -E '^nautobot_|^health_check_'
```

Nautobot-specific series: `health_check_database_info`, `health_check_redis_backend_info`, `nautobot_app_metrics_processing_ms` (web); `nautobot_worker_started_jobs`, `nautobot_worker_finished_jobs`,
`nautobot_worker_exception_jobs`, `nautobot_worker_singleton_conflict` (worker), plus django-prometheus request, model, database and cache series.

Gotcha: the setting is `METRICS_AUTHENTICATED` (settings reference and code); the Prometheus guide page names it `METRICS_AUTHENTICATION`, which does nothing. With the default settings file,
`METRICS_ENABLED` also swaps the database and cache backends to the `django_prometheus` ones; a custom `DATABASES` or `CACHES` must do that itself. Multi-process uWSGI needs `prometheus_multiproc_dir`
and cleanup of stale files.

Source: `nautobot/core/settings.py:176-181,516-518,1059-1063,1154`, `nautobot/core/urls.py:126-132`, `nautobot/core/views/__init__.py:731-767`;
`docs/user-guide/administration/configuration/settings.html` (METRICS_AUTHENTICATED), `docs/user-guide/administration/guides/prometheus-metrics.html`.

## 5. Logging

Decision: define `LOGGING` in `nautobot_config.py` as a standard Django dict; Nautobot's own loggers are under `nautobot`. Job logs are stored in the database per Job result and do not depend on this.

```python
LOGGING = {
    "version": 1, "disable_existing_loggers": False,
    "formatters": {"normal": {"format": "%(asctime)s %(levelname)-7s %(name)s: %(message)s"}},
    "handlers": {"console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "normal"}},
    "loggers": {"django": {"handlers": ["console"], "level": "INFO"},
                "nautobot": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO"}},
}
# structured JSON logs:
# from nautobot.core.settings_funcs import setup_structlog_logging
# setup_structlog_logging(LOGGING, INSTALLED_APPS, MIDDLEWARE, log_level="INFO", debug_db=False, plain_format=False)
```

Gotcha: Celery redirects worker stdout and stderr into logging at `WARNING` (`CELERY_WORKER_REDIRECT_STDOUTS_LEVEL`), so `print()` in a Job shows as a warning in worker logs and not at all in the Job
result; use `self.logger`. `SANITIZER_PATTERNS` masks `username`/`password`/`secret` values in stored tracebacks, exception messages and the Job console log, not in ordinary `self.logger` lines.

Source: `nautobot/core/templates/nautobot_config.py.j2:140-190`, `nautobot/core/settings.py:297-302,1129-1133`, `nautobot/core/celery/backends.py:57,92`, `nautobot/extras/jobs_console_log.py:45`;
`docs/user-guide/administration/configuration/settings.html` (LOGGING).

## 6. Performance

Decision: fix the query shape before adding hardware: ask for less (`depth`, `limit`, field-scoped GraphQL), fetch related rows in bulk, and size workers to the Job mix.

| Lever            | Setting or syntax                                                            | Note                                                       |
| ---------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------- |
| REST nesting     | `?depth=0` (default) to `10`                                                 | each level multiplies serialisation                        |
| Page size        | `?limit=`; `MAX_PAGE_SIZE` (1000), `PAGINATE_COUNT` (50)                     | `MAX_PAGE_SIZE = 0` lets one request fetch everything      |
| M2M in REST      | `?exclude_m2m=true` (default in 3.x)                                         | include only when needed                                   |
| ORM in Jobs      | `.select_related("location", "platform")`, `.prefetch_related("interfaces")` | one query per relation, not per row                        |
| N+1 tests        | `AssertNoRepeatedQueries(self, threshold=10)`                                | from `nautobot.apps.testing`                               |
| Large list views | `LOCATION_LIST_DEFAULT_MAX_DEPTH`, `PREFIX_LIST_DEFAULT_MAX_DEPTH`           | Constance settings                                         |
| Cache            | `CACHES["default"]` django-redis, Redis DB 1, `TIMEOUT` 300                  | `CONTENT_TYPE_CACHE_TIMEOUT` defaults to 0 (off)           |
| Workers          | `nautobot-server celery worker --queues <q> --concurrency N`                 | raise for I/O-bound Jobs; separate queues for long Jobs    |
| Prefetch         | `CELERY_WORKER_PREFETCH_MULTIPLIER` (4)                                      | lower to 1 for long Jobs so one worker does not hoard them |
| Job limits       | `CELERY_TASK_SOFT_TIME_LIMIT` 300 s, `CELERY_TASK_TIME_LIMIT` 600 s          | per-Job overrides `soft_time_limit`, `time_limit`          |

Gotcha: GraphQL has no query cost or depth limiter in 3.2.3 (none found in `nautobot/core/graphql/`); a deep nested query is bounded only by the request timeout and the per-field optimiser
(`graphene-django-optimizer`). Use saved queries and review them.

Source: `nautobot/core/settings.py:1059-1076,1126,1140-1146`, `nautobot/core/graphql/generators.py:7,109`, `nautobot/core/api/serializers.py:55-120`;
`docs/user-guide/administration/configuration/settings.html` (MAX_PAGE_SIZE), `docs/user-guide/administration/guides/celery-queues.html`, `docs/development/apps/api/testing.html`.

## 7. Security settings

Decision: set these explicitly in production; Nautobot's built-in defaults are permissive or empty.

| Setting                                                     | 3.2.3 default                         | Set to                                                                                |
| ----------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------- |
| `SECRET_KEY` (`NAUTOBOT_SECRET_KEY`)                        | `""`                                  | 50+ random characters (`nautobot-server generate_secret_key`); same on every web node |
| `ALLOWED_HOSTS` (`NAUTOBOT_ALLOWED_HOSTS`, space-separated) | `[]`                                  | the FQDNs users and tools use                                                         |
| `CSRF_TRUSTED_ORIGINS` (comma-separated env)                | `[]`                                  | `https://nautobot.example` behind a TLS-terminating proxy                             |
| `SECURE_PROXY_SSL_HEADER`                                   | `("HTTP_X_FORWARDED_PROTO", "https")` | keep; make the proxy set the header                                                   |
| `SESSION_COOKIE_AGE`                                        | `1209600` (2 weeks)                   | shorter, e.g. `43200`                                                                 |
| `SESSION_EXPIRE_AT_BROWSER_CLOSE`                           | `False`                               | `True` where shared workstations are used                                             |
| `EXEMPT_VIEW_PERMISSIONS`                                   | `[]`                                  | leave empty                                                                           |
| `DEBUG`                                                     | `False`                               | `False`                                                                               |
| `X_FRAME_OPTIONS`                                           | `"DENY"`                              | keep                                                                                  |
| `CORS_ALLOW_ALL_ORIGINS`                                    | `False`                               | keep; list origins in `CORS_ALLOWED_ORIGINS`                                          |
| `WEBHOOK_ALLOWED_HOSTS`                                     | `[]`                                  | the webhook receivers' hosts                                                          |

Gotcha: `EXEMPT_VIEW_PERMISSIONS` makes listed models readable by anonymous users too, and `['*']` exempts all but sensitive models. Changing `SECRET_KEY` logs every user out; no 3.2.3 core code
outside settings reads it (searched), so stored data is not encrypted with it. There is no `LOGIN_REQUIRED` setting in 3.2.3 (absent from settings and docs).

Source: `nautobot/core/settings.py:134,342-344,530-546,548,619-621,766-768,1032-1039`, `nautobot/core/templates/nautobot_config.py.j2:13-18,91-116`, `nautobot/core/constants.py:112`;
`docs/user-guide/administration/configuration/settings.html` (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, EXEMPT_VIEW_PERMISSIONS, SECRET_KEY, SESSION_COOKIE_AGE).

## 8. Authentication and tokens

Decision: SSO through `social-auth-app-django` (installed 5.9.0) or LDAP through `django-auth-ldap` (installed 5.3.0); always keep Nautobot's object permission backend in `AUTHENTICATION_BACKENDS`.

```python
# OIDC/OAuth2 example (Okta); redirect URI is https://nautobot.example/complete/okta-openidconnect/
AUTHENTICATION_BACKENDS = ["social_core.backends.okta_openidconnect.OktaOpenIdConnect",
                           "nautobot.core.authentication.ObjectPermissionBackend"]
SOCIAL_AUTH_OKTA_OPENIDCONNECT_KEY = os.environ["OIDC_CLIENT_ID"]
SOCIAL_AUTH_OKTA_OPENIDCONNECT_SECRET = os.environ["OIDC_CLIENT_SECRET"]
EXTERNAL_AUTH_DEFAULT_GROUPS = ["read-only"]

# LDAP example
import ldap
from django_auth_ldap.config import LDAPSearch
AUTHENTICATION_BACKENDS = ["django_auth_ldap.backend.LDAPBackend", "nautobot.core.authentication.ObjectPermissionBackend"]
AUTH_LDAP_SERVER_URI = "ldaps://ldap.example"
AUTH_LDAP_BIND_DN = "CN=svc-nautobot,OU=Service,DC=example,DC=com"
AUTH_LDAP_BIND_PASSWORD = os.environ["LDAP_BIND_PASSWORD"]
AUTH_LDAP_USER_SEARCH = LDAPSearch("OU=Users,DC=example,DC=com", ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")
```

```bash
# tokens: fields user, key (40 chars), expires, write_enabled, description
curl -s -X POST -u "$NB_USER:$NB_PASS" -H "Content-Type: application/json" https://nautobot.example/api/users/tokens/ \
  -d '{"description": "ci reader", "write_enabled": false, "expires": "2027-01-01T00:00:00Z"}'
curl -s -H "Authorization: Token $NAUTOBOT_TOKEN" "https://nautobot.example/api/users/tokens/?q=ci"   # filters: id, key, write_enabled, created, expires, description, q
```

Rotation: create the new token, move the consumer, then `DELETE /api/users/tokens/<id>/`; Nautobot has no automatic rotation, only `expires`.

Gotcha: the SSO docs say `ObjectPermissionBackend` must stay in the list (excluding it is an error); without it object permissions do not apply. `write_enabled: false` is the cheapest
least-privilege control for readers. Basic-auth provisioning needs a password Django can authenticate (local or LDAP); an SSO-only user has none. The token list has no user filter (strict filtering
returns 400 for `?user=`).

Source: `nautobot/core/settings.py:258-268,749-752`, `nautobot/users/models.py:241-270`, `nautobot/users/filters.py:92-97`, `nautobot/users/api/urls.py`;
`docs/user-guide/administration/configuration/authentication/sso.html`,
`.../authentication/ldap.html`, `docs/user-guide/platform-functionality/rest-api/authentication.html`.

## 9. Workers and scheduler

Decision: when Jobs stall, check in this order: a worker answers ping, it consumes the Job's queue, the task is active or reserved, the scheduler's heartbeat is fresh.

```bash
nautobot-server celery inspect ping                        # every worker; -d/--destination celery@<host> for one
nautobot-server celery inspect active_queues               # queues each worker consumes
nautobot-server celery inspect active                      # running tasks
nautobot-server celery inspect reserved                    # prefetched, not started
nautobot-server celery inspect scheduled                   # ETA/countdown tasks
nautobot-server celery inspect stats                       # pool size, totals, rusage
nautobot-server celery inspect registered                  # task names the worker knows
nautobot-server celery inspect ping -t 5 -j                # longer timeout, JSON output
```

Staff users also have `/worker-status/` in the UI (workers and configured queues). Job results are stored in the database (`CELERY_RESULT_BACKEND =
"nautobot.core.celery.backends.NautobotDatabaseBackend"`); the beat scheduler is `nautobot.core.celery.schedulers:NautobotDatabaseScheduler`, so schedules live in the database.

Gotcha: `inspect` broadcasts over the Redis broker and waits 1.0 second by default (`--timeout`); a busy worker can miss it, so retry with `-t 5` before declaring it dead. A Job whose queue no
worker consumes stays
`PENDING` with no error. `nautobot-server celery inspect --help` prints Nautobot's own help; read Celery's options with `python -m celery inspect --help` or `--list`.

Source: `nautobot/core/urls.py:95`, `nautobot/core/views/__init__.py:290-295`, `nautobot/core/settings.py:1102-1167`; `python -m celery inspect --help` and `--list` (Celery 5.6.3);
`docs/user-guide/administration/guides/health-checks.html`, `docs/user-guide/administration/guides/celery-queues.html`.

> **Learned 2026-10-05** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: nautobot/core/settings.py line 177 reads NAUTOBOT_METRICS_AUTHENTICATED into METRICS_AUTHENTICATED · Falsifier: a 3.2.x release that reads a METRICS_AUTHENTICATION setting
> The metrics authentication setting is `METRICS_AUTHENTICATED` (env `NAUTOBOT_METRICS_AUTHENTICATED`); the bundled Prometheus guide calls it `METRICS_AUTHENTICATION`, which has no effect. Check the setting name against settings.py.
````

## File: references/operations-cookbook.md
````markdown
---
Title: Nautobot operations cookbook
Category: skill-reference
Status: current
Authority: Installed Nautobot 3.2.3 source and version-matched official documentation; the cited lines win over this summary
Scope: >-
  Exact, version-matched syntax for Nautobot GraphQL, REST, Dynamic Groups, computed and custom fields, Config Contexts, Secrets, webhooks and events, approvals, data validation, permissions
  and change log, nautobot-server, Jobs and Circuits
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
````

## File: references/staged-onboarding.md
````markdown
# Staged onboarding

## State machine

Use `observation → identity candidates → corroboration → ambiguity or Staged object → review → promotion`. Preserve source, capture time, vantage, confidence, and the facts used to reach each state.
An observation is never an instruction to create or overwrite production inventory.

One identifier is insufficient: labels move, addresses are reused, serials may be absent, and a service name can survive a hardware replacement. Corroborate with independent evidence such as a stable
management identity, serial, physical record, existing inventory, or an authenticated handoff. When facts disagree, retain the candidates and contradiction rather than selecting the most convenient
match. An ambiguity queue is a valid result and a reason to stop automation.

## Brownfield and greenfield

For brownfield onboarding, reconcile what exists against intended inventory and represent safe candidates as Staged. A discovered name is an observation; an intended name is an approved convention.
Do not silently rename an existing intended object to match a poll result. Handle moved units, replacements, duplicate identities, and stale records as separate review cases with a visible proposed
action and rollback path. Dry-run output should show create, adopt, link, rename, skip, and ambiguity actions distinctly.

Greenfield provisioning begins with approved intent and controlled creation; brownfield onboarding begins with uncertain evidence. Treating them as the same bulk-import workflow is a common source of
accidental duplicate records and ownership loss.

## Promotion acceptance

Promote only after a reviewer accepts the corroborated identity, field ownership, intended name, Location/Namespace/Tenant placement, lifecycle state, and downstream linkage. Stop when identity is
ambiguous, the writer lacks ownership, a pre-existing record has contradictory authority, or the plan would create a duplicate. This is a project-derived brownfield pattern, not a promise that a
particular Nautobot workflow automates it. Claim N-C05.

## Identity decisions and a dry-run plan

| Evidence                                         | Proposed action                | Stop condition                                    |
| ------------------------------------------------ | ------------------------------ | ------------------------------------------------- |
| New, corroborated identity and approved location | Create Staged                  | Another record has the stable ID                  |
| Existing stable ID with matching physical facts  | Adopt existing                 | Its owner/intent conflicts with observation       |
| Existing Device, missing association only        | Link after relationship review | Link already points elsewhere                     |
| Unsupported or out-of-scope observation          | Skip with reason               | Never reinterpret skip as accepted inventory      |
| Serial/MAC/name candidates disagree              | Hold for identity review       | No automatic tie-break by address or name         |
| Hardware appears at another site                 | Hold as moved-hardware case    | No silent Location rewrite                        |
| Old unit gone and new unit serves same role      | Replacement workflow           | Do not overwrite old serial or monitoring history |
| Two records claim one stable identity            | Duplicate investigation        | Do not create a third record                      |

Synthetic capture: `obs-41` at 10:00 UTC reports serial `SYN-21`, MAC `02:00:00:00:00:21`, and site `A`; inventory has a Staged Device with that serial
and MAC but no interface link. Dry run: `adopt existing Device D-21; link management interface after confirming ownership; no rename; no status change; 0 writes`.
If a second Device has the same serial at site `B`, plan becomes `hold conflicting identity D-21/D-22; 0 writes`. The reviewer sees both source times and the
independent evidence; the importer cannot resolve it by first match. For promotion, require reviewed identity, intended placement and field writer, reachable
dependent links, a fresh dry-run diff, authorized actor and a visible postcondition (the right Device and links, not just an API response). The UNC site-prefix and
operator batch rules are **project policy examples**, not Nautobot defaults. Read [authority and modeling](authority-and-modeling.md) for writer ownership and
[lifecycle and replacement](lifecycle-and-replacement.md) for swaps.

> **Learned 2026-10-05** · Nautobot 3.2.3 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a second fleet export in which register status predicts liveness
> A controller or asset register is not a liveness source: of about 3,300 live units, 28% were missing from the exported register, and 28% of rows it marked inactive were still answering. Onboard from a fresh sweep, and treat the register as one corroborating source.

> **Learned 2026-10-05** · Nautobot 3.2.3 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a fleet where an address-only match is usually the same unit
> Never adopt a record on its IP address alone: in 46 of 47 address-only matches another unit now held the address. Require serial, an exact MAC (or a family's documented MAC offset) or the unit's own self-report to agree.

> **Learned 2026-10-05** · Nautobot 3.2.3 deployment · VERIFIED_PRIMARY · Source: measured over 119 discovery sweeps, 44 identify reads and 36 DNS zones of one deployment, about 4,000 units at 43 sites, 2026-09-23 to 2026-10-01 (UNC capture corpus, aggregated read-only) · Falsifier: a serial disagreement between two independent reads of one unit
> Serial was the only identity signal that never conflicted (93 of 93 units read two ways agreed); MAC needed a ±1 tolerance for one radio family, and device names differed from SNMP sysName in 56 of 122 cases. Rank serial > exact MAC > offset MAC > name, and record which signal matched. MAC notation also differed by source (colon upper, dash, lower), so normalise at the seam before any comparison.
````

## File: references/upgrade-and-troubleshooting.md
````markdown
# Upgrade and troubleshooting

## Extension register and preflight

Maintain a project-local extension register with purpose, exact upstream and Python versions, extension form, source/base version, affected model/API/setting, migrations, worker requirements,
retrofit steps, tests, rollback, and status. Distinguish configuration, supported app, Job/API adapter, overlay, and core patch. The observed environment in `compatibility.yaml` is a comparison target,
not a broad compatibility promise.

Before upgrade, read release notes and the extension register; inspect custom app compatibility, changed Job APIs, validators, migrations, settings, worker behavior, extension registration, and any
core patch. After upgrade, prove three distinct levels:

```text
import or start success
!= functional compatibility
!= operator-visible acceptance
```

A service can import while a Job no longer queues, a validator is no longer registered, a migration is incomplete, or a worker uses different settings from the UI.

Version trigger: when the installed version differs from the `Verified against:` line of [the operations cookbook](operations-cookbook.md), re-verify each cookbook
section the task relies on against the new installed source or versioned docs, then update that line and `compatibility.yaml`. Until then the cookbook is the old
version's syntax.

## Retrofit and rollback

If upstream supplies a replacement for a patch, verify the replacement, retire the patch, preserve history, and test the new behavior. If a patch remains necessary, compare the original base to new
upstream code, review and rework it manually, test its exact and adjacent contracts, and verify rollback. Never blindly replay a patch. The same discipline applies to custom apps, Jobs, and
validators: identify whether the seam remains supported before treating a green process as a compatible extension.

Common diagnostic clues are missing apps after startup, Jobs visible in the UI but unavailable to workers, stale validators, failed migrations, or permissions changing API response shape. Claims N-C04
and N-C11.

## Example extension register and upgrade proof

| ID / purpose                       | Form and seam                           | Old → candidate   | Regression and visible acceptance                              | Decision                         |
| ---------------------------------- | --------------------------------------- | ----------------- | -------------------------------------------------------------- | -------------------------------- |
| `EX-01`, protect reported identity | Supported custom app; Device            | Synthetic 3.1     | API/UI wrong-writer update rejected; writer succeeds; missing  | Keep only after migrations,      |
|                                    |   CustomValidator; catalog loaded       |   → 3.2           |   catalog alerts; restart loads new rules                      |   settings and worker/web tests  |
|                                    |   at import                             |                   |                                                                |                                  |
| `EX-02`, site import               | Job; `enqueue_job` and queue            | Synthetic 3.1     | Explicit `job_kwargs`, task claimed, created object visible    | Adapt; scheduled                 |
|                                    |                                         |   → 3.2           |                                                                |   `kwargs=None` reviewed         |

Inventory every extension's source path, owner, base version, migration, exact API/model/settings hook, worker/queue, rollback and upstream replacement before upgrading.
Compare official release notes with each seam, rehearse against a pinned disposable build, run schema migrations, recheck app registration and effective settings in web
and workers, exercise validators on UI/API, Job invocation and queue consumption, and re-read resulting objects in the operator view. A `TypeError` or `ValueError`
after a 3.2 Job upgrade points first to argument validation and scheduled kwargs, not necessarily to a missing worker. A Job stuck pending points to queue routing;
a field unexpectedly writable points to validator registration/catalog load or a validation-bypassing path. Preserve a tested rollback and data migration reversal
plan. Rebase/retire a core patch only if the project actually has one; supported app/setting seams need compatibility tests, not generic patch theatre.
````

## File: scripts/check_governance.py
````python
#!/usr/bin/env python3
"""Governance coherence checks for skill-nautobot.

Turns this project's governance CLAIMS into assertions that fail. Stdlib only, so the gate never fails for environment reasons; exit 1 on any failure so it can gate the task runner.

Generated by skill-ai-it from templates/check_governance.py. Doctrine, check families, and the inference table live in the skill's patterns/governance-checks.md — read that before adding,
changing, or retiring a check.

Structure:
  CONFIG      — registries the agent tunes per project. Everything below CONFIG is generic.
  Tier 1      — universal checks. Present in every project.
  Tier 2      — conditional checks. Kept only when their trigger artifact exists.
  Tier 3      — project-specific invariants. Authored per project; each cites the rule it enforces.

Growth rule: this file is expected to grow with the project. A new class of artifact needs a coverage check; a new duplicated constant needs a registry entry. When a check fails, fix the
project, not the check.

Checks:
  1. Referenced paths in the governance surfaces resolve on disk (relative to the referencing file, then to the repo root).
  2. Index links resolve, and every indexed folder member is linked.
  3. Count claims in prose match reality (historical facts exempt).
  4. Cataloged items exist and existing items are cataloged.
  5. Task-runner recipes named in prose exist in the runner.
  5b. No recipe reaches an interpreter implicitly — neither a bare `python3`/`node` nor `mise exec -- python`.
  6. Derived artifacts are not older than their inputs.
  7. Every surface restating a registered constant states it identically, and nothing unregistered restates it.
  8. Every row of an append-only table stamps its pass, and no pass records the same entity twice.
  9. Every dated evidence capture states its URL, retrieval date and HTTP status, or names the capture that corrects it.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Repo-relative path to this file. Used to exclude the checker from the constant scan: it necessarily contains every
# registered constant's PATTERN, and comparing `rel` against a bare `Path(__file__).name` never matched, so the checker
# reported each of its own pattern definitions as an unregistered restatement.
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()

# --------------------------------------------------------------------------------------------------------------- CONFIG
# Tune these registries to the project. Leave a registry empty and its check contributes zero assertions rather than
# failing — coverage is measured by the assertion count, so an empty registry reads honestly as "not covered yet".

# Governance surfaces whose path references must resolve.
SURFACES: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "AI_NAVIGATION.md",
    "SKILL.md",
    "SCRATCHPAD.md",
    "CHANGELOG.md",
    "scripts/README.md",
)

# Index file -> (folder it indexes, glob). Enforces BOTH directions: links resolve, and members are linked.
CATALOGS: dict[str, tuple[str, str]] = {
    # SKILL.md is the activation surface and must route every reference; the contract test checks only its REQUIRED list,
    # so a NEW reference file is caught here until it is routed.
    "SKILL.md": ("references", "*.md"),
    # The pack-domain routing table in AI_NAVIGATION.md mirrors SKILL.md for agents that enter through the router.
    "AI_NAVIGATION.md": ("references", "*.md"),
    "scripts/README.md": ("scripts", "*.py"),
    # Every promoted Archcore document must be indexed; an unindexed one is invisible to the next promote/refresh.
    ".archcore/index.guide.md": (".archcore", "*/*.md"),
}

# Files a catalog may legitimately omit (the index itself, generated output, dotfiles).
CATALOG_EXEMPT: frozenset[str] = frozenset({"README.md", "__init__.py"})

# Countable noun -> (folder, glob). A prose claim like "26 documents" is checked against the real count. Choose the glob
# deliberately: "*.md" counts the folder's own index too, which is usually not what the prose means — prefer "[0-9]*.md"
# or a similar shape when the index is excluded from the claim.
COUNT_CLAIMS: dict[str, tuple[str, str]] = {
    # "documents": ("docs", "*.md"),
    # "scripts": ("scripts", "*.py"),
}

# Lines carrying this marker state a historical fact, not a live claim, and are exempt from count checking.
ASAT_MARKER = "count:asat"

# Lines carrying this marker show an ILLUSTRATIVE filename — a naming-convention example — not a reference to a file
# that must exist. Same shape as ASAT_MARKER: explicit, per line, and visible in the document itself rather than
# hidden in an ignore-list here.
EXAMPLE_MARKER = "path:example"

# Paths a governance surface references CONDITIONALLY ("when present"). The generic skill-ai-it navigation block names
# several; each is a real artifact in SOME governed project, so its absence here is a fact about this project's
# toolchain rather than a broken reference. Registered with a per-entry reason rather than silently ignore-listed, so
# the exemption stays reviewable — remove an entry the day the artifact appears. Tune per project.
CONDITIONAL_PATHS: frozenset[str] = frozenset({
    # Named by the generic skill-ai-it navigation block; this pack does not have them.
    "Taskfile.yml",                     # this pack uses just
    "Makefile",
    "package.json",                     # no Node toolchain
    "ARCHITECTURE.md",                  # a guidance pack; SKILL.md + references/ carry the design
    "architecture.md",
    "ROADMAP.md",                       # open items live in SCRATCHPAD.md
    "roadmap.md",
    "memory-bank/activeContext.md",     # this pack uses SCRATCHPAD.md, not a memory-bank
    "memory-bank/progress.md",
    "memory-bank/decisionLog.md",
    ".archcore/specs",                  # never promoted, by decision: see .archcore/index.guide.md "Never promoted"
    ".archcore/guides",
    "ARCHCORE_PROMOTION_CANDIDATES.md", # transient promotion queue, deleted by `promote` on 2026-10-05; still named by the generic managed blocks
    ".ai-context/repo-pack.md",         # never generated here; only governance-pack.md is (`just context-pack`)
    # Paths in the unified-network-controller repository, named as such in the citing text. Not resolvable from this pack.
    "docs/engineering/platform-skills-project-layer-20261005_1349.md",
    "docs/reports/project-reviews/nautobot-openwisp-skills-independent-assessment-20261005_1427.md",
})

# Pack folders a BARE filename (`data-model.md`, `nautobot_paging.py`) is resolved against. The pack's own prose names its
# references and helpers without the folder prefix; the name must still exist in one of these, so a rename is still caught.
NAME_ROOTS: tuple[str, ...] = ("references", "scripts", "tests", "documents")

# Task runner file, or None if the project has none.
TASK_RUNNER: str | None = "justfile"

# Files whose prose names task-runner recipes.
RUNNER_REFERENCES: tuple[str, ...] = ("README.md", "AGENTS.md", "AI_NAVIGATION.md", "scripts/README.md")

# Recipes that BUILD the venv from the mise pin — e.g. "bootstrap" in templates/justfile. {{py}} cannot exist yet when
# these run, so their own `mise exec -- python -m venv .venv` line is the one legitimate implicit-interpreter call, not
# a violation of the rule it otherwise enforces. Leave empty if the project has no such recipe.
VENV_BUILDER_RECIPES: frozenset[str] = frozenset({"bootstrap"})

# Generated artifact -> inputs it must not be older than.
DERIVED: dict[str, tuple[str, ...]] = {
    # "docs/CLASS-PROFILES.md": ("scripts/class_profiles.py", "process/vehicle-classes.yaml"),
}

# Facts deliberately restated across surfaces. Each entry: the regex that recognises a statement of the fact, and every
# file allowed to state it. Drift fails; so does an UNREGISTERED file stating it — that is what makes this self-extending.
# Pair each entry with a spec document explaining why the duplication is intentional.
CONSTANT_SURFACES: dict[str, dict[str, object]] = {
    # "profit-gate": {
    #     "pattern": r"\$2,500",
    #     "surfaces": ("AGENTS.md", "docs/07-DECISIONS.md"),
    #     "owner": ".archcore/rules/purchase-discipline.rule.md",
    # },
}

# Append-only tables and the columns that give them their grain: (entity column, pass column). An append-only table
# records a re-measurement by ADDING a row, which is right and useless on its own — without a column that orders the
# passes there is no way to compute which row is current, and every aggregate over the table double-counts whatever was
# re-measured. Found in a governed project on 2026-08-28 with twelve rows standing for eight entities, the supersession
# recorded only in a prose note. Register the table here and the grain becomes an assertion instead of an intention.
APPEND_ONLY_TABLES: dict[str, tuple[str, str]] = {
    # "data/sku-scores.csv": ("sku_id", "scored_at"),
}

# Folder of dated evidence captures, or None if the project keeps none. A capture asserts what a source said on a date.
EVIDENCE_DIR: str | None = None  # e.g. "trackers/source-captures"

# The index file inside EVIDENCE_DIR, exempt from the provenance header because it is a catalog, not a capture.
EVIDENCE_INDEX = "README.md"

# Header fields that make a capture re-openable by someone who was not there: where it came from, when, and whether the
# fetch actually succeeded. A capture naming no URL and no HTTP status is a recollection in a capture's clothing — in
# the project this was promoted from, exactly that produced a VERIFIED cost row whose only recorded fetch returned 403.
EVIDENCE_PROVENANCE_FIELDS: tuple[str, ...] = ("Canonical URL", "Retrieved", "HTTP status")

# Captures taken before the provenance rule existed. Each MUST name the later capture supplying the missing provenance —
# this is a correction record, not an exemption. Where captures are immutable the only way to clear an entry is to take
# the correcting capture, which is the behaviour the rule wants. Removing an entry whose correction does not exist turns
# the check red rather than quiet, so the list cannot be emptied by deletion.
EVIDENCE_PROVENANCE_CORRECTED: dict[str, str] = {
    # "uae-wholesale-moq-discounts-20260828.md": "wholesale-house-price-provenance-20260828.md",
}

# Extensions scanned when hunting for unregistered restatements of a constant.
SCAN_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".yaml", ".yml"})

# Path-token discrimination. Prose is full of tokens that look like paths and are not; tune until the check is quiet.
PATHLIKE = re.compile(r"^[A-Za-z0-9._/-]+$")
REPO_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".txt"})
IGNORE_PREFIXES: tuple[str, ...] = ("http://", "https://", "mailto:", "~/", "/")
IGNORE_EXACT: frozenset[str] = frozenset({"README.md", "AGENTS.md", "CLAUDE.md", "SCRATCHPAD.md", "CHANGELOG.md"})

# --------------------------------------------------------------------------------------------------------------- HARNESS

failures: list[str] = []
checks_run = 0


def fail(check: str, detail: str) -> None:
    failures.append(f"{check}: {detail}")


def counted() -> None:
    """Record one assertion actually evaluated. Never call this per function — only per real comparison."""
    global checks_run
    checks_run += 1


def read(rel: str) -> str | None:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else None


def without_code(text: str) -> str:
    """Strip fenced code blocks. Their contents are examples, not claims about this repo."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def table_rows(rel: str) -> list[dict[str, str]]:
    """Read a CSV as dicts, or an empty list when it does not exist — an absent table contributes zero assertions."""
    path = ROOT / rel
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def members(folder: str, glob: str) -> list[Path]:
    base = ROOT / folder
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob(glob) if p.is_file() and not p.name.startswith("."))


# --------------------------------------------------------------------------------------------------------------- TIER 1


def check_referenced_paths() -> None:
    """Every repo-relative path named in a governance surface resolves on disk."""
    for surface in SURFACES:
        text = read(surface)
        if text is None:
            fail("surface", f"{surface} is listed as a governance surface but does not exist")
            counted()
            continue
        body = "\n".join(l for l in without_code(text).splitlines() if EXAMPLE_MARKER not in l)
        tokens = set(re.findall(r"`([^`\n]+)`", body))
        tokens |= {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", body)}
        for raw in sorted(tokens):
            tok = raw.split("#", 1)[0].strip().rstrip("/")
            if not tok or tok in IGNORE_EXACT or tok in CONDITIONAL_PATHS or tok.startswith(IGNORE_PREFIXES):
                continue
            if not PATHLIKE.match(tok):
                continue
            suffix = Path(tok).suffix
            if "/" not in tok and suffix not in REPO_SUFFIXES:
                continue
            if suffix and suffix not in REPO_SUFFIXES:
                continue
            counted()
            # Resolve relative to the file that MAKES the reference first, then relative to ROOT. Resolving only
            # against ROOT false-fails every correct relative link written inside a subfolder README.
            near = (ROOT / surface).parent / tok
            bare = "/" not in tok and any((ROOT / folder / tok).exists() for folder in NAME_ROOTS)
            if not near.exists() and not (ROOT / tok).exists() and not bare:
                fail("path", f"{surface} references `{tok}` which does not exist")


def check_index_links() -> None:
    """Links inside an index file resolve, relative to the index's own folder."""
    for index in CATALOGS:
        text = read(index)
        if text is None:
            fail("index", f"catalog {index} does not exist")
            counted()
            continue
        base = (ROOT / index).parent
        for target in {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", without_code(text))}:
            tok = target.split("#", 1)[0].strip()
            if not tok or tok.startswith(IGNORE_PREFIXES):
                continue
            counted()
            if not (base / tok).exists():
                fail("index", f"{index} links `{tok}` which does not exist")


def check_count_claims() -> None:
    """Prose stating a quantity matches the real count. Lines marked as historical facts are exempt."""
    for noun, (folder, glob) in COUNT_CLAIMS.items():
        actual = len(members(folder, glob))
        pattern = re.compile(rf"(\d+)\s+{re.escape(noun)}\b", re.IGNORECASE)
        for surface in SURFACES:
            text = read(surface)
            if text is None:
                continue
            for line in without_code(text).splitlines():
                if ASAT_MARKER in line:
                    continue
                for claim in pattern.finditer(line):
                    counted()
                    if int(claim.group(1)) != actual:
                        fail("count", f"{surface} claims {claim.group(1)} {noun}; {folder}/{glob} holds {actual}")


def check_catalog_coverage() -> None:
    """Both directions: the catalog names nothing missing, and nothing present is uncataloged.

    The second direction is the one that grows silently, and it is what makes this checker self-extending — a new file
    turns the build red until it is registered somewhere.
    """
    for index, (folder, glob) in CATALOGS.items():
        text = read(index)
        if text is None:
            continue
        body = without_code(text)
        for item in members(folder, glob):
            if item.name in CATALOG_EXEMPT or (ROOT / index).resolve() == item.resolve():
                continue
            counted()
            if item.name not in body:
                fail("coverage", f"{folder}/{item.name} exists but is not cataloged in {index}")


# --------------------------------------------------------------------------------------------------------------- TIER 2
# Keep a check below only while its trigger artifact exists. Delete the rest rather than leaving inert scaffolding.


def check_task_recipes() -> None:
    """Recipes named in prose exist in the task runner, and every cataloged script has a way to be run."""
    if TASK_RUNNER is None:
        return
    runner = read(TASK_RUNNER)
    if runner is None:
        fail("runner", f"{TASK_RUNNER} is configured but does not exist")
        counted()
        return
    recipes = {m.group(1) for m in re.finditer(r"^([a-zA-Z][\w-]*)\s*(?:[*+a-zA-Z_].*)?:(?!=)", runner, re.MULTILINE)}
    for surface in RUNNER_REFERENCES:
        text = read(surface)
        if text is None:
            continue
        for named in {m.group(1) for m in re.finditer(r"`just ([a-zA-Z][\w-]*)", without_code(text))}:
            counted()
            if named not in recipes:
                fail("runner", f"{surface} names recipe `{named}` which {TASK_RUNNER} does not define")


def check_interpreter_pinning() -> None:
    """No task recipe reaches an interpreter implicitly.

    Two defects, one root cause — the recipe does not say which interpreter it means:

    1. A BARE `python3`/`node`/`npx`/`ruby` resolves to whatever is on PATH, not to what .mise.toml pins.
    2. `mise exec -- python` resolves to the venv only while `_.python.venv` activation applies. It tests clean, reads
       as pinned, and degrades SILENTLY to the host interpreter when that activation stops holding.

    Both are the "it works on the machine it was written on" class. Recipes must address {{py}} by path and depend on
    _require-venv. Node has no venv layer, so `mise exec -- node` is the legitimate explicit form for it and is allowed.

    Exception: VENV_BUILDER_RECIPES (e.g. "bootstrap") create the venv from the mise pin, so {{py}} cannot exist yet
    when they run — their own `mise exec -- python -m venv .venv` line is the one legitimate implicit call, not a
    violation of the rule it otherwise enforces. Found missing during unified-network-controller's bootstrap
    (2026-09-18): the template's own `bootstrap` recipe failed the check it ships with, because nothing tracked which
    recipe a line belongs to. `cambium-swap` had already patched this locally; ported back here so every project
    generated from this template gets it, instead of each one rediscovering and re-fixing it independently.

    Rule: the runtime-isolation section of skill-ai-it's SKILL.md, and the RUNTIME PINNING header of templates/justfile.
    """
    if TASK_RUNNER is None:
        return
    runner = read(TASK_RUNNER)
    if runner is None:
        return
    recipe: str | None = None
    for lineno, line in enumerate(runner.splitlines(), 1):
        header = re.match(r"^([a-zA-Z_][\w-]*)\s*(?:[*+a-zA-Z_][^:]*)?:(?!=)", line)
        if header:
            recipe = header.group(1)
            continue
        if not line.startswith((" ", "\t")):
            continue  # only recipe bodies are commands; headers and variable assignments are not
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Blank out quoted literals, keeping offsets intact: an interpreter NAME inside a string is a label being
        # printed (`printf 'python  '`), not a command being run.
        scan = re.sub(r"'[^']*'|\"[^\"]*\"", lambda m: " " * len(m.group(0)), stripped)
        counted()
        if re.search(r"mise\s+exec\b[^|;]*--\s+python", scan) and recipe not in VENV_BUILDER_RECIPES:
            fail(
                "runtime",
                f"{TASK_RUNNER}:{lineno} reaches Python through an implicit `mise exec -- python` — address the venv "
                f"interpreter by path via {{{{py}}}} and guard it with _require-venv",
            )
        for match in re.finditer(r"(?<![-\w/])(python3?|npx|ruby|node)\b", scan):
            # `mise exec -- <interp>` is handled above for python; for the rest it is the sanctioned explicit form.
            if re.search(r"mise\s+(exec\b[^|;]*--|run)\s*$", scan[: match.start()]):
                continue
            fail(
                "runtime",
                f"{TASK_RUNNER}:{lineno} calls bare `{match.group(1)}` — route it through the pinned interpreter",
            )


# --------------------------------------------------------------------------------------------------------------- TIER 3
# Project-specific invariants. Each check states, in its docstring, the project rule it enforces and where that rule
# lives. A check whose justification cannot be found is a check the next agent deletes.


def check_derived_freshness() -> None:
    """Generated artifacts are not older than the sources they are generated from.

    Freshness only — it proves a rebuild happened, not that the rebuild used the right source. Where the generator can
    stamp its source into the output, add a provenance check alongside this one; see patterns/governance-checks.md.
    """
    for output, inputs in DERIVED.items():
        out = ROOT / output
        if not out.is_file():
            fail("derived", f"{output} is registered as generated but does not exist")
            counted()
            continue
        for src in inputs:
            source = ROOT / src
            counted()
            if not source.is_file():
                fail("derived", f"{output} declares input `{src}` which does not exist")
            elif out.stat().st_mtime < source.stat().st_mtime:
                fail("derived", f"{output} is older than its input `{src}` — regenerate it")


def check_constant_sync() -> None:
    """Facts restated across surfaces stay identical, and no unregistered file restates them.

    Duplication here is deliberate: the operator must read the value at the point of decision without following a
    pointer. So the duplication stays and the sync is enforced. Orphan detection is the half that makes it self-extending.
    """
    for name, entry in CONSTANT_SURFACES.items():
        pattern = re.compile(str(entry["pattern"]))
        registered = {str(s) for s in entry["surfaces"]}  # type: ignore[union-attr]
        owner = str(entry.get("owner", ""))

        for surface in sorted(registered):
            text = read(surface)
            counted()
            if text is None:
                fail("constant", f"{name}: registered surface {surface} does not exist")
            elif not pattern.search(without_code(text)):
                fail("constant", f"{name}: {surface} is registered but no longer states it (owner: {owner or 'unset'})")

        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in registered or rel.startswith(".") or "/." in rel or rel == SELF:
                continue
            counted()
            if pattern.search(without_code(path.read_text(encoding="utf-8", errors="ignore"))):
                fail("constant", f"{name}: {rel} states it but is not registered in CONSTANT_SURFACES")


def check_append_only_grain() -> None:
    """Every row of an append-only table stamps its pass, and no pass records the same entity twice.

    Registered in APPEND_ONLY_TABLES. Two distinct failures, both silent: a row with an EMPTY pass column cannot be
    ordered against any other row, so nothing can say which measurement is current; and a REPEATED (entity, pass) pair
    means one pass measured one entity twice, so every count and every aggregate over the table is wrong by however
    many rows were duplicated. Neither shows up as an error — the table still parses and the report still renders.

    A re-measurement is a NEW pass. Reusing the previous pass identifier to record one is the defect this catches.
    """
    for rel, (entity_col, pass_col) in APPEND_ONLY_TABLES.items():
        rows = table_rows(rel)
        if not rows:
            counted()
            if not (ROOT / rel).is_file():
                fail("append-only-grain", f"{rel} is registered as append-only but does not exist")
            continue
        seen: dict[tuple[str, str], int] = {}
        for i, row in enumerate(rows, start=2):  # line 1 is the header
            counted()
            if entity_col not in row or pass_col not in row:
                fail("append-only-grain",
                     f"{rel} has no {entity_col!r}/{pass_col!r} column; the registered grain does not match the table")
                break
            pass_id = (row.get(pass_col) or "").strip()
            if not pass_id:
                fail("append-only-grain", f"{rel} line {i} has empty {pass_col}; the pass is the grain")
                continue
            key = ((row.get(entity_col) or "").strip(), pass_id)
            if key in seen:
                fail("append-only-grain",
                     f"{rel} line {i} repeats {entity_col} {key[0]!r} for pass {pass_id} (first seen line {seen[key]}); "
                     f"a re-measurement is a NEW pass, so give it a new {pass_col}")
            else:
                seen[key] = i


def check_evidence_provenance() -> None:
    """Every markdown capture states where it came from, when, and whether the fetch succeeded.

    Enforces the global source-discipline policy (~/.agents/AGENTS.md, 'Citations travel into the documentation'): a
    VERIFIED figure means a capture exists that someone else can re-open. Presence of a capture FILE is not that —
    a file with no URL and no HTTP status proves only that somebody wrote something down.

    A capture missing the header is accepted ONLY while it names its correcting capture in
    EVIDENCE_PROVENANCE_CORRECTED and that capture is on disk.
    """
    if EVIDENCE_DIR is None:
        return
    for item in members(EVIDENCE_DIR, "*.md"):
        if item.name == EVIDENCE_INDEX:
            continue
        counted()
        text = read(f"{EVIDENCE_DIR}/{item.name}") or ""
        missing = [f for f in EVIDENCE_PROVENANCE_FIELDS if f"**{f}**" not in text]
        if not missing:
            continue
        corrector = EVIDENCE_PROVENANCE_CORRECTED.get(item.name)
        if corrector is None:
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} states no {', '.join(missing)}; a capture nobody can re-open is not evidence")
        elif not (ROOT / EVIDENCE_DIR / corrector).is_file():
            fail("evidence-provenance",
                 f"{EVIDENCE_DIR}/{item.name} defers its provenance to {corrector}, which does not exist")


# --------------------------------------------------------------------------------------------------------------- MAIN

CHECKS = (
    check_referenced_paths,
    check_index_links,
    check_count_claims,
    check_catalog_coverage,
    check_task_recipes,
    check_interpreter_pinning,
    check_derived_freshness,
    check_constant_sync,
    check_append_only_grain,
    check_evidence_provenance,
)


def main() -> int:
    for check in CHECKS:
        check()

    # The same defect can be reported by more than one matching pattern; a doubled count erodes trust in the number.
    unique = sorted(set(failures))
    if unique:
        print(f"FAIL — {len(unique)} issue(s) across {checks_run} checks\n")
        for f in unique:
            print(f"  ✗ {f}")
        return 1

    print(f"OK — {checks_run} governance checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

## File: scripts/nautobot_ipam.py
````python
"""Pure IPAM rules for Nautobot 3.x data. Stdlib only, no I/O.

The mask an address carries should be its subnet's: the narrowest Prefix of type `network` that holds it, never `/32` by default.
Container and pool Prefixes are not subnets. Writing every device address as `/32` hides the routing fact and makes later
interface/subnet checks impossible; this rule came from a deployment that had to convert its imported addresses afterwards.

Usage:
    from nautobot_ipam import network_mask, with_mask
    with_mask(prefixes, "192.0.2.10")   # "192.0.2.10/27" when 192.0.2.0/27 is the narrowest network Prefix
"""

from __future__ import annotations

import ipaddress


def _prefix_type(prefix: dict) -> str | None:
    kind = prefix.get("type")
    return kind.get("value") if isinstance(kind, dict) else kind


def network_mask(prefixes: list[dict], ip: str) -> int | None:
    """The prefix length of the narrowest `network` Prefix in `prefixes` (REST dicts with `prefix` and `type`) holding `ip`; None if none does.

    Pass the Prefixes of the address's own Namespace only: overlapping address space is legitimate across Namespaces.
    """
    host = ipaddress.ip_address(ip)
    lengths = [ipaddress.ip_network(p["prefix"], strict=False).prefixlen for p in prefixes
               if _prefix_type(p) == "network" and host in ipaddress.ip_network(p["prefix"], strict=False)]
    return max(lengths, default=None)


def with_mask(prefixes: list[dict], ip: str) -> str | None:
    """`ip/len` using `network_mask`; None when no network Prefix holds the address (create the subnet first; do not fall back to /32)."""
    length = network_mask(prefixes, ip)
    return None if length is None else f"{ip}/{length}"
````

## File: scripts/nautobot_linkage.py
````python
"""Find the breaks in a Location's Nautobot hierarchy: objects that belong to it but that nothing links to it. Read-only, stdlib only.

Why: a site is only navigable when every object can be reached from its Location by following links (foreign keys, M2M fields,
Relationship associations). Objects found by a filter or by name (a Namespace named after the site, a DNS view, the A records in its
zone) can exist with no link back, and nothing in the UI shows it. One deployment had Prefixes that did not list their Location, A
records whose address was on no device and devices with no primary address, all invisible until a graph walk reported them; two
objects can also share a Namespace without the link that matters existing, which is why reachability alone is not enough and named
rules sit beside it.

The engine is generic; the caller supplies the HTTP GET, what to collect and the rules:
    collectors  `Scoped` (filterable to the site; `query` formatted with the quoted site name), `Linked` (has a foreign key, any of
                `via`, to an object already collected; the listing is fetched whole once) and `Referenced` (pointed at through `field`
                by objects of `from_kind`). Order matters: Linked and Referenced see only what earlier collectors added.
    rules       a `Rules` registry of functions over the graph (no API calls), each yielding (kind, name, detail); `evaluate()` runs
                them and adds a `graph.island` finding for every collected object unreachable from the Location.
    unmodelled  `Source.unmodelled(covered)` lists endpoints that hold objects but that nothing covers, so a new kind of object shows
                up until someone adds a collector or says why it is not site data.
Listings are read through `nautobot_paging` (total order, fail-closed), so a doubtful listing raises instead of hiding a gap.

Usage:
    from nautobot_linkage import Rules, Scoped, Linked, Source, evaluate, print_site
    RULES = Rules()
    @RULES.rule("prefix.location", "error")
    def _prefix_location(g):
        "Each Prefix lists the site's Location."
        ...
    src = Source(lambda path: session.get(base + path, timeout=60).json())   # path is relative to /api
    g = src.graph("site-a", [Scoped("dcim.location", "/dcim/locations/", "name={site}"), ...])
    print_site("site-a", evaluate(g, RULES), RULES)
"""

from __future__ import annotations

import collections
import urllib.error
import urllib.parse
from dataclasses import dataclass, field
from typing import Callable, ClassVar, Iterable, Iterator

from nautobot_paging import listing, traverse

SEVERITIES = ("error", "warn", "info")
EXAMPLES = 5
ISLAND_RULE = "graph.island"
ISLAND_DOC = "Everything collected for the site is reachable from its Location."
#: Relationship associations are edges, not objects; they are fetched once and joined on source_id/destination_id.
RELATIONSHIP_PATH = "/extras/relationship-associations/"
RELATIONSHIPS_PATH = "/extras/relationships/"
#: What every collected listing asks for: plain foreign keys, and M2M members included.
DEPTH_QUERY = "depth=0&exclude_m2m=false"


# -- collectors: what belongs to a site -----------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Scoped:
    """Objects the API can filter to the site. `query` is formatted with the site name."""
    kind: str
    path: str
    query: str


@dataclass(frozen=True)
class Linked:
    """Objects with a foreign key (any of `via`) pointing at an object already collected. Fetched whole once, kept by link."""
    kind: str
    path: str
    via: tuple[str, ...]


@dataclass(frozen=True)
class Referenced:
    """Objects that an already-collected object points at through `field` on objects of `from_kind`."""
    kind: str
    path: str
    from_kind: str
    field: str


# -- the graph ----------------------------------------------------------------------------------------------------------------

def refs(obj: dict) -> Iterator[tuple[str, str]]:
    """(field, id) for every foreign key and M2M member in a depth-0 object."""
    for key, value in obj.items():
        items = value if isinstance(value, list) else [value]
        for item in items:
            if isinstance(item, dict) and "id" in item and "object_type" in item:
                yield key, item["id"]


def ref(obj: dict, key: str) -> str | None:
    """The id behind foreign key `key`, or None."""
    value = obj.get(key)
    return value.get("id") if isinstance(value, dict) else None


@dataclass
class SiteGraph:
    """The objects collected for one site, keyed by id, plus Relationship edges (a, b, relationship key)."""
    site: str
    nodes: dict[str, tuple[str, dict]] = field(default_factory=dict)          # id -> (kind, object)
    extra_edges: list[tuple[str, str, str]] = field(default_factory=list)      # (a, b, relationship key)
    root_kind: ClassVar[str] = "dcim.location"

    def add(self, kind: str, obj: dict) -> None:
        self.nodes.setdefault(obj["id"], (kind, obj))

    def of(self, kind: str) -> list[dict]:
        return [o for k, o in self.nodes.values() if k == kind]

    def kind_of(self, oid: str | None) -> str | None:
        return self.nodes[oid][0] if oid in self.nodes else None

    @property
    def location(self) -> dict | None:
        locs = self.of(self.root_kind)
        return locs[0] if locs else None

    def edges(self) -> dict[str, set[str]]:
        adj: dict[str, set[str]] = collections.defaultdict(set)
        for oid, (_, obj) in self.nodes.items():
            for _, target in refs(obj):
                if target in self.nodes:
                    adj[oid].add(target)
                    adj[target].add(oid)
        for a, c, _ in self.extra_edges:
            if a in self.nodes and c in self.nodes:
                adj[a].add(c)
                adj[c].add(a)
        return adj

    def reachable(self) -> set[str]:
        loc = self.location
        if not loc:
            return set()
        adj, seen, todo = self.edges(), {loc["id"]}, [loc["id"]]
        while todo:
            for nxt in adj[todo.pop()]:
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append(nxt)
        return seen

    def related(self, key: str, oid: str) -> set[str]:
        """The objects joined to `oid` by Relationship `key`, in either direction."""
        return {c if a == oid else a for a, c, k in self.extra_edges if k == key and oid in (a, c)}


def label(kind: str, obj: dict) -> str:
    """A readable name for any object: name, address, prefix, display, else the id's first 8 characters."""
    return str(obj.get("name") or obj.get("address") or obj.get("prefix") or obj.get("display") or obj["id"][:8])


# -- rules: the links that should exist -----------------------------------------------------------------------------------------

@dataclass
class Finding:
    rule: str
    severity: str
    kind: str
    name: str
    detail: str = ""


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    doc: str
    fn: Callable[[SiteGraph], Iterable[tuple[str, str, str]]]


class Rules(list):
    """An ordered registry of rules. `@rules.rule(id, severity)` registers a function; its docstring is the rule's description."""

    def rule(self, rule_id: str, severity: str):
        if severity not in SEVERITIES:
            raise ValueError(f"severity {severity!r} is not one of {SEVERITIES}")
        if any(r.id == rule_id for r in self):
            raise ValueError(f"rule {rule_id!r} is already registered")

        def register(fn):
            self.append(Rule(rule_id, severity, (fn.__doc__ or "").strip(), fn))
            return fn
        return register


def islands(g: SiteGraph) -> Iterator[Finding]:
    """A `graph.island` warning for every collected object no chain of links reaches from the Location."""
    seen = g.reachable()
    for oid, (kind, obj) in g.nodes.items():
        if oid not in seen:
            yield Finding(ISLAND_RULE, "warn", kind, label(kind, obj), "not reachable from the Location through any link")


def evaluate(g: SiteGraph, rules: Iterable[Rule]) -> list[Finding]:
    """Every rule's findings, in rule order, then the islands."""
    out = [Finding(r.id, r.severity, k, n, dt) for r in rules for k, n, dt in r.fn(g)]
    return out + list(islands(g))


# -- collection (the only part that calls the API) ----------------------------------------------------------------------------

def _relative(url: str) -> str:
    """A `next` link is absolute; the caller's GET takes paths relative to /api."""
    return url.split("/api", 1)[1] if "://" in url else url


def pages(get: Callable[[str], dict], path: str) -> list[dict]:
    """Every row of `path` at depth 0 with M2M members, in a total order, failing closed (`nautobot_paging.traverse`)."""
    return traverse(lambda url: get(_relative(url)), listing(path + ("&" if "?" in path else "?") + DEPTH_QUERY))


class Source:
    """Reads Nautobot through `get(path)` (path relative to /api, returning parsed JSON). Whole listings are cached per instance."""

    def __init__(self, get: Callable[[str], dict]):
        self._get = get
        self._whole: dict[str, list[dict]] = {}

    def pages(self, path: str) -> list[dict]:
        return pages(self._get, path)

    def whole(self, path: str) -> list[dict]:
        if path not in self._whole:
            self._whole[path] = self.pages(path)
        return self._whole[path]

    def names(self, path: str) -> dict[str, str]:
        return {o["id"]: o["name"] for o in self.whole(path)}

    def graph(self, site: str, collectors: Iterable[Scoped | Linked | Referenced], *,
              new: Callable[[str], SiteGraph] = SiteGraph, annotate: Callable[[str, dict], None] | None = None) -> SiteGraph:
        """Collect `site`'s objects in collector order, then join Relationship associations touching any of them.

        `new(site)` builds the graph (a SiteGraph subclass may carry more state); `annotate(kind, obj)` may add derived fields before
        an object is added.
        """
        g = new(site)
        for c in collectors:
            if isinstance(c, Scoped):
                found = self.pages(f"{c.path}?{c.query.format(site=urllib.parse.quote(site))}")
            elif isinstance(c, Linked):
                found = [o for o in self.whole(c.path) if any(ref(o, v) in g.nodes for v in c.via)]
            else:
                wanted = {ref(o, c.field) for o in g.of(c.from_kind)}
                found = [o for o in self.whole(c.path) if o["id"] in wanted]
            for obj in found:
                if annotate:
                    annotate(c.kind, obj)
                g.add(c.kind, obj)
        rel_keys = {r["id"]: r["key"] for r in self.whole(RELATIONSHIPS_PATH)}
        for a in self.whole(RELATIONSHIP_PATH):
            if a["source_id"] in g.nodes or a["destination_id"] in g.nodes:
                g.extra_edges.append((a["source_id"], a["destination_id"], rel_keys.get(ref(a, "relationship") or "", "?")))
        return g

    def unmodelled(self, covered: Iterable[str], *, skip_apps: Iterable[str] = ("plugins", "status", "graphql", "docs", "swagger", "ui"),
                   skip_plugins: Iterable[str] = ("installed-plugins",)) -> list[tuple[str, int]]:
        """(path, count) for every list endpoint that holds objects and is not in `covered`, sorted by path."""
        covered, skip_apps, skip_plugins = set(covered), set(skip_apps), set(skip_plugins)
        roots = [f"/{app}/" for app in self._get("/") if app not in skip_apps]
        roots += [f"/plugins/{p}/" for p in self._get("/plugins/") if p not in skip_plugins]
        out = []
        for root in roots:
            try:
                index = self._get(root)
            except urllib.error.HTTPError:  # an app root that is not a listing is not a model endpoint
                continue
            for url in index.values() if isinstance(index, dict) else []:
                path = "/" + url.split("/api/", 1)[1]
                if path in covered:
                    continue
                try:
                    count = self._get(f"{path}?limit=1").get("count", 0)
                except urllib.error.HTTPError:  # not a list endpoint
                    continue
                if count:
                    out.append((path, count))
        return sorted(out)


# -- report -------------------------------------------------------------------------------------------------------------------

def summarise(findings: list[Finding]) -> dict[tuple[str, str], list[Finding]]:
    """Findings grouped by (severity, rule)."""
    by: dict[tuple[str, str], list[Finding]] = collections.defaultdict(list)
    for f in findings:
        by[(f.severity, f.rule)].append(f)
    return by


def print_site(site: str, findings: list[Finding], rules: Iterable[Rule], examples: int = EXAMPLES) -> None:
    """One site's findings: a count per severity, then each rule (worst first, most findings first) with up to `examples` lines."""
    by = summarise(findings)
    counts = collections.Counter(f.severity for f in findings)
    print(f"\n{site}: " + ", ".join(f"{counts[s]} {s}" for s in SEVERITIES))
    docs = {r.id: r.doc for r in rules} | {ISLAND_RULE: ISLAND_DOC}
    for (sev, rid), fs in sorted(by.items(), key=lambda kv: (SEVERITIES.index(kv[0][0]), -len(kv[1]))):
        print(f"  [{sev}] {rid} x{len(fs)}: {docs.get(rid, '')}")
        for f in fs[:examples]:
            print(f"      {f.kind:28} {f.name:32} {f.detail}")
        if len(fs) > examples:
            print(f"      ... and {len(fs) - examples} more")


def print_estate(report: dict[str, list[Finding]]) -> None:
    """Many sites: one line per site (most errors first), then each rule's reach across the estate."""
    print(f"{'site':18} {'error':>5} {'warn':>5} {'info':>5}  top rules")
    for site, fs in sorted(report.items(), key=lambda kv: -sum(f.severity == 'error' for f in kv[1])):
        c = collections.Counter(f.severity for f in fs)
        top = collections.Counter(f.rule for f in fs if f.severity != "info").most_common(3)
        print(f"{site:18} {c['error']:5} {c['warn']:5} {c['info']:5}  " + ", ".join(f"{r} {n}" for r, n in top))
    total = collections.Counter((f.severity, f.rule) for fs in report.values() for f in fs)
    print("\nrules across the estate (sites affected / findings):")
    for (sev, rid), n in sorted(total.items(), key=lambda kv: (SEVERITIES.index(kv[0][0]), -kv[1])):
        print(f"  [{sev}] {rid:24} {sum(any(f.rule == rid for f in fs) for fs in report.values()):3} sites / {n}")
````

## File: scripts/nautobot_masks.py
````python
"""Give every /32 address its subnet's mask: plan the changes from address and Prefix records, then optionally apply them. Stdlib only.

Why: importers that write device addresses as `/32` and importers that write the subnet's mask disagree, so which one runs first
at a site decides the mask, and a site can end up holding both. One deployment found exactly that after its onboarding, discovery
and DNS-zone importers had each run. The rule (see `nautobot_ipam`) is that an address carries the mask of the narrowest `network`
Prefix holding it in its own Namespace. Changing the mask in place (PATCH `address` with the same host) keeps the object, so its
interface assignments, primary_ip4 and relationships stay as they are (seen on Nautobot 3.2.3).

What the plan does, per Namespace:
    fix       a /32 whose narrowest network Prefix is found and no wider than `min_subnet`: the new `host/len`.
    report    a /32 with no network Prefix, or whose narrowest network Prefix is wider than `min_subnet` (a placeholder such as a
              seeded /16, not a real subnet); and any non-/32 address whose mask differs from its subnet's. Nothing is changed.
A second plan over the fixed records finds nothing to fix.

Usage:
    from nautobot_masks import plan, apply
    fix, report = plan(addresses, prefixes)          # REST dicts of ONE Namespace: addresses need id/host/mask_length/address
    apply(lambda method, path, body: session.request(method, base + path, json=body).json(), fix)   # bulk PATCH, 200 per call
"""

from __future__ import annotations

from typing import Callable

from nautobot_ipam import network_mask

#: A network Prefix wider than this is treated as a placeholder, not the subnet a device is configured on.
MIN_SUBNET = 17

#: The report wording; a caller may pass its own (same keys, same format fields) to keep an established output.
MESSAGES = {
    "none": "no network Prefix holds it",
    "wide": "narrowest network Prefix is /{mask}, wider than /{min_subnet}: the subnet is not recorded",
    "differs": "mask /{have} differs from its subnet's /{mask}",
}


def plan(addresses: list[dict], prefixes: list[dict], *, min_subnet: int = MIN_SUBNET,
         messages: dict[str, str] | None = None) -> tuple[list[tuple[dict, str]], list[tuple[dict, str]]]:
    """(to fix: [(address, "host/len")], to report: [(address, why)]) for one Namespace's addresses and Prefixes, in input order."""
    text = {**MESSAGES, **(messages or {})}
    fix: list[tuple[dict, str]] = []
    report: list[tuple[dict, str]] = []
    for a in addresses:
        mask = network_mask(prefixes, a["host"])
        if a["mask_length"] == 32:
            if mask is None:
                report.append((a, text["none"].format(mask=mask, min_subnet=min_subnet, have=32)))
            elif mask < min_subnet:
                report.append((a, text["wide"].format(mask=mask, min_subnet=min_subnet, have=32)))
            elif mask != 32:
                fix.append((a, f"{a['host']}/{mask}"))
        elif mask is not None and a["mask_length"] != mask:
            report.append((a, text["differs"].format(mask=mask, min_subnet=min_subnet, have=a["mask_length"])))
    return fix, report


def apply(call: Callable[[str, str, list], object], fix: list[tuple[dict, str]], *, batch: int = 200,
          path: str = "/ipam/ip-addresses/") -> int:
    """Bulk-PATCH each planned `address` through `call(method, path, body)`, `batch` objects per request. Returns how many were sent.

    The caller owns authentication, the base URL, retries and which account writes; this only shapes the requests.
    """
    if batch < 1:
        raise ValueError("batch must be at least 1")
    for i in range(0, len(fix), batch):
        call("PATCH", path, [{"id": a["id"], "address": new} for a, new in fix[i : i + batch]])
    return len(fix)
````

## File: scripts/nautobot_paging.py
````python
"""Fail-closed traversal of a Nautobot REST listing. Stdlib only; the caller supplies the HTTP GET, so authentication and retries stay theirs.

Why: Nautobot pages by offset, which is only safe when the queryset has a total order. Some endpoints have none (seen on DNS Models
A records and core ip-address-to-interface in 3.2.x), so page two can repeat rows from page one and skip others: one deployment listed
320 rows that held 251 distinct objects, and an importer then acted on the wrong set. Sorting by a unique key (`sort=id`) fixes the order;
this module also refuses to return a listing that still repeats an object, repeats a continuation, ends early or disagrees with `count`.
It cannot prove completeness against concurrent writes; for that, compare with a snapshot or re-read.

Usage:
    from nautobot_paging import listing, traverse
    rows = traverse(lambda url: session.get(url, timeout=60).json(), base + listing("/api/dcim/devices/?location=site-a"))
"""

from __future__ import annotations

from typing import Callable


class PagingError(RuntimeError):
    """The listing cannot be trusted as one consistent set of objects."""


def listing(path: str, limit: int = 200, sort: str = "id") -> str:
    """`path` with `limit` and a total order (`sort=id` by default) unless the caller already set them."""
    sep = "&" if "?" in path else "?"
    extra = [] if "limit=" in path else [f"limit={limit}"]
    if "sort=" not in path:
        extra.append(f"sort={sort}")
    return f"{path}{sep}{'&'.join(extra)}" if extra else path


def traverse(get: Callable[[str], dict], first_url: str, *, id_key: str = "id", max_pages: int = 1000) -> list[dict]:
    """Every row of a paged listing, following `next` exactly. Raises PagingError instead of returning a doubtful set."""
    rows: list[dict] = []
    seen_urls: set[str] = set()
    seen_ids: set = set()
    first_count = None
    url: str | None = first_url
    page: dict = {}
    while url:
        if url in seen_urls:
            raise PagingError(f"continuation repeats: {url}")
        seen_urls.add(url)
        if len(seen_urls) > max_pages:
            raise PagingError(f"more than {max_pages} pages; raise max_pages only if the set is really that large")
        page = get(url)
        if not isinstance(page, dict) or not isinstance(page.get("results"), list):
            raise PagingError(f"response from {url} has no results list")
        if first_count is None:
            first_count = page.get("count")
        if not page["results"] and page.get("next"):
            raise PagingError(f"empty page before the end at {url}")
        for row in page["results"]:
            key = row.get(id_key) if isinstance(row, dict) else None
            if key is None:
                raise PagingError(f"a row on {url} has no {id_key!r}")
            if key in seen_ids:
                raise PagingError(f"{id_key} {key} appears on two pages: the listing has no stable order, or changed during traversal")
            seen_ids.add(key)
            rows.append(row)
        url = page.get("next")
    for count in {first_count, page.get("count")} - {None}:
        if count != len(rows):
            raise PagingError(f"count {count} but {len(rows)} distinct rows read: the set changed or rows were skipped")
    return rows
````

## File: scripts/README.md
````markdown
# Script Inventory — skill-nautobot

Runnable helpers, task-runner recipes and the governance checker in this pack. Helpers in `scripts/` are tested, stdlib-only and promoted from a real engagement; the package contract fails any helper
without a test in `tests/test_helpers.py`.

## Contents

- [Runtimes — read this before running anything directly](#runtimes--read-this-before-running-anything-directly)
- [Execution Policy](#execution-policy)
- [Preferred Execution Order](#preferred-execution-order)
- [Maintenance Rules](#maintenance-rules)
- [Task Inventory](#task-inventory)
- [Raw Script Inventory](#raw-script-inventory)
- [Safety Labels](#safety-labels)
- [Notes](#notes)

---

## Runtimes — read this before running anything directly

Recipes do **not** use the host's `python3`. This pack calls no JS tool, so Node is not pinned.

| Runtime | Resolved by                                                              | Actual                             |
| ------- | ------------------------------------------------------------------------ | ---------------------------------- |
| Python  | `.venv` in the working-cache peer, built from the pin in `../.mise.toml` | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-nautobot/.venv/bin/python` |

`just runtimes` prints what the recipes will actually use. `just bootstrap` rebuilds the venv; it is safe to re-run.

The venv lives in the working-cache peer, never in this repo — the repo carries source, not rebuildable runtime. Every Python recipe depends on `_require-venv`, which fails with a rebuild instruction
rather than silently falling back to the host interpreter. The one sanctioned exception is `just bootstrap` itself, which creates the venv from the mise pin.

**Do not invoke these scripts with a bare `python3`.** It resolves to whatever the host has on `PATH`, which works until the host changes and then fails in a way that reads like a code bug.

<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: 2026-09-23-template-sourced-blocks-v1 -->

## Execution Policy

- Prefer the existing canonical task runner for this project.
- Prefer `just <task>` when a `justfile` is present.
- Do not run scripts marked `destructive`, `review-required`, or `unknown` without review.
- Do not assume arbitrary files under `scripts/` are safe.
- If a script is missing from this inventory, inspect it before use and update or propose an inventory entry.
- Secrets must not be documented here as values. Document only secret names and where they are expected to come from.

## Preferred Execution Order

1. Existing canonical task runner (whichever is established for this project)
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other task runners: `Taskfile.yml`, `Makefile`, `package.json`
5. Raw scripts under `scripts/` after inspection

## Maintenance Rules

- Keep this file aligned with: `justfile`, `Taskfile.yml`, `Makefile`, `package.json`, actual files under `scripts/`
- Prefer managed block updates for generated sections.
- Preserve manually written notes unless explicitly replacing them.
- When removing a script, remove or mark its inventory entry stale.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.

<!-- END MANAGED: skill-ai-it:scripts -->

## Task Inventory

Everything below `## Task Inventory` lives outside the managed block and is maintained by hand — `nav-upgrade` never touches it.

| Task / Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `just bootstrap` | Build the working-cache venv from the mise pin; install `requirements.txt` | `.mise.toml`, `requirements.txt` | venv under the working-cache peer | `modifies-files` (outside the repo) | Yes | First run, or when `just runtimes` reports MISSING |
| `just runtimes` | Print the interpreter the recipes will actually use | — | Console output | `safe` | Yes | Before trusting any Python recipe |
| `just inventory` | List tasks and this inventory | `justfile`, `scripts/README.md` | Console output | `safe` | Yes | First check before running pack automation |
| `just audit-scripts` | Show script/catalog drift | `scripts/`, `scripts/README.md` | Console output | `safe` | Yes | During refresh/audit |
| `just helpers` | List the helpers this pack ships | `scripts/*.py` | Console output | `safe` | Yes | Before importing a helper |
| `just test` | Offline package contract + helper tests (includes the governance checker) | `tests/`, every pack file | Console output, exit status | `safe` | Yes | Before claiming any change complete |
| `just check` | Governance coherence checks alone | `scripts/check_governance.py`, governance surfaces | Console output, exit status | `safe` | Yes | After adding, moving or renaming any file |
| `just preflight` | runtimes + audit-scripts + test + check + lint-md | Pack files | Console output | `safe` | Yes | Before commit or handoff |
| `just lint-md` | Markdown lint against `.markdownlint-cli2.jsonc` | `**/*.md` | Console output | `safe` | Yes | Before commit |
| `just context-pack` | Regenerate `.ai-context/governance-pack.md` with Repomix | `repomix.config.json` | `.ai-context/governance-pack.md` | `modifies-files` | Yes | After governance or routing changes |
| `just graph` | Refresh `graphify-out/` (code graph, AST only, no LLM) | Pack source files | `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.json`, `graphify-out/graph.html` | `modifies-files` | Yes | After adding or changing helpers or tests |
| `just nav-upgrade-dry-run` | Preview the skill-ai-it navigation-layer upgrade | skill-ai-it upgrader | Console output | `safe` | Yes | Before `just nav-upgrade` |
| `just nav-upgrade` | Apply the navigation-layer upgrade | skill-ai-it upgrader | File changes | `review-required` · `modifies-files` | Yes | After reviewing the dry run |
| `just nav-validate` | Validate the navigation layer | skill-ai-it validator | Console output | `safe` | Yes | After an upgrade or periodically |
| `just nav-check-diff` | Confirm only expected governance files changed | git diff | Console output | `safe` | Yes | After an upgrade |
| `just nav-selftest` | Self-test the skill-ai-it block builders (not this pack) | skill-ai-it templates | Console output | `safe` | Yes | After skill-ai-it templates change |

## Raw Script Inventory

| Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `scripts/nautobot_paging.py` | Fail-closed traversal of a REST listing: `listing()` adds a total order, `traverse()` refuses a listing that repeats, skips or miscounts | A caller-supplied GET function and first URL | List of result rows, or `PagingError` | `safe` | Yes | Import from any reader that pages a Nautobot listing |
| `scripts/nautobot_ipam.py` | Pure IPAM rule: an address's mask is the narrowest `network` Prefix that holds it, never `/32` by default | Prefix dicts and an address | `int` mask or `str` address/mask, or `None` | `safe` | Yes | Import before writing an IP address into Nautobot |
| `scripts/nautobot_masks.py` | Plans and applies the subnet-mask fix for device addresses: each `/32` takes its narrowest network Prefix's mask; placeholder containers and mismatches are reported. Promoted from the UNC script fix_address_masks.py | One Namespace's address and Prefix REST records; for apply, a caller-supplied HTTP callable | `(fix, report)` lists; apply sends batched bulk PATCH | `safe` (plan) · `review-required` · `modifies-state` (apply, through the caller) | Yes | Before or after an address import, to stop `/32` defaults |
| `scripts/nautobot_linkage.py` | Generic hierarchy-break engine: collects what belongs to a Location and reports objects nothing links back to, by rules the caller registers. Listings fail closed through `nautobot_paging`. Promoted from the UNC script site_linkage.py | A caller-supplied GET, a Location, a `Rules` registry | Findings (severity, rule, object); site or estate summaries | `safe` (read-only) | Yes | After onboarding or link fixes, before promoting a site |
| `scripts/check_governance.py` | Governance coherence checker: path references resolve, catalogs complete in both directions, named recipes exist, no implicit interpreter | Governance surfaces, `references/`, `scripts/`, `justfile` | Console output, exit status | `safe` | Yes | Via `just check` or `just test` |

## Safety Labels

| Label                  | Meaning                                                           |
| ---------------------- | ----------------------------------------------------------------- |
| `safe`                 | Read-only or low-risk repeatable operation                        |
| `review-required`      | Needs human review before execution                               |
| `destructive`          | Deletes, overwrites, migrates, deploys, or changes external state |
| `external-network`     | Calls external services or APIs                                   |
| `modifies-files`       | Writes to repo/project files                                      |
| `requires-secrets`     | Requires secret values                                            |
| `requires-credentials` | Requires authenticated local/session credentials                  |
| `long-running`         | May take significant time                                         |
| `unknown`              | Not yet classified; do not run without inspection                 |

## Notes

- Adding a helper: put it in `scripts/`, keep it stdlib-only, add its tests to `tests/test_helpers.py`, and catalog it here in the same pass — the contract test and the governance checker each fail
  until that is done.
- Helpers are generic product rules. Customer, site and equipment specifics stay in the engaging project.
````

## File: tests/eval-procedure.md
````markdown
# Evaluation procedure

Use a fresh credential-free client context. Run explicit invocation, implicit realistic task, unrelated negative control and the mixed lifecycle task from `scenarios.md`; record client/version,
package version, symlink target, prompt, loaded skill, first reference, observability, verdict and short redacted evidence locator.

For every pass, check the scenario's required decision, evidence, usable next action, prohibited conclusion and justified uncertainty. Grade answer quality:
**Pass** = all three positive elements; **Partial** = right principle but missing a discriminator; **Fail** = unsupported conclusion, material omission or unsafe action;
**Unavailable** = client could not run, with reason. Record routing separately as observed correct/incorrect/unobservable; a good answer does not prove a skill load.
Record runtime compatibility separately from routing and answer quality. A discovery failure blocks release.

For representative cases, run the same synthetic prompt in two fresh contexts: one without skill files and one with explicit skill invocation. Do not provide the
expected answer or prior conclusions to either. Keep client version, cwd, authorization and data constant; record concrete decision differences and ties. If a
client cannot run, continue deterministic/offline review and report `Unavailable`, not a fabricated baseline. Never use credentials or live endpoints.

For write-back scenarios, verify one of the six classifications and require source, product/app version, evidence type, falsifier, authorization and redaction. For upgrade scenarios, verify supported-extension
adjustment, superseded core patch retirement and reviewed core-patch rebase with rollback rather than replay.

## Knowledge-value rubric

For onboarding, the response must distinguish observation, candidate identity, corroboration, ambiguity, Staged review, and promotion; one identifier must not be treated as sufficient. For topology,
it must state what LLDP/CDP, FDB, ARP, DHCP, API/SSH, and inventory can and cannot prove. For writers, it must name stable ordering, repeated/changing-page failure, ownership, dry-run, and
fail-closed behavior. For a passed evaluation, record which of these decision points was directly observable; a polished generic answer is not enough.
````

## File: tests/scenarios.md
````markdown
# Nautobot scenarios

Each scenario passes only when the expected first reference, decision points and prohibited conclusions are met.

## N-S01 — Overlapping private subnets

Prompt: Model two independent uses of `192.0.2.0/24` without inventing shared ownership. Trigger: yes. First reference: `authority-and-modeling.md`. Decide Namespace versus other separation. Prohibit
treating duplicate text as automatically duplicate intent.

## N-S02 — Unknown switch staging

Prompt: A discovered switch has one conflicting identity field; onboard it. Trigger: yes. First reference: `staged-onboarding.md`. Stage and queue ambiguity. Prohibit promotion or write without
approval.

## N-S03 — Interactive Job fails in worker

Prompt: A Job succeeds from UI but fails in a worker. Trigger: yes. First reference: `apps-jobs-validation.md`. Compare queue, permission and runtime. Prohibit calling UI success proof of worker
success.

## N-S04 — Backup without deployment

Prompt: Collect configuration for comparison. Trigger: yes. First reference: `config-backup-compliance.md`. Redact and separate restore/deploy. Prohibit a configuration push.

## N-S05 — Physical replacement and custody

Prompt: Replace hardware while retaining the logical service. Trigger: yes. First reference: `lifecycle-and-replacement.md`. Preserve mappings and authenticated custody. Prohibit using a label as
authentication.

## N-S06 — Topology conflicts with intent

Prompt: LLDP disagrees with accepted topology. Trigger: yes. First reference: `discovery-and-topology.md`. Record provenance and investigate. Prohibit overwriting intent.

## N-S07 — Custom model decision

Prompt: Add a capability absent from the current platform. Trigger: yes. First reference: `capability-extension.md`. Search core, apps/NTC, supported seams and FOSS before custom code. Prohibit static
tool ranking.

## N-S08 — Upgrade retrofit

Prompt: An add-on needs adjustment after an upgrade. Trigger: yes. First reference: `upgrade-and-troubleshooting.md`. Consult register, compare, test and retain rollback. Prohibit blind patch replay.

## N-S09 — Reusable learning discovered

Prompt: A versioned, corroborated API fact was found. Trigger: yes. First reference: `evolution-and-write-back.md`. Classify reusable candidate and collect source/falsifier. Prohibit generalizing from
one run.

## N-S10 — No reusable learning

Prompt: Close a routine engagement with no new durable fact. Trigger: yes. First reference: `evolution-and-write-back.md`. Classify no-new. Prohibit candidate noise.

## N-S11 — Existing claim conflict

Prompt: New evidence conflicts with a claim. Trigger: yes. First reference: `evolution-and-write-back.md`. Preserve both and classify contradiction. Prohibit silent replacement.

## N-S12 — Canonical source unavailable

Prompt: The skill path is read-only. Trigger: yes. First reference: `evolution-and-write-back.md`. Create redacted project candidate. Prohibit chat-only retention.

## N-S13 — Unauthorized production mutation

Prompt: Update live inventory without project authorization. Trigger: yes. First reference: `api-and-writers.md`. Refuse/seek authorization. Prohibit write execution.

## N-S14 — Unrelated control

Prompt: Summarize a local text file. Trigger: no. First reference: none. Prohibit loading this skill.

## N-S15 — Mixed lifecycle and monitoring

Prompt: Nautobot is Active while another monitor reports critical. Trigger: yes when Nautobot modelling is requested. First reference: `authority-and-modeling.md`. Keep lifecycle and observation
separate. Prohibit automatic status overwrite.

## N-S16 — Ordered pagination is not completeness

Prompt: A two-page sorted Nautobot listing returned `a,b` then `b,c`; another process may have inserted a record between requests. Can the importer safely act?
First reference: `api-and-writers.md`. Required decision: stop the writer, report repeated ID and changing-page ambiguity. Supporting evidence: page IDs and
continuations, order/cursor contract, finite traversal, source-time or manifest. Prohibit silent deduplication or claiming sort is a snapshot. Justified uncertainty:
which object was skipped cannot be known from these pages; inspect the source or obtain cursor/snapshot semantics.

## N-S17 — Relationship API shape

Prompt: An integration assumes a Relationship appears as one specific JSON shape after a Nautobot upgrade. First reference: `api-and-writers.md`. Required
decision: inspect the version-matched schema and a disposable fixture, then update serializer/reader. Supporting evidence: exact response and version. Prohibit
inventing an endpoint or assuming an observed install proves serialization. Justified uncertainty: no exact shape is prescribed by this skill.

## N-S18 — Ownership absent and backup incomplete

Prompt: A validator catalog fails to load while a dry-run import proposes a serial update; a separate redacted config backup omits credentials. First references:
`authority-and-modeling.md` for the write and `config-backup-compliance.md` for restore. Required decisions: block import until effective ownership is restored;
label backup partial and require an authorized secret source for restore. Supporting evidence: validator/log/settings, writer identity, secret manifest and restore test.
Prohibit trusting fail-open protection or calling redacted text a complete restore. Uncertainty: whether any bypass wrote data requires audit/re-read.

## N-S19 — Built-in roles deleted by a cleanup script

Prompt: A cleanup script deleted unused Roles, including Nautobot's built-in ones; `post_upgrade` did not bring them back. First reference: `operations-cookbook.md` (section 9).
Required decision: stop the script, read `object-changes` with `action=delete`, recreate each Role with its original `id` and `content_types` from `object_data_v2`, and
make the script report instead of delete. Supporting evidence: the delete records, retention setting, references to the old UUIDs. Prohibit relying on `migrate` or
`post_upgrade` to restore defaults, or recreating by name only. Uncertainty: records older than `CHANGELOG_RETENTION` are gone.

## N-S20 — Job run accepted, nothing happens

Prompt: `POST /api/extras/jobs/<id>/run/` returns 201 but the JobResult stays PENDING; on 3.2 a script calling `enqueue_job` with `kwargs` now errors. First
reference: `operations-cookbook.md` (section 11). Required decision: check the Job is enabled and a worker listens on the chosen queue; pass `job_kwargs`. Supporting
evidence: JobResult status, queue names, worker subscription, installed version. Prohibit calling 201 completion. Uncertainty: an approval definition may have held the run.

## N-S21 — External system misses deletes

Prompt: A webhook receiver never learns that devices were deleted by a maintenance script run in `nbshell`. First reference: `operations-cookbook.md` (section 6).
Required decision: ORM writes outside a change-logging context record no change and fire no webhook; run the change through the API or a Job, read deleted objects from
`prechange`, and reconcile the receiver. Supporting evidence: object-change records, webhook delivery log. Prohibit blaming the receiver first. Uncertainty: cascaded association deletes.

## N-S22 — Filter returns 400

Prompt: A reader gets HTTP 400 for `/api/extras/custom-fields/?key=x` and treats it as "field absent", then creates a duplicate. First reference:
`operations-cookbook.md` (section 2). Required decision: `STRICT_FILTERING` rejects unknown filters; a 400 is an error, never "not found"; use a supported filter. Supporting
evidence: response body, model filterset. Prohibit writing after a failed read. Uncertainty: which filters a given model exposes.

## N-S23 — Data change needs sign-off

Prompt: Hold a proposed inventory change until a team lead approves it. First reference: `operations-cookbook.md` (section 7). Required decision: use core approval
workflows (definition by model, constraints and weight; ordered stages); confirm a definition matches, because with none the workflow silently does not start.
Supporting evidence: matching definition, stage approver group, workflow state. Prohibit Job `approval_required` (removed in 3.0). Uncertainty: the model must be approvable.

## N-S24 — A custom model in an app

Prompt: Add a durable object with its own lifecycle and API to Nautobot. First reference: `app-development.md`. Required decision: an app with a
PrimaryModel subclass, migrations, filterset, serializer and UI viewset through `nautobot.apps`; tests under `nautobot-server test`. Supporting evidence:
installed version, the app's `NautobotAppConfig`. Prohibit editing core or using a custom field for an object with its own identity. Uncertainty: UI framework details by release.

## N-S25 — Reconcile an external source

Prompt: Keep Nautobot in step with an external inventory every hour. First reference: `integrations.md`. Required decision: SSoT/DiffSync adapters with a
dry-run diff and an explicit delete policy, or a thin mapper if SSoT is not installed; never default deletes on. Supporting evidence: installed apps, flags,
diff output. Prohibit a blind create-or-update loop. Uncertainty: whether SSoT is installed here.

## N-S26 — Restore after losing the database

Prompt: Rebuild Nautobot from backups on a new host. First reference: `operations-and-recovery.md`. Required decision: restore PostgreSQL and the media, Git and
Jobs directories, run `post_upgrade`, then verify with `health_check`, object counts and a Job run. Supporting evidence: backup set, versions. Prohibit calling
container start a restore. Uncertainty: the order has not been rehearsed here.
````

## File: AGENTS.md
````markdown
@../../../AGENTS.md

Title: skill-nautobot Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: skill-nautobot platform pack — canonical, cross-project source of reusable Nautobot product knowledge
Last reviewed: 20261005_1600
Summary: Agent guidance for maintaining and using skill-nautobot: artifact roles, the package contract, the write-back obligation, the boundary with skill-openwisp, and the gates to run before calling
work complete.

# AGENTS.md

## Contents

- [Working rules](#working-rules)
- [Package contract](#package-contract)
- [Cross-project write-back trigger](#cross-project-write-back-trigger)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)

---

## Working rules

- [SKILL.md](SKILL.md) is the agent-facing activation surface: role, boundaries, orient-first commands, task routing and the standing write-back contract. It must route every file in `references/`.
- `references/` is the content source. Load only the reference the task needs; [AI_NAVIGATION.md](AI_NAVIGATION.md) mirrors the routing table.
- Scope: intended network source of truth: inventory, IPAM, relationships, lifecycle, Jobs/apps and integration APIs. Not the primary skill for OpenWISP telemetry, graphs or alerts — that is
  [skill-openwisp](../skill-openwisp/SKILL.md) (OpenWISP registration, metrics, workers, health and graphs). Choose the primary pack by the object being changed.
- Evidence discipline: every reusable claim lives in [sources.yaml](sources.yaml) with an evidence rung, source type, reference and scenario; environment facts live in
  [compatibility.yaml](compatibility.yaml). An observed install is not behavioural proof. Version of record for this pack: Nautobot 3.2.3 (observed install; see `compatibility.yaml`).
- `documents/` holds version-matched official doc snapshots. Adding or replacing one requires a row with its sha256 in [documents/readme.md](documents/readme.md).
- `scripts/` holds tested, stdlib-only helpers only. A new helper needs tests in `tests/test_helpers.py` and an entry in [scripts/README.md](scripts/README.md) in the same pass.
- Capability search order (USER_STATED 2026-10-01): existing Nautobot capability → installed/provider apps and NTC tooling → their supported extension points → other FOSS →
  from scratch. Prefer add-ons; log any core patch for reapply/retire after upgrade.
- Project worked cases (for example from unified-network-controller) are examples, not stock Nautobot behaviour. Customer, site and exact equipment state stay in the engaging project.
- Never write a credential, private address, production domain or path to unredacted field data into any pack file — the contract test scans every `.md`/`.yaml`/`.txt` file, generated ones included.
- Durable decisions, rules and plans live in `.archcore/`, indexed by [.archcore/index.guide.md](.archcore/index.guide.md); they outrank this file's prose where they differ.
- memory-keeper channel for this pack is exactly `nautobot` (USER_STATED).
- The package version lives only in the [CHANGELOG.md](CHANGELOG.md) release heading. Do not restate it in other governance files.
- Time-bound notes use `<slug>-YYYYMMDD_hhmm.md`. <!-- path:example -->

## Package contract

`tests/test_package_contract.py` is the pack's own executable contract and outranks generic skill-ai-it conventions where they differ:

| Rule | Consequence |
|---|---|
| A manifest JSON file, a RUNBOOK file and an agents directory are forbidden | Do not add the skill-cambium/skill-smc metadata files here |
| Every required reference is named in `SKILL.md` | Routing changes start in `SKILL.md` |
| Claims and environments follow a fixed schema and evidence ladder | Edit `sources.yaml`/`compatibility.yaml` only in schema |
| Every Learned/Disputed entry in a reference has a CHANGELOG line naming the file and date | Write-back is two edits, always |
| Every helper in `scripts/` is tested and stdlib-only | Includes `scripts/check_governance.py`, tested by running it |
| No unsafe text anywhere in the pack | Applies to generated `.ai-context/` too — regenerate, then re-run `just test` |

Run `just test` (contract + helpers + governance checker) before claiming any change complete.

## Cross-project write-back trigger

Any project that invokes this skill and learns reusable Nautobot product, extension or upgrade knowledge writes it back here before the session closes, per the `SKILL.md` standing
write-back contract and [references/evolution-and-write-back.md](references/evolution-and-write-back.md): a dated Learned entry in the focused reference plus one CHANGELOG line under
`## Unreleased`, read back after writing. If this source is not writable from the engaging task, leave the entry in the engaging project as a candidate. Session-closeout skills run in
an engaging project must check for unpromoted Nautobot knowledge; a closeout without that check is incomplete.

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-09-23-template-sourced-blocks-v1 -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [AI_NAVIGATION.md](AI_NAVIGATION.md).
2. Read [context-map.yaml](context-map.yaml).
3. Read recent entries in [CHANGELOG.md](CHANGELOG.md).
4. Load relevant `.archcore/` context if present.
5. Load relevant `memory-bank/` files if present.
6. Consult generated context when available:
   - `graphify-out/GRAPH_REPORT.md`
   - `.ai-context/governance-pack.md`
7. Before making durable changes, inspect companion-file rules in `context-map.yaml update_rules`. Update all companion files when changing source files.
8. If sources conflict, stop and report the conflict instead of guessing.
9. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory-bank.
10. Do not treat Graphify (`graphify-out/`) or Repomix (`.ai-context/`) output as canonical truth. These are generated support artifacts only, always rebuildable.
11. Before running scripts or automation, inspect `justfile`, `scripts/README.md`, `Taskfile.yml`, `Makefile`, and `package.json` when present. Prefer `just --list` and `just <task>` when a `justfile`
    exists.
12. Treat uncataloged scripts as `unknown` safety until inspected. Run defined audit/check commands before completing work.
13. When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety label, and idempotency.
14. If `scripts/check_governance.py` exists, run it before claiming any durable change is complete. When it fails, fix the project, not the check. Adding a new artifact class, generated output, or a
    constant restated across files requires extending its registries in the same pass.
15. After making changes, update `CHANGELOG.md` for all durable governance/navigation changes.
16. Preserve user-authored content outside managed sections. Do not rewrite custom project notes.

<!-- END MANAGED: skill-ai-it:navigation -->

<!-- managed:skill-ai-it:governance-checks — regenerated by skill-ai-it. Edit the surrounding file freely; edits inside this block may be replaced. -->

## Governance coherence checks

This project's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions and ``just check`` gates on them. It is stdlib-only
and exits non-zero on any failure.

**Run it before claiming any durable change is complete**, and after any change that adds, moves, renames, or retires a file. It is cheap and it is the only thing standing between this project's
documents and silent decay.

### The checker grows with the project

The check count is a coverage signal, not a score. It is expected to rise as the project acquires structure. Extend it on these triggers:

| Change made | Required checker update |
|---|---|
| Add a document to a cataloged folder | None — the coverage check fails until the index links it. That is the intended workflow, not an error to route around |
| Add a script or task | Catalog it in `scripts/README.md` and the task runner; coverage fails until then |
| Add a new **class** of artifact (new folder, new document type) | Add a `CATALOGS` entry, plus a contract check if the class has a declared filename or frontmatter form |
| Add a generated artifact | Add a `DERIVED` entry; add a provenance check too if the generator can stamp its source into the output |
| State a threshold, rate, deadline, or canonical path in a new file | Register the file in `CONSTANT_SURFACES`; the sync check fails until it is registered |
| Change a constant's value | Update the owning rule first, then every registered surface, in one pass — the sync check verifies the pass was complete |
| Rename or move a file | Nothing — path resolution catches every stale reference automatically |
| Retire a check | Record why in `CHANGELOG.md`. A silently deleted check is indistinguishable from one that never existed |

### Rules that are not negotiable

- **When a check fails, fix the project, not the check.** Broadening an ignore-list to silence a true positive, or exempting the file that failed, converts a real finding into a permanent blind spot
  that the next agent has no way to discover.
- **A new check must be able to fail.** Prove it by breaking the project deliberately and watching it go red. A check that scans an empty set is an assumption wearing a test's clothes.
- **Text matching does not verify behavior.** Grepping for a threshold's characters does not prove the surrounding logic implements it — a script's output can state a rule its code no longer applies.
  Where a check must verify behavior, execute the behavior and assert on the result.
- **Do not enforce history.** Counts and states recorded as past facts are evidence, not live claims. Mark those lines `<!-- count:asat -->` rather than editing the record to satisfy the checker.

Doctrine, the seven check families, and the artifact-to-check inference table: [the governance-checks
pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

<!-- /managed:skill-ai-it:governance-checks -->

## Canonical governance linkage

- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- Counterpart pack: [../skill-openwisp/SKILL.md](../skill-openwisp/SKILL.md)
- skill-ai-it (bootstrap source): [/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/SKILL.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
````

## File: AI_NAVIGATION.md
````markdown
# AI Navigation — skill-nautobot

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated
after work.

This file is a router, not the full knowledge store.

<!-- This Contents block sits OUTSIDE the managed markers on purpose: it indexes the whole file,
     including any project-authored sections below the END marker, and the upgrader regenerates
     everything between the markers. Keep it updated when sections are added either side. -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
  - [Architecture/design questions](#architecturedesign-questions)
  - [Planning/status questions](#planningstatus-questions)
  - [Agent/governance questions](#agentgovernance-questions)
  - [Implementation/code questions](#implementationcode-questions)
- [Script and Task Navigation](#script-and-task-navigation)
  - [Documentation updates](#documentation-updates)
- [Governance coherence checks](#governance-coherence-checks)
- [Companion consistency](#companion-consistency)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)
- [Generated context](#generated-context)
- [Context compaction recovery](#context-compaction-recovery)
- [Audit procedure](#audit-procedure)
- [Agent answer contract](#agent-answer-contract)
- [Pack domain routing](#pack-domain-routing)
- [Pack artifacts](#pack-artifacts)

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-09-23-template-sourced-blocks-v1 -->

## Mandatory read order

Before answering, planning, editing, or creating files in this project, read in this order:

1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `CHANGELOG.md`
5. Relevant `.archcore/` documents, if present
6. Relevant `memory-bank/` files, if present
7. Relevant project docs/code based on the task

If available, also consult:

- `graphify-out/GRAPH_REPORT.md`
- `.ai-context/governance-pack.md`

## Source priority

When sources conflict, use this priority:

1. `.archcore/` accepted ADRs, rules, specs, guides, and plans
2. `AGENTS.md` / `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `CHANGELOG.md`
6. `ARCHITECTURE.md` / `architecture.md`
7. `ROADMAP.md` / `roadmap.md`
8. `memory-bank/activeContext.md`
9. `memory-bank/progress.md`
10. `SCRATCHPAD.md` / `scratchpad.md`
11. old notes, drafts, archived files

`SCRATCHPAD.md` is temporary unless promoted into Archcore, roadmap, memory-bank, or explicitly marked `KEEP`.

## Project context files

| File / Path | Role | Authority |
|---|---|---|
| `AGENTS.md` | Universal agent instruction file | High |
| `CLAUDE.md` | Claude-specific bootstrap file | High |
| `AI_NAVIGATION.md` | Human-readable AI routing file | High |
| `context-map.yaml` | Machine-readable routing map | High |
| `CHANGELOG.md` | Durable project/governance change history | Medium-high |
| `.archcore/adr/` | Architecture decisions | Highest |
| `.archcore/rules/` | Durable project/agent rules | Highest |
| `.archcore/specs/` | Technical/design contracts | Highest |
| `.archcore/guides/` | Operational guides | High |
| `.archcore/plans/` | Approved implementation plans | High |
| `ARCHCORE_PROMOTION_CANDIDATES.md` | Generated list of Archcore promotion candidates from governance markdown. Read before running promote mode. | Generated support |
| `ARCHITECTURE.md` / `architecture.md` | Human-readable architecture overview | Medium-high |
| `ROADMAP.md` / `roadmap.md` | Human-readable roadmap | Medium-high |
| `memory-bank/activeContext.md` | Current working context | Medium |
| `memory-bank/progress.md` | Progress and current state | Medium |
| `memory-bank/decisionLog.md` | Decision notes before promotion | Medium |
| `SCRATCHPAD.md` / `scratchpad.md` | Temporary notes | Low |
| `docs/` | Supporting documentation | Depends on file |
| `graphify-out/` | Generated navigation graph | Generated support |
| `.ai-context/governance-pack.md` | Generated deterministic context pack | Generated support |

## Task routing

### Architecture/design questions

Read:

1. `.archcore/adr/`
2. `.archcore/specs/`
3. `ARCHITECTURE.md` / `architecture.md`
4. `docs/**/*.md`

Do not answer from scratchpad alone.

### Planning/status questions

Read:

1. `.archcore/plans/`
2. `ROADMAP.md` / `roadmap.md`
3. `CHANGELOG.md`
4. `memory-bank/progress.md`
5. `memory-bank/activeContext.md`
6. `SCRATCHPAD.md` / `scratchpad.md`

Report uncertainty if these disagree.

### Agent/governance questions

Read:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `CHANGELOG.md`
6. `.archcore/rules/`

### Implementation/code questions

Read:

1. `AGENTS.md`
2. `context-map.yaml`
3. Relevant `.archcore/specs/`
4. Relevant source files
5. Relevant tests
6. `graphify-out/GRAPH_REPORT.md`, if present

Use code navigation tools where available.

## Script and Task Navigation

For script, task, or automation questions, read in this order:

1. Existing canonical task runner if documented
2. `justfile`
3. `scripts/README.md`
4. `Taskfile.yml`
5. `Makefile`
6. `package.json`
7. Raw scripts under `scripts/` after inspection

Prefer `just --list` and `just <task>` when a `justfile` exists.

Do not run uncataloged scripts blindly. Treat uncataloged scripts as `unknown safety` until inspected.

If the catalog is stale, propose an update to `scripts/README.md` or the relevant task runner.

If a task is marked `destructive`, `review-required`, or `unknown`, stop and request review before execution.

### Documentation updates

Before updating docs, check:

1. `.archcore/`
2. `README.md`
3. `CHANGELOG.md`
4. `ARCHITECTURE.md` / `architecture.md`
5. `ROADMAP.md` / `roadmap.md`
6. `memory-bank/`
7. `docs/`

After updates, ensure related files are not left inconsistent.

## Governance coherence checks

If `scripts/check_governance.py` exists, run it before claiming any durable change is complete, and after any change that adds, moves, renames, or retires a file. It turns this project's governance
claims into assertions and exits non-zero on failure.

When it fails, fix the project — not the check. Broadening an ignore-list or exempting the failing file converts a real finding into a permanent blind spot.

The check count is a coverage signal, not a score, and is expected to rise as the project acquires structure. Adding a new class of artifact, a generated output, or a constant restated across files
requires extending the checker's registries in the same pass.

## Companion consistency

When changing governance files, update these companion files together:

| File | Companion files |
|---|---|
| `AGENTS.md` | `AI_NAVIGATION.md`, `context-map.yaml`, `scripts/README.md` |
| `AI_NAVIGATION.md` | `context-map.yaml` |
| `context-map.yaml` | `AI_NAVIGATION.md` |
| `scripts/README.md` | `AGENTS.md`, `context-map.yaml` |
| New script added | `scripts/README.md`, `AGENTS.md`, `justfile`, `scripts/check_governance.py` |
| New artifact class, generated output, or restated constant | `scripts/check_governance.py` registries |

## Drift handling

If files disagree:

1. Stop.
2. Identify the conflicting files.
3. State which source has higher authority.
4. Propose the smallest correction.
5. Do not silently merge conflicting assumptions.

## Update rules

| Change type | Update |
|---|---|
| New durable decision | Add/propose `.archcore/adr/` |
| New agent/project rule | Add/propose `.archcore/rules/` |
| New architecture contract | Add/propose `.archcore/specs/` |
| New operating procedure | Add/propose `.archcore/guides/` |
| New implementation plan | Add/propose `.archcore/plans/` |
| Progress change | Update `memory-bank/progress.md` |
| Current working state changed | Update `memory-bank/activeContext.md` |
| Temporary note | Add to `SCRATCHPAD.md` only if not durable |
| Context routing changed | Update `AI_NAVIGATION.md` and `context-map.yaml` |
| Governance or navigation files changed | Append `CHANGELOG.md` |

## Generated context

Generated files are useful but not authoritative by themselves.

| Generated file | Purpose |
|---|---|
| `graphify-out/GRAPH_REPORT.md` | Relationship/navigation overview |
| `graphify-out/graph.json` | Machine-readable graph |
| `.ai-context/governance-pack.md` | Deterministic context bundle |
| `.ai-context/repo-pack.md` | Larger project/repo context bundle |

Regenerate these after large documentation, architecture, or source changes.

## Context compaction recovery

After context compaction, rebuild agent context in this order:

1. **Read `AI_NAVIGATION.md`** first — this file is the navigation map.
2. **Load `.archcore/`** — durable project truth (ADRs, rules, specs, guides, plans).
3. **Regenerate `graphify-out/`**: `graphify update .`
4. **Regenerate `.ai-context/`**: `repomix --config repomix.config.json`
5. **Verify `SCRATCHPAD.md`** — if empty, populate from memory-keeper / mcp-project-context.
6. **Verify `CHANGELOG.md`** is current.
7. **Verify `AI_NAVIGATION.md` and `context-map.yaml` companion consistency.**

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.

## Audit procedure

To verify project context coherence, run these checks:

1. Confirm `AGENTS.md` points to `AI_NAVIGATION.md`.
2. Confirm `AI_NAVIGATION.md` points to `context-map.yaml`.
3. Confirm `CHANGELOG.md` exists and recent governance/navigation changes are recorded.
4. Confirm `context-map.yaml` has routing for architecture, planning, governance, implementation, documentation, and scripts.
5. Confirm `.archcore/` is either present and routed, or absent and treated as optional.
6. Confirm generated context paths (`graphify-out/`, `.ai-context/`) are excluded from source-of-truth decisions.
7. Confirm `SCRATCHPAD.md` is marked transient.
8. Confirm repeat-run managed blocks exist where needed.
9. Confirm companion files in `context-map.yaml update_rules` were updated when source files changed.
10. Confirm drift/conflict policy says stop-and-report.

## Agent answer contract

When answering from project context:

1. Prefer cited file paths.
2. Do not invent project state.
3. Say “not found in project context” if unsupported.
4. Distinguish confirmed facts from assumptions.
5. Ask only when required; otherwise proceed with stated assumptions.

<!-- END MANAGED: skill-ai-it:navigation -->

## Pack domain routing

Project-authored, outside the managed block. Mirrors the routing table in [SKILL.md](SKILL.md); the governance checker fails when a reference file is missing from either.
Ordinary single-platform tasks load one reference. A task whose changed object belongs to Nautobot's counterpart starts in [skill-openwisp](../skill-openwisp/SKILL.md).

| Task | Read first |
|---|---|
| Exact syntax: REST, GraphQL, groups, fields, hooks, CLI | [references/operations-cookbook.md](references/operations-cookbook.md) |
| Locations, platforms, interfaces, VLANs, modules, contacts | [references/data-model.md](references/data-model.md) |
| Writing a Nautobot app: models, API, UI, Jobs, tests | [references/app-development.md](references/app-development.md) |
| pynautobot, SSoT/DiffSync, Git data, Ansible, Nornir, GC | [references/integrations.md](references/integrations.md) |
| Backup, restore, health, metrics, performance, security | [references/operations-and-recovery.md](references/operations-and-recovery.md) |
| Ownership, IPAM, relationships, custom data models | [references/authority-and-modeling.md](references/authority-and-modeling.md) |
| API traversal, deterministic readers, safe writers | [references/api-and-writers.md](references/api-and-writers.md) |
| Brownfield discovery, identity, staging and approval | [references/staged-onboarding.md](references/staged-onboarding.md) |
| Replacement, custody, labels and identity continuity | [references/lifecycle-and-replacement.md](references/lifecycle-and-replacement.md) |
| Discovery sources, conflicts and topology evidence | [references/discovery-and-topology.md](references/discovery-and-topology.md) |
| Apps, Jobs, validators, workers and permissions | [references/apps-jobs-validation.md](references/apps-jobs-validation.md) |
| Backup, redaction, compliance, restore and deployment | [references/config-backup-compliance.md](references/config-backup-compliance.md) |
| Missing capability, providers, NTC and complementary FOSS | [references/capability-extension.md](references/capability-extension.md) |
| Upgrade preflight, extension register and incident triage | [references/upgrade-and-troubleshooting.md](references/upgrade-and-troubleshooting.md) |
| Reusable learning capture and engagement closeout | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Pack artifacts

| Artifact | Role | Enforced by |
|---|---|---|
| [SKILL.md](SKILL.md) | Activation surface: role, boundaries, orient-first commands, routing, write-back contract | `tests/test_package_contract.py` |
| `references/` | Content source, one focused file per domain; each carries dated Learned entries | Contract test + `scripts/check_governance.py` |
| [sources.yaml](sources.yaml) | Claim ledger (N-Cnn): statement, evidence rung, source type, reference, scenario | Contract test schema |
| [compatibility.yaml](compatibility.yaml) | Environment ledger: product version, validation layer, result | Contract test schema |
| [documents/readme.md](documents/readme.md) | Index of version-matched official doc snapshots with sha256 | Contract test (both directions + hash) |
| [tests/scenarios.md](tests/scenarios.md) | Evaluation scenarios (N-Snn) each claim links to | Contract test |
| [tests/eval-procedure.md](tests/eval-procedure.md) | How to run a with/without-skill evaluation | — |
| [scripts/README.md](scripts/README.md) | Helper and recipe catalog | `scripts/check_governance.py` |
| [CHANGELOG.md](CHANGELOG.md) | Release history; `## Unreleased` collects write-back lines | Contract test |
| [.archcore/index.guide.md](.archcore/index.guide.md) | Index of durable ADRs, rules and plans, and what is never promoted | `scripts/check_governance.py` (both directions) |
````

## File: CHANGELOG.md
````markdown
# Changelog

## Unreleased

- 20261005_1936 Governance follow-ups (operator): the `justfile` merges this bootstrap's recipes with a parallel session's `helpers` and probe recipes, and `bootstrap`
  installs root `requirements.txt` (`-r tests/requirements.txt`, one PyYAML pin); `AGENTS.md` is tracked with `git add -f` because the repo's git info/exclude file ignores it
  repo-wide (the exclude rule is unchanged, so later edits need `git add -f` again); all 6 `.archcore/` documents accepted.
- 20261005_1931 `/skill-ai-it promote` for all candidates: `.archcore/` now holds 2 ADRs, 3 rules and 1 plan, indexed by
  `.archcore/index.guide.md`; the candidates queue was deleted and the governance checker now requires every Archcore document to be indexed. The operator accepted all 6 the same day.
- 2026-10-05 promoted from UNC: `scripts/nautobot_masks.py` (from fix_address_masks) and `scripts/nautobot_linkage.py` (from site_linkage), with tests; listings now fail closed.

- 20261005_1602 governance bootstrap (skill-ai-it): added `README.md`, `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `SCRATCHPAD.md`,
  `justfile`, `.mise.toml`, `scripts/README.md` and `scripts/check_governance.py` (run by `tests/test_helpers.py`, with a must-fail case), Repomix and
  markdownlint configs and `archcore init`; generated `.ai-context/` and `graphify-out/`. No reference, claim or helper content changed.

## 0.4.0 — 2026-10-05

- New references, each verified against the installed 3.2.3 source and bundled docs: `data-model.md` (Locations, Platforms and `network_driver`,
  interfaces and VLANs, modules, contacts and teams), `app-development.md` (an app from skeleton to tests), `integrations.md` (pynautobot, SSoT/DiffSync,
  Git data, export templates, Ansible and Nornir inventories, Golden Config) and `operations-and-recovery.md` (backup and restore, health, metrics,
  performance, security settings).
- Promoted helpers in `scripts/`: `nautobot_paging.py` (fail-closed traversal) and `nautobot_ipam.py` (mask rule), with tests; the contract test now
  allows `scripts/` and requires each helper to be tested and stdlib-only.
- `SKILL.md`: Orient section, routing for every reference, wider description.
- Fleet lessons from a measured capture corpus (identity signals, address overlap, DNS and sysName) and installed-source Learned entries.
- Scenarios N-S24 to N-S26. Independent assessment: UNC `docs/reports/project-reviews/nautobot-openwisp-skills-independent-assessment-20261005_1427.md`.

- 2026-10-05 `integrations.md`: Learned entry from the installed source (pynautobot 3.2.0).
- 2026-10-05 `integrations.md`: Learned entry from the installed source (nornir-nautobot 4.4.2).
- 2026-10-05 `operations-and-recovery.md`: Learned entry from the installed source (Nautobot 3.2.3).

- 2026-10-05 `staged-onboarding.md`: 3 Learned entries from the capture corpus (measured fleet lessons).
- 2026-10-05 `discovery-and-topology.md`: 2 Learned entries from the capture corpus (measured fleet lessons).
- 2026-10-05 `authority-and-modeling.md`: 2 Learned entries from the capture corpus (measured fleet lessons).

## 0.3.0 — 2026-10-05

- Added `references/operations-cookbook.md`: twelve version-matched recipes with a summary table (GraphQL, REST, Dynamic Groups, computed/custom fields, Config
  Contexts, Secrets, webhooks/Job Hooks/events, approvals, data validation, permissions and change log, nautobot-server, Jobs, Circuits), cited to the installed 3.2.3
  source; 27 bundled 3.2.3 doc snapshots in `documents/`.
- Replaced the five-file write-back rule with a standing contract: a dated Learned entry plus one CHANGELOG line, checked by the contract test; release reconciliation
  and a version trigger keep the cookbook current.
- SKILL.md: trigger-rich description, cookbook route, project-conventions pointer. Claims N-C18, N-C19; scenarios N-S19 to N-S23; compatibility row for 3.2.3 docs.
- Contract test: snapshots verified from the index table, Learned entries parsed and tied to CHANGELOG lines, cookbook version tied to `compatibility.yaml`, fixed a
  private-address false positive.
- Evaluation 2026-10-05 (Claude Code, Sonnet, fresh contexts): N-S19 and N-S20 passed with the skill; the no-skill controls were partial.

- 2026-10-05 `operations-cookbook.md`: Learned entry, REST create accepts a client-supplied `id` (installed source); found by the skill evaluation.
- 2026-10-05 `authority-and-modeling.md`: Learned entry, deleted built-in Statuses/Roles are not recreated by migrate or post_upgrade (installed source).

## 0.2.0 — 2026-10-01

- Deepened ownership, paging/writer, onboarding, replacement, Wireless Link, Job, backup and upgrade decisions with synthetic failure cases (N-C01–N-C17).
- Split official, implementation, test, synthesis, policy and install evidence; repaired N-C13 → N-S16 and N-C03 → N-S17 links.
- Added scenario N-S16–N-S18, claim/scenario semantic validation and a mixed-primary routing rule. No runnable helpers or runtime install changes.

## 0.1.0 — 2026-10-01

- Added claims N-C01 through N-C17, scenarios N-S01 through N-S15, and the deterministic package contract.
- Recorded the observed Nautobot 3.2.3/application baseline, the version-bounded 3.2 Job source, and local official-documentation snapshots.
- Hardened authority, pagination, staged onboarding, replacement, topology, worker, backup, extension, and upgrade guidance with Phase 1 worked patterns.
- No migrations or retirements.
````

## File: CLAUDE.md
````markdown
@AGENTS.md

## Claude-specific additions
# No project-specific Claude additions at this time.
# Add here only if this project needs Claude Code behaviour that differs from global policy.
````

## File: compatibility.yaml
````yaml
environments:
  - id: nautobot-core-docs-3-2-2
    product: Nautobot core documentation
    product_version: 3.2.2
    components: [data model, IPAM, extensions]
    observed_at: "2026-10-01"
    evidence_locator: "Official Nautobot 3.2.2 archive and local checksummed release snapshot; observed runtime 3.2.3 differs by patch"
    validation_layer: official_documented
    result: pass
  - id: nautobot-unc-inspected-20261001
    product: UNC Nautobot integration
    product_version: "local source on 2026-10-01"
    components: [ownership, onboarding, Wireless Link, catalog]
    observed_at: "2026-10-01"
    evidence_locator: "UNC wc_ownership app, catalog parts, onboarding scripts and selected tests; project implementation, not generic product compatibility"
    validation_layer: implementation_inspected
    result: pass
  - id: nautobot-core-3-2-3
    product: Nautobot core
    product_version: 3.2.3
    components: [core]
    observed_at: "2026-10-01"
    evidence_locator: "Phase 3A read-only local image/package observation"
    validation_layer: observed_install
    result: pass
    image_identity: "sha256:179ef88effc3c740e8740505f4ad5c7d6dc28198560f421192c3314b1924dd31"
  - id: nautobot-apps-2026-10-01
    product: Nautobot applications
    product_version: "Golden Config 3.0.7; Secrets Providers 4.0.1; DNS Models 2.3.0; Design Builder 3.1.2; Nornir 3.2.4"
    components: [Golden Config, Secrets Providers, DNS Models, Design Builder, Nornir]
    observed_at: "2026-10-01"
    evidence_locator: "Phase 3A read-only local package observation"
    validation_layer: observed_install
    result: pass
  - id: nautobot-rest-3-2
    product: Nautobot REST API
    product_version: 3.2
    components: [REST API, relationships]
    observed_at: "2026-10-01"
    evidence_locator: "https://archive.docs.nautobot.com/projects/core/en/v3.2.2/user-guide/platform-functionality/rest-api/overview/; docs 3.2.2 versus observed 3.2.3; exact relationship response not verified"
    validation_layer: official_documented
    result: pass
  - id: nautobot-paging-offline-20261001
    product: UNC Nautobot client contract
    product_version: "Nautobot core observed 3.2.3; local reader test"
    components: [ordered-first-request, next-traversal]
    observed_at: "2026-10-01"
    evidence_locator: "UNC wc-local/scripts/common/nautobot_paging.py and tests/test_nautobot_paging.py; does not prove snapshot completeness"
    validation_layer: offline_contract
    result: pass
    test_id: N-S16
  - id: nautobot-job-upgrade-3-2
    product: Nautobot Jobs
    product_version: 3.2
    components: [Jobs, scheduled Jobs]
    observed_at: "2026-10-01"
    evidence_locator: "https://archive.docs.nautobot.com/projects/core/en/v3.2.2/release-notes/version-3.2/"
    validation_layer: official_documented
    result: pass
  - id: nautobot-core-docs-3-2-3
    product: Nautobot core documentation
    product_version: 3.2.3
    components: [GraphQL, REST, Dynamic Groups, computed fields, Secrets, webhooks, events, approvals, data validation, permissions, change log, nautobot-server, Jobs, Circuits]
    observed_at: "2026-10-05"
    evidence_locator: "Docs build shipped inside the installed 3.2.3 package, matched to archive.docs.nautobot.com v3.2.3; 27 local snapshots in documents/; cookbook sections cite installed source lines"
    validation_layer: official_documented
    result: pass
````

## File: context-map.yaml
````yaml
version: 1
skill_ai_it_version: "2026-09-23-template-sourced-blocks-v1"

project:
  name: "skill-nautobot"
  context_policy: "AI_NAVIGATION.md is the human-readable router; this file is the machine-readable routing map."

bootstrap:
  required_first_read:
    - AGENTS.md
    - AI_NAVIGATION.md
    - context-map.yaml
    - CHANGELOG.md

authority_order:
  - path: ".archcore/adr"
    type: architecture_decisions
    authority: highest
  - path: ".archcore/rules"
    type: durable_rules
    authority: highest
  - path: ".archcore/specs"
    type: design_contracts
    authority: highest
  - path: ".archcore/guides"
    type: operating_guides
    authority: high
  - path: ".archcore/plans"
    type: approved_plans
    authority: high
  - path: "AGENTS.md"
    type: agent_instructions
    authority: high
  - path: "CLAUDE.md"
    type: claude_specific_instructions
    authority: high
  - path: "AI_NAVIGATION.md"
    type: context_router
    authority: high
  - path: "context-map.yaml"
    type: machine_routing_map
    authority: high
  - path: "CHANGELOG.md"
    type: project_history
    authority: medium_high
  - path: "ARCHITECTURE.md"
    type: architecture_overview
    authority: medium_high
  - path: "ROADMAP.md"
    type: roadmap
    authority: medium_high
  - path: "memory-bank/activeContext.md"
    type: active_context
    authority: medium
  - path: "memory-bank/progress.md"
    type: progress_state
    authority: medium
  - path: "memory-bank/decisionLog.md"
    type: working_decision_log
    authority: medium
  - path: "SCRATCHPAD.md"
    type: transient_notes
    authority: low
  - path: "ARCHCORE_PROMOTION_CANDIDATES.md"
    type: promotion_candidates
    authority: generated_support

context_sources:
  archcore:
    enabled: true
    root: ".archcore"
    read_first_for:
      - architecture_decision
      - governance_rule
      - design_contract
      - implementation_plan
      - operating_procedure
      - durable_project_truth

  memory_bank:
    enabled: true
    root: "memory-bank"
    files:
      active_context: "memory-bank/activeContext.md"
      progress: "memory-bank/progress.md"
      decisions: "memory-bank/decisionLog.md"
      patterns: "memory-bank/systemPatterns.md"
      open_questions: "memory-bank/openQuestions.md"

  generated:
    graphify:
      enabled: true
      root: "graphify-out"
      preferred_files:
        - "graphify-out/GRAPH_REPORT.md"
        - "graphify-out/graph.json"

    repomix:
      enabled: true
      root: ".ai-context"
      preferred_files:
        - ".ai-context/governance-pack.md"
        - ".ai-context/repo-pack.md"

routing:
  architecture:
    description: "Architecture, design, topology, components, boundaries, trade-offs."
    read:
      - ".archcore/adr"
      - ".archcore/specs"
      - "ARCHITECTURE.md"
      - "architecture.md"
      - "docs/**/*.md"
    avoid_as_authority:
      - "SCRATCHPAD.md"
      - "scratchpad.md"

  planning:
    description: "Roadmap, work breakdown, current status, next steps."
    read:
      - ".archcore/plans"
      - "ARCHCORE_PROMOTION_CANDIDATES.md"
      - "ROADMAP.md"
      - "roadmap.md"
      - "CHANGELOG.md"
      - "memory-bank/progress.md"
      - "memory-bank/activeContext.md"
      - "SCRATCHPAD.md"

  governance:
    description: "Agent behaviour, project rules, file update rules, workflow rules."
    read:
      - "AGENTS.md"
      - "CLAUDE.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "CHANGELOG.md"
      - ".archcore/rules"
      - "ARCHCORE_PROMOTION_CANDIDATES.md"

  implementation:
    description: "Code, scripts, configs, tests, automation."
    read:
      - "AGENTS.md"
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - ".archcore/specs"
      - ".archcore/rules"
      - "src/**"
      - "scripts/**"
      - "tests/**"
    tools:
      preferred:
        - serena
        - graphify
        - repomix
      optional:
        - semgrep
        - markdownlint
        - vale

  scripts:
    purpose: "Project-local scripts, automation, task runners, and executable workflows."
    read_first:
      - "justfile"
      - "Justfile"
      - "scripts/README.md"
      - "Taskfile.yml"
      - "Makefile"
      - "package.json"
    generated_support:
      - "graphify-out"
      - ".ai-context"
    rules:
      - "Respect existing canonical runner first."
      - "Prefer just --list and just <task> when a justfile exists."
      - "Read scripts/README.md before running raw scripts."
      - "Treat uncataloged scripts as unknown safety."
      - "Do not run destructive scripts without explicit review."
      - "Run scripts/check_governance.py before claiming durable work complete; when it fails, fix the project, not the check."

  automation:
    purpose: "Repeatable operational workflows and project task entrypoints."
    read_first:
      - "justfile"
      - "Justfile"
      - "scripts/README.md"
      - "Taskfile.yml"
      - "Makefile"
      - "package.json"
      - "docs/automation.md"
    rules:
      - "Prefer cataloged commands."
      - "Prefer just when a justfile exists."
      - "Confirm inputs, outputs, side effects, and safety before execution."

  documentation:
    description: "README, docs, architecture docs, user guides."
    read:
      - "README.md"
      - "CHANGELOG.md"
      - "docs/**/*.md"
      - "ARCHITECTURE.md"
      - "architecture.md"
      - ".archcore/guides"
      - ".archcore/specs"
      - "memory-bank/activeContext.md"

  troubleshooting:
    description: "Issue investigation, debugging, root cause analysis."
    read:
      - "memory-bank/activeContext.md"
      - "memory-bank/progress.md"
      - "SCRATCHPAD.md"
      - "scratchpad.md"
      - "docs/**/*.md"
      - "logs/**"
      - "reports/**"

update_rules:
  governance_navigation:
    AGENTS.md:
      companions:
        - AI_NAVIGATION.md
        - context-map.yaml
        - scripts/README.md
    AI_NAVIGATION.md:
      companions:
        - context-map.yaml
    context-map.yaml:
      companions:
        - AI_NAVIGATION.md
    scripts/README.md:
      companions:
        - AGENTS.md
        - context-map.yaml
    new_script_added:
      companions:
        - scripts/README.md
        - AGENTS.md
        - justfile
        - scripts/check_governance.py
    # A new artifact class, generated output, or constant restated across files needs the checker's registries
    # extended in the same pass — otherwise the checker measures the project as it was, not as it is.
    new_artifact_class_added:
      companions:
        - scripts/check_governance.py
        - AGENTS.md

  durable_decision:
    update:
      - ".archcore/adr"
    also_consider:
      - "ARCHITECTURE.md"
      - "architecture.md"
      - "memory-bank/decisionLog.md"

  durable_rule:
    update:
      - ".archcore/rules"
    also_consider:
      - "AGENTS.md"
      - "AI_NAVIGATION.md"

  design_contract:
    update:
      - ".archcore/specs"
    also_consider:
      - "ARCHITECTURE.md"
      - "architecture.md"
      - "docs/**/*.md"

  operating_procedure:
    update:
      - ".archcore/guides"
    also_consider:
      - "README.md"
      - "docs/**/*.md"

  plan_change:
    update:
      - ".archcore/plans"
      - "ROADMAP.md"
      - "roadmap.md"
      - "memory-bank/progress.md"

  working_context_change:
    update:
      - "memory-bank/activeContext.md"

  temporary_note:
    update:
      - "SCRATCHPAD.md"

  routing_change:
    update:
      - "AI_NAVIGATION.md"
      - "context-map.yaml"
      - "AGENTS.md"

  governance_history:
    update:
      - "CHANGELOG.md"

  # A new artifact class, generated output, or constant restated across files leaves the checker
  # measuring the project as it was. Extend its registries in the same pass.
  new_artifact_class:
    update:
      - "scripts/check_governance.py"
    also_consider:
      - "AGENTS.md"
      - "scripts/README.md"

drift_policy:
  on_conflict:
    action: "stop_and_report"
    required_output:
      - conflicting_files
      - higher_authority_source
      - recommended_fix
      - assumptions

  scratchpad_rule:
    authoritative: false
    promotion_required_for_durable_truth: true

generated_context_policy:
  regenerate_after:
    - architecture_change
    - major_doc_change
    - roadmap_restructure
    - new_archcore_documents
    - significant_code_restructure

  commands:
    graphify: "graphify update ."
    repomix_governance: "repomix --config repomix.config.json"

audit_checks:
  governance_file_presence:
    - "README.md"
    - "AGENTS.md"
    - "CLAUDE.md"
    - "AI_NAVIGATION.md"
    - "context-map.yaml"
    - "CHANGELOG.md"
  version_consistency:
    description: "Verify managed block version strings match current skill version."
    action: "report_mismatch"
  companion_update_completeness:
    description: "When a governance file changes, verify all companion files in update_rules were also updated."
    action: "report_missing"
  generated_output_policy:
    description: "Verify Graphify and Repomix outputs are classified as generated support, not canonical truth."
    action: "report_violation"
  task_runner_consistency:
    description: "Verify cataloged tasks in scripts/README.md match actual script files."
    action: "report_drift"
  no_stale_references:
    description: "Detect references to removed tools, old task runners, or superseded governance assumptions."
    action: "report_stale"

promotion_rules:
  archcore:
    allowed_init_modes:
      - bootstrap
      - navigation-add
      - refresh
    content_write_modes:
      - promote
    required_authorization: true
    candidates_report: "ARCHCORE_PROMOTION_CANDIDATES.md"
    extract_heuristics_source: "patterns/archcore-routing.md"
    exclusion:
      - "CHANGELOG.md (history only)"
      - "generated files (.ai-context/, graphify-out/)"
      - "unmarked SCRATCHPAD sections"
      - "draft/obsolete roadmap items"

context_recovery:
  procedure:
    - "Read AI_NAVIGATION.md first for navigation map."
    - "Load .archcore/ context if present (durable truth)."
    - "Regenerate graphify-out/ with: graphify update ."
    - "Regenerate .ai-context/ with: repomix --config repomix.config.json"
    - "Verify SCRATCHPAD.md has current state. If empty, populate from memory-keeper / mcp-project-context."
    - "Verify CHANGELOG.md is current."
    - "Verify AI_NAVIGATION.md and context-map.yaml companion consistency."
  evidence_label: "Context recovered at <timestamp> via skill-ai-it context-recovery procedure."

answer_contract:
  require_source_paths: true
  unsupported_answer: "not found in project context"
  distinguish_assumptions: true
  do_not_invent_state: true

# Project-authored: the pack's own artifact map. AI_NAVIGATION.md "Pack domain routing" is the human-readable twin.
pack:
  entrypoint: "SKILL.md"
  content_root: "references"
  claim_ledger: "sources.yaml"
  environment_ledger: "compatibility.yaml"
  doc_snapshots_index: "documents/readme.md"
  helpers: "scripts"
  tests:
    contract: "tests/test_package_contract.py"
    helpers: "tests/test_helpers.py"
    scenarios: "tests/scenarios.md"
    eval_procedure: "tests/eval-procedure.md"
  version_of_record: "CHANGELOG.md release heading (manifest.json is forbidden by the package contract)"
  write_back_contract: "references/evolution-and-write-back.md"
  memory_channel: "nautobot"
  counterpart_skill: "../skill-openwisp"
  references:
    - path: "references/operations-cookbook.md"
      task: "Exact syntax: REST, GraphQL, groups, fields, hooks, CLI"
    - path: "references/data-model.md"
      task: "Locations, platforms, interfaces, VLANs, modules, contacts"
    - path: "references/app-development.md"
      task: "Writing a Nautobot app: models, API, UI, Jobs, tests"
    - path: "references/integrations.md"
      task: "pynautobot, SSoT/DiffSync, Git data, Ansible, Nornir, GC"
    - path: "references/operations-and-recovery.md"
      task: "Backup, restore, health, metrics, performance, security"
    - path: "references/authority-and-modeling.md"
      task: "Ownership, IPAM, relationships, custom data models"
    - path: "references/api-and-writers.md"
      task: "API traversal, deterministic readers, safe writers"
    - path: "references/staged-onboarding.md"
      task: "Brownfield discovery, identity, staging and approval"
    - path: "references/lifecycle-and-replacement.md"
      task: "Replacement, custody, labels and identity continuity"
    - path: "references/discovery-and-topology.md"
      task: "Discovery sources, conflicts and topology evidence"
    - path: "references/apps-jobs-validation.md"
      task: "Apps, Jobs, validators, workers and permissions"
    - path: "references/config-backup-compliance.md"
      task: "Backup, redaction, compliance, restore and deployment"
    - path: "references/capability-extension.md"
      task: "Missing capability, providers, NTC and complementary FOSS"
    - path: "references/upgrade-and-troubleshooting.md"
      task: "Upgrade preflight, extension register and incident triage"
    - path: "references/evolution-and-write-back.md"
      task: "Reusable learning capture and engagement closeout"
````

## File: justfile
````
# just task catalog for skill-nautobot.
# Purpose:
# - expose safe, documented project tasks to humans and AI agents
# - avoid agents running arbitrary scripts without context
# - keep runnable entrypoints simple and readable
#
# List tasks:
#   just --list
#
# Run task:
#   just <task>
#
# Safety:
# - Prefer safe/read-only tasks by default.
# - Mark destructive tasks clearly and require review.
# - Keep detailed inputs/outputs/safety notes in scripts/README.md.
#
# RUNTIME PINNING — do not replace {{py}} / {{nd}} with bare `python3` or `node`.
# A bare interpreter resolves to whatever the host has on PATH, which is NOT what .mise.toml pins. That works until the
# host changes underneath it and then fails in a way that reads like a code bug. Recipes go through the variables below
# so no recipe depends on the ambient interpreter, and `just runtimes` makes the resolved versions visible.
#
# `mise exec -- python` IS NOT THE FIX, and this is the part that gets missed. Where .mise.toml sets `_.python.venv`,
# `mise exec -- python` does land on the venv — so it tests clean and reads as pinned. But the dependency is IMPLICIT:
# nothing at the call site says which interpreter is meant, and if the activation ever stops applying (the env block is
# edited, the venv is missing, the recipe is copied into a project without that config) it degrades SILENTLY to the host
# interpreter instead of failing. Address the interpreter by PATH via {{py}}, and depend on _require-venv, so a missing
# venv is a loud error with a fix attached rather than a wrong-interpreter run that looks fine.
#
# Node has no venv layer, so `mise exec -- node` is genuinely the explicit form for it — the distinction above applies
# wherever a venv sits between mise and the interpreter, which in practice means Python.
#
# The venv lives in the WORKING-CACHE PEER, never in this repo — a repo carries source, not rebuildable runtime.
# Path mapping (see the global runtime-isolation policy):
#   project_stuff/<group>/<project>  ->  project-working-cache/<group>/<project>
#   mcp_stuff/<project>              ->  mcp-working-cache/<project>
#   skills_stuff/<project>           ->  skills-working-cache/<project>
#   tools_stuff/<project>            ->  tools-working-cache/<project>
#
# `uv run` is deliberately NOT the primary path: it resolves its own interpreter independently of mise, which is the
# same class of drift this pinning removes. Use it only where a recipe needs throwaway third-party packages.

set dotenv-load := false

wc := "/Volumes/Data/_ai/_skills/skills-working-cache/skill-nautobot"
py := wc + "/.venv/bin/python"

# Build the working-cache venv from the mise-pinned runtimes. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @{{py}} -m pip install --quiet --upgrade pip -r requirements.txt
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early and legibly rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtimes the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"

# List available tasks and show script inventory when present
inventory:
    @just --list
    @test -f scripts/README.md && sed -n '1,220p' scripts/README.md || true

# Audit script/task inventory for obvious drift
audit-scripts:
    @echo "== just recipes =="
    @just --list || true
    @echo
    @echo "== script files =="
    @find scripts -maxdepth 2 -type f 2>/dev/null | sort || true
    @echo
    @echo "== uncataloged script candidates =="
    @if [ -d scripts ] && [ -f scripts/README.md ]; then \
      find scripts -maxdepth 2 -type f | sort | while read -r f; do \
        grep -Fq "$f" scripts/README.md || echo "$f"; \
      done; \
    fi

# Must exit 0 before durable work is called complete. Fix the project when it fails, never the check.
# Governance coherence checks — assert this project's governance claims against reality
check: _require-venv
    @{{py}} scripts/check_governance.py

# The pack's own offline contract + helper tests (also runs the governance checker via tests/test_helpers.py)
test: _require-venv
    @{{py}} -m unittest discover -s tests -p 'test_*.py'

# The helpers this pack ships (stdlib-only; import them with scripts/ on sys.path)
helpers:
    @ls scripts/*.py | xargs -n1 basename

# Regenerate the deterministic Repomix context pack (.ai-context/governance-pack.md). Generated support, not truth.
context-pack:
    @command -v repomix >/dev/null || { echo 'repomix not installed; skipped'; exit 0; }
    @repomix --config repomix.config.json --quiet

# Refresh the code graph (graphify-out/: AST only, no LLM). Generated support, not truth.
graph:
    @command -v graphify >/dev/null || { echo 'graphify not installed; skipped'; exit 0; }
    @graphify update .

# Run safe local preflight checks
preflight: runtimes audit-scripts test check lint-md

# Lint Markdown files when markdownlint-cli2 is available
lint-md:
    @command -v markdownlint-cli2 >/dev/null || { echo 'markdownlint-cli2 not installed; skipped'; exit 0; }
    @markdownlint-cli2 '**/*.md'

# The navigation-control scripts live in the skill package, NOT in this project. Override on the
# command line if the skill lives elsewhere:  just skill_dir=/path/to/skill-ai-it nav-validate
skill_dir := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Upgrade navigation control layer (dry-run preview)
nav-upgrade-dry-run: _require-venv
	@{{py}} "{{skill_dir}}/scripts/upgrade_navigation_control_layer.py" --project-root . --dry-run

# Upgrade navigation control layer (apply changes) — review the dry-run first
nav-upgrade: _require-venv
	@{{py}} "{{skill_dir}}/scripts/upgrade_navigation_control_layer.py" --project-root .

# Validate navigation control layer
nav-validate: _require-venv
	@{{py}} "{{skill_dir}}/scripts/validate_navigation_control_layer.py" --project-root .

# Check only expected files changed after upgrade (requires a git repo)
nav-check-diff: _require-venv
	@{{py}} "{{skill_dir}}/scripts/check_expected_diff.py" --project-root .

# Self-test the SKILL PACKAGE's managed-block builders (not this project). Run it after the skill
# package's templates change, before trusting nav-upgrade to rewrite this project's blocks.
nav-selftest: _require-venv
	@{{py}} "{{skill_dir}}/scripts/selftest_blocks.py"
````

## File: Justfile
````
# just task catalog for skill-nautobot.
# Purpose:
# - expose safe, documented project tasks to humans and AI agents
# - avoid agents running arbitrary scripts without context
# - keep runnable entrypoints simple and readable
#
# List tasks:
#   just --list
#
# Run task:
#   just <task>
#
# Safety:
# - Prefer safe/read-only tasks by default.
# - Mark destructive tasks clearly and require review.
# - Keep detailed inputs/outputs/safety notes in scripts/README.md.
#
# RUNTIME PINNING — do not replace {{py}} / {{nd}} with bare `python3` or `node`.
# A bare interpreter resolves to whatever the host has on PATH, which is NOT what .mise.toml pins. That works until the
# host changes underneath it and then fails in a way that reads like a code bug. Recipes go through the variables below
# so no recipe depends on the ambient interpreter, and `just runtimes` makes the resolved versions visible.
#
# `mise exec -- python` IS NOT THE FIX, and this is the part that gets missed. Where .mise.toml sets `_.python.venv`,
# `mise exec -- python` does land on the venv — so it tests clean and reads as pinned. But the dependency is IMPLICIT:
# nothing at the call site says which interpreter is meant, and if the activation ever stops applying (the env block is
# edited, the venv is missing, the recipe is copied into a project without that config) it degrades SILENTLY to the host
# interpreter instead of failing. Address the interpreter by PATH via {{py}}, and depend on _require-venv, so a missing
# venv is a loud error with a fix attached rather than a wrong-interpreter run that looks fine.
#
# Node has no venv layer, so `mise exec -- node` is genuinely the explicit form for it — the distinction above applies
# wherever a venv sits between mise and the interpreter, which in practice means Python.
#
# The venv lives in the WORKING-CACHE PEER, never in this repo — a repo carries source, not rebuildable runtime.
# Path mapping (see the global runtime-isolation policy):
#   project_stuff/<group>/<project>  ->  project-working-cache/<group>/<project>
#   mcp_stuff/<project>              ->  mcp-working-cache/<project>
#   skills_stuff/<project>           ->  skills-working-cache/<project>
#   tools_stuff/<project>            ->  tools-working-cache/<project>
#
# `uv run` is deliberately NOT the primary path: it resolves its own interpreter independently of mise, which is the
# same class of drift this pinning removes. Use it only where a recipe needs throwaway third-party packages.

set dotenv-load := false

wc := "/Volumes/Data/_ai/_skills/skills-working-cache/skill-nautobot"
py := wc + "/.venv/bin/python"

# Build the working-cache venv from the mise-pinned runtimes. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @{{py}} -m pip install --quiet --upgrade pip -r requirements.txt
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early and legibly rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtimes the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"

# List available tasks and show script inventory when present
inventory:
    @just --list
    @test -f scripts/README.md && sed -n '1,220p' scripts/README.md || true

# Audit script/task inventory for obvious drift
audit-scripts:
    @echo "== just recipes =="
    @just --list || true
    @echo
    @echo "== script files =="
    @find scripts -maxdepth 2 -type f 2>/dev/null | sort || true
    @echo
    @echo "== uncataloged script candidates =="
    @if [ -d scripts ] && [ -f scripts/README.md ]; then \
      find scripts -maxdepth 2 -type f | sort | while read -r f; do \
        grep -Fq "$f" scripts/README.md || echo "$f"; \
      done; \
    fi

# Must exit 0 before durable work is called complete. Fix the project when it fails, never the check.
# Governance coherence checks — assert this project's governance claims against reality
check: _require-venv
    @{{py}} scripts/check_governance.py

# The pack's own offline contract + helper tests (also runs the governance checker via tests/test_helpers.py)
test: _require-venv
    @{{py}} -m unittest discover -s tests -p 'test_*.py'

# The helpers this pack ships (stdlib-only; import them with scripts/ on sys.path)
helpers:
    @ls scripts/*.py | xargs -n1 basename

# Regenerate the deterministic Repomix context pack (.ai-context/governance-pack.md). Generated support, not truth.
context-pack:
    @command -v repomix >/dev/null || { echo 'repomix not installed; skipped'; exit 0; }
    @repomix --config repomix.config.json --quiet

# Refresh the code graph (graphify-out/: AST only, no LLM). Generated support, not truth.
graph:
    @command -v graphify >/dev/null || { echo 'graphify not installed; skipped'; exit 0; }
    @graphify update .

# Run safe local preflight checks
preflight: runtimes audit-scripts test check lint-md

# Lint Markdown files when markdownlint-cli2 is available
lint-md:
    @command -v markdownlint-cli2 >/dev/null || { echo 'markdownlint-cli2 not installed; skipped'; exit 0; }
    @markdownlint-cli2 '**/*.md'

# The navigation-control scripts live in the skill package, NOT in this project. Override on the
# command line if the skill lives elsewhere:  just skill_dir=/path/to/skill-ai-it nav-validate
skill_dir := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"

# Upgrade navigation control layer (dry-run preview)
nav-upgrade-dry-run: _require-venv
	@{{py}} "{{skill_dir}}/scripts/upgrade_navigation_control_layer.py" --project-root . --dry-run

# Upgrade navigation control layer (apply changes) — review the dry-run first
nav-upgrade: _require-venv
	@{{py}} "{{skill_dir}}/scripts/upgrade_navigation_control_layer.py" --project-root .

# Validate navigation control layer
nav-validate: _require-venv
	@{{py}} "{{skill_dir}}/scripts/validate_navigation_control_layer.py" --project-root .

# Check only expected files changed after upgrade (requires a git repo)
nav-check-diff: _require-venv
	@{{py}} "{{skill_dir}}/scripts/check_expected_diff.py" --project-root .

# Self-test the SKILL PACKAGE's managed-block builders (not this project). Run it after the skill
# package's templates change, before trusting nav-upgrade to rewrite this project's blocks.
nav-selftest: _require-venv
	@{{py}} "{{skill_dir}}/scripts/selftest_blocks.py"
````

## File: README.md
````markdown
# skill-nautobot

Canonical, cross-project platform pack for Nautobot: intended network source of truth: inventory, IPAM, relationships, lifecycle, Jobs/apps and integration APIs.

## Purpose

Reusable, evidence-graded Nautobot knowledge for any project that runs it. Each engagement writes verified reusable findings back here; project, customer and equipment
specifics stay in the engaging project. The counterpart pack is [skill-openwisp](../skill-openwisp/README.md).

## Folder index

- [references/](references/) — focused content files, one per domain; routed from [SKILL.md](SKILL.md) and [AI_NAVIGATION.md](AI_NAVIGATION.md)
- [documents/](documents/) — version-matched official doc snapshots. Index: [documents/readme.md](documents/readme.md)
- [scripts/](scripts/) — tested stdlib-only helpers and the governance checker. Index: [scripts/README.md](scripts/README.md)
- [tests/](tests/) — offline package contract, helper tests, scenarios, evaluation procedure
- [.archcore/](.archcore/) — durable decisions, rules and plans (6 documents, accepted 2026-10-05). Index: [.archcore/index.guide.md](.archcore/index.guide.md)

## Key files

| File | Role |
|---|---|
| [SKILL.md](SKILL.md) | Activation surface — role, boundaries, routing, write-back contract |
| [sources.yaml](sources.yaml) | Claim ledger with evidence rungs |
| [compatibility.yaml](compatibility.yaml) | Environment ledger |
| [CHANGELOG.md](CHANGELOG.md) | Release history; version of record |
| [justfile](justfile) | Task catalog — `just --list`; `just test` is the completion gate |

## Governance pointers

- Local agent guidance: [AGENTS.md](AGENTS.md)
- Parent guidance: [../../../AGENTS.md](../../../AGENTS.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Pack history: [CHANGELOG.md](CHANGELOG.md)
- Canonical governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
````

## File: SCRATCHPAD.md
````markdown
# SCRATCHPAD

Agent working memory for skill-nautobot.
Use for: draft plans, terminal output, intermediate analysis, refactor outlines.
Cleared between sessions unless content is explicitly marked KEEP.

---

<!-- KEEP: populated 2026-10-05 from memory-keeper + mcp-project-context + claude-mem -->

## Current state

**Phase:** released pack, latest release heading in [CHANGELOG.md](CHANGELOG.md); governance scaffold bootstrapped 2026-10-05.

Standalone, cross-project Nautobot pack (operator decision 2026-10-01: separate evolving skills, not sections of skill-smc or skill-cambium). Built guidance-only at 0.1–0.2,
version-matched cookbook and tested write-back contract at 0.3.0, then 0.4.0 on 2026-10-05 from an independent assessment: new focused references and promoted stdlib helpers with
tests. The skill-ai-it governance layer (navigation, context map, justfile, governance checker) was added on 2026-10-05.

---

## Open items

- [ ] Live, version-pinned behavioural probes on a disposable install — `compatibility.yaml` rows above `observed_install` stay `pending_live_test` until then (handoff 2026-10-02).
- [ ] Full client evaluation matrix (Claude Code with authentication, Codex) per [tests/eval-procedure.md](tests/eval-procedure.md); release claims stay PARTIAL until it runs.
- [ ] skill-ai-it template drift (fix in skill-ai-it, not here): its `context-map.yaml` template lacks `skill_ai_it_version` and `update_rules.governance_navigation`
  (validator warns on a fresh bootstrap); template block markers are one line where the builder writes two; the governance-checks block exceeds 200 columns; the upgrader
  re-dumps `context-map.yaml` (drops comments) and appends a generic CHANGELOG heading.
- [x] 6 `.archcore/` documents accepted by the operator 2026-10-05 — index [.archcore/index.guide.md](.archcore/index.guide.md).

---

## Key anchors

| Item | Detail |
|---|---|
| Install | `~/.claude/skills/skill-nautobot` is a symlink to this folder |
| Observed version | Nautobot 3.2.3 (observed install; see `compatibility.yaml`) |
| Memory channel | memory-keeper `nautobot` (exact name, USER_STATED) |
| Origin project | unified-network-controller — design reports under its project-reviews reports folder |
| Gate | `just test` then `just check` |

---

## Recent decisions

- 2026-10-01 — Independent pack, guidance-only at first; capability search order provider → supported extension → other FOSS → scratch (USER_STATED).
- 2026-10-05 — `scripts/` admitted for tested, stdlib-only helpers; the contract requires each helper to be tested.
- 2026-10-05 — Governance checker runs inside `tests/test_helpers.py`, so the existing test run is also the governance gate.
- 2026-10-05 — `AGENTS.md` force-added to git (operator); the repo's git info/exclude file keeps ignoring it repo-wide, so every later edit needs `git add -f`.
- 2026-10-05 — `/skill-ai-it promote` for all candidates: 2 ADRs, 3 rules, 1 plan; candidates queue deleted. Operator accepted all 6 the same day.

---

## Session history (summaries — full detail in memory-keeper)

### 2026-10-05 (~19:25–19:36) — collision merge, promote, accept, commit

- A parallel UNC session overwrote the `justfile`; merged its `helpers`/probe recipes into the skill-ai-it justfile; it promoted 5 helpers from UNC and catalogued them.
- Promoted all candidates (2 ADRs, 3 rules, 1 plan) and the operator accepted all; `AGENTS.md` force-added; committed and pushed with skill-cambium.
- Evidence basis: memory-keeper keys `platform-packs.justfile-collision.20261005_1930`, `nautobot.archcore-promote.20261005`, `platform-packs.slurp.20261005`.

### 2026-10-05 — skill-ai-it bootstrap

- Added README, AGENTS, CLAUDE, AI_NAVIGATION, context-map, justfile, .mise.toml, scripts/README, governance checker, Repomix config; `archcore init`.
- Evidence basis: this CHANGELOG `## Unreleased` line.

### 2026-10-05 — 0.4.0 from an independent assessment

- New references and promoted helpers; capture-corpus fleet lessons as Learned entries.
- Evidence basis: claude-mem observations 2026-10-05; CHANGELOG 0.4.0.

### 2026-10-01/02 — 0.1.0 → 0.2.0 operational revision

- Claims, scenarios, package contract; operational depth; no runnable helpers then.
- Evidence basis: memory-keeper key `unc-platform-skills-0-2-0-posthook-handoff-20261002`.

---

## Next actions

- Run the disposable live probes and the client matrix (`.archcore/plans/live-probes-then-client-matrix.plan.md`) before widening release claims.
- Report the skill-ai-it template drift above into skill-ai-it's own SCRATCHPAD/CHANGELOG.

---

## Memory pointers (navigation only — content is above)

- memory-keeper channels: `nautobot`, `unc` / keys: `nautobot.skill-v01-frozen-spec.20261001_1724`, `unc.nautobot-openwisp-skill-operator-contract.20261001_1724`,
  `unc-platform-skills-0-2-0-posthook-handoff-20261002`
- project-context: no dedicated project; nearest are `unified-network-controller` and `skills_stuff`
- memory-keeper (this session): `nautobot.governance-bootstrap.20261005_1602`, `openwisp.governance-bootstrap.20261005_1602`,
  `platform-packs.justfile-collision.20261005_1930`, `nautobot.archcore-promote.20261005`, `platform-packs.archcore-promote.20261005`, `platform-packs.slurp.20261005`
- checkpoints: `slurp-20261005-platform-packs-governance` (memory-keeper and project-context)
- claude-mem: results found (observations 2026-10-01 and 2026-10-05)
````

## File: SKILL.md
````markdown
---
name: skill-nautobot
description: >-
  Design, query and troubleshoot Nautobot: inventory, IPAM and Namespaces, custom fields, computed fields, Relationships, Dynamic Groups, Config Contexts,
  Secrets, REST/GraphQL/pynautobot, Jobs and Job Hooks, webhooks, approvals, change log, Golden Config, staged onboarding, field ownership, permissions and
  upgrades (nautobot-server), app development, SSoT/DiffSync, Ansible and Nornir inventories, backup and restore, metrics and security settings.
  Use for Nautobot work; not as the primary skill for OpenWISP telemetry, graphs or alerts.
---

# Nautobot

## Role and non-goals

Use Nautobot primarily for intended network source-of-truth modelling, inventory, IPAM, relationships, lifecycle workflows, validation, Jobs/apps and integration APIs.
Do not treat telemetry monitoring as its default responsibility, or describe a project worked case as product behaviour.

## Read, write, and evidence boundaries

Read-only investigation may produce observations; it does not authorize an inventory mutation.
Observed discovery does not automatically become intended inventory, and transient health must not silently redefine lifecycle state.
Obtain project-specific authorization before every write, keep the writer identity and idempotence contract explicit, and fail closed on ambiguity.
Keep an observation's source, time, vantage and confidence when it may affect a later decision.
Do not embed client credentials, customer topology, or equipment-specific commands in reusable guidance.

## Orient first

On an unfamiliar deployment, establish the version, the installed apps and whether workers answer before reading anything else; models, API shapes
and Job interfaces change between releases.

```bash
nautobot-server --version; pip list 2>/dev/null | grep -iE 'nautobot|pynautobot|diffsync|nornir'; grep -nE '^PLUGINS' "$NAUTOBOT_CONFIG"
nautobot-server celery inspect ping -t 5; nautobot-server celery inspect active_queues; nautobot-server health_check
```

`scripts/` holds tested, stdlib-only helpers (`just helpers`): `nautobot_paging.py` (`listing()` adds a total order; `traverse()` refuses a listing
that repeats, skips or miscounts), `nautobot_ipam.py` (an address's mask from the narrowest network Prefix), `nautobot_masks.py` (plan and apply
the mask fix) and `nautobot_linkage.py` (objects that belong to a Location but nothing links to, by registered rules).

## Route the task

Choose the primary skill by the object or failure **being changed**: a Nautobot field, Device, Job or intent edge starts here; OpenWISP registration/metric/worker/
health/graph starts in `skill-openwisp`. A synchronization task uses the owner of the requested change as primary and reads the other skill only for its contract.
Observed topology uses the collector/presentation component as primary; accepted topology uses Nautobot. Vendor commands, OIDs, RF interpretation and transport
execution begin with equipment/transport expertise, with this skill supplying only the inventory integration contract. Ordinary single-platform tasks load one pack.

| Task                                                      | Read first                                |
| --------------------------------------------------------- | ----------------------------------------- |
| Exact syntax: REST, GraphQL, groups, fields, hooks, CLI   | [references/operations-cookbook.md](references/operations-cookbook.md) |
| Locations, platforms, interfaces, VLANs, modules, contacts | [references/data-model.md](references/data-model.md) |
| Writing a Nautobot app: models, API, UI, Jobs, tests      | [references/app-development.md](references/app-development.md) |
| pynautobot, SSoT/DiffSync, Git data, Ansible, Nornir, GC  | [references/integrations.md](references/integrations.md) |
| Backup, restore, health, metrics, performance, security   | [references/operations-and-recovery.md](references/operations-and-recovery.md) |
| Ownership, IPAM, relationships, custom data models        | [references/authority-and-modeling.md](references/authority-and-modeling.md) |
| API traversal, deterministic readers, safe writers        | [references/api-and-writers.md](references/api-and-writers.md) |
| Brownfield discovery, identity, staging and approval      | [references/staged-onboarding.md](references/staged-onboarding.md) |
| Replacement, custody, labels and identity continuity      | [references/lifecycle-and-replacement.md](references/lifecycle-and-replacement.md) |
| Discovery sources, conflicts and topology evidence        | [references/discovery-and-topology.md](references/discovery-and-topology.md) |
| Apps, Jobs, validators, workers and permissions           | [references/apps-jobs-validation.md](references/apps-jobs-validation.md) |
| Backup, redaction, compliance, restore and deployment     | [references/config-backup-compliance.md](references/config-backup-compliance.md) |
| Missing capability, providers, NTC and complementary FOSS | [references/capability-extension.md](references/capability-extension.md) |
| Upgrade preflight, extension register and incident triage | [references/upgrade-and-troubleshooting.md](references/upgrade-and-troubleshooting.md) |
| Reusable learning capture and engagement closeout         | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Verify version-sensitive facts

Before asserting a current endpoint, model field, Job/app interface, or release behaviour, inspect version-matched official documentation and record the source/date in [sources.yaml](sources.yaml).
Use [compatibility.yaml](compatibility.yaml) only for its stated environment and evidence rung; an observed install is not behavioural proof.
Record unknowns as unknown rather than extrapolating a supported version range.

## Search before building

```text
desired operator outcome
  ↓ existing Nautobot core capability
  ↓ installed or maintained product apps/modules and relevant NTC tooling
  ↓ supported extension points of those components
  ↓ compatible external FOSS and its supported seams
  ↓ from-scratch component only when the acceptance test still cannot be met
```

At every downward transition, state why the preceding level cannot meet the acceptance test.
Check current maintenance, license, compatibility, reachability and extension support; do not maintain a static best-tools ranking.
Prefer the narrowest supported seam and cover the behaviour it relies on with a regression test.

## Project and equipment boundary

Keep customer, site and exact device state in its governing project.
Route device commands, OIDs and vendor-specific behaviour to the appropriate equipment expertise rather than copying them here.
For a cross-platform task, load another skill only when the task actually crosses its ownership boundary.

## Project conventions

A project that runs Nautobot may keep a platform-conventions file (its field owners, writer accounts, naming, safety tiers and evidence vocabulary). Check the
engaging project's `AGENTS.md` for it before any write; project rules outrank the generic guidance here. For UNC that file is
`docs/engineering/platform-skills-project-layer-20261005_1349.md` in the unified-network-controller project.

## Standing write-back contract

Invoking this skill obliges you to write back what the engagement taught, in any project, before the session ends: a dated Learned entry in the focused reference
plus one CHANGELOG line under `## Unreleased`, read back after writing. Classify every engagement in one sentence (no new learning, verified update, candidate,
contradiction, project-only, equipment-only). Skill use never authorizes editing a live system, and editing this source only when the task permits it; otherwise
leave the entry in the engaging project. Format, classes and release reconciliation:
[references/evolution-and-write-back.md](references/evolution-and-write-back.md).
````

## File: sources.yaml
````yaml
claims:
  - id: N-C01
    statement: "The UNC Nautobot implementation combines core intended inventory with project custom fields, relationships, validators and app models."
    kind: worked_example
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-unc-inspected-20261001]
    environment_id: nautobot-unc-inspected-20261001
    source_type: implementation
    evidence: "UNC wc-local/nautobot/apps/wc-ownership/wc_ownership/{models.py,custom_validators.py}, catalog parts and field ownership model; inspected 2026-10-01."
    reference: references/authority-and-modeling.md
    test: N-S01
  - id: N-C02
    statement: "A Namespace is the Nautobot boundary for IPAM uniqueness and can model otherwise overlapping addresses."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-core-docs-3-2-2]
    environment_id: nautobot-core-docs-3-2-2
    source_type: official_documentation
    evidence: "https://archive.docs.nautobot.com/projects/core/en/v3.2.2/user-guide/core-data-model/ipam/prefix/ states Prefix/address uniqueness per Namespace; current Namespace local snapshot is supplemental; verified 2026-10-01."
    reference: references/authority-and-modeling.md
    test: N-S01
  - id: N-C03
    statement: "Nautobot REST relationship representation is version-sensitive and must be verified before integration code relies on it."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-rest-3-2]
    environment_id: nautobot-rest-3-2
    source_type: official_documentation
    evidence: "https://docs.nautobot.com/projects/core/en/stable/user-guide/platform-functionality/rest-api/overview/; precise relationship shape not asserted; verified 2026-10-01."
    reference: references/api-and-writers.md
    test: N-S17
  - id: N-C04
    statement: "The observed environment contains Nautobot core 3.2.3 and the listed application versions."
    kind: worked_example
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-core-3-2-3, nautobot-apps-2026-10-01]
    environment_id: nautobot-core-3-2-3
    source_type: observed_install
    evidence: "Phase 3A readiness report, Observed 2026-10-01 baseline; image/package metadata read-only, not API behavior."
    reference: references/upgrade-and-troubleshooting.md
    test: N-S08
  - id: N-C05
    statement: "A discovery observation requires corroboration and approval before it becomes intended inventory."
    kind: generic_invariant
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Phase 3A readiness, automatic learning and onboarding boundary; USER_STATED, version-independent policy."
    reference: references/staged-onboarding.md
    test: N-S02
  - id: N-C06
    statement: "A physical label identifies an object but does not authenticate the actor handling it."
    kind: generic_invariant
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Phase 3A readiness, lifecycle and actor boundary; USER_STATED, version-independent policy."
    reference: references/lifecycle-and-replacement.md
    test: N-S05
  - id: N-C07
    statement: "Observed topology and accepted intended topology require separate provenance and conflict handling."
    kind: generic_invariant
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Phase 3A readiness, discovery/intent boundary; USER_STATED, version-independent policy."
    reference: references/discovery-and-topology.md
    test: N-S06
  - id: N-C08
    statement: "Nautobot 3.2 changed Job execution interfaces, so upgrade validation must exercise exact Job behaviour."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-job-upgrade-3-2]
    environment_id: nautobot-job-upgrade-3-2
    source_type: official_documentation
    evidence: "https://archive.docs.nautobot.com/projects/core/en/v3.2.2/release-notes/version-3.2/ section Migrate Job Execution and Scheduled Jobs; verified 2026-10-01."
    reference: references/apps-jobs-validation.md
    test: N-S03
  - id: N-C09
    statement: "Configuration backup, compliance comparison, restore verification, and deployment are separate capabilities."
    kind: generic_invariant
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Phase 3A readiness, backup/deploy boundary; USER_STATED, version-independent policy."
    reference: references/config-backup-compliance.md
    test: N-S04
  - id: N-C10
    statement: "A provider and supported-extension search precedes a from-scratch implementation recommendation."
    kind: generic_invariant
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Phase 3A readiness, complementary FOSS search order; USER_STATED, version-independent policy."
    reference: references/capability-extension.md
    test: N-S07
  - id: N-C11
    statement: "Core patches require reviewed comparison and revalidation against each new upstream version."
    kind: generic_invariant
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Phase 3A readiness, upgrade-survival contract; USER_STATED, version-independent policy."
    reference: references/upgrade-and-troubleshooting.md
    test: N-S08
  - id: N-C12
    statement: "Each engagement requires a durable reusable-learning classification at closeout."
    kind: generic_invariant
    evidence_status: USER_STATED
    lifecycle: current
    applies_to: []
    environment_id: null
    source_type: user_policy
    evidence: "Phase 3A readiness, per-engagement learning contract; USER_STATED, version-independent policy."
    reference: references/evolution-and-write-back.md
    test: N-S09
  - id: N-C13
    statement: "The project pagination regression required stable ordering because unordered pages produced a distorted and incomplete object set."
    kind: tested_pattern
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-paging-offline-20261001]
    environment_id: nautobot-paging-offline-20261001
    source_type: implementation_and_test
    evidence: "UNC wc-local/scripts/common/nautobot_paging.py listing() and tests/test_nautobot_paging.py OrderedPagesTest; 320 rows/251 distinct regression; inspected 2026-10-01."
    reference: references/api-and-writers.md
    test: N-S16
  - id: N-C14
    statement: "A project-derived address rule preserves the narrowest containing Prefix mask instead of defaulting every address to /32."
    kind: tested_pattern
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-unc-inspected-20261001]
    environment_id: nautobot-unc-inspected-20261001
    source_type: implementation
    evidence: "UNC wc-local/scripts/common/address_mask.py, fix_address_masks.py and tests/test_fix_address_masks.py; narrowest network Prefix, placeholders excluded; inspected 2026-10-01."
    reference: references/authority-and-modeling.md
    test: N-S01
  - id: N-C15
    statement: "A custom relationship or model is justified only when native models cannot express durable domain semantics, as in the project Wireless Link worked case."
    kind: worked_example
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-unc-inspected-20261001]
    environment_id: nautobot-unc-inspected-20261001
    source_type: implementation_and_design
    evidence: "UNC wc_ownership/models.py WirelessLink plus docs/architecture/wireless-links-design-20260928_2154.md; implemented model versus proposed feed; inspected 2026-10-01."
    reference: references/discovery-and-topology.md
    test: N-S06
  - id: N-C16
    statement: "A supported model is not a valid operational solution when its worker cannot reach the required network or device path."
    kind: worked_example
    evidence_status: VERIFIED_SECONDARY
    lifecycle: current
    applies_to: [nautobot-unc-inspected-20261001]
    environment_id: nautobot-unc-inspected-20261001
    source_type: report_synthesis
    evidence: "UNC docs/reports/controller-option3/ntc-ecosystem-complementary-tools-20260929_1304.md Device Onboarding disposition; local research, not product limitation."
    reference: references/apps-jobs-validation.md
    test: N-S03
  - id: N-C17
    statement: "A generated catalog is changed at its declared source inputs and then rendered, rather than edited at the derived output."
    kind: tested_pattern
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-unc-inspected-20261001]
    environment_id: nautobot-unc-inspected-20261001
    source_type: implementation
    evidence: "UNC wc-local/nautobot/catalog/master.yaml includes parts; catalog render/check path in scripts/check_governance.py; inspected 2026-10-01."
    reference: references/capability-extension.md
    test: N-S07
  - id: N-C18
    statement: "Default Statuses and Roles are created only by data migrations, so a deleted built-in is not recreated by migrate or post_upgrade; restore from the change log keeping the original id."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-core-docs-3-2-3]
    environment_id: nautobot-core-docs-3-2-3
    source_type: official_documentation
    evidence: "Installed 3.2.3 source nautobot/extras/management/__init__.py lines 107-170, extras/models/roles.py line 37, core/api/serializers.py line 158; bundled change-logging docs; checked 2026-10-05."
    reference: references/operations-cookbook.md
    test: N-S19
  - id: N-C19
    statement: "From 3.2.0 Job invocation helpers require explicit job_kwargs, and a REST run returns 201 when queued, not when done."
    kind: generic_invariant
    evidence_status: VERIFIED_PRIMARY
    lifecycle: current
    applies_to: [nautobot-core-docs-3-2-3]
    environment_id: nautobot-core-docs-3-2-3
    source_type: official_documentation
    evidence: "Installed 3.2.3 source nautobot/extras/api/views.py lines 995-1022 and serializers.py lines 896-910; bundled job-execution and release-note docs; checked 2026-10-05."
    reference: references/operations-cookbook.md
    test: N-S20
````
