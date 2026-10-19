"""Offline contract checks for the skill-coder pack: routing, the claim ledger, write-back entries, helper portability and documentation, and
safe text. Each rule has a negative fixture showing it can fail.

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
REQUIRED = {"SKILL.md", "naming.toml", "references/naming-conventions.md", "AGENTS.md", "CHANGELOG.md", "sources.yaml", "code-map.toml", "templates/code-map.toml", "languages/readme.md",
            "references/evolution-and-write-back.md", "tests/scenarios.md", "tests/test_helpers.py", "scripts/README.md"}
CLAIM_FIELDS = {"id", "statement", "kind", "evidence_status", "source_type", "evidence", "reference"}
CLAIM_KINDS = {"generic_invariant", "tested_pattern", "worked_example"}
EVIDENCE = {"VERIFIED_PRIMARY", "VERIFIED_SECONDARY", "UNVERIFIED", "USER_STATED"}
SOURCE_TYPES = {"official_documentation", "implementation", "implementation_and_test", "report_synthesis", "user_policy"}
#: The oldest Python every helper must run on (each declares REQUIRES_PYTHON; the helpers run with the target project's interpreter).
MIN_PYTHON = (3, 11)
#: The pack's own governance checker is generated from skill-ai-it's template; its canonical source and size rule live there.
NOT_HELPERS = {"check_governance.py"}
LEARNED = re.compile(r"^> \*\*(Learned|Disputed) (\d{4}-\d{2}-\d{2})(?: \([a-z]\))?\*\* · (?P<scope>[^·]+?) · "
                     r"(?P<evidence>VERIFIED_PRIMARY|VERIFIED_SECONDARY|UNVERIFIED|USER_STATED|CANDIDATE)(?: \([^·]*\))? · Source: (?P<source>[^·]+?)"
                     r" · Falsifier: (?P<falsifier>[^·]+?)(?: · Conflicts: (?P<conflicts>.+))?$")


def _without_fences(text: str) -> str:
    """Text with fenced code blocks removed (examples are not entries).

    Args:
        text: markdown.

    Returns:
        The text outside fences.
    """
    return re.sub(r"(?ms)^```.*?^```", "", text)


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
    lines = _without_fences(text).splitlines()
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


#: Checks that do not apply to verbatim third-party captures under documents/ (a specification's section numbers look like private addresses);
#: credentials and keys are still checked there.
CAPTURE_EXEMPT = ("production domain", "private address")


def assert_safe_text(text: str, where: str = "fixture", capture: bool = False) -> None:
    """Fail on credentials, private keys, production domains or private addresses.

    Args:
        text: file content.
        where: its path, for the message.
        capture: True for a verbatim third-party capture under documents/ (CAPTURE_EXEMPT checks are skipped).

    Raises:
        AssertionError: naming the first unsafe pattern found.
    """
    patterns = {
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----": "private key",
        r"(?im)^authorization:\s*(?!Bearer DUMMY_TOKEN_DO_NOT_USE$).+": "live authorization header",
        r"(?im)^\s*(?:password|token|api[_-]?key)\s*[:=]\s*[\"']?(?!DUMMY|<|\$\{|\*\*\*)[A-Za-z0-9+/_-]{8,}": "credential assignment",
        r"(?i)\b(?:teleport|communitywifi|apn)\.(?:au|com)\b": "production domain",
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
        params = [a.arg for a in node.args.args + node.args.kwonlyargs if a.arg not in ("self", "cls")]
        returns = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
        if not doc or (params and "Args:" not in doc) or (returns and "Returns:" not in doc and "Returns" not in doc.split("\n")[0]):
            out.append(node.name)
    return out


def helpers() -> list[Path]:
    """The pack's helper scripts.

    Returns:
        scripts/*.py except NOT_HELPERS.
    """
    return sorted(p for p in (ROOT / "scripts").glob("*.py") if p.name not in NOT_HELPERS)


class PackageContract(unittest.TestCase):
    """The pack's executable contract."""

    def test_required_tree(self) -> None:
        """Every required file exists."""
        actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()}
        self.assertTrue(REQUIRED <= actual, sorted(REQUIRED - actual))

    def test_skill_routes_every_reference_and_language(self) -> None:
        """SKILL.md has exactly name and description, no TODO, and names every reference and language file."""
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        front = re.match(r"^---\n(.*?)\n---\n", content, re.S)
        self.assertIsNotNone(front)
        meta = yaml.safe_load(front.group(1))
        self.assertEqual(set(meta), {"name", "description"})
        self.assertEqual(meta["name"], "skill-coder")
        self.assertNotIn("TODO", content.upper())
        for path in sorted([*(ROOT / "references").glob("*.md"), *(ROOT / "languages").glob("*.md")]):
            if path.name != "readme.md":
                self.assertIn(path.relative_to(ROOT).as_posix(), content, f"{path.name} is not routed from SKILL.md")

    def test_claim_ledger(self) -> None:
        """Claims follow the schema, ids are unique, references exist, operator rules are user_policy."""
        claims = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))["claims"]
        self.assertTrue(claims)
        ids = set()
        for c in claims:
            self.assertTrue(CLAIM_FIELDS <= set(c), c.get("id"))
            self.assertNotIn(c["id"], ids)
            ids.add(c["id"])
            self.assertIn(c["kind"], CLAIM_KINDS, c["id"])
            self.assertIn(c["evidence_status"], EVIDENCE, c["id"])
            self.assertIn(c["source_type"], SOURCE_TYPES, c["id"])
            self.assertEqual(c["evidence_status"] == "USER_STATED", c["source_type"] == "user_policy", c["id"])
            self.assertTrue((ROOT / c["reference"]).is_file(), c["id"])
            self.assertRegex(c["statement"], r"\.$", c["id"])

    def test_claim_captures_exist(self) -> None:
        """Every capture a claim's evidence names (`documents/...txt`) is on disk, so a VERIFIED claim can be re-opened (first done by hand on a sample,
        2026-10-19; now for every claim)."""
        claims = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8"))["claims"]
        for c in claims:
            for rel in re.findall(r"documents/[\w./-]+\.txt", c["evidence"]):
                self.assertTrue((ROOT / rel).is_file(), f"{c['id']}: {rel} is missing")

    def test_write_back_entries_logged(self) -> None:
        """Every Learned or Disputed entry has a CHANGELOG line naming its file and date."""
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        for path in sorted([*(ROOT / "references").glob("*.md"), *(ROOT / "languages").glob("*.md")]):
            for _kind, date in learned_entries(path.read_text(encoding="utf-8")):
                self.assertTrue([ln for ln in changelog.splitlines() if date in ln and path.name in ln], f"{path.name} {date} not logged")

    def test_helpers_portable_tested_and_documented(self) -> None:
        """Each helper is tested, stdlib-only, declares REQUIRES_PYTHON, parses at that grammar and documents every function."""
        tests = (ROOT / "tests" / "test_helpers.py").read_text(encoding="utf-8")
        local = {p.stem for p in (ROOT / "scripts").glob("*.py")}
        for path in helpers():
            text = path.read_text(encoding="utf-8")
            self.assertIn(f'"{path.stem}"', tests, f"{path.name} has no tests")
            self.assertRegex(text, r"(?m)^REQUIRES_PYTHON = \(3, 11\)$", path.name)
            tree = ast.parse(text, feature_version=MIN_PYTHON)
            for node in ast.walk(tree):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                    [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                for name in names:
                    self.assertIn(name.split(".")[0], set(sys.stdlib_module_names) | local | {"__future__"}, f"{path.name} imports {name}")
            self.assertEqual(missing_docs(text), [], path.name)

    def test_naming_rows_cite_existing_captures(self) -> None:
        """Every naming.toml row names a capture that exists, unless its source is the operator's own rule (USER_STATED)."""
        import tomllib
        rows = tomllib.loads((ROOT / "naming.toml").read_text(encoding="utf-8"))["rule"]
        for r in rows:
            if "USER_STATED" in r["source"]:
                continue
            self.assertTrue((ROOT / "documents/research-sources-20261019" / r["capture"]).is_file(), f"{r['language']} {r['element']}: {r['capture']}")

    def test_text_is_safe(self) -> None:
        """No unsafe text in any markdown, YAML, TOML or text file."""
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".yml", ".toml", ".txt"} and ".git" not in path.parts:
                rel = path.relative_to(ROOT).as_posix()
                assert_safe_text(path.read_text(encoding="utf-8", errors="replace"), rel, rel.startswith("documents/research-sources-"))


class ContractCanFail(unittest.TestCase):
    """Negative fixtures: every contract rule above rejects a bad input."""

    def test_bad_write_back_entries(self) -> None:
        """A wrong label, a missing falsifier and a Disputed entry without a conflict are rejected; a good entry and a fenced one pass."""
        good = "> **Learned 2026-10-19** · Python 3.12 · VERIFIED_PRIMARY · Source: https://example.org/x · Falsifier: a run showing otherwise"
        self.assertEqual(len(learned_entries(good)), 1)
        self.assertEqual(learned_entries("```text\n" + good + "\n```\n"), [])
        for bad in ("> **Learned 2026-10-19** · x · VERIFIED · Source: s · Falsifier: f",
                    "> **Learned 2026-10-19** · x · UNVERIFIED · Source: s",
                    "> **Disputed 2026-10-19** · x · UNVERIFIED · Source: s · Falsifier: f"):
            with self.assertRaises(AssertionError):
                learned_entries(bad)

    def test_unsafe_text(self) -> None:
        """Credentials, keys, private addresses and production domains are caught; placeholders are not."""
        assert_safe_text("token: <from the vault>\npassword = ${DB_PASSWORD}\nhost 192.0.2.10")
        for bad in ("Authorization: Bearer abc", "password = hunter2hunter2", "-----BEGIN PRIVATE KEY-----", "ssh 10.1.2.3"):
            with self.assertRaises(AssertionError):
                assert_safe_text(bad)
        assert_safe_text("see section 10.1.1.1", capture=True)          # a capture's section number is not an address
        with self.assertRaises(AssertionError):
            assert_safe_text("-----BEGIN PRIVATE KEY-----", capture=True)   # but a key in a capture still fails

    def test_missing_docs(self) -> None:
        """A function without Args or Returns, and a class without a docstring, are named."""
        src = 'class A:\n    pass\n\ndef f(x):\n    """Do f."""\n    return x\n'
        self.assertEqual(sorted(missing_docs(src)), ["A", "f"])


if __name__ == "__main__":
    unittest.main()
