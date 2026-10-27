"""Tests for scripts/plans/target_map.py: the schema levels (mandatory, recommended, optional, rejected), every validator rule, both
definition modes (a source document, or inline), the source parser and the renderer's determinism. Offline, in a temporary
folder per test; nothing in the project tree is read or written.
"""

from __future__ import annotations

import contextlib
import copy
import datetime as dt
import importlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "plans"))

tm = importlib.import_module("target_map")

PLAN = """# Plan

## Phase A — First thing

### Exit condition

> Proceed when the first thing works.

### Acceptance test

Given a lab:

1. the widget starts;
2. the widget stops and
   reports why.

## Phase B — Second thing

### Exit condition

> Proceed when the second thing works.

### Acceptance test

1. it works.
"""

ROADMAP = """# Roadmap

- [ ] **Phase A (first thing), under way.** Details.
- [ ] Something unrelated.
"""

TODAY = dt.date(2026, 9, 27)


def base_map() -> dict:
    """A valid source-based map: target A started with evidence, target B not started."""
    return {
        "schema": 1,
        "title": "Test tracker",
        "render_to": "docs/tracker.md",
        "updated": "2026-09-27",
        "roadmap_file": "ROADMAP.md",
        "labels": {"target": "Phase", "section": "Per phase"},
        "sources": [{"id": "plan", "label": "the plan", "path": "plan.md", "target_heading": r"^## Phase (?P<id>\w+) — (?P<name>.+)$",
                     "exit_section": "Exit condition", "criteria_section": "Acceptance test"}],
        "current_state": {"intro": "Now.", "diagram": "a --> b"},
        "goals": [{"id": "G1", "name": "Goal", "statement": "Why."}],
        "targets": [
            {"id": "A", "source": "plan", "goal": "G1", "state": "in progress", "exit_met": False, "mention": "Phase A",
             "summary": "Going.", "blocker": {"owner": "operator", "text": "hardware"},
             "next": {"owner": "agent", "text": "test it"},
             "evidence": [{"label": "notes", "path": "notes.md"}],
             "as_built": {"intro": "Built.", "diagram": "x"},
             "criteria": [{"n": 1, "status": "pass", "verified": "2026-09-26", "evidence": [{"path": "notes.md"}]},
                          {"n": 2, "status": "not run"}]},
            {"id": "B", "source": "plan", "goal": "G1", "state": "not started", "exit_met": False, "mention": "Phase B",
             "summary": "Later.", "blocker": {"owner": "none", "text": "A first"},
             "criteria": [{"n": 1, "status": "not run"}]},
        ],
    }


class Workspace:
    """A temporary project root holding a map, its plan, a roadmap and one evidence file."""

    def __init__(self, raw: dict, plan: str = PLAN, roadmap: str = ROADMAP, extra: dict[str, str] | None = None) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "plan.md").write_text(plan, encoding="utf-8")
        for name, text in (extra or {}).items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text, encoding="utf-8")
        (self.root / "ROADMAP.md").write_text(roadmap, encoding="utf-8")
        (self.root / "notes.md").write_text("evidence", encoding="utf-8")
        (self.root / "docs").mkdir(exist_ok=True)
        (self.root / tm.MAP_FILE).write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def evaluate(self) -> tm.Outcome:
        return tm.evaluate(self.root, TODAY)

    def close(self) -> None:
        self.tmp.cleanup()


class TargetMapCase(unittest.TestCase):
    def outcome(self, raw: dict, **kw) -> tm.Outcome:
        ws = Workspace(raw, **kw)
        self.addCleanup(ws.close)
        return ws.evaluate()

    def assertProblem(self, raw: dict, fragment: str, **kw) -> None:
        problems = self.outcome(raw, **kw).problems
        self.assertTrue(any(fragment in p for p in problems), f"no problem containing {fragment!r} in {problems}")


