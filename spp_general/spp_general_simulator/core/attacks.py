from .selectors import select_node
from .bfs import get_path_of_pair, simple_bfs
from .utils import find_node, adjust_pair
from .distributions import geometric_distribution
from .rng import genrand64_real3


def core_pair_removal_loop(C, N, bond, edges, E, update_time, threshold,
                           attack_mode_1="random", attack_mode_2="random",
                           rank_1=1, rank_2=1):
    """
    Core routine for pair-removal attacks.
    """
    path, vec, tmp_vec = [0] * (N+1), [0] * (N+1), [0] * (N+1)
    visited, reset, nr_sp = [-1] * (N+1), [0] * (N+1), [0] * (N+1)
    dag = [[0] * (N+1 if i == 0 else (bond[0][i] + 1)) for i in range(N+1)]

    count_E, tau, num_failures = 0, 1, 0
    while num_failures < threshold:
        n = select_node(N, bond, mode=attack_mode_1, rank=rank_1)
        m = select_node(N, bond, mode=attack_mode_2, rank=rank_2, exclude=n)
        if n is None or m is None:
            edges[0][0] = 0
            return

        if bond[0][n] > bond[0][m]:
            n, m = m, n

        p = get_path_of_pair(n, m, N if C == -1 else C, N,
                             bond, path, vec, tmp_vec, visited, reset, dag, nr_sp)

        if p > 0:
            num_failures = 0
            for j in range(1, path[0]):
                s, t = path[j], path[j+1]
                v1, v2 = find_node(s, t, bond), find_node(t, s, bond)
                if v1 == -1 or v2 == -1:
                    continue
                bond[s][v1] = bond[s][bond[0][s]]
                bond[0][s] -= 1
                bond[t][v2] = bond[t][bond[0][t]]
                bond[0][t] -= 1

                count_E += 1
                edges[0][count_E], edges[1][count_E] = min(s, t), max(s, t)
                update_time[count_E] += tau
        else:
            num_failures += 1
        tau += 1

    for i in range(count_E + 1, E + 1):
        update_time[i] += tau
    edges[0][0] = count_E
    

def remove_pair_w_pair_info_v2(C, N, bond, pairs, edges, update_time):
    """
    Remove edges along shortest paths between precomputed node pairs.
    """
    path, vec, tmp_vec = [0] * (N+1), [0] * (N+1), [0] * (N+1)
    visited, reset, nr_sp = [-1] * (N+1), [0] * (N+1), [0] * (N+1)
    dag = [[0] * (N+1 if i == 0 else (bond[0][i] + 1)) for i in range(N+1)]
    for i in range(1, N+1):
        visited[i], dag[0][i], nr_sp[i] = -1, 0, 0

    interval, E = 0, edges[0][0]

    while pairs[0][0] > 0:
        num_pairs = pairs[0][0]
        link_prob = 2.0 * num_pairs / (N * (N - 1))
        interval += geometric_distribution(link_prob)

        q = int(genrand64_real3() * num_pairs + 1)
        n, m = pairs[0][q], pairs[1][q]
        if bond[0][n] > bond[0][m]:
            n, m = m, n

        p = get_path_of_pair(n, m, N if C == -1 else C, N, bond,
                             path, vec, tmp_vec, visited, reset, dag, nr_sp)

        if p > 0:
            for j in range(1, path[0]):
                s, t = path[j], path[j+1]
                v1, v2 = find_node(s, t, bond), find_node(t, s, bond)
                if v1 == -1 or v2 == -1:
                    continue
                bond[s][v1] = bond[s][bond[0][s]]
                bond[0][s] -= 1
                bond[t][v2] = bond[t][bond[0][t]]
                bond[0][t] -= 1

                E += 1
                edges[0][E], edges[1][E] = min(s, t), max(s, t)
                update_time[E] += interval

            control = simple_bfs(C, N, bond, n, m, vec, tmp_vec, visited, reset, dag, nr_sp)
            if control == 1:
                adjust_pair(pairs, q)
        else:
            adjust_pair(pairs, q)

        for i2 in range(1, reset[0] + 1):
            node = reset[i2]
            visited[node], dag[0][node], nr_sp[node] = -1, 0, 0

    edges[0][0] = E
