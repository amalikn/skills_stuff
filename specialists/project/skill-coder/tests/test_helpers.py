"""Offline tests for skill-coder's helper scripts: each rule is shown passing on good input and failing on bad input.

Run: `just test` (unittest, the project's pinned interpreter). The helpers are imported from scripts/ by name.
"""

from __future__ import annotations

import importlib
import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# The helpers are plain modules in scripts/ (not a package), loaded by name once that folder is on sys.path.
call_timeouts, code_map, code_size, import_layers, naming_check, naming_table, pyparse, ratchet, script_headers, write_gates = (
    importlib.import_module(n) for n in ("call_timeouts", "code_map", "code_size", "import_layers", "naming_check", "naming_table", "pyparse",
                                         "ratchet", "script_headers", "write_gates"))

#: Every helper named here, so the contract test can see each one has tests: "ratchet", "code_size", "import_layers", "write_gates", "script_headers", "code_map", "pyparse", "naming_check", "naming_table",
#: "call_timeouts".


def _tree(files: dict[str, str]) -> Path:
    """A temporary project tree.

    Args:
        files: {relative path: content}.

    Returns:
        The root (removed when the interpreter exits).
    """
    root = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(textwrap.dedent(text), encoding="utf-8")
    return root


class Ratchet(unittest.TestCase):
    """The baseline only tightens."""

    def test_new_finding_fails_and_baseline_allows(self) -> None:
        """A finding over 0 fails without a baseline and passes at its baseline value."""
        self.assertEqual(len(ratchet.compare({"a": 3}, {}).regressions), 1)
        self.assertTrue(ratchet.compare({"a": 3}, {"a": 3}).ok)

    def test_improvement_and_gone_must_be_recorded(self) -> None:
        """A count below its baseline, or a baseline key no longer found, is stale (so the gain is locked in)."""
        self.assertEqual(ratchet.compare({"a": 2}, {"a": 3}).improved, ["a: found 2, baseline 3"])
        self.assertEqual(ratchet.compare({}, {"a": 3}).gone, ["a"])

    def test_load_rejects_non_numbers(self) -> None:
        """A malformed baseline is an error, not an empty one."""
        root = _tree({"b.json": '{"a": "x"}'})
        with self.assertRaises(ValueError):
            ratchet.load(root / "b.json")
        self.assertEqual(ratchet.load(root / "missing.json"), {})


