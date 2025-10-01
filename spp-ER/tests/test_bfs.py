from src.bfs import simple_bfs, sample_random_path, get_path_of_pair
from src.utils import init_genrand64

def setup_line_graph(N=4):
    """
    Create a line graph: 1 - 2 - 3 - 4 in bond format.
    """
    bond = [[0] * (N+1) for _ in range(N+1)]
    for i in range(1, N+1):
        bond[i] = [0]  # start with dummy index 0

    # add edges: 1-2, 2-3, 3-4
    bond[0][1] = 1; bond[1].append(2)
    bond[0][2] = 2; bond[2].extend([1,3])
    bond[0][3] = 2; bond[3].extend([2,4])
    bond[0][4] = 1; bond[4].append(3)

    return bond


def test_simple_bfs_finds_target():
    N = 4
    C = 3
    bond = setup_line_graph(N)

    vec = [0]*(N+1)
    tmp_vec = [0]*(N+1)
    visited = [-1]*(N+1)
    reset = [0]*(N+1)
    dag = [[0]*(N+1) for _ in range(N+1)]
    nr_sp = [0]*(N+1)

    control = simple_bfs(C, N, bond, 1, 4, vec, tmp_vec, visited, reset, dag, nr_sp)
    assert control == 2  # found target


def test_sample_random_path_returns_path():
    N = 4
    C = 3
    bond = setup_line_graph(N)

    vec = [0]*(N+1)
    tmp_vec = [0]*(N+1)
    visited = [-1]*(N+1)
    reset = [0]*(N+1)
    dag = [[0]*(N+1) for _ in range(N+1)]
    nr_sp = [0]*(N+1)
    path = [0]*(N+1)

    # Run BFS to build DAG
    simple_bfs(C, N, bond, 1, 4, vec, tmp_vec, visited, reset, dag, nr_sp)

    init_genrand64(123)  # fix seed
    sample_random_path(C, N, dag, 1, 4, path, nr_sp)

    assert path[0] > 0
    assert path[1] == 4  # starts at target
    assert 1 in path[:path[0]+1]  # includes source


def test_get_path_of_pair():
    N = 4
    C = 3
    bond = setup_line_graph(N)

    vec = [0]*(N+1)
    tmp_vec = [0]*(N+1)
    visited = [-1]*(N+1)
    reset = [0]*(N+1)
    dag = [[0]*(N+1) for _ in range(N+1)]
    nr_sp = [0]*(N+1)
    path = [0]*(N+1)

    init_genrand64(456)  # reproducibility
    length = get_path_of_pair(1, 4, C, N, bond, path, vec, tmp_vec, visited, reset, dag, nr_sp)

    assert length > 0
    assert path[length] == 1 or 4 in path[:length+1]
