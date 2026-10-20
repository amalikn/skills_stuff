---
Title: Python override
Category: reference
Status: current
Authority: local-supplement
Scope: Python 3 scripts, packages and services
Last reviewed: 2026-10-19
Summary: >-
  PEP 8, PEP 257 and Google-style docstrings with Args, Returns and Raises; ruff for lint and format; pytest or unittest;
  subprocess.run with a timeout and an argument list; frozen dataclasses and Protocols at seams; the src layout.
---

# Python override

## Authoritative sources

PEP 8 (style), PEP 257 (docstrings), PEP 20 (the Zen of Python), the Google Python Style Guide, the Python standard library docs (`subprocess`, `venv`), the typing specification (Protocols), the
Python Packaging User Guide (src layout), ruff and pytest documentation. Copies: `../documents/research-sources-20261019/`.

## Tools

| Job             | Tool                                                                                  | Note                                                                                       |
| --------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Interpreter     | The project's pin (`.mise.toml`, `requires-python`); operator default 3.14 for        | Address by path; see core tooling                                                          |
|                 |   new work                                                                            |                                                                                            |
| Format and lint | ruff (`ruff format`, `ruff check`)                                                    | ruff's pydocstyle setting accepts `convention = "google"` (VERIFIED_PRIMARY, ruff FAQ)     |
| Types           | The project's type checker (mypy or pyright)                                          | UNVERIFIED: no source fetched; follow the project's config                                 |
| Tests           | pytest, or `unittest` where the project is stdlib-only                                | pytest fixtures with `yield` give set-up and teardown (VERIFIED_PRIMARY)                   |
| Packaging       | `pyproject.toml`; the src layout                                                      | The src layout stops tests importing the working copy by accident (VERIFIED_PRIMARY, PyPA) |
| Environment     | A venv in the working-cache peer                                                      | Not committed; not movable (VERIFIED_PRIMARY, `venv` docs)                                 |

## Core rule mapping

| Core reference                        | In Python                                                                                                                                                    |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| documentation-and-headers             | Module docstring with purpose and `Usage:`; Google-style `Args:`, `Returns:`, `Raises:` (and `Yields:` for generators); triple double quotes and a one-line  |
|                                       |   summary (PEP 257)                                                                                                                                          |
| design-principles                     | Interfaces are `typing.Protocol` (structural, so a fake needs no base class); records are frozen dataclasses with `to_dict`/`from_dict`; third-party         |
|                                       |   validation models (Pydantic) only at the API edge                                                                                                          |
| errors-and-timeouts                   | A project error base class with subclasses; `raise ... from err` to chain; no bare `except:` (PEP 8: it catches `SystemExit` and `KeyboardInterrupt`);       |
|                                       |   `subprocess.run([...], timeout=s, check=True)` raises `TimeoutExpired` or `CalledProcessError`; HTTP clients get an explicit timeout                       |
| safety-and-writes                     | `argparse` with `--apply` defaulting to false; the write path checks it in the writer, not the CLI                                                           |
| configuration-and-literals            | One settings module reads `os.environ`; `pathlib.Path` relative to a root from settings                                                                      |
| security                              | Argument lists, never `shell=True` with input; DB-API placeholders; `yaml.safe_load`; `secrets` module for tokens                                            |
| testing                               | pytest `tmp_path` and `monkeypatch` style isolation; recorded fixtures under `tests/fixtures/`; no network in unit tests                                     |
| runtime-boundaries                    | Helpers parse with `ast.parse(source, feature_version=(3, 11))` style calls (UNVERIFIED: the `ast` docs were not fetched) and never import the target; a     |
|                                       |   `SyntaxError` is reported                                                                                                                                  |
| module-and-function-shape (packages)  | A module family is a regular package (a folder with `__init__.py`, never an implicit namespace package: those merge across every path entry, so two packs'   |
|                                       |   folders of one name combine silently); relative imports inside it (`from .model import Profile`); entry points are top-level scripts or `python -m pkg`    |
|                                       |   with `__main__.py`, never a module inside the package run by path (its relative imports fail)                                                              |
| documentation-and-headers             | Never `# noqa`; fix the cause or configure the rule in `pyproject.toml` with a comment                                                                       |
|   (suppression)                       |                                                                                                                                                              |

> **Learned 2026-10-19** · python 3.14 · VERIFIED_PRIMARY · Source: /Volumes/Data/_ai/_project/project_stuff/apn/unified-network-controller/scripts/render/flows_drawio.py (thin wrapper over skill-drawio) · Falsifier: a linter that flags importlib.import_module after a sys.path change
> A module that must change `sys.path` before importing (a project's seam to a skill pack, a test putting `scripts/` on the path) loads the rest with
> `importlib.import_module(...)` and plain assignments instead of `import` statements below code: the imports stay at the top of the file, so E402 never
> fires and no `# noqa` is needed. Re-exported names are then ordinary assignments a reader can grep.

> **Learned 2026-10-19** · python 3.12+ · VERIFIED_PRIMARY · Source: scripts/import_layers.py analyse() (fan-in); tests/test_import_graph_report.py · Falsifier: a report built from set-valued edges whose tied counts keep one order under different PYTHONHASHSEED values
> `Counter.most_common()` orders equal counts by first insertion, so counts built by walking sets (an import graph's edge sets) list tied entries in
> an order that changes between runs with string hash randomisation. A report or a top-N cut that must be stable sorts by `(-count, name)` instead.

> **Learned 2026-10-20** · python 3.12+ · VERIFIED_PRIMARY · Source: unified-network-controller `scripts/checks/ata_chain_check.py` `check_site`
> (commit 5b3d4e6) · Falsifier: a ThreadPoolExecutor.map that keeps the other results when one task raises SystemExit
> `except Exception` does not catch `SystemExit`: a library helper that calls `sys.exit()` on failure (here a sweep on an unreachable host) ended a
> whole `ThreadPoolExecutor.map` over six sites and the buffered output with it. Per-item isolation catches `(Exception, SystemExit)`, and a long
> run prints with `-u` or flushes so a killed run still leaves its lines.
>
> ```python
> try:
>     alive, neigh, _leases, _path, tool = ds.sweep(node, domain, [net])
> except (Exception, SystemExit) as exc:   # sweep() exits on an unreachable SMC; one site is a result, not the end of the whole check
>     return {"site": site, "lines": [f"sweep failed: {type(exc).__name__}: {exc}"[:200]], "ok": False, "found": 0}
> ```

## Size and limit tweaks

| Item                | Value                                                                                                                  | Reason                                                |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Line length         | The project's ruff setting; PEP 8 says 79 (72 for docstrings and comments), Google says 80; the operator's projects    | Follow the project's config; do not reflow code to    |
|                     |   commonly allow longer                                                                                                |   change it                                           |
| Module and function | Core defaults (400 and 60)                                                                                             | No change                                             |

## Open items

- Type-checker recommendation and settings: UNVERIFIED stub; add with a fetched source.
- A docstring checker that enforces `Args:` completeness: ruff's pydocstyle rules check presence and sections; full parameter coverage may need the project's own ratchet check (UNVERIFIED which ruff
  rules cover it).