class CodeSize(unittest.TestCase):
    """Module and function limits per language."""

    def test_python_functions_exact(self) -> None:
        """Methods are qualified by class; sizes come from the AST."""
        src = "class A:\n    def m(self):\n        x = 1\n        return x\n\ndef f():\n    pass\n"
        self.assertEqual(code_size.python_functions(src), [("A.m", 3), ("f", 2)])

    def test_python_grammar_and_unparsed_reported(self) -> None:
        """Code newer than the project's grammar does not parse at it, and measure() reports the file instead of skipping it."""
        with self.assertRaises(SyntaxError):
            code_size.python_functions("def f[T](x: T) -> T:\n    return x\n", (3, 11))
        root = _tree({"src/bad.py": "def (:\n"})
        self.assertEqual(len(code_size.measure(root, ["src"], {}).unparsed), 1)

    def test_brace_functions_ignore_braces_in_strings(self) -> None:
        """A brace inside a string or comment does not end the function."""
        src = 'function f(a) {\n  const s = "}";  // }\n  return a;\n}\n'
        self.assertEqual(code_size.brace_functions(src, "c-family"), [("f", 4)])

    def test_go_and_shell(self) -> None:
        """Go funcs and shell functions are found; control keywords are not functions."""
        go = "func (s *S) Run(x int) error {\n\tif x > 0 {\n\t\treturn nil\n\t}\n\treturn nil\n}\n"
        self.assertEqual(code_size.brace_functions(go, "c-family"), [("Run", 6)])
        sh = "deploy() {\n  echo a\n}\nfunction other {\n  echo b\n}\n"
        self.assertEqual(code_size.brace_functions(sh, "shell"), [("deploy", 3), ("other", 3)])

    def test_shell_heredoc_hash_and_glob(self) -> None:
        """Braces in a here-document body, `${#arr[@]}` and a `dir/*` glob do not change a shell function's extent (found on a real
        Ansible repository, 2026-10-19: a 14-line function measured 1,514 lines)."""
        sh = textwrap.dedent('''\
            make() {
              cat > main.tf << 'EOF'
            resource "x" "y" {
            }
            }
            EOF
              n=${#arr[@]}
              rm -f dir/*
            }
            other() {
              echo b
            }
        ''')
        self.assertEqual(code_size.brace_functions(sh, "shell"), [("make", 9), ("other", 3)])

    def test_parser_warnings_silenced(self) -> None:
        """A SyntaxWarning in the parsed project's code is the project linter's business, not printed by the helper."""
        import warnings
        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter("always")
            pyparse.parse('def f():\n    return "\\d"\n')   # "\d" in a non-raw string: ast.parse alone warns (checked 2026-10-19)
        self.assertFalse([w for w in seen if issubclass(w.category, SyntaxWarning)])

    def test_limits_and_language_override(self) -> None:
        """A function over the limit is reported; a per-language override raises the limit for that language only."""
        body = "def f():\n" + "    x = 1\n" * 70
        root = _tree({"src/a.py": body, "src/b.js": "function g() {\n" + "  x();\n" * 70 + "}\n"})
        self.assertEqual(sorted(code_size.measure(root, ["src"], {}).functions), ["src/a.py::f", "src/b.js::g"])
        self.assertEqual(sorted(code_size.measure(root, ["src"], {"python": {"function": 100}}).functions), ["src/b.js::g"])

    def test_warning_tier_and_shell_defaults(self) -> None:
        """Past the warning a unit warns without failing; shell scripts warn at 100 lines and fail at 200."""
        root = _tree({"src/a.py": "x = 1\n" * 350, "src/b.sh": "echo a\n" * 150, "src/c.sh": "echo a\n" * 210})
        got = code_size.measure(root, ["src"], {})
        self.assertEqual(sorted(got.modules), ["src/c.sh"])
        self.assertEqual(sorted(w.split(":")[0] for w in got.warnings), ["src/a.py", "src/b.sh"])

    def test_cli_fails_then_baseline_passes(self) -> None:
        """The command line fails on a new oversized module and passes once the baseline records it."""
        root = _tree({"src/a.py": "x = 1\n" * 410})
        self.assertEqual(code_size.main(["--project-root", str(root), "--roots", "src"]), 1)
        self.assertEqual(code_size.main(["--project-root", str(root), "--roots", "src", "--write-baseline"]), 0)
        self.assertEqual(code_size.main(["--project-root", str(root), "--roots", "src"]), 0)


