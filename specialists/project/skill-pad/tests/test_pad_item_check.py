"""Offline tests for pad_item_check.py: each rule of the writing standard can fail and can pass. Run: python3 -m unittest tests/test_pad_item_check.py"""

import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock

_spec = importlib.util.spec_from_file_location("pad_item_check", Path(__file__).resolve().parents[1] / "scripts" / "pad_item_check.py")
pic = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pic)

GOOD_TASK = "**Serves:** tracker S1\n\n**Why:** a finding\n\n**Do:** the step\n\n**Done when:** check passes\n\n**Writes:** repo\n\n**Refs:** a path"


def item(status: str, body: str = GOOD_TASK, collection: str = "tasks", notes: list | None = None) -> dict:
    """One item as the CLI returns it.

    Args:
        status: its status field.
        body: its body.
        collection: its collection slug.
        notes: its implementation notes.

    Returns:
        The item dict, fields as a JSON string like the CLI's.
    """
    return {"collection_slug": collection, "content": body, "fields": json.dumps({"status": status}), "implementation_notes": notes or []}


class FindingsTests(unittest.TestCase):
    """Every rule, failing and passing."""

    def test_a_standard_task_with_a_closing_comment_is_clean(self) -> None:
        """Bold labels, done with a DONE comment, no log named: nothing to report."""
        self.assertEqual(pic.findings(item("done"), [{"body": "2026-11-18 22:10 AEDT DONE:\n- **Outcome:** ran"}], 0), [])

    def test_plain_labels_are_reported(self) -> None:
        """`Serves:` without bold is the jumbled body the operator named."""
        out = pic.findings(item("open", "Serves: S1\nWhy: x\nDo: y\nDone when: z\nWrites: repo\nRefs: p"), [], 0)
        self.assertEqual(len(out), 1)
        self.assertIn("**Serves:**", out[0])
        self.assertIn("5 more", out[0])

    def test_done_without_a_closing_comment_is_reported(self) -> None:
        """A one-line status comment is not a closing statement."""
        out = pic.findings(item("done"), [{"body": "records written"}], 0)
        self.assertTrue(any(line.startswith("done:") for line in out))

    def test_in_progress_without_any_update_is_reported(self) -> None:
        """Work started and nothing written about it."""
        self.assertTrue(any(line.startswith("update:") for line in pic.findings(item("in-progress"), [], 0)))
        self.assertEqual(pic.findings(item("in-progress", notes=[{"summary": "ran case 1"}]), [], 0), [])

    def test_a_named_log_needs_an_attachment(self) -> None:
        """A log path in a comment with nothing attached fails; one attachment clears it."""
        comments = [{"body": "2026-11-18 21:20 AEDT FINDING:\n- **Evidence:** spike/out/s1-pi4-bench.log"}]
        self.assertTrue(any(line.startswith("logs:") for line in pic.findings(item("open"), comments, 0)))
        self.assertEqual(pic.findings(item("open"), comments, 1), [])

    def test_bug_and_plan_labels(self) -> None:
        """Bugs and plans have their own label sets; an unknown collection has none."""
        self.assertEqual(pic.missing_labels("bugs", "**Seen:** x\n**Evidence:** p\n**Effect:** e\n**Closure:** c"), [])
        self.assertEqual(pic.missing_labels("plans", "**Serves:** x\n**Goal:** g"), ["Done when", "Out of scope", "Waits on"])
        self.assertEqual(pic.missing_labels("ideas", "anything"), [])


class RateLimitTests(unittest.TestCase):
    """A rate-limited pad call is retried; any other failure is not."""

    def _run(self, results: list) -> tuple[str | None, int]:
        """Call pic.pad with subprocess.run faked to return `results` in order.

        Args:
            results: (returncode, stdout, stderr) per call.

        Returns:
            (stdout or None when it raised, how many calls were made).
        """
        calls = []

        def fake(cmd, **kw):
            """Record the call and hand back the next canned result."""
            calls.append(cmd)
            rc, out, err = results[len(calls) - 1]
            return mock.Mock(returncode=rc, stdout=out, stderr=err)

        with mock.patch.object(pic.subprocess, "run", side_effect=fake), mock.patch.object(pic.time, "sleep"):
            try:
                return pic.pad(["item", "show", "TASK-1"], 5), len(calls)
            except RuntimeError:
                return None, len(calls)

    def test_a_rate_limited_call_is_retried_until_it_answers(self) -> None:
        """Two refusals, then the answer."""
        limited = (1, "", 'pad-structured-error/v1: {"error":{"code":"rate_limited"}}')
        self.assertEqual(self._run([limited, limited, (0, "{}", "")]), ("{}", 3))

    def test_another_error_is_not_retried(self) -> None:
        """A missing item fails at once."""
        self.assertEqual(self._run([(1, "", "not found")]), (None, 1))

    def test_it_gives_up_after_the_retries(self) -> None:
        """Still limited after RETRIES calls: an error, not a hang."""
        limited = (1, "", "rate_limited")
        self.assertEqual(self._run([limited] * pic.RETRIES), (None, pic.RETRIES))


if __name__ == "__main__":
    unittest.main()