class SchemaTableTest(unittest.TestCase):
    def test_every_field_has_a_level_and_a_reason(self):
        for kind, spec in tm.SCHEMA.items():
            for key, f in spec.items():
                self.assertIn(f.level.split(" when ")[0].split(" unless ")[0], tm.LEVELS, f"{kind}.{key}")
                self.assertTrue(f.reason.strip(), f"{kind}.{key} has no reason")

    def test_schema_markdown_lists_levels_and_reasons(self):
        text = tm.schema_markdown()
        self.assertIn("| Field | Level | Meaning | Reason |", text)
        self.assertIn("rejected", text)


class SchemaCheckTest(TargetMapCase):
    def test_valid_map_has_no_problems(self):
        self.assertEqual(self.outcome(base_map()).problems, [])

    def test_missing_mandatory_field_fails(self):
        raw = base_map()
        del raw["title"]
        self.assertProblem(raw, "mandatory field `title` is missing")

    def test_missing_recommended_field_warns_but_passes(self):
        raw = base_map()
        del raw["targets"][0]["summary"]
        out = self.outcome(raw)
        self.assertEqual(out.problems, [])
        self.assertTrue(any("recommended field `summary`" in w for w in out.warnings))

    def test_missing_optional_field_is_silent(self):
        raw = base_map()
        del raw["labels"]
        out = self.outcome(raw)
        self.assertEqual(out.problems, [])
        self.assertFalse(any("labels" in w for w in out.warnings))

    def test_rejected_field_fails_with_its_reason(self):
        raw = base_map()
        raw["targets"][0]["percent_complete"] = 40
        self.assertProblem(raw, "field `percent_complete` is rejected: a percentage invites guessing")

    def test_unknown_field_fails(self):
        raw = base_map()
        raw["targets"][0]["colour"] = "red"
        self.assertProblem(raw, "unknown field `colour`")


class ValidatorTest(TargetMapCase):
    def test_exit_met_must_agree_with_state(self):
        raw = base_map()
        raw["targets"][0]["exit_met"] = True
        self.assertProblem(raw, "exit_met true disagrees with state `in progress`")

    def test_state_outside_vocabulary(self):
        raw = base_map()
        raw["targets"][0]["state"] = "nearly"
        self.assertProblem(raw, "state `nearly` is outside the vocabulary")

    def test_pass_needs_evidence_and_verified(self):
        raw = base_map()
        raw["targets"][0]["criteria"][0] = {"n": 1, "status": "pass"}
        self.assertProblem(raw, "evidence is mandatory when `pass`")
        self.assertProblem(raw, "verified is mandatory when `pass`")

    def test_partly_needs_a_note(self):
        raw = base_map()
        raw["targets"][0]["criteria"][0]["status"] = "partly"
        self.assertProblem(raw, "note is mandatory when `partly`")

    def test_stale_pending_fails(self):
        raw = base_map()
        raw["targets"][0]["criteria"][0].update(status="pending", verified="2026-09-01")
        self.assertProblem(raw, "re-check it")

    def test_criteria_must_match_the_source(self):
        raw = base_map()
        raw["targets"][0]["criteria"].pop()
        self.assertProblem(raw, "criteria [1] differ from the source's [1, 2]")

    def test_every_source_heading_needs_a_target(self):
        raw = base_map()
        raw["targets"].pop()
        self.assertProblem(raw, "source plan defines `B` but no target tracks it")

    def test_single_source_key_is_rejected(self):
        raw = base_map()
        raw["source"] = raw["sources"][0]
        self.assertProblem(raw, "field `source` is rejected: replaced by `sources`")

    def test_definitions_are_not_restated_when_a_source_is_set(self):
        raw = base_map()
        raw["targets"][0]["name"] = "Restated"
        self.assertProblem(raw, "come from source plan; do not restate them")

    def test_evidence_path_must_exist(self):
        raw = base_map()
        raw["targets"][0]["evidence"] = [{"path": "missing.md"}]
        self.assertProblem(raw, "evidence path `missing.md` does not exist")

    def test_evidence_needs_exactly_one_of_path_or_ref(self):
        raw = base_map()
        raw["targets"][0]["evidence"] = [{"path": "notes.md", "ref": "also"}]
        self.assertProblem(raw, "exactly one of `path` or `ref`")

    def test_started_target_needs_a_roadmap_line(self):
        self.assertProblem(base_map(), "no task line in ROADMAP.md", roadmap="# Roadmap\n")

    def test_ticked_roadmap_line_needs_done(self):
        self.assertProblem(base_map(), "ticks a line naming `Phase A`", roadmap="- [x] **Phase A done.**\n")

    def test_goal_without_target_fails(self):
        raw = base_map()
        raw["goals"].append({"id": "G2", "name": "Orphan", "statement": "Nothing serves it."})
        self.assertProblem(raw, "goal G2 has no target")


