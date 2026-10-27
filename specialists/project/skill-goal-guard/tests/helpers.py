"""Shared test helpers: load goal_guard_lib modules by name and build a throwaway copy of the example projects.

Imported by the tests, not run. Modules are loaded with importlib after putting scripts/ on sys.path, so test files keep their
imports at the top (skill-coder languages/python.md, Learned 2026-10-19). Safety: files only, under a temporary folder.
"""

import datetime as dt
import importlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
EXAMPLES = ROOT / "examples"
if str(SCRIPTS) not in sys.path:
  sys.path.insert(0, str(SCRIPTS))
NOW = dt.datetime(2026, 10, 27, 12, 0, tzinfo=dt.timezone(dt.timedelta(hours=11)))


def lib(name: str):
  """Import one goal_guard_lib module.

  Args:
    name: module name inside goal_guard_lib, e.g. "decide".

  Returns:
    The module.
  """
  return importlib.import_module(f"goal_guard_lib.{name}")


class Workspace:
  """A temporary copy of examples/project_stuff with helpers to edit it; use as a context manager.

  Args:
    none.
  """

  def __enter__(self) -> Workspace:
    """Copy the examples into a new temporary folder.

    Returns:
      self, with root (the copied project_stuff) and spoke (demo-spoke) set.
    """
    self._tmp = tempfile.TemporaryDirectory()
    self.base = Path(self._tmp.name).resolve()
    self.root = self.base / "project_stuff"
    shutil.copytree(EXAMPLES / "project_stuff", self.root)
    self.spoke = self.root / "apn" / "demo-spoke"
    return self

  def __exit__(self, *exc) -> None:
    """Remove the temporary folder.

    Args:
      *exc: exception details, ignored.
    """
    self._tmp.cleanup()

  def edit_yaml(self, relative: str, **changes) -> None:
    """Change top-level keys of a YAML record in the spoke.

    Args:
      relative: path under the spoke, e.g. ".gg/mvp.yaml".
      **changes: keys to set; a value of None removes the key.
    """
    yaml_io = lib("yaml_io")
    path = self.spoke / relative
    data = yaml_io.load_file(path) or {}
    for key, value in changes.items():
      if value is None:
        data.pop(key, None)
      else:
        data[key] = value
    path.write_text(yaml_io.dump_text(data), encoding="utf-8")

  def project(self):
    """Load the spoke.

    Returns:
      The loaded Project.
    """
    return lib("project").load(self.spoke)

  def baseline(self, proj=None):
    """Judge the spoke's baseline from its decision log.

    Args:
      proj: an already loaded project, or None to load it.

    Returns:
      The BaselineState.
    """
    proj = proj or self.project()
    log = lib("decisions_log")
    entries, _ = log.read(proj.decisions_path)
    return lib("project").baseline_state(proj, log.approvals(entries))


def tasks():
  """Load the example Vikunja tasks.

  Returns:
    The TaskSet from examples/vikunja-tasks.json.
  """
  return lib("tasks").from_file(EXAMPLES / "vikunja-tasks.json")


def raw_tasks() -> list[dict]:
  """Load the example raw Vikunja task objects.

  Returns:
    The items list.
  """
  return json.loads((EXAMPLES / "vikunja-tasks.json").read_text())["items"]


def proposal(**overrides):
  """Build a Proposal from the PROCEED fixture with fields changed.

  Args:
    **overrides: fields to set; a value of None removes the field.

  Returns:
    The parsed Proposal.
  """
  data = lib("yaml_io").load_file(EXAMPLES / "proposals" / "proceed.yaml")
  for key, value in overrides.items():
    if value is None:
      data.pop(key, None)
    else:
      data[key] = value
  return lib("records").parse_proposal(data)
