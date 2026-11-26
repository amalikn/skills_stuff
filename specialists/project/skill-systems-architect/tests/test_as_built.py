"""Offline tests for scripts/as_built.py and as_built_probes.py: a fake runner stands in for SSH and local commands. Run: just test."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
_spec = importlib.util.spec_from_file_location("as_built", _SCRIPTS / "as_built.py")
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)


def fake_runner(answers: dict[str, str], counter: list | None = None):
  """A runner answering by substring of the last argument.

  Args:
    answers: substring of the command to output.
    counter: when given, an int list whose first item is appended to every output (simulates churn).

  Returns:
    The runner.
  """

  def run(cmd, stdin=None, timeout=0):
    """Answer one command.

    Args:
      cmd: argv; stdin: ignored; timeout: ignored.
    Returns:
      (0, output).
    """
    last = cmd[-1]
    for key, out in answers.items():
      if key in last:
        if counter is not None:
          counter[0] += 1
          return 0, out + f"tick {counter[0]}\n"
        return 0, out
    return 0, ""

  return run


class Masking(unittest.TestCase):
  """Secrets and emails never reach a capture file."""

  def test_masks(self):
    """Secret-shaped values, tokens and emails are replaced; fingerprints and digests stay.

    Args:
      None.
    Returns:
      None.
    """
    raw = "cipassword: x\npassword=hunter2\nroot hvs.ABCDEFGHIJKLMNOPQRSTUVWX12\nowner admin@example.org\nSHA256:fA0b0Dv17b2l sha256:47e43b1b"
    out = ab.mask(raw, [])
    for bad in ("hunter2", "hvs.ABCDEFGHIJ", "admin@example.org"):
      self.assertNotIn(bad, out)
    self.assertIn("SHA256:fA0b0Dv17b2l sha256:47e43b1b", out)


class Churn(unittest.TestCase):
  """Churn lines go, and --twice catches what is left."""

  def test_drop(self):
    """Lines matching a drop pattern and trailing spaces are removed.

    Args:
      None.
    Returns:
      None.
    """
    self.assertEqual(ab.drop_churn("a  \ntick 1\nb\n\n", ["^tick "]), "a\nb\n")

  def test_twice_detects_and_filters(self):
    """A changing line makes two captures differ; a drop pattern for it makes them identical.

    Args:
      None.
    Returns:
      None.
    """
    t = [{"name": "h", "type": "command", "commands": {"x": "uptime"}}]
    c = [0]
    run = fake_runner({"uptime": "up\n"}, c)
    one, _ = ab.capture({}, t, run)
    two, _ = ab.capture({}, t, run)
    self.assertNotEqual(one, two)
    t[0]["drop"] = ["^tick "]
    self.assertEqual(ab.capture({}, t, run)[0], ab.capture({}, t, run)[0])


class Manifest(unittest.TestCase):
  """Bad manifests are refused before anything runs."""

  def test_refusals(self):
    """Unknown type, missing name and duplicate names give ValueError.

    Args:
      None.
    Returns:
      None.
    """
    with tempfile.TemporaryDirectory() as d:
      for body in (
        '[[target]]\nname="a"\ntype="nope"\n',
        '[[target]]\ntype="hand"\nrows=[]\n',
        '[[target]]\nname="a"\ntype="hand"\nrows=[]\n[[target]]\nname="a"\ntype="hand"\nrows=[]\n',
        '[capture]\ndrop=["[z-a]"]\n[[target]]\nname="a"\ntype="hand"\nrows=[]\n',
      ):
        p = Path(d) / "m.toml"
        p.write_text(body)
        with self.assertRaises(ValueError):
          ab.load_manifest(p)


class Placeholders(unittest.TestCase):
  """Addresses come from the project's resolver, never the manifest; file names can be set."""

  def test_resolve_and_file_name(self):
    """{lan:node} is replaced through [capture.resolvers]; an unknown resolver is refused; `file` renames the output.

    Args:
      None.
    Returns:
      None.
    """
    calls = []

    def run(cmd, stdin=None, timeout=0):
      """Answer the resolver.

      Args:
        cmd: argv; stdin: ignored; timeout: ignored.
      Returns:
        (0, output).
      """
      calls.append(cmd[-1])
      return 0, "10.0.0.5\n"

    cfg = {"resolvers": {"lan": "lanip {key}"}}
    t = ab.resolve({"ssh": "root@{lan:node}", "extra": ["{lan:node}"]}, cfg, Path("/tmp"), run, {})
    self.assertEqual(t, {"ssh": "root@10.0.0.5", "extra": ["10.0.0.5"]})
    self.assertEqual(len(calls), 1)
    with self.assertRaises(ValueError):
      ab.resolve("{nope:x}", cfg, Path("/tmp"), run, {})
    files, _ = ab.capture({}, [{"name": "h", "type": "hand", "file": "services/hand.json", "rows": []}])
    self.assertEqual(list(files), ["services/hand.json"])


