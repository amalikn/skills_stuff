---
Title: python override - learned other
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/python.md (split by scripts/language_split.py)
Last reviewed: 2026-11-07
Summary: The learned other part of the python override; the entry file holds the tools and the core rule mapping.
---

# python: learned other

Part of [python.md](../python.md).

> **Learned 2026-10-20 (b)** · python, scripted edits of Python source · VERIFIED_PRIMARY (two of nine rewritten files broke: tests failed with NameError and a remote agent's CalledProcessError) · Source: unified-network-controller `wc-local/scripts/collector/dhcp_leases.py` and `wc-local/scripts/collector/reachability.py` (fixed before commit 3efcb27) · Falsifier: a source file whose embedded code strings hold no import lines
> A rewrite that places a new import "after the last import line" by matching lines also matches imports inside string literals: a remote-agent program sent over ssh (`import datetime`) or a Django
> shell script (`from swapper import load_model`). The import landed in the string, so the module failed to load and the remote program gained a line its host could not run. Find the insertion point
> from the AST, the last top-level `Import`/`ImportFrom` node of the module body:
>
> ```python
> tree = ast.parse(text)
> last = max(n.end_lineno for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom)))   # never a line inside a string
> lines.insert(last, "from unc.drivers.transports import process")
> ```

> **Learned 2026-10-21** · python 3.14 (stdlib `dataclasses`, `importlib.util`) · VERIFIED_PRIMARY (the test module failed to import: `AttributeError: 'NoneType' object has no attribute '__dict__'` in `dataclasses._is_type`) · Source: unified-network-controller `tests/test_plan_timeline.py` loading `scripts/render/plan_timeline.py` (2026-10-21) · Falsifier: a module with a `@dataclass` and
> `from __future__ import annotations` that loads by `spec_from_file_location` without a `sys.modules` entry A test that loads a script by path must register the module in `sys.modules` before
> `exec_module` when the script defines a dataclass: with postponed annotations, `dataclasses` looks the class's module up in `sys.modules` to resolve `ClassVar` and `InitVar` strings, and an
> unregistered module is `None` there.
>
> ```python
> spec = importlib.util.spec_from_file_location("plan_timeline", ROOT / "scripts/render/plan_timeline.py")
> mod = importlib.util.module_from_spec(spec)
> sys.modules["plan_timeline"] = mod   # before exec_module, or @dataclass fails at class creation
> spec.loader.exec_module(mod)
> ```

> **Learned 2026-10-22 (e)** · python, pathlib containment checks · VERIFIED_PRIMARY (a unit test failed on macOS: a target under a temporary folder read as outside the root) · Source: skill-ai-it `scripts/checks/anchor_links.py` `broken_links`, commit fdf90d0 · Falsifier: `Path.is_relative_to`
> returns True for a resolved child of an unresolved root that sits behind a symlink. Resolve both sides before `is_relative_to` (or `relative_to`): a target built with `.resolve()` follows symlinks,
> so an unresolved root such as macOS's `/var/folders/...` (really `/private/var/...`) never contains it and every file reads as outside.
>
> ```python
> root = root.resolve()  # targets are resolved, so the root must be too (macOS /var is /private/var)
> ...
> dest = (doc.parent / target).resolve() if target else doc.resolve()
> if dest.is_relative_to(root):
> ```

> **Learned 2026-10-23** · ruff 0.17.2 · VERIFIED_PRIMARY (ansible-wifi checkout, 2026-10-23) · Source: `uvx ruff config indent-width`; local-knowledge-ansible `ansible-wifi-root-governance/ruff.toml`, `roles/smc_change/files/probe/check.sh` · Falsifier: ruff formatting an
> excluded file passed by name with `force-exclude = true` Two-space Python with ruff: `indent-width = 2` (the default is 4). To apply a new style to new files only, list the existing files in
> `extend-exclude` and set `force-exclude = true`, so a hook or editor that passes an excluded file by name is still skipped (measured: the 22 tracked files reported "No Python files found"; a new
> four-space file was flagged). ruff honours git's ignore rules, including `.git/info/exclude`, so files reached through a git-excluded symlink are skipped; run from the physical path (`pwd -P`).
> Python joined from parts before it runs is linted on the joined program (names cross files) and formatted per part. A backslash inside an f-string expression is a SyntaxError before Python 3.12;
> compute it outside the f-string when the code may run on 3.10 (Ubuntu 22.04).

> **Learned 2026-10-23 (b)** · pyright/Pylance, modules joined before they run · VERIFIED_PRIMARY · Source: pyright docs "Execution Environment Options" (docs/configuration.md); ansible-wifi local-knowledge `ansible-wifi-root-governance/pyrightconfig.json` · Falsifier: an
> `executionEnvironments` entry whose diagnostic override does not change the report for files under its root Parts that a controller joins into one program (each part uses names another part defines)
> show "X is not defined" in the editor for every part. Keep the linter on the joined program as the real check, and turn the rule off for that folder only with a root `pyrightconfig.json`
> (`{"executionEnvironments": [{"root": "<folder>", "reportUndefinedVariable": "none"}]}`), never an inline suppression. A `"//"` comment key is reported as an unrecognized setting: document the
> config in the project's rules instead. Proven: `npx pyright@1.1.407 <part>` 0 warnings with it, 3 "is not defined" without.

> **Learned 2026-10-27** · git 2.x, Python 3.14 subprocess · VERIFIED_PRIMARY (failed `--apply` run, then fixed and re-run: 198 moves) · Source: local-knowledge-ansible `scripts/smc_change_runs_by_flavor.py` `move()` · Falsifier: `git -C <dir> mv <name> <relative dst>`
> landing the file at `<cwd>/<relative dst>` `git -C <dir>` changes directory before reading its arguments, so a relative destination resolves under `<dir>`, not the caller's cwd: the first migration
> run failed with exit 128 on its first file. Resolve both paths before calling git, and plan every move before the first one (a dry run that prints them) so a failure mid-way leaves a known state.
>
> ```python
> src, dst = src.resolve(), dst.resolve()  # git -C changes directory, so relative paths would point elsewhere
> dst.parent.mkdir(parents=True, exist_ok=True)
> subprocess.run(["git", "-C", str(src.parent), "mv", src.name, str(dst)], check=True)
> ```

> **Learned 2026-11-05** · regex over task-runner and config names · VERIFIED_PRIMARY · Source: skills_stuff skill-ai-it `d40e972`, `scripts/adoption/adopt_governed_files.py` · Falsifier: `re.search(r"^check\b", "check-links:\n", re.M)` returning None
> `\b` treats a hyphen as a word boundary, so `^check\b` also matches `check-links:` and `check-contracts:`; a recipe above `check` was read as the
> check recipe and the fix aimed at the wrong body. Anchor a name on what may follow it: `^check(?=[ \t:])`.
>
> ```python
> # skill-ai-it adopt_governed_files.py, d40e972
> m = re.search(r"^check(?=[ \t:])[^\n]*\n((?:[ \t]+[^\n]*\n?)+)", text, re.M)
> ```

> **Learned 2026-11-07** · ruff 0.17.4 · VERIFIED_PRIMARY · Source: smc-resiliency `ruff.toml`, `lab/` (2026-11-07) · Falsifier: ruff
> checking a file outside `include` when it is passed by name with `force-exclude = true`
> New code only, by folder: `include = ["lab/**/*.py"]` with `force-exclude = true`, `indent-width = 2`, `line-length = 160`,
> `select = ["E","F","W","I","B","UP","D"]` and `[lint.pydocstyle] convention = "google"`: the new package passed with one finding (a
> two-line docstring summary, D205), and the older spike code stayed untouched. Tests that import a package that is not installed use
> `importlib.import_module` after the `sys.path` line, never `# noqa: E402`.

> **Learned 2026-11-07 (b)** · Python 3.14, unittest.mock · VERIFIED_PRIMARY · Source: smc-resiliency `lab/standin/server.py` (S4 contract work) ·
> Falsifier: `mock.patch.object(module, "CONST", ...)` reaching a function whose default is `CONST`
> A default argument that names a module constant is bound when the module is imported, so patching the constant later does not reach it (a
> loopback test failed "signature does not verify"). Write `key: Path | None = None` and use `key or CA_KEY` inside. Also: a search-and-replace
> that routes calls through a new wrapper rewrites the wrapper's own call too (infinite recursion; smc-resiliency `lab/logic/bootstate.py`
> `run_noted`): test a path through the wrapper; a cache keyed only on a name served stale content: key it on the content's hash or signature.

