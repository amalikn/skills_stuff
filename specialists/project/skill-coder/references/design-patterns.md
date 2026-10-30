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
| P-13 | Capability table: exists is not proven                     | Risky paths enabled because they exist, not because they were proven        |
| P-14 | Declared rollback class and explicit end states             | "Failed" that hides whether the target changed                             |
| P-15 | Dead-man revert timer armed before the change               | A change that kills the process or link that would undo it                  |
| P-16 | Ownership and applicability as two axes                     | Writers overwriting each other; "not applicable" mixed with "not allowed"   |
| P-17 | Neutral contract proven by two consumers                    | An abstraction shaped by its first consumer                                 |
| P-18 | Clear a stale lock only after proving the owner dead        | Locks cleared while the owner still runs                                    |
| P-19 | Rule by class with allow and deny exceptions, deny wins     | N x N compatibility tables                                                  |
| P-20 | Acceptance evals: ranked evidence, independent oracle       | "It works" judged by the system itself                                     |
| P-21 | Ratchet a migration: shims, shrinking baseline, redirects   | Gradual moves that stall or regress                                         |
| P-22 | Fallback chain skipping rejected versions to a safe mode    | Fallback that restores the bad version                                      |
| P-23 | Destroy what changed so the reconciler recreates it         | Health passing on objects that were not rebuilt                             |
| P-24 | Build in scratch, validate in a sandbox, rename into place  | Half-written live trees during an update                                    |
| P-25 | Signed config bound to one target, newer-only, idle slot    | Replay, downgrade or wrong-target config                                    |
| P-26 | Self-guarding probe for a live system                       | Experiments on the wrong box, or leaving it changed                         |
| P-27 | Verdict ledger apart from the criteria it judges            | Trackers drifting from the design that defines done                         |
| P-28 | Recovery on immutable parts; recoveries count as faults     | Recovery that depends on broken state; hidden self-healing                  |
| P-29 | Clock floor and "expiry unchecked" under untrusted time      | Time checks on clocks known to be wrong                                     |
| P-30 | Solve in a canonical frame, then transform the result       | A solver written for one orientation needed in a mirrored one               |
| P-31 | Append-only event ledger, content IDs, digest-bound approval | Judgements on changing inputs that must survive reruns and edits           |
| P-32 | Repoint callers after a move                                | Moving shared files that many repos call by path                            |

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

> **Learned 2026-10-29 (f)** · P-01 in an analysis tool · VERIFIED_SECONDARY (harvest 2026-10-29 of the apn workspace) · Source: apn `scripts/speed_tier_engine.py` (`CarrierConfig`, `export()`), `scripts/README.md` · Falsifier: a new supplier added to the engine by
> editing the engine rather than by a config object
> A second shape of P-01: one analysis engine, and each supplier supplies a frozen config object (database path, the SQL, rate-card SQL,
> tier and product-group maps) and calls `export()`. The engine's docstring lists the exact columns a supplier's query must return, so the
> query contract is written down, and the workbook it writes keeps live formulas rather than pasted values so a reviewer can audit each
> figure. It refuses to run on an unmapped category rather than dropping its rows.

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
- **Second project (smc-resiliency, `spike/onbox/smcbox/health.py:169-183`):** external reach counts against the change only if it passed
  before and fails after; reach already down is stored as "unjudged" and rechecked later; during an outage new changes are held (a return to
  last-known-good excepted), since a bad change made then could never be judged.

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
- **Realised in:** Ansible, `tasks/pending.yml` (tsh filter: a failed `tsh ls` keeps its targets). Second project: unified-network-controller's
  ownership guard fails open when its catalog cannot be read, because a guard that can only refuse would otherwise take the whole system down
  (P-16).

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

### P-13 Capability table: exists is not proven

> **Learned 2026-10-27 (m)** · design pattern, any language · CANDIDATE (built and tested offline against a fake adapter; no kind enabled live yet) · Source: unified-network-controller `wc-local/scripts/safe_write/capability.py:26-56`, `tests/test_safe_write.py` · Falsifier: a write path used while its row says proven: false
> Pattern P-13, written generically below.

- **Problem:** a risky operation path is switched on because someone wrote it, not because anyone proved it.
- **Solution:** one plain table per target kind: mechanism, rollback class, `proven`, evidence text. Supported means a mechanism exists **and** proven is true; a kind missing from the table is unsupported, not an error. Checked before any adapter is touched; enabling a kind is one row change citing its evidence; a test keeps the table's keys equal to the adapter registry.
- **Why it works:** the system can never claim more than its evidence; the table is the audit trail.
- **Reuse:** payment refunds per provider, migration strategies per database, feature rollout per device class.
- **Pitfalls:** every row still unproven means the path has never run for real; say so in status.
- **Realised in:** Python, unified-network-controller safe_write.

```python
CAPABILITY_TABLE = {"enterprise-wifi": {"write_mechanism": None, "rollback_class": "R0", "proven": False, "evidence": _F1_TODO}, ...}

@property
def supported(self) -> bool:
    return self.write_mechanism is not None and self.proven
```

### P-14 Declared rollback class and explicit end states

> **Learned 2026-10-27 (n)** · design pattern, any language · CANDIDATE (pipeline tested with a fake adapter; not live) · Source: unified-network-controller `wc-local/scripts/safe_write/pipeline.py:1-20`, `rollback.py:3-50` · Falsifier: a run that ends `failed` while the target did change, or a rollback stronger than the one declared
> Pattern P-14, written generically below.

- **Problem:** "rollback" means different things per target, and "failed" hides whether anything changed.
- **Solution:** each target declares its rollback class: R0 stop and tell the operator, R1 the target's own transactional revert, R2 restore a redacted backup (secrets re-injected from the vault only at restore), R3 a compensating write of the previous values. Fixed stages: authorise, capability, back up, validate, delta, preview, apply, read back, verify. Every run ends in one named state (`unsupported`, `not_authorised`, `cancelled` already in state, `failed`, `succeeded`, `rolled_back`, `rollback_failed`) with one correlation id and one JSONL audit line.
- **Why it works:** callers act on a state that says what happened to the target, not on an exception.
- **Reuse:** cloud resource changes, ERP data fixes, firmware pushes.
- **Pitfalls:** never try a stronger rollback than declared; an untested R1 is worse than an honest R0.
- **Realised in:** Python, unified-network-controller safe_write; P-01's smc_change records end in a comparable set (passed, gates_failed, failed, refused, unreachable).

### P-15 Dead-man revert timer armed before the change

> **Learned 2026-10-27 (o)** · design pattern, any language · VERIFIED_PRIMARY (two projects: a bad swap reverted in 100 s on a lab VM; a revert rehearsed on a virtual target) · Source: smc-resiliency `spike/onbox/smcbox/activate.py:185-275`; unified-network-controller `wc-local/scripts/smc/smc_intent.py:696-752` · Falsifier: a target left on a bad change after its controller died mid-change
> Pattern P-15, written generically below.

- **Problem:** a change can kill the process making it, or the connection you would undo it over, and then nobody reverts it.
- **Solution:** before the change, arm a timer that lives on the target and outside the process (a transient systemd timer) to restore last-known-good after a deadline; stage the candidate and keep last-known-good on the target. Apply detached; judge health; success writes a confirm file or cancels the timer, a handled failure reverts and cancels it. The revert also restarts what died under the bad config.
- **Why it works:** the undo does not depend on the thing that may hang, crash or lose its link.
- **Reuse:** remote firewall and DNS changes, database parameter changes, edge and IoT config, feature-flag flips.
- **Pitfalls:** reset the timer's failed state before arming; its deadline must exceed the health deadline; restoring files without restarting services is not last-known-good.
- **Realised in:** Python with systemd, smc-resiliency spike and unified-network-controller smc_intent (two independent projects).