class ImportLayers(unittest.TestCase):
    """Layer rules and cycles."""

    def _project(self) -> Path:
        """A package `app` with core, services and a cycle between two modules.

        Returns:
            The root.
        """
        return _tree({
            "src/app/__init__.py": "",
            "src/app/core/__init__.py": "",
            "src/app/core/model.py": "from app.services import run\n",
            "src/app/services/__init__.py": "",
            "src/app/services/run.py": "from app.core import model\nfrom . import helper\n",
            "src/app/services/helper.py": "from . import run\n",
            "src/app/layers.toml": '[core]\nlayer = "L0"\nmay_import = []\n[services]\nlayer = "L5"\nmay_import = ["core"]\n',
        })

    def test_inward_import_allowed_outward_fails(self) -> None:
        """services may import core; core importing services breaks the rule."""
        root = self._project()
        rules = import_layers.tomllib.loads((root / "src/app/layers.toml").read_text())
        found = import_layers.layer_violations(root / "src", "app", rules)
        self.assertEqual(found, ["app.core.model -> app.services (L0 core may not import services)"])

    def test_relative_import_cycle_found(self) -> None:
        """A cycle through relative imports is found (the port from the project tool must resolve them)."""
        root = self._project()
        mods = import_layers.module_map(root, ["src"])
        cyc = import_layers.cycles(import_layers.graph(mods), list(mods))
        # core.model imports services.run, which imports core.model back and, relatively, helper (which imports run): one component of three.
        self.assertEqual(cyc, [["app.core.model", "app.services.helper", "app.services.run"]])

    def test_baseline_accepts_known_violation(self) -> None:
        """A violation listed in the baseline passes; the CLI fails without it."""
        root = self._project()
        args = ["--project-root", str(root), "--src", "src", "--package", "app", "--layers", "src/app/layers.toml"]
        self.assertEqual(import_layers.main(args), 1)
        (root / "base.json").write_text(json.dumps(["app.core.model -> app.services (L0 core may not import services)"]))
        self.assertEqual(import_layers.main(args + ["--baseline", "base.json"]), 0)


class WriteGates(unittest.TestCase):
    """Writers take --apply or are registered."""

    def test_ungated_writer_fails_gated_passes(self) -> None:
        """An entry point that POSTs without --apply fails; one with --apply passes; a non-entry module is ignored."""
        root = _tree({
            "scripts/bad.py": 'import requests\nrequests.post("u")\nif __name__ == "__main__":\n    pass\n',
            "scripts/good.py": 'import argparse\np = argparse.ArgumentParser(); p.add_argument("--apply")\nx = "POST"\nif __name__ == "__main__":\n    pass\n',
            "scripts/lib.py": 'x = "DELETE"\n',
        })
        found = write_gates.writers(root, write_gates.load_config(None), set())
        self.assertEqual(found, {"scripts/bad.py": False, "scripts/good.py": True})
        self.assertEqual(len(write_gates.problems(found, {})), 1)

    def test_register_cannot_go_stale(self) -> None:
        """An exception without a reason, for a file that no longer writes, or for one now gated, fails."""
        found = {"scripts/a.py": False, "scripts/b.py": True}
        msgs = write_gates.problems(found, {"scripts/a.py": "", "scripts/gone.py": "x", "scripts/b.py": "y"})
        self.assertEqual(len(msgs), 3)

    def test_prose_and_lowercase_are_not_writes(self) -> None:
        """'delete' as a word, and shell words in a Python docstring, are not writes; the same words in a shell script are."""
        root = _tree({
            "scripts/a.py": '"""Run pip install first."""\naction = "delete"\nif __name__ == "__main__":\n    pass\n',
            "scripts/b.sh": "#!/bin/bash\npip install x\n",
        })
        self.assertEqual(write_gates.writers(root, write_gates.load_config(None), set()), {"scripts/b.sh": False})


class CallTimeouts(unittest.TestCase):
    """Network and subprocess calls carry a timeout."""

    def test_untimed_found_timed_and_kwargs_trusted(self) -> None:
        """A call without timeout= is found; with it, or with **kwargs, it is not; text in a string is not a call."""
        src = textwrap.dedent('''
            import subprocess, requests
            subprocess.run(["x"])
            subprocess.run(["x"], timeout=5)
            requests.get(u, **opts)
            s = "subprocess.run(['x'])"
            p = subprocess.Popen(["x"])
            p.communicate()
        ''')
        self.assertEqual([n for _l, n in call_timeouts.untimed_calls(src)], ["subprocess.run", "p.communicate"])

    def test_cli_ratchet(self) -> None:
        """The command line fails on a new untimed call and passes at its baseline."""
        root = _tree({"src/a.py": "import urllib.request\nurllib.request.urlopen('u')\n"})
        self.assertEqual(call_timeouts.main(["--project-root", str(root), "--roots", "src"]), 1)
        call_timeouts.main(["--project-root", str(root), "--roots", "src", "--write-baseline"])
        self.assertEqual(call_timeouts.main(["--project-root", str(root), "--roots", "src"]), 0)


