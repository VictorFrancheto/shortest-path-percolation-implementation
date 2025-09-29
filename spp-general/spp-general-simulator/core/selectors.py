import random
import networkx as nx
from .io import bond_to_graph

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

def random_attack_node(N: int):
    """
    Select a random node uniformly from the set {1, ..., N}.
    """
    return int(genrand64_real3() * N) + 1

def get_hub_nodes(N, bond, top_k=1):
    """
    Identify the top-k hub nodes ranked by degree.

    Parameters
    ----------
    N : int
        Number of nodes.
    bond : list
        Bond representation of the network.
    top_k : int, optional
        Number of top hub nodes to return (default = 1).

    Returns
    -------
    list
        List of node IDs corresponding to the top-k hubs.
    """
    degree_list = [(bond[0][i], i) for i in range(1, N + 1)]
    degree_list.sort(key=lambda x: x[0], reverse=True)
    return [i for _, i in degree_list[:top_k]]


def select_hub_node(N, bond, top_k=1):
    """
    Randomly select one node from the top-k hubs.

    Parameters
    ----------
    N : int
        Number of nodes.
    bond : list
        Bond representation of the network.
    top_k : int, optional
        Number of top hub nodes considered for selection (default = 1).

    Returns
    -------
    int or None
        ID of the selected hub node, or None if no hubs exist.
    """
    hubs = get_hub_nodes(N, bond, top_k=top_k)
    return random.choice(hubs) if hubs else None


def get_closeness_nodes(N, bond, top_k=1):
    """
    Identify the top-k nodes ranked by closeness centrality.

    Parameters
    ----------
    N : int
        Number of nodes.
    bond : list
        Bond representation of the network.
    top_k : int, optional
        Number of nodes to return (default = 1).

    Returns
    -------
    list
        List of node IDs with the highest closeness centrality.
    """
    G = bond_to_graph(bond, N)
    clos = nx.closeness_centrality(G)
    ordered = sorted(clos.items(), key=lambda kv: kv[1], reverse=True)
    return [n for n, _ in ordered[:top_k]]


def select_closeness_node(N, bond, top_k=1):
    """
    Randomly select one node among the top-k by closeness centrality.

    Parameters
    ----------
    N : int
        Number of nodes.
    bond : list
        Bond representation of the network.
    top_k : int, optional
        Number of nodes considered for selection (default = 1).

    Returns
    -------
    int or None
        ID of the selected node, or None if no nodes exist.
    """
    nodes = get_closeness_nodes(N, bond, top_k=top_k)
    return random.choice(nodes) if nodes else None


def get_betweenness_nodes(N, bond, top_k=1, normalized=True):
    """
    Identify the top-k nodes ranked by betweenness centrality.

    Parameters
    ----------
    N : int
        Number of nodes.
    bond : list
        Bond representation of the network.
    top_k : int, optional
        Number of nodes to return (default = 1).
    normalized : bool, optional
        Whether to normalize betweenness values (default = True).

    Returns
    -------
    list
        List of node IDs with the highest betweenness centrality.
    """
    G = bond_to_graph(bond, N)
    btw = nx.betweenness_centrality(G, normalized=normalized)
    ordered = sorted(btw.items(), key=lambda kv: kv[1], reverse=True)
    return [n for n, _ in ordered[:top_k]]


def select_betweenness_node(N, bond, top_k=1, normalized=True):
    """
    Randomly select one node among the top-k by betweenness centrality.

    Parameters
    ----------
    N : int
        Number of nodes.
    bond : list
        Bond representation of the network.
    top_k : int, optional
        Number of nodes considered for selection (default = 1).
    normalized : bool, optional
        Whether to normalize betweenness values (default = True).

    Returns
    -------
    int or None
        ID of the selected node, or None if no nodes exist.
    """
    nodes = get_betweenness_nodes(N, bond, top_k=top_k, normalized=normalized)
    return random.choice(nodes) if nodes else None