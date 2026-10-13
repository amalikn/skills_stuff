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

> **Learned 2026-10-13** · Nautobot 3.2.3 · UNVERIFIED · Source: unified-network-controller `unc_ownership/onboarding_flow.py`, `onboarding_run.py`, `onboarding_api.py`, `src/unc/jobs/onboarding_runner.py`; design `docs/engineering/onboarding-flow-and-site-panels-design-20261013_1800.md` 3.1 · Falsifier: a deployment where a Job cannot hold a worker slot for the length of a stage, or where the cache is not shared between web, worker and API
> (reusable_candidate: proven in one deployment, not yet general) Pattern: **a Job whose work needs reach the worker has not got (Teleport bots, SSH keys, a vault on the host) queues it to a host runner.** The Job puts a request in Nautobot's cache, an external service polls an app API view with a writer token (IsAuthenticated plus one explicit permission check in the view, since TokenPermissions needs a queryset), runs the step, posts output lines and the end back, and the Job copies the lines into its own log and waits. Between steps the runner reads an abort flag the page set; a per-object lock (`cache.add`) stops two runs at once; a heartbeat key tells the Job and the page whether the runner is alive. The same runner can publish a list the Job form reads (a callable `ChoiceVar`), so a form offers only valid choices that live outside Nautobot.

> **Learned 2026-10-13** · Nautobot 3.2.3 · UNVERIFIED · Source: as above · Falsifier: JobLogEntry rows pruned before the state is read, or a need to query state across many objects (then a model is warranted)
> (reusable_candidate: proven in one deployment, not yet general) Pattern: **multi-stage workflow state without a model.** Each stage a Job runs leaves log entries with `grouping` `<flow>:<object>:<stage>` and a message starting with a state word; a panel takes the latest per stage. Approval gates are separate Jobs the run queues with `ScheduledJob.create_schedule`, held by an ApprovalWorkflowDefinition matched on the Job's name; the panel links a waiting stage to its approval and reads denied, approved or a dead run (state "running" but its JobResult ended) from native objects. Resume is "first stage not done", which needs every stage idempotent.

> **Learned 2026-10-13** · Nautobot 3.2.3 · UNVERIFIED · Source: unified-network-controller `unc_ownership/asbuilt.py`, `wc-local/scripts/site_onboarding/asbuilt_reference.py` · Falsifier: a reference too large for a Config Context, or a need for the expected objects to appear in other Nautobot views
> (reusable_candidate: proven in one deployment, not yet general) Pattern: **a reference ("as built", "as designed") beside discovered inventory without placeholder objects.** Keep the reference as a schema-validated Config Context on the site Location (reviewed in Git, imported by a writer account with an entry-by-entry dry-run diff; the change log keeps each version), and compute drift when the page is read: bind each expected item to a Device by its strongest evidence (name, number, the cable on its drawn port, role in its Location), then show in place, drift (wrong Location, port or status) or not found. Planned Devices would duplicate discovered ones and need merging; the Config Context needs none.

> **Learned 2026-10-13** · Nautobot 3.2.3 · UNVERIFIED · Source: unified-network-controller `unc_ownership/site_panels.py`, `asbuilt.py`, `wc-local/scripts/nautobot_tools/site_panels_preview.py` · Falsifier: a panel whose markup cannot be built from plain records
> (reusable_candidate: proven in one deployment, not yet general) Pattern: **Django-free panel modules.** A template-extension panel's `render_body_content` only collects records into dataclasses and calls a module with no Django imports that returns escaped Bootstrap 5 markup (semantic `text-bg-*` classes, so light and dark themes both hold). The module is unit-tested offline and rendered by a headless browser in both themes from sample or saved records, so the operator accepts a screenshot before anything is deployed.