```python
sh(["systemd-run", f"--unit={TIMER_UNIT}", f"--on-active={seconds}", sys.executable, "-m", "smcbox", *action])
...
arm_timer(deadline + 120)
```

### P-16 Ownership and applicability as two axes

> **Learned 2026-10-27 (p)** · design pattern, any language · VERIFIED_PRIMARY (in production since 2026-09-23; tests) · Source: unified-network-controller `nautobot/apps/unc-ownership/unc_ownership/inventory/ownership.py:28-115`, `nautobot/catalog/nautobot/ownership-models.yaml` · Falsifier: a field written by a writer outside its class, or refused because applicability and permission were mixed
> Pattern P-16, written generically below.

- **Problem:** several writers (people, collectors, importers) overwrite each other, and "this field does not apply here" is mixed up with "you may not write it".
- **Solution:** a catalog holds two axes: ownership class (operator, device, inventory, system; mirror or unused in secondary systems) and applicability (capability flags per type). Writers are named accounts; an anonymous writer is a non-writer (fail closed). The guard itself fails open when its catalog cannot be read (see P-10). Applicability enforcement stays behind a flag until run on real data.
- **Why it works:** each question has one place to answer it; new hardware adds capabilities, not exceptions.
- **Reuse:** CRM fields owned by sales vs sync jobs, config keys owned by people vs automation, multi-source master data.
- **Pitfalls:** a per-model `not-applicable` class broke at the first new hardware model; keep applicability as capabilities.
- **Realised in:** Python (Django app) and YAML, unified-network-controller.

### P-17 Neutral contract proven by two consumers

