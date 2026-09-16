#!/usr/bin/env python3
"""Check that every live note points at a real line range, and show what it points at.

WHY THIS EXISTS. On 2026-08-26 a strip of 85 lines left notes holding ranges past end-of-file. The
VS Code extension then failed to activate with `Illegal value for line`, and because activation
failed it never regenerated INDEX.json, so the bad state persisted across reloads. Every command the
extension contributes reported "command not found" and it read like a broken install.

Run this after ANY edit to a file that carries notes, and before reloading the window.

    check_note_anchors.py [--notes-dir .code-context-notes] [--repo .] [--quiet] [--no-hash]

Exit status: 0 all live notes in range, 1 at least one out of range, 2 usage/IO error.

CONTENT HASH. Reproduced from the extension bundle on 2026-08-27 and confirmed against live notes:
normalize each line of the range (strip, collapse internal whitespace), drop blank lines, join with
newlines, sha256. A mismatch is classified rather than merely reported, by replicating the
extension's own exact-match pass -- slide a same-line-count window across the whole file:

  MOVED    the stored hash matches a DIFFERENT range in the same file. The extension will relocate
           the note on its next document-change event; the stored range is stale until then.
  DRIFTED  the hash matches nowhere. The anchored code was edited, so the exact pass is exhausted
           and only the fuzzy fallback (Levenshtein >= 0.7, within +/-50 lines) can still find it.
           Range is often still correct -- this is what a completed fuzzy re-anchor leaves behind.

Neither is fatal, so both leave exit status 0: they describe anchor quality, not a broken extension.
Out-of-range notes remain the only thing that crashes activation, and remain exit 1.
"""
from __future__ import annotations
import argparse, hashlib, pathlib, re, sys

FIELD = {
    'file': re.compile(r'^\*\*File:\*\*\s*(.+?)\s*$', re.M),
    'lines': re.compile(r'^\*\*Lines:\*\*\s*(\d+)\s*-\s*(\d+)\s*$', re.M),
    'status': re.compile(r'^\*\*Status:\*\*\s*(.+?)\s*$', re.M),
    'type': re.compile(r'^\*\*Type:\*\*\s*(.+?)\s*$', re.M),
    'priority': re.compile(r'^\*\*Priority:\*\*\s*(.+?)\s*$', re.M),
    'hash': re.compile(r'^\*\*Content Hash:\*\*\s*([0-9a-f]{64})\s*$', re.M),
}


def content_hash(lines: list[str], start1: int, end1: int) -> str:
    """Mirror the extension's hashTracker.generateHash for a 1-indexed inclusive range.

    Normalization is what makes the hash survive reformatting: every line is stripped and its
    internal whitespace collapsed, blank lines are dropped entirely, and the survivors are joined
    with newlines before hashing. So reindenting a block never disturbs its notes.
    """
    raw = lines[start1 - 1:end1]
    norm = [t for t in (' '.join(x.split()) for x in raw) if t]
    return hashlib.sha256('\n'.join(norm).encode()).hexdigest()


def find_hash(lines: list[str], want: str, span: int) -> int | None:
    """Replicate the extension's exact pass: first same-span window whose hash matches, from line 1.

    Scanning from the top rather than outward from the old position is deliberate -- it is what the
    extension does, and it is why a note can silently jump to an earlier identical block.
    """
    for start in range(1, len(lines) - span + 2):
        if content_hash(lines, start, start + span - 1) == want:
            return start
    return None


def parse(md: str) -> dict | None:
    m = FIELD['lines'].search(md)
    f = FIELD['file'].search(md)
    if not m or not f:
        return None
    s = FIELD['status'].search(md)
    t = FIELD['type'].search(md)
    p = FIELD['priority'].search(md)
    h = FIELD['hash'].search(md)
    return {
        'file': f.group(1),
        'start': int(m.group(1)),
        'end': int(m.group(2)),
        'status': s.group(1) if s else 'ACTIVE',
        'type': t.group(1) if t else 'context',
        'priority': p.group(1) if p else 'normal',
        'hash': h.group(1) if h else None,
    }


