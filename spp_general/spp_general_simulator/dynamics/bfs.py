"""BFS and shortest-path sampling (``spp-dynamic.ipynb``, "BFS and Shortest-Path Sampling").

``simple_bfs`` is the main hot loop of the simulation: it explores up to depth
``C`` (or until it reaches ``target``, or exhausts the component when
``target == -1``), while recording the shortest-path DAG (``dag_adj``/``dag_slot``)
that ``sample_random_path`` then uses to sample a shortest path between two
nodes *uniformly at random* among all shortest paths connecting them.

``_get_path_C3_bidir_njit`` is a bidirectional shortcut used automatically for
``1 <= C <= 3`` (dense graphs make a forward BFS to depth 3 visit almost the
whole graph); it samples from the exact same distribution -- uniformly among
shortest paths of length ``d <= C`` -- just faster.
"""

import numpy as np

from ..jit_compat import njit


@njit(cache=True)
def simple_bfs(C, N, deg, indptr, adj, source, target, vec, tmp_vec, visited, reset, dag_cnt, dag_adj, dag_slot, nr_sp):
    """BFS up to depth C or until reaching ``target`` (-1 to sweep everything).

    Records, in the same pass, the shortest-path DAG:
        dag_adj[base_m + i]  = parent node n
        dag_slot[base_m + i] = ABSOLUTE slot in adj where n found m
                                (i.e., adj[dag_slot[..]] == m, and
                                 twin[dag_slot[..]] is n's slot in m's adj).
    """
    int_distance = 0
    control = 0
    vec[0] = 1
    vec[1] = source
    visited[source] = 0
    dag_cnt[source] = 0
    nr_sp[source] = 1
    reset[0] = 1
    reset[1] = source

    while vec[0] > 0 and control == 0:
        tmp_vec[0] = 0
        int_distance += 1
        if int_distance == C:
            control = 1
        for i in range(1, vec[0] + 1):
            n = vec[i]
            base_n = indptr[n]
            d_n = deg[n]
            for k in range(d_n):
                slot_nk = base_n + k
                m = adj[slot_nk]
                if m == target:
                    control = 2
                if visited[m] < 0:
                    tmp_vec[0] += 1
                    tmp_vec[tmp_vec[0]] = m
                    visited[m] = visited[n] + 1
                    reset[0] += 1
                    reset[reset[0]] = m
                if visited[m] == int_distance:
                    base_m = indptr[m]
                    dpos = dag_cnt[m]
                    dag_adj[base_m + dpos] = n
                    dag_slot[base_m + dpos] = slot_nk
                    dag_cnt[m] += 1
                    nr_sp[m] += nr_sp[n]
        cnt = tmp_vec[0]
        vec[0] = cnt
        for i2 in range(1, cnt + 1):
            vec[i2] = tmp_vec[i2]
    return control


@njit(cache=True)
def sample_random_path(C, N, indptr, dag_cnt, dag_adj, dag_slot, source, target, path, path_slot, nr_sp):
    """Sample one shortest path from target -> source in the BFS DAG.

    path[j]      : node
    path_slot[j] : absolute slot in adj where edge (path[j] -> path[j-1]) is
                   stored in path[j]'s adjacency vector. path_slot[1] = -1
                   (target has no "parent to the left").
    """
    path[0] = 1
    path[1] = target
    path_slot[1] = -1
    control = 0
    while control == 0:
        n = path[path[0]]
        d_n = dag_cnt[n]
        if d_n > 0:
            base_n = indptr[n]
            T = 0
            for i in range(d_n):
                T += nr_sp[dag_adj[base_n + i]]
            if T == 0:
                path[0] = 0
                return
            q = int(np.random.random() * T) + 1
            acc = 0
            found = 0
            found_slot = -1
            for i in range(d_n):
                acc += nr_sp[dag_adj[base_n + i]]
                if q <= acc:
                    found = dag_adj[base_n + i]
                    found_slot = dag_slot[base_n + i]
                    break
            path[0] += 1
            path[path[0]] = found
            path_slot[path[0]] = found_slot
            if path[0] == C + 1 or path[path[0]] == source:
                control = 1
        else:
            path[0] = 0
            return


@njit(cache=True)
def get_path_of_pair(source, target, C, N, deg, indptr, adj, path, path_slot, vec, tmp_vec, visited, reset, dag_cnt, dag_adj, dag_slot, nr_sp):
    """Run the BFS, sample a path if one exists, and clear the touched buffers."""
    control = simple_bfs(C, N, deg, indptr, adj, source, target, vec, tmp_vec, visited, reset, dag_cnt, dag_adj, dag_slot, nr_sp)
    path[0] = 0
    if control == 2:
        sample_random_path(C, N, indptr, dag_cnt, dag_adj, dag_slot, source, target, path, path_slot, nr_sp)
    for i in range(1, reset[0] + 1):
        node = reset[i]
        visited[node] = -1
        dag_cnt[node] = 0
        nr_sp[node] = 0
    return path[0]


