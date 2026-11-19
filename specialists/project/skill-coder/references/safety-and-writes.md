---
Title: Safety and writes
Category: reference
Status: current
Authority: local-supplement
Scope: Code that changes anything outside its own process - files, databases, devices, remote systems
Last reviewed: 2026-11-19
Summary: >-
  Read by default, plan then --apply, write gates the code enforces, credentials never in code, one writer per record,
  idempotent writes, record only after the target confirms, fail closed, and canary before batch; Learned entries on process
  matching, freeing locks, scratch files, crash-safe writes, verified rollback, formatter hooks and shared-tool defaults.
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

> **Learned 2026-11-19** · shell, macOS, root-run device write · VERIFIED_PRIMARY (accepted the registered card; refused a 988 GB and a 2 TB data
> disk, the internal disk, an image outside the image store, a `/dev/` path, an unknown option and a write without root; three refusals kept as negative
> tests, one proved by a mutant) · Source: smc-resiliency lab/payloads/lab_flash_guarded.sh (commit 42af8ebd), promoted from the entry parked there on
> 2026-11-19 · Falsifier: a write that reaches a disk the guard should refuse.
> A destructive device write re-reads the target's identity at execution, not at plan time (whole physical disk, not internal, removable or external,
> USB or SD, a size ceiling, an exact size from an allowlist, a denylist of known disks), and reads back exactly the image's length (a whole-block count
> rounds down and never matches). When an agent is to run it as root through a one-path NOPASSWD sudoers line, the allowlist lives **inside the installed
> root-owned copy**, never in a file the agent can edit, and the script calls only system binaries by absolute path with a fixed PATH: a tool under
> `/opt/homebrew` is user-writable, so root running it is an escalation. The editable source is installed by the operator; adding a medium is an
> edit and a re-install.
>
> ```bash
> # smc-resiliency lab/payloads/lab_flash_guarded.sh (commit 42af8ebd)
> PATH=/usr/bin:/bin:/usr/sbin:/sbin
> ALLOWED_SIZES=(31914983424 31266439168) # the registered lab cards
> [ "$(key "$DISK" Internal)" = false ] || refuse "$DISK is internal"
> size=$(key "$DISK" TotalSize)
> for d in "${DENY_SIZES[@]}"; do [ "$size" != "$d" ] || refuse "$DISK has the size of a denied disk ($d bytes)"; done
> blocks=$(((IMG_BYTES + BS - 1) / BS))
> got=$(dd if="/dev/r$DISK" bs=$BS count=$blocks 2>/dev/null | head -c "$IMG_BYTES" | shasum -a 256 | cut -d' ' -f1)
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
A rollback is a write too: it reports "restored" only after reading the prestate back (Learned 2026-11-08, transaction recovery, below).

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

> **Learned 2026-11-08** · core (crash-safe writes on FAT) · VERIFIED_PRIMARY · Source: smc-resiliency `docs/overview/smc-lab-test-record-20261107_1931.md` section 15, `spike/release/rauc/tryboot_backend.sh` `write`, commit 065b9a8f · Falsifier: a vfat file rewritten in a loop by write, fsync, rename that is never found empty after a power cut
> Write to a temporary file, fsync it, rename it over the old one and fsync the folder is crash-safe on ext4 and xfs, not on FAT (vfat, the
> EFI system partition, a Pi's boot partition): FAT has no atomic rename. A power cut while a selection file was rewritten in a loop left it at 0
> bytes: the directory entry reached the disk, the data did not. A file a firmware must read on a FAT partition needs another plan (a fixed-length
> overwrite in place, two copies the reader can choose between, or a repair at boot), and the cut itself is the test:
>
> ```sh
> printf '[all]\n...# smc-boot: committed=%s ...\n' ... >"$tmp"
> sync "$tmp" 2>/dev/null || sync
> mv "$tmp" "$SELECTION"     # on vfat this is not atomic
> sync "$(dirname "$SELECTION")" 2>/dev/null || sync
> ```

> **Learned 2026-11-08** · core (transaction recovery) · VERIFIED_PRIMARY · Source: unified-network-controller audit follow-up `docs/reports/project-reviews/unc-technical-audit-followup-20261108_1255.md` (offline fake-target probes), code at e873366b, `wc-local/scripts/safe_write/rollback.py:150-174` · Falsifier: a no-op
> revert cannot return a restored outcome.
> A rollback result must verify the state it claims to restore. "The target answers" proves reachability only: a no-op revert, a partial restore
> or an ignored compensating write all leave a reachable target with the new value. Read the managed prestate back after every rollback class; a
> mismatch, a timeout or an exception during verification is failed or unknown, and an unknown keeps a manual recovery obligation.
>
> ```python
> # Anti-pattern, sanitized excerpt (rollback.py at e873366b): success is reachability, not restored state.
> revert()
> if not adapter.reachable():
>     return RollbackOutcome("rollback_failed", "unreachable")
> return RollbackOutcome("rolled_back", "reachable")
> ```

> **Disputed 2026-11-18** · any language, files rewritten by a post-edit formatter hook · VERIFIED_PRIMARY (on a copy of the committed file, un-wrapping the original and the hook's output gives
> identical tables, 383 rows and none differing, the prose is identical word for word, and the hook's output is unchanged when run twice) · Source: unified-network-controller CHANGELOG
> 20261118_2103, written by the same session as the entry below · Falsifier: an un-wrapped comparison that differs · Conflicts: the Learned 2026-11-18 entry below (formatter hook)
>
> The entry below calls the rewrite damage ("bold spans split across table cells"). It was not: the hook closes and reopens bold on each wrapped line of one cell, and the re-wrap was lossless. The
> true finding is that the committed file was not in the formatter's normal form, so one edit re-wrapped all of it. A token comparison cannot tell a re-wrap of a table from damage, because a table
> wraps column by column and the token order changes; compare the tables un-wrapped, row by row and cell by cell, and the prose word by word. What stands from the entry below: compare the diff's
> size with the edit's, and do not accept or condemn a whole-file reflow before proving which it is. What does not stand: "restore and apply outside the hook" as the default, since that keeps the
> file out of normal form and repeats the surprise at the next edit; a reflow proven lossless is committable.
>
> The comparison is `scripts/reflow_lossless.py` (`just reflow-lossless --git FILE --table-reflow <cli.mjs> --ignore-contents`): exit 0 lossless, 1 with the differing words and rows, 2 when
> tables are present and cannot be proven. On the file of 2026-11-18 it reports lossless for the table step and for the whole hook, and catches a one-word tamper.

> **Learned 2026-11-18** · any language, files rewritten by a post-edit formatter hook · VERIFIED_PRIMARY (one edit of three strings in a 1,400-line governed markdown file came back as 315
> lines added and 304 removed; a whitespace-insensitive token comparison with HEAD found 52 changed blocks, among them bold spans split across table cells) · Source: unified-network-controller
> CHANGELOG 20261118_1947, commit b54b707e · Falsifier: a formatter that is idempotent on the committed file, so an edit's diff is the edit.
>
> After a tool-mediated edit of a governed file, compare `git diff --numstat` with the size of the edit made. When it is larger, compare tokens, not lines, to tell a re-wrap from damage; restore
> the file from version control and apply the edit by exact replacement with a match-count guard (abort unless exactly one match), outside the hook. Never bless a whole-file reflow as "formatting".
>
> ```python
> # token comparison against HEAD: every non-equal block is printed
> old = subprocess.run(["git", "show", "HEAD:./" + path], capture_output=True, text=True).stdout
> toks = lambda s: re.sub(r"-{3,}", "---", s).split()
> for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, toks(old), toks(new), autojunk=False).get_opcodes():
>     if tag != "equal":
>         print(tag, toks(old)[i1:i2], toks(new)[j1:j2])
> ```

> **Learned 2026-11-16** · any language, shared CLIs called by hooks · VERIFIED_PRIMARY (the markdown hook `governance/hooks/markdown-wrap-toc.sh` runs
> `table-reflow/cli.mjs FILE --width 200 --measure-rendered --in-place` on every markdown write; a new path rule made default-on was live for about eight minutes
> before a side note caught it; ten files were written in that window, none changed) · Source: scripts_stuff `vscode_extensions/shared/table-reflow/cli.mjs`
> `--link-paths` (uncommitted, 2026-11-16) · Falsifier: a tool whose callers are all interactive, where a default change reaches only the person who asked.

- Before changing a default in a shared tool, find its non-interactive callers (hooks, generators, other skills' scripts: `grep -rl <tool path>` over hook folders and
  skill scripts). A default change there is a write to every file those callers touch. Ship the new behaviour behind an opt-in flag, prove it with a
  before/after run over real files with the flag off (expect zero changes) and on, and let the operator decide whether the hooks pass the flag.
- To find what a live window already touched, use a file saved just before the change as the mtime marker: `find <roots> -name '*.md' -newer <marker>`.

> **Learned 2026-11-19** · output files named by a timestamp · VERIFIED_PRIMARY (two packs lost CHANGELOG entries; restored from git) · Source: skill-ai-it `scripts/records/rotate_records.py` `free_archive_name` and test `test_a_second_rotation_in_the_same_minute_keeps_the_first_archive` · Falsifier: two writes in the same stamp period that both survive without an existence check
> A name stamped to the minute (`changelog-20261119_1628.md`) is not unique: two rotations in one minute wrote the same archive, the second overwrote the first, and the entries
> the first had moved out of the live file were gone from both. Before writing a stamped file, check it does not exist and add a suffix (`-2`, `-3`) when it does; update any
> pattern that recognises the stamped names (`-\d{8}_\d{4}(?:-\d+)?\.md$`). Prove it with a test that pre-creates the names, not with two quick runs that may straddle a minute.
>
> ```python
> # skill-ai-it scripts/records/rotate_records.py (2026-11-19)
> def free_archive_name(root: pathlib.Path, base: str) -> str:
>   rel, n = f"{base}.md", 2
>   while (root / rel).exists():
>     rel, n = f"{base}-{n}.md", n + 1
>   return rel
> ```
