"""Offline tests for pad_export.py: rendering by collection, cell cleaning, and the stamp-blind change check. Run: python3 -m unittest test_pad_export."""

import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_export", Path(__file__).resolve().parents[1] / "scripts" / "pad_export.py")
pe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pe)

ITEMS = [
    {"ref": "TASK-1", "title": "Apply N01 | narrowing", "collection_slug": "tasks", "fields": '{"status": "open", "priority": "high"}',
     "content_preview": "bug tracker N01\nsecond line", "updated_at": "2026-11-10T01:00:00Z"},
    {"ref": "TASK-2", "title": "Older", "collection_slug": "tasks", "fields": {"status": "done"}, "updated_at": "2026-11-09T01:00:00Z"},
    {"ref": "CONVE-1", "title": "Conventional commits", "collection_slug": "conventions", "fields": {}, "updated_at": "2026-11-10T00:00:00Z"},
]


class Render(unittest.TestCase):
    """render() groups, orders and cleans."""

    def test_groups_skip_and_order(self):
        """Conventions are skipped; tasks are newest first; pipes and second lines are cleaned out.

        Returns:
            None.
        """
        page = pe.render(ITEMS, "ws", "2026-11-10 12:00", {"conventions"})
        self.assertNotIn("CONVE-1", page)
        self.assertLess(page.index("TASK-1"), page.index("TASK-2"))
        self.assertIn("| TASK-1 | Apply N01 / narrowing | open | high | 2026-11-10 | bug tracker N01 |", page)
        self.assertIn("2 item(s) in 1 collection(s)", page)

    def test_change_check_ignores_the_stamp(self):
        """The same items rendered at another time are not a change; a changed item is.

        Returns:
            None.
        """
        a = pe.render(ITEMS, "ws", "2026-11-10 12:00", set())
        b = pe.render(ITEMS, "ws", "2026-11-11 08:30", set())
        self.assertFalse(pe.changed(a, b))
        self.assertTrue(pe.changed(a, pe.render(ITEMS[:1], "ws", "2026-11-11 08:30", set())))
        self.assertTrue(pe.changed(None, a))


if __name__ == "__main__":
    unittest.main()
