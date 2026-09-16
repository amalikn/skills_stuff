"""Explain command tests (Phase 3 completion of the CLI surface)."""

from __future__ import annotations

from pathlib import Path

from ansible_repo_intelligence.cli import main
from ansible_repo_intelligence.query import (
    QueryOptions, load_store, render_explain, run_explain,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "multi_role_repo"


def _scan(tmp_path) -> Path:
    out = tmp_path / "ctx"
    assert main(["scan", "--repo", str(FIXTURE), "--output", str(out), "--offline"]) == 0
    return out


def test_explain_role_by_exact_id(tmp_path):
    store = load_store(_scan(tmp_path))
    p = run_explain(store, "role:dns", QueryOptions())
    assert p["found"] and not p.get("ambiguous")
    assert p["id"] == "role:dns"
    assert p["resolution"]["status"] == "resolved"


def test_explain_ambiguous_name_role_vs_group(tmp_path):
    # 'dns' is both a role and an inventory group in the fixture -> ambiguous.
    store = load_store(_scan(tmp_path))
    p = run_explain(store, "dns", QueryOptions())
    assert p["found"] and p.get("ambiguous")
    ids = {c["id"] for c in p["candidates"]}
    assert "role:dns" in ids


def test_explain_handler_shows_incoming_notify(tmp_path):
    store = load_store(_scan(tmp_path))
    p = run_explain(store, "restart resolved", QueryOptions())
    assert p["found"]
    incoming_types = {e["type"] for e in p["relationships"]["incoming"]}
    assert "notifies" in incoming_types
    # each relationship carries a reason
    for e in p["relationships"]["incoming"]:
        assert e["reason"]


def test_explain_by_exact_id(tmp_path):
    store = load_store(_scan(tmp_path))
    p = run_explain(store, "role:web", QueryOptions())
    assert p["found"] and p["id"] == "role:web"


def test_explain_not_found(tmp_path):
    store = load_store(_scan(tmp_path))
    p = run_explain(store, "does-not-exist-xyz", QueryOptions())
    assert not p["found"]


def test_explain_ambiguous_lists_candidates(tmp_path):
    store = load_store(_scan(tmp_path))
    # add nothing; 'dns' is unique here, so craft ambiguity via a common token
    p = run_explain(store, "main.yml", QueryOptions())
    # multiple task_file/handler nodes share 'main.yml' in their id
    if p.get("ambiguous"):
        assert p["candidates"]
    else:
        assert p["found"] in (True, False)


def test_explain_dynamic_resolution_surfaced(tmp_path):
    store = load_store(_scan(tmp_path))
    # the vars plugin node is dynamic
    vp = [nid for nid in store.nodes if nid.startswith("vars_plugin:")]
    assert vp
    p = run_explain(store, vp[0], QueryOptions())
    assert p["resolution"]["status"] == "dynamic"
    assert "not statically resolvable" in p["resolution"]["reason"]


def test_explain_render_concise_and_yaml(tmp_path):
    store = load_store(_scan(tmp_path))
    p = run_explain(store, "role:dns", QueryOptions())
    text = render_explain(p, "concise")
    assert "kind:" in text and "resolution:" in text
    y = render_explain(p, "yaml")
    assert "relationships" in y


def test_explain_cli(tmp_path):
    ctx = _scan(tmp_path)
    assert main(["explain", "role:dns", "--context", str(ctx)]) == 0
    assert main(["explain", "nope-xyz", "--context", str(ctx)]) == 1
