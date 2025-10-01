from src.network import (
    find_node, copy_network, generate_ERgraph,
    clean_time_stamp, geometric_distribution
)
from src.utils import init_genrand64


def test_find_node():
    bond = [[0, 1, 2], [0, 2], [0, 1]]
    bond[0] = [0, 1, 1]  # degrees
    assert find_node(1, 2, bond) == 1
    assert find_node(2, 1, bond) == 1
    assert find_node(1, 3, bond) == -1


def test_copy_network():
    N = 2
    origin_bond = [[0]*(N+1) for _ in range(N+1)]
    origin_bond[0][1] = 1
    origin_bond[1] = [0, 2]
    origin_bond[0][2] = 1
    origin_bond[2] = [0, 1]

    copy_bond = [[0]*(N+1) for _ in range(N+1)]
    copy_network(N, origin_bond, copy_bond)

    assert copy_bond[0][1] == 1
    assert copy_bond[1][1] == 2
    assert copy_bond[0][2] == 1
    assert copy_bond[2][1] == 1


def test_generate_ERgraph_creates_edges():
    N = 4
    E = 2

    # Correct initialization: each bond[i] starts with a dummy 0
    bond = [[0] * (N+1) for _ in range(N+1)]
    for i in range(1, N+1):
        bond[i] = [0]  # start with dummy at index 0

    init_genrand64(42)  # seed reproducibility
    generate_ERgraph(N, bond, E)

    total_edges = sum(bond[0][1:])
    # undirected edges counted twice
    assert total_edges == 2 * E


def test_clean_time_stamp():
    E = 5
    ts = [i for i in range(E+1)]
    clean_time_stamp(ts, E)
    assert all(val == 0 for val in ts[1:])


def test_geometric_distribution_values():
    init_genrand64(1234)
    assert geometric_distribution(1) == 1
    assert geometric_distribution(0) == -1
    val = geometric_distribution(0.5)
    assert isinstance(val, int)
    assert val >= 1
