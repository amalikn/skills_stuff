# Recording demo

`history.jsonl` contains an initial synthetic `fail` followed by a synthetic `pass` that supersedes it. `report.md` shows only the latest observation while retaining a count of both history records.

`invalidation-history.jsonl` contains a synthetic pass followed by a declared `config_change` invalidation. `invalidation-report.md` computes `stale`; it does not record that value.
