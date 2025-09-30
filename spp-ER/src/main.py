
from .utils import *
from .bfs import *
from .network import *
from .removal import *
from .tree import *



def main(argc, argv):
    """
    Main entry point for running network percolation simulations.

    Args:
        argc (int): number of arguments
        argv (list[str]): command line arguments
    """
    start = time.time()
    mean_cpu_time = 0.0

    # Defaults if arguments are missing
    if argc < 6:
        print("Insufficient arguments! Using default values:")
        N = 4096
        avg_k = 4
        C = N
        num_iter = 10
        num_instance = 1
    else:
        N = int(argv[1])       # network size
        avg_k = int(argv[2])   # mean degree
        C = int(argv[3])       # maximum cost
        num_iter = int(argv[4])
        num_instance = int(argv[5])

    E = int(0.5*N*avg_k)

    # Allocate structures
    bond = [[] for _ in range(N+1)]
    bond[0] = [0]*(N+1)
    for i in range(1, N+1):
        bond[i] = [0]

    copy_bond = [[] for _ in range(N+1)]
    copy_bond[0] = [0]*(N+1)

    edges = [[] for _ in range(2)]
    edges[0] = [0]*(E+1)
    edges[1] = [0]*(E+1)

    update_time = [0]*(E+1)

    largest_cluster = []
    for _ in range(6):
        largest_cluster.append([0.0]*(E+1))

    # Random seed
    pid_id = int(time.time()) * os.getpid()
    init_genrand64(pid_id)

    for x in range(num_instance):
        generate_ERgraph(N, bond, E)

        for i in range(num_iter):
            copy_network(N, bond, copy_bond)
            clean_time_stamp(update_time, E)

            # threshold = 7*N^0.44
            threshold = int(7*(N**0.44))

            # Run efficient pair removal
            efficient_pair_removal(C, N, copy_bond, edges, E, update_time, threshold)

            # Run modified NZ algorithm
            modified_NZ_algorithm(N, edges, largest_cluster)

            # Output results
            if C > 0:
                dir_path = f"./notebook/data/N{N}/k{avg_k}/C{C}/"
                file_id = i
                file_name = f"{dir_path}full_data_{file_id}.csv"
            else:
                dir_path = f"./notebook/data/N{N}/k{avg_k}/C{N}/"
                file_id = i
                file_name = f"{dir_path}full_data_{file_id}.csv"

            os.makedirs(dir_path, exist_ok=True)

            with open(file_name, "w") as f:
                for j in range(1, edges[0][0] + 1):
                    removed_edges = float(j)/float(edges[0][0])
                    f.write(f"{removed_edges:.10f} "
                            f"{largest_cluster[1][j]:.10f} "
                            f"{largest_cluster[2][j]:.10f} "
                            f"{largest_cluster[3][j]:.10f} "
                            f"{largest_cluster[4][j]:.10f} "
                            f"{largest_cluster[5][j]:.10f} "
                            f"{edges[0][j]} "
                            f"{edges[1][j]} "
                            f"{update_time[j]}\n")

    end = time.time()
    cpu_time_used = (end - start)
    print(f"# mean simulation time for N={N} C={C} calculated from {num_instance} instances "
          f"and {num_iter} iterations : {cpu_time_used/(num_instance*num_iter)}")


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
