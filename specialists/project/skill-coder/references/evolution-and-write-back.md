---
Title: Evolution and write-back
Category: reference
Status: current
Authority: local-supplement
Scope: How engagements in any project feed reusable coding knowledge back into this skill, and how it is kept current
Last reviewed: 2026-10-19
Summary: >-
  Standing write-back contract: classify every engagement at closeout, add dated Learned or Disputed entries with evidence
  and a falsifier plus a CHANGELOG line, route project or language facts to their owner, and reconcile at release.
---

# Evolution and write-back

Adapted from skill-nautobot `references/evolution-and-write-back.md`.

## Standing write-back contract

This skill is a cross-project source of programming practice. Using it, invoked or not, carries the obligation to write back what the engagement taught: a rule that held or failed, a tool's
version-specific behaviour, a fix, a root cause or a correction. Write it before the session ends when the task permits edits to this skill's canonical source (`skills_stuff`). Read the edited file
back in the same session; a scratchpad note is not proof.

Classify every engagement at closeout, one sentence in the reply:

| Class                        | Action                                                                                                      |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `no_new_reusable_learning`   | Nothing to write; say so                                                                                    |
| `verified_reusable_update`   | Add a Learned entry to the focused reference or language file, and one CHANGELOG line under `## Unreleased` |
| `reusable_candidate`         | Same, with evidence `UNVERIFIED` and a falsifier that would settle it                                       |
| `contradicts_existing_claim` | Add a Disputed entry beside the old text; never delete or silently rewrite it                               |
| `language_specific`          | Write it in `languages/<lang>.md`, not in a core reference                                                  |
| `project_only`               | Write it in the engaging project's own docs, not here                                                       |
| `domain_only`                | Write it in the domain skill that owns it (a platform or device skill), not here                            |

## Entry format

Put the entry in the file a future reader would open for that task (the routing table in `SKILL.md`), at the end of the relevant section:

```text
> **Learned 2026-10-19** · <scope: core | python 3.14 | ruff 0.x | ...> · VERIFIED_PRIMARY · Source: <doc URL, or file:line> · Falsifier: <observation that would prove it wrong>
> <the fact, generic: no customer names, hostnames, addresses, keys or credentials>
```

A contradiction uses `> **Disputed YYYY-MM-DD**` with the same fields plus `Conflicts: <claim ID or section>`. The evidence label is one of `VERIFIED_PRIMARY`, `VERIFIED_SECONDARY`, `UNVERIFIED` or
`USER_STATED`. The CHANGELOG line names the file and the same date. The pack's checks are expected to fail on a malformed entry or on an entry with no matching CHANGELOG line (UNVERIFIED until the
coordinator's checker implements it).

If this skill's source cannot be written (read-only path, no authorisation), put the same entry in the engaging project's governed docs under a heading naming this skill, and link it from that
project's index; the next engagement with write access promotes it.

## Release reconciliation

At a release the maintainer promotes each still-valid Learned entry into the prose; adds a `sources.yaml` claim only when a decision depends on it; adds a scenario to `tests/scenarios.md` when a
no-skill agent would plausibly get the fact wrong; moves `## Unreleased` under the new version; and reruns the checks.

## Promoting a project script

See [refactoring-and-promotion.md](refactoring-and-promotion.md). A script promoted into this pack is stdlib-only, declares `REQUIRES_PYTHON`, reads code as files and runs in the target's interpreter
([runtime-boundaries.md](runtime-boundaries.md)).

## Keeping it current

Each language file names the tool versions its commands were checked against, or says UNVERIFIED. When a project's tool version differs, re-verify the command against that version's documentation
before relying on it. A single success is a candidate, not a rule: label it `UNVERIFIED` until a second environment, the official documentation or the source agrees.
