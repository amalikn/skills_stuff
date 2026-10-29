---
Title: Safety and writes
Category: reference
Status: current
Authority: local-supplement
Scope: Code that changes anything outside its own process - files, databases, devices, remote systems
Last reviewed: 2026-10-19
Summary: >-
  Read by default, plan then --apply, write gates the code enforces, credentials never in code, one writer per record,
  idempotent writes, record only after the target confirms, fail closed, and canary before batch.
---

# Safety and writes

## Contents

- [Rules](#rules)
- [The write chain](#the-write-chain)
- [Deleting](#deleting)
- [Canary before batch](#canary-before-batch)
- [Changing an identifier](#changing-an-identifier)

## Rules

| Rule                                                                                                                                            | Why                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Read is the default. A program that can write prints its plan without a flag and writes only with `--apply` (or the project's equivalent)       | A first run on a new input is always safe          |
| The gate is enforced by the layer that writes, not by each caller; exceptions are listed in one place with a reason (for example a              | A caller cannot forget it                          |
|   `WRITE_GATES` table a checker reads)                                                                                                          |                                                    |
| A guard reads its refusal from the system of record, never from a command-line flag                                                             | A flag can be passed by mistake; the record holds  |
|                                                                                                                                                 |   the decision                                     |
| Machine writes go through a named writer identity with least privilege; an administrator credential is refused for routine writes               | The audit trail names who changed what             |
| One writer per record or field: where a controller or another tool owns a value, write through it or not at all                                 | Two writers fight and the last silently wins       |
| Writes are idempotent: running the same apply twice changes nothing the second time, and reports "no change"                                    | A retry or a rerun after a crash is safe           |
| Record a change only after the target confirms it                                                                                               | The record never claims a change that did          |
|                                                                                                                                                 |   not happen                                       |
| Fail closed: on ambiguity, missing data or an unexpected answer, refuse and say why                                                             | A guess that writes is worse than a stop           |
| Login and retry budgets are enforced centrally (one budget per target per process); never try another password on an unreachable target         | Repeated logins trip lockouts                      |
| Credentials come from the secret store at run time, never from code, arguments that appear in process lists, or logs ([security.md](security.md)) | Code and logs are copied widely                    |
| Back up before a deploy or a bulk write, and gate the next step on the backup's exit code                                                       | The backup is the rollback                         |

> **Learned 2026-10-27** · python, `scripts/write_gates.py` · VERIFIED_PRIMARY (run on skill-goal-guard: "0 writer(s)" although four write paths exist) · Source: skill-goal-guard `code-map.toml` `[write_gates]` note; `scripts/goal_guard_lib/decisions_log.py` `append` · Falsifier: write_gates.py reporting a writer for a front end whose write lives in an imported module
> `write_gates.py` reads entry points only, so a program whose writes live in a library module (the front end passes `apply` down) reports no writer at all: a clean result is not proof. Keep the
> gate in the writing function (`append(..., apply)` refuses to write without it), test that a plan writes nothing, and name every library write path in the code map's `[write_gates]` section.

> **Learned 2026-10-27** · python, `scripts/write_gates.py` · VERIFIED_PRIMARY (skill-ai-it: "0 writer(s)" by default, 23 with local-write patterns) · Source: skill-ai-it `scripts/write-gates.json` · Falsifier: the default patterns reporting a script whose only writes are local `write_text` calls
> The default patterns count live-system writes only (HTTP, SQL, recursive delete), by design. A tool whose job is rewriting other projects' files
> needs `write_patterns` for local writes, and then reports what it should: on skill-ai-it 23 writers, of which eight are gated by their own flag
> (`--write`, `--write-baseline`, `--report-json`) and registered with that reason, and two write on a bare run with only `--dry-run` to stop them.
>
> ```json
> "write_patterns": ["\\.write_text\\(", "open\\([^)]*[\"']w", "\"mv\","],
> "exceptions": {"scripts/plans/target_map.py": "validates by default; writes the tracker and embeds only with --write"}
> ```

## The write chain

```text
+-----------+    +------------+    +-----------+    +-------------+    +------------+
| plan      |--->| approval   |--->| apply     |--->| target step |--->| record     |
| read only:|    | operator   |    | --apply,  |    | confirmed   |    | after      |
| diff and  |    | or policy  |    | writer    |    | (verify     |    | success    |
| risks     |    |            |    | identity  |    | read-back)  |    | only       |
+-----------+    +------------+    +-----------+    +-------------+    +------------+
   any refusal or failed verify stops the chain; nothing is recorded
```

The plan is the same code path as the apply with writes turned off, so the dry run proves what the apply will do. Why: a separate "preview" function drifts from the real one.

## Deleting

- Never delete a feature, schema element or configuration section without confirmation; a script reports such candidates and stops.
- Stale or duplicate data records may be deleted by a gated script; name which and why in the change log.
- Prefer recoverable operations: deactivate before delete, move to an archive before removing, keep a backup.

Why: deletions are the least reversible change (operator rule in a governed project; global policy "never delete without explicit authorisation").

## Canary before batch

A change that touches many targets (devices, sites, projects, customers) goes one unit end to end first, to the outcome the operator can see, then a small canary of the same kind (the operator's
default is one plus five, spread across sites), then stops and hands the batch command to the operator. Report success at the outcome layer (stored, visible, healthy), never at the transport layer
(HTTP 200, "accepted"). Why: in 2026-09 a batch reported success on HTTP 200 while 22 of 26 units had never stored data (operator lesson `feedback_depth_before_breadth`); the same rule covers tooling
rolled out across projects.

## Changing an identifier

Before renaming or retargeting any identifier (a function, flag, tag, variable, config key, file path), search every file type that can reference it, including templates, shell scripts, configuration,
CI jobs and runbooks; classify each hit (declaration, use, unrelated namesake); check external callers; and verify with a dry run of behaviour, not only a syntax check. Why: some tools ignore an
unmatched name silently, so the old command still exits 0 and does nothing (operator lesson `feedback_trace_all_references_before_ansible_change`, where a templating file was the missed reference).

> **Learned 2026-10-26** · interrupted transactions · VERIFIED_PRIMARY · Source: local-knowledge-ansible base `aacf57c` plus uncommitted `roles/smc_change/tasks/{record,cleanup,journal}.yml`; controller integration red/green fixtures · Falsifier: a failed cleanup that still
> produces a completed marker, or a repeated partial cleanup that drops an original backup-manifest entry.
> Completion includes verification and cleanup. Persist the original baseline, backup manifest and cleanup ownership before mutation;
> retries preserve those records and get a separate attempt id. Rebuilding a manifest from the files remaining after partial deletion loses rollback material.
>
> ```yaml
> # tasks/record.yml, same source (generic; no customer identifiers)
> when:
>   - smc_change_record.result == 'passed'
>   - smc_change_cleanup_complete | default(false) | bool
> ```

> **Learned 2026-10-26** · process matching from automation kills or waits on itself · VERIFIED_PRIMARY (ansible-wifi smc_change: session dropped twice at a `pkill -f`; an AVR check waited 60 s on itself every probe) · Source: local-knowledge-ansible `roles/smc_change/tasks/restart.yml` (commit 0918fc0 era, 2026-10-26) · Falsifier: a `pgrep -f` in an
> Ansible shell task that never matches its own shell although the pattern is in `environment:` or in the script text
> `pgrep -f`/`pkill -f` match whole command lines. Ansible's `environment:` values land on the remote command line, and a shell script's
> own text is its shell's command line, so a pattern placed in either matches the task itself: pkill then kills the task's session, a wait
> loop waits for itself. Pass the pattern encoded (`| b64encode`, decode inside) and spell a command the script also runs through a variable
> (`a=artisan; php "$a" ...`); the `[a]rtisan` bracket trick fails when the plain command appears anywhere else in the same script.

> **Learned 2026-10-28** · process matching: anchor the pattern, and check it · VERIFIED_PRIMARY (warehouse-rct01: decoy shell carrying the text matched 2 with `pgrep -fc '[a]rtisan update:stats'`, 0 with `'^php [a]rtisan update:stats'`, 1 with a real run) · Source: local-knowledge-ansible `roles/smc_change/files/changes/rct-tstik-iridium-update/rct-tstik-iridium-update.yml` and `files/tests/test_spec_pgrep.py` (uncommitted at writing) · Falsifier: an unanchored `pgrep -f` wait in an Ansible probe or command action that never runs to its timeout
> The 2026-10-26 advice (bracket trick, spelling through `$a`) recurred three more times in two days: the pattern text also arrives from
> places the script author does not see, here the probe's `PROBE_CONFIG` holding the spec's restart pattern on its own shell line (each
> wait ran its full 60 s: self test 79 s, AVR check 66 s per probe), and a comment inside a command action's script. Anchor every
> `pgrep -f`/`pkill -f` pattern at the real program's command line with `^`: a shell line starts with `/bin/sh` and cannot match.
> Then make it a check, not a memory: `scripts/process_match.py` reports unanchored literal patterns in shell, YAML, Python and Jinja.

```bash
# wrong: matches any command line holding the text (the probe's shell, the task's own sh -c, a cron job's shell)
for i in $(seq 1 60); do pgrep -f '[a]rtisan update:stats' >/dev/null || break; sleep 1; done
# right: only the program itself starts with "php artisan"
for i in $(seq 1 60); do pgrep -f '^php [a]rtisan update:stats' >/dev/null || break; sleep 1; done
```


> **Learned 2026-10-28** · freeing a lock another process holds · VERIFIED_PRIMARY (Ubuntu 22.04 container, real fcntl locks: 16 of 16 cases; fleet: node_exporter `apt_info.py` held apt's lists lock 14 h to 290 days on 8 SMCs) · Source: local-knowledge-ansible `plans/apt-lock-guard-20261028_2055/apt_lock_guard.py` (uncommitted at writing) · Falsifier: a lock freed by deleting its file, or a holder
> killed by age alone, in a helper that also runs installs
> Every version of an apt helper on 11 branches freed locks the same two ways, both wrong. Deleting a lock file frees nothing: fcntl/flock
> locks belong to the open file and die with their holder, and a new file lets a second writer in beside the first. Killing any holder past an
> age kills a long, legitimate writer mid-write (a kernel install, dpkg configuring). Decide by what the holder is doing, which the set of
> locks it holds tells you: a reader or a refresh whose output is swapped in atomically (rename) can be ended; a writer of shared state is
> waited for and then reported by name, never killed. Find the owner by the lock file's device and inode in `/proc/locks`, not the inode
> alone (it matched an unrelated lock on another device) and not by process name.

```python
# right: classify by the locks held, end only what is safe to end
def classify(cmdline, held):
    if held <= {LISTS}:                      # only the refresh lock: its output is renamed into place
        return "apt_info" if cmdline.startswith(APT_INFO) else "refresh"
    return "install"                         # dpkg or archives lock: wait, then report; never kill
```

> **Learned 2026-10-28** · a symlinked source ships whatever is checked out · VERIFIED_PRIMARY (ansible-wifi smc_change apt-info-no-update: the copy source linked to `roles/smc_node_exporter/files/apt_info.py`, fixed on master only, old on rise) · Source: local-knowledge-ansible `roles/smc_change/files/changes/apt-info-no-update/` (uncommitted at writing) · Falsifier: a deploy that links into a branch-switched checkout
> and still ships one fixed version
> A symlink to a file inside a git checkout resolves at run time to whatever branch, stash or `git restore` left there, so a deployment that
> needs a specific version must carry a pinned copy (from the commit: `git show <commit>:<path> > file`). A link is right only when the
> target cannot vary by branch (a repo without branches, or a file the same on every branch), and then it keeps one tested copy for every user.

> **Learned 2026-10-29** · shared fixed scratch paths · VERIFIED_PRIMARY (source read 2026-10-29) · Source: project_stuff/me vehicle-import track `scripts/tmp_workbook.py` (`scratch_workbook`, commit 9892f82) · Falsifier: two overlapping runs that share one
> fixed scratch path and never read each other's input
> Scripts that call each other and write a scratch file at one fixed path fail silently, not with a crash: overlapping runs read each
> other's inputs and produce a well-formed answer for the wrong item. Give each run its own scratch file, remove it even on an exception,
> and add a static check that fails on any hard-coded scratch path so the old pattern cannot return.
>
> ```python
> @contextlib.contextmanager
> def scratch_workbook(prefix, directory=SCRATCH_DIR):   # tmp_workbook.py
>     os.makedirs(directory, exist_ok=True)
>     fd, path = tempfile.mkstemp(prefix=f"{prefix}-", suffix=".xlsx", dir=directory)
>     os.close(fd)
>     try:
>         yield path
>     finally:
>         with contextlib.suppress(OSError):
>             os.remove(path)
> ```

> **Learned 2026-10-29 (b)** · fetch caches · VERIFIED_SECONDARY (harvest 2026-10-29 of a personal research project) · Source: project_stuff/me vehicle-import track `scripts/README.md` (prestige_auction_search row) · Falsifier: a full run, without the narrowing
> flag, that leaves pruned cache entries pruned
> Deleting entries from a fetch cache does not express a filter: to the next run without the narrowing flag an absent id reads as
> "not fetched yet", so it fetches them again and silently undoes the pruning. Record exclusions explicitly (an exclusion list the fetcher
> reads), and keep the cache a cache.
