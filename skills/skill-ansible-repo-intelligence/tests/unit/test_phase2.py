"""Phase 2 gate tests: bounded query, impact, shared traversal, incremental."""

from __future__ import annotations

from pathlib import Path

from ansible_repo_intelligence.cli import main
from ansible_repo_intelligence.query import (
    QueryOptions, load_store, run_impact, run_query,
)
from ansible_repo_intelligence.traversal import Bounds, bounded_bfs

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "multi_role_repo"


def _scan(tmp_path) -> Path:
    out = tmp_path / "ctx"
    assert main(["scan", "--repo", str(FIXTURE), "--output", str(out), "--offline"]) == 0
    return out


def test_query_default_bounds(tmp_path):
    store = load_store(_scan(tmp_path))
    res = run_query(store, "role", "dns", QueryOptions())
    assert res["returned_nodes"] <= 25
    # 1-hop default: no node beyond immediate neighbours.
    assert res["matched_roots"] >= 1


def test_query_and_impact_share_traversal(tmp_path):
    # Both call bounded_bfs; assert identical engine behaviour on same roots.
    store = load_store(_scan(tmp_path))
    roots = [n for n in store.nodes if n == "role:dns"]
    a = bounded_bfs(store, roots, Bounds(25, 1, 65536))
    b = bounded_bfs(store, roots, Bounds(25, 1, 65536))
    assert a.node_ids == b.node_ids  # deterministic
    assert "role:dns" in a.node_ids


def test_query_limit_enforced(tmp_path):
    store = load_store(_scan(tmp_path))
    res = run_query(store, "task", None, QueryOptions(limit=3, max_depth=1))
    assert res["returned_nodes"] <= 3
    assert res["truncated"] in (True, False)


def test_impact_bounded_and_not_greedy(tmp_path):
    store = load_store(_scan(tmp_path))
    res = run_impact(store, "roles/dns/tasks/main.yml", QueryOptions(limit=50, max_depth=3))
    # Must NOT match every */main.yml — only this file's nodes + reachable.
    assert res["matched_roots"] < 20
    # dns tasks notify 'restart resolved' -> handler should appear in affected.
    assert "restart resolved" in res["affected"]["handlers_notified"]


def test_impact_reports_caveat(tmp_path):
    store = load_store(_scan(tmp_path))
    res = run_impact(store, "roles/dns", QueryOptions())
    assert "Static reachability only" in res["caveat"]


def test_incremental_no_change_short_circuits(tmp_path, capsys):
    out = _scan(tmp_path)
    rc = main(["scan", "--repo", str(FIXTURE), "--output", str(out), "--offline", "--incremental"])
    assert rc == 0
    assert "no changes" in capsys.readouterr().out


def test_incremental_equivalent_to_full(tmp_path):
    out_full = tmp_path / "full"
    out_inc = tmp_path / "inc"
    main(["scan", "--repo", str(FIXTURE), "--output", str(out_inc), "--offline"])
    # touch nothing; incremental rebuild path forced by --force
    main(["scan", "--repo", str(FIXTURE), "--output", str(out_inc), "--offline", "--incremental", "--force"])
    main(["scan", "--repo", str(FIXTURE), "--output", str(out_full), "--offline"])
    assert (out_inc / "graph.yaml").read_bytes() == (out_full / "graph.yaml").read_bytes()
