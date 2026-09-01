"""Per-realization result: the arrays ``spp-dynamic.ipynb`` actually produces.

Ports ``_write_npz`` (notebook cell 35). The 4 power-of-`largest` columns from
the original notebook that inspired this one are not serialized: they are
trivially derivable as ``largest ** k`` on read, so keeping only ``largest``
loses no information while keeping the output compact.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class RealizationResult:
    """Everything produced by one SPP realization, trimmed to ``edge_count`` entries.

    removed      : fraction of edges removed so far, at each removal step.
    largest      : giant component size / N, at each removal step.
    chi          : susceptibility <s^2>/<s> (excluding the giant component).
    edges_a/edges_b : the two endpoints of the edge removed at each step (a <= b).
    update_time  : the internal "tau"/"interval" clock value at which the edge was removed.
    """

    removed: np.ndarray
    largest: np.ndarray
    chi: np.ndarray
    edges_a: np.ndarray
    edges_b: np.ndarray
    update_time: np.ndarray

    @property
    def edge_count(self) -> int:
        return int(self.edges_a.shape[0])

    @classmethod
    def from_arrays(cls, edge_count, largest_arr, chi_arr, edges_a, edges_b, update_time) -> "RealizationResult":
        """Build a result from the raw 1-indexed buffers filled by ``efficient_pair_removal``
        + ``modified_NZ_algorithm``, trimming them to ``[1, edge_count]``."""
        j = np.arange(1, edge_count + 1, dtype=np.float32)
        removed = j / np.float32(edge_count)
        return cls(
            removed=removed,
            largest=largest_arr[1 : edge_count + 1].astype(np.float32, copy=False),
            chi=chi_arr[1 : edge_count + 1].astype(np.float32, copy=False),
            edges_a=edges_a[1 : edge_count + 1].astype(np.int32, copy=False),
            edges_b=edges_b[1 : edge_count + 1].astype(np.int32, copy=False),
            update_time=update_time[1 : edge_count + 1].astype(np.int64, copy=False),
        )

    def save(self, path) -> None:
        """Compact binary output (``.npz``, compressed)."""
        np.savez_compressed(
            path,
            removed=self.removed,
            largest=self.largest,
            chi=self.chi,
            edges_a=self.edges_a,
            edges_b=self.edges_b,
            update_time=self.update_time,
        )

    @classmethod
    def load(cls, path) -> "RealizationResult":
        with np.load(path) as data:
            return cls(
                removed=data["removed"],
                largest=data["largest"],
                chi=data["chi"],
                edges_a=data["edges_a"],
                edges_b=data["edges_b"],
                update_time=data["update_time"],
            )


def realization_path(output_dir, selection, C, iteration) -> Path:
    """Layout mirroring the notebook's ``{output_dir}/{mode_name}/C{C}/full_data_{i}.npz``."""
    directory = Path(output_dir) / selection / f"C{C}"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"realization_{iteration}.npz"
