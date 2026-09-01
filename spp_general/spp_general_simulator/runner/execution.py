"""Running one or many SPP realizations (``spp-dynamic.ipynb``, "Runner" section).

The base graph is saved to ``.npy`` before parallelizing. Each worker opens
``indptr`` as a read-only mmap (shared across all processes) and makes a
private copy of ``deg``, ``adj``, and ``twin`` (mutated during the
realization). Each realization corresponds to an independent seed;
parallelism (when ``workers > 1``) is provided by ``joblib``/``loky``, which
the notebook picks specifically because raw ``multiprocessing.Process`` is
fragile on Windows (no ``fork()``, pickling of interpreter globals).

The seed for a given realization index is derived purely from
``(base_seed, iteration)`` -- never from which worker executes it -- so
``workers=1`` and ``workers=N`` given the same ``base_seed`` reproduce
*exactly* the same per-realization results.
"""

import os
import tempfile
import time

import numpy as np
from joblib import Parallel, delayed

from ..dynamics.clusters import modified_NZ_algorithm
from ..dynamics.orchestrator import efficient_pair_removal
from ..network_loader import load_csr_mmap, save_csr_to_disk
from ..rng import init_rng
from .results import RealizationResult, realization_path


def derive_seed(iteration: int, base_seed) -> int:
    """Deterministic per-iteration seed when ``base_seed`` is given; otherwise a
    seed derived from wall-clock time + PID + iteration (matches the notebook)."""
    if base_seed is not None:
        return (int(base_seed) * 1000003 + iteration * 6364136223846793005) & ((1 << 64) - 1)
    return (int(time.time() * 1000) ^ (os.getpid() * 2654435761) ^ (iteration * 6364136223846793005)) & ((1 << 64) - 1)


def run_realization(C, N, deg_base, indptr, adj_base, twin_base, attack_mode_1, attack_mode_2, rank_1, rank_2, seed) -> RealizationResult:
    """Run one full SPP realization (Phase 1 + Phase 2 + cluster reconstruction)
    starting from the given base graph, and return its result.

    ``deg_base``/``adj_base``/``twin_base`` are copied before mutation;
    ``indptr`` is read-only and can be shared as-is (e.g. a memory-mapped array).
    """
    init_rng(seed)

    deg = np.asarray(deg_base, dtype=np.int32).copy()
    adj = np.asarray(adj_base, dtype=np.int32).copy()
    twin = np.asarray(twin_base, dtype=np.int32).copy()
    indptr = np.asarray(indptr, dtype=np.int64)

    E_val = int(indptr[N + 1] // 2)

    edges_a = np.zeros(E_val + 1, dtype=np.int32)
    edges_b = np.zeros(E_val + 1, dtype=np.int32)
    update_time = np.zeros(E_val + 1, dtype=np.int64)
    largest_arr = np.zeros(E_val + 1, dtype=np.float64)
    chi_arr = np.zeros(E_val + 1, dtype=np.float64)
    root_parent = np.zeros(N + 1, dtype=np.int32)
    root_size = np.zeros(N + 1, dtype=np.int64)

    threshold = int(7 * (N**0.44))
    efficient_pair_removal(C, N, deg, indptr, adj, twin, edges_a, edges_b, E_val, update_time, threshold, attack_mode_1=attack_mode_1, attack_mode_2=attack_mode_2, rank_1=rank_1, rank_2=rank_2)

    edge_count = int(edges_a[0])
    modified_NZ_algorithm(N, edges_a, edges_b, edge_count, largest_arr, chi_arr, root_parent, root_size)

    return RealizationResult.from_arrays(edge_count, largest_arr, chi_arr, edges_a, edges_b, update_time)


def _run_single_iteration(args):
    """Run one SPP realization and write the result to ``.npz``.

    Returns ``(iteration, status)`` -- status in {'done', 'skipped'}.
    """
    (iteration, base_csr_dir, N, C, attack_mode_1, attack_mode_2, rank_1, rank_2, base_seed, output_dir, selection_name) = args

    out_path = realization_path(output_dir, selection_name, C, iteration)
    if out_path.exists():
        return iteration, "skipped"

    seed = derive_seed(iteration, base_seed)
    deg_base, indptr_base, adj_base, twin_base = load_csr_mmap(base_csr_dir)
    result = run_realization(C, N, deg_base, indptr_base, adj_base, twin_base, attack_mode_1, attack_mode_2, rank_1, rank_2, seed)
    result.save(out_path)
    return iteration, "done"


def run_realizations(N, deg, indptr, adj, twin, C, realizations, attack_mode_1, attack_mode_2, rank_1, rank_2, output_dir, selection_name, workers=1, base_seed=None):
    """Run ``realizations`` independent SPP realizations, one per seed.

    ``workers=1`` (the default) runs sequentially, with no dependency on
    ``joblib``'s process pool. ``workers>1`` distributes the realizations
    across processes via ``joblib``/``loky``, sharing the base graph through a
    memory-mapped CSR snapshot on disk.

    Returns the list of ``(iteration, status)`` results, ``status`` in
    ``{'done', 'skipped'}`` -- a realization is skipped when its output file
    already exists, so an interrupted run can be resumed.
    """
    with tempfile.TemporaryDirectory(prefix="spp_csr_") as base_csr_dir:
        save_csr_to_disk(np.asarray(deg), np.asarray(indptr), np.asarray(adj), np.asarray(twin), base_csr_dir)

        args_list = [(i, base_csr_dir, N, C, attack_mode_1, attack_mode_2, rank_1, rank_2, base_seed, output_dir, selection_name) for i in range(realizations)]

        if workers == 1:
            return [_run_single_iteration(args) for args in args_list]

        return Parallel(n_jobs=workers, backend="loky", verbose=0)(delayed(_run_single_iteration)(args) for args in args_list)
