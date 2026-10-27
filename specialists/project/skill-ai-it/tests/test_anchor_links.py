"""scripts/checks/anchor_links.py: links to a missing heading are found, duplicates and HTML anchors count, verbatim folders are skipped. Offline."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("anchor_links", _ROOT / "scripts/checks/anchor_links.py")
al = importlib.util.module_from_spec(_spec)
sys.modules["anchor_links"] = al
_spec.loader.exec_module(al)


class Anchors(unittest.TestCase):
    """heading_anchors() and slug()."""

    def test_slug_matches_github(self):
        """Punctuation and tags drop, an em dash leaves a double hyphen, underscores stay."""
        self.assertEqual(al.slug("Step 1 — Unattended transport"), "step-1--unattended-transport")
        self.assertEqual(al.slug("20261022_1734 — Plan (links)"), "20261022_1734--plan-links")
        self.assertEqual(al.slug("Step N — <short name>"), "step-n-")

    def test_duplicates_html_anchors_and_fenced_code(self):
        """A repeat gets -1; <a id> counts; a heading inside a fence does not."""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "a.md"
            p.write_text('# Notes\n\n## Notes\n\n<a id="here"></a>\n\n```\n# not a heading\n```\n', encoding="utf-8")
            self.assertEqual(al.heading_anchors(p), {"notes", "notes-1", "here"})


class BrokenLinks(unittest.TestCase):
    """broken_links()."""

    def test_finds_broken_and_skips_verbatim(self):
        """A missing heading is reported; same-page, good and non-markdown links pass; skipped paths are not read."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs/history").mkdir(parents=True)
            (root / "docs/x-sources-1").mkdir()
            (root / "b.md").write_text("# Real\n", encoding="utf-8")
            (root / "a.md").write_text("# Top\n[ok](b.md#real) [self](#top) [bad](b.md#gone) [yaml](c.yaml#k) [none](n.md#x)\n", encoding="utf-8")
            for rel in ("docs/history/old.md", "docs/x-sources-1/cap.md", "prompt-ask.md"):
                (root / rel).write_text("[bad](../b.md#gone)\n", encoding="utf-8")
            checked, broken, outside = al.broken_links(root, ("docs/history/",), ("prompt-*.md",))
            self.assertEqual(outside, [])
            self.assertEqual(checked, 3)
            self.assertEqual(len(broken), 1)
            self.assertIn("a.md links `b.md#gone`", broken[0])

    def test_check_exit_code(self):
        """--check exits 1 on a broken anchor; without it, 0."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.md").write_text("[bad](#gone)\n", encoding="utf-8")
            self.assertEqual(al.main(["--project-root", tmp]), 0)
            self.assertEqual(al.main(["--project-root", tmp, "--check"]), 1)

    def test_outside_links_warn_only_when_asked(self):
        """A broken link into a file outside the root fails by default and only warns with --outside warn."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            root.mkdir()
            (Path(tmp) / "other.md").write_text("# Renamed\n", encoding="utf-8")
            (root / "a.md").write_text("[x](../other.md#old)\n", encoding="utf-8")
            _, broken, outside = al.broken_links(root)
            self.assertEqual((broken, len(outside)), ([], 1))
            self.assertEqual(al.main(["--project-root", str(root), "--check"]), 1)
            self.assertEqual(al.main(["--project-root", str(root), "--check", "--outside", "warn"]), 0)


if __name__ == "__main__":
    unittest.main()
