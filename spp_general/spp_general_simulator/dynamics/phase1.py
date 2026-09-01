"""Phase 1 -- unified pairwise attack core (``spp-dynamic.ipynb``, cell 26-27).

At each iteration, choose a ``(source, target)`` pair according to
``attack_mode_1``/``attack_mode_2`` and remove the edges along a sampled
shortest path between them. Repeat until ``threshold`` consecutive failures
(no path found). For ``random``/``hub``, the whole loop runs inside a single
``@njit`` kernel; for ``closeness``/``betweenness``/``domirank``, a pure-Python
fallback calls ``select_node`` at every iteration (same rules, without the
``@njit`` acceleration).
"""

import numpy as np

from ..csr_ops import remove_neighbor_twin
from ..jit_compat import njit
from ..selection.picking import mode_to_code, pick_hub_rank1_bk, pick_node_njit, select_node
from .bfs import get_path_C3_bidir, get_path_of_pair


@njit(cache=True)
def _core_pair_removal_loop_njit(
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
    mode1_code,
    mode2_code,
    rank_1,
    rank_2,
    buf_path,
    buf_path_slot,
    buf_vec,
    buf_tmp_vec,
    buf_visited,
    buf_reset,
    buf_dag_cnt,
    buf_dag_adj,
    buf_dag_slot,
    buf_nr_sp,
    bk_head,
    bk_next,
    bk_prev,
    bk_max_arr,
    mark_src,
    mark_src_reset,
    mark_tgt_cnt,
    mark_tgt_reset,
):
    """Main pair-attack loop -- fully compiled.

    Active optimizations:
      * O(1) edge removal via the twin pointer + the slot captured during the BFS.
      * O(1)-amortized HUB rank=1 selection via the degree bucket.
      * For `C <= 3`, uses the bidirectional BFS instead of forward BFS.
    """
    count_E = 0
    tau = 1
    num_failures = 0
    C_eff = N if C == -1 else C
    use_bidir = C >= 1 and C <= 3

    use_bk_1 = mode1_code == 1 and rank_1 == 1
    use_bk_2 = mode2_code == 1 and rank_2 == 1

    while num_failures < threshold:
        if use_bk_1:
            n = pick_hub_rank1_bk(bk_head, bk_next, bk_max_arr, -1)
        else:
            n = pick_node_njit(N, deg, mode1_code, rank_1, -1)
        if use_bk_2:
            m = pick_hub_rank1_bk(bk_head, bk_next, bk_max_arr, n)
        else:
            m = pick_node_njit(N, deg, mode2_code, rank_2, n)
        if n < 0 or m < 0:
            edges_a[0] = 0
            return count_E

        if deg[n] > deg[m]:
            tmp = n
            n = m
            m = tmp

        if use_bidir:
            get_path_C3_bidir(n, m, C_eff, N, deg, indptr, adj, twin, buf_path, buf_path_slot, mark_src, mark_src_reset, mark_tgt_cnt, mark_tgt_reset)
            p = buf_path[0]
        else:
            p = get_path_of_pair(n, m, C_eff, N, deg, indptr, adj, buf_path, buf_path_slot, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp)

        if p > 0:
            num_failures = 0
            for j in range(1, buf_path[0]):
                s = buf_path[j]  # child (closer to target)
                t = buf_path[j + 1]  # parent (closer to source)
                slot_s_in_t = buf_path_slot[j + 1]  # absolute: adj[slot]==s
                slot_t_in_s = twin[slot_s_in_t]  # back-edge via twin
                ks = slot_t_in_s - indptr[s] + 1
                kt = slot_s_in_t - indptr[t] + 1
                if ks < 1 or ks > deg[s] or kt < 1 or kt > deg[t]:
                    continue  # edge already removed earlier along the path
                remove_neighbor_twin(s, ks, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr)
                remove_neighbor_twin(t, kt, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr)
                count_E += 1
                if s <= t:
                    edges_a[count_E] = s
                    edges_b[count_E] = t
                else:
                    edges_a[count_E] = t
                    edges_b[count_E] = s
                update_time[count_E] += tau
        else:
            num_failures += 1
        tau += 1

    for i in range(count_E + 1, E + 1):
        update_time[i] += tau
    edges_a[0] = count_E
    return count_E


