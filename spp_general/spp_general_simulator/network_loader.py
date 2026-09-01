"""Loading a previously saved network and converting it to CSR arrays.

Ports ``read_network_from_txt``, ``network_to_csr``, ``save_csr_to_disk`` and
``load_csr_mmap`` from ``spp-dynamic.ipynb`` ("Reading and Conversion to CSR").
This module never generates networks -- it only reads files already present in
a ``network-save`` directory.

Networks in ``network-save/*.txt`` are edge lists, one ``u v`` pair per line,
1-indexed. Isolated nodes are preserved as a self-loop line ``i i`` (confirmed
against the notebook's own ``network-save/er500-graph.txt``); ``remove_selfloops``
strips those self-loops back out after they have served their purpose of
keeping the node present in the graph, so the resulting network has the
correct node count with isolated nodes at degree 0.
"""

from pathlib import Path

import networkx as nx
import numpy as np


def read_network_from_txt(path, one_indexed: bool = True, remove_selfloops: bool = True) -> nx.Graph:
    """Read a graph from a ``.txt`` edge-list file (``i j`` per line).

    Parameters
    ----------
    path : str or Path
        Path to the text file containing the network edges.
    one_indexed : bool
        If True (the format used by ``network-save/*.txt``), node IDs in the
        file are 1-indexed and are shifted to 0-index internally.
    remove_selfloops : bool
        If True, removes self-loops (edges ``i i``) after reading -- these are
        only present to keep isolated nodes in the file.
    """
    G = nx.Graph()
    with open(path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            i, j = map(int, parts[:2])
            if one_indexed:
                i, j = i - 1, j - 1
            G.add_edge(i, j)
    if remove_selfloops:
        G.remove_edges_from(nx.selfloop_edges(G))
    return G


def network_to_csr(G: nx.Graph):
    """Convert a NetworkX graph into 1-indexed CSR arrays: ``(deg, indptr, adj, twin, N)``.

    deg    : int32[N+1]   current degree (initially = total degree)
    indptr : int64[N+2]   offsets; indptr[N+1] = 2E
    adj    : int32[2E]    neighbors
    twin   : int32[2E]    "twin pointer" -- for each slot e in adj, twin[e] is
                          the slot of the reverse edge, so the back-edge can be
                          found in O(1) without a linear scan.
    """
    nodes = sorted(G.nodes())
    id_map = {old: i + 1 for i, old in enumerate(nodes)}
    N = len(nodes)

    deg = np.zeros(N + 1, dtype=np.int32)
    for u in nodes:
        deg[id_map[u]] = G.degree(u)

    indptr = np.zeros(N + 2, dtype=np.int64)
    for i in range(1, N + 1):
        indptr[i + 1] = indptr[i] + deg[i]

    total = int(indptr[N + 1])
    adj = np.zeros(total, dtype=np.int32)
    twin = np.zeros(total, dtype=np.int32)
    pos = np.zeros(N + 1, dtype=np.int64)

    for u, v in G.edges():
        iu = id_map[u]
        iv = id_map[v]
        e_uv = indptr[iu] + pos[iu]
        e_vu = indptr[iv] + pos[iv]
        adj[e_uv] = iv
        adj[e_vu] = iu
        twin[e_uv] = e_vu
        twin[e_vu] = e_uv
        pos[iu] += 1
        pos[iv] += 1

    return deg, indptr, adj, twin, N


def save_csr_to_disk(deg, indptr, adj, twin, base_path):
    """Persist the CSR arrays (incl. twin) as four ``.npy`` files for mmap sharing between workers."""
    base_path = Path(base_path)
    base_path.mkdir(parents=True, exist_ok=True)
    np.save(base_path / "deg.npy", deg)
    np.save(base_path / "indptr.npy", indptr)
    np.save(base_path / "adj.npy", adj)
    np.save(base_path / "twin.npy", twin)
    return str(base_path)


def load_csr_mmap(base_path):
    """Open the ``.npy`` CSR arrays as memory-mapped, read-only (incl. twin)."""
    base_path = Path(base_path)
    deg = np.load(base_path / "deg.npy", mmap_mode="r")
    indptr = np.load(base_path / "indptr.npy", mmap_mode="r")
    adj = np.load(base_path / "adj.npy", mmap_mode="r")
    twin = np.load(base_path / "twin.npy", mmap_mode="r")
    return deg, indptr, adj, twin


def load_network_csr(network_dir, network_file, one_indexed: bool = True):
    """Read ``{network_dir}/{network_file}`` and return its CSR representation.

    Convenience wrapper combining ``read_network_from_txt`` + ``network_to_csr``
    -- the single entry point the CLI/runner use to load a saved network.
    """
    path = Path(network_dir) / network_file
    G = read_network_from_txt(path, one_indexed=one_indexed)
    return network_to_csr(G)
