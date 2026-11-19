"""Offline tests for scripts/records/rotate_records.py: rotation never loses a content line, keeps prose under Contents, pins open items."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "records" / "rotate_records.py"
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


class GroupKeyTest(unittest.TestCase):
    """Dated sections of one kind form one group whatever time marker follows the date."""

    def test_time_suffixes_do_not_split_a_group(self):
        heads = ["## Residual risk register (staleness audit, 2026-09-14 ~1:35p)", "## Residual risk register (staleness audit, 2026-09-15 ~10:53a)",
                 "## Residual risk register (staleness audit, 2026-09-20 ~12:11)", "## Residual risk — staleness audit 20261009_1816 `KEEP`"]
        keys = {rr.group_key("state", h) for h in heads[:3]}
        self.assertEqual(len(keys), 1, keys)
        self.assertEqual(rr.group_key("state", heads[3]), "Residual risk — staleness audit")

    def test_written_dates_in_headings_date_and_group(self):
        a = "## Residual risk register — staleness audit, 21 September 2026 `KEEP`"
        b = "## Residual risk register — staleness audit, 25 August 2026 `KEEP`"
        self.assertEqual(rr.heading_stamp(a), "2026-09-21")
        self.assertEqual(rr.group_key("state", a), rr.group_key("state", b))
        rec = rr.parse("# S\n\n## Current state\n\n- contemporaneous note created 10 Jul 2026\n", "state")
        units = [u for _, items in rec.blocks for u in items if isinstance(u, rr.Unit)]
        self.assertEqual([u.stamp for u in units], [""])  # a written date in prose does not date a bullet


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
            archives = "".join(p.read_text() for p in sorted((root / "docs" / "history").rglob("*.md")) if p.name != "readme.md")  # by-kind layout
            return (root / name).read_text(), archives

    def test_no_content_line_is_lost_and_prose_under_contents_stays(self):
        original = scratchpad(120)
        live, archive = self.rotate("SCRATCHPAD.md", original)
        self.assertIn("Phase notes that are not navigation and must survive", live)
        before = Counter(l for l in rr.content_lines(original) if l.strip())
        after = Counter(l for l in rr.content_lines(live) if l.strip()) + Counter(l for l in archive.split("\n") if l.strip())
        missing = [l for l in before if after[l] < 1 and after[rr.relink([l], "", "docs/history/scratchpad")[0]] < 1]
        self.assertEqual(missing, [])
        self.assertLessEqual(live.count("\n"), 220)

    def test_a_second_rotation_in_the_same_minute_keeps_the_first_archive(self):
        """2026-11-19, skill-drawio and skill-nautobot: two rotations in one minute wrote the same archive name and the second erased the first."""
        import datetime as dt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "SCRATCHPAD.md").write_text(scratchpad(120))
            arc = root / "docs" / "history" / "scratchpad"
            arc.mkdir(parents=True)
            now = dt.datetime.now()
            earlier = [arc / f"scratchpad-{(now + dt.timedelta(minutes=m)).strftime('%Y%m%d_%H%M')}.md" for m in (0, 1)]
            for path in earlier:
                path.write_text("SENTINEL from an earlier rotation\n")
            subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root), "--apply", "SCRATCHPAD.md"], check=True, capture_output=True)
            self.assertEqual([p.read_text() for p in earlier], ["SENTINEL from an earlier rotation\n"] * 2)
            self.assertGreater(len(list(arc.glob("scratchpad-*.md"))), 2)

    def test_archive_has_no_blank_line_runs(self):
        """Units that end with blank lines must not leave double blanks or a blank last line in the archive (MD012, 2026-11-18)."""
        lines = ["# Scratchpad", "", "## Current state", ""]
        for i in range(60):
            lines += [f"### 2026-0{1 + i % 8}-1{i % 10} — thread {i}", "", f"paragraph {i}", "", "", ""]
        _live, archive = self.rotate("SCRATCHPAD.md", "\n".join(lines) + "\n")
        self.assertNotIn("\n\n\n", archive)
        self.assertIn("\nAuthority: record\n", archive)
        self.assertIn("\nScope: Entries rotated out of SCRATCHPAD.md, verbatim\n", archive)
        self.assertTrue(archive.endswith("\n") and not archive.endswith("\n\n"))

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

    def test_the_unreleased_section_never_rotates(self):
        """A CHANGELOG's `## Unreleased` stays live even when git blame dates its heading oldest; dated entries rotate instead (2026-11-17)."""
        lines = ["# Changelog", "", "## Unreleased", ""]
        lines += [f"- unreleased note {i} " + "x" * 120 for i in range(120)]
        for i in range(40):
            lines += ["", f"## 2026010{1 + i % 9}_12{i:02d} — entry {i}", "", f"- old entry body {i} " + "y" * 120]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {**os.environ, "GIT_AUTHOR_DATE": "2025-01-01T00:00:00", "GIT_COMMITTER_DATE": "2025-01-01T00:00:00"}
            git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "CHANGELOG.md").write_text("\n".join(lines) + "\n")
            subprocess.run([*git, "add", "CHANGELOG.md"], cwd=root, check=True)
            subprocess.run([*git, "commit", "-qm", "old"], cwd=root, check=True, env=env)
            subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root), "--apply", "CHANGELOG.md"], check=True, capture_output=True)
            live = (root / "CHANGELOG.md").read_text()
        self.assertIn("## Unreleased", live)
        self.assertIn("unreleased note 0 ", live)

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

    def test_the_tracker_pointer_is_written_once(self):
        text = scratchpad(20).replace("# Scratchpad\n", "---\nTitle: Scratchpad\nOpen items tracker: docs/trackers/open-items.md\n---\n# Scratchpad\n", 1)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            for extra in ("- [ ] **20260902_0900** first old item", "- [ ] **20260903_0900** second old item"):
                body = (root / "SCRATCHPAD.md").read_text() if (root / "SCRATCHPAD.md").exists() else text
                body = body.replace("## Open items\n\n", "## Open items\n\n" + extra + "\n" + "".join(
                    f"- [ ] **2026091{k}_0900** newer {k}\n" for k in range(4)), 1)
                (root / "SCRATCHPAD.md").write_text(body)
                subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root), "--apply", "SCRATCHPAD.md"], check=True, capture_output=True)
            live = (root / "SCRATCHPAD.md").read_text()
        self.assertEqual(live.count("Older open items are tracked in"), 1)

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

    def test_a_tracker_value_that_is_not_a_markdown_path_is_ignored(self):
        """skill-coder, 2026-11-07: `Open items tracker: this file, Open items` made a file named `this` at the root and linked it from the live file."""
        text = scratchpad(20).replace("# Scratchpad\n", "---\nTitle: Scratchpad\nOpen items tracker: this file, Open items\n---\n# Scratchpad\n", 1)
        text = text.replace("- [ ] **20260901_0900** still open, never rotated", "- [ ] **20260901_0900** still open\n- [ ] **20260905_0900** a\n- [ ] **20260906_0900** b\n- [ ] **20260907_0900** c")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "SCRATCHPAD.md").write_text(text)
            run = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root), "--apply", "SCRATCHPAD.md"], check=True, capture_output=True, text=True)
            live = (root / "SCRATCHPAD.md").read_text()
            made = sorted(p.name for p in root.iterdir())
        self.assertNotIn("this", made)
        self.assertIn("still open", live)
        self.assertNotIn("Older open items are tracked in", live)
        self.assertIn("not a markdown path", run.stdout + run.stderr)

    def test_project_sync_blocks_never_move(self):
        """Outbox and inbox lines between project-sync markers stay put however old (smc-resiliency, 2026-10-20: an unsent outbox line and an
        unanswered inbox item were moved to the tracker, so the sync never sent the one and reported 0 open for the other)."""
        text = scratchpad(20).replace("# Scratchpad\n", "---\nTitle: Scratchpad\nOpen items tracker: docs/trackers/open-items.md\n---\n# Scratchpad\n", 1)
        sync = ("<!-- project-sync:outbox:start -->\n- [ ] to unc: unsent outbox line\n  second line\n<!-- project-sync:outbox:end -->\n"
                "<!-- project-sync:inbox:start -->\n- [ ] **20260901_0700** from es: unanswered inbox item <!--sync-id:es-1-->\n"
                "<!-- project-sync:inbox:end -->\n")
        text = text.replace("- [ ] **20260901_0900** still open, never rotated", "- [ ] **20260901_0900** still open\n- [ ] **20260905_0900** a\n"
                            "- [ ] **20260906_0900** b\n- [ ] **20260907_0900** c\n" + sync.rstrip("\n"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "SCRATCHPAD.md").write_text(text)
            subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(root), "--apply", "SCRATCHPAD.md"], check=True, capture_output=True)
            live = (root / "SCRATCHPAD.md").read_text()
            tracker = (root / "docs/trackers/open-items.md").read_text()
        self.assertIn("still open", tracker)
        for line in ("unsent outbox line", "second line", "unanswered inbox item"):
            self.assertIn(line, live)
            self.assertNotIn(line, tracker)
        self.assertIn(sync, live)


if __name__ == "__main__":
    unittest.main()
