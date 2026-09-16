---
Title: skill-walk-before-run — README
Status: current
Last reviewed: 2026-09-16
Summary: Purpose, invocation, package map and state location for the walk-before-run gate skill.
---

# skill-walk-before-run

## Purpose

A minimal blocking gate that judges whether the work about to happen is expansion sitting on an unverified load-bearing assumption. On RED it stops expansion and redirects to the cheapest real-world
test of that assumption, instead of the design-before-verification pattern described in [`BRIEF.md`](BRIEF.md).

v0.1 is deliberately small: it exists to test whether a tiny blocking gate changes behaviour at the moment scaffolding starts, on a three-project trial (cambium-swap plus two fresh projects). See the
brief for the full decision logic rationale, parked v0.2 ideas, and the acceptance tests — it is the provenance record for this build and is not loaded at runtime.

## Invocation

Manual only: `/skill-walk-before-run` or its alias `/skill-wbr`. Defaults to the calling project — the project of the invoking session; name a different project explicitly to override. There is no
session-start auto-fire and no self-modification in v0.1.

## Package map

- `SKILL.md` — the entire runtime decision procedure: Step 0 (name the assumption), the RED/AMBER/GREEN signals, what each verdict does, the reality-contact definition, the four-step gate, the
  stand-down cases, and the ledger entry format. This is the only file with runtime behaviour.
- `README.md` — this file.
- `CHANGELOG.md` — behavioural revisions between versions.
- `BRIEF.md` — the frozen creation brief: full decision-logic rationale, parked v0.2 ideas, acceptance tests, and the calibration example. Not loaded at runtime; kept as the provenance record.
- `schemas/ledger-entry.md` — field reference and examples for `ledger.jsonl` entries. Not loaded at runtime; `SKILL.md`'s inline JSON templates are sufficient to act on.

No `scripts/`, `references/`, `evals/` or `docs/` directories yet. Each has a named earn-in trigger in the brief's parked list (§ "Parked for v0.2") and is added only when the trial actually presses
on it.

## Where the mutable state lives

Everything above is specification, versioned with the skill. The one piece of runtime state is the episode ledger, `ledger.jsonl`, colocated in this same directory rather than under `skills-data`:

```text
/Volumes/Data/_ai/_skills/skills_stuff/skills/skill-walk-before-run/ledger.jsonl
```

Appended only on RED, on waiver, and on RED-to-resolved — never on GREEN or AMBER. One JSON object per line. It is created on first write and is absent until then. Field reference:
[`schemas/ledger-entry.md`](schemas/ledger-entry.md).

On the same condition (RED or RESOLVED), two things are also appended to the target project: the full entry, mirrored verbatim to `.wbr-ledger.jsonl` in that project's own root (created if absent —
recovery copy only, read only if `ledger.jsonl` here is ever lost), and a one-line pointer under its `SCRATCHPAD.md`'s `## Open items`, if that file already exists (never created if absent).
`ledger.jsonl` remains the sole source of truth while it exists; both of these are secondary.

Recovery, if `ledger.jsonl` is ever actually lost: reconstruct it by concatenating every known project's `.wbr-ledger.jsonl`, sorted by `ts`. A one-time manual step, done deliberately once loss is
confirmed — not an automatic or continuous sync.

## Install

Canonical source is this directory. Installed into agent runtimes by symlink, never by copy, so the specification never drifts:

```text
~/.claude/skills/skill-walk-before-run -> /Volumes/Data/_ai/_skills/skills_stuff/skills/skill-walk-before-run
~/.codex/skills/skill-walk-before-run  -> /Volumes/Data/_ai/_skills/skills_stuff/skills/skill-walk-before-run
```