class InlineModeTest(TargetMapCase):
    def inline_map(self) -> dict:
        raw = base_map()
        del raw["sources"]
        del raw["roadmap_file"]
        for t in raw["targets"]:
            del t["source"]
            t["name"] = f"Thing {t['id']}"
            t["exit_condition"] = "It works."
            for c in t["criteria"]:
                c["text"] = f"criterion {c['n']};"
        return raw

    def test_inline_map_is_valid_and_renders_its_text(self):
        out = self.outcome(self.inline_map())
        self.assertEqual(out.problems, [])
        self.assertIn("### Phase A — Thing A", out.rendered)
        self.assertIn("| Criterion 1 |", out.rendered)

    def test_inline_map_needs_names_and_criteria_text(self):
        raw = self.inline_map()
        del raw["targets"][0]["name"]
        del raw["targets"][0]["criteria"][0]["text"]
        self.assertProblem(raw, "name and exit_condition are mandatory when no source is set")
        self.assertProblem(raw, "criterion text is mandatory when no source is set")


OTHER = """# Second plan

## Phase A — Other first thing

### Exit condition

> Done when the other thing works.

### Acceptance test

1. it runs.
"""


class MultipleSourcesTest(TargetMapCase):
    def multi_map(self) -> dict:
        raw = base_map()
        raw["sources"].append({"id": "other", "label": "the other plan", "path": "other.md",
                               "target_heading": r"^## Phase (?P<id>\w+) — (?P<name>.+)$",
                               "exit_section": "Exit condition", "criteria_section": "Acceptance test"})
        raw["targets"].append({"id": "OA", "source": "other", "ref": "A", "goal": "G1", "state": "not started", "exit_met": False,
                               "summary": "Later.", "criteria": [{"n": 1, "status": "not run"}]})
        raw["targets"].append({"id": "X", "goal": "G1", "state": "not started", "exit_met": False, "name": "Inline thing",
                               "exit_condition": "It exists.", "summary": "Later.",
                               "criteria": [{"n": 1, "status": "not run", "text": "it exists"}]})
        return raw

    def test_two_sources_with_shared_ids_and_an_inline_target(self):
        ws = Workspace(self.multi_map(), extra={"other.md": OTHER})
        self.addCleanup(ws.close)
        out = ws.evaluate()
        self.assertEqual(out.problems, [])
        self.assertIn("### Phase OA — Other first thing", out.rendered)
        self.assertIn("Defined in [the other plan](../other.md).", out.rendered)
        self.assertIn("Defined inline in the map.", out.rendered)
        self.assertIn("Sources: plan.md, other.md", out.rendered)

    def test_unknown_source_id_fails(self):
        raw = self.multi_map()
        raw["targets"][2]["source"] = "nowhere"
        self.assertProblem(raw, "source `nowhere` is not listed under `sources`", extra={"other.md": OTHER})

    def test_ref_not_in_its_source_fails(self):
        raw = self.multi_map()
        raw["targets"][2]["ref"] = "Z"
        self.assertProblem(raw, "`Z` is not defined in source other", extra={"other.md": OTHER})

    def test_ref_without_source_fails(self):
        raw = self.multi_map()
        raw["targets"][3]["ref"] = "A"
        self.assertProblem(raw, "`ref` needs a `source`", extra={"other.md": OTHER})

    def test_missing_source_file_fails(self):
        self.assertProblem(self.multi_map(), "source other: `other.md` does not exist")

    def test_duplicate_source_ids_fail(self):
        raw = self.multi_map()
        raw["sources"][1]["id"] = "plan"
        self.assertProblem(raw, "source ids are not unique", extra={"other.md": OTHER})


