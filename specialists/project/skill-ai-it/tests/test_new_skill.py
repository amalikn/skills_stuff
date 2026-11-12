"""Tests for the new-skill capability: seed parsing, scaffold plan and apply, repeat-safety, and the pack contract check.

Run: python -m unittest discover -s tests   (or `just test`)
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "scripts" / "skills"


def load(name: str):
  """Import one module of scripts/skills by path, so the tests need no sys.path edit.

  Args:
    name: the module name (file stem).

  Returns:
    The loaded module, also registered in sys.modules so modules that import each other resolve.
  """
  spec = importlib.util.spec_from_file_location(name, SKILLS / f"{name}.py")
  module = importlib.util.module_from_spec(spec)
  sys.modules[name] = module
  spec.loader.exec_module(module)
  return module


ss = load("skill_seed")
ns = load("new_skill")
spc = load("skill_pack_check")

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "skill-seed.md"

SEED = """---
Title: Skill seed: skill-demo
Category: skill-seed
Status: draft
Authority: test
Scope: test
Last reviewed: 20261112_1200
Summary: test seed
---

# Skill seed: skill-demo

## Parameters

```text seed-parameters
name: skill-demo
family: specialists/project
short_description: Demo topics: one, two, three.
aliases:
scripts: no
operator_context: no
memory_channel: demo
related: skill-coder
```

## Purpose and users

The demo skill lets an agent produce a demonstration artifact the same way every time, for the operator and for calling skills, in any project that needs one.

## Trigger phrases

- make a demo
- demo this
- show a demonstration

## Non-goals and neighbours

| Not this skill's job | Owner |
| --- | --- |
| Writing code | skill-coder |

## Source material

| Source | Where | Label | Capture |
| --- | --- | --- | --- |
| The operator | chat | USER_STATED | not needed |

## What was learned

| Lesson | Evidence | Becomes |
| --- | --- | --- |
| Review the render before showing it | session 2026-11-12 | standing rule |

## Vocabulary

- demo: a sample artifact

## Outputs and artifacts

| Output | Format and name | Saved in | Reader |
| --- | --- | --- | --- |
| Demo | demo-YYYYMMDD_hhmm.md | docs/ | the operator |

## Task routing

| Task | Reference file | Contents |
| --- | --- | --- |
| Make a demo | making-demos.md | Steps, checks and a worked example |
| Review a demo | reviewing-demos.md | What to look at before showing |

## Scripts plan

none

## Templates and assets

- none

## Standing rules

| Rule | Reason | Decided by |
| --- | --- | --- |
| Review before showing | an unreviewed render hid a fault | operator, 2026-11-12 |

## Safety boundaries

- Reads: the project's docs
- Writes: only files the task names
- Never: send anything outside the project

## Evidence plan

| Claim | Evidence and source | Falsifier |
| --- | --- | --- |
| A reviewed demo has fewer faults | session record | a reviewed demo with the same faults |

## Acceptance scenarios

| Prompt | Expected behaviour |
| --- | --- |
| Make a demo of X | Loads making-demos.md and reviews before showing |
| Review this demo | Loads reviewing-demos.md |
| Write a Python script | Does not use this skill |
| Make a demo and send it to a customer | Stops and asks before sending |
| Demo with no source given | Asks for the source |

## Write-back

- Learned entries go to: references/making-demos.md
- Stays in the project: names and paths

## Install and registry

- Registry rows: skills.md row for skill-demo

## Open questions

| Question | Blocking | Owner |
| --- | --- | --- |
| Which formats beyond markdown | later | operator |

## Build order and done