def core_pair_removal_loop(
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
    attack_mode_1="random",
    attack_mode_2="random",
    rank_1=1,
    rank_2=1,
    buf_path=None,
    buf_path_slot=None,
    buf_vec=None,
    buf_tmp_vec=None,
    buf_visited=None,
    buf_reset=None,
    buf_dag_cnt=None,
    buf_dag_adj=None,
    buf_dag_slot=None,
    buf_nr_sp=None,
    bk_head=None,
    bk_next=None,
    bk_prev=None,
    bk_max_arr=None,
    mark_src=None,
    mark_src_reset=None,
    mark_tgt_cnt=None,
    mark_tgt_reset=None,
):
    """Wrapper. For `random`/`hub` calls the @njit kernel (with automatic
    bidirectional BFS when C <= 3). For `closeness`/`betweenness`/`domirank`,
    falls back to a Python loop that calls `select_node` directly (no @njit).
    """
    code1 = mode_to_code(attack_mode_1)
    code2 = mode_to_code(attack_mode_2)

    if code1 is not None and code2 is not None:
        if mark_src is None:
            mark_src = np.zeros(N + 1, dtype=np.int32)
        if mark_src_reset is None:
            mark_src_reset = np.zeros(N + 1, dtype=np.int32)
        if mark_tgt_cnt is None:
            mark_tgt_cnt = np.zeros(N + 1, dtype=np.int32)
        if mark_tgt_reset is None:
            mark_tgt_reset = np.zeros(N + 1, dtype=np.int32)
        return _core_pair_removal_loop_njit(
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
            code1,
            code2,
            rank_1,
            rank_2,
            buf_path,
            buf_path_slot,
            buf_vec,
            buf_tmp_vec,
            buf_visited,
            buf_reset,
            buf_dag_cnt,
            buf_dag_adj,
            buf_dag_slot,
            buf_nr_sp,
            bk_head,
            bk_next,
            bk_prev,
            bk_max_arr,
            mark_src,
            mark_src_reset,
            mark_tgt_cnt,
            mark_tgt_reset,
        )

    # ----- Python fallback for closeness / betweenness / domirank -----
    count_E = 0
    tau = 1
    num_failures = 0
    C_eff = N if C == -1 else C

    while num_failures < threshold:
        n = select_node(N, deg, indptr, adj, mode=attack_mode_1, rank=rank_1)
        m = select_node(N, deg, indptr, adj, mode=attack_mode_2, rank=rank_2, exclude=n)
        if n is None or m is None:
            edges_a[0] = 0
            return count_E

        if deg[n] > deg[m]:
            n, m = m, n

        p = get_path_of_pair(n, m, C_eff, N, deg, indptr, adj, buf_path, buf_path_slot, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp)

        if p > 0:
            num_failures = 0
            for j in range(1, buf_path[0]):
                s = int(buf_path[j])
                t = int(buf_path[j + 1])
                slot_s_in_t = int(buf_path_slot[j + 1])
                slot_t_in_s = int(twin[slot_s_in_t])
                ks = slot_t_in_s - int(indptr[s]) + 1
                kt = slot_s_in_t - int(indptr[t]) + 1
                if ks < 1 or ks > int(deg[s]) or kt < 1 or kt > int(deg[t]):
                    continue
                remove_neighbor_twin(s, ks, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr)
                remove_neighbor_twin(t, kt, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr)
                count_E += 1
                if s <= t:
                    edges_a[count_E] = s
                    edges_b[count_E] = t
                else:
                    edges_a[count_E] = t
                    edges_b[count_E] = s
                update_time[count_E] += tau
        else:
            num_failures += 1
        tau += 1

    for i in range(count_E + 1, E + 1):
        update_time[i] += tau
    edges_a[0] = count_E
    return count_E
