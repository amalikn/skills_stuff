---
Title: Design patterns harvested from projects
Category: reference
Status: current
Authority: local-supplement
Scope: Reusable solutions found in one project's code, stated so a project in another domain can apply them
Last reviewed: 2026-10-27
Summary: >-
  Pattern catalogue: problem, solution, why it works, how to reuse it elsewhere, pitfalls, and its realisation per language with a source
  excerpt. First entries come from the ansible-wifi smc_change engine (change orchestration over unreliable links); none needs that domain.
---

# Design patterns harvested from projects

A `Learned` entry in a language file records how a tool behaves. A pattern here records a piece of design that solved a problem well enough that another project, in another domain, should reuse it
(operator, 2026-10-27: "its logic and out of box thinking and how it can benefit other projects which will not have even SMC needs to be captured"). Write a pattern when a project's code solved a
general problem (safe retries, resumable work, partitioning targets, evidence layout) in a way that is not obvious; write the language-specific trick that made it work as a `Learned` entry in the
language file and link the two.

## Contents

- [Entry format](#entry-format)
- [Index](#index)
- [Patterns](#patterns)
- [Language realisations](#language-realisations)

## Entry format

```text
### P-NN Name
Problem:      the general problem, no project nouns
Solution:     the design in three to six lines
Why it works: the property that makes it safe or cheap
Reuse:        two or three other settings where it applies
Pitfalls:     what broke or nearly broke, and the guard
Realised in:  language -> file (project, commit or CHANGELOG stamp); excerpt below, about 30 lines at most, secrets and site names removed
Evidence:     VERIFIED_PRIMARY | VERIFIED_SECONDARY | CANDIDATE, with what was observed
```

## Index

| ID   | Pattern                                            | Problem in one line                                                               |
| ---- | -------------------------------------------------- | --------------------------------------------------------------------------------- |
| P-01 | Generic engine, change as data                     | Many similar changes without a new script each time                               |
| P-02 | Before/after probe with baseline gates             | Prove a change broke nothing, and refuse when you could not tell                  |
| P-03 | Write-ahead journal with a code fingerprint        | Resume an interrupted multi-step change without replaying unsafe steps            |
| P-04 | Done ledger keyed by a target hash                 | Skip finished targets without re-checking them, and redo them when the goal moves |
| P-05 | Prepare once, partition, then batch                | Do run-wide work once and keep every batch slot for real work                     |
| P-06 | Detached long step with one tolerated drop         | A long remote operation over a link that drops                                    |
| P-07 | Evidence tree by a stable partition key            | Keep run records findable as targets, groups and changes multiply                 |
| P-08 | Shared pool by name with atomic no-overwrite links | Back up the same large artefact from many targets once                            |
| P-09 | Plug-in checks joined into one program, piped      | Run many read-only checks on a target without writing to it                       |
| P-10 | Fail-open filters, fail-closed gates               | Optional pre-filters must never block work; safety gates must                     |
| P-11 | Freeze code under in-flight transactions           | Edit an engine while some of its transactions are still open                      |
| P-12 | Plan, print, then apply                            | A migration or bulk move that must not stop half-way unnoticed                    |

## Patterns

### P-01 Generic engine, change as data

> **Learned 2026-10-27 (a)** · design pattern, any language · VERIFIED_PRIMARY (two unrelated changes ran on one engine unchanged) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: a new change that needed an engine edit naming its type
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-01, written generically below.

- **Problem:** every change to a fleet (a package pin, a config line, a hosts file, a scripted fix) becomes its own script, each with its
  own backup, verify and rollback bugs; the tenth change is no safer than the first.
- **Solution, the anatomy:**
  1. **An engine** runs the same stages for every change: load and check the spec, scope (which targets it applies to), probe before,
     guard (refuse an unfit or unhealthy target), back up, act, restart, reboot if the policy says, probe after and judge gates, clean up,
     record. The engine never names an action type, a package or a file.
  2. **An action catalogue**: one file per action type (`apt_pin`, `template`, `copy`, `ini`, `command`), each with a paired undo file
     (`<type>_rollback`). The engine dispatches by the spec's `type`; rollback dispatches the undo files in reverse order. A new type is two
     new files and no engine edit.
  3. **A check catalogue**: one plug-in per check (`services`, `commands`, `http`, `processes`, `logs`, `files`, `apt_pin`), each giving
     collect, healthy, gates and describe; the spec turns them on by naming their keys.
  4. **The change is data**: a spec file says what it applies to, the actions with their parameters, what to back up, what to restart,
     the reboot policy, how long to soak, and what proves it worked. Reviewing a change is reading one data file.
- **Contracts that keep it generic:** the spec's shape is checked at load (unknown type, bad policy: the whole run fails before any target
  is touched); rollback refuses a type with no undo file; every new per-change behaviour is a spec field whose default is today's
  behaviour (so old specs keep working); `proves` checks (false before, true after: what the change fixes) are kept apart from health
  checks, so a target is never refused for lacking the fix it is about to get; type knowledge lives only in the type's files.
- **Why it works:** safety (baseline, guard, backup, journal, gates, record) is written once and every change inherits it; adding a change
  is cheap, adding a capability is local; the same spec runs in check, apply, verify and rollback modes.
- **Reuse:** database migrations (actions = DDL, data fix, index build; checks = row counts, query plans); Kubernetes or cloud config
  rollouts (actions = patch, scale, annotate); network device changes (actions = config block, firmware; checks = neighbours, routes); SaaS
  admin changes through an API. Anywhere many small, similar changes hit many targets.
- **Pitfalls:** a one-change exception coded in the engine (move it to a spec field); a type that cannot be undone (write the undo file
  first, or have the spec carry an explicit `undo` command); checks that hit a default endpoint and look healthy on a dead service.
- **How to add an action type:** write `<type>.yml` (apply on every target path it must reach) and `<type>_rollback.yml`; add its keys to
  the spec check; add a probe part if its effect needs its own check; write one spec using it and run it in check mode, then canary.
- **Realised in:** Ansible, `roles/smc_change` (`tasks/apply.yml`, `tasks/rollback.yml`, `tasks/actions/`, `files/probe/`,
  `files/changes/<name>/<name>.yml`), local-knowledge-ansible ansible-wifi, 2026-10-23 onward. Python, the probe's check registry.

```yaml
# Engine: dispatch by type (tasks/apply.yml), undo last first and refuse a type with no undo file (tasks/rollback.yml)
- name: Run the actions
  ansible.builtin.include_tasks: "actions/{{ smc_change_action.type }}.yml"
  loop: "{{ smc_change_spec.actions }}"
  loop_control: {loop_var: smc_change_action, index_var: smc_change_action_index}
- name: Undo the actions, last first
  ansible.builtin.include_tasks: "actions/{{ smc_change_action.type }}_rollback.yml"
  loop: "{{ smc_change_spec.actions | reverse | list }}"
```

```yaml
# A change as data (files/changes/<name>/<name>.yml, shortened): what, where, how to undo, how it is proven
name: etc-hosts-hostname
applies_to: {flavors: [rcp, rct, wh], arch: [x86_64, aarch64]}
actions:
  - type: command
    check: grep -qx "127.0.1.1 $(hostname)" /etc/hosts
    cmd: sed -i -e "s/^127\.0\.1\.1[[:space:]].*/127.0.1.1 $(hostname)/" /etc/hosts
    undo: tar -xzpf "$SMC_CHANGE_BACKUP/paths.tgz" -C / etc/hosts
backup: {paths: [/etc/hosts]}
reboot: overlay_fallback
verify:
  proves: [{cmd: 'grep -qx "127.0.1.1 $(hostname)" /etc/hosts'}]
```

- **Evidence:** VERIFIED_PRIMARY, a package pin (PHP security fix, dozens of production targets) and a hosts-file fix ran on the same engine
  with no engine edit; rollback of both proven on a bench target.

### P-02 Before/after probe with baseline gates

> **Learned 2026-10-27 (b)** · design pattern, any language · VERIFIED_PRIMARY (portal render judged before and after each production apply; unhealthy baselines refused) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: an after-probe pass on a target whose before-probe was not taken
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-02, written generically below.

- **Problem:** "it still works" after a change is a guess unless you compared it with before; and a target already broken makes any after-result meaningless.
- **Solution:** a read-only probe before the change is the baseline; the same probe after it is judged as gates against the baseline (same status code, same module list, no new error lines). A
  baseline that is already unhealthy refuses the change unless overridden.
- **Why it works:** a failure afterwards is attributable to the change; nothing is changed on a box you could not judge.
- **Reuse:** schema changes (row counts, query plans before/after), API deploys (contract checks), firmware upgrades.
- **Pitfalls:** checks that hit a default endpoint look healthy on a dead service (probe the real name, not localhost).
- **Realised in:** Python, `files/probe/40_http.py` registers `healthy` and `gates`; Ansible, `tasks/guard.yml` refuses an unhealthy baseline.

```python
def http_ok(item, res):
  return res["code"] == "200" and (res["html"] or not item.get("require_html", True)) and not res["bad_markers"]

register(Check("http", collect=http_collect, healthy=http_healthy, gates=http_gates, describe=http_describe))
```

- **Evidence:** VERIFIED_PRIMARY, captive portal pages judged before and after every PHP apply on production; unhealthy baselines refused.

### P-03 Write-ahead journal with a code fingerprint

> **Learned 2026-10-27 (c)** · design pattern, any language · VERIFIED_PRIMARY (six interrupted applies refused on changed code, accepted on the original) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: a resume that replays an install step after the code changed
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-03, written generically below.

- **Problem:** a multi-step change cut off half-way (power, dropped link) must resume, but replaying a step on different code or inputs can do damage.
- **Solution:** before the first write, save a journal (phase, original baseline, transaction-owned facts) on the controller and update it at each phase. Store a fingerprint of the engine code plus
  the resolved inputs. A resume classifies: complete, safe to resume, or needs repair. Steps that install or back up are never replayed on changed code; steps that only restart, verify or clean up may
  be.
- **Why it works:** the decision is a pure function of journal, fingerprint and a fresh safety probe, so it is testable offline.
- **Reuse:** long data backfills, multi-region deploys, any saga with compensating steps.
- **Pitfalls:** "no process is running" is not "no transaction is open" (see P-11); keep the journal off the target if the target may reboot into a different filesystem.
- **Realised in:** Python, `files/recovery.py` (pure classification); Ansible, `tasks/journal.yml`, `tasks/recovery.yml`.

```python
drifted = journal.get("fingerprint") != data.get("fingerprint")
if drifted and journal.get("phase") not in (7, 8, 9, 10):
  result["reasons"] = ["Host or resolved spec fingerprint changed; do not replay this transaction."]
  return result
```

- **Evidence:** VERIFIED_PRIMARY, six interrupted applies refused on changed code and accepted on the original code (2026-10-27).

### P-04 Done ledger keyed by a target hash

> **Learned 2026-10-27 (d)** · design pattern, any language · VERIFIED_PRIMARY (done targets skipped in 2 s without connecting; ~17 s and a batch slot each before) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: a finished target re-applied after an engine-only edit, or skipped after the goal moved
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-04, written generically below.

- **Problem:** re-running a fleet job re-checks finished targets (slow), or re-applies them (risky); but when the goal changes (a newer version) they must be redone.
- **Solution:** after a verified success write a small state record per target with the hash of what was applied, computed from the spec's semantic fields only (drop fields that say how to replay, not
  what to apply). The next run skips a target whose state is a pass of the same hash and whose journal is complete; `--force` overrides.
- **Why it works:** editing the engine does not redo finished work; moving the goal does.
- **Reuse:** idempotent migrations per tenant, per-repo bulk refactors, per-device config pushes.
- **Pitfalls:** decide per mode whether "done" skips (verify modes should not skip; their job is to re-prove).
- **Realised in:** Ansible, `tasks/state.yml` and `tasks/pending.yml`.

```yaml
smc_change_target: >-
  {{ smc_change_spec.actions | map('dict2items') | map('rejectattr', 'key', 'equalto', 'resume_safe') | map('items2dict') | list
     | to_json(sort_keys=true) | hash('sha256') }}
```

- **Evidence:** VERIFIED_PRIMARY, done targets skipped in 2 s with no connection, against ~17 s and a batch slot each before.

### P-05 Prepare once, partition, then batch

> **Learned 2026-10-27 (e)** · design pattern, any language · CANDIDATE (partition live and measured; the prepare stage tested in a scratch copy only) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: a batch slot taken by a target the partition marked done or offline
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-05, written generically below.

- **Problem:** run-wide work (load and validate the spec, fingerprint, build the probe program, create folders) repeated per target, and finished or offline targets occupying batch slots.
- **Solution:** a first stage with no batching runs on the controller: does the run-wide work once, fails the whole run on a bad spec before any connection, then partitions targets into done, offline
  and to-do. The batched stage runs over to-do only.
- **Why it works:** batches are built from the partitioned list, so every slot is real work; a spec error costs seconds, not a fleet.
- **Reuse:** CI matrices (skip unchanged packages), crawlers (skip fresh pages), bulk API jobs (skip already-synced records).
- **Pitfalls:** a framework's "run once" can mean once per batch, not per run (Ansible `run_once`); keep the per-target part (values that read each target's variables) out of the once stage.
- **Realised in:** Ansible, `playbooks/smc_change.yml` first play + `tasks/pending.yml` (live), `tasks/prepare.yml` (patch `plans/smc-change-resume-20261027_1038/`); see `languages/ansible.md` Learned
  2026-10-27 (g).
- **Evidence:** VERIFIED_PRIMARY for the partition; prepare stage tested in a scratch copy (2026-10-27), not yet live.

### P-06 Detached long step with one tolerated drop

> **Learned 2026-10-27 (f)** · design pattern, any language · VERIFIED_PRIMARY (installs finished through Teleport drops; retry window measured 117 s) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: a link drop during the long step failing the step itself
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-06, written generically below.

- **Problem:** a long remote step (package install) dies with the session when the link drops, leaving the target half-changed.
- **Solution:** start it detached with a job id, poll its status; on one unreachable poll wait for the connection (bounded), then poll again. Transport retries with backoff cover short blips (only for
  transport errors, never for the command's own failure).
- **Why it works:** the work no longer depends on the session; the poll is idempotent.
- **Reuse:** remote builds, database dumps over VPN, OTA updates.
- **Pitfalls:** a retried start can launch a second job (guard with a lock or check-before-start).
- **Realised in:** Ansible, `async`/`poll: 0` + `tasks/await_job.yml`; `ansible_ssh_retries: 8` (see `languages/ansible.md` (e), (i)).

### P-07 Evidence tree by a stable partition key

> **Learned 2026-10-27 (g)** · design pattern, any language · VERIFIED_PRIMARY (198 items moved, six open journals still resumable) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: a run whose records cannot be found from its inputs alone
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-07, written generically below.

- **Problem:** run records, state, journals and backups pile into one folder; tools and people stop finding them.
- **Solution:** `<change>/runs/<partition>/{records,state,journal,backups}/`, the partition being a stable key the run already knows (the inventory group here); records named
  `<target>-<change>-<mode>-<start>`. A summary selects this run's records by modification time since the run start and then by the run stamp inside each record, not by file name (a resumed run keeps
  its original start).
- **Why it works:** every path is computable from the run's inputs; adding a partition needs no migration.
- **Reuse:** test artefacts per environment, audit logs per tenant, ML runs per dataset.
- **Pitfalls:** moving the tree under open transactions (see P-11): move the files and the path setting in one step.
- **Realised in:** Ansible, `defaults/main.yml` `smc_change_runs_dir`; Python, `scripts/smc_change_runs_by_flavor.py`.

### P-08 Shared pool by name with atomic no-overwrite links

> **Learned 2026-10-27 (h)** · design pattern, any language · VERIFIED_PRIMARY (one pool copy of shared builds across many backups) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: two pool copies of one name, or a per-target file pooled
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-08, written generically below.

- **Problem:** every target's backup carries the same large files (the same package builds); copying each per target wastes link and disk.
- **Solution:** the spec names which backup files are shared (globs); the controller keeps one pool copy by name; each target's backup lists the pooled names it needs. Adding to the pool uses `ln`
  without `-f` (atomic, never overwrites), so two targets adding the same name leave one copy.
- **Reuse:** artefact caches across CI jobs, dedup of identical attachments, golden images.
- **Pitfalls:** never pool a file whose name is the same everywhere but whose content is per target (rejected at spec load).
- **Realised in:** Ansible, `tasks/cleanup.yml`, `tasks/backup.yml`, `files/pool_match.py`.

### P-09 Plug-in checks joined into one program, piped

> **Learned 2026-10-27 (i)** · design pattern, any language · VERIFIED_PRIMARY (every probe of the rollout; nothing written on targets) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: a file left on the target by a probe
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-09, written generically below.

- **Problem:** many read-only checks per target, without installing or writing anything there.
- **Solution:** each check is a file with collect, healthy, gates and describe functions that registers itself; the controller joins the files in name order (core first, main last) into one program
  and pipes it to the target's interpreter on stdin, with its configuration in the environment. Lint the joined program, not the parts.
- **Reuse:** fleet audits, compliance scans, pre-flight checks for deploys.
- **Pitfalls:** environment values appear on the remote command line, so a process-matching check finds itself (see `references/safety-and-writes.md` Learned 2026-10-26).
- **Realised in:** Python, `files/probe/NN_*.py` with `register(Check(...))`; Ansible, `tasks/probe.yml`.

### P-10 Fail-open filters, fail-closed gates

> **Learned 2026-10-27 (j)** · design pattern, any language · VERIFIED_PRIMARY (a failed online lookup filtered nothing) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: every target dropped because a pre-filter errored
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-10, written generically below.

- **Problem:** an optional pre-filter (is the target listed online?) that errors can silently drop every target, while a safety gate that errors must stop the change.
- **Solution:** decide per check which way it fails. Filters fail open: a failed lookup filters nothing and says so once. Gates fail closed: missing data is a failed gate.
- **Reuse:** feature flags, rate limiters, pre-commit hooks versus release gates.
- **Realised in:** Ansible, `tasks/pending.yml` (tsh filter: a failed `tsh ls` keeps its targets).

### P-11 Freeze code under in-flight transactions

> **Learned 2026-10-27 (k)** · design pattern, any language · VERIFIED_PRIMARY (2026-10-27 incident and recovery) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: a resume refused after an edit made while its journal was open
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-11, written generically below.

- **Problem:** the engine is edited while some transactions are open; their resume then refuses (P-03) or, without a fingerprint, replays on code it never ran with.
- **Solution:** while any journal is open, the fingerprinted code is frozen: build the change in a scratch copy, test it there against real state read-only, and leave a patch plus a runbook; keep any
  file a resume needs, with its hash, in the repo. Settings outside the fingerprint (paths, defaults) can still move.
- **Reuse:** schema migrations with long-running jobs, workflow engines with persisted state machines.
- **Realised in:** ansible-wifi RULE-007 (2026-10-27 incident); `plans/smc-change-resume-20261027_1038/`.

### P-12 Plan, print, then apply

> **Learned 2026-10-27 (l)** · design pattern, any language · VERIFIED_PRIMARY (failed first apply left a known state; re-run moved 198 items) · Source: local-knowledge-ansible ansible-wifi `roles/smc_change` (CHANGELOG 20261027_1042) · Falsifier: a bulk move stopping half-way with no list of what moved
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-12, written generically below.

- **Problem:** a bulk move fails on item 1 of 198, after a related setting already changed, and the state is unclear.
- **Solution:** compute the full list of moves first; print it (dry run is the default); refuse when any item is ambiguous or unsafe; apply only on `--apply`; resolve paths to absolute before calling
  tools that change directory.
- **Realised in:** Python, `scripts/smc_change_runs_by_flavor.py` (`plan()` then `move()`); see `languages/python.md` Learned 2026-10-27.

```python
moves, problems = plan(runs, inv, args.with_active)
for src, dst, copy in all_moves:
  print(f"{'copy' if copy else 'move'}  {src.relative_to(changes)}  ->  {dst.relative_to(changes)}")
if all_problems:
  return 1
```

## Language realisations

| Pattern | Ansible (`languages/ansible.md`)                         | Python (`languages/python.md`)                       |
| ------- | -------------------------------------------------------- | ---------------------------------------------------- |
| P-03    | journal and recovery tasks; Learned (e) drop-proof waits | pure `classify(journal, current)` function, tested   |
| P-05    | no-serial first play + `group_by`; Learned (g), (j)      | build the plan once, then `concurrent.futures` batch |
| P-06    | `async` + `poll: 0` + await; Learned (e), (i)            | detached job id + idempotent status poll             |
| P-09    | `include_tasks` per type; joined probe via stdin         | `register(Check(...))` plug-in registry              |
| P-12    | `--check` / diff before apply                            | `plan()` then `--apply`; Learned 2026-10-27          |
