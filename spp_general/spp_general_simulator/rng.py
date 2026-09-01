"""Random number generator setup (``spp-dynamic.ipynb``, "Random Number Generator" section).

Numba keeps an internal RNG state for ``@njit`` functions that is *separate*
from NumPy's own generator: calling ``np.random.seed(x)`` from plain Python
does not reseed the generator used by ``np.random.random()``/``np.random.randint()``
when called from inside an ``@njit`` function. ``init_rng`` reseeds Python's
``random``, NumPy's RNG, and (via a tiny ``@njit`` helper run from inside
compiled code) Numba's internal RNG, so a given seed reproduces the whole
pipeline end to end regardless of whether Numba is installed.
"""

import random

import numpy as np

from .jit_compat import njit


@njit(cache=True)
def _seed_njit_rng(seed):
    np.random.seed(seed)


def init_rng(seed: int) -> None:
    """Seed Python's ``random``, NumPy's RNG, and Numba's internal RNG."""
    random.seed(seed)
    np.random.seed(seed & 0xFFFFFFFF)
    _seed_njit_rng(seed & 0xFFFFFFFF)


def genrand64_real3() -> float:
    """Random float in [0, 1) via Python's ``random`` (slow-path compatibility)."""
    return random.random()
