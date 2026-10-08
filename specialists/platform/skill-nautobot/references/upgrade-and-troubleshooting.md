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

> **Learned 2026-10-08** · Nautobot 3.2.3 (image networktocode/nautobot:3.2.3-py3.13) · VERIFIED_PRIMARY · Source: PyPI metadata read 2026-10-08 and a live install on one deployment: image rebuilt, `nautobot-server post_upgrade`, 46 app migrations applied, 0 pending, core and every existing app version unchanged in `pip list` · Falsifier: one of these pins failing to install or migrate on 3.2.x with Python 3.13
> nautobot-ssot 4.7.0 (nautobot >=3.1,<4; Python >=3.10,<3.15), nautobot-device-lifecycle-mgmt 4.2.0 and nautobot-capacity-metrics 4.1.1 (nautobot >=3.0,<4) install together beside Golden Config 3.0.7 without moving Nautobot or Django. Capacity Metrics is already pulled in as a Golden Config dependency, so enabling it is a PLUGINS line, not a new package. DLM registers six jobs on first start; set SSoT's `hide_example_jobs: True` to keep its demo jobs out of the job list. Recreate the web, worker and scheduler containers by service name before running `post_upgrade`: run in the old container, it migrates nothing new and reports success. `post_upgrade` also sends installation metrics to nautobot.cloud unless `INSTALLATION_METRICS_ENABLED = False`.

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
