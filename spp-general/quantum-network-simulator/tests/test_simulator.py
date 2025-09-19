import os
import networkx as nx
import matplotlib
from quantum_network.simulator import QuantumNetworkSimulator

matplotlib.use("Agg")  

def test_generate_waxman_graph():
    sim = QuantumNetworkSimulator()
    G, nodes = sim.generate_waxman_graph(30)

    # Check number of nodes
    assert len(G.nodes) == 30

    # Check shape of node coordinates
    assert nodes.shape == (30, 2)

    # All edges should have positive weights
    for _, _, data in G.edges(data=True):
        assert data["weight"] > 0


def test_generate_photonic_network():
    sim = QuantumNetworkSimulator()
    G, nodes = sim.generate_waxman_graph(20)
    H = sim.generate_photonic_network(G, nodes)

    # H must contain the same nodes as G
    assert set(H.nodes) == set(G.nodes)

    # All edges in H must also exist in G
    for u, v in H.edges:
        assert G.has_edge(u, v)


def test_calculate_largest_cluster_size_empty():
    sim = QuantumNetworkSimulator()
    G = nx.Graph()  # empty graph
    assert sim.calculate_largest_cluster_size(G) == 0


def test_calculate_largest_cluster_size_connected():
    sim = QuantumNetworkSimulator()
    G = nx.path_graph(5)  # connected graph
    assert sim.calculate_largest_cluster_size(G) == 5


def test_run_single_simulation_creates_file(tmp_path):
    sim = QuantumNetworkSimulator()
    filename = tmp_path / "test_network.png"

    sim.run_single_simulation(N=10, filename=str(filename))

    # The file should exist and not be empty
    assert filename.exists()
    assert filename.stat().st_size > 0
