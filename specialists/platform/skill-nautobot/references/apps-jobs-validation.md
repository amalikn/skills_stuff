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

> **Learned 2026-10-13** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: installed `nautobot/extras/models/jobs.py` ScheduledJob.save (begin_approval_workflow on first save), on_workflow_approved (enabled, ACTIVE), and `nautobot/extras/models/approvals.py` find_for_model · Falsifier: a ScheduledJob created with `ScheduledJob.create_schedule` from inside a Job runs without waiting while a matching definition exists
> A Job can stop at an approval by queuing another Job: `ScheduledJob.create_schedule(job_model, user, job_kwargs={...})` saves a ScheduledJob, and its first save starts the matching ApprovalWorkflowDefinition (state Pending, disabled); approval enables it and it runs. A definition's `model_constraints` are passed to `.filter()`, so ORM lookups such as `{"job_model__name__in": [...]}` work. Definitions are unique on (model content type, weight), and a fresh install ships "Scheduled Jobs Approval - Example" on Scheduled Jobs at weight 100 (its constraint matches no Job): pick another weight; the highest weight is tried first. The approver needs `change` on the stage, the workflow and the ScheduledJob under review; no rule stops the requester approving their own run. A Job flagged `has_sensitive_variables` cannot carry an approval.

> **Learned 2026-10-13** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: installed `nautobot/extras/jobs.py` ChoiceVar (line 984) and ScriptVariable.as_field; `nautobot/__init__.py` (SUCCESS, FAILURE levels); `extras/jobs.py` JobButtonReceiver (line 1157) and the time-limit lookup (line 1305) · Falsifier: a callable ChoiceVar showing a stale list after its source changes, or `self.logger.success` raising AttributeError
> `ChoiceVar(choices=<callable>)` works: the choices go to Django's `ChoiceField`, which is built each time the form is (as_field), so a list read from the cache is fresh on every open. `self.logger.success()` and `self.logger.failure()` exist (custom levels), and `extra={"grouping": ..., "object": obj}` sets the log entry's grouping and link, which a panel can query back (`JobLogEntry.grouping__startswith`). A Job Button runs a `JobButtonReceiver` (`receive_job_button(obj)`; fixed vars `object_pk`, `object_model_name`); a button whose Jinja2 text renders empty is hidden. A Job's `Meta.soft_time_limit` and `time_limit` override Celery's defaults for its runs.

> **Learned 2026-10-14** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: `ScheduledJob._meta.get_fields()` and `JobResult._meta` on a 3.2.3 instance; a gate Job denying earlier requests in production code (UNC 0.8.8) · Falsifier: a 3.2.x ScheduledJob with an `approval_required` field, or `task` differing from the Job's `class_path`
> A Job queued for approval twice (a second request while the first waits) leaves the first pending after the second is answered. Clear it where it
> is created: in the approved Job's `run()`, find `ScheduledJob.objects.filter(task=self.class_path, kwargs__icontains=<object pk>)` excluding
> `self.job_result.scheduled_job_id`, take each one's pending `associated_approval_workflows` stage and save an `ApprovalWorkflowStageResponse` for the
> running user with `state=DENIED` and a comment. 3.2.3 has no `ScheduledJob.approval_required` field (filter by `task` and `kwargs`); `ScheduledJob.task`
> equals the Job's `class_path`; `JobResult.scheduled_job` links a run to the schedule that queued it.

> **Learned 2026-10-14 (b)** · Nautobot 3.2.3, DNS Models 2.3.0 · CANDIDATE (system check and offline tests; not yet exercised live) · Source: `extras/templates/extras/job.html`
> (blocks `job_form`, `javascript`), `nautobot.core.forms.widgets.StaticSelect2`, `nautobot_dns_models/__init__.py` `constance_config` and `models.py:517-532` read
> on a 3.2.3 container · Falsifier: a 3.2.x job form that drops `Meta.template_name`, or a DNS Models release that reads the setting from `PLUGINS_CONFIG`
> **Dependent Job fields.** `ChoiceVar` has no `query_params`, so "pick a group, then only its items" is done in the Job's own form template: `Meta.template_name`
> pointing at an app template that `{% extends 'extras/job.html' %}` and adds a `javascript` block. Keep every item in the second field with a value that
> carries its group (`"<group>:<item>"`), rebuild that `<select>`'s options on the first field's change and fire jQuery `change` so Select2 redraws; check the
> pair again in `run()`, since the script only narrows. Fields render in class order. **DNS Models CNAME exclusivity** is the constance key
> `nautobot_dns_models__CNAME_RESTRICTION_ENABLED` (default False), read directly from constance, so `PLUGINS_CONFIG` cannot set it; set it in nbshell with
> `setattr(constance.config, key, True)`. **htmx polling that must not close a pop-up:** add a trigger filter, `every 10s[!document.querySelector('.modal.show')]`.

