"""Phase 1 gate tests against the multi_role_repo fixture."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "multi_role_repo"


def _nodes(graph, kind):
    return [n for n in graph.nodes.values() if n.kind == kind]


def test_roles_discovered(scanned):
    _, _, disc, graph, _ = scanned
    assert set(disc.roles) == {"dns", "web"}
    assert len(_nodes(graph, "role")) == 2


def test_vendored_collection_excluded(scanned):
    _, _, disc, graph, _ = scanned
    # The vendored plugin YAML must not appear as a first-class node.
    assert disc.vendored_yaml_count >= 1
    for n in graph.nodes.values():
        assert "should_not_be_indexed" not in (n.name or "")
        if n.source:
            assert "ansible_collections/community/general/plugins" not in n.source.path
    # But the collection itself is tracked.
    colls = _nodes(graph, "collection")
    assert any(c.name == "community.general" for c in colls)


def test_notify_resolves_to_handler(scanned):
    _, _, _, graph, _ = scanned
    notifies = [e for e in graph.edges.values() if e.type == "notifies"]
    assert notifies, "expected at least one notifies edge"
    # dns task -> restart resolved handler, resolved status
    assert any(e.resolution.status.value == "resolved" for e in notifies)


def test_dynamic_include_labelled_not_guessed(scanned):
    _, _, _, graph, diags = scanned
    # The templated include must be dynamic, never a concrete guessed target.
    dynamic = [d for d in diags.items if d.code == "ARI002_DYNAMIC_INCLUDE"]
    assert dynamic, "templated include must produce ARI002"


def test_destructive_task_is_critical(scanned):
    _, _, _, graph, _ = scanned
    tasks = _nodes(graph, "task")
    destroy = [t for t in tasks if "Destroy" in t.name]
    assert destroy and destroy[0].significance.value == "critical"
    assert destroy[0].significance_rule_id == "destructive-shell-command"


def test_vars_plugin_marked_dynamic(scanned):
    _, _, _, graph, _ = scanned
    vps = _nodes(graph, "vars_plugin")
    assert vps, "custom vars plugin must be detected"
    assert vps[0].resolution.status.value == "dynamic"
    # Literal keys become dynamic variable nodes linked via 'supplies' edges.
    supplied = [e for e in graph.edges.values() if e.type == "supplies"]
    assert supplied


def test_role_dependency_edge(scanned):
    _, _, _, graph, _ = scanned
    deps = [e for e in graph.edges.values() if e.type == "depends_on"]
    assert any(e.from_id == "role:web" and e.to_id == "role:dns" for e in deps)


def test_secret_name_flagged_without_value(scanned):
    _, _, _, graph, _ = scanned
    api = [n for n in graph.nodes.values() if n.kind == "variable" and n.name == "api_token"]
    assert api
    assert api[0].attributes.get("sensitive_name") is True
    # The secret VALUE must never appear anywhere in the graph.
    for n in graph.nodes.values():
        assert "CHANGEME" not in str(n.attributes)


def test_precedence_conflict_detected(scanned):
    _, _, _, graph, diags = scanned
    # dns_servers defined in role default AND group_vars -> cross-class conflict.
    conflicts = [d for d in diags.items if d.code == "ARI006_POSSIBLE_VARIABLE_PRECEDENCE_CONFLICT"]
    assert any("dns_servers" in d.message for d in conflicts)


def test_source_provenance_on_every_source_node(scanned):
    _, _, _, graph, _ = scanned
    for n in graph.nodes.values():
        if n.kind in ("task", "handler", "playbook", "play", "template"):
            assert n.source is not None and n.source.path


def test_flavor_scoping_on_inventory_nodes(scanned):
    _, _, _, graph, _ = scanned
    for n in graph.nodes.values():
        if n.kind in ("inventory_group", "inventory_host"):
            assert "flavor" in n.attributes and "environment" in n.attributes


def test_scan_is_deterministic_and_valid(tmp_path):
    from ansible_repo_intelligence.cli import main
    out1 = tmp_path / "a"
    out2 = tmp_path / "b"
    assert main(["scan", "--repo", str(FIXTURE), "--output", str(out1), "--offline"]) == 0
    assert main(["scan", "--repo", str(FIXTURE), "--output", str(out2), "--offline"]) == 0
    for f in ("graph.yaml", "ANSIBLE_REPO_MAP.md", "diagnostics.yaml"):
        assert (out1 / f).read_bytes() == (out2 / f).read_bytes(), f"{f} not deterministic"
    assert main(["validate", "--context", str(out1)]) == 0


def test_map_within_budget(tmp_path):
    from ansible_repo_intelligence.cli import main
    out = tmp_path / "m"
    main(["scan", "--repo", str(FIXTURE), "--output", str(out), "--offline"])
    lines = (out / "ANSIBLE_REPO_MAP.md").read_text().splitlines()
    assert len(lines) <= 1000


def test_ansible_cfg_honoured(scanned):
    _, acfg, _, _, _ = scanned
    assert acfg.roles_paths == ("roles",)
    assert acfg.collections_paths == ("collections",)
    assert "jinja2.ext.do" in acfg.safe_jinja_extensions
