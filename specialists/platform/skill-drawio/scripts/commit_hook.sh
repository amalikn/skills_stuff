#!/usr/bin/env bash
# A git pre-commit hook body for a project with a flow map: when a commit touches the watched folder, run the project's check and stop the commit on
# a failure, so code cannot land with its flow steps unreviewed. Read-only. Bypass one commit with `git commit --no-verify`.
#
# usage: commit_hook.sh <watched path, relative to the repository root> <check command...>
#   a person installs it as .git/hooks/pre-commit, with one line after the shebang:
#     exec /path/to/commit_hook.sh roles/x just -f /path/to/justfile x_flows_check
# Exit: 0 nothing watched was staged, or the check passed; the check's exit code otherwise; 2 bad usage.
# Runtime: about a second for 200 steps, plus the check's own render (measured 2026-11-02).
set -u

# Run the check when a staged path sits under the watched folder.
#
# Args: $1 the watched path; the rest, the check command.
# Returns: 0, the check's exit code, or 2 on bad usage.
main() {
  if [ "$#" -lt 2 ]; then
    echo "usage: commit_hook.sh <watched path> <check command...>" >&2
    return 2
  fi
  local watched="$1"
  shift
  if ! git diff --cached --name-only | grep -q "^${watched}"; then
    return 0
  fi
  "$@" || {
    local rc=$?
    echo "commit_hook: the flows and the code disagree (rc ${rc}); review the steps, then accept or fix them" >&2
    return "$rc"
  }
}

main "$@"
