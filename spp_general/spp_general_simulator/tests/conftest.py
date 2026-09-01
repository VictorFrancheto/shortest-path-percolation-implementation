"""Small, deterministic graphs shared by the test suite.

Every fixture builds a network whose exact structure is known up front, so
tests can assert precise expected outputs instead of just "it ran".
"""

import networkx as nx
import numpy as np
import pytest

from spp_general_simulator.network_loader import network_to_csr


def alloc_bfs_buffers(N, indptr):
    """Allocate a fresh set of BFS/DAG buffers, sized exactly like
    ``efficient_pair_removal`` does. Returned as a plain namespace so tests can
    access fields by name (``buffers.path``, ``buffers.visited``, ...)."""
    total_adj = int(indptr[N + 1])

    class Buffers:
        pass

    b = Buffers()
    b.path = np.zeros(N + 1, dtype=np.int32)
    b.path_slot = np.full(N + 1, -1, dtype=np.int32)
    b.vec = np.zeros(N + 1, dtype=np.int32)
    b.tmp_vec = np.zeros(N + 1, dtype=np.int32)
    b.visited = -np.ones(N + 1, dtype=np.int32)
    b.reset = np.zeros(N + 1, dtype=np.int32)
    b.dag_cnt = np.zeros(N + 1, dtype=np.int32)
    b.dag_adj = np.zeros(total_adj, dtype=np.int32)
    b.dag_slot = np.zeros(total_adj, dtype=np.int32)
    b.nr_sp = np.zeros(N + 1, dtype=np.int64)
    return b


@pytest.fixture
def triangle_csr():
    """Nodes 0,1,2, all mutually connected (K3)."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (0, 2)])
    return network_to_csr(G)


@pytest.fixture
def path5_csr():
    """Path graph 0-1-2-3-4 (a single shortest path between any two nodes)."""
    return network_to_csr(nx.path_graph(5))


@pytest.fixture
def star_csr():
    """Star graph: center 0, leaves 1..6 (0 has degree 6, every leaf has degree 1)."""
    return network_to_csr(nx.star_graph(6))


@pytest.fixture
def cycle4_csr():
    """4-cycle 0-1-2-3-0: nodes 0 and 2 (resp. 1 and 3) have exactly two
    shortest paths of length 2 between them."""
    return network_to_csr(nx.cycle_graph(4))


@pytest.fixture
def disconnected_csr():
    """Two disjoint edges: {0-1} and {2-3} -- no path between the two components."""
    G = nx.Graph()
    G.add_edge(0, 1)
    G.add_edge(2, 3)
    return network_to_csr(G)


@pytest.fixture
def er_csr_n24():
    """A connected, moderately dense Erdos-Renyi graph (N=24) -- large enough for
    closeness/betweenness/DomiRank to be meaningful, mirroring the notebook's
    own `run_quick_tests(N_test=24, avg_k_test=5)`."""
    G = nx.gnp_random_graph(24, 5 / 23, seed=42, directed=False)
    if not nx.is_connected(G):
        giant = max(nx.connected_components(G), key=len)
        G = nx.convert_node_labels_to_integers(G.subgraph(giant).copy())
    return network_to_csr(G)


@pytest.fixture
def network_save_dir(tmp_path):
    """A temporary ``network-save`` directory containing a small, deterministic,
    1-indexed edge-list file: a triangle {1,2,3} plus an isolated node 4
    (preserved via the self-loop line ``4 4``, matching the real files in
    ``network-save/*.txt``)."""
    content = "1 2\n2 3\n1 3\n4 4\n"
    directory = tmp_path / "network-save"
    directory.mkdir()
    (directory / "tiny.txt").write_text(content)
    return directory
