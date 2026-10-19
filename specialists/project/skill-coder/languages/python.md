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

| Core reference              | In Python                                                                                                                                                              |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| documentation-and-headers   | Module docstring with purpose and `Usage:`; Google-style `Args:`, `Returns:`, `Raises:` (and `Yields:` for generators); triple double quotes and a one-line summary    |
|                             |   (PEP 257)                                                                                                                                                            |
| design-principles           | Interfaces are `typing.Protocol` (structural, so a fake needs no base class); records are frozen dataclasses with `to_dict`/`from_dict`; third-party validation models |
|                             |   (Pydantic) only at the API edge                                                                                                                                      |
| errors-and-timeouts         | A project error base class with subclasses; `raise ... from err` to chain; no bare `except:` (PEP 8: it catches `SystemExit` and `KeyboardInterrupt`);                 |
|                             |   `subprocess.run([...], timeout=s, check=True)` raises `TimeoutExpired` or `CalledProcessError`; HTTP clients get an explicit timeout                                 |
| safety-and-writes           | `argparse` with `--apply` defaulting to false; the write path checks it in the writer, not the CLI                                                                     |
| configuration-and-literals  | One settings module reads `os.environ`; `pathlib.Path` relative to a root from settings                                                                                |
| security                    | Argument lists, never `shell=True` with input; DB-API placeholders; `yaml.safe_load`; `secrets` module for tokens                                                      |
| testing                     | pytest `tmp_path` and `monkeypatch` style isolation; recorded fixtures under `tests/fixtures/`; no network in unit tests                                               |
| runtime-boundaries          | Helpers parse with `ast.parse(source, feature_version=(3, 11))` style calls (UNVERIFIED: the `ast` docs were not fetched) and never import the target; a `SyntaxError` is reported                                   |
| documentation-and-headers   | Never `# noqa`; fix the cause or configure the rule in `pyproject.toml` with a comment                                                                                 |
|   (suppression)             |                                                                                                                                                                        |

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
