import numpy as np

from spp_general_simulator.csr_ops import bk_init, new_degree_bucket
from spp_general_simulator.dynamics.phase2 import (
    count_reachable_pairs,
    fenwick_find,
    fenwick_update,
    lazy_pair_phase2,
)
from spp_general_simulator.rng import init_rng

from .conftest import alloc_bfs_buffers


def test_fenwick_prefix_and_find_match_manual_weights():
    N = 4
    bit = np.zeros(N + 1, dtype=np.int64)
    weights = {1: 3, 3: 2, 4: 5}  # position 2 has weight 0
    for pos, w in weights.items():
        fenwick_update(bit, pos, w)

    # cumulative weight up to each k determines which bucket `find` should land on.
    assert fenwick_find(bit, 1) == 1
    assert fenwick_find(bit, 3) == 1
    assert fenwick_find(bit, 4) == 3
    assert fenwick_find(bit, 5) == 3
    assert fenwick_find(bit, 6) == 4
    assert fenwick_find(bit, 10) == 4
    assert fenwick_find(bit, 0) == 0
    assert fenwick_find(bit, -1) == 0


def test_count_reachable_pairs_matches_bruteforce_on_chain(path5_csr):
    deg, indptr, adj, twin, N = path5_csr
    b = alloc_bfs_buffers(N, indptr)
    reachable_count = np.zeros(N + 1, dtype=np.int64)
    fenwick = np.zeros(N + 1, dtype=np.int64)

    total = count_reachable_pairs(2, N, deg, indptr, adj, reachable_count, fenwick, b.vec, b.tmp_vec, b.visited, b.reset, b.dag_cnt, b.dag_adj, b.dag_slot, b.nr_sp)

    # chain 1-2-3-4-5, C=2: reachable (i<j) pairs are exactly those at distance 1 or 2.
    assert total == 7
    assert [int(reachable_count[i]) for i in range(1, 6)] == [2, 2, 2, 1, 0]


def test_lazy_pair_phase2_alone_empties_a_triangle_when_C_is_direct_only(triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    b = alloc_bfs_buffers(N, indptr)
    bk_head, bk_next, bk_prev, bk_max_arr = new_degree_bucket(N)
    bk_init(N, deg, bk_head, bk_next, bk_prev, bk_max_arr)

    E = 3
    edges_a = np.zeros(E + 1, dtype=np.int32)
    edges_b = np.zeros(E + 1, dtype=np.int32)
    update_time = np.zeros(E + 1, dtype=np.int64)
    reachable_count = np.zeros(N + 1, dtype=np.int64)
    fenwick = np.zeros(N + 1, dtype=np.int64)
    reach_list = np.zeros(N + 1, dtype=np.int32)

    init_rng(7)
    n_active = count_reachable_pairs(1, N, deg, indptr, adj, reachable_count, fenwick, b.vec, b.tmp_vec, b.visited, b.reset, b.dag_cnt, b.dag_adj, b.dag_slot, b.nr_sp)
    assert n_active == 3  # C=1 -> "reachable" means a direct edge; the triangle has 3.

    final_E = lazy_pair_phase2(1, N, deg, indptr, adj, twin, reachable_count, fenwick, n_active, edges_a, edges_b, update_time, b.path, b.path_slot, b.vec, b.tmp_vec, b.visited, b.reset, b.dag_cnt, b.dag_adj, b.dag_slot, b.nr_sp, bk_head, bk_next, bk_prev, bk_max_arr, reach_list)

    assert final_E == 3
    assert edges_a[0] == 3
    removed = {(int(edges_a[i]), int(edges_b[i])) for i in range(1, 4)}
    assert removed == {(1, 2), (1, 3), (2, 3)}
    assert deg[1] == 0 and deg[2] == 0 and deg[3] == 0


def test_lazy_pair_phase2_is_deterministic_given_same_seed(er_csr_n24):
    def run():
        deg, indptr, adj, twin, N = er_csr_n24
        deg = deg.copy()
        adj = adj.copy()
        twin = twin.copy()
        b = alloc_bfs_buffers(N, indptr)
        bk_head, bk_next, bk_prev, bk_max_arr = new_degree_bucket(N)
        bk_init(N, deg, bk_head, bk_next, bk_prev, bk_max_arr)
        E = int(indptr[N + 1] // 2)
        edges_a = np.zeros(E + 1, dtype=np.int32)
        edges_b = np.zeros(E + 1, dtype=np.int32)
        update_time = np.zeros(E + 1, dtype=np.int64)
        reachable_count = np.zeros(N + 1, dtype=np.int64)
        fenwick = np.zeros(N + 1, dtype=np.int64)
        reach_list = np.zeros(N + 1, dtype=np.int32)

        init_rng(99)
        n_active = count_reachable_pairs(2, N, deg, indptr, adj, reachable_count, fenwick, b.vec, b.tmp_vec, b.visited, b.reset, b.dag_cnt, b.dag_adj, b.dag_slot, b.nr_sp)
        lazy_pair_phase2(2, N, deg, indptr, adj, twin, reachable_count, fenwick, n_active, edges_a, edges_b, update_time, b.path, b.path_slot, b.vec, b.tmp_vec, b.visited, b.reset, b.dag_cnt, b.dag_adj, b.dag_slot, b.nr_sp, bk_head, bk_next, bk_prev, bk_max_arr, reach_list)
        return edges_a.copy(), edges_b.copy(), update_time.copy()

    a1, b1, t1 = run()
    a2, b2, t2 = run()
    assert np.array_equal(a1, a2)
    assert np.array_equal(b1, b2)
    assert np.array_equal(t1, t2)
