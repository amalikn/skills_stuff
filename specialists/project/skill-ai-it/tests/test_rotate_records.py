"""Offline tests for scripts/rotate_records.py: rotation never loses a content line, keeps prose under Contents, pins open items."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "rotate_records.py"
_spec = importlib.util.spec_from_file_location("rotate_records", SCRIPT)
rr = importlib.util.module_from_spec(_spec)
sys.modules["rotate_records"] = rr
_spec.loader.exec_module(rr)


def scratchpad(n_old: int) -> str:
    """A SCRATCHPAD with prose under its Contents list, many old dated entries and one open item.

    Args:
        n_old: how many old dated Current-state entries to write.

    Returns:
        The file text.
    """
    lines = ["# Scratchpad", "", "## Contents", "", "- [Current state](#current-state)", "- [Open items](#open-items)", "",
             "Phase notes that are not navigation and must survive (vocus-profitability, 2026-10-10).", "Second prose line.", "",
             "## Current state", ""]
    for i in range(n_old):
        lines += [f"- **2026090{1 + i % 9}_1{i % 10}00** `KEEP`: entry {i} with a [link](docs/x.md)", f"  detail line {i}"]
    lines += ["", "## Open items", "", "- [ ] **20260901_0900** still open, never rotated", "- [x] **20260901_0800** finished item", ""]
    return "\n".join(lines) + "\n"


class RotateTest(unittest.TestCase):
    """Run the real script on a temporary git repository and check what moved."""

    def rotate(self, name: str, text: str) -> tuple[str, str]:
        """Rotate one record in a scratch repository.

        Args:
            name: the record's file name.
            text: its content.

        Returns:
            (the live file after rotation, the concatenated archives).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / name).write_text(text)
            subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root), "--apply", name], check=True, capture_output=True)
            archives = "".join(p.read_text() for p in sorted((root / "docs" / "history").glob("*.md")) if p.name != "readme.md")
            return (root / name).read_text(), archives

    def test_no_content_line_is_lost_and_prose_under_contents_stays(self):
        original = scratchpad(120)
        live, archive = self.rotate("SCRATCHPAD.md", original)
        self.assertIn("Phase notes that are not navigation and must survive", live)
        before = Counter(l for l in rr.content_lines(original) if l.strip())
        after = Counter(l for l in rr.content_lines(live) if l.strip()) + Counter(l for l in archive.split("\n") if l.strip())
        missing = [l for l in before if after[l] < 1 and after[rr.relink([l], "", "docs/history")[0]] < 1]
        self.assertEqual(missing, [])
        self.assertLessEqual(live.count("\n"), 220)

    def test_a_dated_prose_subsection_rotates_whole(self):
        """A `### <date>` subsection of paragraphs (no bullets) moves as one unit; the newest stay."""
        lines = ["# Scratchpad", "", "## Current state", ""]
        for i in range(60):
            lines += [f"### 2026-0{1 + i % 8}-1{i % 10} — thread {i}", "", f"**Thread {i} paragraph.** detail {i}", f"second paragraph {i}", ""]
        live, archive = self.rotate("SCRATCHPAD.md", "\n".join(lines) + "\n")
        self.assertIn("**Thread 0 paragraph.** detail 0", archive)
        self.assertIn("second paragraph 0", archive)
        self.assertNotIn("second paragraph 0\n", live)
        self.assertLessEqual(live.count("\n"), 220)

    def test_a_wrapped_item_moves_with_its_unindented_continuation(self):
        """Lines wrapped at column 0 under a dated item travel with it; none is left behind as an orphan paragraph."""
        lines = ["# Scratchpad", "", "## Next actions", ""]
        for i in range(80):
            lines += [f"1. **2026-0{1 + i % 8}-1{i % 10}** action {i} starts here and", f"continues unindented {i}", f"and ends {i}.", ""]
        live, archive = self.rotate("SCRATCHPAD.md", "\n".join(lines) + "\n")
        self.assertIn("action 0 starts here and\ncontinues unindented 0\nand ends 0.", archive)
        self.assertNotIn("continues unindented 0\n", live)

    def test_only_an_explicit_marker_pins(self):
        """A captive-portal "PIN" in content is not a pin; `PIN` in backticks is."""
        text = scratchpad(120).replace("entry 0 with", "entry 0 `PIN` with").replace("entry 1 with", "entry 1 portal/PIN-activation outage with")
        live, archive = self.rotate("SCRATCHPAD.md", text)
        self.assertIn("entry 0 `PIN` with", live)
        self.assertIn("entry 1 portal/PIN-activation outage with", archive)

    def test_open_item_stays_and_finished_item_may_move(self):
        live, _ = self.rotate("SCRATCHPAD.md", scratchpad(120))
        self.assertIn("still open, never rotated", live)

    def test_contents_mid_file_is_moved_to_the_top_not_counted_as_loss(self):
        entries = "\n".join(f"## 202609{10 + i:02d}_1200 — entry {i}\n\n- change {i}\n" + "  more\n" * 8 for i in range(20))
        text = "# Changelog\n\n## 20261010_1200 — newest\n\n- x\n\n## Contents\n\n- [old](#old)\n\n" + entries
        live, archive = self.rotate("CHANGELOG.md", text)
        self.assertIn("## Contents", live)
        self.assertLess(live.index("## Contents"), live.index("## 20261010_1200"))
        self.assertIn("entry 0", archive)


class TrackerTest(RotateTest):
    """Old open items move to the live tracker, not to history; recent ones stay; the pointer is left behind."""

    def test_old_open_items_go_to_the_tracker(self):
        text = scratchpad(20).replace("# Scratchpad\n", "---\nTitle: Scratchpad\nOpen items tracker: docs/trackers/open-items.md\n---\n# Scratchpad\n", 1)
        text = text.replace("- [ ] **20260901_0900** still open, never rotated", "- [ ] **20260901_0900** still open\n- [ ] undated open item\n- [ ] **20260905_0900** a\n- [ ] **20260906_0900** b\n- [ ] **20260907_0900** c")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "SCRATCHPAD.md").write_text(text)
            subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root), "--apply", "SCRATCHPAD.md"], check=True, capture_output=True)
            live = (root / "SCRATCHPAD.md").read_text()
            tracker = (root / "docs/trackers/open-items.md").read_text()
        self.assertIn("still open", tracker)
        self.assertIn("undated open item", tracker)
        self.assertNotIn("still open", live)
        self.assertIn("open-items.md", live)


if __name__ == "__main__":
    unittest.main()
