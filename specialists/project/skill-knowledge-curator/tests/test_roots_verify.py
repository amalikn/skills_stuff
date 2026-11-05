"""kc roots and kc verify (research B3, B4): grouping by cause, citation-constrained verdicts, guarded bulk confirmation, the model seam.

Each test failed before its feature existed. The model is replaced by a fake in these tests; the real oMLX run is measured in
references/evaluation.md.

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies; no network.
"""

import contextlib
import importlib
import io
import json
import unittest
from unittest import mock

from helpers import FixCase, lib, make_claim

ROOT_PATH = "/srv/data/mcp-root"


class Case(FixCase):
  """Pilot copy with helpers for one conflict between two new documents."""

  def pair(self, name: str, left: str, right: str, severity: str = "P1", topic: str = "t.t", **scopes) -> str:
    """Two one-line documents, a claim each, and an open conflict between them.

    Args:
      name: document name prefix.
      left: first claim text.
      right: second claim text.
      severity: conflict severity.
      topic: topic key.
      **scopes: optional scope_a and scope_b.

    Returns:
      The conflict ID.
    """
    p1, p2 = self.add_doc(f"{name}-a.md", ["# A", "", left]), self.add_doc(f"{name}-b.md", ["# B", "", right])
    recs = [
      make_claim(p1, 3, left, f"{name} subject", "is", left[-12:], topic, scope=scopes.get("scope_a", {})),
      make_claim(p2, 3, right, f"{name} subject", "is", right[-12:], topic, scope=scopes.get("scope_b", {})),
    ]
    code, _, err = self.ingest(recs, "--apply")
    self.assertEqual(code, 0, err)
    return self.conflict(self.claim_for(left), self.claim_for(right), severity)

  def verdicts(self, rows: list[dict], *flags: str) -> tuple[int, dict, str]:
    """Run kc verify --file on verdict rows.

    Args:
      rows: verdict records.
      *flags: extra options.

    Returns:
      The kc result.
    """
    path = self.root.parent / "verdicts.json"
    path.write_text(json.dumps(rows))
    return self.kc("verify", "--file", str(path), *flags)


class RootsTest(Case, unittest.TestCase):
  """One finding per cause."""

  def test_shared_identifier_groups_and_unrelated_stands_alone(self):
    """Two conflicts naming one path on both sides group; a third with another cause does not; nothing is written."""
    self.pipeline("related")
    one = self.pair("r1", f"{ROOT_PATH} is retired.", f"{ROOT_PATH} holds the live shims.")
    two = self.pair("r2", f"The old {ROOT_PATH} root is absent.", f"Semgrep starts from {ROOT_PATH}/semgrep.")
    other = self.pair("r3", "The cache size is 10.", "The cache size is 20.")
    before = (self.root / ".kc" / "conflicts.jsonl").read_bytes()
    code, out, err = self.kc("roots")
    self.assertEqual(code, 0, err)
    groups = {c: g for g in out["groups"] for c in g["members"]}
    self.assertEqual(groups[one]["root_id"], groups[two]["root_id"])
    self.assertEqual(groups[one]["token"], "mcp-root")
    self.assertNotEqual(groups[other]["root_id"], groups[one]["root_id"])
    self.assertEqual(len(groups[one]["decide"][one]), 2)
    self.assertEqual((self.root / ".kc" / "conflicts.jsonl").read_bytes(), before)

  def test_document_names_are_not_causes(self):
    """A step name both claims cite says where, not why: no group."""
    self.pipeline("related")
    one = self.pair("step7", "Report step7 says the cache is 10.", "Report step7 says the cache is 20.")
    two = self.pair("step8", "Report step7 says the queue is 1.", "Report step7 says the queue is 2.")
    groups = {c: g for g in self.kc("roots")[1]["groups"] for c in g["members"]}
    self.assertNotEqual(groups[one]["root_id"], groups[two]["root_id"])

  def test_review_queue_lists_root_causes(self):
    """The review queue names the shared cause once, above the cards."""
    self.pipeline("related")
    self.pair("r1", f"{ROOT_PATH} is retired.", f"{ROOT_PATH} holds the live shims.")
    self.pair("r2", f"The old {ROOT_PATH} root is absent.", f"Semgrep starts from {ROOT_PATH}/semgrep.")
    text = self.kc("review")[1]
    self.assertIn("## Root causes", text)
    self.assertIn("`mcp-root`", text)


