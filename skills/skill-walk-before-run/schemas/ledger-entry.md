---
Title: skill-walk-before-run — ledger entry schema
Status: current
Last reviewed: 2026-09-16
Summary: Field definitions and examples for ledger.jsonl entries. Reference only, not loaded at runtime — SKILL.md's inline JSON templates are sufficient to act on.
---

# Ledger entry schema

One JSON object per line, appended to `ledger.jsonl` (colocated with `SKILL.md`), on RED, waiver, and RED-to-resolved only — never on GREEN or AMBER. This file documents the fields; `SKILL.md` carries
the inline templates needed to act and remains the runtime source of truth.

Same schema, same lines, mirrored verbatim to `.wbr-ledger.jsonl` in the target project's own root — a recovery copy, read only if `ledger.jsonl` above is ever lost. Not a second source of truth.

## Why JSONL

The ledger is append-only, single-writer, and read both by a human (during RED/waiver review) and — once the parked SessionStart hook lands — by a script that tails the last few lines and filters on
`verdict`. JSONL gives O(1) append with no reparse of prior entries, and a malformed line stays isolated instead of risking the whole file, which a single multi-line text block or a TOML
array-of-tables doesn't guarantee to the same degree.

## Fields

| Field        | Type                   | Entries  | Meaning                                                                                                                                           |
| ------------ | ---------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ts`         | ISO 8601, local offset | all      | Invocation time, e.g. `2026-09-16T14:47:03+10:00`. Local offset so it reads correctly without conversion.                                         |
| `project`    | string                 | all      | `mcp-project-context`'s registered name for the working directory if one exists; otherwise the working directory's leaf name. Never the git       |
|              |                        |          |   top-level directory name — this workspace has unrelated projects sharing git roots.                                                             |
| `branch`     | string                 | all      | Git branch at invocation (`git branch --show-current`). `"n/a"` if not a git repo.                                                                |
| `verdict`    | `"RED"`                | all      | Matches the gate verdict that triggered the write.                                                                                                |
|              |   \| `"RESOLVED"`      |          |                                                                                                                                                   |
| `assumption` | string                 | all      | The Step 0 line, verbatim. `RESOLVED` restates the `RED` entry's assumption so both are found together.                                           |
| `reason`     | string                 | RED      | Which signal(s) fired (e.g. `"signal-1,signal-2"`).                                                                                               |
| `next_test`  | string                 | RED      | The cheapest real-world test defined by the gate.                                                                                                 |
| `waiver`     | boolean                | RED      | `true` if expansion proceeded despite RED. Two `true` on one assumption is itself a finding.                                                      |
| `result`     | `"PASS"` \| `"FAIL"`   | RESOLVED | Outcome of the `next_test` named in the RED entry being resolved.                                                                                 |
| `killed`     | string                 | RESOLVED | What this result invalidated, or `"none"`.                                                                                                        |
| `learned`    | string \| `null`       | all      | Optional miss/false-positive/wording note. Capture only — never read back or acted on.                                                            |

## Examples

RED:

```json
{"ts":"2026-09-16T14:47:03+10:00","project":"cambium-swap","branch":"main","verdict":"RED","assumption":"real cnMaestro auth/read works with held credentials","reason":"signal-1","next_test":"one authenticated call against one real cnMaestro-managed device","waiver":false,"learned":null}
```

RESOLVED:

```json
{"ts":"2026-09-17T09:12:00+10:00","project":"cambium-swap","branch":"main","verdict":"RESOLVED","assumption":"real cnMaestro auth/read works with held credentials","result":"PASS","killed":"none","learned":null}
```

## Provenance

Supersedes the original colon-delimited text-block format, changed before any entry was ever written to the ledger (no trial data existed at the time of the change, so this is pre-first-write
hardening, not mid-trial schema churn). See [`../BRIEF.md`](../BRIEF.md), open decision #5.
