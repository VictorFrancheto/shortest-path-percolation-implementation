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