class VerifyFileTest(Case, unittest.TestCase):
  """Agent verdicts: proposals, citation-constrained."""

  def test_export_carries_excerpts_and_instructions(self):
    """Export is read-only and gives each claim its excerpt and document status."""
    self.pipeline("related")
    cf = self.pair("e1", "The gateway is Caddy.", "The gateway is Traefik.")
    out = self.kc("verify", "--export")[1]
    task = next(t for b in out["batches"] for t in b if t["conflict_id"] == cf)
    self.assertEqual(task["claims"][0]["evidence"][0]["doc_status"], "unknown")
    self.assertIn("not-conflict", out["instructions"])
    self.assertFalse((self.root / ".kc" / "verify").exists())

  def test_not_conflict_needs_a_real_quote(self):
    """A quoted excerpt is kept as a proposal; an invented quote is downgraded to uncertain; the conflict stays open."""
    self.pipeline("related")
    one = self.pair("q1", "In 2025 the gateway was Caddy.", "Since 2026 the gateway is Traefik.")
    two = self.pair("q2", "The mode is one.", "The mode is two.")
    rows = [
      {"conflict_id": one, "verdict": "not-conflict", "kind": "time-evolution", "quote": "Since 2026 the gateway is Traefik", "reason": "dated replacement"},
      {"conflict_id": two, "verdict": "not-conflict", "kind": "equivalent", "quote": "the two modes are the same", "reason": "same meaning"},
    ]
    code, out, err = self.verdicts(rows, "--apply")
    self.assertEqual(code, 0, err)
    self.assertEqual(out["downgraded"], [two])
    st = self.state()
    self.assertEqual(st.conflicts[one]["status"], "open")
    self.assertEqual(st.conflicts[one]["verify"]["verdict"], "not-conflict")
    self.assertEqual(st.conflicts[two]["verify"]["verdict"], "uncertain")
    self.assertIn("Verifier (proposal only)", self.kc("review")[1])

  def test_ambiguous_verdict_word_is_refused(self):
    """'refuted' reads both ways, so the schema refuses it and nothing is written."""
    self.pipeline("related")
    cf = self.pair("w1", "The gateway is Caddy.", "The gateway is Traefik.")
    before = (self.root / ".kc" / "conflicts.jsonl").read_bytes()
    code, _, err = self.verdicts([{"conflict_id": cf, "verdict": "refuted", "reason": "they disagree"}], "--apply")
    self.assertEqual(code, 1)
    self.assertIn("verdicts rejected", err)
    self.assertEqual((self.root / ".kc" / "conflicts.jsonl").read_bytes(), before)


class ConfirmTest(Case, unittest.TestCase):
  """Bulk confirmation: guarded, honest about history, reversible."""

  def test_confirm_clears_with_guards_and_undoes(self):
    """Time-evolution becomes documented-evolution; P0 and same-path opposite status stay; triage --undo reopens."""
    self.pipeline("related")
    evo = self.pair("c1", "In 2025 the gateway was Caddy.", "Since 2026 the gateway is Traefik.")
    p0 = self.pair("c2", "The vault key is rotated daily.", "The vault key is never rotated.", "P0")
    guard = self.pair("c3", f"{ROOT_PATH} is retired.", f"{ROOT_PATH} is the active root.")
    rows = [
      {"conflict_id": evo, "verdict": "not-conflict", "kind": "time-evolution", "quote": "Since 2026 the gateway is Traefik", "reason": "replaced"},
      {"conflict_id": p0, "verdict": "not-conflict", "kind": "different-scope", "quote": "The vault key is rotated daily", "reason": "checked"},
      {"conflict_id": guard, "verdict": "not-conflict", "kind": "time-evolution", "quote": f"{ROOT_PATH} is retired", "reason": "checked"},
    ]
    run = self.verdicts(rows, "--apply")[1]["run_id"]
    code, out, err = self.kc("verify", "--confirm", run, "--apply")
    self.assertEqual(code, 0, err)
    st = self.state()
    self.assertEqual(st.conflicts[evo]["status"], "documented-evolution")
    self.assertEqual(st.conflicts[evo]["triage"]["rule"], "verify:time-evolution")
    self.assertEqual({k["conflict_id"]: k["why"] for k in out["kept"]}, {p0: "p0", guard: "same-identifier-opposite-status"})
    self.kc("triage", "--undo", out["run_id"], "--apply")
    self.assertEqual(self.state().conflicts[evo]["status"], "open")

  def test_different_scope_needs_recorded_scopes(self):
    """A model's different-scope clears only when the ledger records disjoint scopes for the two claims."""
    self.pipeline("related")
    bare = self.pair("d1", "The proxy is Caddy.", "The proxy is Traefik.")
    scoped = self.pair("d2", "Lab proxy is Caddy.", "Prod proxy is Traefik.", scope_a={"environment": "lab"}, scope_b={"environment": "prod"})
    rows = [
      {"conflict_id": bare, "verdict": "not-conflict", "kind": "different-scope", "quote": "The proxy is Caddy", "reason": "different hosts"},
      {"conflict_id": scoped, "verdict": "not-conflict", "kind": "different-scope", "quote": "Lab proxy is Caddy", "reason": "lab and prod"},
    ]
    run = self.verdicts(rows, "--apply")[1]["run_id"]
    out = self.kc("verify", "--confirm", run, "--apply")[1]
    self.assertEqual(out["kept"], [{"conflict_id": bare, "why": "scope-not-recorded"}])
    self.assertEqual(self.state().conflicts[scoped]["status"], "dismissed")

  def test_score_counts_real_conflicts_lost(self):
    """A labelled real conflict the verifier called not-conflict is reported lost."""
    self.pipeline("related")
    cf = self.pair("s1", "In 2025 the gateway was Caddy.", "Since 2026 the gateway is Traefik.")
    self.verdicts(
      [{"conflict_id": cf, "verdict": "not-conflict", "kind": "time-evolution", "quote": "Since 2026 the gateway is Traefik", "reason": "checked"}], "--apply"
    )
    labels = self.root.parent / "labels.json"
    labels.write_text(json.dumps([{"conflict_id": cf, "verdict": "real"}]))
    out = self.kc("verify", "--score", str(labels))[1]
    self.assertEqual(out["real_lost"], [cf])
    self.assertEqual(out["real_recall_kept"], 0.0)
    run = next(iter(out["confirm"]))
    self.assertEqual(out["confirm"][run]["real_cleared"], [cf])
    self.assertEqual(out["confirm"][run]["clears_right"], 0.0)


