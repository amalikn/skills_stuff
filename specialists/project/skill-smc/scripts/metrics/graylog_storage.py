#!/usr/bin/env python3
"""Read-only Graylog storage report: index sets and retention, per-index sizes, ingest rate, disk needed, journal and notifications.

Built from the 2026-11-27 apn-datanode01 flood-stage incident (references/13_known-issues.md): retention keeps an index for
`index_lifetime_min` after it closes, so the disk must hold (min lifetime + rotation interval) x daily volume.

Run:   python3 scripts/metrics/graylog_storage.py [--top] [--headroom 0.80]
       just graylog_storage --top
Needs: `tsh --proxy=teleport.apn.au apps login apn-graylog` and the token used by smc_graylog.py. Nothing is changed.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DUR = re.compile(r"^P(?:(\d+)D)?$")


def iso_days(duration):
  """Turn an ISO-8601 day duration such as 'P60D' into a number of days.

  Args:
    duration: the duration string Graylog stores (only whole days are used by its tiering config).

  Returns:
    The number of days as an int, or None when the string is empty or not a day duration.
  """
  m = DUR.match(duration or "")
  return int(m.group(1)) if m and m.group(1) else None


def index_number(name):
  """Return the trailing number of an index name ('graylog_68' -> 68), or -1 when it has none.

  Args:
    name: the OpenSearch index name.

  Returns:
    The integer suffix, used to sort indices in rotation order.
  """
  tail = name.rsplit("_", 1)[-1]
  return int(tail) if tail.isdigit() else -1


def daily_rate(indices):
  """Estimate the ingest rate from closed indices: total bytes over the days between the first and last close.

  Args:
    indices: list of dicts with 'bytes' (int) and 'end' (datetime or None, the index range end), the write index excluded.

  Returns:
    (bytes_per_day, rotation_days): average bytes per day and average days between rotations, or (None, None) with fewer
    than three dated indices.
  """
  dated = sorted((i for i in indices if i["end"]), key=lambda i: i["end"])
  if len(dated) < 3:
    return None, None
  span = (dated[-1]["end"] - dated[0]["end"]).total_seconds() / 86400
  if span <= 0:
    return None, None
  return sum(i["bytes"] for i in dated[1:]) / span, span / (len(dated) - 1)


def disk_needed(bytes_per_day, min_days, rotation_days, headroom):
  """Disk an index set needs to hold its retention below a usage ceiling.

  Args:
    bytes_per_day: ingest rate.
    min_days: index_lifetime_min in days (an index is deleted only this long after it closes).
    rotation_days: days one index stays the write index.
    headroom: the usage ceiling to stay under, e.g. 0.80 (below OpenSearch's 85% low watermark).

  Returns:
    Bytes of disk needed.

  Raises:
    ValueError: when headroom is not between 0 and 1.
  """
  if not 0 < headroom <= 1:
    raise ValueError("headroom must be in (0, 1]")
  return (min_days + rotation_days) * bytes_per_day / headroom


def parse_end(rng):
  """Parse an index range end; Graylog writes 1970-01-01 for a range not yet calculated.

  Args:
    rng: the 'range' dict from /system/indexer/overview, or None.

  Returns:
    A timezone-aware datetime, or None for a missing or epoch range.
  """
  end = (rng or {}).get("end") or ""
  if not end or end.startswith("1970"):
    return None
  return datetime.fromisoformat(end.replace("Z", "+00:00")).astimezone(timezone.utc)


def main():
  """Print the report.

  Returns:
    0 always (a report, not a gate).
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--top", action="store_true", help="also list the top paths and sources over the last 10 days")
  ap.add_argument("--headroom", type=float, default=0.80, help="disk usage ceiling for the sizing line (default 0.80)")
  a = ap.parse_args()
  import smc_graylog as g  # imported here so the pure functions above test offline

  sets = g._curl([f"{g.API}/system/indices/index_sets?stats=true"])
  ov = g._curl([f"{g.API}/system/indexer/overview"])
  by_prefix = {}
  for i in ov.get("indices", []):
    by_prefix.setdefault(i["index_name"].rsplit("_", 1)[0], []).append(i)
  for s in sets["index_sets"]:
    tier = s.get("data_tiering") or {}
    mn, mx = iso_days(tier.get("index_lifetime_min")), iso_days(tier.get("index_lifetime_max"))
    st = sets.get("stats", {}).get(s["id"], {})
    print(
      f"SET {s['title']} prefix={s['index_prefix']} tiering={tier.get('type')} min={mn}d max={mx}d "
      f"indices={st.get('indices')} size={st.get('size', 0) / 1e9:.1f} GB"
    )
    rows = sorted(by_prefix.get(s["index_prefix"], []), key=lambda i: index_number(i["index_name"]))
    closed = []
    for i in rows:
      end = parse_end(i.get("range"))
      print(
        f"  {i['index_name']:24s} {i['size']['bytes'] / 1e9:7.1f} GB {i['size']['events']:>13,d} ev "
        f"end={end.date() if end else '-'}{' WRITE' if i.get('is_deflector') else ''}"
      )
      if not i.get("is_deflector"):
        closed.append({"bytes": i["size"]["bytes"], "end": end})
    rate, rot = daily_rate(closed)
    if rate and mn:
      print(
        f"  ingest about {rate / 1e9:.1f} GB/day, rotation every {rot:.1f} d; disk needed for min={mn}d at "
        f"{a.headroom:.0%}: {disk_needed(rate, mn, rot, a.headroom) / 1e9:.0f} GB"
      )
  j = g._curl([f"{g.API}/system/journal"])
  print(
    f"JOURNAL uncommitted={j['uncommitted_journal_entries']:,} size={j['journal_size'] / 1e9:.2f}/"
    f"{j['journal_size_limit'] / 1e9:.2f} GB read/s={j['read_events_per_second']} append/s={j['append_events_per_second']} "
    f"oldest={j.get('oldest_segment')} max_age={j['journal_config']['max_age'] / 3.6e6:.0f} h"
  )
  n = g._curl([f"{g.API}/system/notifications"])
  print("NOTIFICATIONS", ", ".join(x.get("type", "?") for x in n.get("notifications", [])) or "none")
  if a.top:
    for field in ("path", "source"):
      r = g.aggregate("*", 10 * 86400, field=field)
      rows = sorted(r["datarows"], key=lambda x: -x[1])
      tot = sum(x[1] for x in rows) or 1
      print(f"TOP {field} (10 days, {tot:,} messages)")
      for x in rows[:10]:
        print(f"  {str(x[0])[:50]:50s} {x[1]:>12,d} {100 * x[1] / tot:5.1f}%")
  return 0


if __name__ == "__main__":
  sys.exit(main())
