"""Offline tests for pad_link_opener.py: which requests redirect to VS Code and which are refused. Run: python3 -m unittest test_pad_link_opener."""

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_link_opener", Path(__file__).resolve().parents[1] / "scripts" / "pad_link_opener.py")
po = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(po)


class Target(unittest.TestCase):
  """The pure request decision: redirect only for an existing path under an allowed root."""

  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.root = os.path.realpath(self.tmp.name)
    self.file = os.path.join(self.root, "a b", "x.py")
    os.makedirs(os.path.dirname(self.file))
    Path(self.file).write_text("x\n")

  def tearDown(self):
    self.tmp.cleanup()

  def req(self, link: str) -> str:
    """The request path a browser sends for a link (scheme, host and port dropped)."""
    return link.split("47800", 1)[1]

  def test_line_redirect(self):
    status, url = po.target(self.req(po.link_for(self.file, "L86", 47800)), (self.root,))
    self.assertEqual((status, url), (302, "vscode://file" + self.file.replace(" ", "%20") + ":86"))

  def test_no_line_for_heading_fragment(self):
    status, url = po.target(self.req(po.link_for(self.file, "some-heading", 47800)), (self.root,))
    self.assertEqual(status, 302)
    self.assertTrue(url.endswith("x.py"))

  def test_refused(self):
    cases = {
      "missing file": po.link_for(os.path.join(self.root, "nope.py"), "", 47800),
      "outside roots": po.link_for("/etc/hosts", "", 47800),
      "dot-dot escape": po.link_for(self.root + "/../../etc/hosts", "", 47800),
      "not /open": "http://127.0.0.1:47800/other" + self.file,
    }
    for name, link in cases.items():
      with self.subTest(name):
        self.assertEqual(po.target(self.req(link), (self.root,))[0], 404)


if __name__ == "__main__":
  unittest.main()
