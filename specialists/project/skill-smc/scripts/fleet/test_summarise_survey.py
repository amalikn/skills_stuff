"""Offline tests of summarise_survey.py on canned probe and census output (the parsing bugs of 2026-11-10 among them).

Run: python3 -m unittest discover -s scripts/fleet -p 'test_*.py' (stdlib only; reads nothing outside its temporary folder).
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
ss = importlib.import_module("summarise_survey")

X86 = """== box-a (proxy)
dmi_model=BOXER-6641 bios=B641HM20 bios_date=09/19/2024
disk=sda 119.2G TS128GSSD472K
root=/dev/sda2,ext4 root_use=13%
watchdog_dev=
watchdog_drivers=f71808e_wdt.ko iTCO_vendor_support.ko iTCO_wdt.ko
os=Ubuntu 22.04.3 LTS codename=jammy rauc=
uptime_s=86400
io=sda,sectors_written=2000000,sectors_read=1
"""
PI = """== pi-a (proxy)
model=Raspberry Pi 4 Model B Rev 1.5 mem_mb=7807
os=Ubuntu 22.04.1 LTS codename=jammy kernel=5.15.0-1078-raspi rauc=
uptime_s=86400
io=mmcblk0,sectors_written=20000,sectors_read=1
"""


class Parse(unittest.TestCase):
  """Blocks to rows."""

  def test_os_name_with_spaces(self) -> None:
    """The OS name keeps its spaces (it was cut to 'Ubuntu')."""
    d = ss.kv(ss.blocks(X86)[0][1])
    self.assertEqual(ss.first(d, "os"), "Ubuntu 22.04.3 LTS")

  def test_itco_found_in_driver_list(self) -> None:
    """iTCO_wdt is found anywhere in the space-separated driver list (only the first name was read)."""
    row = ss.x86_row("rcp", "box-a", ss.kv(ss.blocks(X86)[0][1]))
    self.assertEqual(row["itco_driver"], "yes")
    self.assertEqual(row["gb_written_per_day"], "1.0")

  def test_pi_rate_in_megabytes(self) -> None:
    """A Pi writing about 10 MB a day reports 10.2 MB/day, not 0.0 GB/day."""
    row = ss.pi_row("rct", "pi-a", ss.kv(ss.blocks(PI)[0][1]))
    self.assertEqual(row["mb_written_per_day"], "10.2")

  def test_census_tally(self) -> None:
    """The census tally counts bootloaders, board revisions, undervoltage and silent boxes."""
    text = ("rct a bootloader=2023-01-11 model=Raspberry_Pi_4_Model_B_Rev_1.5 throttled=0x50005\n"
            "rct b bootloader=2022-01-25 model=Raspberry_Pi_4_Model_B_Rev_1.4 throttled=0x0\n"
            "rct c unreachable rc=124\n")
    out = ss.census(text)
    self.assertIn("| rct | 2022-01-25 | 1 |", out)
    self.assertIn("2022-01-25 rev 1.4 x1", out)
    self.assertIn("now: a", out)
    self.assertIn("did not answer (1): c", out)


if __name__ == "__main__":
  unittest.main()
