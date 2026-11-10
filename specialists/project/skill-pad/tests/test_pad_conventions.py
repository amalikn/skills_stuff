"""Offline tests for scripts/pad_conventions.py: the baseline loads with placeholders filled, and the plan says same, update or create correctly."""

import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_conventions", Path(__file__).resolve().parents[1] / "scripts" / "pad_conventions.py")
pc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pc)


def item(ref, b, **over):
    """A workspace convention as `pad item list --format json --full` gives it, built from a baseline entry.

    Args:
        ref: the issue ID.
        b: a baseline entry.
        over: fields or keys to override.

    Returns:
        The item dict.
    """
    fields = {k: b[k] for k in pc.FIELDS if b.get(k)} | {"status": "active"} | ({"commands": b["commands"]} if b.get("commands") else {})
    return {"ref": ref, "seq": 1, "title": b["title"], "content": b["content"], "fields": {**fields, **over.pop("fields", {})}, **over}


class Baseline(unittest.TestCase):
    """load_baseline() and plan()."""

    def setUp(self):
        self.b = pc.load_baseline(pc.BASELINE, "proj-x", "ROADMAP")

    def test_seven_conventions_with_placeholders_filled(self):
        """Five entries; no placeholder left; the project name reaches the commit-message title.

        Returns:
            None.
        """
        self.assertEqual(len(self.b), 7)
        self.assertTrue(all("{" not in c["title"] + c["content"] for c in self.b))
        self.assertIn("'proj-x: <summary>'", next(c for c in self.b if c["id"] == "commit-message")["title"])

    def test_plan_same_update_create(self):
        """A matching workspace is all same; a template title is an update; an absent entry is a create.

        Returns:
            None.
        """
        existing = [item(f"CONVE-{n}", c) for n, c in enumerate(self.b, 1)]
        self.assertEqual({a for a, *_ in pc.plan(self.b, existing)}, {"same"})
        tmpl = dict(existing[0], title=self.b[0]["replaces"], content="old")
        actions = pc.plan(self.b, [tmpl] + existing[1:4])
        self.assertEqual([a for a, *_ in actions], ["update", "same", "same", "same", "create", "create", "create"])
        self.assertEqual(actions[0][3], ["title", "content"])

    def test_disabled_or_wrong_commands_is_an_update(self):
        """A disabled convention or the template's commands list is brought back in line.

        Returns:
            None.
        """
        just = next(c for c in self.b if c["id"] == "just-check")
        acts = pc.plan([just], [item("CONVE-3", just, fields={"status": "disabled", "commands": ["go test ./..."]})])
        self.assertEqual((acts[0][0], acts[0][3]), ("update", ["status", "commands"]))

    def test_only_selects_named_entries_and_refuses_unknown(self):
        """--only keeps the named entries in baseline order; an unknown id raises before anything is planned.

        Returns:
            None.
        """
        self.assertEqual([b["id"] for b in pc.select_entries(self.b, "writing-standard")], ["writing-standard"])
        self.assertEqual([b["id"] for b in pc.select_entries(self.b, "writing-standard, commit-message")], ["commit-message", "writing-standard"])
        self.assertEqual(len(pc.select_entries(self.b, None)), 7)
        with self.assertRaises(ValueError):
            pc.select_entries(self.b, "writing-standard,nope")


if __name__ == "__main__":
    unittest.main()
