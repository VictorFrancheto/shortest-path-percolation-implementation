"""Optional Numba acceleration.

Mirrors ``spp-dynamic.ipynb`` exactly: if Numba is installed, ``njit`` compiles
the hot kernels; otherwise it becomes a no-op decorator and every kernel runs
as plain Python (same logic, just slower). Numba is never a hard dependency.
"""

try:
    from numba import njit

    HAS_NUMBA = True
except Exception:
    HAS_NUMBA = False

    def njit(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]

        def _decorator(f):
            return f

        return _decorator
