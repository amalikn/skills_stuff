#!/usr/bin/env python3
"""Fetch a Confluence page (help.mikrotik.com) by id and save as plain text, through the REST API (the HTML pages need JavaScript).

Usage: confluence_fetch.py <page_id> <out.txt> [base_url]
"""
import datetime
import html
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser

BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "table", "ul", "ol"}


class Txt(HTMLParser):
    """Confluence `body.view` HTML to readable text: block tags become lines, headings `#`, list items `-`, table cells ` | `; scripts and styles
    are dropped."""

    def __init__(self):
        """Start with an empty output buffer, outside any <script>/<style> element."""
        super().__init__()
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        """Open a new line for block tags, mark headings (#) and list items (-), separate table cells with ' | ', and enter skip mode inside
        <script>/<style>, whose text is code, not page content.
        """
        if tag in ("script", "style"):
            self.skip += 1
        if tag in BLOCK:
            self.out.append("\n")
        if tag in ("h1", "h2", "h3", "h4"):
            self.out.append("#" * int(tag[1]) + " ")
        if tag == "li":
            self.out.append("- ")
        if tag in ("td", "th"):
            self.out.append(" | ")

    def handle_endtag(self, tag):
        """Leave skip mode after </script>/</style>, and close the line after a block tag."""
        if tag in ("script", "style"):
            self.skip -= 1
        if tag in BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        """Keep a text node unless it sits inside a skipped element."""
        if not self.skip:
            self.out.append(data)


def main():
    """Fetch one help.mikrotik.com page by Confluence id and save it as text with a source header.

    Uses the REST API (`/rest/api/content/<id>?expand=body.view,version`) because the HTML pages render only with JavaScript. The header records the
    page URL, the retrieval date, and the Confluence version and last-edited time, so a later reader can tell whether the vendor page changed since.
    An HTTP or JSON error raises before anything is written, so a partial file is never left behind.
    """
    pid, out = sys.argv[1], sys.argv[2]
    base = sys.argv[3] if len(sys.argv) > 3 else "https://help.mikrotik.com/docs"
    url = f"{base}/rest/api/content/{pid}?expand=body.view,version"
    with urllib.request.urlopen(url, timeout=60) as r:
        d = json.load(r)
    p = Txt()
    p.feed(d["body"]["view"]["value"])
    text = html.unescape("".join(p.out))
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    page = f"{base}/spaces/{d['space']['key'] if 'space' in d else 'ROS'}/pages/{pid}"
    head = (f"Source: {page} — retrieved {datetime.date.today().isoformat()}\n"
            f"Title: {d['title']} (Confluence version {d['version']['number']}, last edited {d['version']['when']})\n\n")
    with open(out, "w") as f:
        f.write(head + text.strip() + "\n")
    print(out, len(text))


if __name__ == "__main__":
    main()
