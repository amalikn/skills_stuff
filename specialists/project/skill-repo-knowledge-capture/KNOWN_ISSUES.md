# KNOWN_ISSUES

- The workflow assumes `git` is installed and available in `PATH`.
- `history-commit` records the latest snapshot only; it does not deduplicate old snapshots.
- Large cache databases may increase local storage usage quickly.
- `exclude_file` assumes `<repo>/.git` is a directory; pointed at a linked worktree path, `setup` cannot write the exclude entries (pass the main
  checkout, as the pre-push hook does). Not fixed.
- A snapshot taken by the faulty run of 2026-09-30 (ansible-wifi `20260930_1954`) has no history commit; the next push's capture commits the
  then-latest snapshot only.
