#!/usr/bin/env python3
"""Fetch and verify one RouterOS version's files from download.mikrotik.com, and print manifest-ready YAML.

Usage:
    routeros_firmware_fetch.py <version> [--dest firmware-files/<version>] [--arch arm,mipsbe] [--verify-only]

Files, per version, from https://download.mikrotik.com/routeros/<version>/:
    routeros-<v>-<arch>.npk, all_packages-<arch>-<v>.zip    one each per --arch (default arm,mipsbe)
    wireless-<v>-mipsbe.npk                                 when mipsbe is selected and the host serves a real file
    netinstall-<v>.zip, netinstall-<v>.tar.gz               always

What it does:
    - Fetches a missing file and resumes a truncated one with an HTTP Range request (restarts if the host ignores the range
      or the local file is longer than the remote one).
    - Verifies each file's size against Content-Length, its md5 against the host's ETag (when the ETag is a plain 32-hex md5),
      and its sha256 against MikroTik's published <url>.sha256 sidecar when one exists; the sidecar is saved beside the file.
    - Prints one YAML block per file (filename, version, url, local_path, size_bytes, sha256, published_sha256, md5,
      etag_md5_match, match) to paste into references/firmware-manifest.yaml, whose curated fields (channel, kind, models,
      firmware_type, retrieved) are added by hand.

--verify-only downloads nothing: HEAD requests only, compared with the local files and any local .sha256 sidecar.
Stops at the first HTTP 429 (exit 2). Exit 1 when any file is missing or fails a check, else 0. Stdlib only.

Known host quirks (2026-10-08):
    - wireless-<v>-mipsbe.npk is a 0-byte placeholder before 7.13: the legacy wireless driver is inside the main mipsbe
      package. The placeholder is reported and skipped, never saved.
    - .sha256 sidecars are not published for 7.8 or 7.12.x; published_sha256 is then null and the ETag md5 is the only
      host-side check.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://download.mikrotik.com/routeros"
PACK = Path(__file__).resolve().parent.parent
CHUNK = 1 << 20
ATTEMPTS = 6
UA = {"User-Agent": "skill-mikrotik routeros_firmware_fetch.py"}


class RateLimited(Exception):
    """The host answered HTTP 429; the run stops rather than retrying."""


def file_names(version: str, arches: list[str]) -> list[str]:
    """Names of the files to fetch for one version and the chosen architectures, in manifest order."""
    names = [f"all_packages-{a}-{version}.zip" for a in arches]
    names += [f"netinstall-{version}.tar.gz", f"netinstall-{version}.zip"]
    names += [f"routeros-{version}-{a}.npk" for a in arches]
    if "mipsbe" in arches:
        names.append(f"wireless-{version}-mipsbe.npk")
    return names


def open_url(req: urllib.request.Request, timeout: int):
    """urlopen that turns HTTP 429 into RateLimited and lets other HTTP errors propagate."""
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited(req.full_url) from e
        raise


def head(url: str) -> tuple[int, str] | None:
    """(Content-Length, ETag without quotes) of url, or None when the host answers 404."""
    try:
        with open_url(urllib.request.Request(url, method="HEAD", headers=UA), 60) as r:
            return int(r.headers.get("Content-Length", -1)), (r.headers.get("ETag") or "").strip('"')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def fetch(url: str, path: Path, size: int) -> None:
    """Download url to path until it is size bytes long, resuming with Range; gives up after ATTEMPTS tries."""
    for _ in range(ATTEMPTS):
        have = path.stat().st_size if path.exists() else 0
        if have == size:
            return
        if have > size:
            path.unlink()
            have = 0
        headers = dict(UA, Range=f"bytes={have}-") if have else dict(UA)
        try:
            with open_url(urllib.request.Request(url, headers=headers), 120) as r:
                mode = "ab" if have and r.status == 206 else "wb"
                with open(path, mode) as f:
                    for block in iter(lambda: r.read(CHUNK), b""):
                        f.write(block)
        except RateLimited:
            raise
        except (urllib.error.URLError, OSError) as e:
            print(f"# {path.name}: transfer error, retrying: {e}", file=sys.stderr)


def fetch_sidecar(url: str, path: Path) -> None:
    """Save url's published .sha256 sidecar beside path when MikroTik publishes one; a 404 leaves nothing."""
    try:
        with open_url(urllib.request.Request(url + ".sha256", headers=UA), 60) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return
        raise
    if data.strip():
        Path(str(path) + ".sha256").write_bytes(data)