> **Learned 2026-11-09** · ruff (legacy files outside `include`) · VERIFIED_PRIMARY · Source: smc-resiliency `justfile` `lint` and `spike/onbox/smcbox/recheck.py:86`, commit f923adbe · Falsifier: a legacy file outside `include` whose undefined name ruff reports
> Leaving legacy files out of ruff's `include` (so they are not reformatted) also turns off its correctness rules for them: an exception handler
> named a module it never imported (`NameError` on the error path) and nothing flagged it. Run the undefined-name rules over every file, legacy
> included, without the project config: `ruff check --isolated --select F821,F822,F823 .`; it found exactly that one error. The same project's
> `check` also ran none of the on-box unit tests (see testing.md, the closing check): both went red with the import removed.

> **Learned 2026-11-11** · Python 3.14, scripted edits of Markdown front matter and JSON config · VERIFIED_PRIMARY · Source: token-optimizer session scratch scripts
> `shorten_desc.py` and `apply_qw.py` (one-offs, not committed; edits landed in skills_stuff `specialists/*/SKILL.md`, 2026-11-11) · Falsifier: a dry run whose reported old
> length equals the real folded description length with the plain split
> Splitting front matter with `src.split("\n---", 1)[0]` drops the newline that ends the last front-matter line, so a line regex such as
> `^description: >-\n((?:  .*\n)+)` stops one line short: the dry run reported 466 old characters for a 620-character description, and an apply would have left the old
> last line under the new text. Keep the newline (`+ "\n"`), compare the dry run's old length with the listing, then parse the result with `yaml.safe_load` and assert
> the field equals the intended text. Rewriting a JSON config with `json.dumps` can silently re-escape the whole file (`–` vs `–`): before writing, check that
> loading and dumping the untouched file reproduces it byte for byte, choose `ensure_ascii` per file to match, and only then apply the change, so the diff holds the change alone.
>
> ```python
> head = src.split("\n---", 1)[0] + "\n"          # keep the last line's newline
> block = re.compile(r"^description: >-\n((?:  .*\n)+)", re.M)
> raw = open(cfg).read()
> for ascii_ in (True, False):                    # pick the escaping that round-trips
>   if json.dumps(json.loads(raw), indent=2, ensure_ascii=ascii_) + "\n" == raw:
>     break
> ```

> **Learned 2026-11-06** (promoted 2026-11-11 from enterprise-strategy's parked candidates) · Python, parsing hand-written list items · reusable_candidate ·
> Source: apn scripts/project_sync.py `OUT_ITEM` @ 2683a323 · Falsifier: a hand-stamped line is left alone again.
> A line format people type by hand gets the decorations they habitually add (here a leading `**YYYYMMDD_hhmm**` copied from ticked lines).
> Accept the decoration as optional in the pattern and drop it, rebuilding the line on write; a refusal that recurs (30 Oct and 6 Nov) is the
> signal. Prove it with a self-test that fails on the old pattern.
>
> ```python
> OUT_ITEM = re.compile(r"^- \[ \] (?:\*\*\d{8}_\d{4}\*\* )?(?P<directive>directive )?to (?P<to>[\w ,-]+?):\s*(?P<text>.+)$", re.S)
> ```
