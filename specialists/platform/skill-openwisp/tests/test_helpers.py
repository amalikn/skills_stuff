"""Offline tests for the promoted helpers in scripts/: identity and time conversions, and the read-only probe on recorded output."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
_identity = importlib.import_module("openwisp_identity")
OpenWispProbe = importlib.import_module("openwisp_probe").OpenWispProbe
backfill_time, device_name, from_hardware_id = _identity.backfill_time, _identity.device_name, _identity.from_hardware_id
normalise_mac, to_hardware_id = _identity.normalise_mac, _identity.to_hardware_id


class Identity(unittest.TestCase):
    UUID = "11111111-2222-3333-4444-555555555555"

    def test_hardware_id_round_trip_fits_32(self):
        hw = to_hardware_id(self.UUID)
        self.assertEqual(hw, "11111111222233334444555555555555")
        self.assertEqual(len(hw), 32)
        self.assertEqual(from_hardware_id(hw), self.UUID)

    def test_bad_hardware_id_rejected(self):
        for bad in ("", "xyz", self.UUID, "1" * 31):
            with self.assertRaises(ValueError):
                from_hardware_id(bad)

    def test_mac_notations_normalise(self):
        for raw in ("AA-BB-CC-DD-EE-0F", "aabb.ccdd.ee0f", "AA:BB:CC:DD:EE:0F"):
            self.assertEqual(normalise_mac(raw), "aa:bb:cc:dd:ee:0f")
        self.assertIsNone(normalise_mac("aa:bb"))
        self.assertIsNone(normalise_mac(None))

    def test_device_name_made_valid(self):
        self.assertEqual(device_name("SITE_AP 01__x"), "SITE-AP-01-x")
        self.assertEqual(device_name("a_.b"), "a.b")
        with self.assertRaises(ValueError):
            device_name("___")
        with self.assertRaises(ValueError):
            device_name("x" * 64)

    def test_backfill_time_is_utc_and_rejects_naive(self):
        local = datetime(2026, 10, 5, 11, 30, tzinfo=timezone(timedelta(hours=10)))
        self.assertEqual(backfill_time(local), "05-10-2026_01:30:00.000000")
        with self.assertRaises(ValueError):
            backfill_time(datetime(2026, 10, 5, 1, 30))


def recorded(stdout: str):
    return lambda cmd: subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr="")


class Probe(unittest.TestCase):
    def test_workers_counts_replying_nodes(self):
        five = json.dumps({f"{n}@host": {"ok": "pong"} for n in ("celery", "network", "firmware_upgrader", "monitoring", "monitoring_checks")})
        self.assertTrue(OpenWispProbe(recorded(five)).workers("c").healthy)
        none = OpenWispProbe(recorded("Error: No nodes replied within time constraint\n")).workers("c")
        self.assertFalse(none.healthy)
        self.assertIn("none replied", none.detail)

    def test_freshness_flags_old_point(self):
        out = json.dumps({"results": [{"series": [{"columns": ["time", "reachable"], "values": [["2026-09-28T07:34:45Z", 1]]}]}]})
        now = datetime(2026, 10, 5, 7, 34, 45, tzinfo=timezone.utc)
        stale = OpenWispProbe(recorded(out)).freshness("i", now=now)
        self.assertFalse(stale.healthy)
        self.assertEqual(stale.data["age"], 7 * 86400)
        self.assertTrue(OpenWispProbe(recorded(out)).freshness("i", now=now - timedelta(days=7) + timedelta(minutes=5)).healthy)
        self.assertFalse(OpenWispProbe(recorded("")).freshness("i").healthy)

    def test_settings_compares_and_hides_secret_values(self):
        out = "PROBE " + json.dumps({"A": True, "B": "__UNSET__", "SECRET_KEY": "real"})
        f = OpenWispProbe(recorded(out)).settings(["c1"], {"A": True, "B": 1, "SECRET_KEY": "other"})
        self.assertFalse(f.healthy)
        self.assertIn("B = '__UNSET__'", f.detail)
        self.assertIn("SECRET_KEY = <differs>", f.detail)
        self.assertNotIn("real", f.detail)


if __name__ == "__main__":
    unittest.main()
