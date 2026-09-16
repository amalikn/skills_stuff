#!/usr/bin/env python3
"""
commtracker/reconcile.py — Reconcile EML files in a communications/ folder
against the entries in communications-tracking.md.

Usage:
    python reconcile.py <communications-dir>

Output:
    Lists any EML files whose date slug does not appear in the tracker,
    plus a summary of date-match candidates (e.g. a Teams EML that
    corresponds to a Teams entry with the same timestamp).
"""

import argparse
import re
import sys
from datetime import datetime, timezone, timedelta
from email.parser import BytesParser
from email import policy as epolicy
from pathlib import Path


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _parse_headers(eml_path: Path) -> object:
    with open(eml_path, "rb") as f:
        # Read up to 200 lines — enough to find headers in most emails including
        # Teams notifications that have long preamble before the Date header.
        msg = BytesParser(policy=epolicy.compat32).parsebytes(
            b"".join(line for i, line in enumerate(f) if i < 200)
        )
    return msg


def parse_eml_date(eml_path: Path) -> datetime | None:
    msg = _parse_headers(eml_path)
    raw = msg.get("Date", "")
    if not raw:
        return None
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(raw)
    except Exception:
        return None


def dt_to_slug(dt: datetime) -> str:
    # Use the email's own timezone — matches extract.py behaviour.
    return dt.strftime("%Y%m%d_%H%M")


def dt_to_slug_aest(dt: datetime) -> str:
    # AEST fallback for matching entries that were historically recorded in AEST.
    try:
        aest = dt.astimezone(timezone(timedelta(hours=10)))
    except Exception:
        aest = dt
    return aest.strftime("%Y%m%d_%H%M")


def eml_subject(eml_path: Path) -> str:
    msg = _parse_headers(eml_path)
    from email.header import decode_header
    raw = msg.get("Subject", "") or ""
    parts = decode_header(raw)
    result = []
    for chunk, enc in parts:
        if isinstance(chunk, bytes):
            result.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            result.append(chunk)
    return "".join(result)


# ---------------------------------------------------------------------------
# Tracker parsing
# ---------------------------------------------------------------------------

_ENTRY_HEADING = re.compile(
    r'^## (Email|Teams)\s+(\d+)\s*[-–]\s*(\d{8}_\d{4})\s*[-–]\s*(.+)$',
    re.IGNORECASE
)


def parse_tracker(tracker_path: Path) -> list[dict]:
    entries = []
    with open(tracker_path, encoding="utf-8") as f:
        for line in f:
            m = _ENTRY_HEADING.match(line.strip())
            if m:
                entries.append({
                    "type": m.group(1).capitalize(),
                    "n": int(m.group(2)),
                    "slug": m.group(3),
                    "summary": m.group(4).strip(),
                })
    return entries


# ---------------------------------------------------------------------------
# Reconcile
# ---------------------------------------------------------------------------

def reconcile(comms_dir: str) -> None:
    comms_path = Path(comms_dir).resolve()
    if not comms_path.is_dir():
        print(f"ERROR: not a directory: {comms_path}", file=sys.stderr)
        sys.exit(1)

    tracker_path = comms_path / "communications-tracking.md"
    eml_files = sorted(comms_path.glob("*.eml"))

    if not eml_files:
        print("No .eml files found.")
        return

    # Load tracker
    entries = []
    if tracker_path.exists():
        entries = parse_tracker(tracker_path)
        slugs_in_tracker = {e["slug"] for e in entries}
        last = entries[-1] if entries else None
        last_str = f"{last['type']} {last['n']} - {last['slug']}" if last else "none"
        print(f"Tracker: {tracker_path.name} ({len(entries)} entries, last: {last_str})")
    else:
        slugs_in_tracker = set()
        print(f"Tracker: not found ({tracker_path.name})")

    print()

    untracked = []
    date_matched = []

    for eml in eml_files:
        dt = parse_eml_date(eml)
        slug = dt_to_slug(dt) if dt else None
        slug_aest = dt_to_slug_aest(dt) if dt else None
        subject = eml_subject(eml)
        raw_date = dt.strftime("%a, %d %b %Y %H:%M:%S %z") if dt else "unknown"

        # Try matching with both the email's own timezone and AEST (for historically
        # captured entries that used AEST conversion).
        matched_slug = None
        if slug and slug in slugs_in_tracker:
            matched_slug = slug
        elif slug_aest and slug_aest in slugs_in_tracker:
            matched_slug = slug_aest

        if matched_slug:
            matched_entry = next((e for e in entries if e["slug"] == matched_slug), None)
            entry_str = f"{matched_entry['type']} {matched_entry['n']} - {matched_slug}" if matched_entry else matched_slug
            tz_note = " (AEST match)" if matched_slug == slug_aest and matched_slug != slug else ""
            print(f"  ✓ {eml.name}")
            print(f"      Slug {matched_slug}{tz_note} → matched {entry_str}")
        else:
            # Check for same-date candidate across both slug variants
            close_match = None
            for check_slug in filter(None, [slug, slug_aest]):
                for e in entries:
                    if e["slug"][:8] == check_slug[:8]:
                        close_match = e
                        break
                if close_match:
                    break

            if close_match:
                date_matched.append({
                    "file": eml.name,
                    "date": raw_date,
                    "slug": slug,
                    "slug_aest": slug_aest,
                    "subject": subject,
                    "close_match": close_match,
                })
            else:
                untracked.append({
                    "file": eml.name,
                    "date": raw_date,
                    "slug": slug,
                    "subject": subject,
                })

    if date_matched:
        print(f"\nDATE-MATCHED ({len(date_matched)}) — same date, slug not exact:")
        for item in date_matched:
            print(f"  {item['file']}")
            slug_display = item['slug'] or 'no date'
            if item.get('slug_aest') and item['slug_aest'] != item['slug']:
                slug_display += f" / {item['slug_aest']} AEST"
            print(f"    Date:    {item['date']} → {slug_display}")
            print(f"    Subject: {item['subject']}")
            entry = item['close_match']
            print(f"    → Possible match: {entry['type']} {entry['n']} - {entry['slug']} — {entry['summary']}")

    if untracked:
        print(f"\nUNTRACKED ({len(untracked)}):")
        for item in untracked:
            print(f"  {item['file']}")
            print(f"    Date:    {item['date']} → {item['slug'] or 'no date'}")
            print(f"    Subject: {item['subject']}")
    else:
        if not date_matched:
            print("\nALL EML FILES ACCOUNTED FOR")
        else:
            print("\nAll unambiguous EML files accounted for. Review date-matched items above.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Reconcile EML files against tracker.")
    parser.add_argument("comms_dir", help="Path to communications/ directory")
    args = parser.parse_args()
    reconcile(args.comms_dir)


if __name__ == "__main__":
    main()
