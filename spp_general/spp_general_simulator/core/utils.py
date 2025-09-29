def find_node(i, j, bond):
    """
    Find the neighbor index of node j in the adjacency list of node i.

    Parameters
    ----------
    i : int
        Node whose neighbors will be searched.
    j : int
        Target node to find in the adjacency list.
    bond : list
        Bond representation of the network.

    Returns
    -------
    int
        Index position of node j in the adjacency list of node i
        (1..degree(i)) or -1 if not found.
    """
    for k in range(1, bond[0][i] + 1):
        if bond[i][k] == j:
            return k
    return -1

def copy_network(N, origin_bond, copy_bond):
    """
    Copy node degrees and adjacency lists from one bond structure to another.

    Parameters
    ----------
    N : int
        Number of nodes.
    origin_bond : list
        Source bond structure.
    copy_bond : list
        Destination bond structure. Must be preallocated with length N+1.
    """
    if len(copy_bond) != N + 1:
        raise ValueError("copy_bond must have size N+1")

    for i in range(1, N + 1):
        deg = origin_bond[0][i]
        if len(copy_bond[0]) <= i:
            copy_bond[0].extend([0] * (i - len(copy_bond[0]) + 1))
        copy_bond[0][i] = deg
        copy_bond[i] = origin_bond[i][:deg + 1]
        

def clean_time_stamp(update_time, E):
    """
    Reset all timestamps to zero.

    Parameters
    ----------
    update_time : list
        List of timestamps to be reset.
    E : int
        Number of elements (edges or entries) to reset.
    """
    for i in range(1, E+1):
        update_time[i] = 0


def adjust_pair(pairs, q: int):
    """
    Move the pair at position q to the end of the active list 
    and decrease the active counter.

    Parameters
    ----------
    pairs : list of lists
        Pair structure:
        - pairs[0] : list of node1 indices (1-indexed).
        - pairs[1] : list of node2 indices (1-indexed).
        - pairs[0][0] : integer counter of currently active pairs.
    q : int
        Index of the pair to be moved (1 <= q <= pairs[0][0]).

    Notes
    -----
    - This function modifies 'pairs' in place.
    - The order of pairs is not preserved (swap-and-pop removal).
    """
    if q < 1 or q > pairs[0][0]:
        raise IndexError("q is out of range of active pairs")

    node1 = pairs[0][q]
    node2 = pairs[1][q]

    # overwrite position q with the last active pair
    pairs[0][q] = pairs[0][pairs[0][0]]
    pairs[1][q] = pairs[1][pairs[0][0]]

    # move removed pair to the end (optional, just to keep it)
    pairs[0][pairs[0][0]] = node1
    pairs[1][pairs[0][0]] = node2

    # decrement active counter
    pairs[0][0] -= 1