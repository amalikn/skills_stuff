"""Offline tests for pad_decisions.py: ledger folding, versions, decision-log rows, recommendation reading and the create/update split. Run: python3 -m unittest test_pad_decisions."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_decisions", Path(__file__).resolve().parents[1] / "scripts" / "pad_decisions.py")
pdm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pdm)


def write_project(root: Path) -> None:
    """Write a two-conflict ledger and a decision log into a temporary project.

    Args:
        root: the project folder.

    Returns:
        None.
    """
    kc = root / ".kc"
    kc.mkdir()
    decisions = [
        {"conflict_id": "cf-aaaaaaaaaa", "decision_id": "dr-111111111111", "decided_at": "2026-11-01T10:00:00+11:00", "action": "DEFER", "reason": "later"},
        {"conflict_id": "cf-aaaaaaaaaa", "decision_id": "dr-222222222222", "decided_at": "2026-11-18T10:00:00+11:00", "action": "USE_OTHER", "answer_text": "B",
         "reason": "Answered; went against the (Recommended) option.", "current_claims": ["cl-1"], "superseded_claims": ["cl-2"]},
        {"conflict_id": "cf-bbbbbbbbbb", "decision_id": "dr-333333333333", "decided_at": "2026-11-18T11:00:00+11:00", "action": "DEFER", "reason": "followed the (Recommended) option"},
    ]
    (kc / "decisions.jsonl").write_text("\n".join(json.dumps(d) for d in decisions) + "\n")
    (kc / "conflicts.jsonl").write_text(json.dumps({"conflict_id": "cf-aaaaaaaaaa", "question": "Cancel or abort?", "severity": "P2", "topic_key": "contracts.api"}) + "\n")
    log = root / "DECISION-LOG.md"
    log.write_text("| DL-011 | 2026-11-18 | architecture | Operator: NAS pulls; followed the recommendation. | Single host. | Operator. |\n"
                   "| DL-001 | 2026-10-30 | process | Hash entries. | Proof. | - |\n")


class Build(unittest.TestCase):
    """Desired items from the project's records."""

    def test_items(self):
        """Versions, status, recommendation and decision-log rows come out right.

        Returns:
            None.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(root)
            items = {i["ref"]: i for i in pdm.conflict_items(root / ".kc") + pdm.log_items(root / "DECISION-LOG.md")}
        self.assertEqual(sorted(items), ["DL-001", "DL-011", "cf-aaaaaaaaaa", "cf-bbbbbbbbbb"])
        self.assertEqual((items["DL-001"]["category"], items["DL-011"]["category"]), ("decision-log-process", "decision-log"))
        a = items["cf-aaaaaaaaaa"]
        self.assertEqual((a["status"], a["recommendation"], a["category"]), ("accepted", "not-followed", "contracts.api"))
        self.assertIn("| v1 |", a["body"])
        self.assertIn("Current: v2", a["body"])
        self.assertEqual(items["cf-bbbbbbbbbb"]["status"], "deferred")
        self.assertEqual(items["DL-011"]["recommendation"], "followed")


class WrappedAndStatus(unittest.TestCase):
    """A hook-wrapped row is read whole, and a Status column sets the Pad status (2026-11-20)."""

    def test_wrapped_rows_and_status(self):
        """Continuation rows join their cells; superseded names the replacement; deferred is kept.

        Returns:
            None.
        """
        log = ("| ID     | Date       | Kind    | Decision                   | Reason             | Status                 |\n"
               "| ------ | ---------- | ------- | -------------------------- | ------------------ | ---------------------- |\n"
               "| DL-001 | 2026-10-06 | process | Chris is out of            | Retail work; no    | superseded by DL-003   |\n"
               "|        |            |         |   scope.                   |   enterprise role. |                        |\n"
               "| DL-002 | 2026-10-07 | process | Dates wait.                | Session first.     | deferred               |\n"
               "| DL-003 | 2026-11-20 | process | Chris joins the sessions.  | Martin named him.  | accepted               |\n")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decision-log.md"
            path.write_text(log)
            items = {i["ref"]: i for i in pdm.log_items(path)}
        self.assertEqual(sorted(items), ["DL-001", "DL-002", "DL-003"])
        self.assertIn("Decision: Chris is out of scope.", items["DL-001"]["body"])
        self.assertIn("Reason: Retail work; no enterprise role.", items["DL-001"]["body"])
        self.assertIn("Superseded by: DL-003", items["DL-001"]["body"])
        self.assertEqual([items[k]["status"] for k in ("DL-001", "DL-002", "DL-003")], ["superseded", "deferred", "accepted"])


class Split(unittest.TestCase):
    """plan() creates the missing and rewrites only changed bodies."""

    def test_plan(self):
        """A missing ref is created, a changed body updated, an equal one left.

        Returns:
            None.
        """
        want = [{"ref": "a", "body": "x"}, {"ref": "b", "body": "y"}, {"ref": "c", "body": "z"}]
        creates, updates = pdm.plan(want, {"b": "DECIS-1", "c": "DECIS-2"}, {"DECIS-1": "old", "DECIS-2": "z\n"}.get)
        self.assertEqual([w["ref"] for w in creates], ["a"])
        self.assertEqual([w["ref"] for w in updates], ["b"])


if __name__ == "__main__":
    unittest.main()
