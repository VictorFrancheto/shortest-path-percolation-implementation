from .rng import genrand64_real3



def simple_bfs(C, N, bond, source, target, vec, tmp_vec, visited, reset, dag, nr_sp):
    """
    BFS up to depth C or until reaching target.
    """
    int_distance, control = 0, 0
    vec[0], vec[1] = 1, source
    visited[source], dag[0][source], nr_sp[source] = 0, 0, 1
    reset[0], reset[1] = 1, source

    while vec[0] > 0 and control == 0:
        tmp_vec[0] = 0
        int_distance += 1
        if int_distance == C:
            control = 1
        for i in range(1, vec[0] + 1):
            n = vec[i]
            for j in range(1, bond[0][n] + 1):
                m = bond[n][j]
                if m == target:
                    control = 2
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
        for i2 in range(tmp_vec[0] + 1):
            vec[i2] = tmp_vec[i2]
    return control


def sample_random_path(C, N, dag, source, target, path, nr_sp):
    """
    Sample one shortest path from target to source in the BFS DAG.
    """
    control = 0
    path[0], path[1] = 1, target
    while control == 0:
        n = path[path[0]]
        if dag[0][n] > 0:
            T = sum(nr_sp[dag[n][i]] for i in range(1, dag[0][n] + 1))
            if T == 0:
                path[0] = 0
                return
            q = int(genrand64_real3() * T) + 1
            acc, found = 0, 0
            for i in range(1, dag[0][n] + 1):
                acc += nr_sp[dag[n][i]]
                if q <= acc:
                    found = dag[n][i]
                    break
            path[0] += 1
            path[path[0]] = found
            if path[0] == C + 1 or path[path[0]] == source:
                control = 1
        else:
            path[0] = 0
            return



def get_path_of_pair(source, target, C, N, bond, path, vec, tmp_vec, visited, reset, dag, nr_sp):
    """
    Compute and sample a shortest path between a source-target pair, limited by C.

    Parameters
    ----------
    source : int
        Starting node.
    target : int
        Target node.
    C : int
        Maximum BFS depth or path length.
    N : int
        Number of nodes.
    bond : list
        Bond adjacency structure.
    path, vec, tmp_vec, visited, reset, dag, nr_sp : list
        Auxiliary arrays for BFS and path sampling.

    Returns
    -------
    int
        Length of the sampled path (path[0]) or 0 if no path exists.
    """
    control = simple_bfs(C, N, bond, source, target, vec, tmp_vec, visited, reset, dag, nr_sp)
    path[0] = 0
    if control == 2:
        sample_random_path(C, N, dag, source, target, path, nr_sp)
    for i in range(1, reset[0] + 1):
        node = reset[i]
        visited[node] = -1
        dag[0][node] = 0
        nr_sp[node] = 0
    return path[0]