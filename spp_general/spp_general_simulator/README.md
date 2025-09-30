# 🕸️ Shortest Path Percolation – General Simulator

This repository contains simulation code for the **Shortest Path Percolation (SPP)** process on general networks. The goal is to explore percolation dynamics under different attack strategies and parameters:

- 🧩 Network size ($N$); 
- 🎯 Path-length cost parameter ($C$);  
- ⚡ Attack modes (random, hub, closeness, betweenness and DomiRank). 

📁 Project Structure
--------------------
```
spp_general/
├── spp_general_simulator/       # Core simulation package
│   ├── cli/                     # Command Line Interface (entry points for running simulations)
│   │   └── main.py              # Main script to run simulations directly
│   │
│   ├── core/                    # Core classes and orchestrators for the simulation pipeline
│   │   ├── attacks.py           # Pair-removal attack logic and attack strategies
│   │   ├── bfs.py               # Breadth-First Search utilities for path exploration
│   │   ├── clusters.py          # Component reconstruction using the modified NZ algorithm
│   │   ├── distributions.py     # Degree, distance and statistical distributions for analysis
│   │   ├── io.py                # Network I/O (load/save from/to .txt, CSV, edge lists)
│   │   ├── pairs.py             # Pair generation and enumeration within distance C
│   │   ├── rng.py               # Random number generator (Mersenne Twister 64-bit)
│   │   ├── selectors.py         # Node/edge selection strategies (hub, closeness, betweenness, random…)
│   │   ├── simulator.py         # High-level simulator orchestrating multiple iterations
│   │   ├── unionfind.py         # Union-Find / Disjoint Set structure for component tracking
│   │   └── utils.py             # Helper functions (copying networks, cleaning timestamps, etc.)
│   │
│   ├── network-save/            # Sample networks stored as edge list text files
│   │   └── er1500-graph.txt     # Erdős–Rényi graph with N=1500 nodes
│   │
│   ├── __init__.py
│   ├── README.md
│   └── requirements.txt
│
├── spp-general-notebook/        # Jupyter notebooks for analysis and visualization
│   ├── __init__.py
│   ├── README.md
│   └── requirements.txt
│
├── spp-ER/                      # Specialized ER percolation simulator
│   └── README.md
│
├── README.md                    # Root project documentation
├── requirements.txt             # Global dependencies (if needed)
└── spp_diagram.png              # Diagram of the project/simulator



```

📦 Setup Instructions
----------------------
Before running the simulation, make sure to clone the repository and set up a Python environment.

### Clone this repository
```bash
git clone https://github.com/<your-username>/shortest-path-percolation-implementation.git
cd shortest-path-percolation-implementation
```

### Create a virtual environment
```bash
python -m venv .venv
```

Activate it:
- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate
  ```
- **Linux/Mac:**
  ```bash
  source .venv/bin/activate
  ```

### Install requirements
```bash
pip install -r requirements.txt
```

## 📂 Network File Format  

To run simulations, the network must be stored as a **plain text edge list** (`.txt`).  

Each line represents an edge in the graph: `i j`, where `i` and `j` are integers representing node IDs.  

### Indexing  
By default, nodes should be **1-indexed** (start at 1).  
Example: a graph with 3 nodes and edges `(1,2)` and `(2,3)` is written as:  
`1 2`  
`2 3`  

### Isolated nodes  
To ensure all nodes are represented, isolated nodes must appear as a self-loop `(i i)`.  
Example: if node 4 has no connections, include the line:  
`4 4`  

### Important  
- No comments (`# ...`) or extra spaces.  
- No empty lines.  
- Each line must contain exactly two integers.  

### ✅ Example of a valid network file (`er1500-graph.txt`)  
`1 2`  
`1 3`  
`2 4`  
`5 5`




▶️ How to Run the Simulation
------------------------------
Run simulations through the CLI:

```bash
python -m spp_general_simulator.cli.main --input_txt spp_general_simulator/network-save/er1500-graph.txt --attack random random --iter 10

```

| Parameter       | Description                                                  | Example |
|-----------------|--------------------------------------------------------------|---------|
| `--input_txt`   | Path to network edge list file                               | `er1500-graph.txt` |
| `--attack`      | Attack modes for two nodes (`random`, `hub`, `closeness`)    | `random hub` |
| `--iter`        | Number of iterations per simulation                          | `10` |
| `--output_dir`  | (Optional) Custom folder for simulation results              | `./results` |

📌 Example
```bash
python -m spp_general_simulator.cli.main \
  --input_txt spp_general_simulator/network-save/er1500-graph.txt \
  --attack hub closeness \
  --iter 10 \
  --output_dir ./my_results

```

By default, the files are saved in the folder [spp-general-notebook](https://github.com/VictorFrancheto/shortest-path-percolation-implementation/tree/main/spp_general/spp-general-notebook) under the name **data_simulator**, which refers to the data generated by the simulator.



🔍 What Happens When You Run It?
----------------------------------
1. 📡 Loads the input network from `.txt` edge list;  
2. 🔁 Runs the **efficient pair-removal** attack strategy for given iterations;  
3. 🧮 Reconstructs connected components with the modified NZ algorithm;  
4. 📊 Saves output metrics (`largest cluster`, `edges removed`, timestamps).  

📤 Output Files
------------------
- Results are saved in:
```
spp_general/spp-general-notebook/data_simulator/N{N}/{mode}/C{C}/full_data_*.csv
```
- You can also override the base folder with `--output_dir`.  
- Each CSV contains percolation dynamics for one simulation run.  

💡 Experiment with different network sizes, attack modes, and $C$ values to analyze robustness and percolation thresholds in complex networks.
