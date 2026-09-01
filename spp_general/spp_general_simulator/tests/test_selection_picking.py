import networkx as nx
import pytest

from spp_general_simulator.network_loader import network_to_csr
from spp_general_simulator.rng import init_rng
from spp_general_simulator.selection.picking import choose_source_target, select_node


def test_select_node_random_never_returns_excluded_node(star_csr):
    deg, indptr, adj, twin, N = star_csr
    init_rng(0)
    for _ in range(200):
        node = select_node(N, deg, indptr, adj, mode="random", exclude=1)
        assert node != 1
        assert 1 <= node <= N


def test_select_node_hub_picks_highest_degree_node(star_csr):
    deg, indptr, adj, twin, N = star_csr
    # center is node 1 (0-indexed node 0 -> 1-indexed id 1), degree 6.
    node = select_node(N, deg, indptr, adj, mode="hub", rank=1)
    assert node == 1


def test_select_node_hub_rank2_excludes_the_top_node():
    # Distinct degrees so rank=1/rank=2 are unambiguous: 0-indexed node 0 has
    # degree 3 (-> 1-indexed id 1), node 1 has degree 2 (-> id 2), the rest degree 1.
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 4)])
    deg, indptr, adj, twin, N = network_to_csr(G)
    assert select_node(N, deg, indptr, adj, mode="hub", rank=1) == 1
    assert select_node(N, deg, indptr, adj, mode="hub", rank=2) == 2


def test_select_node_hub_breaks_ties_by_smallest_id():
    # All nodes have degree 2 (a 4-cycle): rank=1 must be the smallest id.
    G = nx.cycle_graph(4)
    deg, indptr, adj, twin, N = network_to_csr(G)
    assert select_node(N, deg, indptr, adj, mode="hub", rank=1) == 1


def test_choose_source_target_rejects_n_below_2():
    G = nx.Graph()
    G.add_node(0)
    deg, indptr, adj, twin, N = network_to_csr(G)
    with pytest.raises(ValueError, match="N must be >= 2"):
        choose_source_target(N, deg, indptr, adj, "random-random")


def test_choose_source_target_source_and_target_always_differ(star_csr):
    deg, indptr, adj, twin, N = star_csr
    init_rng(1)
    for _ in range(50):
        source, target = choose_source_target(N, deg, indptr, adj, "random-random")
        assert source != target
        assert 1 <= source <= N and 1 <= target <= N


def test_choose_source_target_rank_beyond_node_count_raises(triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    with pytest.raises(ValueError, match="No candidate"):
        choose_source_target(N, deg, indptr, adj, "hub-hub", rank_1=1, rank_2=N + 10)
