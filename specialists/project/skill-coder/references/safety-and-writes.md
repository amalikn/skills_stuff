---
Title: Safety and writes
Category: reference
Status: current
Authority: local-supplement
Scope: Code that changes anything outside its own process - files, databases, devices, remote systems
Last reviewed: 2026-10-19
Summary: >-
  Read by default, plan then --apply, write gates the code enforces, credentials never in code, one writer per record,
  idempotent writes, record only after the target confirms, fail closed, and canary before batch.
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
