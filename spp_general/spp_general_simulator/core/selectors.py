import random
import networkx as nx
from .io import bond_to_graph

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


def ordered_by_degree(nodes, bond):
    """
    Order nodes by degree in descending order.
    
    Parameters
    ----------
    nodes : list[int]
        List of node IDs to sort.
    bond : list
        Bond adjacency structure.
    
    Returns
    -------
    list[int]
        Nodes ordered by degree (highest first).
    """
    return sorted(nodes, key=lambda i: bond[0][i], reverse=True)


def ordered_by_centrality(nodes, bond, N, kind="closeness"):
    """
    Order nodes by a centrality measure in descending order.
    
    Parameters
    ----------
    nodes : list[int]
        List of node IDs to sort.
    bond : list
        Bond adjacency structure.
    N : int
        Number of nodes in the network.
    kind : str, optional
        Centrality type: 'closeness' or 'betweenness'. Default is 'closeness'.
    
    Returns
    -------
    list[int]
        Nodes ordered by centrality (highest first).
    """
    G = bond_to_graph(bond, N)
    if kind == "closeness":
        cent = nx.closeness_centrality(G)
    elif kind == "betweenness":
        cent = nx.betweenness_centrality(G, normalized=True)
    else:
        raise ValueError("centrality kind must be 'closeness' or 'betweenness'")
    return sorted(nodes, key=lambda i: cent[i], reverse=True)


def select_node(N, bond, mode="random", rank=1, exclude=None):
    """
    Select a node based on the given mode and rank.
    
    Parameters
    ----------
    N : int
        Number of nodes in the network.
    bond : list
        Bond adjacency structure.
    mode : str, optional
        Node selection mode: 'random', 'hub', 'closeness', 'betweenness'.
    rank : int, optional
        Rank of the node to select (1 = highest, 2 = second highest, etc.).
    exclude : int or None, optional
        Node to exclude from selection (e.g., already chosen).
    
    Returns
    -------
    int or None
        Selected node ID, or None if no nodes are available.
    """
    nodes = list(range(1, N+1))
    if exclude is not None and exclude in nodes:
        nodes.remove(exclude)
    if not nodes:
        return None

    if mode == "random":
        return random.choice(nodes)

    if mode == "hub":
        ordered = ordered_by_degree(nodes, bond)
    elif mode == "closeness":
        ordered = ordered_by_centrality(nodes, bond, N, kind="closeness")
    elif mode == "betweenness":
        ordered = ordered_by_centrality(nodes, bond, N, kind="betweenness")
    else:
        raise ValueError(f"[ERROR] Unknown attack mode: {mode}")

    idx = min(max(1, rank) - 1, len(ordered) - 1)
    return ordered[idx]