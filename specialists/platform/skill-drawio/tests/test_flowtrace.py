"""Tests for the flow-map trace: fingerprints that ignore what cannot change behaviour, the review lock, coverage both ways, and queries."""

import contextlib
import importlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from flowtrace import coverage, lockfile
from flowtrace.fingerprint import fingerprint
from flowtrace.query import Ask, select

#: Every module of the package, so the contract test finds it named here: "fingerprint", "lockfile", "coverage", "query", "trace_sync", "trace_query".
PY = 'def a():\n    """Doc."""\n    return 1\n\n\ndef b():\n    return 2\n'
SHELL = "one() {\n  echo 1\n}\n\ntwo() {\n  echo 2\n}\n"
SPEC = "name: x\nactions:\n  - type: copy\nverify:\n  - cmd: true\n"


def map_for(code: list[str], trace: dict | None = None) -> dict:
    """A one-step map.

    Args:
        code: the step's references.
        trace: the map's `trace:` block.

    Returns:
        The map.
    """
    step = {"id": "s", "actor": "c", "action": "run helper_tool", "via": ["SSH"], "code": code, "writes": ["record"], "failures": ["timeout"]}
    flow = {"id": "f", "title": "F", "purpose": "P", "trigger": {"kind": "command", "detail": "go"}, "steps": [step]}
    return {"components": [{"id": "c", "name": "Comp"}], "flows": [flow], **({"trace": trace} if trace else {})}


class Base(unittest.TestCase):
    """A scratch project."""

    def setUp(self) -> None:
        """Make the project."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "m.py").write_text(PY)
        (self.root / "s.sh").write_text(SHELL)
        (self.root / "spec.yml").write_text(SPEC)


class Fingerprints(Base):
    """A fingerprint moves only on a change of behaviour in what the reference covers."""

    def prints(self, ref: str) -> str:
        """Fingerprint a reference.

        Args:
            ref: the reference.

        Returns:
            The fingerprint.
        """
        return fingerprint(self.root, ref)[0]

    def test_python_comment_and_docstring_change_nothing(self):
        """Words around the code are not behaviour."""
        was = self.prints("m.py:a")
        (self.root / "m.py").write_text(PY.replace("Doc.", "Other.").replace("return 1", "return 1  # note"))
        self.assertEqual(was, self.prints("m.py:a"))

    def test_python_symbol_ignores_its_neighbour_and_a_move(self):
        """A change or a move elsewhere in the file leaves a symbol alone."""
        was = self.prints("m.py:a")
        (self.root / "m.py").write_text("X = 1\n\n\n" + PY.replace("return 2", "return 3"))
        self.assertEqual(was, self.prints("m.py:a"))

    def test_python_body_change_shows(self):
        """A real change moves the fingerprint."""
        was = self.prints("m.py:a")
        (self.root / "m.py").write_text(PY.replace("return 1", "return 9"))
        self.assertNotEqual(was, self.prints("m.py:a"))

    def test_shell_function_is_cut_out(self):
        """A shell function has its own fingerprint."""
        one, two = self.prints("s.sh:one"), self.prints("s.sh:two")
        (self.root / "s.sh").write_text(SHELL.replace("echo 2", "echo 3"))
        self.assertEqual(one, self.prints("s.sh:one"))
        self.assertNotEqual(two, self.prints("s.sh:two"))

    def test_yaml_key_block(self):
        """A new action moves `actions` and leaves `verify`."""
        acts, ver = self.prints("spec.yml:actions"), self.prints("spec.yml:verify")
        (self.root / "spec.yml").write_text(SPEC.replace("  - type: copy\n", "  - type: copy\n  - type: ini\n"))
        self.assertNotEqual(acts, self.prints("spec.yml:actions"))
        self.assertEqual(ver, self.prints("spec.yml:verify"))

    def test_gone_symbol_is_none(self):
        """A missing symbol or file has no fingerprint."""
        self.assertIsNone(self.prints("m.py:nope"))
        self.assertIsNone(self.prints("none.py"))


class Lock(Base):
    """The suspect workflow: raised by a change, shown with a diff, cleared only by accept."""

    def setUp(self) -> None:
        """Accept a one-step map."""
        super().setUp()
        (self.root / "flows.yaml").write_text("x: 1\n")
        self.data = map_for(["m.py:a"])
        lockfile.accept(self.root, "flows.yaml", self.data, ["all"], "tester")

    def found(self) -> list:
        """List findings.

        Returns:
            lockfile.findings().
        """
        return lockfile.findings(self.root, "flows.yaml", self.data)

    def test_clean_after_accept(self):
        """A review holds while the code stands."""
        self.assertEqual(self.found(), [])

    def test_change_raises_a_suspect_with_a_diff(self):
        """The finding names the reference and shows the change."""
        (self.root / "m.py").write_text(PY.replace("return 1", "return 9"))
        f = self.found()[0]
        self.assertEqual((f.step, f.state, f.refs), ("f/s", "suspect", [("m.py:a", "changed")]))
        self.assertTrue(any("return 9" in d for d in f.diff))

    def test_editing_the_words_does_not_clear_it(self):
        """Only accept clears a suspect; the edit is reported beside it."""
        (self.root / "m.py").write_text(PY.replace("return 1", "return 9"))
        self.data["flows"][0]["steps"][0]["action"] = "new words"
        f = self.found()[0]
        self.assertEqual(f.state, "suspect")
        self.assertTrue(f.edited)

    def test_accept_clears_and_prunes_the_old_source(self):
        """After accept the old snapshot goes."""
        (self.root / "m.py").write_text(PY.replace("return 1", "return 9"))
        lockfile.accept(self.root, "flows.yaml", self.data, ["f/s"], "tester")
        self.assertEqual(self.found(), [])
        self.assertEqual(len(list((self.root / "flows.lock.d").glob("*.txt"))), 1)

    def test_gone_code_is_broken_and_refuses_accept(self):
        """A broken reference cannot be accepted away."""
        (self.root / "m.py").write_text("x = 1\n")
        self.assertEqual(self.found()[0].state, "broken")
        with self.assertRaises(ValueError):
            lockfile.accept(self.root, "flows.yaml", self.data, ["all"], "tester")

    def test_new_step_is_new(self):
        """A step never reviewed is listed."""
        self.data["flows"][0]["steps"].append({"id": "t", "actor": "c", "action": "x", "via": ["SSH"], "code": ["m.py:b"]})
        self.assertEqual([(f.step, f.state) for f in self.found()], [("f/t", "new")])

    def test_select_by_cited_file(self):
        """A file names the steps citing it."""
        self.assertEqual(len(lockfile.selected(self.data, ["m.py"])), 1)
        self.assertEqual(lockfile.selected(self.data, ["other.py"]), [])


class Coverage(Base):
    """The trace's other direction."""

    def test_uncited_file_is_reported_until_exempt(self):
        """A covered file needs a citation or a reason."""
        data = map_for(["m.py"], {"cover": ["*.py", "*.sh"]})
        self.assertEqual(len(coverage.coverage_problems(self.root, data)), 1)
        data["trace"]["exempt"] = {"s.sh": "a helper for people"}
        self.assertEqual(coverage.coverage_problems(self.root, data), [])

    def test_stale_exempt_is_reported(self):
        """An exemption that matches nothing is noise."""
        data = map_for(["m.py"], {"cover": ["*.py"], "exempt": {"gone/*": "old"}})
        self.assertIn("stale exempt", coverage.coverage_problems(self.root, data)[0])

    def test_ratchet_both_ways(self):
        """Too many uncited steps fail; fewer ask for the allowance to drop."""
        self.assertIn("uncited steps", coverage.coverage_problems(self.root, map_for([], {"uncited_steps": 0}))[0])
        self.assertIn("ratchet", coverage.coverage_problems(self.root, map_for(["m.py"], {"uncited_steps": 1}))[0])

    def test_word_missing_from_code_warns_until_known(self):
        """A named thing the code no longer holds is flagged."""
        data = map_for(["m.py"], {"cover": ["*.py"]})
        self.assertEqual(coverage.stale_words(self.root, data), ["f/s: `helper_tool`"])
        data["trace"]["known_words"] = ["helper_tool"]
        self.assertEqual(coverage.stale_words(self.root, data), [])


