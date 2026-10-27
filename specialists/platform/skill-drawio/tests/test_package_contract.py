"""Offline contract checks for the skill-drawio pack: routing, the claim ledger and environments, write-back entries, module portability, catalogue
and documentation, and safe text. Each rule has a negative fixture showing it can fail.

Run: `just test` (the pack's venv, which adds PyYAML for reading sources.yaml).
"""

from __future__ import annotations

import ast
import re
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"SKILL.md", "AGENTS.md", "README.md", "CHANGELOG.md", "SCRATCHPAD.md", "sources.yaml", "compatibility.yaml", "code-map.toml", "justfile",
            "references/evolution-and-write-back.md", "schemas/flowmap.schema.json", "examples/shop/flows.yaml", "examples/shop/drawio/flows.drawio",
            "tests/test_helpers.py", "scripts/README.md", "documents/drawio-sources-20261019/readme.md"}
CLAIM_FIELDS = {"id", "statement", "kind", "evidence_status", "lifecycle", "applies_to", "environment_id", "source_type", "evidence", "falsifier", "reference"}
CLAIM_KINDS = {"generic_invariant", "tested_pattern", "worked_example"}
EVIDENCE = {"VERIFIED_PRIMARY", "VERIFIED_SECONDARY", "UNVERIFIED", "USER_STATED"}
#: The oldest Python every module must parse at (projects run the engine with their own interpreter).
MIN_PYTHON = (3, 11)
#: The pack's governance checker is generated from skill-ai-it's template; its canonical source lives there.
NOT_ENGINE = {"check_governance.py"}
#: Third-party modules a module may import, and only inside a function (at the edge): PyYAML reads maps.
EDGE_IMPORTS = {"yaml"}
LEARNED = re.compile(r"^> \*\*(Learned|Disputed) (\d{4}-\d{2}-\d{2})\*\* · (?P<scope>[^·]+?) · "
                     r"(?P<evidence>VERIFIED_PRIMARY|VERIFIED_SECONDARY|UNVERIFIED|USER_STATED) · Source: (?P<source>[^·]+?)"
                     r" · Falsifier: (?P<falsifier>[^·]+?)(?: · Conflicts: (?P<conflicts>.+))?$")
#: Checks that do not apply to verbatim third-party captures under documents/ (vendor examples use private addresses); credentials still apply.
CAPTURE_EXEMPT = ("private address",)


def learned_entries(text: str) -> list[tuple[str, str]]:
    """Every write-back entry outside code fences.

    Args:
        text: a reference file's markdown.

    Returns:
        (kind, date) per entry.

    Raises:
        AssertionError: on a malformed entry, or a Disputed entry naming no conflict.
    """
    out = []
    lines = re.sub(r"(?ms)^```.*?^```", "", text).splitlines()
    for i, line in enumerate(lines):
        if not re.match(r"^> \*\*(?:Learned|Disputed)\b", line):
            continue
        rest = lines[i + 1:i + 6]   # the markdown wrap hook folds a long header over several "> " lines
        while "Falsifier:" not in line and rest and rest[0].startswith("> ") and not re.match(r"^> \*\*", rest[0]):
            line += " " + rest.pop(0)[2:]
        m = LEARNED.match(line)
        if not m:
            raise AssertionError(f"malformed write-back entry: {line[:80]}")
        if m.group(1) == "Disputed" and not m.group("conflicts"):
            raise AssertionError("a Disputed entry must name what it conflicts with")
        out.append((m.group(1), m.group(2)))
    return out


def assert_safe_text(text: str, where: str = "fixture", capture: bool = False) -> None:
    """Fail on credentials, private keys or private addresses.

    Args:
        text: file content.
        where: its path, for the message.
        capture: True for a verbatim third-party capture under documents/ (CAPTURE_EXEMPT checks are skipped).

    Raises:
        AssertionError: naming the first unsafe pattern found.
    """
    patterns = {
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----": "private key",
        r"(?im)^\s*(?:password|token|api[_-]?key)\s*[:=]\s*[\"']?(?!DUMMY|<|\$\{|\*\*\*)[A-Za-z0-9+/_-]{8,}": "credential assignment",
        r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b": "private address",
    }
    for pattern, reason in patterns.items():
        if not (capture and reason in CAPTURE_EXEMPT) and re.search(pattern, text):
            raise AssertionError(f"{where}: {reason}")