> **Learned 2026-10-14 (c)** · Nautobot 3.2.3 · VERIFIED_PRIMARY (live on a 3.2.3 instance, UNC 0.8.12) · Source: `users/models.py` `get_config`/`set_config`,
> `extras/plugins/__init__.py` `banner_function` and `BannerClassChoices` read on the container; a Django test client run against the live app · Falsifier:
> a 3.2.x release dropping `User.config_data`, or app banners no longer called on every page
> **A per-user view switch that persists across pages** needs no model: store it in the user's preferences (`user.set_config("<app>.<key>", value,
> commit=True)`, read with `get_config(path, default)`), flip it from a small POST view that redirects to a validated `return_url`, and draw the switch
> in the app's banner function (one per app, called for every page with the template context; combine anything else the app shows there into the same
> Banner). Banner classes are only success, info, warning and danger. **nbshell from stdin is an interactive shell:** printed lines carry `>>> `
> prompts and a block needs a closing blank line, so search a marker anywhere in the line, or use `nbshell --command`.

> **Learned 2026-10-14 (d)** · Nautobot 3.2.3, DNS Models 2.3.0 · VERIFIED_PRIMARY (live on a 3.2.3 instance, UNC 0.8.15 to 0.8.19) · Source: a PATCH of `tags`
> to `/api/plugins/dns/dns-zones/<id>/` (200, response without `tags`, zone unchanged), then `zone.tags.add(...)` in nbshell; Django test client page reads
> · Falsifier: a DNS Models release whose zone serializer accepts `tags`
> **DNS Models zone tags are not writable over REST:** `DNSZone` is a PrimaryModel with tags, but its serializer drops `tags`, so the write "succeeds" and
> nothing is tagged; set them through the ORM (nbshell `--command`) and read them back. **An object page's banner is drawn on every tab of it**
> (`?tab=<name>`), while a template-extension panel sits on the main tab only: a banner link or button that relies on the panel's markup (a modal, an
> in-page anchor) must point at the main tab when `tab` is not `main`. **An htmx poll filter that names an open element** (`[!document.querySelector
> ('details[open]')]`) stops polling for good when the browser restores the page from its back-forward cache with that element open: on `pageshow`,
> close such elements and fire a custom trigger the poll also listens to (`hx-trigger="every 10s[...], my-refresh"`). **The Job log as a history
> source:** `JobLogEntry` keeps `created`, `grouping` and the Job result's user, enough to time steps a Job logs as start and end lines, but the
> Logs Cleanup system Job deletes them; copy them first if the history must outlive a cleanup. **Badge text:** Nautobot's theme draws white on
> `bg-success` and black on `text-bg-success` and `text-bg-info`.


> **Learned 2026-10-14 (e)** · Nautobot 3.2.3 · VERIFIED_PRIMARY (installed source; UNC 0.8.22) · Source: `extras/views.py` JobRunView POST (create_schedule,
> has_approval_workflow_definition, dryrun branch), `extras/templates/extras/job.html` (schedule card), `extras/views.py` JobResultUIViewSet.log_table,
> `core/ui/object_detail.py` Component.should_render · Falsifier: a Run Now of a workflow-matched Job that executes without approval, or a job.html with a
> wrapper block around the schedule card
> **Run Now goes through approval too:** the run form always makes a ScheduledJob (`create_schedule`, interval `immediately`), and when a workflow
> definition matches it, the run is held for approval like a scheduled one; only a Job's `dryrun` variable skips the approval (runs at once). So a
> name-matched definition plus a `DryRunVar` gives "preview freely, change after approval" with no custom code. **Hiding the schedule card** of one
> Job: `job.html` has a `schedule_form` block inside the card but no block around the card, and its script reads `#id__schedule_type`; in the Job's
> `Meta.template_name` keep the fields and hide the cards with `.card:has(#id__schedule_type)` (and `#id__job_queue`, `#id__console_log`), then refuse
> a schedule in `run()` (`self.job_result.scheduled_job_id`), since hiding is not a guard. `has_sensitive_variables = True` would also force
> immediate runs but shows a warning card and cannot coexist with an approval workflow. **Job result logs filter by message or level only**
> (`log-table?q=`), not by `grouping`: a Job that logs several stages needs its own per-grouping page. **A conditional object tab:** subclass
> `DistinctViewTab` and override `should_render(context)` (call `super()` for `required_permissions`).