> **Learned 2026-10-27 (q)** · design pattern, any language · VERIFIED_PRIMARY (`just t6` passed; settled the project's D8 decision) · Source: unified-network-controller `adapters/protocol.py:1-70`, `adapters/t6/measure.py:1-105` · Falsifier: a framework noun in a contract identifier, or a shim over its size limit, passing the check
> Pattern P-17, written generically below.

- **Problem:** an abstraction quietly takes on the vocabulary of its first consumer.
- **Solution:** the contract names no framework; it is proven by two thin shims to two different destinations against failure criteria written before the code (either shim over ~300 lines, or any framework-only field needed). Leakage is checked mechanically: an AST scan of class and field identifiers against banned framework nouns; prose is not scanned, so comments may explain.
- **Why it works:** two consumers expose the bias one hides; criteria fixed first cannot be bent to pass.
- **Reuse:** storage-agnostic domain models, payment or SMS provider ports, LLM provider layers.
- **Pitfalls:** scan identifiers, not text, or the check blocks documentation.
- **Realised in:** Python, unified-network-controller.

```python
FRAMEWORK_NOUNS = ("netjson", "openwisp", "nautobot", "netbox", "django", ...)
return [(name, noun) for name in _protocol_identifiers() for noun in FRAMEWORK_NOUNS if noun in name.lower()]
```

### P-18 Clear a stale lock only after proving the owner dead

> **Learned 2026-10-27 (r)** · design pattern, any language · VERIFIED_PRIMARY (tests; used in operations) · Source: unified-network-controller `src/unc/backends/nautobot/stale_locks.py:74-149`, `tests/test_stale_locks.py` · Falsifier: a lock cleared while its owner job was still running
> Pattern P-18, written generically below.

- **Problem:** stuck locks get cleared by hand while the owner is in fact still running.
- **Solution:** dry run by default; one exact key, no wildcards; the owner must be a job in a terminal state; host-idle evidence must be fresh (seconds old) and is re-read just before the delete; every queued or running request is inspected and any unknown state means refuse; the delete is compare-and-swap (watch the lock and queues, `--expected-owner` from the preview).
- **Why it works:** every way the owner could still be alive is a refusal, not a guess.
- **Reuse:** distributed cron locks, leases on stuck CI runners, database advisory locks.
- **Pitfalls:** a preview-then-apply without compare-and-swap races the owner.
- **Realised in:** Python (Redis), unified-network-controller.

### P-19 Rule by class with allow and deny exceptions, deny wins

> **Learned 2026-10-27 (s)** · design pattern, any language · VERIFIED_PRIMARY (production; tests) · Source: unified-network-controller `nautobot/apps/unc-ownership/unc_ownership/inventory/replacement_rules.py:45-67` · Falsifier: an unclassified type accepted without an explicit allow, or a deny overridden
> Pattern P-19, written generically below.

- **Problem:** "may X replace Y?" grows into an N x N table that cannot keep up.
- **Solution:** each type gets two vendor-neutral attributes (placement, function) plus two exception lists (may-replace, never-replaces); fixed order: deny wins; an explicit allow holds even for an unclassified type; unclassified is refused; otherwise both attributes must match. Returns (verdict, reason) and the reason is shown to the approver. The rule imports no framework, so it is tested alone.
- **Why it works:** O(types) data instead of O(types^2); the order makes every verdict explainable.
- **Reuse:** substitute products, equivalent drugs, compatible spare parts.
- **Pitfalls:** keep the rule pure (no framework imports) so its table of cases is tested directly.
- **Realised in:** Python, unified-network-controller.

### P-20 Acceptance evals: ranked evidence, independent oracle, append-only history

> **Learned 2026-10-27 (t)** · design pattern, any language · VERIFIED_PRIMARY (A6 coverage measured; history kept) · Source: unified-network-controller `tests/evals.yaml:7-80`, `tests/history.jsonl` · Falsifier: an eval passing on an oracle that routes through the system it judges
> Pattern P-20, written generically below.

- **Problem:** "it works" is claimed on a transport acknowledgement, against a denominator the system itself controls.
- **Solution:** evidence layers are ranked (transport < stored < rendered < durable); each eval declares its population, an oracle that is independent and does not route through the evaluated path, how long a result stays valid and what invalidates it, and a fixture that can make it fail. Results append to a JSONL history; corrections are new records that supersede, never edits.
- **Why it works:** the claim names its strength; old results cannot be rewritten into passes.
- **Reuse:** data-pipeline SLAs, ML deployment acceptance, migration completeness.
- **Pitfalls:** an oracle sharing the system's code path proves nothing.
- **Realised in:** YAML and JSONL, unified-network-controller; skill-eval-manager carries the general discipline.

### P-21 Ratchet a migration with shims, a shrinking baseline and a redirect map

> **Learned 2026-10-27 (u)** · design pattern, any language · VERIFIED_PRIMARY (tests; warn mode) · Source: unified-network-controller `scripts/govcheck/checks/location.py:18-82`, `scripts/govcheck/config.py:245-270`, `wc-local/scripts/moved-paths.json` · Falsifier: new non-shim code in the old tree passing the check
> Pattern P-21, written generically below.

- **Problem:** a gradual move to a new code location stalls, or new code keeps landing in the old place.
- **Solution:** a shim is detected by AST (docstring starts with "Shim" and it imports the new package); any other module in the old tree must be in a baseline that may only shrink, and a stale entry is reported; warn first, then fail. Retired paths go to a redirect map so dated records still resolve; the map is checked so it cannot excuse a path that is really gone. Size and docstring budgets ratchet the same way.
- **Why it works:** progress is monotone and visible; history keeps resolving.
- **Reuse:** monolith to packages, API v1 to v2, renaming config keys across repos.
- **Pitfalls:** 18 non-shim modules landed in the old tree while no check existed; add the ratchet before the move starts.
- **Realised in:** Python and JSON, unified-network-controller.

### P-22 Fallback chain that skips rejected versions and ends in a safe mode

> **Learned 2026-10-27 (v)** · design pattern, any language · VERIFIED_PRIMARY (5 tests; run on a lab VM) · Source: smc-resiliency `spike/onbox/smcbox/site.py:221-243`, `spike/tests/test_site.py:62-78` · Falsifier: a fallback that restores a version already rejected
> Pattern P-22, written generically below.

- **Problem:** falling back to "the other copy" can bring back the bad version just rejected; falling back to "nothing" leaves stale state running.
- **Solution:** try the committed slot, then the other slot, then a built-in safe mode; rejected version numbers are kept in state and skipped.
- **Why it works:** every step of the chain is a known-good or known-safe state.
- **Reuse:** A/B firmware, blue-green deploys, config rollbacks.
- **Pitfalls:** the idle slot can still hold the rejected set; reverting to nothing leaves old services running.
- **Realised in:** Python, smc-resiliency spike.

```python
if doc.get("set") in state.get("rejected", []):
    continue
...
return json.loads(SAFE_VARS.read_text(...)), "safe mode"
```

### P-23 Destroy what changed so the reconciler recreates it

> **Learned 2026-10-27 (w)** · design pattern, any language · VERIFIED_PRIMARY (finding fixed and tested; a kept rebuild in 2.2 s) · Source: smc-resiliency `spike/onbox/smcbox/activate.py:136-158`, `spike/tests/test_activate.py:35-50` · Falsifier: a health check passing on an object whose definition changed but was not rebuilt
> Pattern P-23, written generically below.

- **Problem:** an apply step does not change identity fields of live objects, so a check passes on the old state (a false pass).
- **Solution:** diff the declared definitions before and after (canonical JSON), delete the live objects that changed or vanished, and let the reconciler recreate them; the presence check and command runner are injected so tests need no root.
- **Why it works:** identity changes become recreates, which the reconciler already handles.
- **Reuse:** immutable fields in infrastructure tools, immutable specs in orchestrators, cache invalidation.
- **Pitfalls:** the false pass was found only by changing an identity field (a VLAN id); test that case.
- **Realised in:** Python, smc-resiliency spike.

```python
for name in sorted(set(before) | set(after)):
    if before.get(name) != after.get(name) and exists(name):
        run(["ip", "link", "delete", name])
```

### P-24 Build in scratch, validate in a sandbox, rename into place, keep the previous

> **Learned 2026-10-27 (x)** · design pattern, any language · VERIFIED_PRIMARY (run on a lab VM: render 0.03 s, checks 0.26 s) · Source: smc-resiliency `spike/onbox/smcbox/site.py:153-205` · Falsifier: a live directory empty or half-written at any moment of an update
> Pattern P-24, written generically below.

- **Problem:** a config tree must be replaced atomically and checked by validators that only read fixed paths.
- **Solution:** render into a fresh directory; run the native validators against it, binding it over the fixed path inside a private mount namespace; rename live to `previous` and the new tree into place; keep `previous` until the next render, since readers may still hold it.
- **Why it works:** the live path only ever holds a validated tree; rename is atomic.
- **Reuse:** web server configs, certificate bundles, static site deploys.
- **Pitfalls:** deleting the old tree before readers refresh left the live path empty for a moment.
- **Realised in:** Python with unshare, smc-resiliency spike.

### P-25 Signed config bound to one target, newer-only, into the idle slot

> **Learned 2026-10-27 (y)** · design pattern, any language · VERIFIED_PRIMARY (tests; a tampered and a replayed set refused on a VM) · Source: smc-resiliency `spike/onbox/smcbox/site.py:72-116`, `siteops.py:111-138` · Falsifier: a replayed or older set accepted, or a set committed before health passed
> Pattern P-25, written generically below.

- **Problem:** a config bundle must not be replayed, downgraded or applied to the wrong target.
- **Solution:** verify the signature; then three fit checks: same hardware id, same compatibility level, set number above the committed one. Write to the idle A/B slot, read back byte for byte, commit only after health passes.
- **Why it works:** binding plus monotone numbers turn replay and downgrade into refusals.
- **Reuse:** firmware and licence files, mobile config bundles, edge model pushes.
- **Pitfalls:** a committed number must be stored where a reset cannot roll it back.
- **Realised in:** Python, smc-resiliency spike.

### P-26 Self-guarding probe for a live system

> **Learned 2026-10-27 (z)** · design pattern, any language · VERIFIED_PRIMARY (three runs captured) · Source: smc-resiliency `scripts/confext_probe.sh:67-104` · Falsifier: the probe running on a host it was not named for, or leaving a changed system file
> Pattern P-26, written generically below.

- **Problem:** an experiment on a live box must not run on the wrong box or leave it changed.
- **Solution:** print the plan unless `--apply`; refuse unless the hostname equals the named lab host and the box is in the expected state; a trap cleans up and checks the restored file matches its backup byte for byte; results as key=value lines; `set -e` off on purpose where probes are expected to fail.
- **Why it works:** every safety condition is checked by the script, not remembered by the operator.
- **Reuse:** chaos experiments, DR drills, one-off production diagnostics.
- **Pitfalls:** a fleet survey built on it still goes one box, then five, then all, with a time limit per call.
- **Realised in:** Shell, smc-resiliency.

```sh
[ "$(hostname)" = "$LAB_HOST" ] || { echo "refusing: this box is $(hostname), not the named lab host $LAB_HOST" >&2; exit 2; }
trap 'cleanup; exit $rc' EXIT
```

### P-27 Verdict ledger apart from the criteria it judges

> **Learned 2026-10-27** · design pattern, any language · VERIFIED_PRIMARY (gates the project check) · Source: smc-resiliency `target-map.yaml:1-35`, `scripts/govcheck/checks/trackers.py:43-64` · Falsifier: a criterion added to a design without a ledger verdict passing the check
> Pattern P-27, written generically below.

- **Problem:** status trackers drift from the design documents that define what "done" means.
- **Solution:** the ledger holds only states, verdicts and evidence; the criteria are parsed from the design documents' checklists. A new checklist item fails the check until the ledger has a verdict; a pass needs `verified` and evidence; tracker pages are rendered from the ledger and drift fails.
- **Why it works:** criteria have one owner (the design), verdicts another (the ledger); neither can silently diverge.
- **Reuse:** compliance control matrices, release readiness checklists, acceptance trackers.
- **Pitfalls:** copying criteria into the ledger recreates the drift.
- **Realised in:** YAML and Python, smc-resiliency (UNC's target-map works the same way).

### P-28 Recovery path on immutable parts only; recoveries count as faults

> **Learned 2026-10-27** · design pattern, any language · CANDIDATE (design only) · Source: smc-resiliency `docs/recovery/identity-partition-and-data-recovery-20261014_1455.md:110-126`, `docs/recovery/smc-hang-recovery-options-20261006_1214.md:81-82` · Falsifier: a recovery path that waits on a writable area, or a watchdog reset reported as healthy
> Pattern P-28, written generically below.

- **Problem:** the path that brings a box back reachable must not depend on what may be broken, and silent self-healing hides faults.
- **Solution:** at boot, bring up the uplink and out-of-band tunnel from the read-only release and identity only; mount the writable area `nofail`; a hardware watchdog resets hangs, and every watchdog reset is recorded as a fault (a persistent history that tells it from a power cut).
- **Why it works:** reachability survives any writable-state damage; recoveries stay visible.
- **Reuse:** appliances, kiosks, remote sensors, edge gateways.
- **Pitfalls:** a recovery counted as uptime hides a failing unit.
- **Realised in:** Design, smc-resiliency.

### P-29 Clock floor and "expiry unchecked" under untrusted time

> **Learned 2026-10-27** · design pattern, any language · CANDIDATE (design only) · Source: smc-resiliency `docs/pi/pi-immutable-smc-image-design-20261014_0850.md:426-428, 784-788` · Falsifier: an expired package rejected, or a healthy committed one torn down, on a clock known to be wrong
> Pattern P-29, written generically below.

- **Problem:** devices boot with clocks far behind (months), so time-based checks mean nothing.
- **Solution:** the clock never runs earlier than the release build stamp; without trusted time a package is accepted on signature and binding and marked expiry unchecked; when trusted time arrives, uncommitted expired packages are refused; a committed healthy package is reported, never torn down, for expiry.
- **Why it works:** time checks run only when time can be trusted, and never break a working target.
- **Reuse:** certificate checks on RTC-less devices, licence expiry offline, token validation after long sleep.
- **Pitfalls:** TLS to the time source itself fails until the clock is right; plan the first sync.
- **Realised in:** Design, smc-resiliency (see also the Pi clock wait in the smc_change verify stage).

### P-30 Solve in a canonical frame, then transform the result

> **Learned 2026-10-27** · design pattern, any language · VERIFIED_PRIMARY (folded flow pages: right-to-left rows routed by the unchanged left-to-right router, every layout audit clean, five consumer drawings byte-identical with the feature off) · Source: skill-drawio `scripts/flowmap/fold.py` (CHANGELOG 20261027, uncommitted at writing) · Falsifier: a mirrored row whose copied arrows fail an audit the unmirrored row passes
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-30, written generically below.

- **Problem:** a tuned solver (a router, a layout, a parser) assumes one orientation; a feature needs the mirrored or rotated case, and teaching every
  function a second direction spreads conditionals through code that took many reviews to get right.
- **Solution:** run the solver unchanged on a scratch copy laid out in its own frame, record what it produced (the call arguments, keyed by
  what survived its own undo passes), then replay the result into the real output through the transform. Only cases the frame cannot hold
  (here, arrows between rows) are solved in the real frame.
- **Why it works:** the transform is an isometry, so every property the solver guarantees (clearances, no overlaps) survives it; the solver
  stays one tested path.
- **Reuse:** right-to-left text layout through a left-to-right engine; a mirrored board in a game AI; a reversed time axis through a forward
  scheduler.
- **Pitfalls:** results that encode the frame (a label "left of" a line) must be re-anchored after the transform; record by (id, final geometry),
  not by id, when the solver can retry and roll back; outputs that depend on the surroundings (a background colour sampled under a label) need
  the scratch copy to hold the same surroundings.
- **Realised in:** Python, skill-drawio `scripts/flowmap/fold.py` (`_Scratch`, `_copy_routes`, `_copy_marks`):

```python
class _Scratch(Page):
    def route(self, cid, src, dst, points, style, klass="thick", layer="1", ignore=(), jump=0.0):
        super().route(cid, src, dst, points, style, klass, layer, ignore, jump)
        self.route_args[(cid, tuple(self.routes[-1].points))] = (style, klass, layer, tuple(ignore), jump)

def _copy_routes(scratch, page, axis):
    for rt in scratch.routes:   # only what survived the uncrossing pass
        style, klass, layer, ignore, jump = scratch.route_args[(rt.cid, tuple(rt.points))]
        pts = [(axis - x, y) for x, y in rt.points] if axis is not None else rt.points
        page.route(rt.cid, rt.src, rt.dst, pts, style, klass, layer, ignore, jump)
```

### P-31 Append-only event ledger, content-derived IDs and approval bound to a body digest

> **Learned 2026-10-27** · design pattern, any language · VERIFIED_PRIMARY (skill-knowledge-curator: 42 tests incl. rerun-appends-nothing, render-twice-identical, wrong-digest-refused, hand-edit-detected) · Source: skill-knowledge-curator `scripts/knowledge_curator_lib/state.py`, `ids.py`, `render.py`, `promote.py` (uncommitted 2026-10-27) · Falsifier: a rerun on unchanged input that appends a record, or an approval that survives an edit to the approved text
> (reusable_candidate: proven in one project, not yet in a second) Pattern P-31, written generically below.

- **Problem:** a tool records judgements (decisions, dispositions, approvals) about inputs that keep changing, must never lose history, must be safe to rerun, and must not let an approval given to one
  text cover a later, different text.
- **Solution:** (1) every write is an appended event in a JSONL ledger; the current state is a fold where the last event per ID wins; (2) IDs are hashes of the content that defines identity (subject,
  predicate, object and scope; a section's heading path and text), never of a path, line number or counter, so the same input gives the same ID and intake skips what is already recorded; (3) an
  approval stores the SHA-256 of the approved body (text after a marker line, so a status banner can change without voiding it) and every later check compares it with the file on disk.
- **Why it works:** idempotence falls out of identity (no "already done" bookkeeping); history is the file itself; a reversal is a new event naming the old one; a silent edit becomes a digest mismatch
  a validator can fail on.
- **Reuse:** review queues, approval workflows, data-migration ledgers, config promotion, any generated document that becomes authoritative.
- **Pitfalls:** an ID that includes a field which legitimately changes (wording) splits one thing into two, and an ID that omits a field that distinguishes things (the object of a claim) merges a
  conflict into a silent "newer wins"; choose identity fields deliberately and test both. Exclude volatile fields (timestamps) from IDs and from rendered output, or reruns churn.
- **Realised in:** Python, skill-knowledge-curator:

```python
def make_id(prefix: str, *parts, length: int = 12) -> str:      # ids.py
  return f"{prefix}-{sha256_text(canonical(list(parts)))[:length]}"

claim_id = make_id("cl", project_id, norm(subject), norm(predicate), norm(object), scope)   # object in the key: no newest-wins
if prior and prior["version_id"] == version["version_id"]:      # claims.py: rerun appends nothing
  res.skipped += 1

def body_digest(text: str) -> str:                              # render.py: banner above the marker may change
  return sha256_text(text.split(BODY_MARK, 1)[1] if BODY_MARK in text else text)
```

### P-32 Repoint callers after a move: plan, skip history, guard local namesakes

> **Learned 2026-10-27** · design pattern, any language · VERIFIED_PRIMARY (reusable_candidate: proven in one project) · Source: skill-ai-it: 467 references in 43 files across 30 projects repointed when its flat scripts/ became family folders; every caller's check run after, no path errors · Falsifier: a repoint run whose plan rewrote a local file that merely shares the moved script's name, or left a caller still using the old path (Pattern P-32)

- **Problem:** a shared tool's files move, and many other repositories call them by path from task runners, docs and code; a blind search and replace
  breaks history and hits unrelated files that happen to share a name.
- **Solution:** (1) the move is data: a map of name to new folder; (2) a plan-by-default rewriter matches only the old qualified form (`scripts/<name>.py`,
  not a path already moved), prints counts per file and writes with `--apply`; (3) it skips history by file kind (change logs, history and archive folders,
  dated `<slug>-YYYYMMDD_hhmm` files, generated context, vendored clones); (4) it leaves a reference alone when the caller's own project has a file by that
  name; (5) then every caller's own check runs and its output is searched for path errors specifically.
- **Why it works:** the plan shows the blast radius before a write; idempotence comes from matching only the old form; the namesake guard keeps a local
  copy's references local; running callers' checks proves behaviour, not text.
- **Reuse:** renaming a shared library module, moving a config file other repos read, retiring a recipe name across a fleet of task runners.
- **Pitfalls:** (a) code that builds the path (`DIR / f"{name}.py"`) has no old string to match: grep for the folder constant as well and fix those loaders
  to search the new layout (two projects on 2026-10-27); (b) dated sections inside a living file (a SCRATCHPAD session block) are history too, and were
  rewritten until a rotation audit reported them lost; (c) a self-check whose scans were flat (`scripts/*.py`) silently dropped 81 assertions after the
  move: recount a checker's assertions before and after, and make scans recursive.
- **Realised in:** Python, skill-ai-it `scripts/adoption/repoint_paths.py`:

```python
pattern = re.compile(r"(?<![\w-])scripts/(" + "|".join(map(re.escape, sorted(mapping))) + r")\.py\b")

def swap(match):
  name = match.group(1)
  if has_local(path, name, root):      # the caller's project has its own scripts/<name>.py: leave it
    return match.group(0)
  return f"scripts/{mapping[name]}/{name}.py"

if DATED.search(path.name):             # -YYYYMMDD_hhmm.md: a dated report or record is history
  return True
```

### P-33 Read every source, merge, then write once; write nothing when a source is silent

> **Learned 2026-10-29** · design pattern, any language · VERIFIED_PRIMARY (reusable_candidate) · Source: unified-network-controller `wc-local/scripts/collector/dhcp_leases.py` `check_site`, commit 5505ab5: three DHCP servers at one site, 242 + 211 + 157 leases merged, one write · Falsifier: a merged write that ended a client lease one source still held, or a write made while one source was failing (Pattern P-33)

- **Problem:** several sources each hold part of one record (three redundant boxes each lease part of a site's clients); a loop that writes per
  source lets the last source win and can end what the others hold.
- **Solution:** read all sources (in parallel, bounded), merge by key, then write the record once; when any source fails, write nothing for that
  record and report it, since a partial merge would look like loss.
- **Why it works:** the write sees the whole truth or none of it; sessions keyed by the union are never ended by a source that simply was not read.
- **Reuse:** any per-site aggregate fed by several collectors (leases, neighbours, inventories from redundant controllers).
- **Pitfalls:** a single-source site must keep its old behaviour byte for byte; a source that legitimately has nothing differs from a failed read.
- **Realised in:** Python:

```python
with ThreadPoolExecutor(max_workers=min(BOX_WORKERS, len(smcs))) as pool:
    reads = list(zip(smcs, pool.map(lambda box: read_one(box, domain), smcs)))
failed = [(box, raw["error"]) for box, raw in reads if "error" in raw]
if failed:   # a partial set would end the silent box's sessions: write nothing for the site
    ...
merged = merge_reads(reads)          # sums and unions by address, then one PATCH and one sync
```

### P-34 Pick a moving leader once per cycle

> **Learned 2026-10-29** · design pattern, any language · VERIFIED_PRIMARY (reusable_candidate) · Source: unified-network-controller `src/unc/tasks/site_readers/serving_box.py` `CyclePicks`, 5505ab5: the VRRP master moved about hourly; polling picks it once per cycle · Falsifier: two callers in the same cycle acting on different leaders after a mid-cycle failover (Pattern P-34)

- **Problem:** work must go through whichever member currently leads (a VRRP master), and the leader can move mid-run.
- **Solution:** at the start of a cycle read every member's state in parallel, pick the leader (fallback: configured priority order, said aloud;
  two leaders: the first by priority, both named), then hand every caller in that cycle the same pick.
- **Why it works:** a cycle never straddles two vantage points, so readings are comparable; a flap costs one cycle, not half-done data.
- **Reuse:** any active/standby pair or cluster with a floating address.
- **Pitfalls:** cache per cycle, never across cycles; a single-member case must cost zero extra calls.
- **Realised in:** Python: a lock-guarded `dict[site, Pick]` filled on first `get(site)` (`CyclePicks`).

### P-35 Place by evidence; keep every sighting in a listed ledger

> **Learned 2026-10-29** · design pattern, any language · VERIFIED_PRIMARY (reusable_candidate) · Source: unified-network-controller `src/unc/policy/multi_smc_topology.py`, 5505ab5: a layer-2 site where every box sees every device · Falsifier: a source link that is neither drawn nor listed in the ledger, or a link drawn from a sighting with no physical evidence (Pattern P-35)

- **Problem:** on a shared network every observer sees everything, so "seen by X" drawn as links becomes all-to-all spaghetti.
- **Solution:** place only by evidence that names a physical relation (a MAC learned alone on a cable port, a held link); everything else is
  conserved in a ledger listed beside the drawing (unplaced, sighting only); every source link is either drawn or listed exactly once.
- **Why it works:** the drawing stays true and readable, and nothing is silently dropped; conservation is testable.
- **Reuse:** topology from LLDP/ARP/FDB, dependency graphs from logs.
- **Pitfalls:** never fall back to "first observer wins"; show an undecidable item as unplaced.

### P-36 Widen a name's scope by renaming in place, never by recreating

> **Learned 2026-10-29** · design pattern, any language · VERIFIED_PRIMARY (reusable_candidate) · Source: unified-network-controller `wc-local/scripts/smc/smc_uplink_circuits.py` `rename_legacy`, e62633c: a site gained two more boxes, so `<site>-internet02` became `<box>-internet02` · Falsifier: an object whose cables or change log were lost because it was recreated under the new name rather than renamed (Pattern P-36)

- **Problem:** an identifier was built from a scope that turned out too wide (one name per site, but now there are several boxes per site);
  the new scheme gives every new object a narrower name, while the objects already made carry history (cables, links, change log) under the old one.
- **Solution:** the plan row carries both the new name and the legacy one; on apply, when the legacy object exists and the new name is free,
  PATCH its name; when both exist, change nothing and report it for a person; the dry run says "would rename". Then the usual find-or-create
  runs on the new name and finds the renamed object.
- **Why it works:** identity is the object, not its name, so everything attached stays attached; the rename is idempotent (the second run finds
  no legacy object), and a clash never picks a winner silently.
- **Reuse:** any naming scheme whose scope widens later: per-box after per-site, per-tenant after global, a version or region added to a key.
- **Pitfalls:** scope the lookup (provider, Location) so a namesake elsewhere is not renamed; single-scope cases must produce identical names
  (new == legacy) and cost no extra calls.
- **Realised in:** Python:

```python
def rename_legacy(c, path, field, legacy, name, scope, counts, log=print):   # smc_uplink_circuits.py (e62633c)
    if not legacy or legacy == name:
        return
    old = c.first(path, f"{field}={q(legacy)}&{scope}")
    if old is None:
        return
    if c.first(path, f"{field}={q(name)}&{scope}"):
        log(f"  note: both {legacy} and {name} exist; {legacy} left for the operator")
        return
    c.call("PATCH", f"{path}{old['id']}/", {field: name})
```

### P-37 A cache proved by a differential assert, keyed so an undo hits

> **Learned 2026-10-29** · design pattern, any language · VERIFIED_PRIMARY (reusable_candidate) · Source: skill-drawio `scripts/flowmap/e2e.py` `_refresh` and `_crossings`, 73017a9 and 811c918: a local search's crossing counts, 18.3 -> 10.1 s on the largest drawing, output byte-identical · Falsifier: the differential assert passing while cached and recomputed values differ, or an undo that misses the cache (Pattern P-37)

- **Problem:** a search recomputes a pure but costly value (crossings of a polyline pair, spans of a link) millions of times, and most trials
  are undone; a cache invalidated by version numbers misses on every undo, and a cache updated at many mutation sites goes stale at one.
- **Solution:** key the memo on the content (intern each polyline as a tuple to a small id; cache per pair of ids), or keep the cache at the
  one choke point every mutation already passes through (`_refresh`). Prove it before trusting it: a temporary switch computes the fresh value
  beside the cached one and asserts they match on every call over every real input (all consumers and the tests), then is removed; the
  outputs must still compare byte for byte.
- **Why it works:** an undo restores the same content and so the same key; a pure function of its key never needs invalidating.
- **Reuse:** any trial-and-undo search (layout, scheduling, packing), memoised geometry, incremental scores.
- **Pitfalls:** a cache whose validity depends on all mutation sites (a position index into a list mutated everywhere) needs a
  check-before-use test instead, and earns its keep only when measured (0.3 s here: reverted); watch memory (211 MB peak here).
- **Realised in:** Python:

```python
self.shape[cid] = self.shape_ids.setdefault(tuple(self.pts[cid]), len(self.shape_ids))   # e2e.py _refresh (811c918)
...
key = (ka, shape[b])   # an undone trial redraws the same polylines, so most pairs were counted before
c = memo.get(key)
if c is None:
    c = memo[key] = count_crossings(sa, sb)
```

### P-38 An estimate nominates; the real measure decides, never worse than the start

> **Learned 2026-10-29** · design pattern, any language · VERIFIED_PRIMARY (reusable_candidate) · Source: skill-drawio `scripts/flowmap/e2e.py` `routed_e2e` and `placement.best_cells`, 1e6557d: a column-order search scored by a grid estimate made two pages worse, 427 -> 506 and 44 -> 48 crossings · Falsifier: a shipped result whose real measure is worse than the starting layout on any tracked metric (Pattern P-38)

- **Problem:** a search scored by a cheap proxy finds the proxy's optimum, which on real output can be worse than doing nothing, or better
  on the main measure and worse on another (two arrows merged onto one run).
- **Solution:** keep the start as a candidate; run each candidate through the real pipeline and measure what is shipped; keep a candidate only
  on a strict improvement of the main measure with no regression of the guarded ones; a tie keeps the start.
- **Why it works:** the result is never worse than the start by construction, so the search can only help; the proxy only orders the work.
- **Reuse:** placement, query plans, compiler heuristics, any optimiser with a cheap model and an expensive truth.
- **Pitfalls:** the guard must measure the same thing a reviewer sees (a drawn-file measure, not the proxy); name the guarded secondary measures.
- **Realised in:** Python:

```python
searched = EndToEnd(data, profile, numbers)   # e2e.py routed_e2e (1e6557d)
plain = EndToEnd(data, replace(profile, look={**profile.look, "e2e_row_search": False}), numbers)
return searched if searched._crossings(set(searched.segs)) < plain._crossings(set(plain.segs)) else plain
```

### P-39 Carry a placement over proven edges; narrow the rest by the network's direction

> **Learned 2026-10-29** · design pattern, any language · VERIFIED_PRIMARY (reusable_candidate) · Source: unified-network-controller `src/unc/policy/colocation.py`, a8c58f9: one site went from 0 of 110 units placed to 85, 1 conflict held, in 0.03 s, with no site-specific rule · Falsifier: a unit placed by carry-over across a wireless or uplink edge, or two conflicting placements resolved silently by processing order (Pattern P-39)

- **Problem:** where each item stands (a tower, a rack, a room) is known for a few items only, sites are built and named differently, and a
  rule written for one site's habit (a number in a name) misplaces the next site's units.
- **Solution:** a graph of typed edges. Anchors are the few items placed by strong evidence. Edges that prove "together" (a cable seen by
  LLDP or recorded, shared power) carry a placement, repeated to a fixed point; edges that prove "apart" (a radio link) never do; edges that
  only say "somewhere behind X" narrow the candidates to what lies downstream of X in the network's direction (through access radios, never
  back up through an uplink). A name is a tie-breaker only when a token names exactly one candidate. Two placements reaching one item are held.
- **Why it works:** every placement carries the chain of evidence that made it, so it can be gated by strength (separate apply flags) and
  audited; nothing depends on a convention; disagreement surfaces instead of resolving by processing order.
- **Reuse:** asset placement from discovery, rack/room inference from switch ports, service-to-host mapping from traffic, any "where is it" over
  partial evidence.
- **Pitfalls:** a forwarding table is not a cable (a port can front a transparent bridge); a carried hub drags its neighbours unless hub-to-hub
  needs direct proof; a "one per slot" assumption runs last and only when no rival wants the slot; report the unplaced with their candidates.
- **Realised in:** Python:

```python
while changed:                                   # colocation.propagate (a8c58f9)
    changed = False
    for a, z, source in together:                # LLDP or a Cable, or shared power; never wireless
        for src, dst in ((a, z), (z, a)):
            if src not in at or dst in skip or dst in clash or classes.get(dst) == "root":
                continue
            if dst not in at:
                at[dst], via[dst] = at[src], f"{source} from {src}"
                changed = True
            elif at[dst] != at[src] and dst not in placed:
                clash[dst].update({at[dst]: via.get(dst, "anchor"), at[src]: f"{source} from {src}"})
```

### P-40 Hold citations by a check: a ledger of every cited URL, a local copy keyed by URL, rules as findings

> **Learned 2026-10-29** · design pattern, any language · VERIFIED_PRIMARY (reusable_candidate) · Source: skill-network-architect `scripts/check_package.py` check_ledger and check_prose, `scripts/fetch_sources.py`, `scripts/sources_ledger.py`; uncommitted at write time: 356 sources stored, 271 ledger entries, every rule failing its own negative test · Falsifier: a citation that lands in a reference while just check still passes without its sources.json row (Pattern P-40)

- **Problem:** reference documents decay quietly: links rot, a claim loses its source, a rewrite drops a citation, and writing rules (width,
  diagram form, link form) hold only while someone remembers them. Review catches some of it once; nothing catches it on the next edit.
- **Solution:** three parts. (1) A fetcher keeps a local copy of every cited URL in a store keyed by URL, with an index (path, sha256,
  retrieved); plan by default, `--apply` writes, resumable from the index, bounded workers, a process-group kill on timeout. (2) A ledger
  builder keeps curated evidence entries and catalogues every other cited URL as generated, attaching the local copy. (3) The offline check
  fails on any cited URL missing from the ledger and on each writing rule, and every rule has a negative test that breaks it on purpose.
- **Why it works:** the expensive, networked parts (fetch, link probe) run on demand; the cheap invariant (cited implies catalogued) runs on
  every check, so a new citation cannot land without its ledger row and the fetch that gives it a local copy.
- **Reuse:** any knowledge pack, runbook set or design repo that cites external material; vendor-document stores; research reports.
- **Pitfalls:** a 2xx proves a page exists, not that it still says what was claimed; 401/403/429 and TLS chain errors are unknown, not
  dead; JS-rendered pages return near-empty bodies, so set a body floor and retry with a JS renderer; URLs with parentheses need a balanced
  pattern; a store shared by two packs lives in one and the other symlinks it.
- **Realised in:** Python:

```python
def check_ledger(root):                          # check_package.py (skill-network-architect)
  known = {e.get("url") for e in json.loads((root / "sources.json").read_text()).get("sources", [])}
  findings = []
  for path in [root / "SKILL.md", *(root / "references").glob("*.md"), *(root / "templates").glob("*.md")]:
    text = re.sub(r"```.*?```", "", path.read_text(), flags=re.DOTALL)   # diagrams and code are not citations
    for url in sorted(set(LEDGER_URL.findall(text))):
      if url.rstrip(".,;:") not in known:
        findings.append(f"source not in sources.json (run just ledger --apply): {path.name}: {url}")
  return findings
```

### P-41 Write into files other sessions are editing: a marked region, compare-and-swap, a settle window, idempotent ids

> **Learned 2026-10-29** · design pattern, any language · VERIFIED_PRIMARY (source read 2026-10-29; the project records 0.06-0.4 s per run and a self-test of about 3 s proven able to fail by breaking two features) · Source: apn `scripts/project_sync.py` (`write_cas`, `recently_edited`, `SYNC_ID`; commit e69d6d7), `scripts/project_sync_selftest.sh` · Falsifier: a delivery that overwrote a live
> session's edit, or was delivered twice after a crash (reusable_candidate) Pattern P-41.

- **Problem:** a tool delivers messages or rows into files that live agent sessions are editing at the same time (scratchpads,
  trackers). A plain read-modify-write loses the session's edit; a crash mid-delivery leaves no way to know what was sent.
- **Solution:** (1) write only between start and end markers (`<!-- sync:<box>:start -->` ... `end`), never elsewhere in the file;
  (2) one exclusive lock for the tool; (3) compare-and-swap: re-read just before an atomic replace and write nothing if the file changed
  since it was read (defer to the next run); (4) a settle window: a target edited in the last N seconds is deferred; (5) every item
  carries an id, searched in the target and in the places rotation moves lines to before delivery, so a rerun after a crash skips what
  arrived; (6) an item marked sent but now missing is reported (exit 1), never re-sent, because someone removed it on purpose or by
  accident and only a person can tell which. Exit 0 clean, 1 needs attention, 2 usage.
- **Why it works:** the writable region bounds the damage, CAS and the settle window keep the tool out of a live edit, and ids make
  delivery idempotent without a separate state file that could disagree with the target.
- **Reuse:** status pages several tools update; inbox files between agents; generated blocks inside hand-edited documents.
- **Pitfalls:** the id must survive wrapping (no spaces in the comment); search rotated history too or a rotated item is re-sent; a
  self-test must be shown to fail when a feature is broken, or it proves only that the happy path runs.
- **Realised in:** Python:

```python
def write_cas(path, before, after):                     # apn scripts/project_sync.py
    if path.read_text() != before:
        return False                                     # changed since read: defer
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        fh.write(after)
    os.chmod(tmp, path.stat().st_mode & 0o777)
    if path.read_text() != before:                       # re-check after the slow part
        os.unlink(tmp)
        return False
    os.replace(tmp, path)
    return True

def recently_edited(path, settle):
    return settle > 0 and time.time() - path.stat().st_mtime < settle
```

### P-42 Three outcomes for a lookup: a negative only from a complete walk

> **Learned 2026-10-29 (b)** · design pattern, any language · VERIFIED_PRIMARY (source read 2026-10-29) · Source: project_stuff/me vehicle-import track `scripts/rover_sevs_query.py` (`classify`) · Falsifier: a NOT_FOUND emitted while a page
> of the register was never read (reusable_candidate) Pattern P-42.

- **Problem:** an earlier helper read only the first page of a paginated register and reported "not found", and the untested negative
  entered the knowledge base as a fact.
- **Solution:** every lookup returns FOUND, NOT_FOUND or CHECK_FAILED. NOT_FOUND is emitted only when every page was walked
  (`pages_seen == pages_total`); any tool error, missing dependency or short walk is CHECK_FAILED with a reason. Match locally on the
  fetched rows rather than trusting the site's own filter.
- **Why it works:** "absent" becomes a claim that needs proof of coverage; incomplete coverage has its own name and cannot be read as a
  negative.
- **Reuse:** fleet surveys (a device not answering is not a device without the feature), inventory reconciliations, licence and
  registration checks, log searches over a retention window.
- **Pitfalls:** a recorded "none" without a completeness flag should be read as "not found by this search", not "does not exist"; a
  site's search box is a filter you cannot audit.
- **Realised in:** Python:

```python
def classify(scan, targets):                    # rover_sevs_query.py: never guesses
    out = {}
    for label, terms in targets.items():
        if not scan["ok"]:
            out[label] = {"status": "CHECK_FAILED", "reason": scan["error"], "hits": []}
            continue
        hits = [r for r in scan["rows"] if any(t in r["_raw"].lower() for t in terms)]
        if hits:
            out[label] = {"status": "FOUND", "hits": hits}
        elif not scan["complete"]:
            out[label] = {"status": "CHECK_FAILED", "hits": [],
                          "reason": f"incomplete scan: saw {scan['pages_seen']}/{scan['pages_total']} pages"}
        else:
            out[label] = {"status": "NOT_FOUND", "hits": []}
    return out
```

### P-43 Fail-closed capture: classify the body before writing evidence

> **Learned 2026-10-29 (c)** · design pattern, any language · VERIFIED_SECONDARY (harvest 2026-10-29 of two personal research projects) · Source: project_stuff/me vehicle-import track `scripts/README.md` (browser_fetch row) · Falsifier: an access-denied, bot-check or
> consent page stored as evidence by a capture tool with a body classifier (reusable_candidate) Pattern P-43.

- **Problem:** a capture tool stores fetched pages as evidence. Every failure observed (access denied, a bot interstitial, a cookie wall)
  arrived as HTTP 200 with a full body, so status-code checks stored junk as evidence.
- **Solution:** stamp each capture with URL, retrieval time, HTTP status, the page's own last-updated line and a body hash; run a
  classifier that must rule the body to be the expected content before anything is written; refuse to write an unclassified body. Keep
  404s and refused captures, labelled as negative evidence, rather than deleting them.
- **Why it works:** the write is gated on what the body is, not on what the transport said.
- **Reuse:** vendor-document stores, compliance evidence capture, API scrapers whose errors come back as 200 with an error page.
- **Pitfalls:** classifiers drift as sites change; keep the rejected bodies so a misclassification can be reviewed.
- **Realised in:** Python (browser capture), personal research project; excerpt not taken.

### P-44 Classify by a declared list and surface the unclassified

> **Learned 2026-10-29 (d)** · design pattern, any language · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal project) · Source: project_stuff/me reporting project `scripts/work-summary-digest.py`, `scripts/work-summary-report.py` · Falsifier: a digest that
> silently includes or drops a project missing from its config list (reusable_candidate) Pattern P-44.

- **Problem:** a digest groups records (here: projects in a session-memory store) by a config list; a new record outside the list is
  either silently dropped or silently lumped in, and the report looks complete.
- **Solution:** read the store read-only; classify from the declared list; warn loudly on every unclassified record; filter known noise by
  declared patterns; append output as dated, fenced sections with a generated marker instead of merging into earlier text; roll
  out-of-period sections to archive files idempotently. A second tool imports the first's rules instead of copying them.
- **Why it works:** the unclassified count is the coverage signal; appending keeps every generated section reproducible and reviewable.
- **Reuse:** cost allocation by tag, alert routing tables, changelog digests, any report built from a mapping that can lag reality.
- **Pitfalls:** a rollover that removes sections leaves a contents block stale unless it is rebuilt in the same run.
- **Realised in:** Python, personal reporting project; excerpt not taken.

### P-45 A document an automation edits is a contract: check its shape, test with a fixture

> **Learned 2026-10-29 (e)** · design pattern, any language · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal project) · Source: project_stuff/me finance-notes project `scripts/moon_list_ops.py` · Falsifier: a hand-renamed column in the edited table that the tool
> writes through without stopping (reusable_candidate) Pattern P-45.