class ModelSeamTest(Case, unittest.TestCase):
  """The local-model arm: allowlist, loopback, control pairs, errors kept uncertain."""

  def fake(self, answers: list[dict]):
    """Patch the model call with fixed answers, in order.

    Args:
      answers: reply objects.

    Returns:
      The patcher context.
    """
    replies = iter(answers)
    return mock.patch.object(lib("llm"), "chat_json", side_effect=lambda *a, **k: (next(replies), {"prompt_tokens": 1, "completion_tokens": 1}))

  def test_model_not_allowlisted_or_remote_is_refused(self):
    """An unlisted model, or a remote endpoint without allow_remote, stops before any call."""
    self.pipeline("related")
    self.assertEqual(self.kc("verify", "--model", "some-other-model")[0], 1)
    with mock.patch.dict("os.environ", {"KC_LLM_BASE_URL": "https://api.example.com/v1"}):
      code, _, err = self.kc("verify", "--model", "Qwen3.6-35B-A3B-4bit-DWQ")
    self.assertEqual(code, 1)
    self.assertIn("not loopback", err)

  def test_wrong_control_answer_stops_the_run(self):
    """A model that reads the verdict words backwards fails the first control and records nothing."""
    self.pipeline("related")
    before = (self.root / ".kc" / "conflicts.jsonl").read_bytes()
    with self.fake([{"verdict": "not-conflict"}]):
      code, _, err = self.kc("verify", "--model", "Qwen3.6-35B-A3B-4bit-DWQ", "--apply")
    self.assertEqual(code, 1)
    self.assertIn("not trusted", err)
    self.assertEqual((self.root / ".kc" / "conflicts.jsonl").read_bytes(), before)

  def test_model_errors_and_odd_words_become_uncertain(self):
    """A failed call or an off-vocabulary word is recorded uncertain, never as no conflict."""
    self.pipeline("related")
    n = len(self.state().open_conflicts())
    answers = [{"verdict": "conflict"}, {"verdict": "not-conflict"}] + [{"verdict": "refuted", "reason": "checked"}] * n
    with self.fake(answers):
      code, out, err = self.kc("verify", "--model", "Qwen3.6-35B-A3B-4bit-DWQ", "--apply")
    self.assertEqual(code, 0, err)
    self.assertEqual(out["counts"], {"uncertain": n})
    llm = lib("llm")
    with self.assertRaises(llm.ModelError):
      llm.parse_object("no json here")


class ProbeTest(unittest.TestCase):
  """scripts/llm_probe.py: list models, time the controls, refuse a remote endpoint."""

  def run_probe(self, *argv: str) -> tuple[int, dict | None]:
    """Run the probe's main with a fake server.

    Args:
      *argv: probe arguments.

    Returns:
      (exit code, parsed JSON or None).
    """
    probe = importlib.import_module("llm_probe")
    llm = lib("llm")
    answers = iter([{"verdict": "conflict"}, {"verdict": "conflict"}])
    out = io.StringIO()
    with (
      mock.patch.object(llm, "list_models", return_value=["m-1"]),
      mock.patch.object(llm, "chat_json", side_effect=lambda *a, **k: (next(answers), {"prompt_tokens": 2, "completion_tokens": 1})),
      contextlib.redirect_stdout(out),
      contextlib.redirect_stderr(io.StringIO()),
    ):
      code = probe.main(list(argv))
    return code, json.loads(out.getvalue()) if out.getvalue() else None

  def test_lists_models_without_a_model(self):
    """No --model: list only, exit 0, no chat call."""
    code, out = self.run_probe()
    self.assertEqual((code, out["models"], out["passed"]), (0, ["m-1"], None))

  def test_wrong_control_exits_3(self):
    """A model answering conflict to the dated replacement fails the second control."""
    code, out = self.run_probe("--model", "m-1")
    self.assertEqual(code, 3)
    self.assertEqual([c["got"] for c in out["controls"]], ["conflict", "conflict"])

  def test_remote_endpoint_refused(self):
    """A non-loopback base needs --allow-remote."""
    code, out = self.run_probe("--base", "https://api.example.com/v1")
    self.assertEqual((code, out), (1, None))


if __name__ == "__main__":
  unittest.main()
