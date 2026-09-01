"""Phase 2 -- lazy uniform pair sampling (``spp-dynamic.ipynb``, cells 21-22, 28-29).

After Phase 1, samples uniformly among the pairs of nodes still reachable
within ``<= C`` hops, without ever materializing the full ``(i, j)`` pair
list -- which can require gigabytes of RAM on dense, large-N networks.
Instead it keeps only ``reachable_count[s]`` per source plus a Fenwick tree
for O(log N) weighted sampling. Like Phase 1, this phase does *not* depend on
``attack_mode_1``/``attack_mode_2`` -- sampling among the remaining pairs is
always uniform.
"""

import math

import numpy as np

from ..csr_ops import remove_neighbor_twin
from ..jit_compat import njit
from ..rng import genrand64_real3
from .bfs import sample_random_path, simple_bfs


def geometric_distribution(P: float):
    """Sample from a geometric distribution with parameter P.

    Returns k >= 1 with probability (1-P)^(k-1) * P. Returns -1 if P <= 0;
    always returns 1 if P == 1. Uses the Python-side RNG (genrand64_real3()).
    """
    if P <= 0:
        return -1
    if P == 1:
        return 1
    u = genrand64_real3()
    return 1 + int(math.floor(math.log(u) / math.log(1.0 - P)))


@njit(cache=True)
def _geometric_njit(P):
    """@njit version (uses Numba's internal RNG). Same semantics as geometric_distribution."""
    if P <= 0.0:
        return -1
    if P >= 1.0:
        return 1
    u = np.random.random()
    return 1 + int(np.floor(np.log(u) / np.log(1.0 - P)))


# ---------------------------------------------------------------------------
# Fenwick tree (BIT) -- O(log N) weighted sampling used by the lazy sampler
# ---------------------------------------------------------------------------


@njit(cache=True)
def fenwick_update(bit, i, delta):
    """Add `delta` at position i (1-indexed). bit.size must be N+1."""
    sz = bit.size
    while i < sz:
        bit[i] += delta
        i += i & (-i)


@njit(cache=True)
def fenwick_prefix(bit, i):
    """Sum bit[1..i]."""
    s = 0
    while i > 0:
        s += bit[i]
        i -= i & (-i)
    return s


@njit(cache=True)
def fenwick_find(bit, k):
    """Smallest i (1-indexed) such that prefix_sum[1..i] >= k.

    Returns 0 if k <= 0 or k > total.
    """
    N = bit.size - 1
    if k <= 0 or N <= 0:
        return 0
    log = 1
    while (log << 1) <= N:
        log <<= 1
    pos = 0
    cur = log
    while cur > 0:
        nxt = pos + cur
        if nxt <= N and bit[nxt] < k:
            pos = nxt
            k -= bit[pos]
        cur >>= 1
    return pos + 1


# ---------------------------------------------------------------------------
# Lazy pair sampler
# ---------------------------------------------------------------------------


@njit(cache=True)
def _count_reachable_pairs_njit(C, N, deg, indptr, adj, reachable_count, fenwick, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp):
    """For each source s in [1..N], count nodes j > s reachable within <= C hops.

    Does NOT materialize the (i, j) list -- only keeps ``reachable_count[s]``
    and the Fenwick tree for weighted sampling. Returns the total (= initial
    n_active).
    """
    C_eff = N if C == -1 else C
    total = 0
    for i in range(fenwick.size):
        fenwick[i] = 0
    for i in range(reachable_count.size):
        reachable_count[i] = 0

    for source in range(1, N + 1):
        simple_bfs(C_eff, N, deg, indptr, adj, source, -1, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp)
        cnt = 0
        for k in range(1, buf_reset[0] + 1):
            v = buf_reset[k]
            if source < v:
                cnt += 1
        reachable_count[source] = cnt
        if cnt > 0:
            fenwick_update(fenwick, source, cnt)
            total += cnt
        for k in range(1, buf_reset[0] + 1):
            node = buf_reset[k]
            buf_visited[node] = -1
            buf_dag_cnt[node] = 0
            buf_nr_sp[node] = 0
    return total


def count_reachable_pairs(C, N, deg, indptr, adj, reachable_count, fenwick, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp):
    """Python wrapper -- delegates to the @njit kernel."""
    return _count_reachable_pairs_njit(C, N, deg, indptr, adj, reachable_count, fenwick, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp)


