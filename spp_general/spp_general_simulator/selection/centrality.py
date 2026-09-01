"""Degree/closeness/betweenness node ranking (``spp-dynamic.ipynb``, "CSR Utilities").

Each function returns node IDs (1-indexed) ordered from most to least central.
``domirank`` ranking lives in ``domirank.py`` since it needs its own eigen-solve
machinery.
"""

import networkx as nx
import numpy as np

from ..csr_ops import csr_to_graph


def get_hub_nodes(N, deg, top_k=1):
    """Top-k nodes by degree (descending), ties broken by smallest id."""
    order = np.argsort(-deg[1 : N + 1])
    return [int(order[i]) + 1 for i in range(min(top_k, N))]


def get_closeness_nodes(N, deg, indptr, adj, top_k=1):
    """Top-k nodes by closeness centrality (descending)."""
    G = csr_to_graph(deg, indptr, adj, N)
    clos = nx.closeness_centrality(G)
    ordered = sorted(clos.items(), key=lambda kv: kv[1], reverse=True)
    return [n for n, _ in ordered[:top_k]]


def get_betweenness_nodes(N, deg, indptr, adj, top_k=1, normalized=True):
    """Top-k nodes by betweenness centrality (descending)."""
    G = csr_to_graph(deg, indptr, adj, N)
    btw = nx.betweenness_centrality(G, normalized=normalized)
    ordered = sorted(btw.items(), key=lambda kv: kv[1], reverse=True)
    return [n for n, _ in ordered[:top_k]]
