"""band_search: swap two boxes in the End-to-end band while the real routes cross less, with the trials laid out in worker processes.

Moved out of flowmap.crossing_search on 2026-11-06 (that module passed 400 lines when the pool came in); crossing_search re-exports band_search.
Each trial is a full page layout (about 5 s on unified-network-controller's map, 200 of 250 s of its render), so trials are scored in forked
workers, a chunk at a time, keeping exactly the swaps the one-at-a-time walk keeps. `SKILL_DRAWIO_WORKERS=1` runs them in this process.

Imported, not run: `from flowmap.band_pool import band_search` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import multiprocessing
import os
from itertools import combinations


def band_search(best: object, build: object, look: dict) -> object:
    """Swap two boxes in the band below the columns while the page's real routes cross less (operator, 2026-11-02: "Swapping change spec and
    run trackers would have eliminated an overlap"): each band box is placed alone, nearest its neighbours, so a pair is never weighed
    together. Every candidate is a full layout, so the pairs are tried once, and again only after a gain.

    Args:
        best: the page laid out so far.
        build: a callable from a tuple of band swaps to a page.
        look: the look settings (`e2e_band_search: false` turns this off).

    Returns:
        The page with the fewest crossings; `best` itself when no swap gains.
    """
    if not look.get("e2e_band_search", True):
        return best
    swaps, gained = (), True
    band = [cid for cid, (_c, r) in best.cell.items() if r >= best.band]
    best_cost = _cost(best)
    with _TrialPool(build) as pool:
        while gained and best_cost:
            gained = False
            pairs, k = list(combinations(band, 2)), 0
            # The same greedy walk as one pair at a time (each pair tried against the page as it then stands, the first that gains kept),
            # with the next `pool.width` pairs scored at once from that page; scores past a kept pair are dropped and redone from the new
            # page, so the result is the sequential one (2026-11-06: 200 of 250 s of UNC's render was this loop, one full layout per pair).
            while k < len(pairs):
                chunk = pairs[k:k + pool.width]
                costs = pool.costs([(*swaps, pair) for pair in chunk])
                hit = next((j for j, c in enumerate(costs) if c < best_cost), None)
                if hit is None:
                    k += len(chunk)
                    continue
                swaps = (*swaps, chunk[hit])
                best, gained = build(swaps), True
                best_cost = _cost(best)
                k += hit + 1
    return best


#: Worker processes for band_search's trials: one full layout each. SKILL_DRAWIO_WORKERS overrides (1 runs them in this process).
BAND_WORKERS = max(1, min(8, (os.cpu_count() or 2) - 1))
#: Seconds one round of trials may take (one full layout each, in parallel; about 5 s on UNC's 42-page map).
TRIAL_TIMEOUT_S = 900
_BUILD = None   # the trial builder, read by forked workers: a closure cannot be sent to a worker, but fork copies it


def _cost(page: object) -> int:
    """A laid-out page's real-route crossings.

    Args:
        page: an End-to-end page model.

    Returns:
        Its crossing count.
    """
    return page._crossings(set(page.segs))


def _trial_cost(swaps: tuple) -> int:
    """Lay out one band trial in a worker and score it.

    Args:
        swaps: the band swaps of the trial (pairs of component ids).

    Returns:
        The trial's crossing count.
    """
    return _cost(_BUILD(swaps))


class _TrialPool:
    """Scores band trials in forked workers, in order; falls back to this process when fork is unavailable or one worker is asked for."""

    def __init__(self, build: object):
        """Keep the builder.

        Args:
            build: a callable from a tuple of band swaps to a page.
        """
        self.build, self.pool = build, None
        self.width = max(1, int(os.environ.get("SKILL_DRAWIO_WORKERS", BAND_WORKERS)))

    def __enter__(self) -> "_TrialPool":
        """Start the workers when more than one is wanted and fork exists.

        Returns:
            This pool.
        """
        global _BUILD
        if self.width > 1 and "fork" in multiprocessing.get_all_start_methods():
            _BUILD = self.build
            self.pool = multiprocessing.get_context("fork").Pool(self.width)
        else:
            self.width = 1
        return self

    def costs(self, trials: list) -> list[int]:
        """Score trials, in their order.

        Args:
            trials: band swap tuples.

        Returns:
            One crossing count per trial.

        Raises:
            multiprocessing.TimeoutError: a round took longer than TRIAL_TIMEOUT_S.
        """
        if self.pool is None or len(trials) == 1:
            return [_cost(self.build(t)) for t in trials]
        return self.pool.map_async(_trial_cost, trials, chunksize=1).get(timeout=TRIAL_TIMEOUT_S)   # raises TimeoutError on a stuck worker

    def __exit__(self, *exc) -> None:
        """Stop the workers.

        Args:
            exc: the exception, if any (not handled here).
        """
        global _BUILD
        if self.pool is not None:
            self.pool.terminate() if exc and exc[0] else self.pool.close()
            self.pool.join()
        _BUILD = None
