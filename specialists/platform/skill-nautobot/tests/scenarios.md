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