class Query(unittest.TestCase):
    """Questions asked of a map."""

    def test_each_field_finds_and_a_miss_is_empty(self):
        """Every field narrows; a wrong word finds nothing."""
        data = map_for(["tasks/m.py:a"])
        for ask in (Ask(flow="f"), Ask(file="m.py"), Ask(writes="record"), Ask(failure="timeout"), Ask(actor="comp"), Ask(text="helper")):
            self.assertEqual(len(select(data, ask)), 1, ask)
        self.assertEqual(select(data, Ask(writes="nope")), [])


class FrontEnds(Base):
    """The two commands, end to end."""

    def setUp(self) -> None:
        """A real map on disk."""
        super().setUp()
        (self.root / "flows.yaml").write_text(yaml.safe_dump(map_for(["m.py:a"], {"cover": ["*.py"]})))
        self.args = ["--root", str(self.root), "--map", "flows.yaml"]

    def run_main(self, name: str, *more: str) -> tuple[int, str]:
        """Run a front end.

        Args:
            name: the module.
            *more: its arguments.

        Returns:
            (exit code, stdout).
        """
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = importlib.import_module(name).main(self.args + list(more))
        return rc, out.getvalue()

    def test_sync_plan_apply_change_accept(self):
        """No lock is a finding; a plan writes nothing; apply clears; a change comes back; JSON carries it."""
        self.assertEqual(self.run_main("trace_sync")[0], 1)
        self.run_main("trace_sync", "--accept", "all")
        self.assertFalse((self.root / "flows.lock.json").exists())
        self.assertEqual(self.run_main("trace_sync", "--accept", "all", "--apply")[0], 0)
        self.assertEqual(self.run_main("trace_sync")[0], 0)
        (self.root / "m.py").write_text(PY.replace("return 1", "return 9"))
        rc, text = self.run_main("trace_sync", "--json")
        self.assertEqual((rc, json.loads(text)["findings"][0]["state"]), (1, "suspect"))

    def test_query_marks_a_suspect_step(self):
        """A reader sees a step's review no longer holds."""
        self.run_main("trace_sync", "--accept", "all", "--apply")
        (self.root / "m.py").write_text(PY.replace("return 1", "return 9"))
        rc, text = self.run_main("trace_query", "--flow", "f")
        self.assertEqual(rc, 0)
        self.assertIn("[SUSPECT", text)

    def test_query_needs_a_question(self):
        """No field is a usage error."""
        self.assertEqual(self.run_main("trace_query")[0], 2)

    def test_apply_needs_accept(self):
        """--apply alone is refused."""
        self.assertEqual(self.run_main("trace_sync", "--apply")[0], 2)


if __name__ == "__main__":
    unittest.main()
