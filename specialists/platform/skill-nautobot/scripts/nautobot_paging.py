"""Fail-closed traversal of a Nautobot REST listing. Stdlib only; the caller supplies the HTTP GET, so authentication and retries stay theirs.

Why: Nautobot pages by offset, which is only safe when the queryset has a total order. Some endpoints have none (seen on DNS Models
A records and core ip-address-to-interface in 3.2.x), so page two can repeat rows from page one and skip others: one deployment listed
320 rows that held 251 distinct objects, and an importer then acted on the wrong set. Sorting by a unique key (`sort=id`) fixes the order;
this module also refuses to return a listing that still repeats an object, repeats a continuation, ends early or disagrees with `count`.
It cannot prove completeness against concurrent writes; for that, compare with a snapshot or re-read.

Usage:
    from nautobot_paging import listing, traverse
    rows = traverse(lambda url: session.get(url, timeout=60).json(), base + listing("/api/dcim/devices/?location=site-a"))
"""

from __future__ import annotations

from typing import Callable


class PagingError(RuntimeError):
    """The listing cannot be trusted as one consistent set of objects."""


def listing(path: str, limit: int = 200, sort: str = "id") -> str:
    """`path` with `limit` and a total order (`sort=id` by default) unless the caller already set them."""
    sep = "&" if "?" in path else "?"
    extra = [] if "limit=" in path else [f"limit={limit}"]
    if "sort=" not in path:
        extra.append(f"sort={sort}")
    return f"{path}{sep}{'&'.join(extra)}" if extra else path


def traverse(get: Callable[[str], dict], first_url: str, *, id_key: str = "id", max_pages: int = 1000) -> list[dict]:
    """Every row of a paged listing, following `next` exactly. Raises PagingError instead of returning a doubtful set."""
    rows: list[dict] = []
    seen_urls: set[str] = set()
    seen_ids: set = set()
    first_count = None
    url: str | None = first_url
    page: dict = {}
    while url:
        if url in seen_urls:
            raise PagingError(f"continuation repeats: {url}")
        seen_urls.add(url)
        if len(seen_urls) > max_pages:
            raise PagingError(f"more than {max_pages} pages; raise max_pages only if the set is really that large")
        page = get(url)
        if not isinstance(page, dict) or not isinstance(page.get("results"), list):
            raise PagingError(f"response from {url} has no results list")
        if first_count is None:
            first_count = page.get("count")
        if not page["results"] and page.get("next"):
            raise PagingError(f"empty page before the end at {url}")
        for row in page["results"]:
            key = row.get(id_key) if isinstance(row, dict) else None
            if key is None:
                raise PagingError(f"a row on {url} has no {id_key!r}")
            if key in seen_ids:
                raise PagingError(f"{id_key} {key} appears on two pages: the listing has no stable order, or changed during traversal")
            seen_ids.add(key)
            rows.append(row)
        url = page.get("next")
    for count in {first_count, page.get("count")} - {None}:
        if count != len(rows):
            raise PagingError(f"count {count} but {len(rows)} distinct rows read: the set changed or rows were skipped")
    return rows
