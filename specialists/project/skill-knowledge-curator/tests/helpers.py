"""Shared test helpers: a throwaway copy of the pilot fixture and a pipeline runner over the CLI's main().

Imported by the tests, not run. scripts/ is put on sys.path and modules are loaded with importlib so test files keep their imports
at the top (skill-coder languages/python.md, Learned 2026-10-19). Safety: files only, under a temporary folder.
"""

import contextlib
import importlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"
if str(SCRIPTS) not in sys.path:
  sys.path.insert(0, str(SCRIPTS))

CLI = importlib.import_module("knowledge_curator")
CONTEXT_SECTIONS = ("AGENTS.md", "docs/notes.md", "docs/ops-runbook.md", "docs/ops-runbook-copy.md")


def lib(name: str):
  """Import one knowledge_curator_lib module.

  Args:
    name: module name, e.g. "state".

  Returns:
    The module.
  """
  return importlib.import_module(f"knowledge_curator_lib.{name}")


class PilotCase:
  """Mixin giving each test a fresh copy of tests/fixtures/pilot as self.root (folder name "pilot", so IDs match the fixtures)."""

  def setUp(self):
    """Copy the fixture."""
    self._tmp = tempfile.TemporaryDirectory(prefix="kc-test-")
    self.root = Path(self._tmp.name) / "pilot"
    shutil.copytree(FIXTURES / "pilot", self.root)

  def tearDown(self):
    """Remove the copy."""
    self._tmp.cleanup()

  def kc(self, *argv: str) -> tuple[int, dict | str, str]:
    """Run one kc command against the copy.

    Args:
      *argv: command and options (--project is added).

    Returns:
      (exit code, parsed JSON stdout or raw text, stderr).
    """
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
      try:
        code = CLI.main([argv[0], "--project", str(self.root), *argv[1:]])
      except SystemExit as exc:
        code = exc.code
    text = out.getvalue()
    try:
      return code, json.loads(text), err.getvalue()
    except json.JSONDecodeError:
      return code, text, err.getvalue()

  def state(self):
    """Fold the copy's ledgers.

    Returns:
      A State.
    """
    return lib("state").load(self.root)

  def mark_context(self) -> None:
    """Mark the fixture's non-claim sections as context, as an agent would."""
    st = self.state()
    rows = [r for r in lib("claims").coverage(st)["sections"] if r["status"] == "pending" and r["path"] in CONTEXT_SECTIONS]
    recs = [
      {"record": "section_status", "section_id": r["section_id"], "status": "context", "reason": "navigation or imperative text; data only"} for r in rows
    ]
    path = self.root.parent / "context.json"
    path.write_text(json.dumps(recs))
    code, _, err = self.kc("claims", "--file", str(path), "--apply")
    assert code == 0, err

  def pipeline(self, stage: str = "related") -> None:
    """Run the pipeline up to a stage.

    Args:
      stage: "inventoried", "claimed", "related" or "decided".
    """
    steps = [
      ("inventoried", [("init", "--apply"), ("inventory", "--apply")]),
      ("claimed", [("claims", "--file", str(FIXTURES / "pilot-claims.json"), "--apply")]),
      ("related", [("relate", "--file", str(FIXTURES / "pilot-relations.json"), "--apply")]),
    ]
    for name, cmds in steps:
      for cmd in cmds:
        code, _, err = self.kc(*cmd)
        assert code == 0, f"{cmd}: {err}"
      if name == stage:
        return
    if stage == "decided":
      cf = self.conflict_for("backups.schedule")
      code, _, err = self.kc("decide", cf, "ACCEPT_RECOMMENDATION", "--reason", "requirement governs", "--apply")
      assert code == 0, err

  def conflict_for(self, topic: str) -> str:
    """ID of the open conflict on a topic.

    Args:
      topic: topic key.

    Returns:
      The conflict ID.
    """
    return next(c["conflict_id"] for c in self.state().conflicts.values() if c["topic_key"] == topic)

  def claim_for(self, text: str) -> str:
    """ID of the claim with the given text.

    Args:
      text: claim_text.

    Returns:
      The claim ID.
    """
    return next(cid for cid, c in self.state().claims.items() if c["claim_text"] == text)
