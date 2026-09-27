# Templates — skill-staleness-audit

Working files for an audit. `just audit-templates` copies them into the project's `.staleness-audit/` (this readme excepted). There they are filled in, and `scripts/audit_report.py` embeds every
filled one in the report before the gate deletes the scratch. A copy left untouched is not embedded.

| Template | Phase | Use |
|---|---|---|
| [defect-register.md](defect-register.md) | 1 | One row per finding, ranked M → H → G, each citing evidence |
| [supersession-banner.md](supersession-banner.md) | 3 | Banner boilerplate for superseded sections |
| [residual-risk-register.md](residual-risk-register.md) | 6 | What the audit did not resolve, including its own errors |
| [audit-report.md](audit-report.md) | 7 | The report's narrative skeleton; `audit_report.py` starts the report from it, and the gate refuses to pass while a placeholder is left |
