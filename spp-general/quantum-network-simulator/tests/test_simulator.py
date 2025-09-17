from quantum_network.simulator import QuantumNetworkSimulator

def test_generate_graph():
    sim = QuantumNetworkSimulator()
    G, nodes = sim.generate_waxman_graph(50)
    assert len(G.nodes) == 50
    assert nodes.shape == (50, 2)