1. Check the seed.
"""


def quiet(fn, *args):
  """Call fn with stdout and stderr captured; return (result, stdout, stderr)."""
  out, err = io.StringIO(), io.StringIO()
  with redirect_stdout(out), redirect_stderr(err):
    result = fn(*args)
  return result, out.getvalue(), err.getvalue()


class SeedTests(unittest.TestCase):
  """Parsing and validating seeds."""

  def write(self, text: str) -> Path:
    """Write text to a temp seed file."""
    d = Path(tempfile.mkdtemp())
    self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
    p = d / "seed.md"
    p.write_text(text, encoding="utf-8")
    return p

  def test_template_is_incomplete_and_names_its_problems(self):
    """The shipped template fails check-seed until every TODO(seed) is filled."""
    problems = ss.seed_problems(ss.parse_seed(TEMPLATE))
    self.assertTrue(any("TODO(seed)" in p for p in problems))
    self.assertTrue(any("parameter 'name'" in p for p in problems))

  def test_complete_seed_has_no_problems(self):
    """The fixture seed passes."""
    self.assertEqual([], ss.seed_problems(ss.parse_seed(self.write(SEED))))

  def test_blocking_question_stops_the_build(self):
    """A blocking open question is a problem."""
    seed = ss.parse_seed(self.write(SEED.replace("| later |", "| blocking |")))
    self.assertTrue(any("blocking open question" in p for p in ss.seed_problems(seed)))

  def test_vague_reference_name_is_refused(self):
    """misc.md is not a topic name."""
    seed = ss.parse_seed(self.write(SEED.replace("making-demos.md", "misc.md")))
    self.assertTrue(any("too vague" in p for p in ss.seed_problems(seed)))

  def test_fewer_than_five_scenarios_is_a_problem(self):
    """The scenario minimum is enforced."""
    cut = SEED.replace("| Demo with no source given | Asks for the source |\n", "")
    self.assertTrue(any("Acceptance scenarios" in p for p in ss.seed_problems(ss.parse_seed(self.write(cut)))))

  def test_wrapped_table_rows_are_merged(self):
    """Rows wrapped by the repo's table formatter (cells indented by three spaces) continue the row above, whichever cell wraps."""
    section = (
      "| Task | File | Contents |\n| --- | --- | --- |\n"
      "| Cover business, technical and | thing.md | First words of the |\n"
      "|   management views | | long contents text |\n"
      "| Next | next.md | Short |\n"
      "| Another task | other.md | Words |\n"
      "|   | | more words |\n"
    )
    rows = ss.table_rows(section)
    self.assertEqual(
      [
        ["Cover business, technical and management views", "thing.md", "First words of the long contents text"],
        ["Next", "next.md", "Short"],
        ["Another task", "other.md", "Words more words"],
      ],
      rows,
    )

  def test_comments_do_not_count_as_content(self):
    """Guidance inside HTML comments is ignored by the parser."""
    seed = ss.parse_seed(self.write(SEED.replace("## Vocabulary", "## Vocabulary\n\n<!-- TODO(seed) in a comment -->")))
    self.assertEqual([], ss.seed_problems(seed))

  def test_render_rejects_unknown_placeholder(self):
    """A template placeholder the mapping lacks raises."""
    with self.assertRaises(ValueError):
      ns.render("hello {{NOPE}}", {"NAME": "x"})


