"""Orchestrator (``spp-dynamic.ipynb``, cell 33).

Combines Phase 1 (``core_pair_removal_loop``, guided by
``attack_mode_1``/``attack_mode_2``) with Phase 2 (``lazy_pair_phase2``,
always uniform over the remaining pairs). All large buffers are allocated
once and reused by both phases.
"""

import numpy as np

from ..csr_ops import bk_init, new_degree_bucket
from .phase1 import core_pair_removal_loop
from .phase2 import count_reachable_pairs, lazy_pair_phase2


def efficient_pair_removal(C, N, deg, indptr, adj, twin, edges_a, edges_b, E, update_time, threshold, attack_mode_1="random", attack_mode_2="random", rank_1=1, rank_2=1):
    """Orchestrator: Phase 1 (targeted attack) + Phase 2 (lazy uniform sampler).

    Phase 2 never materializes the (i, j) list of reachable pairs. Instead it
    keeps only ``reachable_count[s]`` (N entries) plus a Fenwick tree for
    O(log N) weighted sampling. Large buffers are allocated ONCE and reused by
    both phases.
    """
    total_adj = int(indptr[N + 1])

    # buffers shared by BOTH phases
    buf_path = np.zeros(N + 1, dtype=np.int32)
    buf_path_slot = np.full(N + 1, -1, dtype=np.int32)
    buf_vec = np.zeros(N + 1, dtype=np.int32)
    buf_tmp_vec = np.zeros(N + 1, dtype=np.int32)
    buf_visited = -np.ones(N + 1, dtype=np.int32)
    buf_reset = np.zeros(N + 1, dtype=np.int32)
    buf_dag_cnt = np.zeros(N + 1, dtype=np.int32)
    buf_dag_adj = np.zeros(total_adj, dtype=np.int32)
    buf_dag_slot = np.zeros(total_adj, dtype=np.int32)
    buf_nr_sp = np.zeros(N + 1, dtype=np.int64)

    # degree bucket: HUB rank=1 in O(|bucket(max)|) ~ O(1); O(1) decrement.
    bk_head, bk_next, bk_prev, bk_max_arr = new_degree_bucket(N)
    bk_init(N, deg, bk_head, bk_next, bk_prev, bk_max_arr)

    # Phase 1
    core_pair_removal_loop(
        C,
        N,
        deg,
        indptr,
        adj,
        twin,
        edges_a,
        edges_b,
        E,
        update_time,
        threshold,
        attack_mode_1=attack_mode_1,
        attack_mode_2=attack_mode_2,
        rank_1=rank_1,
        rank_2=rank_2,
        buf_path=buf_path,
        buf_path_slot=buf_path_slot,
        buf_vec=buf_vec,
        buf_tmp_vec=buf_tmp_vec,
        buf_visited=buf_visited,
        buf_reset=buf_reset,
        buf_dag_cnt=buf_dag_cnt,
        buf_dag_adj=buf_dag_adj,
        buf_dag_slot=buf_dag_slot,
        buf_nr_sp=buf_nr_sp,
        bk_head=bk_head,
        bk_next=bk_next,
        bk_prev=bk_prev,
        bk_max_arr=bk_max_arr,
    )

    # Phase 2 -- lazy sampler (no materialized pair list)
    # size N+1: positions 1..N used; bit[0] is the Fenwick sentinel.
    reachable_count = np.zeros(N + 1, dtype=np.int64)
    fenwick = np.zeros(N + 1, dtype=np.int64)
    reach_list = np.zeros(N + 1, dtype=np.int32)

    n_active = count_reachable_pairs(C, N, deg, indptr, adj, reachable_count, fenwick, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp)

    lazy_pair_phase2(C, N, deg, indptr, adj, twin, reachable_count, fenwick, n_active, edges_a, edges_b, update_time, buf_path, buf_path_slot, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp, bk_head, bk_next, bk_prev, bk_max_arr, reach_list)