class Probes(unittest.TestCase):
  def test_running_container_read_with_pct_exec(self):
    """A running LXC is read on the node through pct exec, not over SSH.

    Args:
      None.
    Returns:
      None.
    """
    seen = []
    pool = json.dumps({"members": [{"vmid": 101, "type": "lxc", "status": "running"}]})

    def run(cmd, stdin=None, timeout=0):
      """Record commands; answer the pool listing.

      Args:
        cmd: argv; stdin: ignored; timeout: ignored.
      Returns:
        (0, output).
      """
      seen.append(cmd[-1])
      return 0, pool if "pvesh get /pools" in cmd[-1] else "x\n"

    ab.capture({}, [{"name": "g", "type": "pve-pool", "ssh": "root@n", "pool": "p"}], run)
    self.assertTrue(any(c.startswith("pct exec 101 -- bash -c ") for c in seen))
    self.assertFalse(any("@" in c for c in seen if c.startswith("ssh")))

  """Probe shapes: one file per target, pve-pool one per guest, sections in name order."""

  def test_pool_files_per_guest(self):
    """A pool with a running VM and a stopped LXC gives two files; the VM is read inside over SSH.

    Args:
      None.
    Returns:
      None.
    """
    pool = json.dumps({"members": [{"vmid": 702, "type": "qemu", "status": "running"}, {"vmid": 101, "type": "lxc", "status": "stopped"}]})
    run = fake_runner({"pvesh get /pools": pool, "qm config 702": "ipconfig0: ip=192.168.86.202/24,gw=192.168.86.1\n", "PRETTY_NAME": "Ubuntu\n"})
    files, failed = ab.capture({}, [{"name": "pool", "type": "pve-pool", "ssh": "root@n", "pool": "p", "guest_user": "ubuntu"}], run)
    self.assertEqual(sorted(files), ["pool/lxc-101.txt", "pool/qemu-702.txt"])
    self.assertIn("== os\nUbuntu", files["pool/qemu-702.txt"])
    self.assertIn("stopped, not read", files["pool/lxc-101.txt"])
    self.assertEqual(failed, [])

  def test_apply_writes_and_plan_does_not(self):
    """Plan reports new without writing; apply writes; a second plan reports same.

    Args:
      None.
    Returns:
      None.
    """
    with tempfile.TemporaryDirectory() as d:
      m = Path(d) / "as-built.toml"
      m.write_text('[capture]\nout="caps"\n[[target]]\nname="router"\ntype="hand"\nrows=[{what="forward 443", value="to .201", checked="2026-11-26"}]\n')
      self.assertEqual(ab.main(["--manifest", str(m)]), 0)
      self.assertFalse((Path(d) / "caps/router.txt").exists())
      self.assertEqual(ab.main(["--manifest", str(m), "--apply"]), 0)
      self.assertIn("forward 443 | to .201", (Path(d) / "caps/router.txt").read_text())
      self.assertEqual(ab.compare(Path(d) / "caps", ab.capture(*ab.load_manifest(m))[0]), {"router.txt": "same"})


def recorder(answer):
  """A runner that records every argv and answers through a function.

  Args:
    answer: function(argv, stdin) -> (rc, output).

  Returns:
    (runner, list of (argv, stdin) seen).
  """
  seen = []

  def run(cmd, stdin=None, timeout=0):
    """Record and answer one command.

    Args:
      cmd: argv; stdin: standard input; timeout: ignored.
    Returns:
      answer(cmd, stdin).
    """
    seen.append((cmd, stdin))
    return answer(cmd, stdin)

  return run, seen


