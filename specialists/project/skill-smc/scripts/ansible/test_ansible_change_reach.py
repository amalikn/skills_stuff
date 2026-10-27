"""Offline test for ansible_change_reach.py. Run: python3 -m unittest test_ansible_change_reach -v (from scripts/).

Safety: a throwaway git repo in a temporary directory; no ansible-wifi, no network.
"""

import contextlib
import io
import runpy
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

MODULE = runpy.run_path(str(Path(__file__).resolve().parent / "ansible_change_reach.py"))

GRAPH = """@smc_ltp:
  |--@guda-guda_smc_ltp:
  |  |--guda-guda-smc01
  |--@old-looma_smc_ltp:
  |  |--old-looma-smc01
  |--old-looma-smc01
"""


def git(repo, *args):
  """Run git in the test repo.

  Args:
    repo: the repo directory.
    *args: git arguments.

  Returns:
    stdout, stripped.
  """
  env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "HOME": repo, "PATH": "/usr/bin:/bin:/opt/homebrew/bin:/usr/local/bin"}
  return subprocess.run(["git", *args], cwd=repo, env=env, capture_output=True, text=True, check=True, timeout=30).stdout.strip()


class ReachTests(unittest.TestCase):
  """Assert reach, cherry-pick simulation and exit codes against a real git repo."""

  def setUp(self):
    """Build: base branch `rise` with one commit, side branch `side` with one more that adds a host.

    Returns:
      None.
    """
    self.tmp = TemporaryDirectory()
    self.repo = self.tmp.name
    git(self.repo, "init", "-q", "-b", "rise")
    Path(self.repo, "prod").write_text("[smc_ltp]\nguda-guda-smc01\n")
    git(self.repo, "add", "prod")
    git(self.repo, "commit", "-q", "-m", "base")
    self.base_commit = git(self.repo, "rev-parse", "--short", "HEAD")
    git(self.repo, "checkout", "-q", "-b", "side")
    Path(self.repo, "prod").write_text("[smc_ltp]\nguda-guda-smc01\numoona-smc01\n")
    git(self.repo, "commit", "-q", "-am", "add umoona")
    self.side_commit = git(self.repo, "rev-parse", "--short", "HEAD")
    git(self.repo, "checkout", "-q", "rise")

  def tearDown(self):
    """Remove the temporary repo.

    Returns:
      None.
    """
    self.tmp.cleanup()

  def test_side_commit_not_on_base(self):
    """A side-branch commit is off the base, lists its branch, and would cherry-pick clean.

    Returns:
      None.
    """
    info = MODULE["reach"](self.repo, self.side_commit, "rise")
    self.assertTrue(info["found"])
    self.assertFalse(info["on_base"])
    self.assertIsNone(info["on_origin_base"])
    self.assertEqual(info["branches"], ["side"])
    self.assertEqual(info["cherry_pick"], "clean")

  def test_conflict_detected(self):
    """A base commit that rewrites the same line makes the cherry-pick a conflict.

    Returns:
      None.
    """
    Path(self.repo, "prod").write_text("[smc_ltp]\nother-smc01\n")
    git(self.repo, "commit", "-q", "-am", "rewrite")
    self.assertEqual(MODULE["reach"](self.repo, self.side_commit, "rise")["cherry_pick"], "conflict")

  def test_exit_codes(self):
    """Exit 0 when every commit is on base, 1 when one is not or is unknown.

    Returns:
      None.
    """
    with contextlib.redirect_stdout(io.StringIO()) as out:
      self.assertEqual(MODULE["main"](["--repo", self.repo, "--base", "rise", self.base_commit]), 0)
      self.assertEqual(MODULE["main"](["--repo", self.repo, "--base", "rise", self.side_commit]), 1)
      self.assertEqual(MODULE["main"](["--repo", self.repo, "--base", "rise", "deadbeef"]), 1)
    self.assertIn("cherry-pick onto rise: clean", out.getvalue())
    self.assertIn("deadbeef: not found", out.getvalue())

  def test_group_refused_off_base(self):
    """The group graph is not read when HEAD is not the base branch.

    Returns:
      None.
    """
    git(self.repo, "checkout", "-q", "side")
    hosts, reason = MODULE["group_members"](self.repo, "rise", "prod", "smc_ltp")
    self.assertIsNone(hosts)
    self.assertIn("HEAD is side", reason)

  def test_graph_hosts(self):
    """Group lines are skipped and repeated hosts listed once.

    Returns:
      None.
    """
    self.assertEqual(MODULE["graph_hosts"](GRAPH), ["guda-guda-smc01", "old-looma-smc01"])


if __name__ == "__main__":
  unittest.main()
