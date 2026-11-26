"""Tests for scripts/as_built_tenants.py, lifted with the module from me/nas tests/test_nas_tenants.py at 8d8af5c (DL-072): tenant rules fail when broken, healthy nights give identical files, secrets never show.

Run: just test (unittest discovery in tests/). Nothing real is called: the node output is built here.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("tenants", Path(__file__).resolve().parents[1] / "scripts" / "as_built_tenants.py")
tenants = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tenants)

NOW = 1_800_000_000
GOOD = {
  "name": "web",
  "protection": 1,
  "scsi0": "local-zfs:vm-701-disk-0,backup=1,size=16G",
  "scsi1": "tank-demo:vm-701-disk-1,backup=0,size=50G",
  "ide2": "local-zfs:vm-701-cloudinit,media=cdrom",
  "ipconfig0": "gw=10.0.0.1,ip=10.0.0.21/24",
  "cipassword": "hunter2",
  "sshkeys": "ssh-ed25519%20AAAA",
  "digest": "abc",
}


def node_output(configs: dict, pools: dict, backup_age: int = 3600, quota_used: int = 5 * 1024**3) -> str:
  """Fake node_script() output.

  Args:
    configs: {vmid: config}.
    pools: {vmid: pool name or None}.
    backup_age: seconds since each guest's newest backup.
    quota_used: bytes used in tank/demo.

  Returns:
    Text in the node script's format.

  """
  res = [{"vmid": v, "type": "qemu", "status": "running", "pool": pools[v], "maxmem": 2 * 1024**3, "maxcpu": 1} for v in configs]
  text = "== resources\n" + json.dumps(res) + "\n"
  for v, c in configs.items():
    text += f"== config qemu/{v}\n" + json.dumps(c) + "\n"
  text += f"== zfs\ntank/demo\tquota\t{300 * 1024**3}\ntank/demo\tused\t{quota_used}\n"
  text += "== backups vm-backup-staging\n" + json.dumps([{"vmid": v, "ctime": NOW - backup_age} for v in configs]) + "\n"
  return text


class TenantReviewTest(unittest.TestCase):
  """Rules, stability and masking."""

  def setUp(self) -> None:
    """A config folder with one registered tenant and one provider pool.

    Args:
      None.

    Returns:
      None.

    """
    self.tmp = tempfile.TemporaryDirectory()
    self.conf = Path(self.tmp.name)
    (self.conf / "tenants.conf").write_text("# x\nnas|100|149|me/nas\ndemo|700|719|demo-project\n")
    (self.conf / "guest-budgets.conf").write_text("demo|4096|2\n")

  def tearDown(self) -> None:
    """Remove the temporary folder.

    Args:
      None.

    Returns:
      None.

    """
    self.tmp.cleanup()

  def findings(self, configs: dict, pools: dict | None = None, **kw) -> str:
    """Summary text for the given guests.

    Args:
      configs: {vmid: config}.
      pools: {vmid: pool}; default all in demo.
      **kw: passed to node_output.

    Returns:
      tenants/summary.txt.

    """
    pools = pools or dict.fromkeys(configs, "demo")
    return tenants.review(node_output(configs, pools, **kw), self.conf, NOW)["tenants/summary.txt"]

  def test_good_guest_has_no_findings(self) -> None:
    """A guest that follows doc 10 gives `none`.

    Args:
      None.

    Returns:
      None.

    """
    self.assertIn("== findings\nnone\n", self.findings({701: GOOD}))

  def test_each_rule_can_fail(self) -> None:
    """Range, protection, storage, data-disk backup, tank/secure, budget and backup age each raise a finding.

    Args:
      None.

    Returns:
      None.

    """
    cases = {
      "outside the pool's range": ({650: GOOD}, {}),
      "protection is off": ({701: {**GOOD, "protection": 0}}, {}),
      "not one of": ({701: {**GOOD, "scsi2": "tank-media:vm-701-disk-2,backup=0"}}, {}),
      "without backup=0": ({701: {**GOOD, "scsi1": "tank-demo:vm-701-disk-1,size=50G"}}, {}),
      "tank/secure": ({701: {**GOOD, "virtiofs0": "dirid=secure-photos"}}, {}),
      "over its RAM": ({701: GOOD, 702: {**GOOD, "ipconfig0": "ip=10.0.0.22/24"}, 703: {**GOOD, "ipconfig0": "ip=10.0.0.23/24"}}, {}),
      "STALE": ({701: GOOD}, {"backup_age": 3 * 86400}),
    }
    for needle, (configs, kw) in cases.items():
      with self.subTest(needle):
        self.assertIn(needle, self.findings(configs, **kw))

  def test_guest_outside_every_backup_job(self) -> None:
    """A guest Proxmox lists as not backed up by any job is a finding even with an old backup on disk.

    Args:
      None.

    Returns:
      None.

    """
    text = node_output({701: GOOD}, {701: "demo"}) + '== unprotected\n[{"vmid": 701, "type": "qemu"}]\n'
    self.assertIn("NOT IN ANY BACKUP JOB", tenants.review(text, self.conf, NOW)["tenants/summary.txt"])

  def test_duplicate_address_and_unregistered_pool(self) -> None:
    """Two guests on one address, a pool not in tenants.conf and a guest in no pool are reported.

    Args:
      None.

    Returns:
      None.

    """
    out = self.findings({701: GOOD, 702: GOOD, 720: GOOD}, {701: "demo", 702: "other", 720: None})
    self.assertIn("address 10.0.0.21 used by guests 701, 702", out)
    self.assertIn("pool other is not registered", out)
    self.assertIn("qemu 720 is in no pool", out)

  def test_provider_pool_is_not_held_to_tenant_rules(self) -> None:
    """The NAS's own pool may use tank/secure and its own storages.

    Args:
      None.

    Returns:
      None.

    """
    out = self.findings({110: {**GOOD, "protection": 0, "virtiofs0": "dirid=secure-photos"}}, {110: "nas"})
    self.assertIn("none", out)

  def test_healthy_nights_are_byte_identical(self) -> None:
    """Backup an hour or twenty ago and a few MiB more used give the same files.

    Args:
      None.

    Returns:
      None.

    """
    a = tenants.review(node_output({701: GOOD}, {701: "demo"}, backup_age=3600), self.conf, NOW)
    b = tenants.review(node_output({701: GOOD}, {701: "demo"}, backup_age=20 * 3600, quota_used=5 * 1024**3 + 7 * 1024**2), self.conf, NOW)
    self.assertEqual(a, b)

  def test_secrets_and_digest_are_left_out(self) -> None:
    """cipassword, sshkeys and digest never reach the file.

    Args:
      None.

    Returns:
      None.

    """
    text = tenants.review(node_output({701: GOOD}, {701: "demo"}), self.conf, NOW)["tenants/demo.txt"]
    for leaked in ("hunter2", "AAAA", "digest"):
      self.assertNotIn(leaked, text)

  def test_empty_read_writes_nothing(self) -> None:
    """A failed node read produces no files rather than empty ones.

    Args:
      None.

    Returns:
      None.

    """
    self.assertEqual(tenants.review("", self.conf, NOW), {})


if __name__ == "__main__":
  unittest.main()
