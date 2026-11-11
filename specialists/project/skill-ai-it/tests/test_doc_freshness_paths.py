"""Offline tests for doc_freshness's dependency rule: a commit that only rewrites link targets or backticked paths is not a change to review,
and a content change still is (2026-11-11). Uses a temporary git repository with dated commits. Run: just test."""

import datetime as dt
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "checks"
sys.path.insert(0, str(SCRIPTS))  # doc_freshness imports file_headers beside it
_spec = importlib.util.spec_from_file_location("doc_freshness", SCRIPTS / "doc_freshness.py")
df = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(df)


class PathOnly(unittest.TestCase):
  """path_only_change() tells a moved link from an edited sentence."""

  def test_link_target_moved(self):
    self.assertTrue(df.path_only_change(["See [x](../history/a.md#s)."], ["See [x](../history/changelog/a.md#s)."]))

  def test_backticked_path_moved(self):
    self.assertTrue(df.path_only_change(["now in `docs/history/a.md`: done"], ["now in `docs/history/changelog/a.md`: done"]))

  def test_words_changed(self):
    self.assertFalse(df.path_only_change(["T6 passed"], ["T6 failed"]))

  def test_link_text_changed(self):
    self.assertFalse(df.path_only_change(["See [old name](a.md)."], ["See [new name](a.md)."]))

  def test_empty_diff_is_not_path_only(self):
    self.assertFalse(df.path_only_change([], []))


def commit(repo: Path, text: str, day: str) -> None:
  """Write register.md and commit it on a given day.

  Args:
    repo: the repository.
    text: the file's new content.
    day: YYYY-MM-DD for the author and committer dates.
  """
  (repo / "register.md").write_text(text, encoding="utf-8")
  env = {**os.environ, "GIT_AUTHOR_DATE": f"{day}T12:00:00", "GIT_COMMITTER_DATE": f"{day}T12:00:00"}
  subprocess.run(["git", "-C", str(repo), "add", "register.md"], check=True, timeout=30)
  subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", day], check=True, timeout=30, env=env)


class ContentChangeDate(unittest.TestCase):
  """content_change_date() skips path-only commits and stops at the first content change."""

  def setUp(self):
    self.repo = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q", str(self.repo)], check=True, timeout=30)
    subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "t@example.invalid"], check=True, timeout=30)
    subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "test"], check=True, timeout=30)
    commit(self.repo, "Decision A. See [log](../history/a.md).\n", "2026-11-01")

  def test_path_only_commit_is_skipped(self):
    commit(self.repo, "Decision A. See [log](../history/changelog/a.md).\n", "2026-11-11")
    self.assertEqual(df.content_change_date(self.repo, "register.md"), dt.date(2026, 11, 1))

  def test_content_commit_counts(self):
    commit(self.repo, "Decision B. See [log](../history/a.md).\n", "2026-11-11")
    self.assertEqual(df.content_change_date(self.repo, "register.md"), dt.date(2026, 11, 11))


if __name__ == "__main__":
  unittest.main()
