"""Modified Newman-Ziff cluster reconstruction (``spp-dynamic.ipynb``, cell 30-31).

Reconstructs the evolution of the giant component and the susceptibility by
walking the removal order backwards (adding edges back one at a time), via a
union-find with path compression.
"""

from ..jit_compat import njit


@njit(cache=True)
def find_root(n, root_parent):
    """Iterative find with two-pass path compression."""
    r = n
    while root_parent[r] != r:
        r = root_parent[r]
    cur = n
    while root_parent[cur] != r:
        nxt = root_parent[cur]
        root_parent[cur] = r
        cur = nxt
    return r


@njit(cache=True)
def modified_NZ_algorithm(N, edges_a, edges_b, edge_count, largest_arr, chi_arr, root_parent, root_size):
    """Reconstruct clusters by walking from the end to the start (adding edges back).

    Writes ``largest_arr`` (giant component / N) and ``chi_arr``
    (``<s^2>/<s>``, excluding the giant component) at every removal step ``e``.
    """
    for i in range(N + 1):
        root_parent[i] = i
        root_size[i] = 1

    largest = 1
    av2 = float(N - 1)

    for e in range(edge_count, 0, -1):
        n = edges_a[e]
        m = edges_b[e]
        av2 += largest * largest

        rn = find_root(n, root_parent)
        rm = find_root(m, root_parent)
        sn = root_size[rn]
        sm = root_size[rm]

        if rn != rm:
            av2 -= sn * sn + sm * sm
            if sn >= sm:
                root_parent[rm] = rn
                root_size[rn] = sn + sm
            else:
                root_parent[rn] = rm
                root_size[rm] = sn + sm
            if sn + sm > largest:
                largest = sn + sm
            av2 += (sn + sm) * (sn + sm)

        tmp = largest / float(N)
        largest_arr[e] = tmp
        av = float(N) - float(largest)
        av2 -= largest * largest
        if av > 0.0:
            chi_arr[e] = av2 / av
        else:
            chi_arr[e] = 0.0
