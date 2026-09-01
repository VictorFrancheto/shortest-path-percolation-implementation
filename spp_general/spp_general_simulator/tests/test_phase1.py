import networkx as nx
import numpy as np

from spp_general_simulator.csr_ops import bk_init, new_degree_bucket
from spp_general_simulator.dynamics.phase1 import core_pair_removal_loop
from spp_general_simulator.network_loader import network_to_csr
from spp_general_simulator.rng import init_rng

from .conftest import alloc_bfs_buffers


def _run_loop(C, N, deg, indptr, adj, twin, E, threshold, mode_1, mode_2, rank_1=1, rank_2=1):
    b = alloc_bfs_buffers(N, indptr)
    bk_head, bk_next, bk_prev, bk_max_arr = new_degree_bucket(N)
    bk_init(N, deg, bk_head, bk_next, bk_prev, bk_max_arr)
    edges_a = np.zeros(E + 1, dtype=np.int32)
    edges_b = np.zeros(E + 1, dtype=np.int32)
    update_time = np.zeros(E + 1, dtype=np.int64)
    count = core_pair_removal_loop(
        C, N, deg, indptr, adj, twin, edges_a, edges_b, E, update_time, threshold,
        attack_mode_1=mode_1, attack_mode_2=mode_2, rank_1=rank_1, rank_2=rank_2,
        buf_path=b.path, buf_path_slot=b.path_slot, buf_vec=b.vec, buf_tmp_vec=b.tmp_vec,
        buf_visited=b.visited, buf_reset=b.reset, buf_dag_cnt=b.dag_cnt, buf_dag_adj=b.dag_adj,
        buf_dag_slot=b.dag_slot, buf_nr_sp=b.nr_sp, bk_head=bk_head, bk_next=bk_next,
        bk_prev=bk_prev, bk_max_arr=bk_max_arr,
    )
    return count, edges_a, edges_b, update_time


def test_hub_hub_removes_triangle_edges_in_deterministic_order(triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    init_rng(0)
    threshold = 5
    E = 6
    count, edges_a, edges_b, update_time = _run_loop(C=1, N=N, deg=deg, indptr=indptr, adj=adj, twin=twin, E=E, threshold=threshold, mode_1="hub", mode_2="hub")

    assert count == 3  # every edge of the triangle gets removed
    assert edges_a[0] == 3
    removed = [(int(edges_a[i]), int(edges_b[i])) for i in range(1, 4)]
    assert removed == [(1, 2), (1, 3), (2, 3)]

    # tau (the internal clock) advances by 1 per loop iteration, success or
    # failure: each successful removal is stamped with the tau value active
    # at that iteration.
    assert update_time[1] == 1 and update_time[2] == 2 and update_time[3] == 3
    # after all edges are gone, every remaining draw fails deterministically
    # (hub always re-picks the same exhausted pair); the loop stops at
    # exactly `threshold` consecutive failures, and every unused slot is
    # stamped with the final tau.
    final_tau = 1 + (3 + threshold)
    assert update_time[4] == final_tau and update_time[5] == final_tau and update_time[6] == final_tau


def test_loop_stops_after_exact_threshold_when_no_path_ever_exists():
    G = nx.Graph()
    G.add_nodes_from(range(5))  # no edges at all -> every attempt fails
    deg, indptr, adj, twin, N = network_to_csr(G)
    init_rng(0)
    threshold = 6
    E = 4
    count, edges_a, edges_b, update_time = _run_loop(C=-1, N=N, deg=deg, indptr=indptr, adj=adj, twin=twin, E=E, threshold=threshold, mode_1="random", mode_2="random")

    assert count == 0
    assert edges_a[0] == 0
    # every slot is stamped with the tau value reached after exactly
    # `threshold` failed iterations.
    assert update_time[1] == threshold + 1


def test_closeness_closeness_python_fallback_removes_an_edge_on_connected_graph(er_csr_n24):
    deg, indptr, adj, twin, N = er_csr_n24
    E = int(indptr[N + 1] // 2)
    init_rng(0)
    # C is generous (not the point of this test) so the assertion below is
    # about the fallback mechanism working, not about hop-limit luck.
    count, edges_a, edges_b, update_time = _run_loop(C=N, N=N, deg=deg, indptr=indptr, adj=adj, twin=twin, E=E, threshold=3, mode_1="closeness", mode_2="closeness")

    assert count >= 1
    assert edges_a[0] == count
    for i in range(1, count + 1):
        assert edges_a[i] <= edges_b[i]
