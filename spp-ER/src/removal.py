
####################################
# PAIR ADJUSTMENT
####################################

def adjust_pair(pairs, q):
    """
    void adjust_pair(unsigned long **pairs, unsigned long q)

    Adjusts the pair list after one pair has been processed or removed,
    maintaining the data structure consistent by swapping the last element
    into the removed position.
    """
    node1 = pairs[0][q]
    node2 = pairs[0][q]

    pairs[0][q] = pairs[0][pairs[0][0]]
    pairs[1][q] = pairs[1][pairs[0][0]]

    pairs[0][pairs[0][0]] = node1
    pairs[1][pairs[0][0]] = node2

    pairs[0][0] -= 1


####################################
# PAIR REMOVAL
####################################

def remove_pair_w_pair_info_v2(C, N, bond, pairs, edges, update_time):
    """
    void remove_pair_w_pair_info_v2(int C, int N, int **bond,
                                    unsigned long **pairs,
                                    int **edges,
                                    unsigned long long *update_time)

    Iteratively removes pairs of nodes from the network according to 
    the geometric distribution of link probabilities. For each selected 
    pair, it finds a shortest path (if any), removes the corresponding 
    edges, and updates the edge list with time stamps.
    """
    path = [0]*(N+1)
    vec = [0]*(N+1)
    tmp_vec = [0]*(N+1)
    visited = [-1]*(N+1)
    reset = [0]*(N+1)
    nr_sp = [0]*(N+1)

    dag = []
    # dag[0] = [0]*(N+1); dag[i] = [0]*(bond[0][i]+1)
    for i in range(N+1):
        if i == 0:
            dag.append([0]*(N+1))
        else:
            dag.append([0]*(bond[0][i]+1))

    for i in range(1, N+1):
        visited[i] = -1
        dag[0][i] = 0
        nr_sp[i] = 0

    interval = 0
    E = edges[0][0]

    while pairs[0][0] > 0:
        num_pairs = pairs[0][0]
        link_prob = 2.0 * float(num_pairs)/(float(N)*float(N - 1))
        interval += geometric_distribution(link_prob)

        q = int(genrand64_real3()*num_pairs + 1)
        n = pairs[0][q]
        m = pairs[1][q]

        source = n
        target = m
        if bond[0][source] > bond[0][target]:
            n, m = m, n

        if C == -1:
            p = get_path_of_pair(n, m, N, N, bond, path, vec, tmp_vec,
                                 visited, reset, dag, nr_sp)
        else:
            p = get_path_of_pair(n, m, C, N, bond, path, vec, tmp_vec,
                                 visited, reset, dag, nr_sp)

        if p > 0:
            for j in range(1, path[0]):
                s = path[j]
                t = path[j + 1]

                v = find_node(s, t, bond)
                bond[s][v] = bond[s][bond[0][s]]
                bond[0][s] -= 1

                v = find_node(t, s, bond)
                bond[t][v] = bond[t][bond[0][t]]
                bond[0][t] -= 1

                E += 1
                if s < t:
                    edges[0][E] = s
                    edges[1][E] = t
                else:
                    edges[0][E] = t
                    edges[1][E] = s
                update_time[E] += interval

            control = simple_bfs(C, N, bond, n, m, vec, tmp_vec,
                                 visited, reset, dag, nr_sp)
            if control == 1:
                adjust_pair(pairs, q)
        else:
            adjust_pair(pairs, q)

        for i in range(1, reset[0] + 1):
            node = reset[i]
            visited[node] = -1
            dag[0][node] = 0
            nr_sp[node] = 0

    edges[0][0] = E


