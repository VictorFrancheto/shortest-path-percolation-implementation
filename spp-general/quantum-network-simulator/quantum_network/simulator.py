import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import poisson


class QuantumNetworkSimulator:
    """Simulator for quantum photonic networks using Waxman random graphs."""

    def __init__(self, R=1800, aL=226, b=1, g=0.2, np_photons=1000, A_value=5.2e4):
        self.R = R
        self.aL = aL
        self.b = b
        self.g = g
        self.np_photons = np_photons
        self.A_value = A_value

    def generate_waxman_graph(self, N):
        G = nx.Graph()
        G.add_nodes_from(range(N))
        r = self.R * np.sqrt(np.random.uniform(0, 1, N))
        theta = np.random.uniform(0, 2 * np.pi, N)
        x, y = r * np.cos(theta), r * np.sin(theta)
        nodes = np.column_stack((x, y))
        dij = np.sqrt((x[:, None] - x)**2 + (y[:, None] - y)**2)
        Pij = self.b * np.exp(-dij / self.aL)
        mask = np.triu(np.random.uniform(0, 1, size=(N, N)) < Pij, 1)
        for i, j in zip(*np.where(mask)):
            G.add_edge(i, j, weight=dij[i, j])
        return G, nodes

    def generate_photonic_network(self, G):
        H = nx.Graph()
        H.add_nodes_from(G.nodes())
        for i, j, data in G.edges(data=True):
            dij = data['weight']
            pij = 10**(-self.g * dij / 10)
            Pij = 1 - (1 - pij)**self.np_photons
            if np.random.rand() < Pij:
                H.add_edge(i, j, weight=dij)
        return H

    def calculate_largest_cluster_size(self, G):
        if len(G) == 0:
            return 0
        largest_cc = max(nx.connected_components(G), key=len, default=set())
        return len(largest_cc)

    def plot_combined(self, nodes, fiber_net, photonic_net, N, ng_over_n, filename):
        fig, ax = plt.subplots(figsize=(6, 6))

        scale_factor = 0.85
        pos = {i: (x * scale_factor, y * scale_factor) for i, (x, y) in enumerate(nodes)}

        degrees = dict(photonic_net.degree())
        density = N / (np.pi * self.R**2)
        lambda_param = self.A_value * density
        node_colors = [plt.cm.winter(poisson.cdf(degrees.get(node, 0), lambda_param)) for node in range(N)]

        nx.draw_networkx_edges(fiber_net, pos, edge_color='gray', alpha=0.2, ax=ax, label="Fiber links")
        nx.draw_networkx_edges(photonic_net, pos, edge_color='red', alpha=0.7, ax=ax, label="Photonic links")
        nx.draw_networkx_nodes(photonic_net, pos, node_color=node_colors, node_size=20, ax=ax, label="Nodes")

        ax.set_xlim(-self.R, self.R)
        ax.set_ylim(-self.R, self.R)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal', adjustable='box')

        ax.text(0.05, 0.90,
                f"$N_{{G}}/N = {ng_over_n*100:.1f}\\%$   $N = {N}$",
                transform=ax.transAxes, fontsize=10, ha='left',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.85))

        ax.legend(loc="upper right", fontsize=8, frameon=True)

        plt.tight_layout()
        plt.savefig(filename, dpi=600)
        print(f"Figure saved as {filename}")