- **Problem:** a helper updates Markdown tables that people also edit; a renamed column or reordered header makes it write values into
  the wrong place, and it can only be tested against the live API.
- **Solution:** before any write, check that each target file still matches its expected header contract (the exact column list); take
  data from the API or from a deterministic fixture file; render a no-write draft by default and write only on apply. A malformed
  contract or fixture is a hard stop.
- **Why it works:** the contract check turns a silent misplacement into a refusal, and the fixture makes the whole path testable offline.
- **Reuse:** trackers and registers maintained in Markdown or CSV by both people and scripts; generated rows inside hand-kept tables.
- **Pitfalls:** check the contract on every run, not once at setup; people edit headers.
- **Realised in:** Python, personal project; excerpt not taken.

### P-46 Audience words at the output boundary, with a guard that refuses a leak

> **Learned 2026-10-30** · design pattern, any language · VERIFIED_PRIMARY (source read and run 2026-10-30: 2,000+ texts per workbook, 0 left; 15 tests) · Source: apn unified-network-controller
> `src/unc/tasks/site_workbook/xlsx.py` (`team_text`, `team_words`; uncommitted at write time) · Falsifier: a generated workbook for the team that still names the internal platform (reusable_candidate) Pattern P-46.

- **Problem:** a generator's model, notes and tests speak the internal platform's language ("in Nautobot, not drawn", source `nautobot`),
  but the document goes to people who never use that platform. Renaming through the model breaks the internal readers and tests;
  editing the output by hand is lost on the next run.