def missing_docs(text: str) -> list[str]:
    """Functions and classes without a docstring, and functions whose docstring lacks `Args:` (when they take arguments) or `Returns:` (when
    they return a value).

    Args:
        text: Python source.

    Returns:
        The names that fall short.
    """
    out = []
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.ClassDef) and not ast.get_docstring(node):
            out.append(node.name)
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        doc = ast.get_docstring(node) or ""
        params = [a.arg for a in node.args.args + node.args.kwonlyargs if a.arg not in ("self", "cls")] + ([node.args.vararg.arg] if node.args.vararg else [])
        returns = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
        if not doc or (params and "Args:" not in doc) or (returns and "Returns:" not in doc and "Returns" not in doc.split("\n")[0]):
            out.append(node.name)
    return out


def top_level_imports(tree: ast.Module) -> list[str]:
    """The modules a file imports at module level (an import inside a function is at the edge and not listed).

    Args:
        tree: the parsed module.

    Returns:
        Top-level package names, relative imports left out.
    """
    out = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            out += [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom) and not node.level:
            out.append((node.module or "").split(".")[0])
    return out


def engine() -> list[Path]:
    """The pack's Python modules (front ends, packages, helpers).

    Returns:
        scripts/**/*.py except NOT_ENGINE.
    """
    return sorted(p for p in (ROOT / "scripts").rglob("*.py") if p.name not in NOT_ENGINE and "__pycache__" not in p.parts)


class PackageContract(unittest.TestCase):
    """The pack's executable contract."""

    def test_required_tree(self) -> None:
        """Every required file exists."""
        actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()}
        self.assertTrue(REQUIRED <= actual, sorted(REQUIRED - actual))

    def test_skill_routes_every_reference(self) -> None:
        """SKILL.md has exactly name and description, no TODO, and names every reference."""
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        front = re.match(r"^---\n(.*?)\n---\n", content, re.S)
        self.assertIsNotNone(front)
        meta = yaml.safe_load(front.group(1))
        self.assertEqual(set(meta), {"name", "description"})
        self.assertEqual(meta["name"], "skill-drawio")
        self.assertNotIn("TODO", content.upper())
        for path in sorted((ROOT / "references").glob("*.md")):
            self.assertIn(path.relative_to(ROOT).as_posix(), content, f"{path.name} is not routed from SKILL.md")

    def test_claim_ledger_and_environments(self) -> None:
        """Claims follow the schema, ids are unique, references and captures exist, operator rules are user_policy with no environment, and every
        other claim names an environment from compatibility.yaml."""
        envs = {e["id"] for e in yaml.safe_load((ROOT / "compatibility.yaml").read_text(encoding="utf-8"))["environments"]}
        claims = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))["claims"]
        self.assertTrue(claims)
        ids = set()
        for c in claims:
            self.assertTrue(CLAIM_FIELDS <= set(c), c.get("id"))
            self.assertNotIn(c["id"], ids)
            ids.add(c["id"])
            self.assertIn(c["kind"], CLAIM_KINDS, c["id"])
            self.assertIn(c["evidence_status"], EVIDENCE, c["id"])
            self.assertEqual(c["evidence_status"] == "USER_STATED", c["source_type"] == "user_policy", c["id"])
            if c["source_type"] == "user_policy":
                self.assertIsNone(c["environment_id"], c["id"])
            else:
                self.assertIn(c["environment_id"], envs, c["id"])
            self.assertTrue(set(c["applies_to"]) <= envs, c["id"])
            self.assertTrue((ROOT / c["reference"]).is_file(), c["id"])
            for rel in re.findall(r"documents/[\w./-]+\.txt", c["evidence"]):
                self.assertTrue((ROOT / rel).is_file(), f"{c['id']}: {rel} is missing")

    def test_write_back_entries_logged(self) -> None:
        """Every Learned or Disputed entry has a CHANGELOG line naming its file and date; lines the budget rotation moved to docs/ count."""
        logs = [ROOT / "CHANGELOG.md", *sorted((ROOT / "docs").glob("changelog-*.md")), *sorted((ROOT / "docs" / "history").glob("changelog-*.md"))]
        changelog = "\n".join(p.read_text(encoding="utf-8") for p in logs)
        for path in sorted((ROOT / "references").glob("*.md")):
            for _kind, date in learned_entries(path.read_text(encoding="utf-8")):
                self.assertTrue([ln for ln in changelog.splitlines() if date in ln and path.name in ln], f"{path.name} {date} not logged")

    def test_modules_portable_catalogued_tested_and_documented(self) -> None:
        """Each module parses at Python 3.11, imports only the stdlib and this pack at module level, is catalogued and tested, documents every
        function, and declares REQUIRES_PYTHON when it is runnable."""
        catalogue = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
        tests = "\n".join(p.read_text(encoding="utf-8") for p in sorted((ROOT / "tests").glob("test_*.py")))   # any test module may hold a module's tests
        local = {p.stem for p in (ROOT / "scripts").glob("*.py")} | {p.name for p in (ROOT / "scripts").iterdir() if p.is_dir()}
        for path in engine():
            rel = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, feature_version=MIN_PYTHON)
            for name in top_level_imports(tree):
                self.assertIn(name, set(sys.stdlib_module_names) | local | {"__future__"}, f"{rel} imports {name} at module level")
            self.assertIn(f"`{rel}`", catalogue, f"{rel} is not catalogued in scripts/README.md")
            if path.name != "__init__.py":
                self.assertIn(f'"{path.stem}"', tests, f"{rel} has no tests")
            if "__main__" in text:
                self.assertRegex(text, r"(?m)^REQUIRES_PYTHON = \(3, 11\)$", rel)
            self.assertEqual(missing_docs(text), [], rel)

    def test_text_is_safe(self) -> None:
        """No unsafe text in any markdown, YAML, TOML, JSON or text file."""
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".yml", ".toml", ".txt", ".json"} and ".git" not in path.parts:
                rel = path.relative_to(ROOT).as_posix()
                assert_safe_text(path.read_text(encoding="utf-8", errors="replace"), rel, rel.startswith("documents/"))


