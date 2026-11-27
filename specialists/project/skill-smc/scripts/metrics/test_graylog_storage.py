#!/usr/bin/env python3
"""Offline test for graylog_storage.py's pure functions (no Graylog access). Run: python3 scripts/metrics/test_graylog_storage.py"""

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graylog_storage as gs


class GraylogStorageTest(unittest.TestCase):
  """Checks the duration parser, rate estimate and disk sizing against the 2026-11-27 incident figures."""

  def test_iso_days(self):
    """P60D is 60 days; anything else is None."""
    self.assertEqual(gs.iso_days("P60D"), 60)
    self.assertIsNone(gs.iso_days("PT12H"))
    self.assertIsNone(gs.iso_days(None))

  def test_parse_end_epoch_is_none(self):
    """An uncalculated range (1970) gives None; a real one parses as UTC."""
    self.assertIsNone(gs.parse_end({"end": "1970-01-01T00:00:00.000Z"}))
    self.assertEqual(gs.parse_end({"end": "2026-10-07T15:40:00.000Z"}).day, 7)

  def test_rate_and_sizing_match_incident(self):
    """Fourteen 19.5 GB indices closing every 3.5 days give about 5.6 GB/day and need about 450 GB at 80% for 60 days."""
    t0 = datetime(2026, 10, 7, tzinfo=timezone.utc)
    idx = [{"bytes": 19.5e9, "end": t0 + timedelta(days=3.5 * k)} for k in range(14)]
    rate, rot = gs.daily_rate(idx)
    self.assertAlmostEqual(rate / 1e9, 5.57, places=1)
    self.assertAlmostEqual(rot, 3.5)
    need = gs.disk_needed(rate, 60, rot, 0.80) / 1e9
    self.assertTrue(440 < need < 460, need)

  def test_rate_needs_three_indices(self):
    """Fewer than three dated indices give no estimate."""
    self.assertEqual(gs.daily_rate([{"bytes": 1, "end": None}]), (None, None))

  def test_headroom_bounds(self):
    """A headroom outside (0, 1] is refused."""
    with self.assertRaises(ValueError):
      gs.disk_needed(1, 1, 1, 0)

  def test_index_number(self):
    """Index names sort by their numeric suffix."""
    self.assertEqual(gs.index_number("graylog_68"), 68)
    self.assertEqual(gs.index_number("gl-events"), -1)


if __name__ == "__main__":
  unittest.main()
