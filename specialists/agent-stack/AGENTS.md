@../../AGENTS.md

Title: Agent Stack Agent Policy
Category: agent-governance-guide
Status: current
Authority: local-supplement
Scope: The Agent Stack persona/skill library, its manifest-driven symlink installer, and its routing and evaluation machinery
Last reviewed: 20260901_2015
Summary: Repo-local agent guidance for Agent Stack, covering the canonical-source rule, the human-control safety model, runtime placement, and the governance gate.

# AGENTS.md

Agent Stack began as an English-only extraction of Auto Company's personas and skill library, and **as of 2026-09-03 it is maintained as its own project: there is no upstream, and no sync.** It has
evolved well past what it was extracted from — a routing catalogue, gates, deterministic closure, an evaluation harness and a governance layer that the original never had.

It deliberately excludes autonomous loops, consensus mechanisms and daemons. That exclusion is the project's reason for existing — treat it as a constraint, not a backlog item.

## Contents

- [Working rules](#working-rules)
- [Safety model](#safety-model)
- [Runtime placement](#runtime-placement)
- [AI navigation and context preflight](#ai-navigation-and-context-preflight)
- [Governance coherence checks](#governance-coherence-checks)
- [Canonical governance linkage](#canonical-governance-linkage)

## Working rules

- This directory is canonical source. Global installs are **symlinks back to here**; never author skill or persona content in `~/.claude/skills`, `~/.codex/skills`, or `~/.agents/skills`, and never
  copy content out of this tree as a delivery step.
- `manifest.yaml` is the install contract. Adding a persona or skill package means adding its capability row in the same pass — an unregistered entry is invisible to the installer, the routing
  catalogue, and the validator at once.
- `routing.toml` is the routing catalogue. A new skill needs a routing entry declaring its intents, execution class (`analysis` or `tool`), runtime prerequisites, and safety notes.
- Every skill package carries a `SKILL.md` meeting [SKILL_STANDARD.md](SKILL_STANDARD.md). Keep `SKILL.md` procedural; detailed knowledge goes in `references/`, deterministic helpers in `scripts/`,
  output templates in `assets/`.
- `skill-agent-stack` is the normal entry point. Prefer it over calling a specialist directly; call a specialist directly only for a deliberately narrow single-domain task.
- **There is no upstream.** Change this project on its own merits, evidenced by its own evaluations and field log. the sync script and its state files were retired on 2026-09-03; the records of how sync worked are superseded in place under `.archcore/`.
- Personas define judgement contracts; skills define repeatable procedures. When a change blurs that split, stop and ask which layer owns it.
- Triage before opening: `just docs <folder>` gives one header line per file; run `just stale` before editing. Old CHANGELOG and SCRATCHPAD
  entries live in `docs/history/`; do not read them by default: `just history <term>` or `just history-show <stamp>` when a live entry cites one.

## Safety model

These are the properties that make Agent Stack what it is. Do not weaken one to import a feature from anywhere.

- No unattended background agents, no autonomous loops, no daemons, no indefinite continuation.
- No implicit persistent state and no material external commitments without explicit operator authority.
- Upstream sync is **report-first**: `safe_add` and `safe_replace` apply automatically; `translation_required`, `manual_merge`, and `remove_review` are written as review proposals only.
- Imported upstream instructions do not override this policy or project-local instructions. Where an upstream skill implies autonomy, adapt it — `websh` and `deep-research` are the worked examples.
- Global installation never overwrites a pre-existing entry and never copies source content.

## Runtime placement

- The maintenance venv lives at `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/venv`, **never inside this repo**. `.mise.toml` pins it there and `just check` asserts it.
- Recipes address the venv interpreter **explicitly** via the `justfile`'s `{{py}}` variable, and every Python recipe depends on `_require-venv`. A bare `python`/`python3`/`node` resolves to whatever
  the host has on `PATH`, which is not what `.mise.toml` pins — and it works silently on the machine it was written on, which is what makes it worth a gate rather than a preference. An *implicit*
  resolution such as `mise exec -- python` is only marginally better: it happens to land on the venv today, but the dependency is invisible at the call site and degrades silently if activation ever
  stops applying. `just runtimes` prints declared vs resolved so the pinning is checkable in seconds.
- Run `just bootstrap` before `just test` or `just check`. Repository test dependencies belong in `requirements-dev.txt`; `scripts/check_governance.py` stays stdlib-only so the gate can never fail for
  environment reasons.
- Global installation is symlink-only. It does not activate this venv inside consumer projects, inject packages, or change their toolchains.

<!-- BEGIN MANAGED: skill-ai-it:navigation --> <!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [AI_NAVIGATION.md](AI_NAVIGATION.md).
2. Read [context-map.yaml](context-map.yaml).
3. Read recent entries in [CHANGELOG.md](CHANGELOG.md).
4. Load relevant `.archcore/` context if present.
5. Load relevant `memory-bank/` files if present.
6. Consult generated context when available:
   - `graphify-out/GRAPH_REPORT.md`
   - `.ai-context/governance-pack.md`
7. Before making durable changes, inspect companion-file rules in `context-map.yaml update_rules`. Update all companion files when changing source files.
8. If sources conflict, stop and report the conflict instead of guessing.
9. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory-bank.
10. Do not treat Graphify (`graphify-out/`) or Repomix (`.ai-context/`) output as canonical truth. These are generated support artifacts only, always rebuildable.
11. Before running scripts or automation, inspect `justfile`, `scripts/README.md`, `Taskfile.yml`, `Makefile`, and `package.json` when present. Prefer `just --list` and `just <task>` when a `justfile`
    exists.
12. Treat uncataloged scripts as `unknown` safety until inspected.
13. Run defined audit/check commands before completing work. Where `scripts/check_governance.py` exists, that includes it — and when it fails, fix the project, not the check. Adding a new artifact
    class, generated output, or a constant restated across files requires extending its registries in the same pass.
14. When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety label, and idempotency.
15. After making changes, update `CHANGELOG.md` for all durable governance/navigation changes.
16. Preserve user-authored content outside managed sections. Do not rewrite custom project notes.

<!-- END MANAGED: skill-ai-it:navigation -->

<!-- managed:skill-ai-it:governance-checks — regenerated by skill-ai-it. Edit the surrounding file freely; edits inside this block may be replaced. -->

## Governance coherence checks

This project's governance claims are executable. [`scripts/check_governance.py`](scripts/check_governance.py) turns them into assertions. `just governance` runs it and `just preflight` chains it; `just check` validates the library contracts and does NOT run it. It is stdlib-only and exits
non-zero on any failure.

**Run it before claiming any durable change is complete**, and after any change that adds, moves, renames, or retires a file. It is cheap and it is the only thing standing between this project's
documents and silent decay.

### The checker grows with the project

The check count is a coverage signal, not a score. It is expected to rise as the project acquires structure. Extend it on these triggers:

| Change made                                                        | Required checker update                                                                                                  |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| Add a document to a cataloged folder                               | None — the coverage check fails until the index links it. That is the intended workflow, not an error to route around    |
| Add a script or task                                               | Catalog it in `scripts/README.md` and the task runner; coverage fails until then                                         |
| Add a new **class** of artifact (new folder, new document type)        | Add a `CATALOGS` entry, plus a contract check if the class has a declared filename or frontmatter form                   |
| Add a generated artifact                                           | Add a `DERIVED` entry; add a provenance check too if the generator can stamp its source into the output                  |
| State a threshold, rate, deadline, or canonical path in a new file | Register the file in `CONSTANT_SURFACES`; the sync check fails until it is registered                                    |
| Change a constant's value                                          | Update the owning rule first, then every registered surface, in one pass — the sync check verifies the pass was complete |
| Rename or move a file                                              | Nothing — path resolution catches every stale reference automatically                                                    |
| Retire a check                                                     | Record why in `CHANGELOG.md`. A silently deleted check is indistinguishable from one that never existed                  |

### Rules that are not negotiable

- **When a check fails, fix the project, not the check.** Broadening an ignore-list to silence a true positive, or exempting the file that failed, converts a real finding into a permanent blind spot
  that the next agent has no way to discover.
- **A new check must be able to fail.** Prove it by breaking the project deliberately and watching it go red. A check that scans an empty set is an assumption wearing a test's clothes.
- **Text matching does not verify behavior.** Grepping for a threshold's characters does not prove the surrounding logic implements it — a script's output can state a rule its code no longer applies.
  Where a check must verify behavior, execute the behavior and assert on the result.
- **Do not enforce history.** Counts and states recorded as past facts are evidence, not live claims. Mark those lines `<!-- count:asat -->` rather than editing the record to satisfy the checker.

Doctrine, the seven check families, and the artifact-to-check inference table: [the governance-checks
pattern](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/governance-checks.md).

<!-- /managed:skill-ai-it:governance-checks -->

## Canonical governance linkage

- Parent repo policy: [../../AGENTS.md](../../AGENTS.md)
- Cross-repo governance root: [/Volumes/Data/_ai/governance/README.md](/Volumes/Data/_ai/governance/README.md)