CHANGELOG = """# Changelog

## Contents

- [20260928_0900 — Phase A work](#x)

## 20260928_0900 — Phase A work landed

Details about Phase A.

## 20260926_1000 — Older Phase B note

Phase B was discussed.

## 20260928_0930 — Phase AB is unrelated

Mentions Phase AB and Phase A-ish only.
"""


class ChangelogRuleTest(TargetMapCase):
    def with_changelog(self, reviewed_a: str, reviewed_b: str = "2026-09-27 12:00") -> dict:
        raw = base_map()
        raw["changelog"] = {"path": "CHANGELOG.md", "entry_heading": r"^## (?P<stamp>\d{8}_\d{4}) — "}
        raw["targets"][0]["reviewed"] = reviewed_a
        raw["targets"][1]["reviewed"] = reviewed_b
        return raw

    def test_entry_after_review_naming_the_target_fails(self):
        self.assertProblem(self.with_changelog("2026-09-27 12:00"), "target A: 1 change-log entry after its review",
                           extra={"CHANGELOG.md": CHANGELOG})

    def test_entry_at_or_before_review_passes(self):
        out = self.outcome(self.with_changelog("2026-09-28 09:00"), extra={"CHANGELOG.md": CHANGELOG})
        self.assertEqual(out.problems, [])

    def test_bare_date_counts_as_the_whole_day(self):
        out = self.outcome(self.with_changelog("2026-09-28"), extra={"CHANGELOG.md": CHANGELOG})
        self.assertEqual(out.problems, [])

    def test_older_entries_and_near_misses_do_not_match(self):
        # Phase B's only entry predates its review; "Phase AB" and "Phase A-ish" are not "Phase A".
        raw = self.with_changelog("2026-09-28 09:00")
        out = self.outcome(raw, extra={"CHANGELOG.md": CHANGELOG})
        self.assertFalse(any("target B" in p for p in out.problems))

    def test_reviewed_and_mention_are_mandatory_with_a_changelog(self):
        raw = self.with_changelog("2026-09-28 09:00")
        del raw["targets"][1]["reviewed"]
        self.assertProblem(raw, "target B: `mention` and `reviewed` are mandatory when changelog is set",
                           extra={"CHANGELOG.md": CHANGELOG})

    def test_missing_changelog_file_fails(self):
        self.assertProblem(self.with_changelog("2026-09-28 09:00"), "changelog `CHANGELOG.md` does not exist")


    def test_an_archive_index_is_not_read_as_the_last_live_entry(self):
        # The live log's last entry used to run on into the first archive's front matter and index (2026-10-10: five false findings).
        live = "# Changelog\n\n## 20260929_0900 — Unrelated work\n\nNothing here.\n"
        archive = ("---\nTitle: archive\n---\n\n## Index\n\n| 20260901_0900 | Phase B planning |\n\n"
                   "## 20260901_0900 — Phase B planning\n\nOld.\n")
        out = self.outcome(self.with_changelog("2026-09-28 09:00"),
                           extra={"CHANGELOG.md": live, "docs/history/changelog-20261010_0000.md": archive})
        self.assertEqual(out.problems, [])

class UpdatedAgeTest(TargetMapCase):
    def test_old_updated_fails(self):
        raw = base_map()
        raw["updated"] = "2026-09-01"
        self.assertProblem(raw, "map `updated` 2026-09-01 is over 7 days old")


class SourceReaderTest(unittest.TestCase):
    def test_reads_names_exit_given_and_joined_criteria(self):
        src = tm.Source(id="plan", path="plan.md", target_heading=r"^## Phase (?P<id>\w+) — (?P<name>.+)$",
                        exit_section="Exit condition", criteria_section="Acceptance test")
        defs = tm.SourceReader(PLAN, src).definitions()
        self.assertEqual(sorted(defs), ["A", "B"])
        a = defs["A"]
        self.assertEqual(a.name, "First thing")
        self.assertEqual(a.exit_condition, "Proceed when the first thing works.")
        self.assertEqual(a.given, "Given a lab")
        self.assertEqual(a.criteria, {1: "The widget starts", 2: "The widget stops and reports why"})


