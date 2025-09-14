
#Importing libaries
import sys
import time
import os
import math
import random

####################################
#      Mersenne Twister 64-bit     #
# (or placeholder with random below)
####################################

NN = 312
mt = [0]*NN
mti = 0

def genrand64_int64():
    """
    In C, there would be a real implementation of the 64-bit Mersenne Twister.
    Here, we use a placeholder with random.getrandbits(64).
    If you want identical behavior, implement the full MT64.
    """
    return random.getrandbits(64)

def genrand64_real3():
    """
    In C: ((genrand64_int64() >> 12) + 0.5) * (1.0 / 4503599627370496.0).
    Placeholder using 64-bit random bits:
    """
    return genrand64_int64() / float(1 << 64)

def init_genrand64(seed):
    """
    Initialize the generator with a 64-bit seed.
    This function follows the standard initialization procedure
    used in the Mersenne Twister algorithm.
    """
    global mt, mti
    mt[0] = seed
    for mti in range(1, NN):
        mt[mti] = (6364136223846793005 * (mt[mti - 1] ^ (mt[mti - 1] >> 62)) + mti) & ((1 << 64) - 1)
        

####################################
#           NETWORK UTILITIES      #
####################################

def find_node(i, j, bond):
    """
    int find_node(int i, int j, int **bond)
    Returns index k if bond[i][k] == j, otherwise -1.
    """
    for k in range(1, bond[0][i] + 1):
        if bond[i][k] == j:
            return k
    return -1

def copy_network(N, origin_bond, copy_bond):
    """
    void copy_network(int N, int **origin_bond, int **copy_bond)
    Copies the bond structure from origin_bond to copy_bond.
    """
    for i in range(1, N+1):
        degree = origin_bond[0][i]
        copy_bond[0][i] = degree
        # Copy adjacency list (0..degree)
        copy_bond[i] = origin_bond[i][:degree+1]

def generate_ERgraph(N, bond, E):
    """
    void generate_ERgraph(int N, int **bond, int E)
    Generates an Erdős-Rényi graph with N nodes and E edges, populating bond.
    Does not update edges (if you need edges, update them manually).
    """
    for i in range(1, N+1):
        bond[0][i] = 0

    for _ in range(E):
        n = int(genrand64_real3() * N) + 1
        m = int(genrand64_real3() * N)
        control = 0
        while control == 0:
            m += 1
            if m > N:
                m = 1
            if n != m and find_node(n, m, bond) < 0:
                control = 1
        bond[0][n] += 1
        bond[n].append(m)
        bond[0][m] += 1
        bond[m].append(n)

def clean_time_stamp(update_time, E):
    """
    void clean_time_stamp(unsigned long long *time_stamp, int E)
    Sets update_time[i] = 0 for i = 1..E.
    """
    for i in range(1, E+1):
        update_time[i] = 0


####################################
#       BFS AND RELATED FUNCTIONS
####################################

def simple_bfs(C, N, bond, source, target, vec, tmp_vec, visited, reset, dag, nr_sp):
    """
    int simple_bfs(int C, int N, int **bond, int source, int target,
                   int *vec, int *tmp_vec, int *visited, int *reset,
                   int **dag, int *nr_sp)

    Performs a simple breadth-first search (BFS) from source to target,
    building a directed acyclic graph (DAG) of shortest paths and tracking
    the number of shortest paths to each node.
    
    Returns:
        control (int): 0 if not finished, 1 if max cost reached, 2 if target found.
    """
    int_distance = 0
    control = 0

    vec[0] = 1
    vec[1] = source
    visited[source] = 0
    dag[0][source] = 0
    nr_sp[source] = 1

    reset[0] = 1
    reset[1] = source

    while vec[0] > 0 and control == 0:
        tmp_vec[0] = 0
        int_distance += 1

        if int_distance == C:
            control = 1  # reached maximum cost

        for i in range(1, vec[0] + 1):
            n = vec[i]
            for j in range(1, bond[0][n] + 1):
                m = bond[n][j]

                if m == target:
                    control = 2  # target found

                if visited[m] < 0:
                    tmp_vec[0] += 1
                    tmp_vec[tmp_vec[0]] = m
                    visited[m] = visited[n] + 1
                    reset[0] += 1
                    reset[reset[0]] = m

                if visited[m] == int_distance:
                    dag[0][m] += 1
                    dag[m][dag[0][m]] = n
                    nr_sp[m] += nr_sp[n]

        for i in range(tmp_vec[0] + 1):
            vec[i] = tmp_vec[i]

    return control


def sample_random_path(C, N, dag, source, target, path, nr_sp):
    """
    void sample_random_path(int C, int N, int **dag, int source, int target,
                            int *path, int *nr_sp)

    Samples a random shortest path from source to target using the DAG
    constructed by BFS, with probabilities proportional to the number
    of shortest paths through each node.
    
    Updates:
        path (list[int]): path sampled from target back to source.
    """
    control = 0
    path[0] = 1
    path[1] = target

    while control == 0:
        n = path[path[0]]
        if dag[0][n] > 0:
            T = 0
            for i in range(1, dag[0][n] + 1):
                T += nr_sp[dag[n][i]]

            q = int(genrand64_real3() * T) + 1
            if q > T:
                q = 1

            i = 0
            acc = 0
            found = 0

            while found == 0:
                i += 1
                acc += nr_sp[dag[n][i]]
                if q <= acc:
                    found = dag[n][i]

            path[0] += 1
            path[path[0]] = found

            if path[0] == C + 1 or path[path[0]] == source:
                control = 1
        else:
            path[0] = 0
            return

