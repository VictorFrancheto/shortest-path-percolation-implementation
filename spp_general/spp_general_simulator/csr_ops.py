"""Low-level CSR mutation helpers (``spp-dynamic.ipynb``, "CSR Utilities").

Neighbor lookup, O(1) removal via the twin pointer, the degree bucket used to
accelerate rank-1 hub selection, and reconstruction into an ``nx.Graph``
(needed only for the centrality-based selection modes).
"""

import networkx as nx
import numpy as np

from .jit_compat import njit


@njit(cache=True)
def find_neighbor_pos(i, j, deg, indptr, adj):
    """Return the 1-indexed position of j in i's neighbor list, or -1."""
    base = indptr[i]
    d = deg[i]
    for k in range(d):
        if adj[base + k] == j:
            return k + 1
    return -1


@njit(cache=True)
def remove_neighbor(i, k_pos, deg, indptr, adj):
    """Plain swap-and-pop (no twin/bucket bookkeeping)."""
    base = indptr[i]
    last = base + deg[i] - 1
    adj[base + k_pos - 1] = adj[last]
    deg[i] -= 1


@njit(cache=True)
def bk_init(N, deg, bk_head, bk_next, bk_prev, bk_max_arr):
    """Initialize the degree-bucket structures from ``deg``."""
    for d in range(bk_head.size):
        bk_head[d] = 0
    for i in range(bk_next.size):
        bk_next[i] = 0
        bk_prev[i] = 0
    bk_max = 0
    for i in range(1, N + 1):
        d = deg[i]
        nxt = bk_head[d]
        bk_next[i] = nxt
        bk_prev[i] = 0
        if nxt != 0:
            bk_prev[nxt] = i
        bk_head[d] = i
        if d > bk_max:
            bk_max = d
    bk_max_arr[0] = bk_max


@njit(cache=True)
def bk_decrement(i, old_d, bk_head, bk_next, bk_prev, bk_max_arr):
    """Move node i from bucket ``old_d`` to ``old_d - 1`` in O(1).

    Called AFTER ``deg[i]`` has already been decremented.
    """
    nxt = bk_next[i]
    prv = bk_prev[i]
    if prv == 0:
        bk_head[old_d] = nxt
    else:
        bk_next[prv] = nxt
    if nxt != 0:
        bk_prev[nxt] = prv
    new_d = old_d - 1
    nxt2 = bk_head[new_d]
    bk_next[i] = nxt2
    bk_prev[i] = 0
    if nxt2 != 0:
        bk_prev[nxt2] = i
    bk_head[new_d] = i
    if bk_head[bk_max_arr[0]] == 0:
        m = bk_max_arr[0]
        while m > 0 and bk_head[m] == 0:
            m -= 1
        bk_max_arr[0] = m


@njit(cache=True)
def remove_neighbor_twin(i, k_pos, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr):
    """O(1) swap-and-pop that keeps the twin pointer and the degree bucket consistent."""
    base = indptr[i]
    cur = base + k_pos - 1
    last = base + deg[i] - 1
    if cur != last:
        adj[cur] = adj[last]
        twin[cur] = twin[last]
        twin[twin[cur]] = cur  # the swapped neighbor now points back at the new slot
    old_d = deg[i]
    deg[i] = old_d - 1
    bk_decrement(i, old_d, bk_head, bk_next, bk_prev, bk_max_arr)


def csr_to_graph(deg, indptr, adj, N) -> nx.Graph:
    """Rebuild an ``nx.Graph`` from the CSR arrays (only needed for centrality measures)."""
    G = nx.Graph()
    G.add_nodes_from(range(1, N + 1))
    for i in range(1, N + 1):
        base = int(indptr[i])
        for k in range(int(deg[i])):
            j = int(adj[base + k])
            if i < j:
                G.add_edge(i, j)
    return G


def new_degree_bucket(N: int):
    """Allocate a fresh degree bucket for a network with N nodes."""
    bk_head = np.zeros(N + 2, dtype=np.int32)
    bk_next = np.zeros(N + 1, dtype=np.int32)
    bk_prev = np.zeros(N + 1, dtype=np.int32)
    bk_max_arr = np.zeros(1, dtype=np.int32)
    return bk_head, bk_next, bk_prev, bk_max_arr
