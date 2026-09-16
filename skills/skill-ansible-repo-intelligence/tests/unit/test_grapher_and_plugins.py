"""Tests for the grapher adapter and custom-plugin/module graph nodes."""

from __future__ import annotations

from pathlib import Path

from ansible_repo_intelligence.cli import main
from ansible_repo_intelligence.grapher import (
    GrapherProvenance, RunResult, detect, run_grapher, validate_dot,
)
from ansible_repo_intelligence.query import load_store

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "multi_role_repo"


def _scan(tmp_path) -> Path:
    out = tmp_path / "ctx"
    assert main(["scan", "--repo", str(FIXTURE), "--output", str(out), "--offline"]) == 0
    return out


# --- grapher adapter -------------------------------------------------------

def test_grapher_absent_is_graceful(monkeypatch):
    # Force "not on PATH and no candidate" -> available False, never raises.
    import ansible_repo_intelligence.grapher as g
    monkeypatch.setattr(g.shutil, "which", lambda _: None)
    monkeypatch.setattr(g, "_GRAPHER_CANDIDATES", ())
    prov = detect()
    assert prov.available is False and prov.invoked is False


def test_grapher_exit_zero_but_no_output_not_trusted(tmp_path, monkeypatch):
    import ansible_repo_intelligence.grapher as g
    monkeypatch.setattr(g.shutil, "which", lambda _: "/fake/ansible-playbook-grapher")
    # runner returns success but writes no .dot file
    runner = lambda cmd, cwd: RunResult(0, "ok", "")
    prov = run_grapher(tmp_path, "site.yml", tmp_path / "out", runner=runner)
    assert prov.invoked and prov.exit_code == 0
    assert prov.output_validated is False  # exit 0 alone is not trusted
    assert "no .dot" in (prov.note or "")


def test_grapher_valid_output_is_validated(tmp_path, monkeypatch):
    import ansible_repo_intelligence.grapher as g
    monkeypatch.setattr(g.shutil, "which", lambda _: "/fake/ansible-playbook-grapher")
    out = tmp_path / "out"

    def runner(cmd, cwd):
        out.mkdir(parents=True, exist_ok=True)
        (out / "playbook-grapher.dot").write_text(
            'digraph { "play" -> "role_dns" [label="uses_role"]; }', encoding="utf-8")
        return RunResult(0, "", "")

    prov = run_grapher(tmp_path, "site.yml", out, runner=runner)
    assert prov.output_validated is True


def test_validate_dot_rejects_garbage(tmp_path):
    p = tmp_path / "x.dot"
    p.write_text("not a graph at all", encoding="utf-8")
    assert validate_dot(p) is False


def test_default_scan_has_empty_external_tools(tmp_path):
    import io
    from ruamel.yaml import YAML
    ctx = _scan(tmp_path)
    data = YAML(typ="safe", pure=True).load((ctx / "manifest.yaml").read_text())
    # Default scan (no --playbook-grapher) keeps manifest machine-independent.
    assert data["external_tools"] == {}


def test_opt_in_grapher_records_provenance(tmp_path):
    out = tmp_path / "ctx"
    assert main(["scan", "--repo", str(FIXTURE), "--output", str(out),
                 "--offline", "--playbook-grapher"]) == 0
    from ruamel.yaml import YAML
    data = YAML(typ="safe", pure=True).load((out / "manifest.yaml").read_text())
    assert "ansible_playbook_grapher" in data["external_tools"]
    # honest availability record; scan still succeeded regardless
    assert "available" in data["external_tools"]["ansible_playbook_grapher"]


# --- custom plugin / module nodes -----------------------------------------

def test_vars_plugin_still_dynamic(tmp_path):
    store = load_store(_scan(tmp_path))
    vp = [n for n in store.nodes.values() if n["kind"] == "vars_plugin"]
    assert vp and vp[0]["resolution"]["status"] == "dynamic"


def test_plugin_nodes_marked_dynamic_when_present():
    # Build a tiny synthetic graph check via the fixture: the fixture has no
    # callback plugin, so assert the machinery exists and doesn't crash, and
    # that any plugin-kind node (if present) is dynamic.
    import tempfile
    from ansible_repo_intelligence.cli import main as _main
    d = Path(tempfile.mkdtemp()) / "ctx"
    _main(["scan", "--repo", str(FIXTURE), "--output", str(d), "--offline"])
    store = load_store(d)
    plugin_kinds = {"callback_plugin", "filter_plugin", "lookup_plugin",
                    "action_plugin", "module", "module_utils"}
    for n in store.nodes.values():
        if n["kind"] in plugin_kinds:
            assert n["resolution"]["status"] == "dynamic"
