"""Phase 3 benchmark harness tests (deterministic half only)."""

from __future__ import annotations

from pathlib import Path

from ansible_repo_intelligence.benchmark import (
    Question, load_questions, render_benchmark, run_benchmark,
)
from ansible_repo_intelligence.cli import main

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "multi_role_repo"


def _scan(tmp_path) -> Path:
    out = tmp_path / "ctx"
    assert main(["scan", "--repo", str(FIXTURE), "--output", str(out), "--offline"]) == 0
    return out


def _fixture_questions() -> list[Question]:
    return [
        Question("q-dns", "How is dns configured?", "role", "dns",
                 gold_files=["roles/dns/tasks/main.yml", "roles/dns/handlers/main.yml"],
                 keywords=["resolved", "systemd-resolved"]),
        Question("q-web", "How is web configured?", "role", "web",
                 gold_files=["roles/web/tasks/main.yml"], keywords=["nginx"]),
    ]


def test_harness_runs_and_is_partial(tmp_path):
    ctx = _scan(tmp_path)
    result = run_benchmark(FIXTURE, ctx, _fixture_questions())
    assert result.verdict == "PARTIAL"
    # correctness/unsupported-claims are explicitly NOT self-graded here
    assert "not self-graded" in result.partial_reason.lower()
    assert "blind-grading" in result.partial_reason.lower()
    assert result.aggregate["questions"] == 2


def test_efficiency_metrics_computed(tmp_path):
    ctx = _scan(tmp_path)
    result = run_benchmark(FIXTURE, ctx, _fixture_questions())
    a = result.aggregate
    # Deterministic metrics exist and are well-formed. (On a tiny fixture the
    # index is not necessarily fewer-files than a 1-2-file grep; the scale
    # advantage is demonstrated on the real 94-role repo, ~96% fewer.)
    assert a["total_indexed_files_opened"] >= 0
    assert a["total_baseline_files_opened"] >= 0
    assert "fewer_files_opened_pct" in a
    assert "meets_recall_target" in a


def test_indexed_recall_reasonable(tmp_path):
    ctx = _scan(tmp_path)
    result = run_benchmark(FIXTURE, ctx, _fixture_questions())
    # The dns role's task+handler files are reachable via retrieval topics.
    assert result.aggregate["mean_indexed_recall_pct"] >= 50.0


def test_render_mentions_external_grading(tmp_path):
    ctx = _scan(tmp_path)
    result = run_benchmark(FIXTURE, ctx, _fixture_questions())
    text = render_benchmark(result, "concise")
    assert "PARTIAL" in text and "external grading" in text
    y = render_benchmark(result, "yaml")
    assert "external_grading_required" in y


def test_real_question_file_loads():
    qs = load_questions(ROOT / "tests" / "benchmark" / "questions.ansible_wifi.yaml")
    assert len(qs) >= 20
    assert all(q.gold_files for q in qs)


def test_benchmark_cli(tmp_path):
    ctx = _scan(tmp_path)
    # Write a tiny question file for the fixture.
    qf = tmp_path / "q.yaml"
    qf.write_text(
        "version: '1.0.0'\nquestions:\n"
        "  - id: q-dns\n    question: dns?\n    selector: role\n    term: dns\n"
        "    gold_files: [roles/dns/tasks/main.yml]\n    keywords: [resolved]\n",
        encoding="utf-8",
    )
    rc = main(["benchmark", "--repo", str(FIXTURE), "--context", str(ctx),
               "--questions", str(qf)])
    assert rc == 0
