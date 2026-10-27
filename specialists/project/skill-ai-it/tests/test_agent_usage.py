"""Offline tests for scripts/survey/agent_usage.py --md-reads: outline greps, recipe calls and whole/ranged Markdown Reads are counted per project."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "survey" / "agent_usage.py"
_spec = importlib.util.spec_from_file_location("agent_usage", SCRIPT)
au = importlib.util.module_from_spec(_spec)
sys.modules["agent_usage"] = au
_spec.loader.exec_module(au)


def call(name: str, **inp: object) -> str:
    """One transcript line holding a single tool call.

    Args:
        name: the tool name.
        inp: the tool input.

    Returns:
        The JSON line.
    """
    return json.dumps({"message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}}) + "\n"


class MdReadsTest(unittest.TestCase):
    """md_reads() on a fake transcripts folder."""

    def test_counts_by_kind_and_project(self) -> None:
        """Each kind of read lands in its own count; a subagent transcript counts; another project's does not."""
        with tempfile.TemporaryDirectory() as root:
            proj = Path(root) / "-x-unified-network-controller"
            (proj / "s1" / "subagents").mkdir(parents=True)
            (proj / "a.jsonl").write_text(call("Bash", command="grep -n '^#' docs/x.md") + call("Read", file_path="/p/x.md")
                                          + call("Read", file_path="/p/x.md", offset=10, limit=5) + call("Read", file_path="/p/x.py"))
            (proj / "s1" / "subagents" / "b.jsonl").write_text(call("Bash", command='just section docs/x.md "Stage 1"'))
            other = Path(root) / "-x-other"
            other.mkdir()
            (other / "c.jsonl").write_text(call("Bash", command="grep -n '^#' y.md"))
            got = au.md_reads(30, "unified-network-controller", root)
        self.assertEqual(got, {"transcripts": 2, "outline_greps": 1, "outline_grep_sessions": 1, "recipe_calls": 1, "recipe_sessions": 1,
                               "md_read_whole": 1, "md_read_ranged": 1})


if __name__ == "__main__":
    unittest.main()
