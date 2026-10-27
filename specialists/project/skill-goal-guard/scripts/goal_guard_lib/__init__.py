"""Goal Guard library: the pilot implementation behind the scripts/goal_guard*.py front ends.

Imported, not run. Modules, by layer (core first; a module imports only those above it):

  errors, settings          program error types and run-time settings (environment only)
  yaml_io                   the PyYAML seam
  records, mvp              frozen dataclasses for task, proposal and verdict records, and the MVP contract
  project                   load a project's .gg/ records and resolve its partition
  decisions_log             the append-only, hash-chained decisions.jsonl
  vikunja, tasks            the Vikunja HTTP seam, and task sources (live or file) normalised to records
  decide, rank              the decision rules and the What's Next pipeline (pure policy)
  trace, snapshot, restore  milestone trace, snapshot and verify, clean-instance restore
  excel                     the management workbook sample (openpyxl seam)
  cli                       shared front-end plumbing (task source, JSON output, exit codes)
  doctor, hook              enforcement report and the Claude Code PreToolUse adapter (draft)

Consumers: scripts/goal_guard.py, goal_guard_vikunja.py, goal_guard_trace.py, goal_guard_snapshot.py, goal_guard_excel.py,
goal_guard_doctor.py, goal_guard_hook.py, and tests/. Rules implemented: references/decision-rules.md and the references each module names.
"""