> **Learned 2026-10-14 (f)** · Nautobot 3.2.3, DLM 4.2.0, Golden Config 3.0.7 · VERIFIED_PRIMARY (read-only probes of a 3.2.3 instance) · Source:
> installed DLM 4.2.0 and Golden Config 3.0.7 sources, UNC platform features plan 20261014_2348 · Falsifier: a DLM release that matches a version range, or a Golden Config Device tab shown
> with no compliance rows
> **Device Lifecycle Management shows every versioned Device "Software INVALID" while no Validated Software exists**: validity is a match of the
> Device's one SoftwareVersion against a ValidatedSoftware entry (by device type, role or device), exactly, so "22.04.x" is one entry per point
> release; an entry is unique on (software, start, end). **Golden Config 3.0.7's only Device tab is Configuration Compliance**, hidden while the
> device has no compliance rows; the backed-up configuration is reached through the GoldenConfig record, not a tab. **Core's LLDP Neighbors and
> Configuration tabs are live NAPALM calls** from the web process: they need a Platform with a NAPALM driver and the device reachable from Nautobot,
> so behind a jump host or for a vendor without a driver they stay empty; show stored observations from an app instead. **Core Data Compliance
> rules** register through an app's custom validators or a Git repository and report, they do not refuse a save by default.

> **Learned 2026-10-15 (g)** · Nautobot 3.2.3, DLM 4.2.0 · VERIFIED_PRIMARY (seeded and pages read on a live 3.2.3 instance, UNC 0.8.23) · Source:
> installed DLM 4.2.0 source (validated-software API and model uniqueness) · Falsifier: a DLM release with another endpoint or uniqueness, or a list with a global default view that answers 200 without a redirect
> **DLM Validated Software over REST:** `/api/plugins/nautobot-device-lifecycle-mgmt/validated-software/` with `software`, `device_types`,
> `device_roles`, `start`, `end`, `preferred`; key an idempotent seed on (software, start, end), DLM's uniqueness. **A global default Saved View**
> (`is_global_default`, one per list view; saving one clears the others) makes the list URL answer 302 to `?saved_view=<id>`: a page check must follow
> redirects, and `?clear_view=true` opens the list without it. **A Device-page tab from an app:** an `ObjectView` rendering a template that extends
> `dcim/device.html`, with `get_detail_view_components_context_for_model(Device)` in its context, plus a `DistinctViewTab` in a TemplateExtension's
> `object_detail_tabs`; `should_render(context)` can hide it per object (call `super()` for `required_permissions`).

> **Learned 2026-10-15 (i)** · Nautobot 3.2.3 · VERIFIED_PRIMARY (installed source; not yet run on a live instance) · Source: `nautobot/extras/models/jobs.py:1808-1935` (`ScheduledJob.create_schedule`) · Falsifier: a release that checks the owner's run permission when creating or dispatching a schedule
> **A schedule owned by a machine account**: `ScheduledJob.create_schedule(job_model, user, name=..., interval="custom", crontab="7 * * * *", job_kwargs={...})`
> takes the next crontab match as the start time, the Job's default queue and its time limits, and checks no permission of `user`; run it from
> `nbshell` as an admin step to give a token-only account (no `run` on extras.job) a schedule whose writes it owns. `job_kwargs` is required.

> **Learned 2026-10-15 (p)** · Nautobot 3.2.3, Django 5.2 · VERIFIED_PRIMARY (not yet run live; first dry run pending) · Source: Django 5.2 `django/db/models/deletion.py` `Collector.collect` · Falsifier: Collector accepting a PROTECT object that is itself scheduled for deletion
> A Job that deletes a whole site cannot preview with `Collector` alone: Collector raises ProtectedError even when the protecting object (a Prefix in the
> site's Namespace) is also due for deletion. Preview by doing the real deletes in dependency order inside `transaction.atomic()` and rolling back;
> the counts are Django's own. `Namespace.delete()` returns None (no count tuple). Whether a rolled-back run leaves no ObjectChange and fires no hooks
> is to be confirmed on the first dry run.

> **Learned 2026-10-15 (r)** · Nautobot 3.2.3, Design Builder 3.1.2, DNS Models 2.3.0 · VERIFIED_PRIMARY (released wheel source; not yet run live) · Source: `nautobot_design_builder/design.py` `ModelInstance.save` and `ModelMetadata` load, `models.py` `ChangeSet.log` and `__sub__`, `design_job.py` `_run_in_transaction`; `nautobot/extras/jobs.py` `Job.__call__` (`web_request_context(user=self.user)`) · Falsifier: a deployment-mode re-run that keeps an object the design now only `!get`s, or a custom validator seeing another user than the Job's launcher
> A deployment-mode design re-run decommissions every object an earlier run recorded that the new run does not name, and a `!get` is never saved, so never
> recorded: a rerunnable design names each of its objects with `!create_or_update` every run and writes attributes only when the object is new (decide it in the
> context). A lookup filter's values are copied into a new object's attributes, so a many-to-many field cannot be a filter (look the object up in the context
> and name it by `id`). Tags and many-to-many values are added, never removed. A Design Builder Job saves as its launcher (UI user or API token owner), and
> custom validators see that user. DNS Models' `DNSView.prefixes` is a many-to-many through `DNSViewPrefixAssignment`; the design key is `dns_views`.
