---
Title: GoalGuard Evolution and Write-Back
Category: reference
Status: current
Authority: local-supplement; entry format and evidence rule follow skill-coder and skill-drawio (operator, 2026-10-19 and 2026-10-20)
Scope: What a session that used or touched GoalGuard owes this pack at closeout, and the entry format
Last reviewed: 2026-10-27
Summary: >-
  Any session that gated, ranked, traced or changed GoalGuard work writes a dated Learned entry into the reference a future reader would open, plus
  one changelog line, with a code excerpt or screenshot as evidence; entries that cannot be written here are parked in the project.
---
# Evolution and write-back

## Trigger

Touching this skill's domain, invoked or not, engages its write-back: assessing a proposal, ranking work, tracing a milestone, wiring a hook, reading Vikunja for GoalGuard, or changing this pack.

## Classify the engagement

`no_new_reusable_learning`, `verified_reusable_update`, `reusable_candidate`, `contradicts_existing_claim`, `project_only`, `domain_only` (same classes as skill-coder).

## Entry format

```text
> **Learned YYYY-MM-DD** · <scope> · <EVIDENCE> · Source: <URL or file:line> · Falsifier: <observation that would prove it wrong>
> <the fact, generic: no customer names, hostnames, addresses, keys or credentials>
```

`EVIDENCE` is `VERIFIED_PRIMARY`, `VERIFIED_SECONDARY`, `UNVERIFIED` or `USER_STATED`. Put the entry in the reference a future reader would open (a hook fact in [enforcement-and-hooks.md](enforcement-and-hooks.md), a Vikunja
behaviour in [vikunja-integration.md](vikunja-integration.md)), and add one line under `## Unreleased` in [../changelog.md](../changelog.md) naming that file and date. Read the entry back and commit it in `skills_stuff`; an uncommitted entry is not written back. A contradiction is a `Disputed` entry beside the old text with `Conflicts:
<claim>`; never delete or silently rewrite.

## Evidence with every entry

A write-back that records how something is done carries a code excerpt of the logic (about 30 lines at most, fenced, with source path and commit, secrets and customer identifiers removed), and for a
visual surface (Vikunja views, a hook prompt) a screenshot under `references/screenshots/<YYYYMMDD>-<slug>/` with a `readme.md` naming each image. When the surface is not live yet, write "screenshot
pending: <page>, after <deploy>".

## When this pack cannot be written

Park the entry in the project under `## skill-goal-guard write-back candidates`; the next engagement promotes it here and removes it there.
