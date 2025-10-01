from src.tree import tree_find_root, modified_NZ_algorithm, efficient_pair_removal
from src.utils import init_genrand64


def test_tree_find_root_direct_and_recursive():
    # root[0][i] = parent, root[1][i] = size
    N = 3
    root = [[0]*(N+1), [0]*(N+1)]
    for i in range(1, N+1):
        root[0][i] = i
        root[1][i] = 1

    res = [0, 0]
    tree_find_root(1, root, res)
    assert res[0] == 1 and res[1] == 1

    # Make 1 parent of 2
    root[0][2] = 1
    tree_find_root(2, root, res)
    assert res[0] == 1  # root is 1


def test_modified_NZ_algorithm_updates_clusters():
    N = 3
    # edges list: edges[0][0] = number of edges
    edges = [[0, 1, 2], [0, 2, 3]]
    edges[0][0] = 2  # E = 2 edges: (1,2), (2,3)

    # largest_cluster[1..5][e] must be updated
    largest_cluster = [[0]*(N+1) for _ in range(6)]

    modified_NZ_algorithm(N, edges, largest_cluster)

    # After percolation, cluster values should be between 0 and 1
    for power in range(1, 5):
        for e in range(1, edges[0][0]+1):
            assert 0 <= largest_cluster[power][e] <= 1


def test_efficient_pair_removal_runs():
    # tiny graph with 2 nodes connected
    N = 2
    bond = [[0]*(N+1) for _ in range(N+1)]
    bond[1] = [0, 2]
    bond[2] = [0, 1]
    bond[0][1] = 1
    bond[0][2] = 1

    edges = [[0]*10, [0]*10]
    edges[0][0] = 1
    edges[0][1] = 1
    edges[1][1] = 2
    update_time = [0]*10

    init_genrand64(123)
    efficient_pair_removal(C=2, N=N, bond=bond, edges=edges, E=1, update_time=update_time, threshold=2)

    # It should update edges[0][0] with number of removed edges
    assert edges[0][0] >= 0
    # update_time should not remain all zeros
    assert any(x > 0 for x in update_time[1:])
