"""Joint moves for the End-to-end local search (flowmap.e2e EndToEnd._improve). Stdlib only.

The search swaps one pair of neighbouring tracks or ports at a time and keeps a swap only when crossings drop. An out arrow and a back arrow
between the same two boxes can need two changes at once: their ports on one box swapped and their vertical tracks reordered in the channel
they share. Either alone leaves them crossing, so the one-at-a-time search never takes it (2026-10-26, ansible-wifi PHP page: 1.2 and 1.3
crossed although an order without a crossing existed). Here the port swap is tried with each link's track moved next to the other's,
the other tracks kept in order, and the best that cuts crossings is kept.

improve() runs the plain search and the search with joint moves from the same start and keeps the page with fewer crossings, so no
page ends worse than the plain search left it. Measured 2026-10-26: unified-network-controller's 31-flow page 4,177 -> 3,689 crossings
in about 15 s (3 s before); ansible-wifi's PHP page 29 -> 20; the shop example unchanged.

Imported, not run: `from flowmap.crossing_search import port_and_tracks` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from copy import deepcopy

from drawio.route import count_crossings


def link_tracks(grid: object, cids: tuple[str, str]) -> dict[int, dict[str, int]]:
    """Each channel where both links hold exactly one vertical track: {channel: {link id: track}}.

    Args:
        grid: the End-to-end page being improved (flowmap.e2e.EndToEnd).
        cids: the two link ids.

    Returns:
        The channels and their tracks.
    """
    own: dict[int, dict[str, set]] = {}
    for (ch, t), keys in grid.vruns.items():
        for key in keys:
            cid = key.split("|")[0]
            if cid in cids:
                own.setdefault(ch, {}).setdefault(cid, set()).add(t)
    return {ch: {c: next(iter(ts)) for c, ts in by.items()} for ch, by in own.items()
            if len(by) == 2 and all(len(ts) == 1 for ts in by.values()) and len(set.union(*by.values())) == 2}   # two tracks, not one shared


def moved_next_to(slots: list, mover: int, anchor: int) -> list[list]:
    """The slot lists with one track lifted out and put on either side of another, the rest in order.

    Args:
        slots: {track: slot} as a list.
        mover: the track that moves.
        anchor: the track it goes beside.

    Returns:
        The new lists (one or two).
    """
    order = sorted(range(len(slots)), key=slots.__getitem__)
    order.remove(mover)
    out = []
    for side in (0, 1):
        new = order[:]
        new.insert(new.index(anchor) + side, mover)
        perm = [0] * len(slots)
        for slot, track in enumerate(new):
            perm[track] = slot
        if perm != slots:
            out.append(perm)
    return out


def port_and_tracks(grid: object, users: list, i: int) -> bool:
    """Swap ports i and i + 1 of a pool together with a track move in each channel both links use; keep the best that cuts crossings.

    Args:
        grid: the End-to-end page being improved (flowmap.e2e.EndToEnd).
        users: the port pool, permuted in place when a move is kept.
        i: the first of the two neighbouring ports.

    Returns:
        True when a move was kept.
    """
    a, b = users[i][0], users[i + 1][0]
    if a == b or not count_crossings(grid.segs[a], grid.segs[b]):   # only a pair that crosses itself; keeps the search fast
        return False
    chans = link_tracks(grid, (a, b))
    if not chans:
        return False
    on = {ct: {key.split("|")[0] for key in keys} for ct, keys in grid.vruns.items() if ct[0] in chans}
    tried = []
    for ch, by in sorted(chans.items()):   # one channel at a time; a pair rarely shares more than one
        for mover, anchor in ((by[a], by[b]), (by[b], by[a])):
            tried += [(ch, perm) for perm in moved_next_to(grid.vslot[ch], mover, anchor)]
    best, best_gain = None, 0
    for ch, perm in tried:   # only the links whose track or port moves are recounted, against every link
        saved = grid.vslot[ch][:]
        cids = {a, b}.union(*(on.get((ch, t), set()) for t in range(len(perm)) if perm[t] != saved[t]))
        gain = grid._crossings(cids) - _apply(grid, users, i, ch, perm, cids)
        _apply(grid, users, i, ch, saved, cids)
        if gain > best_gain:
            best, best_gain = (ch, perm, cids), gain
    if best is None:
        return False
    ch, perm, cids = best
    saved = grid.vslot[ch][:]
    _apply(grid, users, i, ch, perm, cids)
    if grid._runs_ok(cids):   # the costly spacing check only for the move chosen
        return True
    _apply(grid, users, i, ch, saved, cids)
    return False


def _apply(grid: object, users: list, i: int, ch: int, perm: list, cids: set) -> int:
    """Swap ports i and i + 1 (its own inverse) and set a channel's track order, then redraw the links it moves.

    Args:
        grid: the End-to-end page being improved.
        users: the port pool.
        i: the first of the two ports.
        ch: the channel.
        perm: its new {track: slot} list.
        cids: the links to redraw.

    Returns:
        Their crossings with every link afterwards.
    """
    users[i], users[i + 1] = users[i + 1], users[i]
    grid.vslot[ch][:] = perm
    grid._refresh(cids)
    return grid._crossings(cids)


def improve(grid: object) -> None:
    """The End-to-end local search: plain neighbouring swaps of tracks and ports, and the same with joint moves; the result with fewer
    crossings on the whole page is kept (the plain one on a tie, so a page no joint move helps is unchanged).

    Args:
        grid: the End-to-end page being improved (flowmap.e2e.EndToEnd); its slot and port orders are set in place.
    """
    grid.pts, grid.segs, grid.bbox = {}, {}, {}
    every = {link.cid for link in grid.links}
    grid._refresh(every)
    start = deepcopy((grid.vslot, grid.gslot, grid.pools))
    results = []
    for joint in (False, True):
        grid.vslot, grid.gslot, grid.pools = deepcopy(start)
        grid._refresh(every)
        _search(grid, joint)
        results.append((grid._crossings(every), joint, deepcopy((grid.vslot, grid.gslot, grid.pools))))
    _n, _joint, best = min(results, key=lambda r: (r[0], r[1]))
    grid.vslot, grid.gslot, grid.pools = best
    grid._refresh(every)


def _search(grid: object, joint: bool) -> None:
    """Up to four rounds of neighbouring track and port swaps (and, with joint, port-and-track moves), until a round keeps none.

    Args:
        grid: the End-to-end page being improved.
        joint: also try port_and_tracks on each pair of neighbouring ports.
    """
    vusers = {ct: {key.split("|")[0] for key in keys} for ct, keys in grid.vruns.items()}
    gusers: dict[tuple[int, int], set] = {}
    for (cid, g), t in grid.gtrack.items():
        gusers.setdefault((g, t), set()).add(cid)
    for _ in range(4):
        changed = grid._sweep_slots(grid.vslot, vusers, False)
        changed = grid._sweep_slots(grid.gslot, gusers, True) or changed
        for _key, users in sorted(grid.pools.items()):
            for i in range(len(users) - 1):
                if grid._try(_swap(users, i), {users[i][0], users[i + 1][0]}, check_runs=True) or (joint and port_and_tracks(grid, users, i)):
                    changed = True
        if not changed:
            break


def _swap(order: list, i: int) -> object:
    """A callable swapping entries i and i + 1 of a list (its own inverse).

    Args:
        order: the list.
        i: the first index.

    Returns:
        The callable.
    """
    def run() -> None:
        """Swap the entries."""
        order[i], order[i + 1] = order[i + 1], order[i]
    return run
