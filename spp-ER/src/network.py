####################################
#           NETWORK UTILITIES      #
####################################

from .utils import *

def find_node(i, j, bond):
    """
    int find_node(int i, int j, int **bond)
    Returns index k if bond[i][k] == j, otherwise -1.
    """
    for k in range(1, bond[0][i] + 1):
        if bond[i][k] == j:
            return k
    return -1

def copy_network(N, origin_bond, copy_bond):
    """
    void copy_network(int N, int **origin_bond, int **copy_bond)
    Copies the bond structure from origin_bond to copy_bond.
    """
    for i in range(1, N+1):
        degree = origin_bond[0][i]
        copy_bond[0][i] = degree
        # Copy adjacency list (0..degree)
        copy_bond[i] = origin_bond[i][:degree+1]

def generate_ERgraph(N, bond, E):
    """
    void generate_ERgraph(int N, int **bond, int E)
    Generates an Erdős-Rényi graph with N nodes and E edges, populating bond.
    Does not update edges (if you need edges, update them manually).
    """
    for i in range(1, N+1):
        bond[0][i] = 0

    for _ in range(E):
        n = int(genrand64_real3() * N) + 1
        m = int(genrand64_real3() * N)
        control = 0
        while control == 0:
            m += 1
            if m > N:
                m = 1
            if n != m and find_node(n, m, bond) < 0:
                control = 1
        bond[0][n] += 1
        bond[n].append(m)
        bond[0][m] += 1
        bond[m].append(n)

def clean_time_stamp(update_time, E):
    """
    void clean_time_stamp(unsigned long long *time_stamp, int E)
    Sets update_time[i] = 0 for i = 1..E.
    """
    for i in range(1, E+1):
        update_time[i] = 0



####################################
# GEOMETRIC DISTRIBUTION
####################################

def geometric_distribution(P):
    """
    unsigned long long geometric_distribution(double P)

    Generates a random sample from a geometric distribution with 
    success probability P using the Mersenne Twister random generator.
    
    Returns:
        int: number of trials until the first success 
             (-1 if P <= 0, 1 if P == 1).
    """
    if P <= 0:
        return -1
    if P == 1:
        return 1
    u = genrand64_real3()
    interval = int(1 + math.floor(math.log(u)/math.log(1. - P)))
    return interval
