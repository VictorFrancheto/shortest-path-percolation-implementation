"""Validated configuration for one SPP simulation run.

``build_config`` is the single place where CLI arguments are validated -- it
is independent of ``argparse`` so it can be exercised directly by tests.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .selection.strategies import SELECTION_STRATEGIES


@dataclass(frozen=True)
class SimulationConfig:
    network_path: Path
    C: int
    realizations: int
    workers: int
    selection: str
    attack_mode_1: str
    attack_mode_2: str
    rank_source: int
    rank_target: int
    output_dir: Path
    seed: Optional[int]


def build_config(
    network_dir,
    network_file,
    C,
    realizations,
    selection,
    workers: int = 1,
    rank_source: int = 1,
    rank_target: int = 1,
    output_dir="./spp-results",
    seed: Optional[int] = None,
) -> SimulationConfig:
    """Validate the raw arguments and return an immutable ``SimulationConfig``.

    Raises
    ------
    ValueError
        If any argument is invalid (missing network file, non-positive
        C/realizations/workers/ranks, or an unknown ``selection`` strategy).
    """
    network_path = Path(network_dir) / network_file
    if not network_path.is_file():
        raise ValueError(f"Network file not found: {network_path}")

    if not isinstance(C, int) or isinstance(C, bool) or C < 1:
        raise ValueError(f"C must be a positive integer, got {C!r}.")

    if not isinstance(realizations, int) or isinstance(realizations, bool) or realizations < 1:
        raise ValueError(f"realizations must be a positive integer, got {realizations!r}.")

    if not isinstance(workers, int) or isinstance(workers, bool) or workers < 1:
        raise ValueError(f"workers must be a positive integer, got {workers!r}.")

    if selection not in SELECTION_STRATEGIES:
        available = ", ".join(sorted(SELECTION_STRATEGIES))
        raise ValueError(f"Unknown selection={selection!r}. Available options: {available}")

    if not isinstance(rank_source, int) or isinstance(rank_source, bool) or rank_source < 1:
        raise ValueError(f"rank_source must be a positive integer, got {rank_source!r}.")

    if not isinstance(rank_target, int) or isinstance(rank_target, bool) or rank_target < 1:
        raise ValueError(f"rank_target must be a positive integer, got {rank_target!r}.")

    cfg = SELECTION_STRATEGIES[selection]

    return SimulationConfig(
        network_path=network_path,
        C=C,
        realizations=realizations,
        workers=workers,
        selection=selection,
        attack_mode_1=cfg["attack_mode_1"],
        attack_mode_2=cfg["attack_mode_2"],
        rank_source=rank_source,
        rank_target=rank_target,
        output_dir=Path(output_dir),
        seed=seed,
    )
