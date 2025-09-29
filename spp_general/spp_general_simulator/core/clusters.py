from .unionfind import tree_find_root

def modified_NZ_algorithm(N, edges, largest_cluster):
    """
    Modified Newman–Ziff algorithm to reconstruct clusters
    after edge removals.
    """
    root = [[i for i in range(N+1)], [1] * (N+1)]
    res, largest, av2 = [0, 0], 1, float(N - 1)

    E = edges[0][0]
    for e in range(E, 0, -1):
        n, m = edges[0][e], edges[1][e]
        av2 += largest * largest

        rn, sn = tree_find_root(n, root, res).copy()
        rm, sm = tree_find_root(m, root, res).copy()

        if rn != rm:
            av2 -= sn * sn + sm * sm
            if sn >= sm:
                root[0][rm] = rn
                root[1][rn] = sn + sm
            else:
                root[0][rn] = rm
                root[1][rm] = sn + sm
            largest = max(largest, sn + sm)
            av2 += (sn + sm) * (sn + sm)

        tmp = largest / float(N)
        largest_cluster[1][e] = tmp
        largest_cluster[2][e] = tmp**2
        largest_cluster[3][e] = tmp**3
        largest_cluster[4][e] = tmp**4

        av = float(N) - float(largest)
        av2 -= largest * largest
        if av > 0:
            largest_cluster[5][e] = av2/av