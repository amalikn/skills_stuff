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
    def __init__(self):
        super().__init__()
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
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
        if tag in ("script", "style"):
            self.skip -= 1
        if tag in BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def main():
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
