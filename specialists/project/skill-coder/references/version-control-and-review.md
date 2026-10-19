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
