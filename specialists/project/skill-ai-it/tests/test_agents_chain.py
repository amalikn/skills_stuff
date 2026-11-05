"""scripts/checks/agents_chain.py: Claude import chains, Codex root and byte limit, and trust spread. Offline, temp folders only."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("agents_chain", _ROOT / "scripts/checks/agents_chain.py")
ac = importlib.util.module_from_spec(_spec)
sys.modules["agents_chain"] = ac
_spec.loader.exec_module(ac)


def tree(tmp: str) -> Path:
    """Build top/AGENTS.md <- top/ws/AGENTS.md <- top/ws/repo/AGENTS.md (a git repo), each importing the one above.

    Args:
        tmp: temp folder.

    Returns:
        The top folder.
    """
    top = Path(tmp).resolve() / "top"
    repo = top / "ws" / "repo"
    (repo / ".git").mkdir(parents=True)
    (top / "AGENTS.md").write_text("# top\n", encoding="utf-8")
    (top / "ws" / "AGENTS.md").write_text(f"@{top / 'AGENTS.md'}\n# ws\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text(f"@{top / 'ws' / 'AGENTS.md'}\n# repo\n", encoding="utf-8")
    return top


def config(tmp: str, body: str) -> Path:
    """Write a Codex config.toml.

    Args:
        tmp: temp folder.
        body: TOML text.

    Returns:
        Its path.
    """
    p = Path(tmp) / "config.toml"
    p.write_text(body, encoding="utf-8")
    return p


class Chains(unittest.TestCase):
    """Claude chain, Codex root, byte limit and trust."""

    def test_default_git_root_misses_parents(self):
        """With the default .git marker Codex loads only the repo file and the parents are reported as not loaded."""
        with tempfile.TemporaryDirectory() as tmp:
            top = tree(tmp)
            r = ac.run(top / "ws" / "repo", config(tmp, ""), None)
            self.assertEqual(len(r.claude), 3)
            self.assertEqual(r.codex_root, top / "ws" / "repo")
            self.assertTrue(any("does not load" in line for line in r.lines))

    def test_marker_root_loads_whole_chain_in_order(self):
        """A .codex-root marker at the top makes Codex load top, ws and repo, root first."""
        with tempfile.TemporaryDirectory() as tmp:
            top = tree(tmp)
            (top / ".codex-root").touch()
            r = ac.run(top / "ws" / "repo", config(tmp, 'project_root_markers = [".codex-root"]\n'), None)
            self.assertEqual([p.parent.name for p, _ in r.codex_docs], ["top", "ws", "repo"])
            self.assertFalse(any("does not load" in line for line in r.lines))

    def test_byte_limit_names_the_cut_file(self):
        """Past project_doc_max_bytes the deepest file is reported as cut."""
        with tempfile.TemporaryDirectory() as tmp:
            top = tree(tmp)
            (top / ".codex-root").touch()
            r = ac.run(top / "ws" / "repo", config(tmp, 'project_root_markers = [".codex-root"]\nproject_doc_max_bytes = 40\n'), None)
            self.assertGreater(r.errors, 0)
            self.assertTrue(any("is cut" in line or "not loaded at all" in line for line in r.lines))

    def test_missing_import_and_cycle(self):
        """An import of a missing file and an import cycle are errors."""
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp).resolve()
            (d / "AGENTS.md").write_text("@/nonexistent/AGENTS.md\n", encoding="utf-8")
            self.assertGreater(ac.run(d, config(tmp, ""), None).errors, 0)
            a, b = d / "a", d / "b"
            a.mkdir()
            b.mkdir()
            (a / "AGENTS.md").write_text(f"@{b / 'AGENTS.md'}\n", encoding="utf-8")
            (b / "AGENTS.md").write_text(f"@{a / 'AGENTS.md'}\n", encoding="utf-8")
            r = ac.run(a, config(tmp, ""), None)
            self.assertTrue(any("cycle" in line for line in r.lines))

    def test_trusted_root_spreads_trust_to_untrusted_repos(self):
        """A marker in a trusted folder that holds an untrusted repo is an error; a per-repo entry below an untrusted root is a warning."""
        with tempfile.TemporaryDirectory() as tmp:
            top = tree(tmp)
            (top / ".codex-root").touch()
            cfg = f'project_root_markers = [".codex-root"]\n[projects."{top}"]\ntrust_level = "trusted"\n'
            r = ac.run(top / "ws" / "repo", config(tmp, cfg), None)
            self.assertTrue(any("without their own trust entry" in line for line in r.lines))
            cfg2 = f'project_root_markers = [".codex-root"]\n[projects."{top / "ws" / "repo"}"]\ntrust_level = "trusted"\n'
            r2 = ac.run(top / "ws" / "repo", config(tmp, cfg2), None)
            self.assertTrue(any("no longer apply" in line for line in r2.lines))

    def test_check_exit_code(self):
        """--check exits 1 on an error and 0 on a clean chain."""
        with tempfile.TemporaryDirectory() as tmp:
            top = tree(tmp)
            self.assertEqual(ac.main(["--path", str(top / "ws" / "repo"), "--codex-config", str(config(tmp, "")), "--check"]), 0)
            (top / "AGENTS.md").unlink()
            self.assertEqual(ac.main(["--path", str(top / "ws" / "repo"), "--codex-config", str(config(tmp, "")), "--check"]), 1)


if __name__ == "__main__":
    unittest.main()
