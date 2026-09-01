"""Single-node selection kernels and the ``(source, target)`` picker (notebook cell 24-25).

``random``/``hub`` have dedicated ``@njit`` kernels (the "fast path"); the
other modes recompute a global metric on every call and use the "slow path"
in pure Python -- ``core_pair_removal_loop`` (in ``dynamics/phase1.py``)
automatically detects which path to use.
"""

import numpy as np

from ..jit_compat import njit
from .centrality import get_betweenness_nodes, get_closeness_nodes
from .domirank import get_domirank_nodes
from .strategies import resolve_selection_strategy

# Integer mode codes used by the @njit kernels (random/hub only; the other
# modes use the slow Python path and don't need an integer code).
MODE_RANDOM = 0
MODE_HUB = 1


@njit(cache=True)
def pick_node_njit(N, deg, mode_code, rank, exclude):
    """@njit-compatible picker (O(N) fallback version).

    - random : uniform in {1..N}, no `exclude`.
    - hub    : rank-th node by (-deg, id), with `exclude` filtered out. Ties
               are broken by the SMALLEST id (stable descending sort by degree).

    `exclude` < 0 means no exclusion.
    """
    if mode_code == 0:  # random
        if exclude < 0:
            return np.int64(np.random.randint(1, N + 1))
        while True:
            n = np.int64(np.random.randint(1, N + 1))
            if n != exclude:
                return n

    # hub
    if rank < 1:
        rank = 1
    best_ids = np.full(rank, -1, dtype=np.int64)
    best_degs = np.full(rank, -1, dtype=np.int64)
    for i in range(1, N + 1):
        if i == exclude:
            continue
        d = np.int64(deg[i])
        pos = -1
        for r in range(rank):
            if best_ids[r] == -1 or d > best_degs[r]:
                pos = r
                break
        if pos >= 0:
            for r in range(rank - 1, pos, -1):
                best_ids[r] = best_ids[r - 1]
                best_degs[r] = best_degs[r - 1]
            best_ids[pos] = i
            best_degs[pos] = d
    return best_ids[rank - 1]


@njit(cache=True)
def pick_hub_rank1_bk(bk_head, bk_next, bk_max_arr, exclude):
    """HUB rank=1 accelerated via the degree bucket -- O(|bucket(max)|) ~ O(1).

    Ties broken by SMALLEST id. Walks down in degree until a non-empty bucket
    is found or none remain. `exclude` < 0 means no exclusion.
    """
    d = bk_max_arr[0]
    while True:
        cur = bk_head[d]
        best = 0
        while cur != 0:
            if cur != exclude:
                if best == 0 or cur < best:
                    best = cur
            cur = bk_next[cur]
        if best != 0:
            return np.int64(best)
        if d <= 0:
            return np.int64(-1)
        d -= 1


def select_node(N, deg, indptr, adj, mode="random", rank=1, exclude=None):
    """Select a node according to ``mode``.

    Parameters
    ----------
    N : int
        Number of nodes in the network.
    deg, indptr, adj : np.ndarray
        CSR representation of the network.
    mode : str
        One of 'random', 'hub', 'closeness', 'betweenness', 'domirank'.
    rank : int
        Rank of the node to select (1 = highest, 2 = second highest, ...).
    exclude : int or None
        Node to exclude from selection (e.g. the source already chosen).

    Returns
    -------
    int or None
        Selected node ID (1-indexed), or None if no candidate is available.
    """
    if mode == "random":
        ex = -1 if exclude is None else int(exclude)
        return int(pick_node_njit(N, deg, MODE_RANDOM, 1, ex))

    if mode == "hub":
        ex = -1 if exclude is None else int(exclude)
        node = int(pick_node_njit(N, deg, MODE_HUB, int(rank), ex))
        return node if node > 0 else None

    if mode == "closeness":
        ordered = get_closeness_nodes(N, deg, indptr, adj, top_k=N)
    elif mode == "betweenness":
        ordered = get_betweenness_nodes(N, deg, indptr, adj, top_k=N)
    elif mode == "domirank":
        ordered = get_domirank_nodes(N, deg, indptr, adj, top_k=N)
    else:
        raise ValueError(f"Unknown attack mode: {mode}")

    if exclude is not None:
        ordered = [n for n in ordered if n != exclude]
    if not ordered:
        return None
    idx = min(max(1, rank) - 1, len(ordered) - 1)
    return ordered[idx]


def mode_to_code(mode):
    """String -> integer mode code for the @njit hot path.

    None => slow Python fallback (closeness / betweenness / domirank).
    """
    if mode == "random":
        return MODE_RANDOM
    if mode == "hub":
        return MODE_HUB
    return None


def choose_source_target(N, deg, indptr, adj, strategy_name, rank_1=1, rank_2=1):
    """Select a validated ``(source, target)`` pair for ``strategy_name``.

    Centralizes validation: valid node IDs, source != target, graceful errors
    for empty candidate lists, and clear messages when a mode has no valid
    candidate (e.g. rank beyond the number of nodes, or a
    degenerate/fragmented graph).

    Raises
    ------
    ValueError
        For any invalid configuration (N < 2, no candidates for a mode, node
        ids outside [1, N], ...).
    """
    if N < 2:
        raise ValueError("N must be >= 2 to choose a (source, target) pair.")

    mode_1, mode_2 = resolve_selection_strategy(strategy_name)

    source = select_node(N, deg, indptr, adj, mode=mode_1, rank=rank_1)
    if source is None:
        raise ValueError(f"No candidate for the source (mode={mode_1!r}, rank={rank_1}).")
    if not (1 <= source <= N):
        raise ValueError(f"Source outside the valid range [1,{N}]: {source}.")

    target = select_node(N, deg, indptr, adj, mode=mode_2, rank=rank_2, exclude=source)
    if target is None:
        raise ValueError(f"No candidate for the target (mode={mode_2!r}, rank={rank_2}, excluding node {source}).")
    if not (1 <= target <= N):
        raise ValueError(f"Target outside the valid range [1,{N}]: {target}.")

    if source == target:
        # select_node already excludes the source when drawing the target; this
        # is a safeguard against future regressions, not an expected code path.
        raise RuntimeError("source == target after selection -- should not happen.")

    return source, target