class ScriptHeaders(unittest.TestCase):
    """A runnable script's header says what it is for, how to run it and what it touches."""

    def test_complete_header_passes(self) -> None:
        """Summary, Usage and a safety statement: nothing missing."""
        src = '"""Count things. Read-only.\n\nUsage:\n    x.py --root .\n"""\nif __name__ == "__main__":\n    pass\n'
        self.assertEqual(script_headers.missing_parts(src, ".py"), [])

    def test_gaps_reported_library_needs_summary_only(self) -> None:
        """An entry point without Usage or safety lacks both; no docstring lacks all three; a library module needs only a summary."""
        self.assertEqual(script_headers.missing_parts('"""Count things."""\nif __name__ == "__main__":\n    pass\n', ".py"), ["run", "safety"])
        self.assertEqual(script_headers.missing_parts('if __name__ == "__main__":\n    pass\n', ".py"), ["summary", "run", "safety"])
        self.assertEqual(script_headers.missing_parts('"""Helpers."""\n', ".py"), [])

    def test_shell_header_after_shebang(self) -> None:
        """A shell script's header is the comment block after its shebang."""
        good = "#!/bin/bash\n# Back up the database; writes only with --apply.\n# Usage: backup.sh [--apply]\nset -euo pipefail\n"
        self.assertEqual(script_headers.missing_parts(good, ".sh"), [])
        self.assertEqual(script_headers.missing_parts("#!/bin/bash\nset -e\n", ".sh"), ["summary", "run", "safety"])


class CodeMap(unittest.TestCase):
    """The code map holds decisions only, is checked on load, and drives each checker."""

    def test_template_loads(self) -> None:
        """The shipped template is a valid map."""
        self.assertIn("layers", code_map.load(ROOT / "templates" / "code-map.toml"))

    def test_typo_and_bad_module_entry_fail(self) -> None:
        """An unknown section (a typo would switch a rule off silently) and a module entry without status or reason both fail."""
        root = _tree({"a.toml": "[limit.python]\nmodule = 1\n", "b.toml": '[modules."x.py"]\nstatus = "done"\n',
                      "c.toml": '[modules."x.py"]\nstatus = "candidate"\n', "d.toml": '[modules."x.py"]\nstatus = "promoted"\n'})
        for name in ("a.toml", "b.toml", "c.toml", "d.toml"):
            with self.assertRaises(ValueError, msg=name):
                code_map.load(root / name)

    def test_map_drives_limits_layers_and_gates(self) -> None:
        """A code-map.toml at the root is found without a flag and sets roots, limits, layer rules and write-gate exceptions."""
        root = _tree({
            "code-map.toml": textwrap.dedent('''
                [scan]
                roots = ["lib"]
                [limits.python]
                module = 5
                warn_module = 4
                [layers]
                package = "app"
                src = "lib"
                [layers.rules.core]
                layer = "L0"
                may_import = []
                [write_gates]
                roots = ["lib"]
                [write_gates.exceptions]
                "lib/push.py" = "pushes by design; --dry-run reads only"
            '''),
            "lib/app/__init__.py": "", "lib/app/core/__init__.py": "", "lib/app/core/m.py": "import app.ui\n" + "x = 1\n" * 6,
            "lib/app/ui/__init__.py": "",
            "lib/push.py": 'x = "POST"\nif __name__ == "__main__":\n    pass\n',
        })
        self.assertEqual(code_size.main(["--project-root", str(root)]), 1)            # lib/app/core/m.py is 7 lines, limit 5
        self.assertEqual(import_layers.main(["--project-root", str(root)]), 1)        # core may not import ui
        self.assertEqual(write_gates.main(["--project-root", str(root)]), 0)          # the push script is registered


