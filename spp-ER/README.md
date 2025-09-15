# Shortest Path Percolation on Erdős–Rényi Networks

This repository contains simulation code for studying the Shortest Path Percolation (SPP) process on Erdős–Rényi (ER) random networks. The goal is to explore how the percolation dynamics unfold as a function of network size, average degree, and an adjustable cost parameter.

----------------------------------------------------
📂 Project Structure
----------------------------------------------------
```
spp-er/
├── README.md        # You are reading this file
├── requirements.txt  # Python dependencies
└── src/              # Source code and implementations
    ├── __init__.py
    ├── bfs.py        # Breadth-first search utilities
    ├── main.py       # Main entry point for running simulations
    ├── network.py    # Network generation and helpers
    ├── removal.py    # Functions related to node removal
    ├── tree.py       # Tree generation routines
    └── utils.py      # Miscellaneous utilities

```

# Requirements

This project requires Python 3.9 or later. All Python dependencies are listed in requirements.txt and can be installed with the following command:

# Requires Python 3.9+ and pip
```
pip install -r requirements.txt
```

# Running the Simulation

To run a simulation you should execute the main.py script located in the src/ directory. It expects five positional arguments, corresponding to network and simulation parameters:

```
python src/main.py N avg_k C num_iter num_instance
```

|      Parameter | Description                                                                                           | Example |
| -------------: | :---------------------------------------------------------------------------------------------------- | :------ |
|            `N` | Number of nodes in the generated ER network.                                                          | `4096`  |
|        `avg_k` | Desired average degree of the network.  The linking probability is computed as `p = avg_k / (N − 1)`. | `8`     |
|            `C` | Cost/control parameter for the SPP dynamics (positive integer).                                       | `1`     |
|     `num_iter` | Number of iterations per instance.                                                                    | `50`    |
| `num_instance` | Number of independent network realisations to simulate.                                               | `1`     |


# Example Commands

Here are two example invocations:

# 4,096 nodes, average degree 8, cost parameter 1, 50 iterations, 1 realisation
```
python src/main.py 4096 8 1 50 1
```

# 1,024 nodes, average degree 16, cost parameter 2, 30 iterations, 1 realisation
```
python src/main.py 1024 16 2 30 1
```

# What the Script Does

When executed, src/main.py performs the following steps:

1. Network Generation: It creates an Erdős–Rényi network with N nodes. The probability of an edge between any two nodes is calculated as p = avg_k / (N − 1) to achieve the desired average degree avg_k.

2. SPP Dynamics: It runs the Shortest Path Percolation process for num_iter iterations using the cost parameter C. This is repeated across num_instance independent instances of the network.

3. Data Aggregation: Throughout the simulation, it collects order parameters, averages, and other relevant statistics. Aggregated results are written to CSV files to facilitate analysis.

3. Memory Cleanup: After each run, it resets any global state to avoid memory overload when running multiple instances sequentially.

# Outputs

For each realisation, the program produces a CSV file containing the results of the SPP dynamics. These files are automatically saved in the notebook/data directory (if it exists) or in the current working directory. You can use these CSV files to plot order parameters, locate critical thresholds, or perform further analysis.

Feel free to adapt the parameters and explore how the SPP dynamics depend on network size, average degree, and cost. Contributions and improvements are welcome!
