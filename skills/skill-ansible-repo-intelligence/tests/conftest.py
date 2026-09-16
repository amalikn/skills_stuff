import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "multi_role_repo"


@pytest.fixture(scope="session", autouse=True)
def _ensure_fixture():
    if not (FIXTURE / "site.yml").is_file():
        subprocess.run([sys.executable, str(ROOT / "tests" / "_gen_fixture.py")], check=True)


@pytest.fixture(scope="session")
def scanned(tmp_path_factory, _ensure_fixture):
    from ansible_repo_intelligence.ansible_config import load_ansible_config
    from ansible_repo_intelligence.app_config import AppConfig
    from ansible_repo_intelligence.diagnostics import Diagnostics
    from ansible_repo_intelligence.discovery import discover
    from ansible_repo_intelligence.graph import build_graph
    from ansible_repo_intelligence.significance import load_significance_engine
    from ansible_repo_intelligence.variables import load_precedence_config

    out = tmp_path_factory.mktemp("ctx")
    cfg = AppConfig(repo=FIXTURE, output=out)
    acfg = load_ansible_config(FIXTURE)
    sig = load_significance_engine(ROOT / "config" / "significance_rules.yaml")
    pcfg = load_precedence_config(ROOT / "config" / "variable_precedence_rules.yaml")
    diags = Diagnostics()
    disc = discover(cfg, acfg)
    graph = build_graph(cfg, acfg, disc, sig, pcfg, diags)
    return cfg, acfg, disc, graph, diags