class ContractCanFail(unittest.TestCase):
    """Negative fixtures: every contract rule above rejects a bad input."""

    def test_bad_write_back_entries(self) -> None:
        """A wrong label, a missing falsifier and a Disputed entry without a conflict are rejected; a good entry and a fenced one pass."""
        good = "> **Learned 2026-10-19** · draw.io 32.5.5 · VERIFIED_PRIMARY · Source: https://example.org/x · Falsifier: a run showing otherwise"
        self.assertEqual(len(learned_entries(good)), 1)
        self.assertEqual(learned_entries("```text\n" + good + "\n```\n"), [])
        for bad in ("> **Learned 2026-10-19** · x · VERIFIED · Source: s · Falsifier: f",
                    "> **Learned 2026-10-19** · x · UNVERIFIED · Source: s",
                    "> **Disputed 2026-10-19** · x · UNVERIFIED · Source: s · Falsifier: f"):
            with self.assertRaises(AssertionError):
                learned_entries(bad)

    def test_unsafe_text(self) -> None:
        """Credentials, keys and private addresses are caught; placeholders are not; a capture may show a vendor's example address."""
        assert_safe_text("token: <from the vault>\npassword = ${DB_PASSWORD}\nhost 192.0.2.10")
        for bad in ("password = hunter2hunter2", "-----BEGIN PRIVATE KEY-----", "ssh 10.1.2.3"):
            with self.assertRaises(AssertionError):
                assert_safe_text(bad)
        assert_safe_text("example 192.168.1.1", capture=True)
        with self.assertRaises(AssertionError):
            assert_safe_text("-----BEGIN PRIVATE KEY-----", capture=True)

    def test_missing_docs_and_top_level_imports(self) -> None:
        """A function without Args or Returns and a class without a docstring are named; a module-level third-party import is listed, one inside a
        function is not."""
        self.assertEqual(sorted(missing_docs('class A:\n    pass\n\ndef f(x):\n    """Do f."""\n    return x\n')), ["A", "f"])
        tree = ast.parse("import yaml\nfrom .x import y\n\ndef f():\n    import requests\n")
        self.assertEqual(top_level_imports(tree), ["yaml"])


if __name__ == "__main__":
    unittest.main()
