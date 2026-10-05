# Evolution and write-back

## Standing write-back contract

This skill is a cross-project source of Nautobot knowledge. Invoking it carries the obligation, in any project, to write back what the engagement taught: a new fact,
a version change in behaviour, a fix, a root cause, or a correction. Write it before the session ends when the active task permits edits to this skill's canonical
source; skill use alone never authorizes a live-platform action. Read the edited file back in the same session: a scratchpad note or a timestamp is not proof.

Classify every engagement at closeout, one sentence in the reply:

| Class                        | Action                                                                                          |
| ---------------------------- | ----------------------------------------------------------------------------------------------- |
| `no_new_reusable_learning`   | Nothing to write; say so                                                                        |
| `verified_reusable_update`   | Add a Learned entry to the focused reference and one CHANGELOG line under `## Unreleased`       |
| `reusable_candidate`         | Same, with evidence `UNVERIFIED` and a falsifier that would settle it                           |
| `contradicts_existing_claim` | Add a Disputed entry beside the old text; never delete or silently rewrite it                   |
| `project_only`               | Write it in the engaging project's docs, not here                                               |
| `equipment_only`             | Write it in the equipment skill (for example skill-cambium or skill-smc), not here              |

## Entry format

Put the entry in the reference a future reader would open for that task (the routing table in `SKILL.md`), at the end of the relevant section. Two lines minimum:

```text
> **Learned 2026-10-05** · Nautobot 3.2.3 · VERIFIED_PRIMARY · Source: <doc URL, or file:line in the installed source> · Falsifier: <observation that would prove it wrong>
> <the fact, generic: no customer names, hostnames, addresses, keys or credentials>
```

A contradiction uses `> **Disputed YYYY-MM-DD**` with the same fields plus `Conflicts: <claim ID or section>`. The evidence label is one of `VERIFIED_PRIMARY`,
`VERIFIED_SECONDARY`, `UNVERIFIED` or `USER_STATED`. The CHANGELOG line names the reference file and the same date. `tests/test_package_contract.py` fails on a
malformed entry, or on an entry with no matching CHANGELOG line, so a write-back is checked the next time anyone runs the tests.

If this skill's source cannot be written (read-only path, no authorization), put the same entry in the engaging project's governed docs under a heading naming this
skill, and link it from that project's index; the next engagement with write access promotes it.

## Release reconciliation

Learned entries are cheap on purpose. At a release, the maintainer: promotes each still-valid Learned entry into the reference prose; adds a `sources.yaml` claim
only when the fact is load-bearing (a decision depends on it); adds or updates a `compatibility.yaml` row when the evidence came from a new version or a live rung;
adds a scenario when a no-skill agent would plausibly get the fact wrong; moves `## Unreleased` under the new version; and reruns the tests.

## Keeping it current

Each `operations-cookbook.md` names the version it was verified against. When the installed version changes, re-verify every section whose syntax the task relies on,
then update that line and `compatibility.yaml`; until then, treat the cookbook as the old version's syntax. A single success is a candidate, not a rule: label it
`UNVERIFIED` until a second environment, the official documentation or the installed source agrees. Claim N-C12.
