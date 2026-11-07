"""Offline tests for private_commit.py: a temporary git repo where another session has staged a file. Run: just test (in skill-slurp-chat)."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "private_commit.py"


def sh(repo: Path, *args: str) -> str:
  """Run git in the repo.

  Args:
    repo: the repository.
    *args: git arguments.

  Returns:
    Stripped stdout.
  """
  return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, timeout=30, text=True).stdout.strip()


class PrivateCommit(unittest.TestCase):
  """Only the named paths are committed; the other session's staged file stays staged."""

  def setUp(self):
    """A repo with one commit, my edit and a peer's staged file."""
    self._tmp = tempfile.TemporaryDirectory()
    self.repo = Path(self._tmp.name)
    sh(self.repo, "init", "-q", "-b", "main")
    sh(self.repo, "config", "user.email", "t@example.com")
    sh(self.repo, "config", "user.name", "t")
    (self.repo / "mine.txt").write_text("one\n")
    (self.repo / "peer.txt").write_text("one\n")
    sh(self.repo, "add", ".")
    sh(self.repo, "commit", "-q", "-m", "base")
    (self.repo / "mine.txt").write_text("two\n")
    (self.repo / "peer.txt").write_text("peer edit\n")
    sh(self.repo, "add", "peer.txt")
    self.msg = self.repo.parent / f"{self.repo.name}-msg.txt"
    self.msg.write_text("mine only\n")

  def tearDown(self):
    """Remove the repo."""
    self._tmp.cleanup()
    self.msg.unlink(missing_ok=True)

  def run_tool(self, *args: str) -> subprocess.CompletedProcess:
    """Run the script.

    Args:
      *args: script arguments.

    Returns:
      The completed process.
    """
    cmd = [sys.executable, str(SCRIPT), "--repo", str(self.repo), "--message-file", str(self.msg), *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)

  def test_dry_run_writes_nothing(self):
    """Without --apply HEAD stays put."""
    head = sh(self.repo, "rev-parse", "HEAD")
    self.assertEqual(self.run_tool("mine.txt").returncode, 0)
    self.assertEqual(sh(self.repo, "rev-parse", "HEAD"), head)

  def test_commits_named_path_and_leaves_peer_staged(self):
    """The commit holds mine.txt only; peer.txt is still staged, not committed."""
    out = self.run_tool("mine.txt", "--apply")
    self.assertEqual(out.returncode, 0, out.stderr)
    self.assertEqual(sh(self.repo, "show", "--name-only", "--format=", "HEAD"), "mine.txt")
    self.assertEqual(sh(self.repo, "show", "HEAD:peer.txt"), "one")
    self.assertEqual(sh(self.repo, "diff", "--cached", "--name-only"), "peer.txt")
    self.assertEqual(sh(self.repo, "status", "--short", "--", "mine.txt"), "")


if __name__ == "__main__":
  unittest.main()