def digests(path: Path) -> tuple[str, str]:
    """(sha256, md5) of a local file, read in chunks."""
    s, m = hashlib.sha256(), hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            s.update(block)
            m.update(block)
    return s.hexdigest(), m.hexdigest()


def published_sha256(path: Path) -> str | None:
    """The hash in the local .sha256 sidecar beside path, lower-cased, or None when there is none."""
    side = Path(str(path) + ".sha256")
    if not side.exists() or not side.stat().st_size:
        return None
    return side.read_text().split()[0].lower()


def local_path(path: Path) -> str:
    """path relative to the pack root when it is inside the pack, else as given."""
    try:
        return str(path.resolve().relative_to(PACK))
    except ValueError:
        return str(path)


def yaml_block(row: dict) -> str:
    """One manifest entry as YAML, in the key order of references/firmware-manifest.yaml."""
    nul = "null"
    lines = [
        f"  - filename: {row['filename']}",
        f"    version: \"{row['version']}\"",
        f"    url: {row['url']}",
        f"    local_path: {row['local_path']}",
        f"    size_bytes: {row['size']}",
        f"    sha256: {row['sha256']}",
    ]
    if row["published"]:
        lines += [
            f"    published_sha256: {row['published']}",
            f"    published_sha256_source: {row['url']}.sha256",
            f"    published_sha256_match: {str(row['pub_ok']).lower()}",
        ]
    else:
        lines += ["    published_sha256: null  # no .sha256 published for this version", "    published_sha256_match: null"]
    lines += [
        f"    md5: {row['md5']}",
        f"    etag_md5_match: {nul if row['etag_ok'] is None else str(row['etag_ok']).lower()}",
        f"    match: {str(row['match']).lower()}",
    ]
    return "\n".join(lines)


def process(version: str, name: str, dest: Path, verify_only: bool) -> dict | None:
    """Fetch (unless verify_only) and verify one file; None for a 0-byte placeholder or a file the host does not serve."""
    url = f"{BASE}/{version}/{name}"
    remote = head(url)
    if remote is None:
        print(f"# {name}: not on the host (404), skipped", file=sys.stderr)
        return None
    size, etag = remote
    if size == 0:
        print(f"# {name}: 0-byte placeholder on the host (bundled in the main package before 7.13), skipped", file=sys.stderr)
        return None
    path = dest / name
    if not verify_only:
        fetch(url, path, size)
        fetch_sidecar(url, path)
    if not path.exists():
        print(f"# {name}: MISSING locally", file=sys.stderr)
        return {"filename": name, "missing": True, "match": False}
    sha, md5 = digests(path)
    pub = published_sha256(path)
    have = path.stat().st_size
    row = {
        "filename": name, "version": version, "url": url, "local_path": local_path(path), "size": have,
        "sha256": sha, "md5": md5, "published": pub,
        "size_ok": have == size,
        "etag_ok": (md5 == etag.lower()) if len(etag) == 32 else None,
        "pub_ok": (sha == pub) if pub else None,
    }
    row["match"] = row["size_ok"] and row["etag_ok"] is not False and row["pub_ok"] is not False
    print(f"# {name}: size {have}/{size} etag_md5={row['etag_ok']} sha256_published={row['pub_ok']} "
          f"-> {'match' if row['match'] else 'MISMATCH'}", file=sys.stderr)
    return row


def main() -> int:
    """Parse arguments, process every file of the version, print the YAML and a summary; return the exit code."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("version", help="RouterOS version, e.g. 7.12.2")
    ap.add_argument("--dest", type=Path, help="folder for the files (default: <pack>/firmware-files/<version>)")
    ap.add_argument("--arch", default="arm,mipsbe", help="comma-separated architectures (default: arm,mipsbe)")
    ap.add_argument("--verify-only", action="store_true", help="download nothing; HEAD requests and local files only")
    args = ap.parse_args()
    dest = args.dest or PACK / "firmware-files" / args.version
    arches = [a.strip() for a in args.arch.split(",") if a.strip()]
    if args.verify_only and not dest.is_dir():
        print(f"no such folder: {dest}", file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    rows = []
    try:
        for name in file_names(args.version, arches):
            row = process(args.version, name, dest, args.verify_only)
            if row:
                rows.append(row)
    except RateLimited as e:
        print(f"HTTP 429 from {e}; stopping. Re-run later to resume.", file=sys.stderr)
        return 2
    print("files:")
    for row in rows:
        if not row.get("missing"):
            print(yaml_block(row))
    good = sum(1 for r in rows if r["match"])
    print(f"# {good}/{len(rows)} files match", file=sys.stderr)
    return 0 if rows and good == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
