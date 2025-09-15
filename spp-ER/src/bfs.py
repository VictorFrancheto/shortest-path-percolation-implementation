####################################
#       BFS AND RELATED FUNCTIONS
####################################

from .utils import *

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