def tree_find_root(n, root, res):
    """
    Union-Find with path compression.
    """
    if root[0][n] != n:
        root[0][n] = tree_find_root(root[0][n], root, res)[0]
    res[0], res[1] = root[0][n], root[1][root[0][n]]
    return res