"""Offline tests for the helpers in scripts/: the batched SSH reader ("pve_ssh"), the least-privilege audit ("pve_token_audit")
and the node report ("pve_node_report"), plus the governance checker ("check_governance") as the pack's gate.

Run: just test (the pack venv), or python -m unittest discover -s tests -p 'test_*.py'. Fixtures are synthetic: no real
node, address or secret.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
pve_ssh = importlib.import_module("pve_ssh")
audit_mod = importlib.import_module("pve_token_audit")
report_mod = importlib.import_module("pve_node_report")

ROLES = [
  {"roleid": "PVEAdmin", "special": 1, "privs": "VM.Allocate,Sys.Console,Sys.Audit,Datastore.Allocate,Pool.Allocate,SDN.Use"},
  {"roleid": "LabTofu", "privs": "VM.Allocate,VM.Audit,VM.Config.Disk,Datastore.AllocateSpace,SDN.Use"},
  {"roleid": "LabRead", "privs": "Sys.Audit"},
  {"roleid": "Downloader", "privs": "Datastore.AllocateTemplate,Sys.Audit,Sys.Modify"},
]
USERS = [
  {"userid": "root@pam", "enable": 1, "tokens": None},
  {"userid": "wide@pve", "enable": 1, "tokens": [{"tokenid": "auto", "privsep": 0, "expire": 0}]},
  {"userid": "lab@pve", "enable": 1, "tokens": [{"tokenid": "tofu", "privsep": 1, "expire": 1900000000}]},
]


def acl(path, role, kind, ugid, propagate=1):
  """One ACL row as GET /access/acl returns it.

  Args:
    path: ACL path.
    role: role id.
    kind: user, group or token.
    ugid: user, group or token id.
    propagate: 1 or 0.

  Returns:
    The row.
  """
  return {"path": path, "roleid": role, "type": kind, "ugid": ugid, "propagate": propagate}


LEAST = [
  acl("/pool/lab", "LabTofu", "user", "lab@pve"), acl("/pool/lab", "LabTofu", "token", "lab@pve!tofu"),
  acl("/storage/local", "LabTofu", "user", "lab@pve"), acl("/storage/local", "LabTofu", "token", "lab@pve!tofu"),
  acl("/nodes", "LabRead", "user", "lab@pve"), acl("/nodes", "LabRead", "token", "lab@pve!tofu"),
]


class Batch(unittest.TestCase):
  """pve_ssh builds one script and splits its output back by key."""

  def test_round_trip(self):
    script = pve_ssh.batch_script({"a": "echo 1", "b": "echo 2"})
    self.assertIn(pve_ssh.MARK + " a", script)
    text = f"{pve_ssh.MARK} a\n1\n{pve_ssh.MARK} b\n2\nmore\n"
    self.assertEqual(pve_ssh.split_batch(text), {"a": "1", "b": "2\nmore"})

  def test_pvesh_is_a_get(self):
    self.assertEqual(pve_ssh.pvesh("/version"), "pvesh get /version --output-format json")

  def test_non_json_output_fails_closed(self):
    with self.assertRaises(pve_ssh.PveReadError):
      pve_ssh.as_json({"x": "403 Permission check failed"}, "x")
    self.assertEqual(pve_ssh.as_json({}, "x", []), [])

  def test_dir_runner_reads_captures(self):
    with tempfile.TemporaryDirectory() as tmp:
      Path(tmp, "acl.json").write_text("[]", encoding="utf-8")
      raw = pve_ssh.dir_runner(tmp)({"acl": "", "missing": ""})
    self.assertEqual(raw, {"acl": "[]", "missing": ""})

  def test_ssh_runner_has_a_timeout(self):
    calls = {}

    def fake_run(argv, **kw):
      calls.update(kw)
      return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    original = pve_ssh.subprocess.run
    pve_ssh.subprocess.run = fake_run
    try:
      self.assertEqual(pve_ssh.ssh_runner("node.example", timeout=7)("true"), "ok")
    finally:
      pve_ssh.subprocess.run = original
    self.assertEqual(calls["timeout"], 7)


class Audit(unittest.TestCase):
  """pve_token_audit names the wide automation identity and passes the least-privilege one."""

  def rules(self, users, rows):
    return {(f.rule, f.subject) for f in audit_mod.audit(users, rows, ROLES)}

  def test_least_privilege_pattern_is_clean(self):
    found = audit_mod.audit([USERS[0], USERS[2]], LEAST, ROLES)
    self.assertEqual([f for f in found if f.severity in ("high", "medium")], [])

  def test_wide_identity_is_high(self):
    rows = LEAST + [acl("/", "PVEAdmin", "user", "wide@pve")]
    got = self.rules(USERS, rows)
    self.assertIn(("token-not-separated", "wide@pve!auto"), got)
    self.assertIn(("broad-root-grant", "wide@pve"), got)
    self.assertIn(("token-no-expiry", "wide@pve!auto"), got)

  def test_root_pam_is_allowed(self):
    got = self.rules(USERS[:1], [acl("/", "PVEAdmin", "user", "root@pam")])
    self.assertNotIn(("broad-root-grant", "root@pam"), got)

  def test_token_grant_without_user_grant_is_flagged(self):
    rows = [acl("/storage/local", "LabTofu", "token", "lab@pve!tofu")]
    self.assertIn(("token-acl-without-user", "lab@pve!tofu"), self.rules(USERS[2:], rows))

  def test_user_grant_above_with_propagate_covers_token(self):
    rows = [acl("/storage", "LabTofu", "user", "lab@pve"), acl("/storage/local", "LabTofu", "token", "lab@pve!tofu")]
    self.assertNotIn(("token-acl-without-user", "lab@pve!tofu"), self.rules(USERS[2:], rows))
    rows[0]["propagate"] = 0
    self.assertIn(("token-acl-without-user", "lab@pve!tofu"), self.rules(USERS[2:], rows))

  def test_dangerous_privilege_on_a_token(self):
    rows = LEAST + [acl("/nodes/n1", "Downloader", "user", "lab@pve"), acl("/nodes/n1", "Downloader", "token", "lab@pve!tofu")]
    self.assertIn(("dangerous-privilege", "lab@pve!tofu"), self.rules(USERS[2:], rows))

  def test_cli_exit_codes(self):
    with tempfile.TemporaryDirectory() as tmp:
      Path(tmp, "users.json").write_text(json.dumps(USERS), encoding="utf-8")
      Path(tmp, "roles.json").write_text(json.dumps(ROLES), encoding="utf-8")
      Path(tmp, "acl.json").write_text(json.dumps(LEAST), encoding="utf-8")
      with contextlib.redirect_stdout(io.StringIO()):
        self.assertEqual(audit_mod.main(["--from-dir", tmp]), 1)  # wide@pve!auto has privsep 0
        Path(tmp, "users.json").write_text(json.dumps([USERS[0], USERS[2]]), encoding="utf-8")
        self.assertEqual(audit_mod.main(["--from-dir", tmp]), 0)
      with contextlib.redirect_stderr(io.StringIO()):
        Path(tmp, "acl.json").write_text("not json", encoding="utf-8")
        self.assertEqual(audit_mod.main(["--from-dir", tmp]), 2)


class Report(unittest.TestCase):
  """pve_node_report turns captures into sections and warnings."""

  RAW = {
    "version": json.dumps({"version": "9.1.5", "release": "9.1"}),
    "status": json.dumps({"uptime": 100, "current-kernel": {"release": "6.17.9-1-pve"}, "memory": {"used": 1, "total": 4},
                          "rootfs": {"used": 1, "total": 2}}),
    "updates": json.dumps([{"Package": "pve-manager", "OldVersion": "9.1.5", "Version": "9.2.26"}, {"Package": "apt"}]),
    "repos": json.dumps({"files": [{"path": "/etc/apt/sources.list.d/pve-no-subscription.list", "file-type": "list",
                                    "repositories": [{"Enabled": 1, "Suites": ["trixie"], "Components": ["pve-no-subscription"]}]}]}),
    "storage": json.dumps([{"storage": "thin", "type": "lvmthin", "total": 100, "used": 91, "active": 1, "content": "images"},
                           {"storage": "local", "type": "dir", "total": 100, "used": 10, "active": 1, "content": "import,iso"}]),
    "resources": json.dumps([{"type": "qemu", "vmid": 901, "name": "lab-01", "status": "running", "pool": "lab"},
                             {"type": "storage", "id": "storage/x"}]),
    "pools": json.dumps([{"poolid": "lab"}]),
    "daily": "Result=success\nExecMainExitTimestamp=Sat 2026-11-07 01:47:04 UTC",
    "users": json.dumps(USERS[2:]), "acl": json.dumps(LEAST), "roles": json.dumps(ROLES),
  }

  def test_sections_and_warnings(self):
    rep = report_mod.summarise(self.RAW)
    self.assertEqual(rep["version"], "9.1.5")
    self.assertEqual(rep["memory_pct"], 25.0)
    self.assertEqual(rep["updates"]["pending"], 2)
    self.assertEqual(rep["updates"]["pve_stack"], ["pve-manager 9.1.5 -> 9.2.26"])
    self.assertEqual([g["vmid"] for g in rep["guests"]], [901])
    joined = " | ".join(rep["warnings"])
    self.assertIn("full-upgrade", joined)
    self.assertIn("storage thin 91.0% used", joined)
    self.assertIn("modernize-sources", joined)
    self.assertNotIn("high access", joined)
    self.assertIn("apt update NOT run", report_mod.render(rep))

  def test_quiet_node_has_no_warnings(self):
    raw = dict(self.RAW, updates="[]", repos="{}", storage=json.dumps([{"storage": "local", "total": 10, "used": 1, "active": 1}]))
    self.assertEqual(report_mod.summarise(raw)["warnings"], [])

  def test_refresh_needs_apply(self):
    scripts = []

    def fake_runner(host, user="root"):
      def run(script):
        scripts.append(script)
        return "".join(f"{pve_ssh.MARK} {k}\n{v}\n" for k, v in self.RAW.items())
      return run

    original = pve_ssh.ssh_runner
    pve_ssh.ssh_runner = fake_runner
    try:
      with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        report_mod.main(["--host", "node.example", "--refresh"])
        self.assertFalse(any(report_mod.REFRESH in s for s in scripts), "planned refresh must not run")
        report_mod.main(["--host", "node.example", "--refresh", "--apply"])
    finally:
      pve_ssh.ssh_runner = original
    self.assertTrue(any(s == report_mod.REFRESH for s in scripts))

  def test_failed_refresh_is_a_warning(self):
    raw = dict(self.RAW, daily="Result=exit-code")
    self.assertTrue(any("stale" in w for w in report_mod.summarise(raw)["warnings"]))


class Governance(unittest.TestCase):
  """scripts/check_governance.py ("check_governance") is the pack's governance gate; it runs here so `just test` covers it."""

  PACK = Path(__file__).resolve().parents[1]

  def _run(self, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(root / "scripts" / "check_governance.py")], capture_output=True, text=True,
                          check=False, timeout=120)

  def test_governance_claims_hold(self):
    result = self._run(self.PACK)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

  def test_a_broken_reference_fails_the_gate(self):
    with tempfile.TemporaryDirectory() as tmp:
      copy = Path(tmp) / "pack"
      shutil.copytree(self.PACK, copy, ignore=shutil.ignore_patterns(".git", "documents", "graphify-out", ".ai-context"))
      with (copy / "README.md").open("a", encoding="utf-8") as fh:
        fh.write("\nSee `references/does-not-exist.md`.\n")
      result = self._run(copy)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("does-not-exist.md", result.stdout)


if __name__ == "__main__":
  unittest.main()