- **Solution:** keep the model's words; translate once where the file is written: an ordered table of specific phrases (most specific
  first, so they read naturally), then a general regex fallback, applied to every cell, comment and validation prompt; then scan the
  finished file and **raise** if the forbidden term survives anywhere. Source labels go through a separate display map.
- **Why it works:** the model and its tests stay unchanged; the fallback means no phrase leaks, and the guard turns a phrase the table
  missed into a refused write rather than a document that quietly leaks.
- **Reuse:** customer-facing exports of internal data, reports that must not name a vendor, redaction of hostnames from shared logs.
- **Pitfalls:** formula cells must be skipped (their text is code); comments are replaced, not edited in place, in openpyxl; the
  fallback's grammar is rough, so grow the specific table from each run's output.
- **Realised in:** Python (openpyxl). Excerpt:

```python
def team_text(text: str) -> str:
  for old, new in TEAM_PHRASES:          # specific phrases first
    text = text.replace(old, new)
  for pattern, new in TEAM_FALLBACK:     # then any other mention
    text = pattern.sub(new, text)
  return text

# team_words(wb): every cell (not formulas), comment and validation prompt through team_text,
# then: if any text still contains "nautobot": raise ValueError(f"workbook still names Nautobot at ...")
```

### P-47 Decide per item once from read facts, persist the decision, never re-judge it

