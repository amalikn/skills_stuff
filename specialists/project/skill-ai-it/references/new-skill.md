---
Title: skill-ai-it reference: new-skill (seed, scaffold and check a new skill pack)
Category: reference
Status: current
Authority: local-supplement
Scope: The `new-skill` mode: how a new skill pack is seeded, scaffolded, built and checked so every pack shares one shape
Last reviewed: 2026-11-12
Summary: >-
  The new-skill capability: the seed template and what a good seed holds, the scaffold and what it writes versus what bootstrap and the agent write, the pack contract check, the install and registry steps, and
  the lessons built in from skill-nautobot, skill-vagrant, skill-coder and the two architect packs.
---

# new-skill: seed, scaffold and check a new skill pack

Invoked as `skill-ai-it new-skill [skill-name]` (or `/skill-ai-it new-skill`). Added 2026-11-12 (operator): a new skill is built from a written **seed** that keeps what the engagement learned, a
**scaffold** that creates the pack skeleton every skill-* pack shares, and a **pack check** that holds the finished pack to one contract. Before this, each pack was built by hand from a sibling and
drifted (skill-mikrotik, 2026-10-07: shebang-run recipes, bare `python3`, no contract test).

## Contents

- [The flow](#the-flow)
- [Stage 1: the interview and research](#stage-1-the-interview-and-research-what-the-agent-does)
- [The seed folder](#the-seed-folder)
- [What a good seed holds](#what-a-good-seed-holds)
- [Who writes what](#who-writes-what)
- [The pack standard](#the-pack-standard)
- [The pack contract check](#the-pack-contract-check)
- [Install, registry and closeout](#install-registry-and-closeout)
- [Boundaries](#boundaries)
- [Lessons built in](#lessons-built-in)

## The flow

The agent runs the seeding itself: it interviews the operator, researches online, harvests lessons from existing work, and fills the seed. Each stage has a catalogued recipe (scripts in `scripts/skills/`); plan first
everywhere, `--apply` writes.

| Stage | Recipe | What happens |
| --- | --- | --- |
| 1a. Intake | `just new-skill-intake skill-topic [--family F] --apply` | Writes `templates/skill-intake.md` to `pending_skills/<name>/intake-<name>-<stamp>.md` and the seed folder's `research/` and `parts/` indexes. Refuses to overwrite. |
| 1b. Interview | the agent, with the operator | Searches the conversation, named files and the model packs first, then asks what is left in four rounds of at most four questions with options; records answers as USER_STATED. See Stage 1 below. |
| 1c. Harvest | the agent | Reads each row of `Material to harvest` (this conversation, files, repos, earlier session records) and extracts lessons, mistakes and reusable code with their evidence. |
| 1d. Research briefs | `just new-skill-research-briefs INTAKE --apply` | Writes one generic brief per research topic into `research/briefs/`; refuses if a forbidden term would reach an outside search. |
| 1e. Research | research agents, one per brief | Each reads primary sources, reports licences and failure modes, and the report is saved in `research/` (`research-<stamp>.md`), never only in the conversation. |
| 2. Seed | `just new-skill-seed skill-topic --from-intake INTAKE --apply` | Writes the seed with the intake's parameters filled; the agent fills every `TODO(seed)` from the answers, the harvest and the research, and drafts `parts/` for the references. |
| 3. Check | `just new-skill-check SEED` | Lists what is missing: unfilled markers, missing sections, thin tables, vague reference names, blocking questions. |
| 4. Scaffold | `just new-skill-scaffold SEED [--apply]` | Plans, then writes the skeleton under `<skills root>/<family>/<name>/`; a part becomes its reference's body. Skips identical files, writes `.proposed` beside different ones. The seed folder stays in `pending_skills/`. |
| 5. Govern | skill-ai-it `bootstrap` on the new folder, then `just bootstrap` | Adds the task runner, checker, navigation files and managed blocks the scaffold leaves to bootstrap. |
| 6. Build | the agent, from the seed and parts | Fills each `TODO(build)`: references from `What was learned` and the research, scripts from `Scripts plan` (skill-coder), claims into `sources.yaml`, scenarios run. |
| 7. Verify | `just skill-pack-check PACK --strict`, the pack's `just check` and `just test` | No error, no warning, no `planned` tool row. |
| 8. Close | install by symlink, registry rows, CHANGELOG line, commit in `skills_stuff` | The operator decides when to push. |

## Stage 1: the interview and research (what the agent does)

1. **Start from what is known.** When the operator names a skill, run `new-skill-intake`, then fill every answer the conversation, the named files or the repo already gives, tagging each with its source. Never ask a
   question a file answers.
2. **Ask in rounds.** Four rounds (purpose and callers; boundaries and safety; knowledge to keep; quality and install), at most four questions per round, each with two to four options and a recommended first option,
   through the question tool. Write the operator's answer verbatim under the question, labelled `USER_STATED`. "Not sure" becomes an open question (`later` or `blocking`) in the seed.
3. **Harvest.** Treat the current conversation as source material: list what went wrong first and what fixed it, the operator's rulings with their dates, the code that was written and is likely to be reused (promote
   it per skill-coder), and the model packs to read. These become the seed's `What was learned` rows.
4. **Research with briefs.** Run `new-skill-research-briefs`, then dispatch one research agent per brief in parallel (generic queries only: no forbidden term, no project, customer or people name goes to a web search).
   Each report is saved under `research/` before it is used, with its evidence labels, licences quoted exactly and the pages that were blocked. Ask the research to find existing skills, libraries and licences, not
   only guidance, and to record negative findings. Verify load-bearing claims the agents tag `UNVERIFIED` or contradict each other on before they become `sources.yaml` rows. Copy code only after reading its licence
   and the commit it comes from.
5. **Fill the seed.** Run `new-skill-seed --from-intake`, fill each section from the answers, the harvest and the research, and draft the references that carry the most novel knowledge into `parts/`. Run
   `new-skill-check` until it is clean, and ask the operator about any `blocking` question before scaffolding.
6. **Keep the evidence.** Everything gathered stays in the seed folder for good (see the seed folder, below).

## The seed folder

A seed is a folder, not one file: `pending_skills/<name>/` holds the master seed (`seed-<name>-<stamp>.md`, the brief the scaffold reads), `parts/` (drafted reference bodies) and `research/` (research records,
verbatim captures, transcripts). **All research and part files stay in this folder for good, beside the seed (operator, 2026-11-12)**: the seed's `Source material` and `What was learned` tables point at them and a
later revision of the pack starts there; nothing is deleted or moved after the build. `just new-skill-seed` creates the folders with a short index each. A file in `parts/` named like a routed reference becomes that
reference's body under a generated front matter on `scaffold --apply` (the scaffold reports any part it did not use, and `forbidden_terms` is checked against it); the build copies into the pack's own `documents/`
only what the pack needs to cite.

## What a good seed holds

`templates/skill-seed.md` has nineteen sections; the ones that decide quality:

- **What was learned** is the core. A lesson that is not a row is lost: write what turned out true, how it is known, and what it becomes (a rule, a reference section, a script, a template, a
  scenario). Include the mistakes and the rework, not only the result.
- **Source material** labels every source `USER_STATED`, `VERIFIED_PRIMARY`, `VERIFIED_SECONDARY` or `UNVERIFIED`, and says which external pages are captured verbatim.
- **Task routing** is one reference per task kind, named for its topic (never `misc`), small enough to open alone. This table becomes SKILL.md's routing table and the reference stubs.
- **Non-goals and neighbours** keeps the pack from copying a neighbour's facts: the owner keeps them and this pack links.
- **Standing rules** carry a reason and who decided them and when ("operator, 2026-11-12"); they land in SKILL.md.
- **Acceptance scenarios** are at least five, including one that must not trigger the skill and one where the agent must stop and ask.
- **Open questions** marked `blocking` stop the build until answered.
- **Deferred and extensions** lists what was researched or considered and is not used now, with why, where the evidence is and how to enable it later; it is routed as an `extensions.md` reference (a `parts/extensions.md` becomes its body), so the skill can be extended without repeating the research.

Parameters are a plain `key: value` block, so the scaffold needs no YAML parser. `family` is `specialists/project` (method or practice for any project), `specialists/platform` (one product or tool),
`skills` (single-file contract) or `personal`.

## Who writes what

| Written by               | Files                                                                                                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The scaffold (this mode) | `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `references/` (index, write-back, one stub per routed task), `sources.yaml`, `compatibility.yaml`,     |
|                          |   `tests/` (scenarios, eval procedure, contract test), `.gitignore`, and with `scripts: yes` the Python pin, `ruff.toml` and `requirements.txt`; `operator/readme.md`     |
|                          |   with `operator_context: yes`; a copy of the seed in `docs/`                                                                                                             |
| skill-ai-it bootstrap    | `justfile` (pinned runtimes, `check`, `test`, `docs`, `stale`, rotation), `scripts/check_governance.py`, `AI_NAVIGATION.md`, `context-map.yaml`, managed blocks,          |
|                          |   `scripts/README.md`, `code-map.toml`                                                                                                                                    |
| The agent, from the seed | Every `TODO(build)`: reference content, scripts and their tests and catalogue rows, `sources.yaml` rows with evidence, `compatibility.yaml` environments, verbatim        |
|                          |   captures under `documents/`                                                                                                                                             |

The scaffold writes governance files that bootstrap would also write (AGENTS, CLAUDE, README, CHANGELOG) because they carry the pack's own contract; bootstrap then adds only its managed blocks and
never overwrites them.

## The pack standard

What skill-nautobot, skill-vagrant, skill-coder, skill-network-architect and skill-systems-architect share, and so what every pack has. Read the nearest model before writing a seed: skill-nautobot
(version-sensitive platform: versions, compatibility, "search before building"), skill-vagrant (a lab tool: guards, read-only by default), skill-coder (a practice with per-language overrides),
skill-network-architect and skill-systems-architect (method packs: shared modules, an `operator/` layer, a handoff template, evals).

- **SKILL.md is the activation surface**, within 200 lines and 25 KB: a one-paragraph front-matter `description` that says when to pick the skill and when not to; `## Full description` (the full
  scope, moved out of the listing to cut startup tokens, 2026-11-11); `## Role and non-goals`; read, write and evidence boundaries; `## Orient first` with the commands that establish version and
  environment; a task routing table to one reference per row; version-sensitive facts verified against version-matched documentation; a search-before-building ladder; the pack's tools; standing rules;
  related skills; and the `## Standing write-back contract` with its evidence rule.
- **`references/`** holds one topic per file; each opens with scope and decision rules and ends with further reading; `evolution-and-write-back.md` is always there. Detail is never inlined into
  SKILL.md.
- **Evidence is data.** `sources.yaml` holds each load-bearing claim with its source and a falsifier; `compatibility.yaml` holds tested environments; verbatim captures sit under
  `documents/research-sources-<date>/` with a sha256 row.
- **Generic, operator and project layers stay apart.** The general references are operator-neutral; the operator's estate lives in `operator/<area>/`; project facts live in the project.
- **Scripts** are stdlib-only, tested, catalogued and read-only by default, with a timeout on every call and `--apply` for any write; they run through the `justfile`'s pinned interpreter
  (skill-coder).
- **Tests** are `tests/scenarios.md` (prompts and expected behaviour), `tests/eval-procedure.md`, and `tests/test_package_contract.py`, which runs the check below.

## The pack contract check

`scripts/skills/skill_pack_check.py PACK [--strict]` is read-only. Errors fail it: SKILL.md missing, `name` not equal to the folder, no or over-long `description`, no role, routing or write-back
section, a SKILL.md link to a missing file, a `references/` file SKILL.md does not link, a missing `evolution-and-write-back.md`, `sources.yaml`, `compatibility.yaml` or `tests/scenarios.md`, an
unreplaced template placeholder, a key or credential in any authored file, and a script with no header, catalogue row or test. Warnings are reported and fail only with `--strict`: a `TODO(build)`
marker, a `planned` tool row, a missing governance file, fewer than five scenarios, a reference without a header, SKILL.md over budget. A pack's contract test calls `check_pack`, so one definition
holds every pack.

## Install, registry and closeout

- Install by symlink, never by copy: `ln -sfn <canonical folder> ~/.claude/skills/<name>`, and the same for `~/.codex/skills` and `~/.hermes/skills/domain` (`just mirror-skills` links Continue). Audit
  for copies as `skills_stuff/.agents/skill-surfaces.md` describes.
- Registry: add the row to `skills_stuff/.agents/skill-surfaces.md` and `skills.md`; a project area's `skills.md` is checked with `just skills-registry`. A slash alias and a "Shared tools and skills"
  line are the operator's to approve.
- Closeout: CHANGELOG `## Unreleased` line, commit in `skills_stuff`, and this capability's own write-back (a Learned entry here or a template fix) when the build taught something reusable.

## Boundaries

The scaffold never installs, commits, pushes or edits another pack. It writes only inside the new pack folder and `pending_skills/`. A seed is a design brief, not a source of truth for the finished
pack: once the pack exists its references and `sources.yaml` are the truth and the seed stays outside it. A shared pack holds no project, customer or people names: write each lesson in
generic terms in the pack, list the names that must not appear in `forbidden_terms` (the scaffold refuses on a match; the seed itself stays in `pending_skills/` and may name them), and keep project-specific detail in the engaging project or the pack's `operator/` layer (the scaffold refuses on a match).

## Lessons built in

> **Learned 2026-11-12** · new-skill · USER_STATED · Source: operator, 2026-11-12 · Falsifier: a new pack built from the seed still drifts from the five model packs
> A new pack starts from a written seed and a shared scaffold, not from a copy of a sibling, so the lessons of the engagement are kept and the shape stays the same.

> **Learned 2026-11-12** · pack standard · VERIFIED_PRIMARY · Source: skill-nautobot, skill-vagrant, skill-coder, skill-network-architect, skill-systems-architect SKILL.md and layout · Falsifier: a model pack without a write-back contract or routing table
> The shared shape is the SKILL.md sections above plus `references/`, `sources.yaml`, `compatibility.yaml`, `tests/` and a catalogued script set; the scaffold and the check encode exactly that.
