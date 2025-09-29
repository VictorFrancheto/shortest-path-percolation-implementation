# 🔗 Shortest Path Percolation – General Simulator

This repository contains simulation code for the **Shortest Path Percolation (SPP)** process on general networks. The goal is to explore percolation dynamics under different attack strategies and parameters:

- 🧩 Network size ($N$)  
- 🎯 Path-length cost parameter ($C$)  
- ⚡ Attack modes (random, hub, closeness, betweenness and DomiRank)  

📁 Project Structure
--------------------
```
spp_general/
├── .
├── .
├── .
│
├── spp_general_simulator/    # Core simulation package
├──  README.md                 # Project documentation and usage instructions
├── requirements.txt          # Python dependencies required to run the project
├── .gitignore                # Files and folders ignored by Git
│   ├── cli/                  # Command Line Interface (entry points for running simulations)
│   ├── main.py               # Main entry script for running simulations directly
│   ├── core/                 # Core classes and orchestrators for simulation pipeline
│   ├── attacks.py            # Pair-removal attack logic and attack strategies
│   ├── bfs.py                # Breadth-First Search utilities for path exploration
│   ├── clusters.py           # Component reconstruction using the modified NZ algorithm
│   ├── distributions.py      # Degree, distance and statistical distributions for analysis
│   ├── io.py                 # Network I/O (load/save from/to .txt, CSV, edge lists)
│   ├── pairs.py              # Pair generation and enumeration within distance C
│   ├── rng.py                # Random number generator (Mersenne Twister 64-bit)
│   ├── selectors.py          # Node/edge selection strategies (hub, closeness, betweenness, random...)
│   ├── simulator.py          # High-level simulator orchestrating multiple iterations
│   ├── unionfind.py          # Union-Find / Disjoint Set structure for component tracking
│   ├── utils.py              # Helper functions (copying networks, cleaning timestamps, etc.)
│   ├── network-save/         # Sample networks stored as edge list text files
│   ├── er1500-graph.txt      # Erdős–Rényi graph with N=1500 nodes (edge list format)


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

⚙️ Requirements
----------------
- Python 3.9 or newer  
- Pip installed  

▶️ How to Run the Simulation
------------------------------
Run simulations through the CLI:

```bash
python -m spp_general.spp_general_simulator.cli.main \
  --input_txt spp_general/spp_general_simulator/network-save/er1500-graph.txt \
  --attack random random \
  --iter 100
```

| Parameter       | Description                                                  | Example |
|-----------------|--------------------------------------------------------------|---------|
| `--input_txt`   | Path to network edge list file                               | `er1500-graph.txt` |
| `--attack`      | Attack modes for two nodes (`random`, `hub`, `closeness`)    | `random hub` |
| `--iter`        | Number of iterations per simulation                          | `100` |
| `--output_dir`  | (Optional) Custom folder for simulation results              | `./results` |

📌 Example
```bash
python -m spp_general.spp_general_simulator.cli.main \
  --input_txt spp_general/spp_general_simulator/network-save/er1500-graph.txt \
  --attack hub closeness \
  --iter 50 \
  --output_dir ./my_results
```

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
