"""Offline tests for pad_toml_probe.py with fake pad binaries: the known 0.19.2 behaviour passes, a pad that drops tables or writes other
files fails. Run: just test."""

import importlib.util
import os
import stat
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "pad_toml_probe",
    Path(__file__).resolve().parents[1] / "scripts" / "pad_toml_probe.py",
)
ptp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ptp)

# A fake `pad workspace switch <slug>` behaving like 0.19.2: rewrites .pad.toml without comments, keeps other tables.
KNOWN = r"""#!/usr/bin/env python3
import sys, tomllib, pathlib
p = pathlib.Path(".pad.toml"); d = tomllib.loads(p.read_text()); d["workspace"] = sys.argv[3]
lines = [f'workspace = "{d.pop("workspace")}"']
for name, table in d.items():
    lines.append(f"[{name}]"); lines += [f"  {k} = {str(v).lower()}" for k, v in table.items()]
p.write_text("\n".join(lines) + "\n")
"""
DROPS_TABLES = r"""#!/usr/bin/env python3
import sys, pathlib
pathlib.Path(".pad.toml").write_text(f'workspace = "{sys.argv[3]}"\n')
"""
WRITES_OTHER = KNOWN + 'pathlib.Path("tracker-map.toml").write_text("overwritten\\n")\n'


def fake(body: str) -> str:
    """Write an executable fake pad and return its path.

    Args:
        body: the script.
    Returns:
        Path of the executable.
    """
    d = tempfile.mkdtemp()
    path = Path(d) / "pad"
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return str(path)


class Probe(unittest.TestCase):
    """probe() reports only real differences from the known behaviour."""

    def test_known_behaviour_passes(self):
        self.assertEqual(ptp.probe("a", "b", pad=fake(KNOWN)), [])

    def test_dropped_table_fails(self):
        self.assertIn(
            "an unknown table was dropped or changed ([probe] kept = true)",
            ptp.probe("a", "b", pad=fake(DROPS_TABLES)),
        )

    def test_other_file_written_fails(self):
        self.assertTrue(
            any(
                "tracker-map.toml" in d
                for d in ptp.probe("a", "b", pad=fake(WRITES_OTHER))
            )
        )

    def test_missing_pad_exits_2(self):
        self.assertEqual(
            ptp.main(["a", "b", "--pad", os.path.join(tempfile.mkdtemp(), "nopad")]), 2
        )


if __name__ == "__main__":
    unittest.main()
