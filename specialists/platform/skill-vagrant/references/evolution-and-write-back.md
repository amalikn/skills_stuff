---
Title: Evolution and write-back
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: The standing write-back contract: engagement classes, the Learned and Disputed entry format, evidence with every entry, research captures, release reconciliation and script promotion.
---

# Evolution and write-back

## Standing write-back contract

This skill is a cross-project source of Vagrant and Parallels lab knowledge. Invoking it carries the obligation, in any project, to write back what the engagement taught: a new fact, a version change
in behaviour, a fix, a root cause, or a correction. Write it before the session ends when the active task permits edits to this skill's canonical source; skill use alone never authorizes a VM action.
Read the edited file back in the same session: a scratchpad note or a timestamp is not proof.

Classify every engagement at closeout, one sentence in the reply:

| Class                        | Action                                                                                    |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| `no_new_reusable_learning`   | Nothing to write; say so                                                                  |
| `verified_reusable_update`   | Add a Learned entry to the focused reference and one CHANGELOG line under `## Unreleased` |
| `reusable_candidate`         | Same, with evidence `UNVERIFIED` and a falsifier that would settle it                     |
| `contradicts_existing_claim` | Add a Disputed entry beside the old text; never delete or silently rewrite it             |
| `project_only`               | Write it in the engaging project's docs (its lab layout, VM names, stages), not here      |
| `guest_only`                 | Write it in the skill that owns what runs in the guest (for example skill-smc), not here  |

## Entry format

Put the entry in the reference a future reader would open for that task (the routing table in `SKILL.md`), at the end of the relevant section. Two lines minimum:

```text
> **Learned 2026-11-07** · Vagrant 2.4.9 / vagrant-parallels 2.4.9 / Parallels 27.1 · VERIFIED_PRIMARY · Source: <doc URL or capture> · Falsifier: <observation that would prove it wrong>
> <the fact, generic: no site names, hostnames, addresses, keys or credentials>
```

A contradiction uses `> **Disputed YYYY-MM-DD**` with the same fields plus `Conflicts: <claim ID, section or statement>`. The evidence label is one of `VERIFIED_PRIMARY`, `VERIFIED_SECONDARY`,
`UNVERIFIED`, `USER_STATED` or `CANDIDATE`. The CHANGELOG line names the reference file and the same date. `tests/test_package_contract.py` fails on a malformed entry, or on an entry with no matching
CHANGELOG line.

If this skill's source cannot be written, put the same entry in the engaging project's governed docs under a heading naming this skill, and link it from that project's index; the next engagement with
write access promotes it.

## Evidence with every entry

Operator, 2026-10-20 (every calling project owes it): a write-back that records how something is done carries (1) a **code excerpt** of the logic that does it: the few lines that matter (about 30 at
most), as a fenced block with its source path and commit, secrets and lab addresses removed; and (2) for anything with a visual surface (a VM console, the Parallels Control Center) a **screenshot**,
saved under `references/screenshots/<YYYYMMDD>-<slug>/` with a `readme.md` naming each image, what it shows and where it was taken. A console screenshot comes from `prlctl capture <vm> --file <png>`
on a lab VM.

## Research sources

A fact from outside the lab is captured verbatim before it is used: `documents/research-sources-<YYYYMMDD>/<slug>.md` with a provenance header (Canonical URL, Retrieved, HTTP status or fetch path),
indexed with its sha256 in that folder's `readme.md`. Pages that block agents are fetched with all-scraper (`just -f /Volumes/Data/_ai/_tool/tools_stuff/all-scraper/justfile fetch <url> --markdown`);
GitHub issues and files with `gh`. The contract test checks that the index lists every capture with its hash.

## Release reconciliation

At a release, the maintainer: promotes each still-valid Learned entry into the reference prose; adds a `sources.yaml` claim only when the fact is load-bearing; adds or updates a `compatibility.yaml`
row when the evidence came from a new version or a live rung; adds a scenario when a no-skill agent would plausibly get the fact wrong; moves `## Unreleased` under the new version; and reruns the
tests.

## Promoting a project script

A lab script earns promotion when its behaviour holds for any Vagrant or Parallels lab, it imports nothing project-specific, and its engine can be pure or read-only with the command runner injected by
the caller. Then: the engine goes to `scripts/` with offline tests in `tests/test_helpers.py` (stdlib only, enforced by the contract test); the project script becomes a thin wrapper; and the CHANGELOG
names the source project and script. `vagrant_copy_check.py` is the generic form of smc-resiliency's `check_vagrant_copies` (promoted 2026-11-07; the project keeps its own check).

## Keeping it current

`operations-cookbook.md` names the versions it was verified against. When Vagrant, vagrant-parallels or Parallels Desktop changes, re-verify every section whose syntax the task relies on, then update
that line and `compatibility.yaml`. A single success is a candidate, not a rule: label it `UNVERIFIED` until a second environment, the official documentation or the source agrees.
