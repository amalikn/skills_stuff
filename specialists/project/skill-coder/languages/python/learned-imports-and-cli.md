---
Title: python override - learned imports and command lines
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/python.md (split from learned-other.md 2026-11-27): sibling imports, -I, argparse docstrings, ssh arguments, justfile exports
Last reviewed: 2026-11-27
Summary: How a Python script finds its sibling modules, takes its CLI text and receives its arguments and environment from ssh and just.
---

# python: learned imports and command lines

Part of [python.md](../python.md). Moved from [learned-other.md](learned-other.md) when it passed its budget (2026-11-27).

> **Learned 2026-11-12** · Python, scripts and tests that import a sibling module · VERIFIED_PRIMARY (the editor reported three unresolved imports after a `sys.path.insert`; none after the change) ·
> Source: skill-ai-it `tests/test_new_skill.py` `load()` and `scripts/skills/new_skill.py` @ d3132c2 · Falsifier: an editor that resolves a `sys.path.insert` import, or a name collision the path load does not avoid.
> Load a sibling module by its file path with `importlib.util.spec_from_file_location`, and register it in `sys.modules` so modules that import each other resolve. A `sys.path.insert` before the import works at
> run time but leaves the editor's language server with unresolved-import warnings, and a stem such as `json` or `new` can shadow another module. This is the form the pack's older tests already use.
>
> ```python
> def load(name: str):
>   spec = importlib.util.spec_from_file_location(name, SKILLS / f"{name}.py")
>   module = importlib.util.module_from_spec(spec)
>   sys.modules[name] = module
>   spec.loader.exec_module(module)
>   return module
> ```

> **Learned 2026-11-19** · Python, a CLI that takes its argparse description from the module docstring · VERIFIED_PRIMARY (pyright reported `"splitlines" is not a known attribute of "None"`
> in the editor; 0 errors after the change, and `python3 -OO` prints `--help`) · Source: skills_stuff `specialists/project/skill-smc/scripts/ansible/smc_inventory_add.py` @ 57816c98 · Falsifier: a
> type checker that types a module's `__doc__` as `str`, or `python -OO` keeping docstrings.
> `__doc__` is `str | None`: `python -OO` strips docstrings and a module may have none, so `__doc__.splitlines()[0]` fails the type check and crashes under `-OO`. Give it a fallback in place.
>
> ```python
> p = argparse.ArgumentParser(description=(__doc__ or "Add one new SMC to an ansible-wifi inventory.").splitlines()[0])
> ```

> **Learned 2026-11-26** · `python3 -I script.py` and a sibling import · VERIFIED_PRIMARY (operator run: `ModuleNotFoundError: No module named 'stack_target'`
> from `just keycloak-finish-user`; a sibling script with a `sys.path.insert` worked) · Source: continuum-app `scripts/dev-stack/keycloak_finish_user.py` (0e98d70) ·
> Falsifier: a Python release whose `-I` keeps the script's folder on `sys.path`. Isolated mode (`-I`, which implies `-P`/safe path) leaves the script's own folder
> off `sys.path`, so `import sibling` fails although it works under plain `python3`. A script meant to run with `-I` puts its folder back first (or loads the
> sibling by file path, the entry above). A test that pre-sets `sys.path` before importing the script hides the bug: smoke-run the real command line.
> ```python
> sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python -I leaves the script's folder off sys.path
> import stack_target as target  # noqa: E402
> ```

> **Learned 2026-11-26 (b)** · arguments after `ssh host` are joined into one remote command line · VERIFIED_PRIMARY (psql printed `extra command-line
> argument "platform," ignored` for each word of a `-c` query; fixed by quoting) · Source: continuum-app `scripts/dev-stack/stack_target.py` `nas_psql`,
> `test_stack_target.py` (0e98d70; the test fails when the join is unquoted) · Falsifier: an ssh that passes argv through unjoined. `subprocess.run(["ssh", host,
> "psql", "-c", "SELECT a, b FROM t"])` is not an argv on the far side: ssh concatenates the words with spaces and the remote shell splits them again, so a
> query with spaces or quotes arrives broken. Quote the remote part once with `shlex.join`; a prefix list that callers extend (`[*psql_argv(), "-c", q]`) cannot
> quote what is appended later, so route it through a local wrapper that quotes its own argv.
> ```python
> os.execvp("ssh", [*NAS_SSH, NAS_VM, shlex.join([*NAS_PSQL, *args])])   # one quoted remote command line
> ```

> **Learned 2026-11-26 (c)** · a justfile `export` beats a script's "env var first" fallback · VERIFIED_PRIMARY (`CONTINUUM_TARGET=nas just keycloak-bootstrap-user`
> went to `http://localhost:18080`: the justfile's `export KEYCLOAK_URL := env("KEYCLOAK_URL", "http://localhost:" + KC_PORT)` reached the script) · Source:
> continuum-app `scripts/dev-stack/keycloak_bootstrap_user.py` (b3a3772) · Falsifier: a just release that does not pass `export`ed variables to recipes. A script
> written as `os.environ.get("X") or <per-target default>` treats an exported default as an operator override, so a recipe can never reach the other target.
> Honour the override only where it was meant (the dev target), or name it differently from what the justfile exports; check with `just --evaluate X`.
> ```python
> BASE = target.admin_base() if target.NAME == "nas" else (os.environ.get("KEYCLOAK_URL") if target.NAME == "dev" else "") or target.KEYCLOAK
> ```
