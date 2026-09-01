import numpy as np
import pytest

from spp_general_simulator.dynamics.clusters import modified_NZ_algorithm
from spp_general_simulator.dynamics.orchestrator import efficient_pair_removal
from spp_general_simulator.rng import init_rng


def _alloc_and_run(N, indptr, deg, adj, twin, C, threshold, mode_1, mode_2, seed):
    E = int(indptr[N + 1] // 2)
    deg = deg.copy()
    adj = adj.copy()
    twin = twin.copy()
    edges_a = np.zeros(E + 1, dtype=np.int32)
    edges_b = np.zeros(E + 1, dtype=np.int32)
    update_time = np.zeros(E + 1, dtype=np.int64)
    init_rng(seed)
    efficient_pair_removal(C, N, deg, indptr, adj, twin, edges_a, edges_b, E, update_time, threshold, attack_mode_1=mode_1, attack_mode_2=mode_2)
    return E, edges_a, edges_b, update_time, deg


@pytest.mark.parametrize("mode_1,mode_2", [("random", "random"), ("hub", "hub"), ("hub", "random")])
def test_full_pipeline_removes_every_edge_regardless_of_strategy(er_csr_n24, mode_1, mode_2):
    deg, indptr, adj, twin, N = er_csr_n24
    E, edges_a, edges_b, update_time, deg_after = _alloc_and_run(N, indptr, deg, adj, twin, C=3, threshold=5, mode_1=mode_1, mode_2=mode_2, seed=1)

    # Phase 2 only stops once no pair is reachable within C hops -- with C>=1
    # that is only possible once every edge is gone, regardless of how much
    # Phase 1 (and its selection strategy) managed to remove on its own.
    assert edges_a[0] == E
    assert np.all(deg_after[1 : N + 1] == 0)


def test_full_pipeline_is_deterministic_given_same_seed(triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr

    def run():
        return _alloc_and_run(N, indptr, deg, adj, twin, C=1, threshold=3, mode_1="random", mode_2="random", seed=42)

    E1, a1, b1, t1, _ = run()
    E2, a2, b2, t2, _ = run()
    assert np.array_equal(a1, a2)
    assert np.array_equal(b1, b2)
    assert np.array_equal(t1, t2)


def test_full_pipeline_feeds_cluster_reconstruction_consistently(triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    E, edges_a, edges_b, update_time, _ = _alloc_and_run(N, indptr, deg, adj, twin, C=1, threshold=3, mode_1="hub", mode_2="hub", seed=0)
    assert edges_a[0] == E == 3

    edge_count = int(edges_a[0])
    largest_arr = np.zeros(edge_count + 1, dtype=np.float64)
    chi_arr = np.zeros(edge_count + 1, dtype=np.float64)
    root_parent = np.zeros(N + 1, dtype=np.int32)
    root_size = np.zeros(N + 1, dtype=np.int64)
    modified_NZ_algorithm(N, edges_a, edges_b, edge_count, largest_arr, chi_arr, root_parent, root_size)

    # Before any edge was removed, the (connected) triangle's giant component
    # was the whole network.
    assert largest_arr[1] == pytest.approx(1.0)
