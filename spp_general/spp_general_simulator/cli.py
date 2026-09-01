"""Command-line interface.

Usage
-----
python -m spp_general_simulator \\
    --network-dir network-save \\
    --network-file er1500-graph.txt \\
    --C 3 \\
    --realizations 1000 \\
    --workers 4 \\
    --selection random-random
"""

import argparse
import sys
import time

from .config import build_config
from .network_loader import network_to_csr, read_network_from_txt
from .runner.execution import run_realizations
from .selection.strategies import SELECTION_STRATEGIES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spp_general_simulator",
        description="Run the Shortest-Path Percolation (SPP) dynamics on a previously saved network.",
    )
    parser.add_argument("--network-dir", required=True, help="Directory containing the network file (e.g. 'network-save').")
    parser.add_argument("--network-file", required=True, help="Name of the .txt edge-list file inside --network-dir.")
    parser.add_argument("--C", required=True, type=int, help="Maximum shortest-path length (hops) considered by the dynamics.")
    parser.add_argument("--realizations", required=True, type=int, help="Number of independent realizations (seeds) to run.")
    parser.add_argument("--selection", required=True, metavar="SELECTION", help="Source-target selection strategy, as '<source_mode>-<target_mode>'. One of: " + ", ".join(sorted(SELECTION_STRATEGIES)))
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel worker processes (default: 1, sequential).")
    parser.add_argument("--rank-source", type=int, default=1, help="Rank of the source node for ranking-based modes (hub/closeness/betweenness/domirank); ignored for 'random' (default: 1).")
    parser.add_argument("--rank-target", type=int, default=1, help="Rank of the target node for ranking-based modes; ignored for 'random' (default: 1).")
    parser.add_argument("--output-dir", default="./spp-results", help="Directory where per-realization .npz results are written (default: './spp-results').")
    parser.add_argument("--seed", type=int, default=None, help="Base seed for reproducibility. Same seed + same pending realizations => same results, regardless of --workers. Default: derived from wall-clock time (non-reproducible).")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        cfg = build_config(
            network_dir=args.network_dir,
            network_file=args.network_file,
            C=args.C,
            realizations=args.realizations,
            selection=args.selection,
            workers=args.workers,
            rank_source=args.rank_source,
            rank_target=args.rank_target,
            output_dir=args.output_dir,
            seed=args.seed,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    G = read_network_from_txt(cfg.network_path, one_indexed=True)
    deg, indptr, adj, twin, N = network_to_csr(G)

    print(f"Network: {cfg.network_path} (N={N}, E={int(indptr[N + 1] // 2)})")
    print(f"selection={cfg.selection!r} (attack_mode_1={cfg.attack_mode_1!r}, attack_mode_2={cfg.attack_mode_2!r}, rank_source={cfg.rank_source}, rank_target={cfg.rank_target})")
    print(f"C={cfg.C}, realizations={cfg.realizations}, workers={cfg.workers}, output_dir={cfg.output_dir}")

    start = time.time()
    results = run_realizations(
        N,
        deg,
        indptr,
        adj,
        twin,
        cfg.C,
        cfg.realizations,
        cfg.attack_mode_1,
        cfg.attack_mode_2,
        cfg.rank_source,
        cfg.rank_target,
        cfg.output_dir,
        cfg.selection,
        workers=cfg.workers,
        base_seed=cfg.seed,
    )
    done = sum(1 for _, status in results if status == "done")
    skipped = len(results) - done
    print(f"Finished: {done} realizations run, {skipped} already present. Total time: {time.time() - start:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
