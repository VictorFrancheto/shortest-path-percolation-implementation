import math
from .rng import genrand64_real3

def geometric_distribution(P: float):
    """
    Sample from a geometric distribution with parameter P.

    Parameters
    ----------
    P : float
        Success probability of the geometric distribution (0 < P ≤ 1).

    Returns
    -------
    int
        Sampled value k ≥ 1 with probability (1-P)^(k-1) * P.
        Returns -1 if P <= 0.

    Notes
    -----
    - If P = 1, the function always returns 1.
    - Sampling is performed using the custom RNG genrand64_real3().
    - This is the "number of trials until first success" variant (support starts at 1).
    """
    if P <= 0:
        return -1
    if P == 1:
        return 1
    u = genrand64_real3()
    return 1 + int(math.floor(math.log(u) / math.log(1.0 - P)))