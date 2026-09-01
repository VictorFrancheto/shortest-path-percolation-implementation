import numpy as np
import pytest

from spp_general_simulator.network_loader import network_to_csr
from spp_general_simulator.runner.execution import derive_seed, run_realization, run_realizations
from spp_general_simulator.runner.results import RealizationResult, realization_path


def test_run_realization_removes_every_edge_and_shapes_match(triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    result = run_realization(1, N, deg, indptr, adj, twin, "hub", "hub", 1, 1, seed=0)
    assert result.edge_count == 3
    assert result.removed.tolist() == pytest.approx([1 / 3, 2 / 3, 3 / 3], rel=1e-6)
    assert result.largest.shape == (3,)
    assert result.chi.shape == (3,)
    assert result.edges_a.shape == (3,) and result.edges_b.shape == (3,)


def test_run_realization_does_not_mutate_the_base_graph(triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    deg_before = deg.copy()
    adj_before = adj.copy()
    run_realization(1, N, deg, indptr, adj, twin, "random", "random", 1, 1, seed=0)
    assert np.array_equal(deg, deg_before)
    assert np.array_equal(adj, adj_before)


def test_realization_result_save_and_load_roundtrip(tmp_path, triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    result = run_realization(1, N, deg, indptr, adj, twin, "random", "random", 1, 1, seed=0)
    path = tmp_path / "result.npz"
    result.save(path)
    loaded = RealizationResult.load(path)
    assert np.array_equal(result.edges_a, loaded.edges_a)
    assert np.array_equal(result.edges_b, loaded.edges_b)
    assert np.array_equal(result.largest, loaded.largest)
    assert np.array_equal(result.chi, loaded.chi)
    assert np.array_equal(result.update_time, loaded.update_time)


def test_derive_seed_depends_only_on_base_seed_and_iteration():
    assert derive_seed(3, base_seed=42) == derive_seed(3, base_seed=42)
    assert derive_seed(3, base_seed=42) != derive_seed(4, base_seed=42)
    assert derive_seed(3, base_seed=42) != derive_seed(3, base_seed=7)


def test_run_realizations_sequential_writes_expected_files(tmp_path, triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    output_dir = tmp_path / "out"
    results = run_realizations(N, deg, indptr, adj, twin, C=1, realizations=3, attack_mode_1="random", attack_mode_2="random", rank_1=1, rank_2=1, output_dir=output_dir, selection_name="random-random", workers=1, base_seed=123)

    assert [status for _, status in results] == ["done", "done", "done"]
    for i in range(3):
        path = realization_path(output_dir, "random-random", 1, i)
        assert path.exists()
        loaded = RealizationResult.load(path)
        assert loaded.edge_count == 3  # every edge removed, same invariant as the orchestrator tests


def test_run_realizations_skips_already_present_files(tmp_path, triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    output_dir = tmp_path / "out"
    run_realizations(N, deg, indptr, adj, twin, C=1, realizations=2, attack_mode_1="random", attack_mode_2="random", rank_1=1, rank_2=1, output_dir=output_dir, selection_name="random-random", workers=1, base_seed=1)

    results = run_realizations(N, deg, indptr, adj, twin, C=1, realizations=2, attack_mode_1="random", attack_mode_2="random", rank_1=1, rank_2=1, output_dir=output_dir, selection_name="random-random", workers=1, base_seed=1)
    assert [status for _, status in results] == ["skipped", "skipped"]


def test_run_realizations_workers_1_and_workers_2_agree_given_same_seed(tmp_path, triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr

    out1 = tmp_path / "workers1"
    run_realizations(N, deg, indptr, adj, twin, C=1, realizations=3, attack_mode_1="random", attack_mode_2="random", rank_1=1, rank_2=1, output_dir=out1, selection_name="random-random", workers=1, base_seed=7)

    out2 = tmp_path / "workers2"
    run_realizations(N, deg, indptr, adj, twin, C=1, realizations=3, attack_mode_1="random", attack_mode_2="random", rank_1=1, rank_2=1, output_dir=out2, selection_name="random-random", workers=2, base_seed=7)

    for i in range(3):
        r1 = RealizationResult.load(realization_path(out1, "random-random", 1, i))
        r2 = RealizationResult.load(realization_path(out2, "random-random", 1, i))
        assert np.array_equal(r1.edges_a, r2.edges_a)
        assert np.array_equal(r1.edges_b, r2.edges_b)
        assert np.array_equal(r1.update_time, r2.update_time)
        assert np.array_equal(r1.largest, r2.largest)
