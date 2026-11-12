"""Tests for the intake and research stage of new-skill: the form, the refusal on an unfinished interview, research briefs and the seed pre-fill.

Run: python -m unittest discover -s tests   (or `just test`)
"""

from __future__ import annotations

import importlib.util
import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "scripts" / "skills"
TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "skill-intake.md"


def load(name: str):
  """Import one module of scripts/skills by path.

  Args:
    name: the module name (file stem).

  Returns:
    The loaded module, registered in sys.modules.
  """
  spec = importlib.util.spec_from_file_location(name, SKILLS / f"{name}.py")
  module = importlib.util.module_from_spec(spec)
  sys.modules[name] = module
  spec.loader.exec_module(module)
  return module


ss = load("skill_seed")
si = load("skill_intake")
ns = load("new_skill")

INTAKE = """---
Title: Skill intake: skill-demo
Category: skill-intake
Status: draft
Authority: test
Scope: test
Last reviewed: 20261112_1200
Summary: test intake
---

# Skill intake: skill-demo

## Parameters

```text intake-parameters
name: skill-demo
family: specialists/project
short_description: Demos: make, review, ship.
scripts: no
operator_context: no
memory_channel: demo
related: skill-coder
forbidden_terms: Acme, Zed
```

## Round 1: purpose and callers

- Q1.1 What should an agent be able to do? Answer: Produce a demonstration artifact
  the same way every time.
- Q1.2 Who calls it? Answer: the operator
- Q1.3 Family? Answer: project
- Q1.4 Name? Answer: skill-demo

## Round 2: boundaries and safety

- Q2.1 Not do? Answer: writing code
- Q2.2 Writes? Answer: only named files
- Q2.3 Scripts? Answer: no
- Q2.4 Operator rules? Answer: none

## Round 3: knowledge to keep

- Q3.1 Work? Answer: a session
- Q3.2 Went wrong? Answer: unreviewed output
- Q3.3 Code? Answer: none
- Q3.4 Scope? Answer: markdown only

## Round 4: quality and install

- Q4.1 Prompts? Answer: make a demo
- Q4.2 Evidence? Answer: primary sources
- Q4.3 Open? Answer: none

## Material to harvest

| Source | Where | What to extract |
| --- | --- | --- |
| The session | this conversation | lessons |

## Neighbour skills to study

- skill-vagrant

## Research topics

| Area | Questions the research must answer | Products, formats or versions in scope |
| --- | --- | --- |
| Demo tooling | Which libraries make demos; what are their licences | markdown, version 1 |
| Demo review | How do others review demos; common failures | any |
"""


def quiet(fn, *args):
  """Call fn with stdout and stderr captured; return (result, stdout, stderr)."""
  out, err = io.StringIO(), io.StringIO()
  with redirect_stdout(out), redirect_stderr(err):
    result = fn(*args)
  return result, out.getvalue(), err.getvalue()


class IntakeTests(unittest.TestCase):
  """The intake form, its check, research briefs and the seed pre-fill."""

  def setUp(self):
    """A temp skills root and a complete intake file."""
    self.root = Path(tempfile.mkdtemp())
    self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
    self.intake = self.root / "intake.md"
    self.intake.write_text(INTAKE, encoding="utf-8")

  def run_cli(self, *argv: str):
    """Run new_skill.main against the temp root."""
    return quiet(ns.main, ["--skills-root", str(self.root), *argv])

  def test_the_template_is_an_unfinished_interview(self):
    """The shipped intake form reports every unanswered question."""
    problems = si.intake_problems(si.parse_intake(TEMPLATE))
    self.assertTrue(any("unanswered TODO(intake)" in p for p in problems))

  def test_a_finished_intake_has_no_problems(self):
    """The fixture is complete."""
    self.assertEqual([], si.intake_problems(si.parse_intake(self.intake)))

  def test_answers_are_read_across_wrapped_lines(self):
    """An answer wrapped onto a second line is joined."""
    seed = si.parse_intake(self.intake)
    self.assertEqual("Produce a demonstration artifact the same way every time.", si.answer(seed, "Q1.1"))

  def test_intake_command_writes_the_form_and_the_seed_folder(self):
    """`intake --apply` writes the form with the name filled in and the research and parts indexes."""
    code, _, _ = self.run_cli("intake", "skill-other", "--apply")
    self.assertEqual(0, code)
    folder = self.root / "pending_skills" / "skill-other"
    forms = list(folder.glob("intake-skill-other-*.md"))
    self.assertEqual(1, len(forms))
    self.assertIn("name: skill-other", forms[0].read_text(encoding="utf-8"))
    for sub in ("research", "parts"):
      self.assertTrue((folder / sub / "readme.md").is_file())

  def test_research_briefs_plan_then_apply(self):
    """Briefs are planned without writing, then written once per topic; reruns skip existing ones."""
    code, out, _ = self.run_cli("research-briefs", str(self.intake))
    self.assertEqual(0, code)
    self.assertFalse((self.root / "research").exists())
    self.assertIn("plan: would write", out)
    self.run_cli("research-briefs", str(self.intake), "--apply")
    briefs = sorted((self.root / "research" / "briefs").glob("brief-*.md"))
    self.assertEqual(["brief-demo-review.md", "brief-demo-tooling.md"], [b.name for b in briefs])
    text = briefs[1].read_text(encoding="utf-8")
    self.assertFalse(text.startswith("---"), "the template's front matter is stripped from a brief")
    self.assertIn("Produce a demonstration artifact", text)
    self.assertIn("do NOT use any of these words", text)
    _, out, _ = self.run_cli("research-briefs", str(self.intake), "--apply")
    self.assertIn("skip (exists)", out)

  def test_a_forbidden_term_in_a_topic_refuses_the_briefs(self):
    """A research topic that names a forbidden term would send it to an outside service, so it is refused."""
    self.intake.write_text(INTAKE.replace("Which libraries make demos", "Which libraries did Acme use for demos"), encoding="utf-8")
    code, out, err = self.run_cli("research-briefs", str(self.intake), "--apply")
    self.assertEqual(1, code)
    self.assertIn("LEAK", out)
    self.assertIn("refused", err)
    self.assertFalse((self.root / "research").exists())

  def test_an_unfinished_intake_refuses_the_briefs(self):
    """Research waits for the interview."""
    self.intake.write_text(INTAKE.replace("Answer: only named files", "Answer: TODO(intake)"), encoding="utf-8")
    code, out, _ = self.run_cli("research-briefs", str(self.intake), "--apply")
    self.assertEqual(1, code)
    self.assertIn("TODO(intake)", out)

  def test_seed_from_intake_fills_the_parameters(self):
    """`seed --from-intake` copies the answered parameters into the seed's parameter block."""
    out_path = self.root / "seed.md"
    code, _, _ = self.run_cli("seed", "skill-demo", "--from-intake", str(self.intake), "--out", str(out_path), "--apply")
    self.assertEqual(0, code)
    seed = ss.parse_seed(out_path)
    self.assertEqual("Demos: make, review, ship.", seed.params["short_description"])
    self.assertEqual("demo", seed.params["memory_channel"])
    self.assertEqual("Acme, Zed", seed.params["forbidden_terms"])
    self.assertEqual("no", seed.params["scripts"])


if __name__ == "__main__":
  unittest.main()
