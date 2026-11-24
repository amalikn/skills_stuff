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
        self.assertIn("**Decision:** v2", a["body"])
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
        self.assertIn("**Decision:** Chris is out of scope.", items["DL-001"]["body"])
        self.assertIn("**Reason:** Retail work; no enterprise role.", items["DL-001"]["body"])
        self.assertIn("**Superseded by:** DL-003", items["DL-001"]["body"])
        self.assertEqual([items[k]["status"] for k in ("DL-001", "DL-002", "DL-003")], ["superseded", "deferred", "accepted"])

    def test_points_one_per_line(self):
        """A row whose points are split by <br> shows one point per line, a blank line where the list starts and ends, and a title cut at the first break.

        Returns:
            None.
        """
        log = ("| ID     | Date       | Kind    | Decision                                         | Reason | Who |\n"
               "| ------ | ---------- | ------- | ------------------------------------------------ | ------ | --- |\n"
               "| DL-009 | 2026-11-24 | process | Two answers:<br>- one: A.<br>- two: B.<br>Advice followed. | Why.   | Op. |\n")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decision-log.md"
            path.write_text(log)
            item = pdm.log_items(path)[0]
        self.assertIn("**Decision:**\nTwo answers:\n\n- one: A.\n- two: B.\n\nAdvice followed.\n\n**Reason:** Why.", item["body"])
        self.assertEqual(item["title"], "DL-009: Two answers:")
        self.assertNotIn("<br>", item["body"])


class Architecture(unittest.TestCase):
    """architecture_items() reads the decision bullets of a Key decisions section."""

    def test_bullets(self):
        """Register ids, slugs, open decisions, wrapped lines, skipped status notes and the Superseded list.

        Returns:
            None.
        """
        doc = ("# Arch\n\n## Key decisions\n\nIntro line.\n\n"
               "- **D1 — shape: DECIDED 2026-09-21.** Central collector;\n  edge kept as fallback.\n"
               "- **D7 — provisioning: still open** (CONTESTED); built on D7.1 2026-09-30.\n"
               "- **Real-hardware verification status.** Polled once.\n"
               "- **WAN uplinks and their carriers (operator, 2026-10-08):** each uplink is a Circuit.\n"
               "- **A very long decision title that runs well past the forty eight character slug cap: DECIDED 2026-10-01.** Text.\n\n"
               "### Superseded (kept as history)\n\n- **Custom controller: DECIDED 2026-09-01.** Old.\n")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ARCHITECTURE.md"
            path.write_text(doc)
            items, skipped = pdm.architecture_items(path)
        by = {i["ref"]: i for i in items}
        self.assertEqual(skipped, ["Real-hardware verification status"])
        self.assertEqual(by["D1"]["title"], "D1: shape")
        self.assertIn("**Detail:** Central collector; edge kept as fallback.", by["D1"]["body"])
        self.assertEqual((by["D7"]["status"], by["D7"]["date"]), ("deferred", "2026-09-30"))
        self.assertEqual(by["ARCH-wan-uplinks-and-their-carriers"]["title"], "WAN uplinks and their carriers")
        self.assertIn("ARCH-a-very-long-decision-title-that-runs-well-past", by)
        self.assertNotIn("ARCH-custom-controller", by)
        self.assertEqual(len(items), 4)


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

    def test_orphans(self):
        """A Pad item whose ref left the source is listed; present refs are not.

        Returns:
            None.
        """
        self.assertEqual(pdm.orphans([{"ref": "D1"}], {"D1": "DECIS-1", "ARCH-old-name": "DECIS-2"}), [("ARCH-old-name", "DECIS-2")])


if __name__ == "__main__":
    unittest.main()


class LinkBodies(unittest.TestCase):
    """Mirrored bodies carry wiki-links (2026-11-23: decision items had bare refs, which each sync overwrote)."""

    def test_refs_and_other_decisions_become_links_but_not_self(self):
        want = [{"ref": "DL-191", "body": "**Serves:** DECISION-LOG.md (DL-191)\n\n**Decision:** Operator (FR-275), after DL-190; FR-999 unknown; `TASK-1` code."}]
        out = pdm.link_bodies(want, {"DL-191": "DEC-7"}, {"FR-275", "TASK-1", "DEC-7", "DEC-6"}, {"DL-191": "DEC-7", "DL-190": "DEC-6"})
        body = out[0]["body"]
        self.assertIn("[[FR-275]]", body)
        self.assertIn("[[DEC-6|DL-190]]", body)
        self.assertIn("(DL-191)", body, "never links to itself")
        self.assertNotIn("[[FR-999]]", body, "only refs that exist")
        self.assertIn("`TASK-1`", body, "code spans left alone")


class UpdateDiff(unittest.TestCase):
    """update_diff() names the item and shows a trailing-space difference quoted."""

    def test_trailing_space_is_visible(self):
        """A body that differs only by a trailing space shows the space.

        Returns:
            None.
        """
        out = pdm.update_diff({"ref": "DL-1", "body": "**Decision:**\nA"}, "DECIS-9", "**Decision:** \nA")
        self.assertIn("update DL-1 (DECIS-9):", out)
        self.assertIn("'-**Decision:** '", out)