class ScaffoldTests(unittest.TestCase):
  """Scaffold plan, apply and repeat-safety."""

  def setUp(self):
    """A temp skills root and a complete seed file."""
    self.root = Path(tempfile.mkdtemp())
    self.addCleanup(lambda: __import__("shutil").rmtree(self.root, ignore_errors=True))
    self.seed = self.root / "seed.md"
    self.seed.write_text(SEED, encoding="utf-8")
    self.pack = self.root / "specialists" / "project" / "skill-demo"

  def run_scaffold(self, *extra: str):
    """Run the scaffold command line against the temp root."""
    return quiet(ns.main, ["--skills-root", str(self.root), "scaffold", str(self.seed), *extra])

  def test_plan_writes_nothing(self):
    """Without --apply no file appears."""
    code, out, _ = self.run_scaffold()
    self.assertEqual(0, code)
    self.assertIn("plan only", out)
    self.assertFalse(self.pack.exists())

  def test_apply_writes_the_skeleton(self):
    """--apply creates SKILL.md, the two routed references and the seed copy."""
    code, _, _ = self.run_scaffold("--apply")
    self.assertEqual(0, code)
    for rel in (
      "SKILL.md",
      "AGENTS.md",
      "references/making-demos.md",
      "references/reviewing-demos.md",
      "references/evolution-and-write-back.md",
      "sources.yaml",
      "compatibility.yaml",
      "tests/scenarios.md",
      "tests/test_package_contract.py",
    ):
      self.assertTrue((self.pack / rel).is_file(), rel)
    self.assertFalse(list(self.pack.rglob("seed-*.md")), "the seed is never copied into the pack")
    self.assertFalse((self.pack / "scripts").exists(), "scripts: no means no scripts folder, ruff or mise pin")
    self.assertFalse((self.pack / "operator").exists())

  def test_second_run_changes_nothing_and_edits_become_proposed(self):
    """A rerun skips identical files; a hand-edited file gets a .proposed beside it, never an overwrite."""
    self.run_scaffold("--apply")
    skill = self.pack / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nhand edit\n", encoding="utf-8")
    code, out, _ = self.run_scaffold("--apply")
    self.assertEqual(0, code)
    self.assertIn("hand edit", skill.read_text(encoding="utf-8"))
    self.assertTrue((self.pack / "SKILL.md.proposed").is_file())
    self.assertIn("propose", out)

  def test_forbidden_term_in_a_generated_file_is_refused(self):
    """The scaffold refuses when a forbidden term would enter the pack (here through a lesson rendered into SKILL.md)."""
    text = SEED.replace("related: skill-coder", "related: skill-coder\nforbidden_terms: Customer").replace(
      "Review before showing", "Review before showing a Customer"
    )
    self.seed.write_text(text, encoding="utf-8")
    code, out, err = self.run_scaffold("--apply")
    self.assertEqual(1, code)
    self.assertFalse(self.pack.exists())

  def test_a_part_file_becomes_the_reference_body(self):
    """parts/<reference>.md beside the seed is the body of that reference, under a generated front matter; unrouted parts are noted."""
    (self.root / "parts").mkdir()
    (self.root / "parts" / "making-demos.md").write_text("# Making demos\n\nDraft body from the part file.\n", encoding="utf-8")
    (self.root / "parts" / "stray.md").write_text("# stray\n", encoding="utf-8")
    code, out, _ = self.run_scaffold("--apply")
    self.assertEqual(0, code)
    body = (self.pack / "references" / "making-demos.md").read_text(encoding="utf-8")
    self.assertIn("Draft body from the part file.", body)
    self.assertTrue(body.startswith("---\nTitle:"))
    self.assertIn("1 reference(s) drafted from seed parts: making-demos.md", out)
    self.assertIn("NOTE part not routed (not used): parts/stray.md", out)
    self.assertFalse((self.pack / "references" / "stray.md").exists())

  def test_forbidden_terms_match_whole_words_only(self):
    """A forbidden name does not match inside a longer word (Rob in robust)."""
    leaks = ns.sc.find_leaks({"a.md": "A robust plan by Rob", "b.md": "A robust plan"}, ["Rob"])
    self.assertEqual(["a.md: Rob"], leaks)

  def test_incomplete_seed_is_refused(self):
    """A seed with a TODO(seed) left is refused and nothing is written."""
    self.seed.write_text(SEED.replace("- demo: a sample artifact", "- TODO(seed)"), encoding="utf-8")
    code, _, err = self.run_scaffold("--apply")
    self.assertEqual(1, code)
    self.assertIn("refused", err)
    self.assertFalse(self.pack.exists())

  def test_scripts_yes_adds_python_pin_and_lint_config(self):
    """scripts: yes adds .mise.toml, ruff.toml and requirements.txt, and a planned row in SKILL.md."""
    text = SEED.replace("scripts: no", "scripts: yes").replace(
      "## Scripts plan\n\nnone",
      "## Scripts plan\n\n| Script | Does | Origin | Safety | Test |\n| --- | --- | --- | --- | --- |\n| demo_tool.py | Makes a demo | new | read-only | test_demo_tool |",
    )
    self.seed.write_text(text, encoding="utf-8")
    self.run_scaffold("--apply")
    for rel in (".mise.toml", "ruff.toml", "requirements.txt"):
      self.assertTrue((self.pack / rel).is_file(), rel)
    self.assertIn("planned", (self.pack / "SKILL.md").read_text(encoding="utf-8"))

  def test_seed_command_writes_template_once(self):
    """`seed` writes the template with the name filled in and refuses to overwrite it."""
    out = self.root / "new-seed.md"
    code, _, _ = quiet(ns.main, ["--skills-root", str(self.root), "seed", "skill-other", "--out", str(out), "--apply"])
    self.assertEqual(0, code)
    self.assertIn("name: skill-other", out.read_text(encoding="utf-8"))
    for folder in ("research", "parts"):
      self.assertTrue((out.parent / folder / "readme.md").is_file(), f"{folder}/readme.md keeps the seed's research and parts together")
    code, _, err = quiet(ns.main, ["--skills-root", str(self.root), "seed", "skill-other", "--out", str(out), "--apply"])
    self.assertEqual(1, code)
    self.assertIn("refused", err)

  def test_bad_name_is_refused(self):
    """A name that is not skill-topic is rejected."""
    code, _, _ = quiet(ns.main, ["--skills-root", str(self.root), "seed", "Demo"])
    self.assertEqual(2, code)


