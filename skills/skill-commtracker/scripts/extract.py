#!/usr/bin/env python3
"""
commtracker/extract.py — Parse one EML, extract headers + body + MIME parts.

Saves attachments to disk and outputs a JSON summary to stdout.
Claude reads the JSON; no raw EML bytes enter the context window.

Usage:
    python extract.py <eml-path>
        [--attachments-dir <dir>]    default: <eml-dir>/attachments/
        [--internal-domain <domain>] e.g. apn.net.au — marks external senders
        [--slug <YYYYMMDD_HHMM>]     override timestamp slug for file naming
        [--save-signatures]          include Outlook/Teams UI chrome images (default: skip)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from email import policy as epolicy
from email.header import decode_header
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path


# ---------------------------------------------------------------------------
# Signature image detection
# ---------------------------------------------------------------------------

_OUTLOOK_CHROME = re.compile(r'^Outlook-[a-z0-9]{8}\.(png|gif|jpg)$', re.IGNORECASE)
_UUID_FILENAME  = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.(png|gif|jpg)$',
    re.IGNORECASE
)
_SPACER_MAX_BYTES = 200


def is_signature_image(filename: str, size: int) -> bool:
    if _OUTLOOK_CHROME.match(filename):
        return True
    if _UUID_FILENAME.match(filename):
        return True
    if size <= _SPACER_MAX_BYTES:
        return True
    return False


# ---------------------------------------------------------------------------
# Disclaimer / signature stripping
# ---------------------------------------------------------------------------

_DISCLAIMER_PREFIXES = (
    "DISCLAIMER",
    "CONFIDENTIAL",
    "This email and any files transmitted",
    "This message contains confidential",
    "NOTICE: This email message",
    "IMPORTANT: The contents of this email",
)

_PHONE_LINE = re.compile(r'^\s*(Tel|Ph|Fax|Mobile|T:|F:|M:)\s*[\d\s\+\(\)\-\.]+$', re.IGNORECASE)


def strip_boilerplate(text: str) -> str:
    lines = text.splitlines()
    out = []
    in_disclaimer = False
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(p) for p in _DISCLAIMER_PREFIXES):
            in_disclaimer = True
        if in_disclaimer:
            continue
        out.append(line)

    # Collapse 3+ blank lines to 2
    result = []
    blank_run = 0
    for line in out:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                result.append(line)
        else:
            blank_run = 0
            result.append(line)

    return "\n".join(result).strip()


# ---------------------------------------------------------------------------
# HTML → plain text
# ---------------------------------------------------------------------------

class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self._skip = True
        if tag in ("br", "p", "div", "tr", "li"):
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def get_text(self):
        return "".join(self._parts)


def html_to_text(html: str) -> str:
    s = _HTMLStripper()
    s.feed(html)
    text = s.get_text()
    # Collapse excess blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Header helpers
# ---------------------------------------------------------------------------

def decode_str(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    result = []
    for chunk, enc in parts:
        if isinstance(chunk, bytes):
            result.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            result.append(chunk)
    return "".join(result)


_EMAIL_ADDR = re.compile(r'<([^>]+)>')
_DISPLAY    = re.compile(r'^([^<]+?)\s*<')


def parse_address(raw: str, internal_domain: str | None) -> dict:
    raw = decode_str(raw).strip()
    addr_match = _EMAIL_ADDR.search(raw)
    disp_match = _DISPLAY.match(raw)
    addr = addr_match.group(1).lower() if addr_match else raw.lower()
    name = disp_match.group(1).strip().strip('"') if disp_match else raw
    if not name:
        name = addr
    external = False
    if internal_domain and addr:
        domain = addr.split("@")[-1] if "@" in addr else ""
        external = domain.lower() != internal_domain.lower()
    return {"name": name, "external": external}


def parse_address_list(raw: str, internal_domain: str | None) -> list[dict]:
    if not raw:
        return []
    # Split on comma but not inside quotes
    parts = re.split(r',\s*(?=[^"]*(?:"[^"]*"[^"]*)*$)', raw)
    return [parse_address(p.strip(), internal_domain) for p in parts if p.strip()]


def format_date_human(dt: datetime) -> str:
    return dt.strftime("%A, %d %B %Y %I:%M %p %Z").replace(" 0", " ")


def parse_date(raw: str) -> datetime | None:
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(raw)
    except Exception:
        return None


def date_to_slug(dt: datetime) -> str:
    # Use the email's own timezone offset — matches what the sender's client shows.
    # Pass --slug to override if a different timezone is needed.
    return dt.strftime("%Y%m%d_%H%M")


# ---------------------------------------------------------------------------
# Filename helpers
# ---------------------------------------------------------------------------

def safe_filename(name: str) -> str:
    name = name.replace(" ", "-")
    name = re.sub(r'[^\w\.\-]', '_', name)
    return name


def unique_path(dir_path: Path, filename: str) -> Path:
    candidate = dir_path / filename
    if not candidate.exists():
        return candidate
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    n = 2
    while True:
        candidate = dir_path / f"{stem}-{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract(
    eml_path: str,
    attachments_dir: str | None = None,
    internal_domain: str | None = None,
    slug_override: str | None = None,
    save_signatures: bool = False,
) -> dict:
    eml_path = Path(eml_path)
    if not eml_path.exists():
        raise FileNotFoundError(f"EML not found: {eml_path}")

    with open(eml_path, "rb") as f:
        msg = BytesParser(policy=epolicy.compat32).parse(f)

    # --- Headers ---
    raw_date = msg.get("Date", "")
    dt = parse_date(raw_date)
    slug = slug_override or (date_to_slug(dt) if dt else "00000000_0000")
    date_human = format_date_human(dt) if dt else raw_date
    date_iso = dt.isoformat() if dt else raw_date

    from_parsed = parse_address(msg.get("From", ""), internal_domain)
    to_parsed = parse_address_list(msg.get("To", ""), internal_domain)
    cc_parsed = parse_address_list(msg.get("Cc", ""), internal_domain)
    subject = decode_str(msg.get("Subject", ""))

    # --- Body ---
    body_text = ""
    body_html = ""
    for part in msg.walk():
        ct = part.get_content_type()
        if part.is_multipart():
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        if ct == "text/plain" and not body_text:
            body_text = text
        elif ct == "text/html" and not body_html:
            body_html = text

    raw_body = body_text if body_text else html_to_text(body_html)
    body = strip_boilerplate(raw_body)

    # --- Attachments ---
    att_dir = None
    if attachments_dir:
        att_dir = Path(attachments_dir)
    else:
        att_dir = eml_path.parent / "attachments"

    attachments = []
    sig_skipped = 0
    inline_counter = 0
    eml_counter = 0  # sequence counter for .eml attachments (forwarded chain)

    for part in msg.walk():
        ct = part.get_content_type()
        cd = part.get("Content-Disposition", "") or ""
        cid_raw = part.get("Content-ID", "") or ""

        is_attachment = "attachment" in cd.lower()
        is_image = ct.startswith("image/") or ct.startswith("image")
        if part.is_multipart():
            continue
        if ct in ("text/plain", "text/html", "text/calendar"):
            continue
        if not (is_attachment or is_image):
            continue

        payload = part.get_payload(decode=True)
        if not payload:
            continue

        fname = part.get_filename()
        if not fname:
            ext = ct.split("/")[-1].split(";")[0].strip()
            inline_counter += 1
            fname = f"inline-image-{inline_counter}.{ext}"
        else:
            from email.header import decode_header as dh
            decoded = dh(fname)
            fname = "".join(
                chunk.decode(enc or "utf-8") if isinstance(chunk, bytes) else chunk
                for chunk, enc in decoded
            )

        cid = cid_raw.strip("<>")
        size = len(payload)
        sig = is_image and is_signature_image(fname, size)

        if sig and not save_signatures:
            sig_skipped += 1
            continue

        att_dir.mkdir(parents=True, exist_ok=True)
        safe_name = safe_filename(fname)

        # Sequence-number .eml attachments so the order of the forwarded chain is clear
        if fname.lower().endswith('.eml'):
            eml_counter += 1
            out_name = f"{slug}-{eml_counter:02d}-{safe_name}"
        else:
            out_name = f"{slug}-{safe_name}"

        out_path = unique_path(att_dir, out_name)
        with open(out_path, "wb") as fout:
            fout.write(payload)

        attachments.append({
            "original_filename": fname,
            "saved_filename": out_path.name,
            "saved_path": str(out_path),
            "content_type": ct,
            "size_bytes": size,
            "cid": cid or None,
            "is_image": is_image,
            "is_signature": sig,
        })

    return {
        "date_iso": date_iso,
        "date_human": date_human,
        "slug": slug,
        "from": from_parsed["name"],
        "from_external": from_parsed["external"],
        "to": to_parsed,
        "cc": cc_parsed,
        "subject": subject,
        "body_text": body,
        "attachments": attachments,
        "signature_images_skipped": sig_skipped,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract EML content to JSON.")
    parser.add_argument("eml", help="Path to .eml file")
    parser.add_argument("--attachments-dir", help="Directory to save attachments")
    parser.add_argument("--internal-domain", help="Domain considered internal (others marked external)")
    parser.add_argument("--slug", help="Override timestamp slug for file naming")
    parser.add_argument("--save-signatures", action="store_true",
                        help="Save Outlook/Teams signature chrome images (default: skip)")
    args = parser.parse_args()

    try:
        result = extract(
            eml_path=args.eml,
            attachments_dir=args.attachments_dir,
            internal_domain=args.internal_domain,
            slug_override=args.slug,
            save_signatures=args.save_signatures,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
