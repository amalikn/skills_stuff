---
Title: Version control and review
Category: reference
Status: current
Authority: local-supplement
Scope: Commits, change logs, versions, review and the definition of done for any code change
Last reviewed: 2026-10-19
Summary: >-
  Small commits gated on the check's own exit code (never through a pipe or a semicolon), a change-log entry per change,
  SemVer for released interfaces, a review checklist, and a definition of done that includes measured runtime.
---

# Version control and review

## Contents

- [Commits](#commits)
- [Gate on the exit code](#gate-on-the-exit-code)
- [Change logs and versions](#change-logs-and-versions)
- [Review checklist](#review-checklist)
- [Definition of done](#definition-of-done)

## Commits

- One logical change per commit; a refactor and a behaviour change are separate commits. Why: each can be reviewed and reverted alone.
- Commit or push only when the user asks; "commit and push" covers only the repo being worked in (operator lesson `feedback_commit_push_scope`).
- Preserve unrelated work in a dirty tree: stage only the files the change owns. Why: someone else's half-done work is not yours to commit.
- Follow the project's message convention. Where none exists, Conventional Commits (`feat:`, `fix:`, a `BREAKING CHANGE:` footer) is a reasonable default (VERIFIED_PRIMARY, v1.0.0). Use the
  attribution the project's or user's rules require.
- Avoid apostrophes in a heredoc commit body passed through a shell tool; write around contractions. Why: they break shell parsing (operator lesson).

> **Learned 2026-10-20** · git, a repo shared by concurrent sessions · VERIFIED_PRIMARY · Source: apn commits b64a075 and 951a7dc
> (smc-resiliency CHANGELOG 20261020 slurp entry) · Falsifier: two sessions where one's `git add` never ends up in the other's commit
> The index is shared by every session working in one clone. `git add <paths> && git commit` lets another session's commit, made in the same
> second, take what this session staged: here a unified-network-controller commit carried smc-resiliency's files under its own message, and this
> session's commit then found nothing to commit. Commit by pathspec, which commits exactly the named paths whatever else is staged, and check
> the result with `git show --stat HEAD` before pushing. A new file needs `git add -N` (intent to add) first so the pathspec can name it.
> Never amend or split the other session's commit; record where the work landed.
>
> ```bash
> # smc-resiliency, 2026-10-20 (after the race)
> just check >/dev/null 2>&1; rc=$?
> [ $rc -eq 0 ] && git add -N smc-resiliency/docs/history \
>   && git commit -q -m "..." -- smc-resiliency/CHANGELOG.md smc-resiliency/docs/history \
>   && git show --stat --format="%h %s" HEAD
> ```

> **Learned 2026-10-21** · git, one repo shared by several projects and sessions · VERIFIED_PRIMARY · Source: apn `scripts/project_commit.py` and
> `scripts/project_sync_selftest.sh` (uncommitted at writing; apn CHANGELOGs 20261021_1338) · Falsifier: a self-test run where the commit carries a
> second project's changed file, or a failed check still moves HEAD
> Make the pathspec rule a tool when several projects share one clone: one recipe per project that runs the project's check, takes an exclusive
> lock shared by all of them (flock on a file outside the repo), stages only its folder (`git add -A -- <folder>`, so new and deleted files are
> covered without `-N`), commits with the folder as pathspec (git's `--only` mode leaves anything another session staged elsewhere staged and out
> of the commit), then pushes. On a rejected push, rebase onto the upstream only when the whole tree is clean; another session's dirty files mean
> stop and report, never `--autostash` over them. The self-test proves isolation against a throwaway bare remote.
>
> ```python
> # apn scripts/project_commit.py (2026-10-21)
> with git_locked(args.wait):
>     if git("add", "-A", "--", project).returncode: ...
>     r = git("commit", "--quiet", "-m", args.message, "--", project, timeout=CHECK_TIMEOUT)  # pre-commit hooks run here
>     ok, note = push(shlex.split(args.push_cmd), project)   # retry after rebase only when `git status --porcelain` is empty
> ```

> **Learned 2026-10-20** · git rebase onto a diverged remote · VERIFIED_PRIMARY · Source: vagrant_stuff commits 08c81b3 and 62f03f1 (smc-resiliency
> CHANGELOG 20261020 push entry) · Falsifier: a `rebase -X theirs` whose result equals the local branch file for file when the remote changed other hunks
> In a rebase, `-X theirs` means the commits being replayed (the local side) win **conflicting** hunks only; a remote hunk the local side never
> touched still applies without a word. Here a three-year-old remote line pointed a synced folder at a path that does not exist, and it landed
> in a file the operator had asked to keep local. Before the rebase, branch the local head as a backup; after it, diff every file both sides
> changed against that backup and restore any line the operator did not choose. `--autostash` re-applies uncommitted edits onto the new base,
> so check the working copy too. On a real conflict, `git rebase --abort` and ask which side wins; never pick it.
> Compare the **whole repo**, not the files you suspect: the autostash commit (`git rebase` prints its hash) is the exact pre-rebase working
> tree, so `git diff --name-status <autostash> HEAD | awk '$1!="A"'` lists every existing file the remote changed. The first check here looked at
> one file and missed four (a box image switched, guest-tool settings commented out); a side agent caught it (vagrant_stuff 7adb82c).
>
> ```bash
> git branch backup/pre-rebase-$(date +%Y%m%d_%H%M) HEAD
> git rebase -X theirs --autostash @{u} || git rebase --abort
> git diff backup/pre-rebase-<stamp> HEAD -- <files both sides changed>
> ```

> **Learned 2026-10-26** · git, two sessions editing the same files · VERIFIED_PRIMARY · Source: skills_stuff 661075a and cf059eb (smc-resiliency
> CHANGELOG 20261026_1440) · Falsifier: a blob staged this way whose commit differs from HEAD plus only the intended hunks
> When another live session has unrelated hunks in the same files (here e2e.py, visual-style.md, CHANGELOG.md), `git add -p` is interactive and
> unavailable to an agent, and a stash takes the other session's work with it. Build the content you mean to commit (HEAD plus your own edits) in a
> scratch file, write it as a blob and point the index at it; the working tree, with both sessions' edits, is left alone. Then apply
> `git diff --cached --binary` to a scratch worktree at HEAD and run the tests and check there, so the commit is proved on its own, not on the
> mixed working tree (the shared tree's half-written edits failed the tests mid-session). Agree the split by file and hunk with the other session
> first, and let it commit on top.
>
> ```bash
> git show HEAD:path/file.py > /scratch/file.mine.py && <apply only your edits to it>
> git update-index --cacheinfo 100644,"$(git hash-object -w /scratch/file.mine.py)",path/file.py
> git diff --cached --binary | git -C /scratch/wt apply --index && (cd /scratch/wt && just test && just check)
> ```

## Gate on the exit code

Gate a commit, push or deploy on the validation command's own exit code, never through a pipe or a `;`:

```bash
just check > /path/to/check.log 2>&1; rc=$?
tail -1 /path/to/check.log
if [ "$rc" -eq 0 ]; then git commit -m "..."; fi
```

Why: in `check | tail -1 && git commit`, the pipeline's status is `tail`'s, so a failing check commits; `;` ignores the status entirely. This recurred four times in one workspace, once deploying after
a failed backup (operator lesson `feedback_gate_on_check_exit_code`). `set -o pipefail` also works in Bash: it makes a pipeline's status that of the last command to fail (VERIFIED_PRIMARY, Bash
manual).

> **Learned 2026-10-27** · git 2.40+ · VERIFIED_PRIMARY · Source: skill-smc `scripts/ansible/ansible_change_reach.py` `cherry_pick_state`, offline test
> `test_ansible_change_reach.py` (clean and conflict cases) · Falsifier: a `merge-tree` exit 0 for a commit whose `git cherry-pick` conflicts
> "Is this fix on the deploy branch, and would it apply?" is answered without a checkout: `git merge-base --is-ancestor <c> <branch>` for reach, and
> `git merge-tree --write-tree --merge-base <c>^ <branch> <c>` simulates the cherry-pick in the object store (exit 0 clean, 1 conflict, other =
> unknown, e.g. git older than 2.40). A list of branches holding a commit is read whole: a `| head -3` on `git branch --contains` once hid the
> pushed remotes and a report said "not pushed".
>
> ```python
> code, _out, err = run(["git", "merge-tree", "--write-tree", "--merge-base", f"{commit}^", base, commit], repo)
> if code == 0:
>   return "clean"
> if code == 1:
>   return "conflict"
> return f"unknown: {err.strip().splitlines()[0] if err.strip() else f'exit {code}'}"
> ```

## Change logs and versions

- Every change that alters governance, navigation, behaviour or a repeated job's runtime gets a change-log entry; a repeated job's entry carries its measured runtime. Why: the log is the project's
  durable history.
- Keep an `Unreleased` section and group entries as Added, Changed, Deprecated, Removed, Fixed, Security (Keep a Changelog 1.1.0, VERIFIED_PRIMARY), unless the project uses another format.
- Released interfaces (a library, an API, a CLI others script against) follow SemVer 2.0.0: MAJOR for incompatible changes, MINOR for compatible additions, PATCH for compatible fixes; a released
  version is never modified (VERIFIED_PRIMARY). A versioned API may add a field; renaming or removing one is a new version.

## Review checklist

| Question                                                                        | Reference                     |
| ------------------------------------------------------------------------------- | ----------------------------- |
| Is the code in the right layer, with dependencies pointing inward and no cycle? | [design-principles.md](design-principles.md) |
| Did it reuse what exists (project, platform, stdlib) before building?           | [design-principles.md](design-principles.md) |
| Are modules and functions within budget, or held by the ratchet?                | [module-and-function-shape.md](module-and-function-shape.md) |
| Does every file have a header and every function its Args, Returns, Raises?     | [documentation-and-headers.md](documentation-and-headers.md) |
| Do writes need `--apply`, go through one writer and fail closed?                | [safety-and-writes.md](safety-and-writes.md) |
| Does every external call have a timeout, and is every error typed and surfaced? | [errors-and-timeouts.md](errors-and-timeouts.md) |
| Are there literals (paths, hosts, tokens) that belong in settings?              | [configuration-and-literals.md](configuration-and-literals.md) |
| Is there a test at the right level, and a negative test for any new check?      | [testing.md](testing.md)      |
| Is a refactor proven behaviour-preserving?                                      | [refactoring-and-promotion.md](refactoring-and-promotion.md) |
| Is runtime stated and measured where the code repeats?                          | [efficiency-and-measurement.md](efficiency-and-measurement.md) |
| Any new dependency named with its seam, range and upgrade test?                 | [dependencies.md](dependencies.md) |
| Any input reaching a query, command or path unparameterised?                    | [security.md](security.md)    |

## Definition of done

- [ ] Layer and location right; no new raw I/O outside a seam, no literals, no missing timeouts.
- [ ] Tests at the right level pass; the project's closing check passes, gated on its exit code.
- [ ] Dry run or characterisation compared where behaviour must not change.
- [ ] Change-log entry, with measured runtime where the code repeats.
- [ ] Script catalog, promotion register and any registers the project keeps are updated.
- [ ] Work touching many targets was canaried, and the batch handed to the operator.
- [ ] File headers present; modules and functions within size.
- [ ] Reusable learning written back to the owning skill ([evolution-and-write-back.md](evolution-and-write-back.md)).

Adapted from a governed project's definition of done (unified-network-controller, design section 15).