@njit(cache=True)
def get_path_C3_bidir(source, target, C, N, deg, indptr, adj, twin, path, path_slot, mark_src, mark_src_reset, mark_tgt_cnt, mark_tgt_reset):
    """Bidirectional shortest-path sampler for ``d in {1, 2, 3}``.

    Used in place of ``get_path_of_pair`` when ``C <= 3``: explores N(source)
    and N(target) and looks for the meeting point within one intermediate
    edge, instead of a forward BFS that (on dense graphs) visits almost the
    entire graph. Semantics equivalent to ``simple_bfs`` + ``sample_random_path``:
    samples uniformly among shortest paths of length ``d <= C``.

    Output format (same as ``sample_random_path``):
        path[0]      = number of nodes = d + 1
        path[1]      = target
        path[d+1]    = source
        path_slot[1] = -1
        path_slot[j+1] = ABSOLUTE slot in `adj` where `adj[slot] == path[j]`.

    Returns ``d in {1, 2, 3}`` if a path was found, 0 otherwise.

    Buffers ``mark_src`` (int32[N+1]) and ``mark_tgt_cnt`` (int32[N+1]) MUST be
    zeroed on entry; they are cleared before returning.
    """
    path[0] = 0
    if source == target:
        return 0

    base_s = indptr[source]
    deg_s = deg[source]

    # === d = 1: direct source-target edge ===
    for k in range(deg_s):
        if adj[base_s + k] == target:
            path[0] = 2
            path[1] = target
            path[2] = source
            path_slot[1] = -1
            path_slot[2] = base_s + k
            return 1

    if C < 2:
        return 0

    # === Mark N(source) with slot+1 (encoded; 0 => absent) ===
    mark_src_reset[0] = 0
    for k in range(deg_s):
        v = adj[base_s + k]
        mark_src[v] = base_s + k + 1
        mark_src_reset[0] += 1
        mark_src_reset[mark_src_reset[0]] = v

    base_t = indptr[target]
    deg_t = deg[target]

    # === d = 2: common neighbor ===
    num_common = 0
    for k in range(deg_t):
        u = adj[base_t + k]
        if mark_src[u] > 0:
            num_common += 1

    if num_common > 0:
        choice = int(np.random.random() * num_common) + 1
        cur = 0
        chosen_u = 0
        for k in range(deg_t):
            u = adj[base_t + k]
            if mark_src[u] > 0:
                cur += 1
                if cur == choice:
                    chosen_u = u
                    break

        base_u = indptr[chosen_u]
        deg_u = deg[chosen_u]
        slot_t_in_u = -1
        for k in range(deg_u):
            if adj[base_u + k] == target:
                slot_t_in_u = base_u + k
                break

        path[0] = 3
        path[1] = target
        path[2] = chosen_u
        path[3] = source
        path_slot[1] = -1
        path_slot[2] = slot_t_in_u
        path_slot[3] = mark_src[chosen_u] - 1

        for i in range(1, mark_src_reset[0] + 1):
            mark_src[mark_src_reset[i]] = 0
        return 2

    if C < 3:
        for i in range(1, mark_src_reset[0] + 1):
            mark_src[mark_src_reset[i]] = 0
        return 0

    # === d = 3: source-w-u-target with w in N(source), u in N(target), (w,u) in E ===
    mark_tgt_reset[0] = 0
    total = 0
    for k in range(deg_t):
        u = adj[base_t + k]
        if u == source:
            continue
        base_u = indptr[u]
        deg_u = deg[u]
        cnt = 0
        for j in range(deg_u):
            w = adj[base_u + j]
            if w == target:
                continue
            if mark_src[w] > 0:
                cnt += 1
        if cnt > 0:
            mark_tgt_cnt[u] = cnt
            mark_tgt_reset[0] += 1
            mark_tgt_reset[mark_tgt_reset[0]] = u
            total += cnt

    if total == 0:
        for i in range(1, mark_src_reset[0] + 1):
            mark_src[mark_src_reset[i]] = 0
        return 0

    q = int(np.random.random() * total) + 1
    acc = 0
    chosen_u = 0
    for i in range(1, mark_tgt_reset[0] + 1):
        u = mark_tgt_reset[i]
        acc += mark_tgt_cnt[u]
        if q <= acc:
            chosen_u = u
            break

    cnt_u = mark_tgt_cnt[chosen_u]
    q2 = int(np.random.random() * cnt_u) + 1
    base_u = indptr[chosen_u]
    deg_u = deg[chosen_u]
    cur = 0
    chosen_w = 0
    slot_w_in_u = -1
    for j in range(deg_u):
        w = adj[base_u + j]
        if w == target:
            continue
        if mark_src[w] > 0:
            cur += 1
            if cur == q2:
                chosen_w = w
                slot_w_in_u = base_u + j
                break

    slot_t_in_u = -1
    for k in range(deg_u):
        if adj[base_u + k] == target:
            slot_t_in_u = base_u + k
            break

    slot_u_in_w = twin[slot_w_in_u]

    path[0] = 4
    path[1] = target
    path[2] = chosen_u
    path[3] = chosen_w
    path[4] = source
    path_slot[1] = -1
    path_slot[2] = slot_t_in_u
    path_slot[3] = slot_u_in_w
    path_slot[4] = mark_src[chosen_w] - 1

    for i in range(1, mark_src_reset[0] + 1):
        mark_src[mark_src_reset[i]] = 0
    for i in range(1, mark_tgt_reset[0] + 1):
        mark_tgt_cnt[mark_tgt_reset[i]] = 0
    return 3
