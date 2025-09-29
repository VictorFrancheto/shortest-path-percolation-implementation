# 🔗 Shortest Path Percolation – General Simulator
=================================================

This repository contains simulation code for the **Shortest Path Percolation (SPP)** process on general networks. The goal is to explore percolation dynamics under different attack strategies and parameters:

- 🧩 Network size ($N$)  
- 🎯 Path-length cost parameter ($C$)  
- ⚡ Attack modes (random, hub, closeness, betweenness)  

📁 Project Structure
--------------------
```
spp_general/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── .gitignore                # Ignored files
├── spp_general_simulator/    # Core simulation package
│   ├── cli/                  # Command line interface
│   ├── attacks.py            # Pair-removal attack logic
│   ├── clusters.py           # Component reconstruction (NZ algorithm)
│   ├── io.py                 # Network I/O (edge list loading)
│   ├── rng.py                # Random number generator
│   ├── utils.py              # Helpers and utilities
│   └── ...
└── spp-general-notebook/     # Jupyter notebooks & results
    └── data_simulator/       # Simulation outputs
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