@njit(cache=True)
def _lazy_pair_phase2_njit(
    C,
    N,
    deg,
    indptr,
    adj,
    twin,
    reachable_count,
    fenwick,
    n_active_init,
    edges_a,
    edges_b,
    update_time,
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
    reach_list,
):
    """Phase 2 with lazy pair sampling -- no materialized pair list.

    Each iteration:
      1. Sample source `s` ~ reachable_count via the Fenwick tree (O(log N)).
      2. BFS(s, target=-1) -- populates the DAG and buf_reset (nodes reachable <= C).
      3. Enumerate `reach_list` = {v in buf_reset : v > s}. Actual size `r`.
      4. Drift self-correction: if `r != reachable_count[s]`, adjust the
         Fenwick tree and n_active (pairs go stale as other sources remove edges).
      5. Sample destination `m` uniformly in reach_list[0..r-1].
      6. `sample_random_path(s, m)` reusing the DAG already in the buffers (zero BFS).
      7. Remove the edges along the path (O(1) swap-pop via twin).
      8. Post-removal BFS(s, m): if control==1 (no path), decrement
         reachable_count[s] by 1; otherwise (control==2) keep it.
    """
    interval = 0
    E = edges_a[0]
    C_eff = N if C == -1 else C
    n_active = n_active_init

    while n_active > 0:
        link_prob = 2.0 * n_active / (N * (N - 1))
        interval += _geometric_njit(link_prob)

        # 1. sample source s
        q = int(np.random.random() * n_active) + 1
        if q > n_active:
            q = n_active
        s = fenwick_find(fenwick, q)
        if s == 0:
            break  # no positive bucket left -- invariant broken, bail out

        # 2. BFS from s (target=-1, sweeps everything reachable within <= C)
        simple_bfs(C_eff, N, deg, indptr, adj, s, -1, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp)

        # 3. enumerate v > s in buf_reset
        r = 0
        for k in range(1, buf_reset[0] + 1):
            v = buf_reset[k]
            if s < v:
                reach_list[r] = v
                r += 1

        # 4. drift self-correction
        old_cnt = reachable_count[s]
        if r != old_cnt:
            delta = r - old_cnt
            fenwick_update(fenwick, s, delta)
            n_active += delta
            reachable_count[s] = r

        if r == 0:
            for i2 in range(1, buf_reset[0] + 1):
                node = buf_reset[i2]
                buf_visited[node] = -1
                buf_dag_cnt[node] = 0
                buf_nr_sp[node] = 0
            continue

        # 5. sample m uniformly in reach_list
        m_idx = int(np.random.random() * r)
        if m_idx >= r:
            m_idx = r - 1
        m = reach_list[m_idx]

        # 6. sample path s -> m from the DAG still resident in the buffers
        sample_random_path(C_eff, N, indptr, buf_dag_cnt, buf_dag_adj, buf_dag_slot, s, m, buf_path, buf_path_slot, buf_nr_sp)
        p = buf_path[0]

        # cleanup post-sampling BFS buffers
        for i2 in range(1, buf_reset[0] + 1):
            node = buf_reset[i2]
            buf_visited[node] = -1
            buf_dag_cnt[node] = 0
            buf_nr_sp[node] = 0

        if p > 0:
            # 7. remove edges along the path
            for j in range(1, buf_path[0]):
                ss = buf_path[j]  # child (closer to m)
                tt = buf_path[j + 1]  # parent (closer to s)
                slot_s_in_t = buf_path_slot[j + 1]
                slot_t_in_s = twin[slot_s_in_t]
                ks = slot_t_in_s - indptr[ss] + 1
                kt = slot_s_in_t - indptr[tt] + 1
                if ks < 1 or ks > deg[ss] or kt < 1 or kt > deg[tt]:
                    continue
                remove_neighbor_twin(ss, ks, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr)
                remove_neighbor_twin(tt, kt, deg, indptr, adj, twin, bk_head, bk_next, bk_prev, bk_max_arr)
                E += 1
                if ss <= tt:
                    edges_a[E] = ss
                    edges_b[E] = tt
                else:
                    edges_a[E] = tt
                    edges_b[E] = ss
                update_time[E] += interval

            # 8. post-removal BFS(s, m) -- checks whether the pair is still connected
            control = simple_bfs(C_eff, N, deg, indptr, adj, s, m, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp)
            for i2 in range(1, buf_reset[0] + 1):
                node = buf_reset[i2]
                buf_visited[node] = -1
                buf_dag_cnt[node] = 0
                buf_nr_sp[node] = 0
            if control == 1:
                # (s, m) no longer has a path -- decrement one pair
                fenwick_update(fenwick, s, -1)
                reachable_count[s] -= 1
                n_active -= 1
        else:
            # null path (very rare -- m was in reach_list); decrement for safety
            fenwick_update(fenwick, s, -1)
            reachable_count[s] -= 1
            n_active -= 1

    edges_a[0] = E
    return E


def lazy_pair_phase2(C, N, deg, indptr, adj, twin, reachable_count, fenwick, n_active, edges_a, edges_b, update_time, buf_path, buf_path_slot, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp, bk_head, bk_next, bk_prev, bk_max_arr, reach_list):
    """Python wrapper -- delegates to the @njit kernel."""
    return _lazy_pair_phase2_njit(C, N, deg, indptr, adj, twin, reachable_count, fenwick, n_active, edges_a, edges_b, update_time, buf_path, buf_path_slot, buf_vec, buf_tmp_vec, buf_visited, buf_reset, buf_dag_cnt, buf_dag_adj, buf_dag_slot, buf_nr_sp, bk_head, bk_next, bk_prev, bk_max_arr, reach_list)