def remove_pair_wo_pair_info_v2(C, N, bond, edges, E, update_time, threshold):
    """
    void remove_pair_wo_pair_info_v2(int C, int N, int **bond,
                                     int **edges, int E,
                                     unsigned long long *update_time,
                                     int threshold)

    Randomly removes pairs of nodes from the network without explicitly
    storing all possible pairs. For each randomly chosen pair, it attempts
    to find a shortest path and removes the corresponding edges if found.
    The process continues until a number of consecutive failures reaches
    the given threshold. Updates the edge list and edge time stamps.

    Args:
        C (int): maximum allowed path length (-1 means unlimited).
        N (int): number of nodes in the network.
        bond (list[list[int]]): adjacency representation of the network.
        edges (list[list[int]]): edge list updated after removals.
        E (int): initial number of edges.
        update_time (list[int]): timestamps of edge updates.
        threshold (int): maximum allowed number of consecutive failures.

    Updates:
        edges (list[list[int]]): shrinks as edges are removed.
        update_time (list[int]): updated with removal times.
    """
    path = [0]*(N+1)
    vec = [0]*(N+1)
    tmp_vec = [0]*(N+1)
    visited = [-1]*(N+1)
    reset = [0]*(N+1)
    nr_sp = [0]*(N+1)

    dag = []
    dag.append([0]*(N+1))
    for i in range(1, N+1):
        dag.append([0]*(bond[0][i]+1))
        visited[i] = -1
        dag[0][i] = 0
        nr_sp[i] = 0

    count_E = 0
    tau = 1
    num_failures = 0

    while num_failures < threshold:
        while True:
            n = int(genrand64_real3()*N) + 1
            m = int(genrand64_real3()*N) + 1
            if n != m:
                break

        source = n
        target = m
        if bond[0][source] > bond[0][target]:
            n, m = m, n

        if C == -1:
            p = get_path_of_pair(n, m, N, N, bond, path, vec, tmp_vec,
                                 visited, reset, dag, nr_sp)
        else:
            p = get_path_of_pair(n, m, C, N, bond, path, vec, tmp_vec,
                                 visited, reset, dag, nr_sp)

        if p > 0:
            num_failures = 0
            for j in range(1, path[0]):
                s = path[j]
                t = path[j + 1]

                v1 = find_node(s, t, bond)
                bond[s][v1] = bond[s][bond[0][s]]
                bond[0][s] -= 1

                v2 = find_node(t, s, bond)
                bond[t][v2] = bond[t][bond[0][t]]
                bond[0][t] -= 1

                count_E += 1
                if s < t:
                    edges[0][count_E] = s
                    edges[1][count_E] = t
                else:
                    edges[0][count_E] = t
                    edges[1][count_E] = s
                update_time[count_E] += tau
        else:
            num_failures += 1

        tau += 1

    # Adjust update_time for edges not removed
    for i in range(count_E + 1, E + 1):
        update_time[i] += tau

    edges[0][0] = count_E


####################################
#  FUNCTION find_all_possible_pairs
####################################

def find_all_possible_pairs(C, N, bond, pairs):
    """
    int find_all_possible_pairs(int C, int N, int **bond, unsigned long **pairs)

    Finds and stores all possible pairs of nodes that are connected 
    by a path within the network (according to the BFS search). 
    Each unique pair (i, j) with i < j is added to the pairs structure.

    Args:
        C (int): maximum allowed path length (-1 means unlimited).
        N (int): number of nodes in the network.
        bond (list[list[int]]): adjacency representation of the network.
        pairs (list[list[int]]): 2D structure that will store the pairs.

    Returns:
        int: the total number of pairs found.
    """
    num_pairs = 0
    dag = []
    list_pairs = []

    vec = [0]*(N+1)
    tmp_vec = [0]*(N+1)
    visited = [-1]*(N+1)
    reset = [0]*(N+1)
    nr_sp = [0]*(N+1)

    dag.append([0]*(N+1))
    for i in range(1, N+1):
        dag.append([0]*(bond[0][i]+1))

    list_pairs.append([0]*(N+1))
    for i in range(1, N+1):
        list_pairs.append([])
        list_pairs[i].append(0)

    for i in range(1, N+1):
        visited[i] = -1
        dag[0][i] = 0
        nr_sp[i] = 0

    target = -1

    for source in range(1, N+1):
        control = simple_bfs(C, N, bond, source, target,
                             vec, tmp_vec, visited, reset, dag, nr_sp)

        for k in range(1, reset[0] + 1):
            n = reset[k]
            if source < n and find_node(source, n, list_pairs) < 0:
                list_pairs[0][source] += 1
                list_pairs[source].append(n)
                num_pairs += 1

        for k in range(1, reset[0] + 1):
            node = reset[k]
            visited[node] = -1
            dag[0][node] = 0
            nr_sp[node] = 0

    # Expand pairs if needed
    while len(pairs[0]) < num_pairs + 1:
        pairs[0].append(0)
    while len(pairs[1]) < num_pairs + 1:
        pairs[1].append(0)

    num_pairs = 0
    for i in range(1, N+1):
        for j in range(1, list_pairs[0][i] + 1):
            num_pairs += 1
            pairs[0][num_pairs] = i
            pairs[1][num_pairs] = list_pairs[i][j]

    pairs[0][0] = num_pairs

    return num_pairs