> **Learned 2026-10-30** · design pattern, any language (realised in Ansible) · VERIFIED_PRIMARY (offline: 17-assert fixture incl. resume; real spec
> judged for 4 fact/flag combinations; fact read on 2 live boxes) · Source: local-knowledge-ansible `ansible-wifi/roles/smc_change/tasks/conditions.yml`,
> `backup.yml`, `rollback_locate.yml`, commit 7ef59c7 · Falsifier: a resumed or rolled-back run whose action set differs from the original run's (reusable_candidate)

- **Problem:** a change runner must do different steps on different targets (flash only where the firmware is old; ship only the rollback image
  the target needs), and the facts that decide it are on the target. The change itself moves those facts, so a resume or a rollback that
  reads them again picks a different set of steps: it skips a half-done step or undoes one that never ran.
- **Solution:** read the facts with a read-only call before anything else, judge named conditions into one decision (which step indexes run,
  which checks apply, which were skipped and why), and persist that decision with the transaction: the resume journal and the backup it would
  roll back from. Resume and rollback load the decision; they never judge again. A fact that cannot be read refuses the target.
- **Why it works:** the decision is part of the transaction, like its baseline: everything after it (checks, plan, gates, undo) agrees on one
  set of steps. Conditions are named and the plan prints the failed name per skipped step, so a skip is visible, not silent.
