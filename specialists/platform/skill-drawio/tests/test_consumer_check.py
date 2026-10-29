"""Offline tests for scripts/consumer_check.py ("consumer_check"): the registry, look parsing, and a render that never writes a consumer's own
drawing (the example shop stands in for a consumer).

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
consumer_check = importlib.import_module("consumer_check")


class ConsumerCheck(unittest.TestCase):
    """scripts/consumer_check.py."""

    def _registry(self, folder: Path) -> Path:
        """A registry holding only the example shop.

        Args:
            folder: where to write it.

        Returns:
            Its path.
        """
        reg = folder / "consumers.yaml"
        reg.write_text("consumers:\n  - {name: shop, root: examples/shop, map: flows.yaml, schema: ''}\n", encoding="utf-8")
        return reg

    def test_registry_lists_the_example_with_an_absolute_root(self) -> None:
        """The skill's own registry has the example; a relative root is the skill's."""
        shop = [c for c in consumer_check.consumers() if c["name"] == "example-shop"]
        self.assertEqual(shop[0]["root"], str(ROOT / "examples" / "shop"))

    def test_looks_parse_json_or_text(self) -> None:
        """A JSON value is decoded, anything else kept as text; a pair without '=' is refused."""
        self.assertEqual(consumer_check.parse_looks(["a=true", "b=12", "c=sub"]), {"a": True, "b": 12, "c": "sub"})
        with self.assertRaises(ValueError):
            consumer_check.parse_looks(["oops"])

    def test_render_and_compare_identical_then_refuse_own_drawing(self) -> None:
        """Two renders of the example compare identical (exit 0); writing over the example's own drawing is refused."""
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            reg = self._registry(t)
            self.assertEqual(consumer_check.main(["--out", str(t / "a"), "--registry", str(reg)]), 0)
            self.assertEqual(consumer_check.main(["--out", str(t / "b"), "--registry", str(reg), "--compare", str(t / "a")]), 0)
            own = ROOT / "examples" / "shop" / "drawio"
            before = (own / "flows.drawio").read_bytes()
            with self.assertRaises(RuntimeError):
                consumer_check.render_one(ROOT / "scripts", consumer_check.consumers(reg)[0], own / "flows.drawio", {})
            self.assertEqual((own / "flows.drawio").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