class RenderTest(TargetMapCase):
    def test_render_is_deterministic_and_drift_is_detected(self):
        ws = Workspace(base_map())
        self.addCleanup(ws.close)
        first = ws.evaluate()
        self.assertTrue(first.drift)
        first.output.write_text(first.rendered, encoding="utf-8")
        second = ws.evaluate()
        self.assertFalse(second.drift)
        self.assertEqual(first.rendered, second.rendered)

    def test_prose_is_wrapped_at_the_limit(self):
        raw = base_map()
        raw["targets"][0]["summary"] = "word " * 120
        out = self.outcome(raw)
        prose = [l for l in out.rendered.splitlines() if not l.startswith(("|", "```"))]
        self.assertTrue(all(len(l) <= tm.WRAP for l in prose))

    def test_labels_and_links_render(self):
        out = self.outcome(copy.deepcopy(base_map()))
        self.assertIn("## Per phase", out.rendered)
        self.assertIn("[notes](../notes.md)", out.rendered)


NOW = dt.datetime(2026, 9, 27, 20, 5)
HEADING = r"^## Phase (?P<id>\w+) — (?P<name>.+)$"


def fill_placeholders(text: str) -> str:
    """What a person does after --init: replace every TODO and pick the goal."""
    return text.replace("TODO_GOAL", "G1").replace("'TODO'", "'Filled.'").replace("TODO", "Filled")


class PlaceholderTest(TargetMapCase):
    def test_a_todo_left_in_fails(self):
        raw = base_map()
        raw["goals"][0]["statement"] = "TODO: why this project exists"
        self.assertProblem(raw, "placeholder")

    def test_todo_inside_prose_is_not_a_placeholder(self):
        raw = base_map()
        raw["targets"][0]["summary"] = "The TODO list in the plan is out of scope."
        self.assertEqual(self.outcome(raw).problems, [])


class InitTest(unittest.TestCase):
    def workspace(self, plan: str | None = PLAN) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        if plan is not None:
            (root / "plan.md").write_text(plan, encoding="utf-8")
        (root / "ROADMAP.md").write_text(ROADMAP, encoding="utf-8")
        (root / "docs").mkdir()
        return root

    def test_source_mode_tracks_every_heading_with_nothing_asserted(self):
        root = self.workspace()
        raw = yaml.safe_load(tm.starter_map(root, source_path="plan.md", target_heading=HEADING, label="Phase", now=NOW))
        self.assertEqual([t["id"] for t in raw["targets"]], ["A", "B"])
        self.assertEqual([c["n"] for c in raw["targets"][0]["criteria"]], [1, 2])
        statuses = {c["status"] for t in raw["targets"] for c in t["criteria"]}
        self.assertEqual(statuses, {"not run"})
        self.assertEqual({t["state"] for t in raw["targets"]}, {"not started"})
        self.assertEqual(raw["targets"][0]["mention"], "Phase A")

    def test_a_starter_map_fails_until_its_placeholders_are_filled(self):
        root = self.workspace()
        text = tm.starter_map(root, source_path="plan.md", target_heading=HEADING, label="Phase", now=NOW)
        (root / tm.MAP_FILE).write_text(text, encoding="utf-8")
        self.assertTrue(any("placeholder" in p for p in tm.evaluate(root, TODAY).problems))
        (root / tm.MAP_FILE).write_text(fill_placeholders(text), encoding="utf-8")
        self.assertEqual(tm.evaluate(root, TODAY).problems, [])

    def test_inline_mode_without_a_plan(self):
        root = self.workspace(plan=None)
        text = tm.starter_map(root, now=NOW)
        raw = yaml.safe_load(text)
        self.assertNotIn("sources", raw)
        self.assertEqual(raw["targets"][0]["criteria"][0]["status"], "not run")
        (root / tm.MAP_FILE).write_text(text, encoding="utf-8")
        self.assertTrue(any("placeholder" in p for p in tm.evaluate(root, TODAY).problems))
        (root / tm.MAP_FILE).write_text(fill_placeholders(text), encoding="utf-8")
        self.assertEqual(tm.evaluate(root, TODAY).problems, [])

    def test_a_heading_pattern_that_matches_nothing_is_refused(self):
        root = self.workspace()
        with self.assertRaises(tm.InitError):
            tm.starter_map(root, source_path="plan.md", target_heading=r"^## Step (?P<id>\d+) — (?P<name>.+)$", now=NOW)


