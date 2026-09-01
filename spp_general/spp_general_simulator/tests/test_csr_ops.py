import numpy as np

from spp_general_simulator.csr_ops import (
    bk_init,
    csr_to_graph,
    find_neighbor_pos,
    new_degree_bucket,
    remove_neighbor,
    remove_neighbor_twin,
)
from spp_general_simulator.selection.picking import pick_hub_rank1_bk, pick_node_njit, MODE_HUB


def test_find_neighbor_pos_and_remove_neighbor_star(star_csr):
    deg, indptr, adj, twin, N = star_csr
    # center is node 1 (0-indexed node 0 -> 1-indexed id 1).
    pos = find_neighbor_pos(1, 2, deg, indptr, adj)
    assert pos >= 1 and adj[indptr[1] + pos - 1] == 2

    remove_neighbor(1, pos, deg, indptr, adj)
    assert deg[1] == 5  # was 6 neighbors, one removed
    assert find_neighbor_pos(1, 2, deg, indptr, adj) == -1


def assert_live_csr_consistent(deg, indptr, adj, twin, N):
    """Every currently-live slot (k < deg[i]) must have a twin that is itself
    live and points back at i."""
    for i in range(1, N + 1):
        base = int(indptr[i])
        for k in range(int(deg[i])):
            slot = base + k
            neighbor = int(adj[slot])
            twin_slot = int(twin[slot])
            neighbor_base = int(indptr[neighbor])
            assert neighbor_base <= twin_slot < neighbor_base + int(deg[neighbor])
            assert int(adj[twin_slot]) == i
            assert int(twin[twin_slot]) == slot


def test_remove_neighbor_twin_keeps_twin_consistent(triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    bk_head, bk_next, bk_prev, bk_max_arr = new_degree_bucket(N)
    bk_init(N, deg, bk_head, bk_next, bk_prev, bk_max_arr)

    pos = find_neighbor_pos(1, 2, deg, indptr, adj)
    remove_neighbor_twin(1, pos, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr)
    pos = find_neighbor_pos(2, 1, deg, indptr, adj)
    remove_neighbor_twin(2, pos, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr)

    assert_live_csr_consistent(deg, indptr, adj, twin, N)

    # edge (1,2) must be gone from both sides.
    assert find_neighbor_pos(1, 2, deg, indptr, adj) == -1
    assert find_neighbor_pos(2, 1, deg, indptr, adj) == -1
    # edge (1,3) and (2,3) survive.
    assert find_neighbor_pos(1, 3, deg, indptr, adj) != -1
    assert find_neighbor_pos(2, 3, deg, indptr, adj) != -1


def test_degree_bucket_rank1_matches_bruteforce_after_removals(er_csr_n24):
    deg, indptr, adj, twin, N = er_csr_n24
    bk_head, bk_next, bk_prev, bk_max_arr = new_degree_bucket(N)
    bk_init(N, deg, bk_head, bk_next, bk_prev, bk_max_arr)

    def bruteforce_hub(exclude):
        return int(pick_node_njit(N, deg, MODE_HUB, 1, exclude))

    assert int(pick_hub_rank1_bk(bk_head, bk_next, bk_max_arr, -1)) == bruteforce_hub(-1)

    # remove a few edges (via plain remove_neighbor_twin) and re-check.
    for i in [1, 2, 3]:
        pos = find_neighbor_pos(i, int(adj[indptr[i]]), deg, indptr, adj)
        remove_neighbor_twin(i, pos, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr)
        assert int(pick_hub_rank1_bk(bk_head, bk_next, bk_max_arr, -1)) == bruteforce_hub(-1)


def test_csr_to_graph_reconstructs_edges(triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    G = csr_to_graph(deg, indptr, adj, N)
    assert set(G.nodes()) == {1, 2, 3}
    assert set(map(frozenset, G.edges())) == {frozenset((1, 2)), frozenset((2, 3)), frozenset((1, 3))}
