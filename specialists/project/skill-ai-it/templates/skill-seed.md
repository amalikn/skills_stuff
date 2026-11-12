---
Title: Skill seed: <skill-name>
Category: skill-seed
Status: draft
Authority: >-
  Design brief for a new skill pack, written by the operator with an agent; the pack is built from it with `new-skill scaffold` and the agent fills the references, scripts and evidence it lists
Scope: What the skill is for, what it is not, what it learned from real work, and every file the pack will hold
Last reviewed: 2026-11-12
Summary: >-
  Seed for <skill-name>: purpose, boundaries, source material, lessons, routing, scripts, rules, evidence, acceptance scenarios and build order, in the form `new-skill` reads.
---

# Skill seed: <skill-name>

<!-- seed: this file is the one input `new-skill` reads. Replace every `TODO(seed)` with content or delete the row; `new-skill check-seed` fails while one remains.
Write for the agent that will build the pack and has no other context: name files, give evidence, say what is decided and what is not. Keep prose
under 200 columns. Model packs to read before filling this in: skill-nautobot (version-sensitive platform), skill-vagrant (lab tool, guards),
skill-coder (practice with language overrides), skill-network-architect and skill-systems-architect (method packs with shared modules and an
operator layer). -->

## Contents

- [Parameters](#parameters)
- [Purpose and users](#purpose-and-users)
- [Trigger phrases](#trigger-phrases)
- [Non-goals and neighbours](#non-goals-and-neighbours)
- [Source material](#source-material)
- [What was learned](#what-was-learned)
- [Vocabulary](#vocabulary)
- [Outputs and artifacts](#outputs-and-artifacts)
- [Task routing](#task-routing)
- [Scripts plan](#scripts-plan)
- [Templates and assets](#templates-and-assets)
- [Standing rules](#standing-rules)
- [Safety boundaries](#safety-boundaries)
- [Evidence plan](#evidence-plan)
- [Acceptance scenarios](#acceptance-scenarios)
- [Write-back](#write-back)
- [Install and registry](#install-and-registry)
- [Deferred and extensions](#deferred-and-extensions)
- [Open questions](#open-questions)
- [Build order and done](#build-order-and-done)

---

## Parameters

One `key: value` per line; the scaffold reads only this block. `family` is the folder under the skills root: `specialists/project` (method or practice, any project), `specialists/platform` (one
product or tool), `skills` (single-file behavioural contract) or `personal`.

```text seed-parameters
name: TODO(seed)
family: specialists/project
short_description: TODO(seed)
aliases:
scripts: yes
operator_context: no
memory_channel: TODO(seed)
related: skill-coder
forbidden_terms:
```

`short_description` is one line, at most 250 characters, in the form "what it covers: topic, topic, topic". It is the only text every session loads, so it must tell an agent when to pick this skill
and when not to. The full scope goes in `Purpose and users` and lands in SKILL.md's `## Full description`. `aliases` are slash shortcuts (for example `/skill-xyz`) and are registered in the global
instructions by the operator, not by this build. `related` lists the neighbouring skills, comma separated. `forbidden_terms` lists project, customer and people names (comma separated) that must never appear in the finished pack: a shared skill holds only what is true in every project, so the
scaffold refuses if one lands in a generated file. This seed stays in `pending_skills/` and is never copied into the pack, so it may name them while recording what was learned.

## Purpose and users

<!-- One paragraph: what the skill lets an agent do that it could not do reliably without it, for whom, and in which situations. Then one line per kind of user or caller. -->

TODO(seed)

## Trigger phrases

<!-- What the operator or a calling skill says when this skill should run, one per line, in their words (include loose wording, dictation slips and nouns for the artifacts). -->

- TODO(seed)

## Non-goals and neighbours

<!-- What this skill does not own, and who does. A neighbour that owns the fact keeps it; this pack links, never copies. -->

| Not this skill's job | Owner      |
| -------------------- | ---------- |
| TODO(seed)           | TODO(seed) |

## Source material

<!-- Where the knowledge comes from. One row per source: a project and files, a transcript, a vendor page, a person's decision. Label each USER_STATED, VERIFIED_PRIMARY,
VERIFIED_SECONDARY or UNVERIFIED. External pages are captured verbatim into documents/research-sources-<date>/ with a sha256 row; say which. -->

| Source     | Where      | Label       | Capture    |
| ---------- | ---------- | ----------- | ---------- |
| TODO(seed) | TODO(seed) | USER_STATED | not needed |

## What was learned

<!-- The engagement lessons the pack must keep. This is the seed's core: a lesson that is not a row here is lost. Each row says what turned out to be true, how we know,
and what it becomes (a rule in SKILL.md, a reference section, a script, a template, a scenario). Include mistakes and rework: what went wrong first and what fixed it. -->

| Lesson     | Evidence   | Becomes    |
| ---------- | ---------- | ---------- |
| TODO(seed) | TODO(seed) | TODO(seed) |

## Vocabulary

<!-- Terms an agent must use the same way every time, one line each. Include the operator's words and the product's words when they differ. -->

- TODO(seed)

## Outputs and artifacts

<!-- Everything the skill produces: file kinds, formats, names, where they are saved, who reads them and what they must show. A skill that produces nothing durable says so. -->

| Output     | Format and name | Saved in   | Reader     |
| ---------- | --------------- | ---------- | ---------- |
| TODO(seed) | TODO(seed)      | TODO(seed) | TODO(seed) |

## Task routing

<!-- The routing table of SKILL.md: one row per task kind, one reference file per row, small enough to open alone. The scaffold creates each file as a stub whose outline is the
Contents column. Name files `topic-name.md`; never `misc`, `notes` or `other`. Every reference opens with Scope and decision rules and ends with Further reading. -->

| Task       | Reference file | Contents   |
| ---------- | -------------- | ---------- |
| TODO(seed) | TODO(seed).md  | TODO(seed) |

## Scripts plan

<!-- Scripts the pack will ship, or `none`. Each is stdlib-only, tested, read-only by default, with a timeout on every call and `--apply` for any write (skill-coder). Mark each `reuse`
(promote from a project: give its path) or `new`. A script not listed here is not built. -->

| Script     | Does       | Origin | Safety    | Test       |
| ---------- | ---------- | ------ | --------- | ---------- |
| TODO(seed) | TODO(seed) | new    | read-only | TODO(seed) |

## Templates and assets

<!-- Forms, starter files, examples and fixtures the pack ships under templates/ or examples/, or `none`. Say who copies them and how placeholders are named. -->

- TODO(seed)

## Standing rules

<!-- Invariants an agent must follow whenever the skill is active, each with its reason and whose decision it is and when ("operator, 2026-11-12"). The rules go into SKILL.md. -->

| Rule       | Reason     | Decided by           |
| ---------- | ---------- | -------------------- |
| TODO(seed) | TODO(seed) | operator, TODO(seed) |

## Safety boundaries

<!-- What the skill may read, what it may write, what needs `--apply` or the project's authorisation, and what it never does (credentials, live systems, deletes, external sends). -->

- Reads: TODO(seed)
- Writes: TODO(seed)
- Never: TODO(seed)

## Evidence plan

<!-- Load-bearing claims the pack makes. Each becomes a row in sources.yaml with a falsifier (the observation that would prove it wrong). Environments tested go in
compatibility.yaml with version and date. -->

| Claim      | Evidence and source | Falsifier  |
| ---------- | ------------------- | ---------- |
| TODO(seed) | TODO(seed)          | TODO(seed) |

## Acceptance scenarios

<!-- At least five prompts with the behaviour expected, including one that should not trigger the skill and one where the agent should stop and ask. They become tests/scenarios.md
and the eval procedure. -->

| Prompt     | Expected behaviour |
| ---------- | ------------------ |
| TODO(seed) | TODO(seed)         |

## Write-back

<!-- How the pack learns. Which reference takes Learned entries per kind of finding, the memory-keeper channel (the `memory_channel` parameter), and which classes of work stay in the
calling project. -->

- Learned entries go to: TODO(seed)
- Stays in the project: TODO(seed)

## Install and registry

<!-- Where the skill is installed (symlink, never copy), the skills.md rows to add, and any AGENTS.md "Shared tools and skills" line the operator wants. -->

- Install targets: `~/.claude/skills`, `~/.codex/skills`, `~/.hermes/skills/domain` (symlinks to the canonical folder).
- Registry rows: TODO(seed)

## Deferred and extensions

<!-- Everything researched or considered that this skill is NOT using now, so it can be enabled or built later without repeating the research. One row each: what it is, why it is not used now (scope, personal use, licence, cost, not read), where the evidence is (a research file and section) and how to enable it. Route this section as an `extensions.md` reference (a part file `parts/extensions.md` becomes its body) so an agent can find it when the skill is extended. Say `none` if nothing was set aside. -->

| Item | Why not now | Evidence | How to enable |
| --- | --- | --- | --- |
| TODO(seed) | TODO(seed) | TODO(seed) | TODO(seed) |

## Open questions

<!-- Decisions not yet made. Mark each `blocking` (the build waits) or `later`. The agent asks the operator about blocking ones before scaffolding. -->

| Question   | Blocking | Owner    |
| ---------- | -------- | -------- |
| TODO(seed) | later    | operator |

## Build order and done

<!-- The order the agent builds in and what done means. Keep the default unless the skill needs otherwise. -->

1. `new-skill check-seed` passes (no `TODO(seed)` left, every table filled or its row deleted).
2. `new-skill scaffold` plan read; then `--apply` writes the skeleton and copies this seed into the pack's `docs/`.
3. Run `skill-ai-it bootstrap` on the new folder (governance files, task runner, checker), then `just bootstrap` and `just check`.
4. Fill each reference from `What was learned` and `Source material`; every claim gets its `sources.yaml` row.
5. Write each script in `Scripts plan` with skill-coder: tests first, catalogue row, recipe, `code-map.toml` entry.
6. Turn `Acceptance scenarios` into `tests/scenarios.md`, run them, and record the result in `tests/eval-procedure.md`.
7. `skill_pack_check.py <pack> --strict` reports no error and no `planned` row; `just check` passes.
8. Install by symlink, add the registry rows, add the CHANGELOG `## Unreleased` line, and commit in `skills_stuff` (the operator decides when to push).
