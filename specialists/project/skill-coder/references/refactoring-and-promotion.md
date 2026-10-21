---
Title: Refactoring and promotion
Category: reference
Status: current
Authority: local-supplement
Scope: Changing structure without changing behaviour, moving code with shims, and promoting project code into a reusable skill
Last reviewed: 2026-10-19
Summary: >-
  A refactor changes no behaviour and proves it with a before-and-after comparison; moved code leaves a shim and a
  moved-paths entry; scripts carry a promotion status and reusable ones move to a skill as a tested engine behind a thin wrapper.
---

# Refactoring and promotion

## Contents

- [Refactoring](#refactoring)
- [Moving code](#moving-code)
- [Promotion](#promotion)

## Refactoring

Martin Fowler defines a refactoring as "a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior"
(VERIFIED_PRIMARY). So:

- A refactor changes no behaviour and carries a characterisation comparison: the same inputs, run before and after, give the same output (byte-identical where the output is text). Why: "it still
  passes the tests" is weak when tests are thin.
- A behaviour change is a separate change, named and tested. Why: mixing the two hides the behaviour change inside a large diff.
- Refactor in small steps, each one green. Why: a failing step is cheap to find.
- Use the read-only or dry-run mode of the program for the comparison. Why: it exercises the real path without writing.

## Moving code

When a module or script moves:

1. Leave a shim at the old path that imports or calls the new one, so existing callers keep working.
2. Add an entry to a moved-paths record (old path, new path, date) that a check reads.
3. Update every string reference too: path literals passed to runners, scheduler wrappers, usage lines in docstrings, task-runner recipes and documentation. Why: an import check and a faked subprocess
   test do not see string paths (a governed project's staleness audit, 2026-10-05).
4. Remove the shim and the entry when no caller remains.

## Promotion

Code grows in the projects that use it and moves to a shared skill when it has earned it. The global policy says every script judged likely to be reused is promoted, in the same session, without being
asked (operator, 2026-10-07).

**The register.** A project keeps a register of its scripts, each with one status:

| Status         | Meaning                                                   |
| -------------- | --------------------------------------------------------- |
| `project_only` | Depends on this project; stays here (one line saying why) |
| `candidate`    | Could be reused; names what it still needs                |
| `promoted`     | Moved to a skill; the project keeps a thin wrapper        |

**When to promote.** The behaviour holds for any deployment, it imports nothing project-specific, and its engine can be pure or read-only with I/O injected by the caller.

**How.**

1. The engine goes to the skill's `scripts/` with generic inputs, offline tests, a docstring header, an entry in that folder's README and a task-runner recipe.
2. The project script becomes a thin wrapper that keeps its command line and defaults and loads the engine through one seam (one module that knows where the skill lives). Why: one place to change when
   the skill moves or its revision pin changes.
3. Before-and-after outputs of the read-only or dry-run modes must match. Why: promotion is a refactor.
4. A write path is tested offline with recorded responses and live only on a disposable instance.
5. The skill's change log names the source project and script; the project's register flips to `promoted`.
6. If no skill fits, promote into the project's own shared `scripts/` the same way. A scratchpad copy is not durable.

Engines a project imports run in the project's interpreter and the project pins the skill revision; see [runtime-boundaries.md](runtime-boundaries.md).

> **Learned 2026-10-20** · adopting `code-map.toml` in a project with its own checks · VERIFIED_PRIMARY (unified-network-controller: layers, 13
> write-gate exceptions, 11 write patterns and 198 module statuses moved; equality asserted against the old files; `just check` 8,699 to 8,701 checks
> pass; four negative cases each fail) · Source: unified-network-controller `scripts/govcheck/config.py`, `code-map.toml` (2026-10-20) · Falsifier: a
> project whose old register cannot be expressed in the map's sections without loss
> Move the decisions, keep the project's checks: the project's checker reads the map instead of its constants, and calls `code_map.load` once so an
> unknown section fails. Generate the map from the old sources and assert equality before deleting them; write the full write-pattern list
> (`write_patterns` plus `apply_pattern`) so this pack's `write_gates.py` sees the same writes; record each retired path in the project's
> moved-paths map so dated records still resolve. Baselines and progress trackers stay out (decisions only).
>
> ```python
> # unified-network-controller scripts/govcheck/config.py (2026-10-20, commit 9970c48)
> CODE_MAP_FILE = ROOT / "code-map.toml"
> CODE_MAP: dict = tomllib.loads(CODE_MAP_FILE.read_text(encoding="utf-8"))
> WRITE_PATTERN = re.compile("|".join(CODE_MAP["write_gates"]["write_patterns"]))
> APPLY_FLAG = re.compile(CODE_MAP["write_gates"]["apply_pattern"])
> WRITE_GATES: dict[str, str] = dict(CODE_MAP["write_gates"].get("exceptions", {}))
> ```

> **Learned 2026-10-20 (b)** · moving modules into packages and a folder up a level, Python with a framework that imports by name ·
> VERIFIED_PRIMARY (two moves in one project, each deployed) · Source: unified-network-controller decisions A-21 and A-22 (commits af71572,
> e4a92af, 03e4a8e) · Falsifier: a move proved by these steps that still breaks a caller
> Prove a move unchanged on four counts, each run before and after: the test count and result; the rendered outputs byte for byte, the
> "before" rendered from HEAD in a `git worktree` so the comparison needs no stash; the built artefact importing every module in its real
> runtime; the closing check. Write the rewrite as one script that maps old to new once and runs once: a second pass is not idempotent when
> a new name contains an old one (`drift.py` into package `drift/` turned `unc_ownership.drift.network` into `.drift.drift.network`), and a
> half-run leaves a mixed tree, so reset to HEAD and rerun rather than repair. Search separately for what a text rewrite cannot see: names
> built at run time (`f"from {pkg}.ownership import"`), paths climbed from `__file__` (`parents[2] / "nautobot"` needs one more level), a
> packaging list kept by hand, and anything a framework keys by module path (Nautobot Jobs). A dated record keeps its old paths; map a moved
> folder once by prefix rather than every file:
>
> ```python
> def _moved_exists(tok, moved):                 # govcheck paths.py (e4a92af): exact entries first, then a moved folder's prefix
>     if tok in moved:
>         return (ROOT / moved[tok]).exists()
>     return any(tok.startswith(old + "/") and (ROOT / new / tok[len(old) + 1:]).exists() for old, new in moved.items())
> ```
>
> No visual surface.

> **Learned 2026-10-21** · promoting a project script into a skill and switching the project to it · VERIFIED_PRIMARY · Source: skill-ai-it
> `scripts/target_map.py`, `scripts/plan_timeline.py` and unified-network-controller `scripts/govcheck/skill_scripts.py` (commit pending) ·
> Falsifier: a promoted script whose pilot output changes, or a project check that imports a skill module by bare name and gets its own file
> Promote in three moves and prove each: (1) replace `ROOT = Path(__file__).parents[N]` with a `--project-root` argument and pass the root into
> every entry point; (2) move every project-shaped string (headers, an explanatory sentence, a data path) into the project's data with the pilot's
> value, and render new behaviour only when it is used, so the pilot renders byte for byte (compare old and new scripts on the same inputs, several
> dates for anything clock-driven); (3) in the project's checks, load the skill script by path under a prefixed module name rather than inserting
> the skill's folder on `sys.path`, where its module names can shadow the project's. Delete the project copy only after the recipes and checks run
> the skill copy and the rendered files are unchanged.

```python
# unified-network-controller scripts/govcheck/skill_scripts.py (commit pending)
key = f"ai_it_{name}"
spec = importlib.util.spec_from_file_location(key, AI_IT_SCRIPTS / f"{name}.py")
module = importlib.util.module_from_spec(spec)
sys.modules[key] = module   # dataclasses resolve annotations through sys.modules
spec.loader.exec_module(module)
```

> **Learned 2026-10-21 (b)** · moving definitions out of a file · VERIFIED_PRIMARY (unified-network-controller code architecture stage 2: the T6
> measure read `adapters/protocol.py` by path and would have gone on passing while checking none of the moved records) · Source:
> unified-network-controller `adapters/t6/measure.py` and `src/unc/core/records/observation.py` (2026-10-21, uncommitted at writing) ·
> Falsifier: a move after which every by-path reader was found by the import graph alone
> Before moving definitions out of a file, find its readers by path as well as its importers: AST scanners, line counters, docstring
> baselines and checks that open the file. An import graph shows only importers; a by-path reader keeps passing on the shim and silently
> checks less. Grep for the file's path and name, point each reader at both files (or the new one), and compare its output before and after.