class Naming(unittest.TestCase):
    """File and recipe names against the pack's naming.toml, with project overrides."""

    def test_mapping_loads_and_rejects_bad_rows(self) -> None:
        """The shipped mapping loads; a checked rule with no convention regex, or a linter rule naming no tool, is refused."""
        self.assertTrue(naming_check.load_mapping()["rule"])
        root = _tree({"a.toml": '[conventions]\nsnake_case = "^x$"\n[[rule]]\nlanguage = "x"\nelement = "y"\nconvention = "nope"\ncheck = "file"\nglobs = ["*.x"]\n',
                      "b.toml": '[[rule]]\nlanguage = "x"\nelement = "y"\nconvention = "z"\ncheck = "linter"\n'})
        for name in ("a.toml", "b.toml"):
            with self.assertRaises(ValueError, msg=name):
                naming_check.load_mapping(root / name)

    def test_files_and_recipes(self) -> None:
        """A hyphenated Python or shell file and an underscored recipe break the mapping; dunder files, private recipes and src/bin Rust files do not."""
        root = _tree({"scripts/good_one.py": "", "scripts/bad-one.py": "", "scripts/__init__.py": "", "scripts/run-it.sh": "",
                      "src/bin/my-tool.rs": "", "src/my-mod.rs": "",
                      "justfile": "_private-thing:\n    echo\ncode-size *args:\n    echo\nnav_upgrade:\n    echo\nx := 'y'\n"})
        m = naming_check.load_mapping()
        self.assertEqual(sorted(naming_check.file_findings(root, ["scripts", "src"], m, {}, set())),
                         ["file scripts/bad-one.py", "file scripts/run-it.sh", "file src/my-mod.rs"])
        self.assertEqual(sorted(naming_check.recipe_findings(root, m, None)), ["recipe nav_upgrade"])
        (root / "justfile").write_text('nav_check REF="HEAD":\n    echo\nok-one A="x:y":\n    echo\n')   # a default argument holds `=` and `:`
        self.assertEqual(sorted(naming_check.recipe_findings(root, m, None)), ["recipe nav_check"])

    def test_exceptions_need_reasons_and_cannot_go_stale(self) -> None:
        """A kept name needs a reason, and an exception for a name that no longer breaks the mapping fails."""
        with self.assertRaises(ValueError):
            naming_check.exceptions({"exceptions": {"recipe a_b": " "}})
        root = _tree({"code-map.toml": '[naming.exceptions]\n"recipe old_name" = "renamed upstream later"\n', "justfile": "new-name:\n    echo\n"})
        self.assertEqual(naming_check.main(["--project-root", str(root)]), 1)

    def test_project_overrides(self) -> None:
        """A project's code-map [naming] keeps underscored recipes and adds a convention for a file type the mapping does not check."""
        root = _tree({"code-map.toml": '[scan]\nroots = ["web"]\n[naming]\nrecipe = "snake_case"\n[naming.files]\n"*.js" = "kebab-case"\n',
                      "web/my_page.js": "", "web/other-page.js": "", "justfile": "nav_upgrade:\n    echo\n"})
        self.assertEqual(naming_check.main(["--project-root", str(root), "--list"]), 1)   # web/my_page.js breaks the project's kebab rule
        (root / "web/my_page.js").rename(root / "web/my-page.js")
        self.assertEqual(naming_check.main(["--project-root", str(root)]), 0)            # snake recipes are this project's choice

    def test_table_is_generated_from_the_mapping(self) -> None:
        """The reference's table is exactly what naming.toml renders, and splicing refuses a file without the markers."""
        self.assertEqual(naming_table.main([]), 0)
        with self.assertRaises(ValueError):
            naming_table.splice("no markers here", "| a |\n")


if __name__ == "__main__":
    unittest.main()
