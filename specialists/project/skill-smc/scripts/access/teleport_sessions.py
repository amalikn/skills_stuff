#!/usr/bin/env python3
"""List who had Teleport sessions on given SMC hosts over a date range, from the cluster's session recordings (read-only).

Answers "who was on this box, when" for an incident window: per-session rows (local start, user, host, minutes, interactive)
and an hourly count per user and host. Queries one UTC day at a time because a busy bot (bot-cw-dashboard opens thousands of
exec sessions a day) fills any single wider listing and hides human sessions. Uses the logged-in `tsh` profile; needs the
auditor role on the named proxy.

Usage:
    teleport_sessions.py --proxy teleport.communitywifi.net.au --from 2026-08-31 --to 2026-09-06 \
        --host hope-vale --host kowanyama [--exclude-user bot-cw-dashboard] [--tz Australia/Brisbane] [--summary]

Origin: 2026-10-15 three-site PIN outage (references/13_known-issues.md, 2026-09-11 entry, update 2026-10-15 later).
"""
import argparse
import collections
import datetime as dt
import json
import subprocess
import sys
from zoneinfo import ZoneInfo


def day_sessions(proxy, day):
    """Fetch the recordings for one UTC day.

    Args:
        proxy: Teleport proxy host, e.g. teleport.communitywifi.net.au.
        day: datetime.date, the UTC day to list.

    Returns:
        A list of recording dicts as printed by `tsh recordings ls --format=json`.

    Raises:
        RuntimeError: when tsh fails or prints something other than JSON.
    """
    nxt = day + dt.timedelta(days=1)
    cmd = ["tsh", f"--proxy={proxy}", "recordings", "ls", f"--from-utc={day}", f"--to-utc={nxt}",
           "--limit=20000", "--format=json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"tsh failed for {day}: {res.stderr.strip()[:300]}")
    try:
        return json.loads(res.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"tsh output for {day} is not JSON: {res.stdout[:200]}") from exc


def parse_args(argv):
    """Parse the command line.

    Args:
        argv: argument list without the program name.

    Returns:
        argparse.Namespace with proxy, start, end, hosts, exclude, tz and summary.
    """
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--proxy", required=True)
    p.add_argument("--from", dest="start", required=True, type=dt.date.fromisoformat, help="first UTC day, YYYY-MM-DD")
    p.add_argument("--to", dest="end", required=True, type=dt.date.fromisoformat, help="last UTC day, inclusive")
    p.add_argument("--host", dest="hosts", action="append", default=[], help="substring of server_hostname; repeatable")
    p.add_argument("--exclude-user", dest="exclude", action="append", default=[], help="repeatable")
    p.add_argument("--tz", default="Australia/Brisbane", help="zone for printed times (default AEST, no DST)")
    p.add_argument("--summary", action="store_true", help="print only the hourly counts")
    return p.parse_args(argv)


def main(argv):
    """Run the listing and print rows and the hourly summary.

    Args:
        argv: argument list without the program name.

    Returns:
        0 when every day was read, 1 when any day failed.
    """
    a = parse_args(argv)
    tz = ZoneInfo(a.tz)
    rows, failed = [], False
    day = a.start
    while day <= a.end:
        try:
            for e in day_sessions(a.proxy, day):
                host, user = e.get("server_hostname", ""), e.get("user", "")
                if user in a.exclude or (a.hosts and not any(h in host for h in a.hosts)):
                    continue
                start = dt.datetime.fromisoformat(e["session_start"].replace("Z", "+00:00"))
                stop = dt.datetime.fromisoformat(e.get("session_stop", e["session_start"]).replace("Z", "+00:00"))
                rows.append((start.astimezone(tz), user, host, round((stop - start).total_seconds() / 60, 1),
                             e.get("interactive"), e.get("sid", "")))
        except RuntimeError as exc:
            print(f"# {exc}", file=sys.stderr)
            failed = True
        day += dt.timedelta(days=1)
    rows.sort()
    if not a.summary:
        print(f"# start ({a.tz})\tuser\thost\tminutes\tinteractive\tsid")
        for r in rows:
            print(f"{r[0]:%Y-%m-%d %H:%M:%S}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}\t{r[5]}")
    print(f"# hourly sessions ({a.tz}): hour, user, host, count")
    for (hour, user, host), n in sorted(collections.Counter((f"{r[0]:%Y-%m-%d %H}", r[1], r[2]) for r in rows).items()):
        print(f"{hour}\t{user}\t{host}\t{n}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
