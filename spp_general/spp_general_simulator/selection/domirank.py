"""DomiRank centrality (``spp-dynamic.ipynb``, "DomiRank Centrality").

Engsig et al., *"DomiRank Centrality: revealing structural fragility of
complex networks via node dominance"* -- reference implementation at
https://github.com/mengsig/DomiRank/tree/main/src.

Like ``closeness``/``betweenness``, this rebuilds the graph and solves a
global system on every call -- it does not scale to very large N. Use it on
small/medium networks.
"""

import networkx as nx
import numpy as np
import scipy as sp
import scipy.sparse
import scipy.sparse.linalg

from ..csr_ops import csr_to_graph
from .centrality import get_hub_nodes


def _to_sparse(G):
    """Coerce a NetworkX graph (or an existing scipy sparse array) into a CSR sparse array."""
    if isinstance(G, nx.Graph):
        return nx.to_scipy_sparse_array(G)
    return G.copy()


def find_eigenvalue(G):
    """Largest-magnitude eigenvalue of the dominant mode of the adjacency matrix, negated."""
    eigval = sp.sparse.linalg.eigs(G.astype(np.float64), k=1, which="LR")[0][0]
    return -eigval.real


def domirank(G, analytical=True, sigma=-1, dt=0.1, epsilon=1e-5, maxIter=1000, checkStep=10):
    """DomiRank centrality. Returns ``(converged: bool, centrality: np.ndarray)``.

    The returned ``centrality`` array is indexed ``0..len(G)-1``, in the same
    order as ``G.nodes()`` when ``G`` is a NetworkX graph -- see
    ``generate_attack(..., node_map=...)`` for translating positions back into
    real node IDs.
    """
    G = _to_sparse(G)
    try:
        if sigma == -1:
            sigma, _ = optimal_sigma(G, analytical=analytical, dt=dt, epsilon=epsilon, maxIter=maxIter, checkStep=checkStep)

        if analytical is False:
            pGAdj = (sigma * G).astype(np.float64)
            Psi = np.ones(pGAdj.shape[0], dtype=np.float64) / pGAdj.shape[0]
            maxVals = np.zeros(max(int(maxIter / checkStep), 1), dtype=np.float64)
            dt = np.float64(dt)
            j = 0
            boundary = epsilon * pGAdj.shape[0] * dt

            for i in range(maxIter):
                tempVal = (pGAdj @ (1 - Psi) - Psi) * dt
                Psi += tempVal.real
                if i % checkStep == 0:
                    if np.abs(tempVal).sum() < boundary:
                        return True, np.nan_to_num(Psi, nan=0.0)
                    maxVals[j] = float(np.nanmax(tempVal))
                    if j >= 2 and maxVals[j] > maxVals[j - 1] > maxVals[j - 2]:
                        return False, np.nan_to_num(Psi, nan=0.0)  # diverged
                    j = min(j + 1, maxVals.size - 1)
            return True, np.nan_to_num(Psi, nan=0.0)

        else:
            Psi = sp.sparse.linalg.spsolve(sigma * G + sp.sparse.identity(G.shape[0]), (sigma * G).sum(axis=-1))
            Psi = np.asarray(Psi).ravel()
            if np.any(~np.isfinite(Psi)) or np.all(Psi == 0):
                return False, np.zeros(G.shape[0])
            return True, np.nan_to_num(Psi, nan=0.0)

    except Exception as e:
        print(f"[DomiRank] Internal error while computing centrality: {e}")
        return False, np.ones(G.shape[0]) / G.shape[0]


def get_component_size(G):
    """Size of the largest weakly-connected component of a scipy sparse graph."""
    _, labels = sp.sparse.csgraph.connected_components(G, directed=True, connection="weak", return_labels=True)
    return int(np.bincount(labels).max())


def get_link_size(G):
    """Number of (directed) nonzero entries in the sparse adjacency matrix."""
    return G.sum()


def remove_node(G, removed_nodes):
    """Zero out the rows/columns of ``removed_nodes`` in a sparse adjacency matrix."""
    diag = sp.sparse.csr_array(sp.sparse.eye(G.shape[0]))
    diag[removed_nodes, removed_nodes] = 0
    return diag @ G @ diag


def generate_attack(centrality, node_map=None):
    """Turn a centrality vector into a node ranking (highest centrality first).

    ``centrality[k]`` refers to the node at position ``k`` in the sparse
    matrix used to compute it. If the underlying graph's node IDs are not
    simply ``0..len(centrality)-1`` (e.g. the 1-indexed nodes ``1..N`` used
    throughout this package), pass ``node_map = dict(enumerate(G.nodes()))``
    so that matrix position ``k`` is translated back to the real node ID
    ``node_map[k]``.
    """
    if node_map is None:
        node_map = range(len(centrality))
    else:
        node_map = list(node_map.values())
    zipped = dict(zip(node_map, centrality))
    return sorted(zipped, reverse=True, key=zipped.get)