def index_freshness(ndir: pathlib.Path, live: list[dict]) -> str | None:
    """Report notes the VS Code sidebar will not show, or will show in the wrong place.

    `INDEX.json` and the `AGENTS.md` digest are written ONLY by the extension; the MCP server writes
    note `.md` files and touches neither. So a note created over MCP is on disk and readable by any
    agent, but stays absent from the sidebar until the extension next activates.

    This compares per-note, NOT by mtime. An mtime comparison cries wolf: every time the extension
    re-anchors a note it rewrites that `.md`, leaving the index legitimately older than the newest
    note while its contents are perfectly current.

    `INDEX.json` stores lineRange 0-indexed (matching the MCP schema); the `.md` header renders the
    same range 1-indexed. Hence the +1 when comparing.

    Display lag, not damage — deliberately NOT an error. Returns a message to print, or None.
    """
    index = ndir / 'INDEX.json'
    if not index.is_file():
        return ('NOT INDEXED: no INDEX.json. The extension has never indexed this workspace — '
                'open it in VS Code once so the sidebar populates.')

    import json
    try:
        entries = json.loads(index.read_text()).get('notes') or []
    except (json.JSONDecodeError, OSError) as exc:
        return f'UNREADABLE INDEX.json ({exc}). Reload the VS Code window to have the extension rebuild it.'

    indexed = {e['id']: (e['lineRange']['start'] + 1, e['lineRange']['end'] + 1)
               for e in entries if e.get('id') and isinstance(e.get('lineRange'), dict)}

    absent, moved = [], []
    for n in live:
        got = indexed.get(n['id'])
        if got is None:
            absent.append(n)
        elif got != (n['start'], n['end']):
            moved.append((n, got))

    if not absent and not moved:
        return None

    out = ['SIDEBAR OUT OF DATE — the notes on disk are fine; the extension has not caught up.']
    for n in sorted(absent, key=lambda x: (x['file'], x['start'])):
        out.append(f"  not indexed  L{n['start']}-{n['end']}  {pathlib.Path(n['file']).name}  [{n['id'][:8]}]")
    for n, got in sorted(moved, key=lambda x: (x[0]['file'], x[0]['start'])):
        out.append(f"  indexed at   L{got[0]}-{got[1]} but on disk L{n['start']}-{n['end']}  "
                   f"{pathlib.Path(n['file']).name}  [{n['id'][:8]}]")
    out.append('  Reload the VS Code window (Developer: Reload Window).')
    out.append('  Nothing to repair — INDEX.json is written only by the extension, never by the MCP server.')
    return '\n'.join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--notes-dir', default='.code-context-notes')
    ap.add_argument('--repo', default='.', help='workspace root, for resolving note file paths')
    ap.add_argument('--quiet', action='store_true', help='only report problems')
    ap.add_argument('--no-hash', action='store_true',
                    help='skip content-hash verification (range checks only)')
    args = ap.parse_args()

    ndir = pathlib.Path(args.notes_dir)
    if not ndir.is_dir():
        print(f'no notes directory at {ndir}', file=sys.stderr)
        return 2
    repo = pathlib.Path(args.repo).resolve()

    cache: dict[str, list[str] | None] = {}

    def load(p: str) -> list[str] | None:
        if p not in cache:
            fp = pathlib.Path(p)
            if not fp.is_absolute():
                fp = repo / fp
            cache[p] = fp.read_text().split('\n') if fp.is_file() else None
        return cache[p]

    live, deleted, bad, missing = [], 0, [], []
    for md in sorted(ndir.glob('*.md')):
        if md.name == 'AGENTS.md':          # auto-generated digest, not a note
            continue
        n = parse(md.read_text())
        if n is None:
            continue
        if n['status'].upper() == 'DELETED':
            deleted += 1
            continue
        n['id'] = md.stem
        lines = load(n['file'])
        if lines is None:
            missing.append(n)
            continue
        n['total'] = len(lines)
        if n['start'] < 1 or n['end'] > len(lines) or n['start'] > n['end']:
            bad.append(n)
        else:
            seg = [x.strip() for x in lines[n['start'] - 1:n['end']] if x.strip()]
            n['anchor'] = seg[0] if seg else '(blank — the range holds no code)'
            if not seg:
                bad.append(n)
                continue
            live.append(n)

    drift: list[dict] = []
    if not args.no_hash:
        for n in live:
            if not n['hash']:
                continue
            lines = load(n['file'])
            if content_hash(lines, n['start'], n['end']) == n['hash']:
                continue
            found = find_hash(lines, n['hash'], n['end'] - n['start'] + 1)
            n['drift'] = ('MOVED', found) if found else ('DRIFTED', None)
            drift.append(n)

    if not args.quiet:
        for n in sorted(live, key=lambda x: (x['file'], x['start'])):
            tag = f"{n['type']}/{n['priority']}"
            mark = {'MOVED': 'move', 'DRIFTED': 'hash'}.get(n.get('drift', ('', ''))[0], 'ok  ')
            print(f"  {mark} {n['start']:>4}-{n['end']:<4} {tag:<20} {n['anchor'][:70]}")

    for n in sorted(missing, key=lambda x: x['file']):
        print(f"  MISS {n['start']:>4}-{n['end']:<4} file not found: {n['file']}", file=sys.stderr)
    for n in sorted(bad, key=lambda x: (x['file'], x['start'])):
        print(f"  BAD  {n['start']:>4}-{n['end']:<4} file has {n.get('total','?')} lines  "
              f"[{n['id'][:8]}] {n['file']}", file=sys.stderr)

    print(f"\nlive: {len(live)}   deleted: {deleted}   out-of-range: {len(bad)}   missing-file: {len(missing)}")

    if drift:
        print(f"\ncontent hash: {len(live) - len(drift)}/{len(live)} verified, {len(drift)} to look at")
        for n in sorted(drift, key=lambda x: (x['file'], x['start'])):
            kind, found = n['drift']
            if kind == 'MOVED':
                print(f"  MOVED   [{n['id'][:8]}] {n['file']} indexed {n['start']}-{n['end']}, "
                      f"content now at {found}-{found + n['end'] - n['start']}")
            else:
                print(f"  DRIFTED [{n['id'][:8]}] {n['file']} {n['start']}-{n['end']} — anchored code was "
                      f"edited; hash matches nowhere in the file")
        print('  Neither is an error. MOVED resolves itself on the next edit in VS Code; DRIFTED means the\n'
              '  exact-match pass is spent, so re-read the note against the code it now points at.')
    elif not args.no_hash and live:
        print(f"\ncontent hash: {len(live)}/{len(live)} verified")

    stale = index_freshness(ndir, live)
    if stale:
        print('\n' + stale)

    if bad:
        print('\nOut-of-range notes crash the extension on activation, which then stops it '
              'regenerating INDEX.json, so a reload will NOT clear it.', file=sys.stderr)
        print('Fix by delete_note + create_note at the correct range BEFORE reloading the window.', file=sys.stderr)
        return 1
    if args.no_hash:
        print('All live notes are in range. Content hashes were not checked (--no-hash).')
    else:
        print('All live notes are in range.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
