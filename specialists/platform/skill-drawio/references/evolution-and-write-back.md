---
Title: Evolution and write-back
Category: reference
Status: current
Authority: local-supplement
Scope: How engagements in any project feed reusable draw.io knowledge back into this skill, and how it is kept current
Last reviewed: 2026-10-19
Summary: >-
  Standing write-back contract: classify every engagement at closeout, add dated Learned or Disputed entries with evidence and a falsifier plus a
  CHANGELOG line, park entries in the project when this source cannot be written, and reconcile at release.
---

# Evolution and write-back

Adapted from skill-coder `references/evolution-and-write-back.md` (operator, 2026-10-19: any project that uses a skill writes its learning back).

## Contents

- [Standing write-back contract](#standing-write-back-contract)
- [Entry format](#entry-format)
- [Projects that use this skill](#projects-that-use-this-skill)
- [Release reconciliation](#release-reconciliation)

## Standing write-back contract

A session that drew, rendered, exported or read a draw.io file engaged this skill, invoked or not. At closeout it classifies the engagement in one sentence and writes what it taught:

| Class                        | Action                                                                                                      |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `no_new_reusable_learning`   | Nothing to write; say so                                                                                    |
| `verified_reusable_update`   | A Learned entry in the focused reference, and one CHANGELOG line under `## Unreleased`                      |
| `reusable_candidate`         | The same, with evidence `UNVERIFIED` and a falsifier that would settle it                                   |
| `contradicts_existing_claim` | A Disputed entry beside the old text; never delete or silently rewrite it                                   |
| `version_specific`           | A Learned entry naming the draw.io version, and a `compatibility.yaml` row when a new version was exercised |
| `project_only`               | The engaging project's own docs (its drawing profile, its page numbering), not here                         |
| `code_practice`              | skill-coder, not here                                                                                       |

## Entry format

At the end of the relevant section of the reference a future reader would open (the routing table in `SKILL.md`):

```text
> **Learned 2026-10-19** · <scope: core | draw.io 32.5.5 | ...> · VERIFIED_PRIMARY · Source: <doc URL, or file:line> · Falsifier: <observation that would prove it wrong>
> <the fact, generic: no customer names, hostnames, addresses, keys or credentials>
```

A contradiction uses `> **Disputed YYYY-MM-DD**` with the same fields plus `Conflicts: <claim ID>`. The CHANGELOG line names the file and the same date; `tests/test_package_contract.py` fails an entry
without one. Read the file back after writing, run `just test` and `just check`, and commit it in `skills_stuff`.

## Projects that use this skill

1. **Engaged means used**: a session that touched a draw.io file or this pack's code, whether or not its project routes to this skill.
2. **At closeout** the session writes each reusable fact here; skill-slurp-chat Step 5b checks it is present, read back and committed.
3. **When this source cannot be written**, the entry waits in the project under `## skill-drawio write-back candidates`. skill-coder's `scripts/write_back.py --project-root <project> --skill
   skill-drawio` lists parked entries; the next engaged session promotes each one (re-verifying it), deletes it from the project and says so in both change logs.
4. A layout or style change found in a project's review goes into the engine with a test (and every consumer's drawing re-proven), not only into prose.

## Evidence with every entry

Operator, 2026-10-20 (every calling project owes it): A write-back that records how something is done carries
(1) a **code excerpt** of the logic that does it: the few lines that matter (about 30 at most), as a fenced block with its source path and
commit, secrets and customer identifiers removed; and (2) for anything with a visual surface (Nautobot, OpenWISP, a device web UI, a draw.io
render) a **screenshot** as reference, saved under `references/screenshots/<YYYYMMDD>-<slug>/` with a `readme.md` naming each image, what it
shows and where it was taken. Site names, addresses, MACs and serials are redacted or the shot is taken on a lab or sample instance; when the
surface is not live yet, the entry says "screenshot pending: <page>, after <deploy>" and the next engagement adds it.

## Release reconciliation

At a release the maintainer folds each still-valid Learned entry into the prose, adds a `sources.yaml` claim when a decision depends on it, moves `## Unreleased` under the new version and reruns the
checks. A single success is a candidate, not a rule, until a second drawing, the official documentation or the source agrees.