- **Reuse:** firmware updates by current version, package changes by installed set, migrations by schema version, any rollout whose steps
  depend on per-target state.
- **Pitfalls:** keep the facts out of anything hashed before they are read (the run fingerprint, the target identity); keep the per-step
  `when` out of the identity of what is applied, or adding a condition reruns every finished target; give old backups without a saved
  decision the old behaviour (undo everything).
- **Realised in:** Ansible (smc_change). Excerpt:

```yaml
# tasks/backup.yml (7ef59c7): the decision goes with the backup a rollback restores
- name: List the actions this apply runs, for a rollback
  ansible.builtin.copy:
    content: |
      {% for a in smc_change_actions %}
      {% if smc_change_active is not defined or loop.index0 in smc_change_active %}
      {{ loop.index }} {{ a.type }}
      {% endif %}
      {% endfor %}
    dest: "{{ smc_change_backup_path }}/actions.txt"
# tasks/main.yml: a resume restores the journal's decision (conditions.yml step restore), never a fresh read
```

## Language realisations

Built: the project has it in that language (source named in the pattern). Suggested: a sketch for a project in that language, not yet
built anywhere; move it to built, with its source, when a project does.

| Pattern | Ansible (`languages/ansible.md`)                                     | Python (`languages/python.md`)                                  |
| ------- | -------------------------------------------------------------------- | --------------------------------------------------------------- |
| P-01    | built: `include_tasks` per action type, `<type>_rollback` in reverse | built: probe check registry `register(Check(...))`              |
| P-03    | built: journal and recovery tasks; Learned (e) drop-proof waits      | built: `recovery.py` pure classification over the journal       |
| P-05    | built: no-serial first play + `group_by`; Learned (g), (j)           | suggested: build the plan once, then a bounded worker pool      |
| P-06    | built: `async` + `poll: 0` + await; Learned (e), (i)                 | suggested: detached job id + idempotent status poll             |
| P-09    | built: joined probe piped on stdin                                   | built: `files/probe/NN_*.py` parts joined into one program      |
| P-12    | built: `--check` before apply                                        | built: `smc_change_runs_by_flavor.py` `plan()` then `--apply`   |

> **Learned 2026-10-28** · optimise the real outcome, not a proxy · VERIFIED_PRIMARY (skill-drawio overview group placement, UNC overview: 245 crossings) · Source: skill-drawio `scripts/flowmap/placement.py` (`group_candidates`, `best_cells`) · Falsifier: a search on a
> proxy score that keeps improving the real measure as it searches harder
> A cheap proxy can rank candidates but must not choose: scoring group placements by straight-line crossings gave 131 real crossings with
> 12 restarts and 182 with 40 (the proxy improved, the drawing got worse); a channel-path proxy gave 192 and 171. Generate candidates with the
> proxy (several seeded starts, as Graphviz and ELK do), then evaluate each with the real computation and keep the best; include the current
> state as a candidate so the result is never worse: 130 real crossings, stable.

```python
best, best_n = current, real_cost(current)
for cand in candidates(current)[1:]:          # proxy-ranked, current first
    n = real_cost(cand)                       # the real thing (here: route and count)
    if n < best_n:
        best, best_n = cand, n
```