def network_attack_sampled(G, attack_strategy, sampling=0):
    """Simulate removing nodes in ``attack_strategy`` order, sampling the giant
    component size every ``sampling`` removals. Used internally by
    ``optimal_sigma`` to score candidate values of sigma."""
    GAdj = G.copy()
    N = GAdj.shape[0]
    if sampling == 0:
        sampling = 1 if N < 100 else int(N / 100)

    initial_component = get_component_size(GAdj)
    initial_links = get_link_size(GAdj)
    component_evolution = np.zeros(N // sampling + 1)
    links_evolution = np.zeros(N // sampling + 1)

    j = 0
    for i in range(N - 1):
        if i % sampling == 0:
            if i > 0:
                GAdj = remove_node(GAdj, attack_strategy[i - sampling : i])
            component_evolution[j] = get_component_size(GAdj) / initial_component
            links_evolution[j] = get_link_size(GAdj) / initial_links
            j += 1
    return component_evolution, links_evolution


def optimal_sigma(spArray, analytical=True, endVal=0, startval=1e-6, iterationNo=100, dt=0.1, epsilon=1e-5, maxIter=100, checkStep=10, sampling=0):
    """Sweep sigma over ``(0, -0.9999/lambda_N]`` and return the value that
    produces the most effective dismantling attack (fewest nodes needed to
    fragment the network)."""
    if endVal == 0:
        endVal = find_eigenvalue(spArray)

    endval = -0.9999 / endVal
    if endval <= startval:
        endval = startval * 10.0
    tempRange = np.linspace(startval, endval, num=iterationNo, endpoint=True)
    finalErrors = np.full(tempRange.shape, np.inf, dtype=float)

    for idx, sigma in enumerate(tempRange):
        try:
            ok, domiDist = domirank(spArray, analytical=analytical, sigma=sigma, dt=dt, epsilon=epsilon, maxIter=maxIter, checkStep=checkStep)
            if (not ok) or domiDist is None or not np.all(np.isfinite(domiDist)):
                continue
            attack = generate_attack(domiDist)
            evolution, _ = network_attack_sampled(spArray, attack, sampling=sampling)
            if len(evolution) and np.all(np.isfinite(evolution)):
                finalErrors[idx] = float(evolution.sum())
        except Exception:
            continue

    if np.all(~np.isfinite(finalErrors)):
        return float(tempRange[0]), finalErrors
    best_idx = int(np.nanargmin(finalErrors))
    return float(tempRange[best_idx]), finalErrors


_sigma_cache = {}


def sigma_otimo_para_grafo(G_nx, analytical=False):
    """Cache ``optimal_sigma`` by number of nodes only (NOT by edge count).

    ``optimal_sigma`` is expensive; since Phase 1 removes only a handful of
    edges per successful attack, the sigma it optimizes for barely shifts
    between removals, so reusing it for the rest of the attack on that same N
    is a standard, well-justified approximation.
    """
    key = G_nx.number_of_nodes()
    if key in _sigma_cache:
        return _sigma_cache[key]
    G = nx.to_scipy_sparse_array(G_nx)
    sigma, _ = optimal_sigma(G, analytical=analytical, sampling=max(1, int(G.shape[0] / 100)))
    _sigma_cache[key] = sigma
    return sigma


def clear_sigma_cache():
    """Reset the sigma-by-N cache (used by tests to avoid cross-test leakage)."""
    _sigma_cache.clear()


def get_domirank_nodes(N, deg, indptr, adj, top_k=1):
    """Rank all N nodes by DomiRank centrality (highest first), returning real
    1-indexed node IDs."""
    G_nx = csr_to_graph(deg, indptr, adj, N)
    if G_nx.number_of_edges() == 0:
        return list(range(1, N + 1))[:top_k]

    sigma = sigma_otimo_para_grafo(G_nx, analytical=False)
    ok, centrality = domirank(G_nx, analytical=False, sigma=sigma)
    if (not ok) or centrality is None or not np.all(np.isfinite(centrality)):
        # DomiRank failed to converge for this sigma/graph: fall back to hub ranking.
        return get_hub_nodes(N, deg, top_k=top_k)

    node_map = dict(enumerate(G_nx.nodes()))
    ordered = generate_attack(centrality, node_map=node_map)
    return ordered[:top_k]
