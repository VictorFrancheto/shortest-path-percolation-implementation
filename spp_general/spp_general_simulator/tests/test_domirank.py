import networkx as nx
import pytest

from spp_general_simulator.network_loader import network_to_csr
from spp_general_simulator.selection.domirank import clear_sigma_cache, get_domirank_nodes


@pytest.fixture(autouse=True)
def _reset_sigma_cache():
    clear_sigma_cache()
    yield
    clear_sigma_cache()


def test_get_domirank_nodes_returns_a_valid_full_ranking(er_csr_n24):
    deg, indptr, adj, twin, N = er_csr_n24
    ordered = get_domirank_nodes(N, deg, indptr, adj, top_k=N)
    assert sorted(ordered) == list(range(1, N + 1))


def test_get_domirank_nodes_on_edgeless_graph_returns_identity_order():
    G = nx.Graph()
    G.add_nodes_from(range(5))
    deg, indptr, adj, twin, N = network_to_csr(G)
    assert get_domirank_nodes(N, deg, indptr, adj, top_k=3) == [1, 2, 3]


def test_get_domirank_nodes_favors_the_star_center(star_csr):
    deg, indptr, adj, twin, N = star_csr
    top = get_domirank_nodes(N, deg, indptr, adj, top_k=1)[0]
    assert top == 1
