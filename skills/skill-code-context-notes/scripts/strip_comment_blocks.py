#!/usr/bin/env python3
"""Replace comment blocks with shorter markers (or delete them), safely.

Every edit names an expected substring on its own first line and the run ABORTS on any mismatch, so a
stale line number can never silently rewrite the wrong part of the file. Edits are applied in
descending start-line order, which keeps the earlier line numbers valid throughout.

For YAML, the result is gated on `safe_load_all` data-EQUALITY against the original, not merely on
"it still parses" — a marker accidentally added inside a `content: |` block scalar parses perfectly
and changes the payload that gets deployed. That gate is the whole safety story.

Edits are supplied as JSON: a list of objects with
    start   1-indexed first line of the block           (required)
    end     1-indexed last line, inclusive; omit or set
            to start-1 to INSERT before `start`         (optional)
    expect  substring that must appear on line `start`  (required)
    repl    list of replacement lines, [] to delete      (required)
    label   short description, for the report            (optional)

Usage:
    strip_comment_blocks.py FILE --edits edits.json [--dry-run] [--backup DIR]
"""
from __future__ import annotations
import argparse, json, pathlib, shutil, sys

try:
    import yaml
except ImportError:
    yaml = None


def yaml_payload(text: str):
    return list(yaml.safe_load_all(text))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('file')
    ap.add_argument('--edits', required=True, help='path to the JSON edit list, or - for stdin')
    ap.add_argument('--dry-run', action='store_true', help='report what would change, write nothing')
    ap.add_argument('--backup', help='directory to copy the original into before writing')
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    if not path.is_file():
        print(f'not a file: {path}', file=sys.stderr)
        return 2

    raw = sys.stdin.read() if args.edits == '-' else pathlib.Path(args.edits).read_text()
    edits = json.loads(raw)
    if not isinstance(edits, list) or not edits:
        print('edits must be a non-empty JSON list', file=sys.stderr)
        return 2

    original = path.read_text()
    lines = original.split('\n')
    is_yaml = path.suffix.lower() in ('.yml', '.yaml')

    if is_yaml and yaml is None:
        print('refusing to edit YAML without PyYAML: the data-equality gate cannot run', file=sys.stderr)
        return 2

    # Descending by start, so earlier indices stay valid as we mutate.
    edits.sort(key=lambda e: e['start'], reverse=True)

    applied = []
    for e in edits:
        start = int(e['start'])
        end = int(e.get('end', start - 1))
        expect = e['expect']
        repl = list(e['repl'])
        label = e.get('label', f'L{start}')

        idx = start - 1
        if not (0 <= idx < len(lines)):
            print(f'ABORT [{label}]: line {start} out of range (file has {len(lines)} lines)', file=sys.stderr)
            return 1
        if expect not in lines[idx]:
            print(f'ABORT [{label}]: line {start} does not contain expected text', file=sys.stderr)
            print(f'  expected substring: {expect!r}', file=sys.stderr)
            print(f'  actual line:        {lines[idx]!r}', file=sys.stderr)
            return 1

        if end >= start:
            lines[idx:end] = repl
            applied.append(f'{label}: L{start}-{end} ({end - start + 1} -> {len(repl)})')
        else:
            lines[idx:idx] = repl
            applied.append(f'{label}: inserted {len(repl)} line(s) before L{start}')

    new_text = '\n'.join(lines)

    # Gate: for YAML the parsed data must be unchanged. Comments are non-semantic; a marker that
    # landed inside a block scalar is not, and only a data comparison catches it.
    if is_yaml:
        try:
            before, after = yaml_payload(original), yaml_payload(new_text)
        except yaml.YAMLError as exc:
            print(f'ABORT: result is not valid YAML: {exc}', file=sys.stderr)
            return 1
        if before != after:
            print('ABORT: YAML data changed. A marker probably landed inside a block scalar '
                  '(content: | / script: |), which alters the deployed payload.', file=sys.stderr)
            return 1
        gate = 'yaml safe_load_all data-equality'
    else:
        gate = 'none (non-YAML: verify by hand)'

    before_n, after_n = len(original.split('\n')), len(lines)
    print(f'{path}: {before_n} -> {after_n} lines ({before_n - after_n} removed)')
    for a in reversed(applied):
        print('  -', a)
    print(f'gate: {gate}')

    if args.dry_run:
        print('\n--dry-run: nothing written')
        return 0

    if args.backup:
        bdir = pathlib.Path(args.backup)
        bdir.mkdir(parents=True, exist_ok=True)
        # Flatten the path into the filename. Keying on path.name alone silently overwrites the
        # previous backup whenever two targets share a basename -- and in an Ansible repo almost
        # every one of them is called main.yml.
        flat = str(path).lstrip('/').replace('/', '__')
        dest = bdir / (flat + '.bak')
        if dest.exists():
            print(f'ABORT: backup already exists, refusing to overwrite: {dest}', file=sys.stderr)
            return 1
        shutil.copy2(path, dest)
        print(f'backup: {dest}')

    path.write_text(new_text)
    print('written')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
