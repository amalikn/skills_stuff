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
        self.assertEqual(pic.missing_labels("playbooks", "anything"), [])

    def test_templates_for_every_collection(self) -> None:
        """Tech debt, ideas, asks, decisions and conventions have required labels (operator, 2026-11-20)."""
        self.assertEqual(pic.missing_labels("ideas", "anything"), ["Serves", "Why", "Do"])
        self.assertEqual(pic.missing_labels("asks", "**Question:** which?"), [])
        self.assertEqual(pic.missing_labels("decisions", "**Serves:** log\n\n**Decision:** d"), [])
        self.assertEqual(pic.missing_labels("conventions", "Commit with just commit-project."), ["Rule", "Source"])

    def test_a_one_line_feature_request_keeps_the_operators_words(self) -> None:
        """A request whose body is its title needs no labels; a longer body does."""
        one = dict(item("submitted", "link test for PtP\n", "feature-requests"), title="link test for PtP")
        self.assertEqual(pic.findings(one, [], 0), [])
        cut = dict(item("submitted", "a long request " * 10, "feature-requests"), title=("a long request " * 10)[:100])
        self.assertEqual(pic.findings(cut, [], 0), [])
        long = dict(item("submitted", "link test for PtP\nmore detail here", "feature-requests"), title="link test for PtP")
        self.assertTrue(any(line.startswith("labels:") for line in pic.findings(long, [], 0)))

    def test_a_source_ledger_is_not_a_log(self) -> None:
        """A decision naming its .jsonl ledger needs no attachment; a task naming a log does (2026-11-20: 102 false findings in continuum)."""
        dec = item("accepted", "**Serves:** .kc/decisions.jsonl (cf-1)\n\n**Decision:** d", "decisions")
        self.assertEqual(pic.findings(dec, [], 0), [])
        self.assertTrue(any(x.startswith("logs:") for x in pic.findings(item("open", GOOD_TASK + " run.log"), [], 0)))

    def test_closing_comment_only_on_work(self) -> None:
        """A closed tech-debt item needs a DONE comment; an accepted decision and a shipped request do not."""
        td = item("resolved", "**Serves:** s\n\n**Why:** w\n\n**Do:** d\n\n**Done when:** x", "tech-debt")
        self.assertTrue(any(line.startswith("done:") for line in pic.findings(td, [], 0)))
        dec = item("accepted", "**Serves:** log\n\n**Decision:** d", "decisions")
        self.assertEqual(pic.findings(dec, [], 0), [])
        fr = dict(item("shipped", "ping devices", "feature-requests"), title="ping devices")
        self.assertEqual(pic.findings(fr, [], 0), [])


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



class CommentFormAndRefsTests(unittest.TestCase):
    """The update form of comments and references as links (operator, 2026-11-20)."""

    def test_a_long_plain_comment_from_today_is_reported(self) -> None:
        """A 300-character paragraph with no bullet line fails the form."""
        c = [{"id": "86e9c9f3-x", "created_at": "2026-11-20T10:49:00Z", "body": "Started: " + "word " * 60}]
        out = pic.findings(item("in-progress"), c, 0)
        self.assertTrue(any(line.startswith("comments: 1 long comment") and "86e9c9f3" in line for line in out), out)

    def test_bullets_short_lines_and_old_comments_pass_the_form(self) -> None:
        """Bullets pass; a short status line passes; a long comment from before 2026-11-18 is not judged."""
        c = [
            {"created_at": "2026-11-20T10:49:00Z", "body": "2026-11-20 21:49 AEDT start:\n- **What:** " + "word " * 60},
            {"created_at": "2026-11-20T10:50:00Z", "body": "Done: see the DONE comment"},
            {"created_at": "2026-11-10T10:00:00Z", "body": "old " * 80},
        ]
        self.assertFalse(any(line.startswith("comments:") for line in pic.findings(item("in-progress"), c, 0)))

    def test_plain_references_are_reported_and_links_pass(self) -> None:
        """TASK-207 and DL-071 as text fail; [[TASK-207]], [[DECIS-177|DL-071]] and `TASK-9` in code pass."""
        bad = pic.findings(item("open", GOOD_TASK + "\nSee TASK-207 and DL-071."), [], 0)
        self.assertTrue(any(line.startswith("refs: TASK-207, DL-071") for line in bad), bad)
        good = pic.findings(item("open", GOOD_TASK + "\nSee [[TASK-207]], [[DECIS-177|DL-071]] and `TASK-9`."), [], 0)
        self.assertFalse(any(line.startswith("refs:") for line in good), good)

    def test_comment_refs_count_from_the_links_rule_and_decisions_are_skipped(self) -> None:
        """A plain ref in a comment of 2026-11-20 fails, one from 2026-11-19 does not; a decision mirror is never judged."""
        new = [{"created_at": "2026-11-20T01:00:00Z", "body": "- **Next:** feeds TASK-53"}]
        old = [{"created_at": "2026-11-19T01:00:00Z", "body": "- **Next:** feeds TASK-53"}]
        self.assertTrue(any(line.startswith("refs: TASK-53") for line in pic.findings(item("open"), new, 0)))
        self.assertFalse(any(line.startswith("refs:") for line in pic.findings(item("open"), old, 0)))
        self.assertFalse(any(line.startswith("refs:") for line in pic.findings(item("accepted", "From TASK-5", "decisions"), [], 0)))

    def test_refs_to_items_outside_the_workspace_are_not_judged(self) -> None:
        """Another workspace's BUG-197 cannot be a link here; a ref of this workspace still counts."""
        out = pic.findings(item("open", GOOD_TASK + "\nunc files it as Pad BUG-197 there; see TASK-5."), [], 0, known={"TASK-5"})
        self.assertTrue(any(line.startswith("refs: TASK-5") for line in out), out)
        self.assertFalse(any("BUG-197" in line for line in out), out)

    def test_decision_ids_are_not_judged_without_a_decisions_collection(self) -> None:
        """In a workspace with no Decisions collection a DL id cannot be a link; item refs still count."""
        out = pic.findings(item("open", GOOD_TASK + "\nsmc-resiliency DL-107; see TASK-5."), [], 0, decision_ids=False)
        self.assertTrue(any(line.startswith("refs: TASK-5") for line in out), out)
        self.assertFalse(any("DL-107" in line for line in out), out)

if __name__ == "__main__":
    unittest.main()
