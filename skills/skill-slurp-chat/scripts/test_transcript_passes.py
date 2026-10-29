"""Offline tests for transcript_passes.py: typed turns that the client prefixes with IDE or harness blocks must still reach pass 1.

Run: `python3 -m unittest scripts/test_transcript_passes.py` from the skill folder (stdlib only).
"""

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
tp = __import__("transcript_passes")


def write_transcript(rows: list[dict]) -> pathlib.Path:
    """Write rows as a JSONL transcript in a temporary file.

    Args:
        rows: transcript records.

    Returns:
        The file's path.
    """
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    for r in rows:
        f.write(json.dumps(r) + "\n")
    f.close()
    return pathlib.Path(f.name)


class SubagentPassTest(unittest.TestCase):
    """Pass 3: the session's sub-agents, read from their own transcripts (operator, 2026-10-29)."""

    def test_subagent_report_and_side_effects_are_listed(self) -> None:
        """An agent's task and final report come out as `subagent`; its Bash call as `sub-bash`."""
        with tempfile.TemporaryDirectory() as tmp:
            session = pathlib.Path(tmp) / "s1.jsonl"
            session.write_text("")
            folder = pathlib.Path(tmp) / "s1" / "subagents"
            folder.mkdir(parents=True)
            (folder / "agent-x.meta.json").write_text(json.dumps({"agentType": "general-purpose", "description": "Check a fact"}))
            rows = [{"type": "assistant", "timestamp": "2026-10-29T01:00:00Z",
                     "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": "ls", "description": "List files"}}]}},
                    {"type": "assistant", "timestamp": "2026-10-29T01:01:00Z", "message": {"content": [{"type": "text", "text": "Found: X is true."}]}}]
            (folder / "agent-x.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
            got = list(tp.subagent_events(session))
        self.assertIn(("2026-10-29T01:00:00Z", "subagent", "general-purpose: Check a fact -> Found: X is true."), got)
        self.assertTrue(any(kind == "sub-bash" for _, kind, _ in got), got)


class TypedTextTest(unittest.TestCase):
    """typed_text and the pass-1 events built on it."""

    def test_slash_command_reaches_pass_one(self) -> None:
        """A /skill invocation, stored as command tags, is listed as the user typed it (missed before 2026-10-27)."""
        text = "<command-message>skill-ai-it</command-message>\n<command-name>/skill-ai-it</command-name>\n<command-args>promote and approve all</command-args>"
        self.assertEqual(tp.slash_command(text), "/skill-ai-it promote and approve all")
        self.assertEqual(tp.slash_command("plain words"), "")
        path = write_transcript([{"type": "user", "timestamp": "2026-10-27T07:00:00Z", "message": {"role": "user", "content": text}}])
        self.assertIn(("2026-10-27T07:00:00Z", "user", "/skill-ai-it promote and approve all"), list(tp.events(path)))

    def test_ide_block_before_text_is_dropped(self) -> None:
        """A two-block turn (IDE note, then the message) yields the message."""
        content = [{"type": "text", "text": "<ide_opened_file>The user opened x.md</ide_opened_file>"}, {"type": "text", "text": "Ask me questions."}]
        self.assertEqual(tp.typed_text(content), "Ask me questions.")

    def test_inline_tag_prefix_is_dropped(self) -> None:
        """A single string with a leading tag block yields the text after it."""
        self.assertEqual(tp.typed_text("<ide_selection>sel</ide_selection>\nyes but slurp"), "yes but slurp")

    def test_pasted_block_and_typed_words_are_kept(self) -> None:
        """A pasted block (with attributes) after an IDE note is operator input: kept as [pasted], with the typed words after it (2026-10-21)."""
        content = [{"type": "text", "text": "<ide_opened_file>f</ide_opened_file>"},
                   {"type": "text", "text": '\n\n<pasted_content id="7419">\nA note\n</pasted_content id="7419">\n\nCatalog it.'}]
        self.assertEqual(tp.typed_text(content), "[pasted] A note\n\nCatalog it.")

    def test_tag_only_turn_is_empty(self) -> None:
        """A turn that is only a harness block yields nothing."""
        self.assertEqual(tp.typed_text("<system-reminder>x</system-reminder>"), "")

    def test_prefixed_turn_reaches_pass_one(self) -> None:
        """events() reports a typed turn that starts with an IDE block."""
        path = write_transcript([{
            "type": "user",
            "timestamp": "2026-10-14T03:46:00Z",
            "message": {"content": [{"type": "text", "text": "<ide_opened_file>f</ide_opened_file>"}, {"type": "text", "text": "Ask me questions."}]},
        }])
        kinds = [(k, t) for _, k, t in tp.events(path)]
        self.assertIn(("user", "Ask me questions."), kinds)

    def test_codex_events_preserve_repeated_turns_and_hide_tool_arguments(self) -> None:
        """Read Codex event envelopes without duplicating mirrored messages or printing command secrets.

        Args:
            None.
        Returns:
            None; assertions fail on missing Codex messages, compaction or tool labels.
        """
        rows = [
            {"type": "event_msg", "payload": {"type": "user_message", "message": "check"}},
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "check"}]}},
            {"type": "event_msg", "payload": {"type": "user_message", "message": "check"}},
            {"type": "compacted", "payload": {}},
            {"type": "response_item", "payload": {"type": "custom_tool_call", "name": "exec", "input": 'await tools.exec_command({cmd:"secret-value"}); await tools.mcp__memory_keeper__context_save({value:"private"});'}},
            {"type": "response_item", "payload": {"type": "function_call", "name": "functions.exec", "arguments": json.dumps({"code": "await tools.apply_patch('private patch body');"})}},
        ]
        for index, row in enumerate(rows):
            row["timestamp"] = f"2026-10-16T10:00:0{index}Z"
        path = write_transcript(rows)
        self.addCleanup(path.unlink)
        found = list(tp.events(path))
        self.assertEqual([text for _, kind, text in found if kind == "user"], ["check", "check"])
        self.assertEqual(sum(kind == "compaction" for _, kind, _ in found), 1)
        tools = [text for _, kind, text in found if kind == "tool"]
        self.assertEqual(len(tools), 2)
        self.assertIn("exec_command", tools[0])
        self.assertIn("mcp__memory_keeper__context_save", tools[0])
        self.assertIn("apply_patch", tools[1])
        self.assertNotIn("secret-value", str(found))
        self.assertNotIn("private", str(found))
        self.assertEqual(len(list(tp.events(path, "2026-10-16T10:00:04"))), 2)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(tp.main(["--transcript", str(path), "--pass", "2"]), 0)
        self.assertIn("tool", output.getvalue())
        self.assertNotIn("secret-value", output.getvalue())


if __name__ == "__main__":
    unittest.main()