class NodeSide(unittest.TestCase):
  """Capture run on the Proxmox node itself (NAS DL-074/075, continuum TASK-680): local commands, file secrets, guest agent, tenants."""

  def test_local_runs_without_ssh(self):
    """ssh = "local" or no ssh runs proxmox-node, pve-pool, tls-endpoint and command locally; no argv starts with ssh.

    Args:
      None.
    Returns:
      None.
    """
    pool = json.dumps({"members": [{"vmid": 101, "type": "lxc", "status": "running"}]})
    run, seen = recorder(lambda cmd, stdin: (0, pool if "pvesh get /pools" in cmd[-1] else "x\n"))
    targets = [
      {"name": "node", "type": "proxmox-node", "ssh": "local"},
      {"name": "pool", "type": "pve-pool", "pool": "p"},
      {"name": "tls", "type": "tls-endpoint", "ssh": "local", "endpoints": [{"name": "a.example"}]},
      {"name": "cmd", "type": "command", "ssh": "local", "commands": {"x": "true"}},
      {"name": "self", "type": "linux-host", "ssh": "local"},
    ]
    files, failed = ab.capture({}, targets, run)
    self.assertEqual(failed, [])
    self.assertTrue(seen)
    self.assertTrue(all(cmd[0] == "bash" for cmd, _ in seen), [c for c, _ in seen if c[0] != "bash"])
    self.assertTrue(any("pct exec 101" in cmd[-1] for cmd, _ in seen))
    run2, seen2 = recorder(lambda cmd, stdin: (0, "x\n"))
    ab.capture({}, [{"name": "node", "type": "proxmox-node", "ssh": "root@n"}], run2)
    self.assertEqual(seen2[0][0][0], "ssh")

  def test_file_secrets(self):
    """secrets = "file:<path>": keys from entry and field, value used, never written; open modes and missing keys fail only that target.

    Args:
      None.
    Returns:
      None.
    """
    self.assertEqual(ab.probes.secret_key("me/malik-nas/cloudflare/api-token", "Password"), "ME_MALIK_NAS_CLOUDFLARE_API_TOKEN_PASSWORD")
    self.assertEqual(ab.probes.secret_key("me/malik-nas/cloudflare/api-token", "URL"), "ME_MALIK_NAS_CLOUDFLARE_API_TOKEN_URL")
    with tempfile.TemporaryDirectory() as d:
      f = Path(d) / "secrets.env"
      f.write_text("# comment\nME_X_TOKEN_PASSWORD=s3cr3t-value\n")
      f.chmod(0o600)
      cfg = {"secrets": f"file:{f}"}
      kp_called = []
      self.assertEqual(ab.probes.kp_field("me/x-token", "Password", lambda *a: kp_called.append(a) or (0, "kp"), cfg), "s3cr3t-value")
      self.assertEqual(kp_called, [])
      with self.assertRaisesRegex(ValueError, "ME_X_TOKEN_URL not in"):
        ab.probes.kp_field("me/x-token", "URL", None, cfg)
      targets = [
        {"name": "cf", "type": "cloudflare-dns", "token_entry": "me/missing", "zones": ["a.example"]},
        {"name": "ok", "type": "hand", "rows": [{"what": "a", "value": "b"}]},
      ]
      files, failed = ab.capture(cfg, targets, None)
      self.assertEqual(failed, ["cf"])
      self.assertIn("ME_MISSING_PASSWORD not in", files["cf.txt"])
      self.assertNotIn("s3cr3t-value", "".join(files.values()))
      f.chmod(0o640)
      with self.assertRaisesRegex(ValueError, "readable by group or others"):
        ab.probes.kp_field("me/x-token", "Password", None, cfg)
      m = Path(d) / "as-built.toml"
      m.write_text('[capture]\nsecrets="vault"\n')
      with self.assertRaisesRegex(ValueError, "secrets must be"):
        ab.load_manifest(m)

  def test_guest_agent_inside(self):
    """inside = "agent": a running VM is read with qm guest exec on the node; exit codes, timeouts (pid only) and truncation are kept.

    Args:
      None.
    Returns:
      None.
    """
    pool = json.dumps({"members": [{"vmid": 702, "type": "qemu", "status": "running"}]})

    def answer(cmd, stdin):
      """Pool listing, then guest-agent JSON by section.

      Args:
        cmd: argv; stdin: ignored.
      Returns:
        (rc, output).
      """
      line = cmd[-1]
      if "pvesh get /pools" in line:
        return 0, pool
      if "PRETTY_NAME" in line:
        return 0, json.dumps({"exitcode": 0, "exited": 1, "out-data": "Ubuntu 24.04\n"})
      if "sshd -T" in line:
        return 0, json.dumps({"pid": 4242})
      if "ss -tulnH" in line:
        return 0, json.dumps({"exitcode": 0, "exited": 1, "out-data": "tcp 0.0.0.0:22\n", "out-truncated": 1})
      if "qm guest exec" in line:
        return 0, json.dumps({"exitcode": 2, "exited": 1, "out-data": ""})
      return 0, "x\n"

    run, seen = recorder(answer)
    files, failed = ab.capture({}, [{"name": "pool", "type": "pve-pool", "ssh": "local", "pool": "p", "inside": "agent", "agent_timeout": 20}], run)
    text = files["pool/qemu-702.txt"]
    self.assertIn("== os\nUbuntu 24.04\n", text)
    self.assertIn("== ssh (rc 124)\nguest agent did not finish within 20 s", text)
    self.assertIn("[output truncated by the guest agent]", text)
    self.assertIn("== fstab (rc 2)", text)
    self.assertEqual(failed, ["pool"])
    execs = [cmd[-1] for cmd, _ in seen if "qm guest exec" in cmd[-1]]
    self.assertTrue(execs and all(c.startswith("qm guest exec 702 --timeout 20 -- bash -c ") for c in execs))
    self.assertFalse(any(cmd[0] == "ssh" for cmd, _ in seen))

  def test_pve_tenants(self):
    """pve-tenants runs the node script locally and writes tenants/<pool>.txt and summary.txt from review(); an empty read fails and writes nothing.

    Args:
      None.
    Returns:
      None.
    """
    res = [{"vmid": 701, "type": "qemu", "status": "running", "pool": "demo", "maxmem": 2 * 1024**3, "maxcpu": 1}]
    conf = {"name": "web", "protection": 1, "scsi0": "local-zfs:vm-701-disk-0,size=16G", "ipconfig0": "ip=10.0.0.21/24"}
    node = "== resources\n" + json.dumps(res) + "\n== config qemu/701\n" + json.dumps(conf) + "\n"
    with tempfile.TemporaryDirectory() as d:
      (Path(d) / "tenants.conf").write_text("demo|700|719|demo-project\n")
      (Path(d) / "budgets.conf").write_text("demo|4096|2\n")
      t = {"name": "tenants", "type": "pve-tenants", "registry": str(Path(d) / "tenants.conf"), "budgets": str(Path(d) / "budgets.conf")}
      run, seen = recorder(lambda cmd, stdin: (0, node))
      files, failed = ab.capture({}, [t], run)
      self.assertEqual(failed, [])
      self.assertEqual(sorted(files), ["tenants/demo.txt", "tenants/summary.txt"])
      self.assertEqual(seen[0][0], ["bash", "-s"])
      self.assertEqual(seen[0][1], ab.probes.tenants.node_script())
      direct = ab.probes.tenants.review(node, Path(d), 0, Path(d) / "tenants.conf", Path(d) / "budgets.conf")
      self.assertEqual(files["tenants/demo.txt"], direct["tenants/demo.txt"])
      self.assertIn("budget: 2048 MiB / 1 vCPUs allocated of 4096 MiB / 2 vCPUs (ok)", files["tenants/demo.txt"])
      lxc = {"hostname": "ct", "protection": 1}
      node_lxc = node.replace('"type": "qemu"', '"type": "lxc"').replace("config qemu/701", "config lxc/701").replace(json.dumps(conf), json.dumps(lxc))
      run3, _ = recorder(lambda cmd, stdin: (0, node_lxc))
      kept = ab.capture({}, [t], run3)[0]["tenants/demo.txt"]
      self.assertIn("== lxc 701 \n", kept, "trailing space of a nameless guest's header is kept (byte-identical to me/nas files)")
      self.assertEqual(kept, ab.probes.tenants.review(node_lxc, Path(d), 0, Path(d) / "tenants.conf", Path(d) / "budgets.conf")["tenants/demo.txt"])
      run2, _ = recorder(lambda cmd, stdin: (0, ""))
      files2, failed2 = ab.capture({}, [t], run2)
      self.assertEqual(failed2, ["tenants"])
      self.assertFalse(any(k.startswith("tenants/") for k in files2))


if __name__ == "__main__":
  unittest.main()
