#!/usr/bin/env python3
"""Fixture tests for the enforcement scripts. Stdlib only: `python3 -m unittest discover scripts/tests`.

Each test builds a throwaway project in a temp dir and runs the real scripts against it as subprocesses, exactly as an
agent would. Every test was written to FAIL on the pre-2026-09-27 scripts first (see CHANGELOG, 2026-09-27), so a pass
here means the gap it names is closed, not that the test is too weak to notice.
"""
# claim-scan:examples — every path in this file is a fixture inside a temp project, not a reference.
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # scripts/
PY = sys.executable


def run(script: str, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([PY, str(HERE / script), "--root", str(cwd), *args],
                          cwd=cwd, capture_output=True, text=True, timeout=120)


def git(cwd: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=env, check=True).stdout


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve() / "proj"
        self.root.mkdir()
        git(self.root, "init", "-q")
        write(self.root, "README.md", "# proj\n\n- `docs/` knowledge base\n- `scripts/` tools\n")
        write(self.root, "docs/readme.md", "# docs\n\n- [a.md](a.md)\n")
        write(self.root, "docs/a.md", "# a\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "base")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # a full, reconciling set of receipts, so a test can knock out exactly one thing
    def complete_receipts(self, negtest: bool = True) -> None:
        def r(*a: str) -> subprocess.CompletedProcess:
            return run("audit_state.py", *a, cwd=self.root)

        self.assertEqual(r("init").returncode, 0)
        r("record", "--phase", "0", "--key", "snapshot_path", "--value", "none", "--key", "files_snapshotted",
          "--value", "0")
        cov = json.loads(run("coverage_manifest.py", "--json", cwd=self.root).stdout)
        r("record", "--phase", "1", "--key", "files_total", "--value", str(cov["total"]), "--key", "files_examined",
          "--value", str(cov["examined"]), "--key", "files_exempt", "--value", str(cov["exempt"]),
          "--key", "files_out_of_scope", "--value", "0", "--key", "defects_found", "--value", "0",
          "--key", "systems_of_record", "--value", "0")
        r("record", "--phase", "2", "--key", "defects_fixed", "--value", "0")
        r("record", "--phase", "3", "--key", "banners_added", "--value", "0")
        r("record", "--phase", "4", "--key", "artifacts_total", "--value", "0", "--key", "artifacts_reasoned",
          "--value", "0", "--key", "findings", "--value", "0")
        r("record", "--phase", "5", "--key", "checks_added", "--value", "0")
        r("record", "--phase", "6", "--key", "residual_items", "--value", "0")
        r("record", "--phase", "7", "--key", "claims_total", "--value", "0", "--key", "claims_verified", "--value",
          "0", "--key", "claims_historical", "--value", "0", "--key", "claims_residual", "--value", "0")


# ── S1: the gate must not delete the audit's evidence before a report holds it ──────────────────────────────────────
class ReportBeforeCleanup(Fixture):
    def _scratch(self) -> None:
        write(self.root, ".staleness-audit/defect-register.md",
              "# Defect register\n\n| # | Mat | File:line | Defect |\n|---|---|---|---|\n| D1 | G | docs/a.md:1 | stale |\n")
        write(self.root, ".staleness-audit/phase4-worksheet.md",
              "# Phase 4\n\n| Artifact | Verdict |\n|---|---|\n| `x.py` | clear: touches nothing |\n")

    def test_pass_without_report_keeps_scratch_and_fails(self) -> None:
        self.complete_receipts()
        self._scratch()
        out = run("verify_completeness.py", cwd=self.root)
        self.assertNotEqual(out.returncode, 0, out.stdout)
        self.assertIn("report", out.stdout.lower())
        self.assertTrue((self.root / ".staleness-audit/defect-register.md").is_file(), "evidence deleted")

    def test_report_embeds_evidence_then_gate_cleans_up(self) -> None:
        self.complete_receipts()
        self._scratch()
        w = run("audit_report.py", "--out-dir", "docs/reports/staleness-audits", "--stamp", "20260927_1800",
                cwd=self.root)
        self.assertEqual(w.returncode, 0, w.stdout + w.stderr)
        rep = self.root / "docs/reports/staleness-audits/staleness-audit-20260927_1800.md"
        text = rep.read_text()
        self.assertIn("docs/a.md:1 | stale", text)
        self.assertIn("clear: touches nothing", text)
        # the report is a new doc; index it so the inverse sweep stays clean, as a project would
        write(self.root, "docs/reports/staleness-audits/readme.md",
              "# audits\n\n- [staleness-audit-20260927_1800.md](staleness-audit-20260927_1800.md)\n")
        write(self.root, "docs/reports/readme.md", "# reports\n\n- [staleness-audits/](staleness-audits/readme.md)\n")
        write(self.root, "docs/readme.md", "# docs\n\n- [a.md](a.md)\n- [reports/](reports/readme.md)\n")
        # an unfilled narrative blocks the gate; the agent fills it (simulated: keep only the evidence block)
        blocked = run("verify_completeness.py", cwd=self.root)
        self.assertIn("placeholder", blocked.stdout)
        self.assertTrue((self.root / ".staleness-audit").is_dir())
        rep.write_text("# Staleness audit — proj — 2026-09-27\n\nOne G finding, fixed.\n\n"
                       + text[text.index("<!-- BEGIN staleness-audit:evidence"):])
        out = run("verify_completeness.py", "--old-value", "stale-old-value", cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertFalse((self.root / ".staleness-audit").exists())
        self.assertIn("GATE PASSED", rep.read_text())

    def test_stale_report_blocks(self) -> None:
        self.complete_receipts()
        self._scratch()
        run("audit_report.py", "--out-dir", "docs/audits", "--stamp", "20260927_1800", cwd=self.root)
        rep = self.root / "docs/audits/staleness-audit-20260927_1800.md"
        text = rep.read_text()
        rep.write_text("# filled\n\n" + text[text.index("<!-- BEGIN staleness-audit:evidence"):])
        write(self.root, "docs/audits/readme.md", "# a\n\n- [r](staleness-audit-20260927_1800.md)\n")
        write(self.root, "docs/readme.md", "# docs\n\n- [a.md](a.md)\n- [audits/](audits/readme.md)\n")
        # the register changed after the report was written: the report no longer holds the evidence
        with (self.root / ".staleness-audit/defect-register.md").open("a") as f:
            f.write("| D2 | G | docs/a.md:2 | also stale |\n")
        out = run("verify_completeness.py", cwd=self.root)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("is stale", out.stdout)
        self.assertTrue((self.root / ".staleness-audit").is_dir())


# ── S2: an index that exists but lists nothing is not an index ──────────────────────────────────────────────────────
class IndexContents(Fixture):
    def test_empty_index_is_found(self) -> None:
        write(self.root, "captures/readme.md", "# captures\n\nRaw captures from the boxes.\n")
        for n in ("umoona.txt", "pia.txt", "malik.txt"):
            write(self.root, f"captures/{n}", "x\n")
        write(self.root, "README.md", "# proj\n\n- `docs/`\n- `captures/`\n")
        out = run("inverse_sweep.py", cwd=self.root)
        self.assertNotEqual(out.returncode, 0, out.stdout)
        self.assertIn("EMPTY-INDEX", out.stdout)

    def test_partial_index_names_the_missing_entry(self) -> None:
        write(self.root, "docs/b.md", "# b\n")
        out = run("inverse_sweep.py", cwd=self.root)
        self.assertNotEqual(out.returncode, 0, out.stdout)
        self.assertIn("UNLISTED", out.stdout)
        self.assertIn("docs/b.md", out.stdout)

    def test_describes_only_marker_is_honoured(self) -> None:
        write(self.root, "captures/readme.md",
              '# captures\n<!-- inverse-sweep:describes-only reason="bulk dated captures" -->\n')
        for n in ("a.txt", "b.txt"):
            write(self.root, f"captures/{n}", "x\n")
        write(self.root, "README.md", "# proj\n\n- `docs/`\n- `captures/`\n")
        out = run("inverse_sweep.py", cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_marker_named_in_prose_does_not_opt_out(self) -> None:
        write(self.root, "docs/readme.md", "# docs\n\nThe `inverse-sweep:describes-only` marker opts out.\n")
        write(self.root, "docs/b.md", "# b\n")
        out = run("inverse_sweep.py", cwd=self.root)
        self.assertIn("EMPTY-INDEX", out.stdout)

    def test_directory_named_as_path_segment_counts(self) -> None:
        write(self.root, "docs/mock/Dockerfile", "FROM x\n")
        write(self.root, "docs/readme.md", "# docs\n\n- [a.md](a.md)\n\n```bash\ndocker build -t m ./docs/mock\n```\n")
        out = run("inverse_sweep.py", cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stdout)

    def test_directory_named_only_as_a_word_is_unlisted(self) -> None:
        write(self.root, "docs/mock/Dockerfile", "FROM x\n")
        write(self.root, "docs/readme.md", "# docs\n\n- [a.md](a.md)\n\nBuild the mock first.\n")
        out = run("inverse_sweep.py", cwd=self.root)
        self.assertIn("docs/mock/", out.stdout)

    def test_complete_index_is_clean(self) -> None:
        out = run("inverse_sweep.py", cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stdout)


# ── S3 + S8: claim classes ──────────────────────────────────────────────────────────────────────────────────────────
class ClaimClasses(Fixture):
    def setUp(self) -> None:
        super().setUp()
        sib = self.root.parent / "sibling-repo"
        write(sib, "references/01_overview.md", "x\n")
        write(self.root, "scripts/check_governance.py",
              'SIBLING_ROOTS: dict[str, str] = {\n    "sib": "../sibling-repo",\n}\n'
              'CONDITIONAL_PATHS: frozenset[str] = frozenset({\n    "Taskfile.yml",  # uses just\n})\n')

    def scan(self, body: str) -> dict:
        write(self.root, "docs/a.md", body)
        return json.loads(run("claim_scan.py", "--json", cwd=self.root).stdout)

    def states(self, d: dict, claim: str) -> list[str]:
        return [c["state"] for c in d["claims"] if c["claim"] == claim]

    def test_sibling_path_verified(self) -> None:
        d = self.scan("See `references/01_overview.md` and `01_overview.md`.\n")
        self.assertEqual(self.states(d, "references/01_overview.md"), ["VERIFIED"])
        self.assertEqual(self.states(d, "01_overview.md"), ["VERIFIED"])

    def test_sibling_name_prefix_verified(self) -> None:
        d = self.scan("See `sib/references/01_overview.md`.\n")
        self.assertEqual(self.states(d, "sib/references/01_overview.md"), ["VERIFIED"])

    def test_on_box_and_conditional(self) -> None:
        d = self.scan("Box file `/etc/netplan/00-ansible.yaml`.\nUse `Taskfile.yml`.\n"
                      "Read `memory-bank/progress.md` when present.\nGone: `docs/missing.md`.\n")
        self.assertEqual(self.states(d, "/etc/netplan/00-ansible.yaml"), ["ON-BOX"])
        self.assertEqual(self.states(d, "Taskfile.yml"), ["CONDITIONAL"])
        self.assertEqual(self.states(d, "memory-bank/progress.md"), ["CONDITIONAL"])
        self.assertEqual(self.states(d, "docs/missing.md"), ["BROKEN"])

    def test_version_numbers_are_not_counts(self) -> None:
        d = self.scan("Read the 6.6.0.3 docs and v2 files.\nThere are 1,225 checks.\n")
        claims = [c["claim"] for c in d["claims"] if c["type"] == "count"]
        self.assertNotIn("3 docs", claims)
        self.assertNotIn("2 files", claims)
        self.assertIn("1,225 checks", claims)

    def test_dated_section_is_history(self) -> None:
        d = self.scan("# log\n\n## 2026-09-20 session\n\n- 12 sites seeded\n\n## Current\n\n- 9 sites live\n")
        self.assertEqual(self.states(d, "12 sites"), ["MARKED-HISTORICAL"])
        self.assertEqual(self.states(d, "9 sites"), ["NEEDS-MANUAL"])

    def test_residual_reconciles_with_new_classes(self) -> None:
        self.complete_receipts()
        self.scan("`/etc/x/y.conf.yaml` `Taskfile.yml` `docs/missing.md` 3 sites\n")
        run("claim_scan.py", "--record", cwd=self.root)
        st = json.loads(run("audit_state.py", "status", "--json", cwd=self.root).stdout)
        p7 = st["phases"]["7"]["data"]
        self.assertEqual(p7["claims_total"],
                         p7["claims_verified"] + p7["claims_historical"] + p7["claims_residual"])
        self.assertGreaterEqual(p7.get("claims_residual_on_box", 0), 1)


# ── S4: negative-test evidence, not a typed count ───────────────────────────────────────────────────────────────────
class NegTest(Fixture):
    def setUp(self) -> None:
        super().setUp()
        self.complete_receipts()
        write(self.root, "check.py",
              "import pathlib,sys\nbad=pathlib.Path('BROKEN').exists()\n"
              "print('FAIL check_x: BROKEN present' if bad else 'check_x ok')\nsys.exit(1 if bad else 0)\n")
        run("audit_state.py", "record", "--phase", "5", "--key", "checks_added", "--value", "1", cwd=self.root)

    def status(self) -> dict:
        return json.loads(run("audit_state.py", "status", "--json", cwd=self.root).stdout)

    def test_typed_count_is_refused(self) -> None:
        out = run("audit_state.py", "record", "--phase", "5", "--key", "checks_negative_tested", "--value", "1",
                  cwd=self.root)
        self.assertNotEqual(out.returncode, 0)
        self.assertTrue(self.status()["reconcile_issues"])

    def test_red_that_passes_is_refused(self) -> None:
        out = run("audit_state.py", "negtest", "red", "--check", "x", "--expect", "FAIL check_x", "--cmd",
                  f"{PY} check.py", cwd=self.root)
        self.assertNotEqual(out.returncode, 0, out.stdout)
        self.assertIn("exited 0 while the project was broken", out.stderr)

    def test_red_then_green_counts(self) -> None:
        (self.root / "BROKEN").write_text("")
        red = run("audit_state.py", "negtest", "red", "--check", "x", "--expect", "FAIL check_x", "--cmd",
                  f"{PY} check.py", cwd=self.root)
        self.assertEqual(red.returncode, 0, red.stdout + red.stderr)
        (self.root / "BROKEN").unlink()
        green = run("audit_state.py", "negtest", "green", "--check", "x", cwd=self.root)
        self.assertEqual(green.returncode, 0, green.stdout + green.stderr)
        st = self.status()
        self.assertEqual(st["phases"]["5"]["data"]["checks_negative_tested"], 1)
        self.assertEqual(st["reconcile_issues"], [])

    def test_expect_text_in_passing_output_is_refused(self) -> None:
        (self.root / "BROKEN").write_text("")
        run("audit_state.py", "negtest", "red", "--check", "x", "--expect", "check_x", "--cmd", f"{PY} check.py",
            cwd=self.root)
        (self.root / "BROKEN").unlink()
        green = run("audit_state.py", "negtest", "green", "--check", "x", cwd=self.root)
        self.assertNotEqual(green.returncode, 0, green.stdout)
        self.assertIn("not failure-specific", green.stderr)
        self.assertEqual(self.status()["phases"]["5"]["data"]["checks_negative_tested"], 0)


# ── S5 + S7: Phase 4 worksheet ──────────────────────────────────────────────────────────────────────────────────────
class Worksheet(Fixture):
    def test_live_enumeration_and_reach_flags(self) -> None:
        write(self.root, "scripts/install.py",
              '"""Install a package on every box."""\nfor loc in nb.dcim.locations.all():\n'
              '    ssh(loc.box, "apt-get install -y fping")\n')
        out = run("artifact_signals.py", cwd=self.root).stdout
        self.assertIn("enumerates-live?", out)
        self.assertIn("REACH?", out)
        self.assertIn("inventory", out.lower())

    def test_since_flags_changed_without_shrinking_denominator(self) -> None:
        write(self.root, "scripts/old.py", '"""old"""\n')
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "old")
        base = git(self.root, "rev-parse", "HEAD").strip()
        write(self.root, "scripts/new.py", '"""new"""\n')
        out = run("artifact_signals.py", "--since", base, cwd=self.root).stdout
        self.assertIn("Artifacts: **2**", out)
        new_row = [ln for ln in out.splitlines() if "scripts/new.py" in ln][0]
        old_row = [ln for ln in out.splitlines() if "scripts/old.py" in ln][0]
        self.assertIn("CHANGED", new_row)
        self.assertNotIn("CHANGED", old_row)


# ── S6 + gate: required receipt keys are enforced, not only listed ──────────────────────────────────────────────────
class RequiredKeys(Fixture):
    def test_gate_blocks_on_missing_required_key(self) -> None:
        self.complete_receipts()
        st = json.loads((self.root / ".staleness-audit/state.json").read_text())
        del st["phases"]["1"]["data"]["systems_of_record"]
        (self.root / ".staleness-audit/state.json").write_text(json.dumps(st))
        out = run("verify_completeness.py", cwd=self.root)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("systems_of_record", out.stdout)

    def test_system_of_record_sample_must_cover_changes(self) -> None:
        self.complete_receipts()
        run("audit_state.py", "record", "--phase", "1", "--key", "systems_of_record", "--value", "1",
            "--key", "sor_objects_changed", "--value", "12", "--key", "sor_objects_read", "--value", "3",
            cwd=self.root)
        st = json.loads(run("audit_state.py", "status", "--json", cwd=self.root).stdout)
        self.assertTrue(any("system" in i for i in st["reconcile_issues"]), st["reconcile_issues"])

    def test_inverse_sweep_record_keeps_state_readable(self) -> None:
        run("audit_state.py", "init", cwd=self.root)
        run("inverse_sweep.py", "--record", cwd=self.root)
        out = run("audit_state.py", "record", "--phase", "7", "--key", "claims_total", "--value", "0",
                  cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stderr)


if __name__ == "__main__":
    unittest.main()


# ── Coverage: files the rules missed on unified-network-controller, 2026-09-28 ─────────────────────────────────────────
class CoverageFileKinds(Fixture):
    def test_env_plist_hcl_and_shebang_scripts_are_classified(self) -> None:
        write(self.root, "wc/.env", "A=1\n")
        write(self.root, "wc/launchd/job.plist", "<plist/>\n")
        write(self.root, "wc/openbao.hcl", "storage {}\n")
        write(self.root, "scripts/githooks/pre-commit", "#!/usr/bin/env bash\nexit 0\n")
        write(self.root, "notes/NOEXT", "plain text, no shebang\n")
        git(self.root, "add", "-A")
        cov = json.loads(run("coverage_manifest.py", "--json", cwd=self.root).stdout)
        self.assertEqual(cov["unclassified_files"], ["notes/NOEXT"])
        self.assertEqual((cov["by_class"].get("runtime-config"), cov["by_class"].get("code")), (3, 1))


class SinceLastAudit(Fixture):
    def test_claim_scan_resolves_last_audit_like_init(self) -> None:
        write(self.root, "docs/staleness-audit-20260101_0000.md", "# audit\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "audit")
        write(self.root, "docs/a.md", "# a changed\n")
        r = run("claim_scan.py", "--json", "--since", "last-audit", cwd=self.root)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("last-audit", json.loads(r.stdout)["since"])