class SyncTest(TargetMapCase):
    GROWN = PLAN + """
## Phase C — Third thing

### Exit condition

> Proceed when the third thing works.

### Acceptance test

1. one;
2. two;
3. three.
"""

    def test_a_new_heading_becomes_a_not_started_target_and_nothing_else_changes(self):
        ws = Workspace(base_map(), plan=self.GROWN)
        self.addCleanup(ws.close)
        before = (ws.root / tm.MAP_FILE).read_text(encoding="utf-8")
        self.assertTrue(any("defines `C` but no target tracks it" in p for p in ws.evaluate().problems))
        text, added = tm.sync_text(before, ws.root, now=NOW)
        self.assertEqual(added, ["C"])
        self.assertTrue(text.startswith(before))
        new = yaml.safe_load(text)["targets"][-1]
        self.assertEqual((new["id"], new["state"], [c["status"] for c in new["criteria"]]), ("C", "not started", ["not run"] * 3))
        self.assertEqual(new["goal"], "TODO_GOAL")

    def test_sync_is_idempotent(self):
        ws = Workspace(base_map(), plan=self.GROWN)
        self.addCleanup(ws.close)
        once, _ = tm.sync_text((ws.root / tm.MAP_FILE).read_text(encoding="utf-8"), ws.root, now=NOW)
        twice, added = tm.sync_text(once, ws.root, now=NOW)
        self.assertEqual((twice, added), (once, []))

    def test_refuses_when_targets_is_not_the_last_key(self):
        raw = base_map()
        raw = {k: v for k, v in raw.items() if k != "goals"} | {"goals": raw["goals"]}
        ws = Workspace(raw, plan=self.GROWN)
        self.addCleanup(ws.close)
        with self.assertRaises(tm.SyncError):
            tm.sync_text((ws.root / tm.MAP_FILE).read_text(encoding="utf-8"), ws.root, now=NOW)


class ShowTest(TargetMapCase):
    """`--show` reads one target without loading the whole map into an agent's context."""

    def test_list_and_one_target(self):
        """The listing names every target; one target shows its definition and its map entry, shorter than the map."""
        ws = Workspace(base_map())
        self.addCleanup(ws.close)
        listing = tm.show(ws.root, None)
        self.assertIn("(2 targets; `--show <id>` for one)", listing)
        one = tm.show(ws.root, "A")
        self.assertIn("id: A", one)
        self.assertIn("1. The widget starts", one)

    def test_unknown_target_raises(self):
        """An id the map lacks raises KeyError."""
        ws = Workspace(base_map())
        self.addCleanup(ws.close)
        with self.assertRaises(KeyError):
            tm.show(ws.root, "no-such-target")


CHECKLIST_PLAN = """# Plan

### S0 — Ready

- **Target:** the lab VM and a key;
  both stored.
- **Completion checklist:** [x] VM up (2026-10-20) · [ ] key made · [ ] R4 and R5
  recorded. Results: [report](report.md).
- **Rollback:** nothing.

### S1 — Rebuild

The tests are in another document.
"""


