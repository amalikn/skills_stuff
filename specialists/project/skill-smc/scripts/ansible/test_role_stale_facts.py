"""Offline tests for role_stale_facts.py on a fixture role. Run: `just role_stale_facts_test` (skill-smc venv, PyYAML). <2 s."""

from __future__ import annotations

import runpy
import tempfile
import unittest
from pathlib import Path

MOD = runpy.run_path(str(Path(__file__).resolve().parent / "role_stale_facts.py"))

MAIN = """
- name: Set a flag only when it holds
  ansible.builtin.set_fact:
    flag_done: yes
  when: something
- name: Set one always
  ansible.builtin.set_fact:
    always_set: 1
- name: Include a guarded file
  ansible.builtin.include_tasks: guarded.yml
  when: other
- name: Read them
  ansible.builtin.debug:
    msg: "{{ flag_done is defined }} {{ always_set | default(0) }} {{ inner | default('') }}"
"""
GUARDED = """
- name: Set inside a guarded include
  ansible.builtin.set_fact:
    inner: x
"""
RESET = """
- name: Reset per run
  ansible.builtin.set_fact:
    flag_done: ''
"""


class StaleFactsTest(unittest.TestCase):
  """scan() on a fixture role."""

  def test_finds_guarded_facts_and_marks_resets(self) -> None:
    """A when-guarded flag and a fact set in a guarded include are found; the always-set one is not; the reset file marks flag_done."""
    with tempfile.TemporaryDirectory() as folder:
      role = Path(folder)
      (role / "tasks").mkdir()
      (role / "tasks/main.yml").write_text(MAIN)
      (role / "tasks/guarded.yml").write_text(GUARDED)
      (role / "tasks/reset.yml").write_text(RESET)
      rows = {key: is_reset for key, _, _, is_reset in MOD["scan"](role, "tasks/reset.yml")}
    self.assertEqual(rows, {"flag_done": True, "inner": False})


if __name__ == "__main__":
  unittest.main()
