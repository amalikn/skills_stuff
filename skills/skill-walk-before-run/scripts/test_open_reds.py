"""Tests for open_reds.py. Offline; fixture ledgers only, the real ledger is never read.

    python3 -m unittest discover -s scripts -p 'test_*.py'
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("open_reds", Path(__file__).resolve().parent / "open_reds.py")
o = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(o)

A = "The controller stack behaves on real hardware as on the mock: SNMP monitoring, TR-069 provisioning and the adapter"
A_NARROW = "The controller stack behaves on real hardware as on the mock: SNMP monitoring specifically"
B = "An SMC configured only from rendered intent matches one built from hand-kept files"


def red(assumption, ts, project="p", waiver=False):
    return {"ts": ts, "project": project, "verdict": "RED", "assumption": assumption, "next_test": f"test {ts}", "waiver": waiver}


def resolved(assumption, ts, project="p", result="PASS"):
    return {"ts": ts, "project": project, "verdict": "RESOLVED", "assumption": assumption, "result": result, "killed": "none"}


class OpenRedsTest(unittest.TestCase):
    def test_every_open_assumption_is_listed_not_only_one(self):
        found = o.open_reds([red(A, "1"), red(B, "2")], "p")
        self.assertEqual([r["assumption"] for r in found], [A, B])

    def test_a_restating_resolved_closes_it_even_with_different_whitespace(self):
        found = o.open_reds([red(A, "1"), red(B, "2"), resolved("  " + B.replace(" ", "  "), "3")], "p")
        self.assertEqual([r["assumption"] for r in found], [A])

    def test_a_narrower_resolved_leaves_the_red_open_and_is_shown_as_partial(self):
        found = o.open_reds([red(A, "1"), resolved(A_NARROW, "2")], "p")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["partial"][0]["assumption"], A_NARROW)

    def test_other_projects_are_ignored(self):
        self.assertEqual(o.open_reds([red(A, "1", project="q")], "p"), [])

    def test_waivers_are_counted_and_a_reopened_red_keeps_its_first_date(self):
        found = o.open_reds([red(A, "1", waiver=True), red(A, "2", waiver=True)], "p")
        self.assertEqual((found[0]["opened"], found[0]["waivers"], found[0]["next_test"]), ("1", 2, "test 2"))

    def test_a_red_after_its_resolution_is_open_again(self):
        found = o.open_reds([red(A, "1"), resolved(A, "2"), red(A, "3")], "p")
        self.assertEqual([r["opened"] for r in found], ["3"])

    def test_a_malformed_line_is_skipped_not_fatal(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "ledger.jsonl"
            path.write_text(json.dumps(red(A, "1")) + "\nnot json\n" + json.dumps(red(B, "2")) + "\n", encoding="utf-8")
            self.assertEqual(len(o.open_reds(o.read_entries(path), "p")), 2)


if __name__ == "__main__":
    unittest.main()