def get_path_of_pair(source, target, C, N, bond, path, vec, tmp_vec, visited, reset, dag, nr_sp):
    """
    int get_path_of_pair(int source, int target, int C, int N, int **bond,
                         int *path, int *vec, int *tmp_vec, int *visited,
                         int *reset, int **dag, int *nr_sp)

    Computes a random shortest path between a given source and target node.
    It first runs a BFS to build the DAG of shortest paths, then samples
    one random path from source to target. After execution, the auxiliary
    arrays (visited, dag, nr_sp) are reset.

    Returns:
        path[0] (int): length of the sampled path (0 if no path found).
    """
    control = simple_bfs(C, N, bond, source, target, vec, tmp_vec, visited, reset, dag, nr_sp)
    path[0] = 0
    if control == 2:
        sample_random_path(C, N, dag, source, target, path, nr_sp)

    # reset
    for i in range(1, reset[0] + 1):
        node = reset[i]
        visited[node] = -1
        dag[0][node] = 0
        nr_sp[node] = 0

    return path[0]

####################################
# GEOMETRIC DISTRIBUTION
####################################

def geometric_distribution(P):
    """
    unsigned long long geometric_distribution(double P)

    Generates a random sample from a geometric distribution with 
    success probability P using the Mersenne Twister random generator.
    
    Returns:
        int: number of trials until the first success 
             (-1 if P <= 0, 1 if P == 1).
    """
    if P <= 0:
        return -1
    if P == 1:
        return 1
    u = genrand64_real3()
    interval = int(1 + math.floor(math.log(u)/math.log(1. - P)))
    return interval


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

####################################
#            TREE FUNCTIONS
####################################

def tree_find_root(n, root, res):
    """
    void tree_find_root(int n, int **root, int *res)

    Recursively finds the root of node n in a union-find (disjoint-set) 
    structure represented by root, storing the root index and size 
    in res.
    """
    if root[0][n] == n:
        res[0] = root[0][n]
        res[1] = root[1][n]
        return
    tree_find_root(root[0][n], root, res)


####################################
#        modified_NZ_algorithm
####################################

def modified_NZ_algorithm(N, edges, largest_cluster):
    """
    void modified_NZ_algorithm(int N, int **edges, double **largest_cluster)

    Performs a percolation analysis using a modified Newman-Ziff algorithm.
    Iteratively merges connected components (via union-find), tracks the 
    size of the largest cluster, and updates statistical measures 
    (1st to 4th powers of the largest cluster fraction and auxiliary variance).

    Args:
        N (int): number of nodes in the network.
        edges (list[list[int]]): list of edges with format edges[0][e], edges[1][e].
        largest_cluster (list[list[float]]): structure updated with cluster statistics.
    """
    root = [ [0]*(N+1), [0]*(N+1) ]
    res = [0, 0]

    larg = 1
    av2 = float(N - 1)

    # initialize root
    for i in range(1, N+1):
        root[0][i] = i
        root[1][i] = 1

    E = edges[0][0]
    for e in range(E, 0, -1):
        n = edges[0][e]
        m = edges[1][e]

        # av2 += larg^2
        av2 += float(larg)*float(larg)

        # find roots of n and m
        tree_find_root(n, root, res)
        rn, sn = res[0], res[1]

        tree_find_root(m, root, res)
        rm, sm = res[0], res[1]

        if rn != rm:
            av2 -= float(sn)*float(sn)
            av2 -= float(sm)*float(sm)

            if sn > sm:
                root[0][rm] = rn
                root[1][rm] = 1
                root[1][rn] = sn + sm
            else:
                root[0][rn] = rm
                root[1][rn] = 1
                root[1][rm] = sn + sm

            if sn + sm > larg:
                larg = sn + sm

        tmp = float(larg)/float(N)
        largest_cluster[1][e] = tmp
        largest_cluster[2][e] = tmp*tmp
        largest_cluster[3][e] = tmp*tmp*tmp
        largest_cluster[4][e] = tmp*tmp*tmp*tmp

        av = float(N) - float(larg)
        if rn != rm:
            av2 += float(sn+sm)*float(sn+sm)
        av2 -= float(larg)*float(larg)
        if av > 0:
            largest_cluster[5][e] = av2/av


####################################
# efficient_pair_removal
####################################

def efficient_pair_removal(C, N, bond, edges, E, update_time, threshold):
    """
    void efficient_pair_removal(int C, int N, int **bond, int **edges, int E,
                                unsigned long long *update_time, int threshold)

    Performs an efficient two-phase pair removal process:
      1) Random removal without storing all possible pairs 
         (remove_pair_wo_pair_info_v2).
      2) Enumerates all possible pairs (find_all_possible_pairs) and 
         continues the removal with explicit pair tracking 
         (remove_pair_w_pair_info_v2).

    Args:
        C (int): maximum allowed path length (-1 means unlimited).
        N (int): number of nodes in the network.
        bond (list[list[int]]): adjacency representation of the network.
        edges (list[list[int]]): edge list.
        E (int): initial number of edges.
        update_time (list[int]): timestamps of edge updates.
        threshold (int): maximum allowed number of consecutive failures.
    """
    # Phase 1
    remove_pair_wo_pair_info_v2(C, N, bond, edges, E, update_time, threshold)

    # Phase 2 (a)
    # In C, pairs would be allocated with malloc.
    # In Python, we define it as a nested list [[], []].
    pairs = [ [0], [0] ]
    num_pairs = find_all_possible_pairs(C, N, bond, pairs)
    remove_pair_w_pair_info_v2(C, N, bond, pairs, edges, update_time)
