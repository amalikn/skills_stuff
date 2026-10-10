---
Title: skill-ai-it reference: Script and task inventory
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Script and task inventory; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Script and task inventory

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

## Contents

- [Script and task inventory](#script-and-task-inventory)

### Script and task inventory

When a target project contains scripts or automation, help agents identify runnable entrypoints, purpose, inputs, outputs, side effects, and safety.

Primary executable source of truth — detection order:

1. `justfile` / `Justfile`
2. `Taskfile.yml`
3. `Makefile`
4. `package.json` scripts
5. raw scripts under `scripts/`
6. `.github/workflows/`, `ansible/`, `playbooks/` (CI/ops runners)

Human/agent-readable operational catalog:

- `scripts/README.md`

Preferred source template:

- `templates/scripts-README.md`

Audit reference: `patterns/script-task-audit-checklist.md`.

#### Mode behavior

- `bootstrap`: if the target has scripts, tasks, or automation files, create or update `scripts/README.md`. If no canonical task runner exists but scripts/automation are present, prefer creating
  `justfile` from `templates/justfile` as the lightweight task catalog. Do not create empty task scaffolding when no scripts/tasks exist.

- `navigation-add`: add navigation pointers to the existing canonical runner first. If a `justfile` exists, route agents to `just --list` then `scripts/README.md`.
- `refresh`: create `scripts/README.md` from `templates/scripts-README.md` if scripts or tasks exist and the file is missing. If the file exists, update managed inventory blocks only. Do not overwrite
  manually written script descriptions. If drift exists between the task runner and `scripts/README.md`, report or propose updates.

- `audit`: report scripts missing from `scripts/README.md`, tasks missing descriptions, cataloged scripts that no longer exist, raw scripts not represented in `scripts/README.md`, and potentially
  unsafe scripts without safety notes.

- `promote`: promote only stable, durable operational procedures to Archcore. Do not promote every script automatically.

#### Task safety labels

Use these labels in `scripts/README.md` and when reporting script/task safety:

- `safe`
- `review-required`
- `destructive`
- `external-network`
- `modifies-files`
- `requires-secrets`
- `requires-credentials`
- `long-running`
- `unknown`

Treat `unknown` as not safe until inspected.

Agents must prefer cataloged tasks over raw script execution. Prefer `just <task>` when a `justfile` exists. Do not run destructive, review-required, or unknown-safety tasks without review.

#### Runtime isolation — recipes must not call a bare interpreter

**A generated `justfile` never calls bare `python3`, `node`, `npx`, or `ruby`.** A bare interpreter resolves to whatever the host has on `PATH`, which is not what the project's `.mise.toml` pins.

This is the failure mode that makes it worth a rule rather than a preference: **it works.** A recipe calling bare `python3` runs correctly on the machine it was written on, passes every check, and
keeps working until the host's Homebrew updates or the operator switches machines — at which point it fails somewhere inside a script, reading like a code bug rather than an environment one. Observed
2026-08-25: a freshly bootstrapped project pinned Python 3.14 and Node 26 in `.mise.toml` while every recipe silently used Homebrew's 3.14.7 and Node 26.7.0. Nothing in the project could detect it.

**`mise exec -- python` is not the fix either.** This is the half-measure that looks correct and is the more common failure in practice, because it *works*. Where `.mise.toml` sets `_.python.venv`,
`mise exec -- python` does resolve to the venv — so it tests clean and reads as pinned. But the dependency is **implicit**: nothing at the call site names the interpreter, and if the activation stops
applying — the `[env]` block is edited, the venv is absent, the recipe is copied into a project without that config — it degrades **silently to the host interpreter** rather than failing. Address the
interpreter by **path** through `{{py}}` and depend on `_require-venv`, so the failure mode is a loud error with a fix attached instead of a wrong-interpreter run that looks fine. Observed 2026-09-01:
an Agent Stack justfile used `mise exec -- python` throughout and resolved correctly, while its `.mise.toml` simultaneously pointed the venv *inside the repo* — the implicit form made both the pinning
and the violation invisible at every call site.

Apply the same reasoning to `mise run` tasks in `.mise.toml`: give them the absolute venv path too, or they become a second, divergent resolution path beside the justfile.

Node has no venv layer, so `mise exec -- node` **is** the explicit form for it. The distinction applies wherever a venv sits between mise and the interpreter — in practice, Python.

**Generate these together, or none of them works:**

1. **`.mise.toml` in the project**, pinning every runtime the recipes use. Pin **Node as well as Python** when any recipe shells out to a JS tool — pinning only Python leaves `mise exec -- node`
   falling through to the host, which looks pinned and is not.

2. **Interpreter variables at the top of the `justfile`**, and every recipe going through them:

   ```just
   wc := "<the working-cache peer for this project>"
   py := wc + "/.venv/bin/python"
ai_it := "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it"
   nd := "mise exec -- node"
   ```

3. **A `_require-venv` guard that every Python recipe depends on**, so a missing venv fails with a rebuild instruction instead of silently falling back to the host — which is the same defect wearing a
   different hat.

4. **Scripts never choose their own interpreter either.** Two ways a recipe that names no interpreter still gets the host one:
   - **A script run by path** (`scripts/check.py`, `./tool.js`): its shebang (`#!/usr/bin/env python3`) resolves on `PATH`. Write `{{py}} scripts/check.py`. The shebang stays for a direct run; the
     recipe must not rely on it.
   - **A shell script that calls the interpreter inline** (`... | python3 -c`, `python3 - <<EOF`): the recipe pins nothing it runs. The script takes the interpreter from a variable with a host
     default, `py=${PROJ_PY:-python3}` then `"$py"`, and the recipe passes it: `PROJ_PY={{py}} scripts/x.sh`. A Python wrapper that calls such a script passes its own `sys.executable` on. A line whose
     interpreter runs on another host (`ssh host python3 ...`) is not a local runtime: mark it `# runtime: remote`.

`check_interpreter_pinning` in `templates/check_governance.py` fails on both (since 2026-10-07), as it does on a bare interpreter name in a recipe.

#### File and command naming — snake_case

Governance `categories/coding-guide.md` (operator, 2026-10-07): **snake_case** for every code file this skill generates or finds (`.py`, `.sh` and the rest) and every command name a project defines
(`just` recipes, CLI symlinks). A Python file must be importable (PEP 8; a hyphen is the minus operator), the Google Shell Style Guide asks the same of shell, and one rule beats a per-language split.
kebab-case only where something outside the code fixes it: skill names, document slugs (`<slug>-YYYYMMDD_hhmm.md`), repo and folder names. `check_file_naming` in `templates/check_governance.py` fails
on a kebab-case code file under `scripts/`; a project adopting the rule lists its existing ones in `KEBAB_LEGACY` and renames each when next touched, updating every reference in the same change. This
package's own optional template is `templates/context_preflight.sh` (renamed from the kebab form). The template's own recipes follow it since 2026-10-07 (`nav_upgrade`, `nav_validate`, `lint_md` and
the rest); `nav_upgrade` renames the old kebab forms in a project's justfile on its next run.

#### Function documentation

Every function a project's scripts define carries a docstring (Python) or a comment block directly above it (shell): a summary line, then the reasoning and the failure behaviour where they are not
obvious, with section banners in longer files. The reference style is ansible-wifi's `roles/smc_rise_watchdog/templates/rise_watchdog.py.j2`. `check_function_docs` in `templates/check_governance.py`
fails on an undocumented one, including Python embedded as a string constant (code shipped to another host), so the template's own functions are documented too (operator, 2026-10-07).

Also generate `just bootstrap` (builds the venv from the mise pins; safe to re-run) and `just runtimes` (prints the resolved interpreters). `runtimes` is the one that makes the invariant *observable*
— without it, "the recipes use the pinned runtime" is an assumption nobody can check in under a minute.

**The venv lives in the working-cache peer, never in the repo.** A repo carries source and evidence; a venv is rebuildable runtime, and mixing them puts a large disposable tree in the same history as
the durable one. Derive the peer path from the source root:

| Source root                        | Working-cache peer                         | Project depth |
| ---------------------------------- | ------------------------------------------ | ------------- |
| `project_stuff/<group>/<project>/` | `project-working-cache/<group>/<project>/` | 2             |
| `mcp_stuff/<project>/`             | `mcp-working-cache/<project>/`             | 1             |
| `skills_stuff/<project>/`          | `skills-working-cache/<project>/`          | 1             |
| `tools_stuff/<project>/`           | `tools-working-cache/<project>/`           | 1             |

For a track nested below that depth (`project_stuff/me/uae/atar/`), extend the peer path to match the track (`project-working-cache/me/uae/atar/`) so the venv sits beside the bytecode cache the
`usercustomize.py` router already writes there.

**`uv run` is not the primary path.** It resolves its own interpreter independently of mise — tested 2026-08-25, `uv run python3` selected Homebrew's 3.14.7 while mise pinned 3.14.5 — so it is the
same class of drift, not a fix for it. Use `uv run --with <pkg>` only where a recipe needs throwaway third-party packages and the exact patch version genuinely does not matter; say so in a comment
where you do.

**Do not add a `.python-version` file alongside `.mise.toml`.** Two files stating the version is two places for it to drift. `.mise.toml` owns the pin.

**Declare third-party dependencies in `requirements.txt`, and have `bootstrap` install them.** Pinning the interpreter without declaring the packages does not remove the hidden host dependency — it
relocates it, and the failure arrives later and reads worse. This is not hypothetical: the moment the 2026-08-25 project switched off the host interpreter, `just nav_validate` failed on a missing
PyYAML that had been supplied invisibly by Homebrew's Python for the whole session. Nothing had ever declared it.

Keep the project's **own** scripts stdlib-only where you can, and say so in the file. The governance gate in particular must never fail for environment reasons — a check that cannot run is
indistinguishable from a check that passes, and it is the one thing you cannot afford to be ambiguous. `requirements.txt` then covers only what the project calls *out* to.

#### justfile — embedded fallback

If `templates/justfile` is unavailable, write the justfile from this embedded fallback and adapt it to the project:

```just
# just task catalog for this project.
# Usage: just --list | just <task>
#
# Recipes go through {{py}} / {{nd}}, never a bare interpreter — see "Runtime isolation" above.

set dotenv-load := false

wc := "<working-cache peer for this project>"
py := wc + "/.venv/bin/python"
nd := "mise exec -- node"

# List available tasks
default:
    @just --list

# Build the working-cache venv from the mise-pinned runtimes. Safe to re-run.
bootstrap:
    @mkdir -p "{{wc}}"
    @test -f "{{wc}}/.mise.toml" || cp .mise.toml "{{wc}}/.mise.toml"
    @cd "{{wc}}" && mise install && mise exec -- python -m venv .venv
    @test -f requirements.txt && {{py}} -m pip install --quiet --upgrade pip -r requirements.txt || true
    @{{py}} -c "import sys; print('venv ready:', sys.version.split()[0], sys.executable)"

# Fail early rather than falling back to the host interpreter
_require-venv:
    @test -x "{{py}}" || { echo "venv missing at {{py}} — run: just bootstrap" >&2; exit 1; }

# Report which runtimes the recipes will actually use
runtimes:
    @printf 'python  '; {{py}} -c "import sys; print(sys.version.split()[0], sys.executable)" 2>/dev/null || echo "MISSING — run: just bootstrap"
    @printf 'node    '; {{nd}} --version 2>/dev/null || echo "MISSING — pin node in .mise.toml"

# Audit script/task inventory for drift
audit_scripts:
    @echo "== just recipes =="; just --list || true
    @echo; echo "== script files =="; find scripts -maxdepth 2 -type f 2>/dev/null | sort || true

# Governance coherence checks — must exit 0 before durable work is called complete
check: _require-venv
    @{{py}} scripts/check_governance.py
    @{{py}} "{{ai_it}}/scripts/doc_freshness.py" --project-root . --check

# Session preflight: list stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only.
stale: _require-venv
    @{{py}} "{{ai_it}}/scripts/doc_freshness.py" --project-root .

# Run safe local preflight checks
preflight: runtimes audit_scripts check

# Lint Markdown files when markdownlint-cli2 is available
lint_md:
    @command -v markdownlint-cli2 >/dev/null || { echo 'markdownlint-cli2 not installed; skipped'; exit 0; }
    @markdownlint-cli2 '**/*.md'
```

Add project-specific tasks by inspecting `scripts/` and adapting to the discovered pipeline.