class PackCheckTests(unittest.TestCase):
  """The pack contract check on a scaffolded pack, and where it must fail."""

  def setUp(self):
    """Scaffold a pack into a temp root."""
    self.root = Path(tempfile.mkdtemp())
    self.addCleanup(lambda: __import__("shutil").rmtree(self.root, ignore_errors=True))
    seed = self.root / "seed.md"
    seed.write_text(SEED, encoding="utf-8")
    quiet(ns.main, ["--skills-root", str(self.root), "scaffold", str(seed), "--apply"])
    self.pack = self.root / "specialists" / "project" / "skill-demo"

  def levels(self, level: str) -> list[str]:
    """Messages of one level for the pack."""
    return [str(f) for f in spc.check_pack(self.pack) if f.level == level]

  def test_fresh_scaffold_has_no_errors_but_warns_about_unfinished_markers(self):
    """A skeleton passes the contract and is flagged as unfinished."""
    self.assertEqual([], self.levels("error"))
    self.assertTrue(any("TODO(build)" in m for m in self.levels("warn")))
    code, _, _ = quiet(spc.main, [str(self.pack), "--strict"])
    self.assertEqual(1, code, "strict fails while markers remain")

  def test_unrouted_reference_is_an_error(self):
    """A reference file SKILL.md does not link fails."""
    (self.pack / "references" / "stray.md").write_text("---\nTitle: s\nSummary: s\n---\n# s\n", encoding="utf-8")
    self.assertTrue(any("stray.md" in m and "not linked" in m for m in self.levels("error")))

  def test_name_must_match_folder(self):
    """front matter name must equal the folder."""
    skill = self.pack / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8").replace("name: skill-demo", "name: skill-other", 1), encoding="utf-8")
    self.assertTrue(any("must equal the folder name" in m for m in self.levels("error")))

  def test_secret_is_an_error(self):
    """A token-looking assignment in an authored file fails."""
    (self.pack / "references" / "making-demos.md").write_text("---\nTitle: t\nSummary: s\n---\n\napi_key: Zk39dkQ82jfn38dKQpz91Lx\n", encoding="utf-8")
    self.assertTrue(any("credential" in m for m in self.levels("error")))

  def test_script_without_catalogue_and_test_is_an_error(self):
    """A script must be catalogued and tested."""
    (self.pack / "scripts").mkdir()
    (self.pack / "scripts" / "tool.py").write_text('"""Does a thing. Run: python scripts/tool.py"""\n', encoding="utf-8")
    msgs = self.levels("error")
    self.assertTrue(any("not catalogued" in m for m in msgs))
    self.assertTrue(any("no test mentions it" in m for m in msgs))

  def test_unreplaced_placeholder_is_an_error(self):
    """A template placeholder left in a file fails."""
    ref = self.pack / "references" / "making-demos.md"
    ref.write_text(ref.read_text(encoding="utf-8") + "\nleft over {{NAME}}\n", encoding="utf-8")
    self.assertTrue(any("placeholder" in m for m in self.levels("error")))

  def test_broken_link_in_skill_md_is_an_error(self):
    """A link to a missing file fails."""
    skill = self.pack / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nSee [gone](references/gone.md).\n", encoding="utf-8")
    self.assertTrue(any("link target does not exist" in m for m in self.levels("error")))


if __name__ == "__main__":
  unittest.main()
