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
