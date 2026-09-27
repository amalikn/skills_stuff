# Scripts — skill-project-coherence

| Script | Step | Purpose | Safety | Idempotent |
|---|---|---|---|---|
| `stale_refs.py` | 4 | Sweep for old values in the project and each `--also` root (sibling skills, sibling repos). Every hit is classed `active`, `history-path`, `history-dated` or `generated`; exit 1 while any `active` hit remains | `safe`, read-only | yes |
| `tests/test_stale_refs.py` | — | Fixture tests: `python3 -m unittest discover -s scripts/tests` | `safe` (temp dirs only) | yes |

Python 3.9+ stdlib only. The dated-section rule matches skill-staleness-audit's `claim_scan.py`, so both skills agree on what counts as history.
