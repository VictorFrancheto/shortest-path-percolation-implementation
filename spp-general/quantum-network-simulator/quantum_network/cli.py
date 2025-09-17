import argparse
from .simulator import QuantumNetworkSimulator


def main():
    parser = argparse.ArgumentParser(description="Quantum Network Simulator CLI")
    parser.add_argument("-N", type=int, default=500, help="Number of nodes in the network")
    parser.add_argument("--R", type=float, default=1800, help="Radius of the area")
    parser.add_argument("--aL", type=float, default=226, help="Characteristic length scale")
    parser.add_argument("--b", type=float, default=1.0, help="Scaling factor for edge probability")
    parser.add_argument("--g", type=float, default=0.2, help="Attenuation factor")
    parser.add_argument("--np_photons", type=int, default=1000, help="Number of photons")
    parser.add_argument("--A_value", type=float, default=5.2e4, help="Poisson parameter for coloring")
    parser.add_argument("-o", "--output", type=str, default="quantum_network.png", help="Output filename")

    args = parser.parse_args()

    simulator = QuantumNetworkSimulator(
        R=args.R, aL=args.aL, b=args.b,
        g=args.g, np_photons=args.np_photons,
        A_value=args.A_value
    )

    fiber_net, nodes = simulator.generate_waxman_graph(args.N)
    photonic_net = simulator.generate_photonic_network(fiber_net)
    ng_over_n = simulator.calculate_largest_cluster_size(photonic_net) / args.N

    simulator.plot_combined(nodes, fiber_net, photonic_net, args.N, ng_over_n, args.output)


if __name__ == "__main__":
    main()
