import numpy as np
import pytest

from spp_general_simulator.dynamics.clusters import modified_NZ_algorithm


def _run(N, edges_a, edges_b, edge_count):
    edges_a = np.array(edges_a, dtype=np.int32)
    edges_b = np.array(edges_b, dtype=np.int32)
    largest_arr = np.zeros(edge_count + 1, dtype=np.float64)
    chi_arr = np.zeros(edge_count + 1, dtype=np.float64)
    root_parent = np.zeros(N + 1, dtype=np.int32)
    root_size = np.zeros(N + 1, dtype=np.int64)
    modified_NZ_algorithm(N, edges_a, edges_b, edge_count, largest_arr, chi_arr, root_parent, root_size)
    return largest_arr, chi_arr


def test_modified_NZ_algorithm_on_hand_computed_path_removal():
    # Path 1-2-3-4 removed in order (1,2), (2,3), (3,4). Reconstructing
    # backwards (adding (3,4), then (2,3), then (1,2)) grows the giant
    # component from a single edge up to the full path -- values below were
    # derived by hand-simulating the union-find exactly as the algorithm does.
    edges_a = [0, 1, 2, 3]
    edges_b = [0, 2, 3, 4]
    largest_arr, chi_arr = _run(N=4, edges_a=edges_a, edges_b=edges_b, edge_count=3)

    assert largest_arr[3] == pytest.approx(0.5)   # only edge (3,4) present -> 2/4
    assert largest_arr[2] == pytest.approx(0.75)  # (2,3),(3,4) present -> 3/4
    assert largest_arr[1] == pytest.approx(1.0)   # all edges present -> 4/4

    assert chi_arr[3] == pytest.approx(1.0)
    assert chi_arr[2] == pytest.approx(1.0)
    assert chi_arr[1] == pytest.approx(0.0)  # no finite clusters left once everything merges


def test_modified_NZ_algorithm_single_edge_two_nodes():
    largest_arr, chi_arr = _run(N=2, edges_a=[0, 1], edges_b=[0, 2], edge_count=1)
    assert largest_arr[1] == pytest.approx(1.0)
    assert chi_arr[1] == pytest.approx(0.0)


def test_modified_NZ_algorithm_disjoint_pairs_never_merge():
    # Two independent edges among 4 nodes: (1,2) and (3,4) never touch each
    # other, so the giant component never exceeds 2 nodes.
    largest_arr, chi_arr = _run(N=4, edges_a=[0, 1, 3], edges_b=[0, 2, 4], edge_count=2)
    assert largest_arr[2] == pytest.approx(0.5)  # one edge present -> component size 2/4
    assert largest_arr[1] == pytest.approx(0.5)  # both edges present, still size-2 components
    # with the giant component fixed at size 2, the other size-2 component is
    # the only "finite" cluster: <s^2>/<s> over it alone is (2^2)/2 = 2.
    assert chi_arr[1] == pytest.approx(2.0)
