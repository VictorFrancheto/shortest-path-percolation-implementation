
import networkx as nx

def read_network_from_txt(path, one_indexed=False, remove_selfloops=True):
    """
    Read a graph from a .txt file in edge list format.

    Parameters
    ----------
    path : str
        Path to the text file containing the network edges.
        Each line must follow the format: "i j".
    one_indexed : bool, optional
        If True, node IDs in the file are 1-indexed and will be shifted
        to 0-index internally. Default = False.
    remove_selfloops : bool, optional
        If True, removes self-loops (edges i i) after reading.

    Returns
    -------
    networkx.Graph
        Graph reconstructed from the edge list file.
    """
    G = nx.Graph()
    with open(path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            i, j = map(int, parts[:2])
            if one_indexed:
                i, j = i - 1, j - 1
            G.add_edge(i, j)

    if remove_selfloops:
        G.remove_edges_from(nx.selfloop_edges(G))

    return G



def network_to_bond(G):
    """
    Convert a NetworkX graph into a 'bond' adjacency structure.

    Parameters
    ----------
    G : networkx.Graph
        Graph to convert. Node IDs must be consecutive integers.

    Returns
    -------
    tuple
        bond : list
            Bond representation of the graph where:
            - bond[0][i] = degree of node i
            - bond[i] = [0, neighbor1, neighbor2, ...]
        N : int
            Number of nodes in the graph.

    Notes
    -----
    The resulting bond structure is 1-indexed to match
    percolation algorithm conventions.
    """
    nodes = sorted(G.nodes())
    id_map = {old: i+1 for i, old in enumerate(nodes)}
    N = len(nodes)

    bond = [None] * (N + 1)
    bond[0] = [0] * (N + 1)
    for i in range(1, N + 1):
        bond[i] = [0]

    for (u, v) in G.edges():
        i1 = id_map[u]
        j1 = id_map[v]
        bond[0][i1] += 1
        bond[0][j1] += 1
        bond[i1].append(j1)
        bond[j1].append(i1)

    return bond, N

def bond_to_graph(bond, N):
    """
    Convert a 'bond' adjacency structure into a NetworkX graph.

    Parameters
    ----------
    bond : list
        Bond representation of the network (adjacency structure).
    N : int
        Number of nodes.

    Returns
    -------
    networkx.Graph
        Graph converted from the bond representation.
    """
    G = nx.Graph()
    G.add_nodes_from(range(1, N + 1))
    for i in range(1, N + 1):
        for idx in range(1, bond[0][i] + 1):
            j = bond[i][idx]
            if i < j:
                G.add_edge(i, j)
    return G