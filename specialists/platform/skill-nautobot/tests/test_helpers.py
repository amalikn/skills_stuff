"""Offline tests for the promoted helpers in scripts/: the fail-closed paging guard and the IPAM mask rule."""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
_ipam = importlib.import_module("nautobot_ipam")
_paging = importlib.import_module("nautobot_paging")
network_mask, with_mask = _ipam.network_mask, _ipam.with_mask
PagingError, listing, traverse = _paging.PagingError, _paging.listing, _paging.traverse


def pages(*chunks, count=None):
    """A fake GET over numbered pages: page n holds chunks[n]."""
    total = count if count is not None else sum(len(c) for c in chunks)
    book = {}
    for n, rows in enumerate(chunks):
        nxt = f"p{n + 1}" if n + 1 < len(chunks) else None
        book[f"p{n}"] = {"count": total, "next": nxt, "results": [{"id": r} for r in rows]}
    return lambda url: book[url]


class Listing(unittest.TestCase):
    def test_adds_limit_and_total_order(self):
        self.assertEqual(listing("/api/dcim/devices/"), "/api/dcim/devices/?limit=200&sort=id")
        self.assertEqual(listing("/api/x/?location=a"), "/api/x/?location=a&limit=200&sort=id")

    def test_keeps_callers_choices(self):
        self.assertEqual(listing("/api/x/?limit=50&sort=name"), "/api/x/?limit=50&sort=name")


class Traverse(unittest.TestCase):
    def test_reads_every_page(self):
        self.assertEqual([r["id"] for r in traverse(pages("ab", "cd"), "p0")], list("abcd"))

    def test_repeated_object_fails_rather_than_deduplicates(self):
        with self.assertRaisesRegex(PagingError, "two pages"):
            traverse(pages("ab", "bc", count=4), "p0")

    def test_count_mismatch_fails(self):
        with self.assertRaisesRegex(PagingError, "count"):
            traverse(pages("ab", "c", count=4), "p0")

    def test_repeated_continuation_fails(self):
        book = {"p0": {"count": 2, "next": "p0", "results": [{"id": 1}]}}
        with self.assertRaisesRegex(PagingError, "continuation"):
            traverse(book.__getitem__, "p0")

    def test_empty_page_before_end_fails(self):
        book = {"p0": {"count": 1, "next": "p1", "results": []}, "p1": {"count": 1, "next": None, "results": [{"id": 1}]}}
        with self.assertRaisesRegex(PagingError, "empty page"):
            traverse(book.__getitem__, "p0")

    def test_missing_results_and_missing_id_fail(self):
        with self.assertRaises(PagingError):
            traverse(lambda url: {"detail": "error"}, "p0")
        with self.assertRaises(PagingError):
            traverse(lambda url: {"count": 1, "next": None, "results": [{"name": "x"}]}, "p0")

    def test_page_bound(self):
        with self.assertRaisesRegex(PagingError, "pages"):
            traverse(lambda url: {"count": 9, "next": url + "x", "results": [{"id": url}]}, "p", max_pages=3)


class Mask(unittest.TestCase):
    PREFIXES = [
        {"prefix": "192.0.2.0/24", "type": {"value": "container"}},
        {"prefix": "192.0.2.0/25", "type": {"value": "network"}},
        {"prefix": "192.0.2.0/27", "type": "network"},
        {"prefix": "192.0.2.0/28", "type": {"value": "pool"}},
    ]

    def test_narrowest_network_prefix_wins(self):
        self.assertEqual(network_mask(self.PREFIXES, "192.0.2.10"), 27)
        self.assertEqual(with_mask(self.PREFIXES, "192.0.2.100"), "192.0.2.100/25")

    def test_containers_and_pools_are_not_subnets(self):
        self.assertIsNone(network_mask([self.PREFIXES[0], self.PREFIXES[3]], "192.0.2.5"))

    def test_no_holder_means_none_not_32(self):
        self.assertIsNone(with_mask(self.PREFIXES, "198.51.100.1"))


if __name__ == "__main__":
    unittest.main()
