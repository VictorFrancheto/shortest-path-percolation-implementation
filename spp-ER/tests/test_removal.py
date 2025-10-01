from src.removal import (
    adjust_pair,
    find_all_possible_pairs,
    remove_pair_w_pair_info_v2,
    remove_pair_wo_pair_info_v2,
)
from src.utils import init_genrand64


def _line_graph_bond():
    """
    Build a tiny line graph 1-2-3 in the 'bond' format used by the code:
    - bond[0][i] = degree of node i
    - bond[i] = [0, neighbors...], neighbors start at index 1
    """
    N = 3
    bond = [[0] * (N + 1) for _ in range(N + 1)]
    for i in range(1, N + 1):
        bond[i] = [0]

    # edges: 1-2, 2-3
    bond[0][1] = 1; bond[1].append(2)
    bond[0][2] = 2; bond[2].extend([1, 3])
    bond[0][3] = 1; bond[3].append(2)
    return N, bond


def test_adjust_pair():
    # pairs holds count in pairs[0][0], then entries from index 1
    # here pairs: (1,2) and (1,3)
    pairs = [
        [2, 1, 1],  # first nodes: count=2, 1, 1
        [0, 2, 3],  # second nodes: -, 2, 3
    ]
    adjust_pair(pairs, 1)
    assert pairs[0][0] == 1  # count decreased by one


def test_find_all_possible_pairs():
    N, bond = _line_graph_bond()
    pairs = [[0], [0]]
    count = find_all_possible_pairs(C=2, N=N, bond=bond, pairs=pairs)
    # in a 1-2-3 line with C=2 we have (1,2), (2,3), (1,3) => 3 pairs
    assert count == 3
    assert pairs[0][0] == 3
    # all pairs must be i<j and distinct nodes
    for i in range(1, count + 1):
        a, b = pairs[0][i], pairs[1][i]
        assert a < b and a != b


def test_remove_pair_w_pair_info_v2_runs_and_updates():
    N, bond = _line_graph_bond()
    # enumerate all connected pairs explicitly (i<j): (1,2), (1,3), (2,3)
    pairs = [
        [3, 1, 1, 2],  # first nodes; count=3
        [0, 2, 3, 3],  # second nodes
    ]
    # edges removed will be written here; big enough buffer
    edges = [[0] * 16, [0] * 16]
    edges[0][0] = 0  # initial E
    update_time = [0] * 16

    init_genrand64(42)
    # Use C=2 (shortest paths exist in the line graph)
    initial_degree_sum = sum(bond[0][1:])
    remove_pair_w_pair_info_v2(2, N, bond, pairs, edges, update_time)

    # pairs should be exhausted by the loop
    assert pairs[0][0] == 0
    # some edges should have been recorded as removed
    assert edges[0][0] >= 1
    # degree sum should not increase
    assert sum(bond[0][1:]) <= initial_degree_sum


def test_remove_pair_wo_pair_info_v2_runs_and_bounded():
    N, bond = _line_graph_bond()
    # original undirected edges: 2 (1-2 and 2-3)
    E = 2
    edges = [[0] * 16, [0] * 16]
    update_time = [0] * 16

    init_genrand64(7)
    initial_degree_sum = sum(bond[0][1:])

    # small threshold; function stops after 'threshold' consecutive failures
    remove_pair_wo_pair_info_v2(2, N, bond, edges, E, update_time, threshold=3)

    # number of removed edges is recorded in edges[0][0] and cannot exceed E
    assert 0 <= edges[0][0] <= E
    # degrees should not increase
    assert sum(bond[0][1:]) <= initial_degree_sum
    # all E "slots" should have some time assigned (removed or not)
    for i in range(1, E + 1):
        assert update_time[i] >= 0
