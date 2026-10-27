"""Tests for the decision rules (goal_guard_lib.decide) against references/decision-rules.md, one case per evaluation step.

Run: just test   (or: python -m unittest discover -s tests)
Safety: files only, in a temporary copy of examples/project_stuff; no network.
"""

import json
import unittest

from helpers import NOW, Workspace, lib, proposal, tasks

decide = lib("decide")


def verdict_of(ws: Workspace, prop, authorised: str = "apn"):
  """Assess a proposal against the workspace spoke.

  Args:
    ws: the workspace.
    prop: the proposal.
    authorised: the session's partition.

  Returns:
    The Verdict.
  """
  proj = ws.project()
  return decide.assess(prop, proj, ws.baseline(proj), tasks(), authorised, NOW)


class DecisionOrder(unittest.TestCase):
  """Each step of the evaluation order yields its verdict."""

  def test_proceed_in_scope(self):
    """A traceable, recorded, non-expanding proposal proceeds (T15-style happy path)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal())
    self.assertEqual((v.verdict, v.reason_code, v.contract_revision), ("PROCEED", "IN_SCOPE", "DEMO-MVP-001@1"))

  def test_cross_partition_blocks(self):
    """A session authorised for me cannot act in an apn project (PORT-005)."""
    with Workspace() as ws:
      self.assertEqual(verdict_of(ws, proposal(), authorised="me").reason_code, "CROSS_PARTITION")

  def test_file_in_other_partition_blocks(self):
    """A proposed file under the me partition blocks."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(proposed_files=["../../me/demo-personal/notes.md"]))
    self.assertEqual((v.verdict, v.reason_code), ("BLOCK", "CROSS_PARTITION"))

  def test_path_escape_reviews(self):
    """A path that leaves the project is REVIEW (GG-404)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(proposed_files=["../../../outside.txt"]))
    self.assertEqual((v.verdict, v.reason_code), ("REVIEW", "PATH_UNRESOLVED"))

  def test_missing_baseline_blocks(self):
    """No mvp.yaml blocks scope-changing work (MVP-001, T01)."""
    with Workspace() as ws:
      (ws.spoke / ".gg/mvp.yaml").unlink()
      v = verdict_of(ws, proposal())
    self.assertEqual((v.verdict, v.reason_code, v.clause), ("BLOCK", "NO_BASELINE", "MVP-001"))

  def test_draft_baseline_blocks(self):
    """A draft contract blocks (MVP-003, T02)."""
    with Workspace() as ws:
      ws.edit_yaml(".gg/mvp.yaml", status="draft")
      self.assertEqual(verdict_of(ws, proposal()).reason_code, "DRAFT")

  def test_unreadable_baseline_blocks(self):
    """An unparseable contract blocks (MVP-012, T11)."""
    with Workspace() as ws:
      (ws.spoke / ".gg/mvp.yaml").write_text("status: [unclosed\n")
      self.assertEqual(verdict_of(ws, proposal()).reason_code, "UNREADABLE")

  def test_approval_not_in_log_blocks(self):
    """status: approved without the owner's approval line in decisions.jsonl is not approved (MVP-007)."""
    with Workspace() as ws:
      (ws.spoke / ".gg/decisions.jsonl").write_text("")
      self.assertEqual(verdict_of(ws, proposal()).reason_code, "UNAPPROVED")

  def test_approval_by_other_actor_blocks(self):
    """An approval line written by someone other than the owner does not count."""
    with Workspace() as ws:
      path = ws.spoke / ".gg/decisions.jsonl"
      entry = json.loads(path.read_text())
      entry["actor"] = "claude-code"
      path.write_text(json.dumps(entry) + "\n")
      self.assertEqual(verdict_of(ws, proposal()).reason_code, "UNAPPROVED")

  def test_inspect_proceeds_without_baseline(self):
    """Read-only inspection fails open."""
    with Workspace() as ws:
      (ws.spoke / ".gg/mvp.yaml").unlink()
      v = verdict_of(ws, proposal(intent="inspect"))
    self.assertEqual((v.verdict, v.reason_code), ("PROCEED", "READ_ONLY"))

  def test_no_task_reviews(self):
    """Nontrivial work without a task is REVIEW (GG-406)."""
    with Workspace() as ws:
      self.assertEqual(verdict_of(ws, proposal(task_id=None)).reason_code, "NO_TASK")

  def test_unmapped_task_blocks(self):
    """A task mapped to no accepted criterion blocks (PORT-002, P03)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(task_id=103))
    self.assertEqual((v.verdict, v.reason_code), ("BLOCK", "TASK_UNMAPPED"))

  def test_unmet_dependency_reviews(self):
    """Task 102 waits on 101."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(task_id=102, criterion_id="AC-02"))
    self.assertEqual((v.verdict, v.details["blocked_by"]), ("REVIEW", [101]))

  def test_exclusion_blocks_whatever_it_is_called(self):
    """'Future-proofing' a dashboard is still the dashboard exclusion (MVP-004, T05)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(description="future-proof it with a small dashboard"))
    self.assertEqual((v.verdict, v.reason_code), ("BLOCK", "EXCLUDED"))

  def test_self_approval_blocks(self):
    """An approval field on a proposal blocks (MVP-007, T07)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(approved_by="claude-code"))
    self.assertEqual((v.verdict, v.reason_code), ("BLOCK", "SELF_APPROVAL"))

  def test_protected_change_blocks(self):
    """Editing the MVP outside change control blocks (MVP-011)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(proposed_files=[".gg/mvp.yaml"]))
    self.assertEqual((v.verdict, v.reason_code), ("BLOCK", "PROTECTED_CHANGE"))

  def test_no_criterion_parks(self):
    """An idea with no criterion and no blocker parks (MVP-005, T04)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(criterion_id=None))
    self.assertEqual((v.verdict, v.reason_code), ("PARK", "NO_CRITERION"))

  def test_unknown_criterion_parks(self):
    """A criterion outside the contract parks."""
    with Workspace() as ws:
      self.assertEqual(verdict_of(ws, proposal(criterion_id="AC-99")).verdict, "PARK")

  def test_false_linkage_reviews(self):
    """Task 101 is mapped to AC-01; citing AC-02 is false linkage (GG-007)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(criterion_id="AC-02"))
    self.assertEqual((v.verdict, v.reason_code), ("REVIEW", "FALSE_LINKAGE"))

  def test_necessity_unrecorded_reviews(self):
    """Missing stop condition is REVIEW (GG-412)."""
    with Workspace() as ws:
      self.assertEqual(verdict_of(ws, proposal(stop_condition=None)).reason_code, "NECESSITY_UNRECORDED")

  def test_adds_scope_reviews(self):
    """adds_scope is REVIEW (MVP-006, T06)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(adds_scope=True))
    self.assertEqual((v.verdict, v.requires_owner_approval), ("REVIEW", True))

  def test_registered_blocker_proceeds(self):
    """A blocker registered in the approved baseline proceeds (T15, GG-002)."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(criterion_id=None, necessary_blocker_id="NB-01"))
    self.assertEqual((v.verdict, v.reason_code), ("PROCEED", "IN_SCOPE"))

  def test_registered_blocker_adding_scope_reviews(self):
    """The v0.1 prototype returned PROCEED here; the settled rule is REVIEW."""
    with Workspace() as ws:
      v = verdict_of(ws, proposal(criterion_id=None, necessary_blocker_id="NB-01", adds_scope=True))
    self.assertEqual(v.verdict, "REVIEW")

  def test_unregistered_blocker_reviews(self):
    """A dependency found during execution is REVIEW until a revision (MVP-006)."""
    with Workspace() as ws:
      self.assertEqual(verdict_of(ws, proposal(criterion_id=None, necessary_blocker_id="NB-77")).reason_code, "UNREGISTERED_BLOCKER")


class RecordParsing(unittest.TestCase):
  """Record validation catches bad contracts and proposals."""

  def test_subjective_criterion_flagged(self):
    """'Scalable' is not an observable test."""
    mvp = lib("mvp").parse_mvp(
      {
        "mvp_id": "X",
        "baseline_version": 1,
        "status": "draft",
        "owner": "o",
        "outcome": "o",
        "acceptance_criteria": [{"id": "AC-1", "test": "The system is scalable"}],
      }
    )
    self.assertTrue(any("subjective" in i for i in mvp.issues))

  def test_bad_date_is_record_error(self):
    """A malformed date is a RecordError, not an uncaught ValueError (v0.1 gap)."""
    with self.assertRaises(lib("errors").RecordError):
      lib("records").parse_date("2026-13-40", "due")

  def test_vikunja_zero_date_is_none(self):
    """Vikunja's year-1 zero time means unset."""
    self.assertIsNone(lib("records").parse_date("0001-01-01T00:00:00Z", "due"))


if __name__ == "__main__":
  unittest.main()
