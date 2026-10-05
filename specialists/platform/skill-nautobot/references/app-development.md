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
