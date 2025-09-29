import os, time
from .attacks import core_pair_removal_loop, remove_pair_w_pair_info_v2
from .pairs import find_all_possible_pairs
from .clusters import modified_NZ_algorithm
from .utils import copy_network, clean_time_stamp
from .rng import init_genrand64
from .io import read_network_from_txt, network_to_bond


def efficient_pair_removal(C, N, bond, edges, E, update_time, threshold,
                           attack_mode_1="random", attack_mode_2="random",
                           rank_1=1, rank_2=1):
    """
    Orchestrates the attack strategy and executes the pair-removal pipeline.

    This function combines the core attack routine with post-processing steps:
    - Selects nodes based on the given attack modes and ranks.
    - Removes edges along shortest paths between the chosen nodes.
    - Enumerates all possible remaining pairs within distance C (or all if C == -1).
    - Applies further edge removals along shortest paths of these pairs.

    Parameters
    ----------
    C : int
        Maximum path length to explore (-1 means use N as the limit).
    N : int
        Number of nodes in the network.
    bond : list
        Bond adjacency structure of the network.
    edges : list[list[int]]
        Container for storing removed edges.
    E : int
        Initial number of edges in the network.
    update_time : list[int]
        Time stamps for edge removals.
    threshold : int
        Maximum number of consecutive failures before termination.
    attack_mode_1 : str, optional
        Selection mode for the first node ('random', 'hub', 'closeness', 'betweenness').
    attack_mode_2 : str, optional
        Selection mode for the second node ('random', 'hub', 'closeness', 'betweenness').
    rank_1 : int, optional
        Rank of the first node (1 = highest, 2 = second highest, etc.).
    rank_2 : int, optional
        Rank of the second node.

    Notes
    -----
    This function is the high-level orchestrator:
    it first calls `core_pair_removal_loop` to perform initial attacks,
    then uses `find_all_possible_pairs` and `remove_pair_w_pair_info_v2`
    to extend removals across all candidate pairs.
    """
    core_pair_removal_loop(C, N, bond, edges, E, update_time, threshold,
                           attack_mode_1=attack_mode_1,
                           attack_mode_2=attack_mode_2,
                           rank_1=rank_1,
                           rank_2=rank_2)

    pairs = [[0], [0]]
    find_all_possible_pairs(C, N, bond, pairs)
    remove_pair_w_pair_info_v2(C, N, bond, pairs, edges, update_time)
    

def main(N_values=[300, 500, 600, 1000],
         C_values=None,
         num_iter=1000,
         num_instance=1,
         output_dir="./spp_general/spp-general-notebook/data_simulator",
         input_txt=None,
         one_indexed=True,
         attack_mode_1="random", attack_mode_2="random",
         rank_1=1, rank_2=2):
    """
    Run the Shortest Path Percolation (SPP) simulations for different network sizes
    and path-length limits.

    Parameters
    ----------
    N_values : list[int], optional
        List of network sizes (number of nodes) to simulate. Overridden if input_txt is provided.
    C_values : list[int] or None, optional
        List of path-length limits to explore. If None, defaults to [1, 2, 3, N].
        Use "N" to denote the maximum path length.
    num_iter : int, optional
        Number of iterations per (N, C) configuration.
    num_instance : int, optional
        Number of independent instances per configuration (using the same base graph).
    output_dir : str, optional
        Directory where simulation results will be saved.
    input_txt : str or None, optional
        Path to a .txt file containing the network edge list. If provided,
        the network is loaded from this file and N_values is ignored.
    one_indexed : bool, optional
        If True, interpret the edge list as 1-indexed.
    attack_mode_1 : str, optional
        Selection mode for the first node ('random', 'hub', 'closeness', 'betweenness').
    attack_mode_2 : str, optional
        Selection mode for the second node ('random', 'hub', 'closeness', 'betweenness').
    rank_1 : int, optional
        Rank for the first node (1 = highest, 2 = second highest, etc.).
    rank_2 : int, optional
        Rank for the second node.

    Notes
    -----
    - For each (N, C) configuration, the algorithm:
      1. Builds the bond structure from the input graph.
      2. Runs the efficient pair-removal attack for `num_iter` iterations.
      3. Reconstructs connected components using the modified NZ algorithm.
      4. Saves results (removed edges, largest component metrics, timestamps) to CSV files.
    - Output files are stored in subdirectories grouped by N, attack mode, and C.
    """
    start = time.time()
    pid_id = int(time.time()) * os.getpid()
    init_genrand64(pid_id)

    if input_txt is not None:
        G = read_network_from_txt(input_txt, one_indexed=one_indexed)
        bond_base, N_file = network_to_bond(G)
        N_values = [N_file]

    for N in N_values:
        if C_values is None:
            C_list = [1, 2, 3, N]
        else:
            C_list = [c if c != "N" else N for c in C_values]

        for C in C_list:
            print(f"Starting simulation: N={N}, C={C}, "
                  f"attack_mode_1={attack_mode_1}, attack_mode_2={attack_mode_2}, "
                  f"rank_1={rank_1}, rank_2={rank_2}")

            for _ in range(num_instance):
                if input_txt is not None:
                    bond = [[] for _ in range(N + 1)]
                    bond[0] = [0] * (N + 1)
                    for i in range(1, N + 1):
                        bond[i] = [0]
                    copy_network(N, bond_base, bond)
                else:
                    raise ValueError("Missing 'input_txt'. Provide a .txt file with the network (edge list).")

                E = int(sum(bond[0][i] for i in range(1, N+1)) // 2)
                edges = [[0] * (E+1), [0] * (E+1)]
                update_time = [0] * (E+1)
                largest_cluster = [[0.0] * (E+1) for _ in range(6)]

                for iteration in range(num_iter):
                    copy_bond = [[] for _ in range(N+1)]
                    copy_bond[0] = [0] * (N+1)
                    copy_network(N, bond, copy_bond)

                    clean_time_stamp(update_time, E)
                    threshold = int(7 * (N**0.44))

                    efficient_pair_removal(
                        C, N, copy_bond, edges, E, update_time, threshold,
                        attack_mode_1=attack_mode_1,
                        attack_mode_2=attack_mode_2,
                        rank_1=rank_1,
                        rank_2=rank_2
                    )

                    modified_NZ_algorithm(N, edges, largest_cluster)

                    mode_name = f"{attack_mode_1}{rank_1}-{attack_mode_2}{rank_2}"
                    C_folder = C if C > 0 else N
                    dir_path = f"{output_dir}/N{N}/{mode_name}/C{C_folder}/"
                    os.makedirs(dir_path, exist_ok=True)

                    file_name = f"{dir_path}full_data_{iteration}.csv"
                    with open(file_name, "w") as f:
                        for j in range(1, edges[0][0] + 1):
                            removed_edges = float(j) / float(edges[0][0])
                            f.write(
                                f"{removed_edges:.10f} "
                                f"{largest_cluster[1][j]:.10f} "
                                f"{largest_cluster[2][j]:.10f} "
                                f"{largest_cluster[3][j]:.10f} "
                                f"{largest_cluster[4][j]:.10f} "
                                f"{largest_cluster[5][j]:.10f} "
                                f"{edges[0][j]} "
                                f"{edges[1][j]} "
                                f"{update_time[j]}\n"
                            )
                print(f"Finished simulation: N={N}, C={C}\n")

    end = time.time()
    print(f"Total time: {end - start:.2f} seconds")