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
