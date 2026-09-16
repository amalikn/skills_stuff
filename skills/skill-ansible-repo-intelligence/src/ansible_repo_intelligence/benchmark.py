"""Token-efficiency benchmark harness.

Measures the *deterministic* half of the benchmark and explicitly leaves the
non-deterministic half (answer correctness, unsupported-claim counting) to an
external blind-grading process. The harness NEVER self-grades correctness.

Deterministic metrics (computed here, reproducible, no LLM):

- indexed lookup: files the tool's own bounded query surfaces per question
- baseline lookup: files a naive keyword grep over the repo would surface
- lookup recall of the gold required-files set for each strategy
- files opened per strategy (indexed = query-surfaced; baseline = grep hits)
- repository-map size and per-question query-result size

Non-deterministic metrics (NOT computed here — require the runbook's two
isolated agent sessions + blind grader):

- answer correctness
- unsupported-claim count
- time-to-first-relevant-file (wall-clock of a real agent)

Because those cannot run in a single automated session, the overall benchmark
verdict is PARTIAL by construction, and the harness says so.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from .query import QueryOptions, run_query
from .traversal import GraphStore


@dataclass
class Question:
    id: str
    question: str
    selector: str
    term: str | None
    gold_files: list[str]
    keywords: list[str]


@dataclass
class QuestionResult:
    id: str
    indexed_files: list[str]
    baseline_files: list[str]
    gold_files: list[str]
    indexed_recall: float
    baseline_recall: float
    indexed_opened: int
    baseline_opened: int
    query_bytes: int


@dataclass
class BenchmarkResult:
    per_question: list[QuestionResult] = field(default_factory=list)
    map_lines: int = 0
    thresholds: dict[str, Any] = field(default_factory=dict)
    aggregate: dict[str, Any] = field(default_factory=dict)
    verdict: str = "PARTIAL"
    partial_reason: str = ""


TARGETS = {
    "min_fewer_files_opened_pct": 60.0,
    "min_lower_token_pct": 40.0,        # approximated by files-opened proxy here
    "min_lookup_recall_pct": 95.0,
}


def load_questions(path: Path) -> list[Question]:
    yaml = YAML(typ="safe", pure=True)
    data = yaml.load(path.read_text(encoding="utf-8")) or {}
    out: list[Question] = []
    for q in data.get("questions", []):
        out.append(Question(
            id=str(q["id"]), question=str(q["question"]),
            selector=str(q["selector"]), term=q.get("term"),
            gold_files=[str(x) for x in q.get("gold_files", [])],
            keywords=[str(x) for x in q.get("keywords", [])],
        ))
    return out


def _recall(found: list[str], gold: list[str]) -> float:
    if not gold:
        return 1.0
    found_set = set(found)
    hit = sum(1 for g in gold if any(f == g or f.endswith("/" + g.split("/")[-1]) or g in f for f in found_set))
    return 100.0 * hit / len(gold)


def indexed_lookup(store: GraphStore, q: Question) -> tuple[list[str], int]:
    """Files surfaced by the tool's intended workflow: bounded query PLUS the
    map's retrieval_topics source_paths for any matched role/topic.

    This mirrors how an agent actually navigates — map -> topic -> source files
    -> bounded query — rather than a single raw query.
    """
    payload = run_query(store, q.selector, q.term, QueryOptions(limit=25, max_depth=1))
    files: list[str] = []
    for n in payload.get("nodes", []):
        src = (n.get("source") or {}).get("path")
        if src:
            files.append(src)
    # Fold in retrieval-topic source paths for matched roles (topic key == role).
    for n in payload.get("nodes", []):
        if n.get("kind") == "role":
            topic = store.retrieval_topics.get(n.get("name"), {})
            files.extend(topic.get("source_paths", []))
    # Also match a topic directly by the query term (e.g. term is a role name).
    if q.term and q.term in store.retrieval_topics:
        files.extend(store.retrieval_topics[q.term].get("source_paths", []))
    y = YAML()
    buf = io.StringIO()
    y.dump(payload, buf)
    return sorted(set(files)), len(buf.getvalue().encode("utf-8"))


def baseline_lookup(repo: Path, q: Question, max_files: int = 2000) -> list[str]:
    """Files a naive keyword grep would surface (proxy for a no-index agent)."""
    if not q.keywords:
        return []
    patterns = [re.compile(re.escape(k), re.IGNORECASE) for k in q.keywords]
    hits: set[str] = set()
    scanned = 0
    for p in sorted(repo.rglob("*")):
        if scanned >= max_files:
            break
        if not p.is_file() or p.suffix not in (".yml", ".yaml", ".j2", ".cfg"):
            continue
        # Skip vendored/venv/git to mirror a sane baseline agent.
        rel = str(p.relative_to(repo))
        if any(seg in rel for seg in ("ansible_collections/", ".git/", ".venv", "graphify-out/")):
            continue
        scanned += 1
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(rx.search(text) for rx in patterns):
            hits.add(rel)
    return sorted(hits)


def run_benchmark(repo: Path, context_dir: Path, questions: list[Question]) -> BenchmarkResult:
    store = GraphStore.load(context_dir / "graph.yaml")
    result = BenchmarkResult(thresholds=TARGETS)
    map_p = context_dir / "ANSIBLE_REPO_MAP.md"
    result.map_lines = len(map_p.read_text(encoding="utf-8").splitlines()) if map_p.is_file() else 0

    for q in questions:
        idx_files, qbytes = indexed_lookup(store, q)
        base_files = baseline_lookup(repo, q)
        result.per_question.append(QuestionResult(
            id=q.id,
            indexed_files=idx_files, baseline_files=base_files, gold_files=q.gold_files,
            indexed_recall=_recall(idx_files, q.gold_files),
            baseline_recall=_recall(base_files, q.gold_files),
            indexed_opened=len(idx_files), baseline_opened=len(base_files),
            query_bytes=qbytes,
        ))

    _aggregate(result)
    result.partial_reason = (
        "Answer correctness, unsupported-claim count and time-to-first-file require "
        "the two-isolated-session blind-grading runbook (tests/benchmark/RUNBOOK.md). "
        "They are NOT self-graded here, so the overall verdict is PARTIAL."
    )
    return result


def _aggregate(result: BenchmarkResult) -> None:
    n = len(result.per_question) or 1
    tot_idx_open = sum(q.indexed_opened for q in result.per_question)
    tot_base_open = sum(q.baseline_opened for q in result.per_question)
    fewer_pct = (100.0 * (tot_base_open - tot_idx_open) / tot_base_open) if tot_base_open else 0.0
    idx_recall = sum(q.indexed_recall for q in result.per_question) / n
    base_recall = sum(q.baseline_recall for q in result.per_question) / n
    result.aggregate = {
        "questions": len(result.per_question),
        "total_indexed_files_opened": tot_idx_open,
        "total_baseline_files_opened": tot_base_open,
        "fewer_files_opened_pct": round(fewer_pct, 1),
        "mean_indexed_recall_pct": round(idx_recall, 1),
        "mean_baseline_recall_pct": round(base_recall, 1),
        "map_lines": result.map_lines,
        "mean_query_bytes": round(sum(q.query_bytes for q in result.per_question) / n, 1),
        "meets_fewer_files_target": fewer_pct >= TARGETS["min_fewer_files_opened_pct"],
        "meets_recall_target": idx_recall >= TARGETS["min_lookup_recall_pct"],
    }


def render_benchmark(result: BenchmarkResult, output: str = "concise") -> str:
    payload = {
        "verdict": result.verdict,
        "partial_reason": result.partial_reason,
        "thresholds": result.thresholds,
        "aggregate": result.aggregate,
        "per_question": [
            {
                "id": q.id,
                "indexed_opened": q.indexed_opened,
                "baseline_opened": q.baseline_opened,
                "indexed_recall_pct": round(q.indexed_recall, 1),
                "baseline_recall_pct": round(q.baseline_recall, 1),
                "query_bytes": q.query_bytes,
            }
            for q in result.per_question
        ],
        "external_grading_required": [
            "answer_correctness", "unsupported_claim_count", "time_to_first_relevant_file",
        ],
    }
    if output == "yaml":
        y = YAML()
        y.default_flow_style = False
        buf = io.StringIO()
        y.dump(payload, buf)
        return buf.getvalue()
    a = result.aggregate
    lines = [
        f"verdict: {result.verdict}",
        f"questions: {a.get('questions')}",
        f"files opened -- baseline: {a.get('total_baseline_files_opened')} | "
        f"indexed: {a.get('total_indexed_files_opened')} | "
        f"fewer: {a.get('fewer_files_opened_pct')}% (target >=60%, "
        f"{'MET' if a.get('meets_fewer_files_target') else 'NOT MET'})",
        f"indexed recall: {a.get('mean_indexed_recall_pct')}% (target >=95%, "
        f"{'MET' if a.get('meets_recall_target') else 'NOT MET'}) | "
        f"baseline recall: {a.get('mean_baseline_recall_pct')}%",
        f"map lines: {a.get('map_lines')} | mean query bytes: {a.get('mean_query_bytes')}",
        "PARTIAL -- external grading required for: answer correctness, unsupported claims, "
        "time-to-first-file. See tests/benchmark/RUNBOOK.md",
    ]
    return "\n".join(lines) + "\n"
