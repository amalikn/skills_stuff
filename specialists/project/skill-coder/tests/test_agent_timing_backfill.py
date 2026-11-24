"""Offline tests for scripts/agent_timing_backfill.py on a hand-built transcript: a tool call, an AskUserQuestion answer and an operator wait.

Run: `just test` (unittest, the project's own interpreter).
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_path = Path(__file__).resolve().parents[1] / "scripts" / "agent_timing_backfill.py"
_spec = importlib.util.spec_from_file_location("agent_timing_backfill", _path)
atb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(atb)


def _entry(stamp: str, kind: str, content) -> str:
  """One transcript line.

  Args:
    stamp: the ISO time.
    kind: "user" or "assistant".
    content: the message content.

  Returns:
    The JSON line.
  """
  return json.dumps({"type": kind, "timestamp": stamp, "message": {"content": content}})


class Events(unittest.TestCase):
  """events_of() turns tool use and result pairs into timed events and a long silence before a prompt into a wait."""

  def test_tool_answer_and_wait(self) -> None:
    """A Bash call of 30 s, an AskUserQuestion of 90 s (operator_answer) and a 120 s wait before the next prompt."""
    lines = [
      _entry("2026-11-24T05:00:00Z", "user", "do the thing"),
      _entry("2026-11-24T05:00:05Z", "assistant", [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"description": "List files"}}]),
      _entry("2026-11-24T05:00:35Z", "user", [{"type": "tool_result", "tool_use_id": "t1"}]),
      _entry("2026-11-24T05:00:40Z", "assistant", [{"type": "tool_use", "id": "t2", "name": "AskUserQuestion", "input": {}}]),
      _entry("2026-11-24T05:02:10Z", "user", [{"type": "tool_result", "tool_use_id": "t2"}]),
      _entry("2026-11-24T05:02:15Z", "assistant", [{"type": "text", "text": "done"}]),
      _entry("2026-11-24T05:04:15Z", "user", "next"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp) / "s1.jsonl"
      path.write_text("\n".join(lines) + "\n")
      window = (atb.epoch("2026-11-24T00:00:00Z"), atb.epoch("2026-11-25T00:00:00Z"))
      events = atb.events_of(path, "s1", "", window, 60)
    kinds = sorted(e["kind"] for e in events)
    self.assertEqual(kinds, ["operator_answer", "operator_wait", "tool"])
    tool = next(e for e in events if e["kind"] == "tool")
    self.assertEqual((tool["name"], round(tool["seconds"])), ("List files", 30))
    wait = next(e for e in events if e["kind"] == "operator_wait")
    self.assertEqual(round(wait["seconds"]), 120)

  def test_label_prefers_description_and_is_short(self) -> None:
    """The label is the description, else the first 120 characters of the command."""
    self.assertEqual(atb.label("Bash", {"description": "Run tests", "command": "x"}), "Run tests")
    self.assertEqual(len(atb.label("Bash", {"command": "y" * 300})), 120)


if __name__ == "__main__":
  unittest.main()
