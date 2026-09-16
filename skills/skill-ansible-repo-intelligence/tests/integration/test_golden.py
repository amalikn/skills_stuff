"""Golden-file acceptance test.

Scans the multi_role_repo fixture and compares every generated artifact
byte-for-byte against the committed golden set. Outputs are deterministic (no
timestamps in content, repo-relative paths only), so an exact diff is the
correct contract. If this test fails after an intentional change, regenerate
the golden set with `just golden` and review the diff.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ansible_repo_intelligence.cli import main

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "multi_role_repo"
GOLDEN = ROOT / "tests" / "golden" / "multi_role_repo"

ARTIFACTS = ("manifest.yaml", "ANSIBLE_REPO_MAP.md", "graph.yaml",
             "diagnostics.yaml", "cache/scan-state.yaml")


def _fresh_scan(out: Path) -> int:
    subprocess.run([sys.executable, str(ROOT / "tests" / "_gen_fixture.py")],
                   check=True, capture_output=True)
    return main(["scan", "--repo", str(FIXTURE), "--output", str(out),
                 "--offline", "--strict"])


def test_golden_matches_byte_for_byte(tmp_path):
    assert GOLDEN.is_dir(), "golden set missing; run `just golden` to create it"
    out = tmp_path / "out"
    assert _fresh_scan(out) == 0
    diffs = []
    for rel in ARTIFACTS:
        got = (out / rel)
        gold = (GOLDEN / rel)
        assert gold.is_file(), f"golden missing {rel}"
        assert got.is_file(), f"scan did not produce {rel}"
        if got.read_bytes() != gold.read_bytes():
            diffs.append(rel)
    assert not diffs, f"golden drift in: {diffs} (regenerate with `just golden` if intended)"


def test_golden_validates(tmp_path):
    # The committed golden set must itself pass validation.
    assert main(["validate", "--context", str(GOLDEN)]) == 0


def test_golden_scan_is_repeatable(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    assert _fresh_scan(a) == 0
    assert _fresh_scan(b) == 0
    for rel in ARTIFACTS:
        assert (a / rel).read_bytes() == (b / rel).read_bytes(), f"non-deterministic: {rel}"
