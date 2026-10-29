"""Prove the package checker passes a minimal well-formed skill and fails each governance claim when it is broken.

Usage: just test (or: <venv python> -B -m unittest discover -s tests -v)
Temporary skill folders are isolated and removed by the standard library.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_package.py"
HEADER = "---\nTitle: t\nCategory: c\nStatus: current\nAuthority: a\nScope: s\nLast reviewed: 2026-10-29\nSummary: s\n---\n\n"


def build(root):
  """Write a minimal skill that satisfies every check.

  Args:
    root: Empty directory named like a skill.
  Returns:
    None.
  """
  (root / "references").mkdir()
  (root / "scripts").mkdir()
  (root / "SKILL.md").write_text(f"---\nname: {root.name}\ndescription: d\n---\n\nSee [runbook](RUNBOOK.md) and [a](references/a.md).\n")
  for name in ("AGENTS.md", "CLAUDE.md", "CHANGELOG.md", "SCRATCHPAD.md", "README.md"):
    (root / name).write_text(HEADER + "# x\n")
  (root / "RUNBOOK.md").write_text(HEADER + "Route: [a](references/a.md). Run `just check`.\n")
  (root / "references" / "a.md").write_text(HEADER + "# a\n")
  (root / "scripts" / "README.md").write_text(HEADER + "| [tool.py](tool.py) |\n")
  (root / "scripts" / "tool.py").write_text('"""Tool."""\n\n\ndef run(x):\n  """Run.\n\n  Args:\n    x: Input.\n  Returns:\n    x.\n  """\n  return x\n')
  (root / "justfile").write_text("check:\n    true\n")
  (root / ".mise.toml").write_text('[tools]\npython = "3.14"\n')
  (root / "sources.json").write_text('{"schema_version": 1, "sources": [{"id": "X", "url": "https://example.org/doc", "evidence": "CITED"}]}')
  (root / "references" / "a.md").write_text(HEADER + "# a\n\nSee [doc](https://example.org/doc).\n")


def run(root):
  """Run the checker on a folder.

  Args:
    root: Skill folder.
  Returns:
    Pair of exit code and the findings list.
  Raises:
    subprocess.TimeoutExpired: If the checker exceeds five seconds.
  """
  result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(root)], capture_output=True, text=True, timeout=5, check=False)
  return result.returncode, json.loads(result.stdout).get("findings", [])


class CheckPackageTests(unittest.TestCase):
  """Each governance claim fails when broken and passes when kept."""

  def test_minimal_skill_passes(self):
    """A minimal well-formed skill has no findings, and dot folders are ignored.

    Args:
      None.
    Returns:
      None.
    """
    with tempfile.TemporaryDirectory() as directory:
      root = Path(directory) / "skill-demo"
      root.mkdir()
      build(root)
      (root / ".remember").mkdir()
      (root / ".remember" / "notes.md").write_text("no header")
      self.assertEqual(run(root), (0, []))

  def test_each_broken_claim_is_found(self):
    """Unrouted reference, uncatalogued script, unknown recipe, missing docstring sections and a missing file each fail.

    Args:
      None.
    Returns:
      None.
    """
    breakers = {
      "reference not routed in SKILL.md": lambda root: (root / "references" / "b.md").write_text(HEADER + "# b\n"),
      "script not catalogued": lambda root: (root / "scripts" / "other.py").write_text('"""Other."""\n'),
      "does not define": lambda root: (root / "RUNBOOK.md").write_text(HEADER + "[a](references/a.md) `just deploy`\n"),
      "lacks Args/Returns": lambda root: (root / "scripts" / "tool.py").write_text('"""Tool."""\n\n\ndef run(x):\n  """Run."""\n  return x\n'),
      "missing required file": lambda root: (root / "SCRATCHPAD.md").unlink(),
      "diagram not ASCII": lambda root: (root / "references" / "a.md").write_text(HEADER + "```text\n+--+ \u2192 x\n```\n"),
      "diagram wider than": lambda root: (root / "references" / "a.md").write_text(HEADER + "```text\n" + "-" * 111 + "\n```\n"),
      "line over 200": lambda root: (root / "references" / "a.md").write_text(HEADER + "word " * 41 + "\n"),
      "bare RFC link": lambda root: (root / "references" / "a.md").write_text(HEADER + "See https://www.rfc-editor.org/rfc/rfc7454 now.\n"),
      "source not in sources.json": lambda root: (root / "references" / "a.md").write_text(HEADER + "See https://example.org/other here.\n"),
      "contraction": lambda root: (root / "references" / "a.md").write_text(HEADER + "Do not say it isn't so.\n"),
      "broken or external local link": lambda root: (root / "SKILL.md").write_text(f"---\nname: {root.name}\ndescription: d\n---\n\n[x](nope.md)\n"),
    }
    for expected, breaker in breakers.items():
      with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "skill-demo"
        root.mkdir()
        build(root)
        breaker(root)
        code, findings = run(root)
        self.assertEqual(code, 1, findings)
        self.assertTrue(any(expected in finding for finding in findings), findings)


if __name__ == "__main__":
  unittest.main()
