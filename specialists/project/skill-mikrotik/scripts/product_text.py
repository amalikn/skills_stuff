#!/usr/bin/env python3
"""Extract a saved mikrotik.com product page's text: the description and the spec tables, without site chrome.

usage: product_text.py <page.html> <url> <out.txt>
The page is saved first (any fetcher); this only turns HTML into text. The first line of the output is the source URL and today's date, the same header
confluence_fetch.py writes, so a vendor file in references/vendor-sources-*/ always says where and when it came from.
"""
import datetime
import html
import re
import sys

# ---------- HTML to lines ----------


def page_lines(raw):
    """The page as a list of non-empty text lines: scripts, styles, SVG and noscript dropped, block tags turned into line breaks, table cells into ' | '.

    Regex rather than an HTML parser on purpose: the product pages are machine-generated with a stable shape, and the output only needs to be readable
    text for a person or a grep, not a faithful DOM.
    """
    t = re.sub(r'<script.*?</script>|<style.*?</style>|<svg.*?</svg>|<noscript.*?</noscript>', '', raw, flags=re.S)
    t = re.sub(r'</(tr|p|div|h\d|li|section)>', '\n', t)
    t = re.sub(r'<(td|th)[^>]*>', ' | ', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t)
    lines = [re.sub(r'\s+', ' ', line).strip(' |') for line in t.split('\n')]
    return [line for line in lines if line]


# ---------- the product section ----------


def product_section(lines):
    """The slice of lines that is the product itself: from just before the first CPU line (a frequency in MHz, or 'core') to the footer.

    The start is anchored on the spec content rather than on markup, because the navigation above it changes from page to page; two lines of lead-in
    are kept so the product name stays with its specs. The end is the first footer marker (newsletter, contacts, copyright) after the start, or the end
    of the page. Raises StopIteration when no CPU line exists, which means the page is not a product page.
    """
    start = next(i for i, line in enumerate(lines) if re.search(r'\d+ ?MHz|core', line, re.I)) - 2
    ends = [i for i, line in enumerate(lines) if re.match(r'(Newsletter|Subscribe|Contacts?|Copyright|©)', line, re.I) and i > start]
    return start, (ends[0] if ends else len(lines))


# ---------- main ----------


def main():
    """Read the saved page, keep the product section, and write it with a `Source: <url> — retrieved <today>` header; print the line range used."""
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    src, url, out = sys.argv[1:4]
    with open(src, encoding='utf-8', errors='replace') as f:
        lines = page_lines(f.read())
    start, end = product_section(lines)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f"Source: {url} — retrieved {datetime.date.today().isoformat()}\n\n" + "\n".join(lines[start:end]) + "\n")
    print(out, start, end, len(lines))


if __name__ == "__main__":
    main()
