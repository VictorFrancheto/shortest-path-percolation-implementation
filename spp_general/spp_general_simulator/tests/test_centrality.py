import networkx as nx

from spp_general_simulator.csr_ops import csr_to_graph
from spp_general_simulator.selection.centrality import (
    get_betweenness_nodes,
    get_closeness_nodes,
    get_hub_nodes,
)


def test_get_hub_nodes_orders_by_degree_descending(er_csr_n24):
    deg, indptr, adj, twin, N = er_csr_n24
    ordered = get_hub_nodes(N, deg, top_k=N)
    degrees = [int(deg[n]) for n in ordered]
    assert degrees == sorted(degrees, reverse=True)


def test_get_closeness_nodes_matches_networkx_reference(er_csr_n24):
    deg, indptr, adj, twin, N = er_csr_n24
    G = csr_to_graph(deg, indptr, adj, N)
    expected_top = max(nx.closeness_centrality(G).items(), key=lambda kv: kv[1])[0]
    assert get_closeness_nodes(N, deg, indptr, adj, top_k=1)[0] == expected_top


def test_get_betweenness_nodes_matches_networkx_reference(er_csr_n24):
    deg, indptr, adj, twin, N = er_csr_n24
    G = csr_to_graph(deg, indptr, adj, N)
    expected_top = max(nx.betweenness_centrality(G, normalized=True).items(), key=lambda kv: kv[1])[0]
    assert get_betweenness_nodes(N, deg, indptr, adj, top_k=1)[0] == expected_top


def test_get_closeness_nodes_favors_star_center(star_csr):
    deg, indptr, adj, twin, N = star_csr
    assert get_closeness_nodes(N, deg, indptr, adj, top_k=1)[0] == 1


def test_get_betweenness_nodes_favors_star_center(star_csr):
    deg, indptr, adj, twin, N = star_csr
    assert get_betweenness_nodes(N, deg, indptr, adj, top_k=1)[0] == 1
