"""Offline tests for scripts/markdown/md_examples_check.py: each check passes a clean file and fails a planted fault. Run: just test."""

import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("md_examples_check", Path(__file__).resolve().parents[1] / "scripts" / "markdown" / "md_examples_check.py")
mec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mec)

CLEAN = """# Title

## 1. Maps

See [maps](#1-maps).

| Map | Level |
| --- | --- |
| `code-map.toml` | Mandatory |

```toml
[meta]
schema = 1
```

```yaml
meta:
  schema: 1
```

```json
{"job": "a", "seconds": 1}
{"job": "b", "seconds": 2}
```

```python
def f(x):
    return x
```
"""


class Examples(unittest.TestCase):
  """Fenced examples parse, and a planted error in each language is found."""

  def test_clean(self):
    self.assertEqual(mec.check_examples(CLEAN), [])

  def test_yaml_block_holding_toml(self):
    bad = "```yaml\n[meta]\nschema = 1\n\nmeta:\n  schema: 1\n```\n"
    self.assertEqual(len(mec.check_examples(bad)), 1)

  def test_duplicate_toml_table(self):
    self.assertEqual(len(mec.check_examples("```toml\n[a.x]\nb=1\n[a.x]\nb=2\n```\n")), 1)

  def test_bad_json_line(self):
    self.assertEqual(len(mec.check_examples('```json\n{"a": 1}\n{"a": \n```\n')), 1)

  def test_python_syntax(self):
    self.assertEqual(len(mec.check_examples("```python\ndef f(:\n```\n")), 1)

  def test_other_languages_ignored(self):
    self.assertEqual(mec.check_examples("```hcl\noutput {\n```\n"), [])


class Tables(unittest.TestCase):
  """A row with a different cell count is found; code fences are skipped."""

  def test_clean(self):
    self.assertEqual(mec.check_tables(CLEAN), [])

  def test_pipe_inside_backticks(self):
    bad = "| A | B |\n| --- | --- |\n| `x|y` | z |\n"
    self.assertEqual(len(mec.check_tables(bad)), 1)

  def test_escaped_pipe_is_not_a_border(self):
    self.assertEqual(mec.check_tables("| A | B |\n| --- | --- |\n| `a\\|b` | c |\n"), [])

  def test_table_inside_fence_ignored(self):
    self.assertEqual(mec.check_tables("```text\n| a | b |\n| - | - |\n| 1 |\n```\n"), [])


class Anchors(unittest.TestCase):
  """Internal links resolve to headings."""

  def test_clean(self):
    self.assertEqual(mec.check_anchors(CLEAN), [])

  def test_renumbered_section(self):
    self.assertEqual(mec.check_anchors("## 2. Maps\n\nSee [maps](#1-maps).\n"), ["broken anchor #1-maps"])


if __name__ == "__main__":
  unittest.main()