def checklist_map() -> dict:
    """A map over a bullet-style plan: S0 with a checklist line (criterion 1 passed), S1 with no criteria in its source."""
    raw = base_map()
    del raw["roadmap_file"]
    raw["labels"] = {"target": "Stage", "section": "Per stage"}
    raw["sources"] = [{"id": "pi", "label": "the plan", "path": "plan.md", "target_heading": r"^### (?P<id>S\d) — (?P<name>.+)$",
                       "exit_line": "Target", "checklist_line": "Completion checklist"}]
    raw["targets"] = [
        {"id": "S0", "source": "pi", "goal": "G1", "state": "in progress", "exit_met": False, "mention": "S0", "summary": "VM half done.",
         "blocker": {"owner": "none", "text": "none"}, "next": {"owner": "operator", "text": "bring the Pi"}, "evidence": [{"path": "notes.md"}],
         "as_built": {"intro": "Built.", "diagram": "vm"},
         "criteria": [{"n": 1, "status": "pass", "verified": "2026-09-26", "evidence": [{"path": "notes.md"}]},
                      {"n": 2, "status": "not run"}, {"n": 3, "status": "not run"}]},
        {"id": "S1", "source": "pi", "goal": "G1", "state": "not started", "exit_met": False, "mention": "S1", "summary": "Parked.",
         "blocker": {"owner": "operator", "text": "parked"}, "criteria": []},
    ]
    return raw


class ChecklistSourceTest(TargetMapCase):
    """Plans written as bold-lead bullets (2026-10-21): the exit line and a one-line checklist are read as the target's definition."""

    def test_checklist_items_become_numbered_criteria(self):
        """Each `[ ]`/`[x]` item is a criterion; continuation lines join; text after the item's full stop is dropped; `[x]` is ticked."""
        src = tm.Source(id="pi", path="plan.md", target_heading=r"^### (?P<id>S\d) — (?P<name>.+)$", exit_line="Target",
                        checklist_line="Completion checklist")
        defs = tm.SourceReader(CHECKLIST_PLAN, src).definitions()
        self.assertEqual(defs["S0"].criteria, {1: "VM up (2026-10-20)", 2: "Key made", 3: "R4 and R5 recorded"})
        self.assertEqual(defs["S0"].ticked, frozenset({1}))
        self.assertEqual(defs["S0"].exit_condition, "the lab VM and a key; both stored.")
        self.assertEqual(defs["S1"].criteria, {})

    def test_map_over_a_checklist_plan_is_valid(self):
        """A source target with no criteria in its source may carry `criteria: []`."""
        self.assertEqual(self.outcome(checklist_map(), plan=CHECKLIST_PLAN).problems, [])

    def test_criteria_count_still_checked(self):
        """A checklist target that drops a criterion fails, as a numbered one does."""
        raw = checklist_map()
        raw["targets"][0]["criteria"].pop()
        self.assertProblem(raw, "differ from the source's", plan=CHECKLIST_PLAN)

    def test_tick_disagreement_warns(self):
        """The source ticks criterion 1; a map that says `not run` gets a warning, not a failure."""
        raw = checklist_map()
        raw["targets"][0]["criteria"][0] = {"n": 1, "status": "not run"}
        out = self.outcome(raw, plan=CHECKLIST_PLAN)
        self.assertTrue(any("source ticks it but the map says `not run`" in w for w in out.warnings), out.warnings)

    def test_numbered_source_never_warns_about_ticks(self):
        """Tick warnings are for checklist sources only: a numbered criteria section has no ticks to disagree with."""
        out = self.outcome(base_map())
        self.assertFalse(any("ticks" in w for w in out.warnings), out.warnings)

    def test_inline_target_needs_a_criterion(self):
        """`criteria: []` is allowed only where a source defines none: an inline target without one fails."""
        raw = checklist_map()
        raw["targets"].append({"id": "T", "goal": "G1", "state": "not started", "exit_met": False, "mention": "triage T",
                               "name": "Triage", "exit_condition": "Designs agree.", "summary": "", "criteria": []})
        self.assertProblem(raw, "an inline target needs at least one criterion", plan=CHECKLIST_PLAN)


