"""Offline tests for role_rerun_cost.py on a fixture repo. Run: `just role_rerun_cost_test` (skill-smc venv). <1 s."""

from __future__ import annotations

import contextlib
import io
import json
import runpy
import tempfile
import unittest
from pathlib import Path

MOD = runpy.run_path(str(Path(__file__).resolve().parent / "role_rerun_cost.py"))

TASKS = """
- name: Install packages one by one
  package:
    name: "{{ item }}"
    state: present
  loop: "{{ pkgs }}"
- name: Install packages as a list
  ansible.builtin.package:
    name: "{{ pkgs }}"
- name: Refresh apt
  apt:
    update_cache: yes
- name: Clear old checkout
  file:
    path: /var/www/x
    state: absent
- name: Clone
  git:
    repo: git@example:x.git
    dest: /var/www/x
- name: Run once
  command: do-thing
  args:
    creates: /etc/done
# - name: Commented task
#   command: never
"""
PLAYBOOK = """
- name: One
  hosts: all
  roles:
    - role: demo
      vars:
        a: 1
- name: Two
  hosts: all
  roles:
    - demo
  tags: two
"""


class RoleRerunCostTest(unittest.TestCase):
  """Counts on a fixture role and role discovery from a playbook."""

  def setUp(self) -> None:
    """Build a fixture repo with one role and one playbook.

    Args:
      None.

    Returns:
      None.

    Raises:
      OSError: when the temp folder cannot be written.
    """
    self.tmp = tempfile.TemporaryDirectory()
    self.repo = Path(self.tmp.name)
    (self.repo / "roles/demo/tasks").mkdir(parents=True)
    (self.repo / "roles/demo/tasks/main.yml").write_text(TASKS, encoding="utf-8")
    (self.repo / "site.yml").write_text(PLAYBOOK, encoding="utf-8")

  def tearDown(self) -> None:
    """Remove the fixture.

    Args:
      None.

    Returns:
      None.

    Raises:
      Nothing.
    """
    self.tmp.cleanup()

  def test_counts(self) -> None:
    """Six named tasks, one per-item loop, one refresh without cache_valid_time, one delete, one git, one creates guard."""
    row = MOD["scan_role"](self.repo / "roles/demo")
    self.assertEqual(row["tasks"], 6)
    self.assertEqual(row["pkg_loops"], 1)
    self.assertEqual((row["update_cache"], row["cache_valid_time"]), (1, 0))
    self.assertEqual((row["absent"], row["git"]), (1, 1))
    self.assertEqual((row["cmd_shell"], row["creates"]), (1, 1))

  def test_playbook_roles_deduplicated(self) -> None:
    """Both role forms are found once."""
    self.assertEqual(MOD["roles_in_playbook"](PLAYBOOK), ["demo"])

  def test_main_json_and_missing_role(self) -> None:
    """--json prints the total; a missing role exits 2."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
      code = MOD["main"](["--repo", str(self.repo), "--playbook", "site.yml", "--json"])
    self.assertEqual(code, 0)
    self.assertEqual(json.loads(out.getvalue())["total"]["tasks"], 6)
    with contextlib.redirect_stderr(io.StringIO()):
      self.assertEqual(MOD["main"](["--repo", str(self.repo), "--role", "nope"]), 2)


if __name__ == "__main__":
  unittest.main()
