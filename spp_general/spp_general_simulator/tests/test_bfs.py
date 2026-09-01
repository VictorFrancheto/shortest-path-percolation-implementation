from spp_general_simulator.dynamics.bfs import get_path_of_pair, sample_random_path, simple_bfs
from spp_general_simulator.rng import init_rng

from .conftest import alloc_bfs_buffers


def _run_bfs(C, N, deg, indptr, adj, source, target):
    b = alloc_bfs_buffers(N, indptr)
    control = simple_bfs(C, N, deg, indptr, adj, source, target, b.vec, b.tmp_vec, b.visited, b.reset, b.dag_cnt, b.dag_adj, b.dag_slot, b.nr_sp)
    return control, b


def test_simple_bfs_finds_target_within_reach(path5_csr):
    deg, indptr, adj, twin, N = path5_csr
    # 0-indexed path 0-1-2-3-4 -> 1-indexed ids 1-2-3-4-5, distance(1,5) = 4.
    control, b = _run_bfs(C=4, N=N, deg=deg, indptr=indptr, adj=adj, source=1, target=5)
    assert control == 2  # target found
    assert b.visited[5] == 4


def test_simple_bfs_respects_C_cutoff(path5_csr):
    deg, indptr, adj, twin, N = path5_csr
    control, b = _run_bfs(C=3, N=N, deg=deg, indptr=indptr, adj=adj, source=1, target=5)
    assert control == 1  # cut off before reaching target (distance is 4 > C=3)
    assert b.visited[5] < 0  # never visited


def test_simple_bfs_sweep_mode_visits_whole_component(path5_csr):
    deg, indptr, adj, twin, N = path5_csr
    control, b = _run_bfs(C=-1, N=N, deg=deg, indptr=indptr, adj=adj, source=1, target=-1)
    assert sorted(int(b.reset[i]) for i in range(1, b.reset[0] + 1)) == [1, 2, 3, 4, 5]


def test_get_path_of_pair_unique_path_on_chain(path5_csr):
    deg, indptr, adj, twin, N = path5_csr
    b = alloc_bfs_buffers(N, indptr)
    init_rng(0)
    length = get_path_of_pair(1, 5, 4, N, deg, indptr, adj, b.path, b.path_slot, b.vec, b.tmp_vec, b.visited, b.reset, b.dag_cnt, b.dag_adj, b.dag_slot, b.nr_sp)
    assert length == 5  # 5 nodes -> path of 4 edges
    nodes = [int(b.path[i]) for i in range(1, b.path[0] + 1)]
    assert nodes == [5, 4, 3, 2, 1]  # target -> ... -> source


def test_get_path_of_pair_returns_zero_when_unreachable(disconnected_csr):
    deg, indptr, adj, twin, N = disconnected_csr
    b = alloc_bfs_buffers(N, indptr)
    init_rng(0)
    length = get_path_of_pair(1, 3, N, N, deg, indptr, adj, b.path, b.path_slot, b.vec, b.tmp_vec, b.visited, b.reset, b.dag_cnt, b.dag_adj, b.dag_slot, b.nr_sp)
    assert length == 0


def test_bfs_counts_multiple_shortest_paths_on_4cycle(cycle4_csr):
    deg, indptr, adj, twin, N = cycle4_csr
    # 1-indexed ids 1,2,3,4 in a cycle 1-2-3-4-1: two shortest paths of length 2 from 1 to 3.
    control, b = _run_bfs(C=4, N=N, deg=deg, indptr=indptr, adj=adj, source=1, target=-1)
    assert control == 0  # frontier exhausts naturally (diameter 2 < C=4), no cutoff hit
    assert int(b.nr_sp[3]) == 2
    assert int(b.nr_sp[2]) == 1
    assert int(b.nr_sp[4]) == 1


def test_sample_random_path_reaches_both_intermediate_nodes_on_4cycle(cycle4_csr):
    deg, indptr, adj, twin, N = cycle4_csr
    seen = set()
    for seed in range(50):
        b = alloc_bfs_buffers(N, indptr)
        init_rng(seed)
        simple_bfs(4, N, deg, indptr, adj, 1, -1, b.vec, b.tmp_vec, b.visited, b.reset, b.dag_cnt, b.dag_adj, b.dag_slot, b.nr_sp)
        sample_random_path(4, N, indptr, b.dag_cnt, b.dag_adj, b.dag_slot, 1, 3, b.path, b.path_slot, b.nr_sp)
        assert b.path[0] == 3  # target, middle, source
        seen.add(int(b.path[2]))
    assert seen == {2, 4}
