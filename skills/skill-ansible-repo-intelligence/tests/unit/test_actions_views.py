"""Managed-resource extraction + digest view tests (Phase 1/2 efficiency work)."""

from __future__ import annotations

from pathlib import Path

from ansible_repo_intelligence.actions import extract_action, short_module
from ansible_repo_intelligence.cli import main
from ansible_repo_intelligence.query import QueryOptions, load_store, run_view

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "multi_role_repo"


def _scan(tmp_path) -> Path:
    out = tmp_path / "ctx"
    assert main(["scan", "--repo", str(FIXTURE), "--output", str(out), "--offline"]) == 0
    return out


# --- extraction ------------------------------------------------------------

def test_short_module_strips_prefix():
    assert short_module("ansible.builtin.template", "template") == "template"
    assert short_module("community.general.parted", "parted") == "parted"


def test_package_extracts_name():
    a = extract_action("ansible.builtin.package", "package", {"name": "nginx", "state": "present"}, [], False)
    assert a.operation == "install_package"
    assert a.resource["packages"] == "nginx" and a.resource["state"] == "present"


def test_template_extracts_src_dest():
    a = extract_action("ansible.builtin.template", "template",
                       {"src": "x.j2", "dest": "/etc/x"}, [], False)
    assert a.operation == "render_template"
    assert a.resource == {"src": "x.j2", "dest": "/etc/x"}


def test_freeform_command_flags_verification():
    a = extract_action("ansible.builtin.shell", "shell", "rm -rf /var/cache/old", [], True)
    assert a.operation == "execute_command"
    assert a.verification_recommended and "command" in a.verification_reason.lower()


def test_jinja_dest_flags_verification():
    a = extract_action("ansible.builtin.template", "template",
                       {"src": "x.j2", "dest": "/etc/{{ svc }}.conf"}, [], False)
    assert a.verification_recommended and "jinja" in a.verification_reason.lower()


def test_complex_when_flags_verification():
    a = extract_action("ansible.builtin.package", "package", {"name": "x"},
                       ["a and b"], False)
    assert a.verification_recommended and "conditional" in a.verification_reason.lower()


def test_unknown_module_generic_fallback():
    a = extract_action("my.custom.widget", "widget", {"foo": 1, "bar": 2}, [], False)
    assert a.operation == "module_action"
    assert a.resource["keys"] == ["bar", "foo"]
    assert a.verification_recommended  # custom module -> verify


# --- views -----------------------------------------------------------------

def test_actions_view_is_source_traceable(tmp_path):
    store = load_store(_scan(tmp_path))
    p = run_view(store, "role", "dns", "actions", QueryOptions())
    assert p["view"] == "actions" and p["actions"]
    for a in p["actions"]:
        assert a["source"] and ":" in a["source"]  # every action cites source
    # the template action carries src/dest facts + notify
    tmpl = [a for a in p["actions"] if a["operation"] == "render_template"]
    assert tmpl and tmpl[0]["resource"].get("dest")


def test_actions_view_no_prose_conclusion(tmp_path):
    store = load_store(_scan(tmp_path))
    p = run_view(store, "role", "dns", "actions", QueryOptions())
    blob = str(p).lower()
    # facts only — must not editorialize
    assert "from source" not in blob or "extracted from source" in blob


def test_summary_view_aggregates(tmp_path):
    store = load_store(_scan(tmp_path))
    p = run_view(store, "role", "dns", "summary", QueryOptions())
    assert p["view"] == "summary"
    assert "resolved" in str(p).lower() or p["packages"] or p["services"] or p["templated_files"]


def test_destructive_action_flagged_verify(tmp_path):
    store = load_store(_scan(tmp_path))
    p = run_view(store, "role", "dns", "actions", QueryOptions())
    # dns fixture has a 'Destroy old data' shell rm -rf task -> critical + verify
    destroy = [a for a in p["actions"] if "Destroy" in (a["task"] or "")]
    assert destroy and destroy[0]["verify"]


def test_view_cli(tmp_path):
    ctx = _scan(tmp_path)
    assert main(["query", "role", "dns", "--view", "actions", "--context", str(ctx)]) == 0
    assert main(["query", "role", "dns", "--view", "sources", "--context", str(ctx)]) == 0