class StartedOnlyTest(TargetMapCase):
    """`changelog.started_only` (operator, 2026-10-21): a not-started target is exempt from the change-log rule; a started one is not."""

    LOG = "# Log\n\n## 20260927_1200 — Planned S1 and worked on S0\n\nS1 later, S0 now.\n"

    def raw(self, started_only: bool) -> dict:
        """The checklist map with a changelog that names both targets after their review.

        Args:
            started_only: the flag under test.

        Returns:
            The raw map.
        """
        raw = checklist_map()
        raw["changelog"] = {"path": "CHANGELOG.md", "entry_heading": r"^## (?P<stamp>\d{8}_\d{4}) — ", "started_only": started_only}
        for t in raw["targets"]:
            t["reviewed"] = "2026-09-27 09:00"
        return raw

    def test_default_flags_every_target(self):
        """Without the flag, both targets are behind their change log."""
        out = self.outcome(self.raw(False), plan=CHECKLIST_PLAN, extra={"CHANGELOG.md": self.LOG}).problems
        self.assertTrue(any(p.startswith("target S1:") for p in out), out)
        self.assertTrue(any(p.startswith("target S0:") for p in out), out)

    def test_started_only_exempts_not_started(self):
        """With the flag, only the started target S0 is flagged."""
        out = self.outcome(self.raw(True), plan=CHECKLIST_PLAN, extra={"CHANGELOG.md": self.LOG}).problems
        self.assertFalse(any(p.startswith("target S1:") for p in out), out)
        self.assertTrue(any(p.startswith("target S0:") for p in out), out)


class EmbedTest(TargetMapCase):
    """`embed`: the summary table rendered into another page between markers, the page's own text untouched."""

    PAGE = f"# Plan tracker\n\nHand text.\n\n## Stages\n\n{tm.EMBED_BEGIN}\nold\n{tm.EMBED_END}\n\nMore hand text.\n"

    def ws(self, page: str | None = None, wrap: int = 0) -> Workspace:
        """A workspace with the checklist map embedding into docs/plan.md.

        Args:
            page: the page text; default PAGE.
            wrap: the embed's wrap_width; 0 (default) keeps one line per row.

        Returns:
            The workspace.
        """
        raw = checklist_map()
        raw["embed"] = [{"path": "docs/plan.md", "heading": "Generated from the target map.", "wrap_width": wrap}]
        ws = Workspace(raw, plan=CHECKLIST_PLAN, extra={"docs/plan.md": self.PAGE if page is None else page})
        self.addCleanup(ws.close)
        return ws

    def test_embed_drift_then_write_then_current(self):
        """A stale block is drift; --write splices it; the second run is current and the hand text is untouched."""
        ws = self.ws()
        out = ws.evaluate()
        self.assertEqual(out.problems, [])
        self.assertTrue(out.drift)
        (ws.root / "docs/tracker.md").write_text(out.rendered, encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tm.main(["--project-root", str(ws.root), "--write", "--today", TODAY.isoformat()]), 0)
        page = (ws.root / "docs/plan.md").read_text(encoding="utf-8")
        self.assertTrue(page.startswith("# Plan tracker\n\nHand text.\n\n## Stages\n\n"))
        self.assertTrue(page.endswith(f"{tm.EMBED_END}\n\nMore hand text.\n"))
        self.assertIn("| [S0](tracker.md#stage-s0--ready) | Ready | in progress | no | VM half done. |", page)
        self.assertFalse(ws.evaluate().drift)

    def test_missing_markers_fail(self):
        """A page without the markers is a problem, not a silent skip."""
        self.assertTrue(any("target-map BEGIN marker" in p for p in self.ws("# Page\n").evaluate().problems))

    def test_empty_criteria_render_a_sentence(self):
        """A target without criteria renders a sentence instead of an empty table."""
        out = self.ws().evaluate()
        self.assertIn("The source writes no acceptance criteria for this stage yet.", out.rendered)

    def test_embed_wraps_as_the_hook_does(self):
        """The default wrap_width (200) pads and wraps the table through table-reflow; the page then reads current."""
        tw = sys.modules["table_wrap"]
        if not (tw.Path(tw.TABLE_REFLOW).is_file() and tw.shutil.which("node")):
            self.skipTest("table-reflow or node not on this machine")
        ws = self.ws(wrap=200)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tm.main(["--project-root", str(ws.root), "--write", "--today", TODAY.isoformat()]), 0)
        page = (ws.root / "docs/plan.md").read_text(encoding="utf-8")
        self.assertIn("| Stage | Name    |", page)
        self.assertFalse(ws.evaluate().drift)


if __name__ == "__main__":
    unittest.main()
