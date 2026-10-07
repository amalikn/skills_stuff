#!/usr/bin/env python3
"""Extract mikrotik.com product page text (description + spec tables). Usage: product_text.py page.html url out.txt"""
import html, re, sys
src, url, out = sys.argv[1:4]
t = open(src).read()
t = re.sub(r'<script.*?</script>|<style.*?</style>|<svg.*?</svg>|<noscript.*?</noscript>', '', t, flags=re.S)
t = re.sub(r'</(tr|p|div|h\d|li|section)>', '\n', t)
t = re.sub(r'<(td|th)[^>]*>', ' | ', t)
t = re.sub(r'<[^>]+>', '', t)
t = html.unescape(t)
lines = [re.sub(r'\s+', ' ', l).strip(' |') for l in t.split('\n')]
lines = [l for l in lines if l]
start = next(i for i, l in enumerate(lines) if re.search(r'\d+ ?MHz|core', l, re.I)) - 2
endm = [i for i, l in enumerate(lines) if re.match(r'(Newsletter|Subscribe|Contacts?|Copyright|©)', l, re.I) and i > start]
end = endm[0] if endm else len(lines)
with open(out, 'w') as f:
    f.write(f"Source: {url} — retrieved 2026-10-07\n\n" + "\n".join(lines[start:end]) + "\n")
print(out, start, end, len(lines))
