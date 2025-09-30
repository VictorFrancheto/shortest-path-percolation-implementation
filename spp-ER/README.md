🔗 Shortest Path Percolation on Erdős–Rényi Networks
=====================================================

This repository contains simulation code for the Shortest Path Percolation (SPP) process on Erdős–Rényi (ER) random networks. The goal is to explore how the percolation dynamics behave based on:

- 🧩 Network size ($N$)
- 🔗 Average degree ($avg_k$)
- 🎯 Cost parameter ($C$)

📁 Project Structure
--------------------
```
spp-ER/
├── README.md        
├── requirements.txt   # Python dependencies
└── src/               # Core simulation code
    ├── __init__.py
    ├── bfs.py         # Breadth-first search tools
    ├── main.py        # Main simulation entry
    ├── network.py     # ER network creation
    ├── removal.py     # Node removal logic
    ├── tree.py        # Tree construction
    └── utils.py       # Utility functions
```

📦 Setup Instructions
----------------------
Before running the simulation, make sure to clone the repository and install the required dependencies.

### Clone this repository
```
git clone https://github.com/<your-username>/spp-ER.git
cd spp-ER
```

⚙️ Virtual Environment
----------------------
It is recommended to create a virtual environment before installing dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # On Linux/Mac
.venv\Scripts\activate      # On Windows
```

⚙️ Requirements
----------------

Install dependencies with:
```bash
pip install -r requirements.txt
```

▶️ How to Run the Simulation
------------------------------
Run the simulation from the terminal **while inside the `spp-ER` directory** by executing the `main.py` script with the following positional arguments:

```bash
python src/main.py N avg_k C num_iter num_instance
```

| Parameter       | Description                                                | Example |
|----------------|------------------------------------------------------------|---------|
| $N$              | Number of nodes                                            | 4096    |
| $avg_k$          | Average degree of the network                              | 8       |
| $C$              | Cost parameter for SPP dynamics                            | 1       |
| num_iter         | Number of iterations per instance                          | 50      |
| num_instance     | Number of independent network realizations                 | 1       |

📌 Example
```bash
python -m src.main 4096 8 1 50 1
python -m src.main 1024 16 2 30 1
```

🔍 What Happens When You Run It?
----------------------------------
1. 📡 Generates an Erdős–Rényi network with $N$ nodes;
2. 🔁 Simulates SPP dynamics with cost parameter $C$, for `num_iter` rounds;
3. 📊 Aggregates order parameters and metrics;
4. 🧼 Frees memory after each instance.

📤 Output Files
------------------
- CSV files are saved for each simulation;
- Default location: `notebook/data` (or current directory if not present);
- If you choose to run the notebook [`spp-ER.ipynb`](https://github.com/VictorFrancheto/shortest-path-percolation-implementation/blob/main/spp-ER/notebook/plot-ER.ipynb)
 the output files will be saved in the `notebook/data_notebook`;
- You can analyze, plot or extend results easily from the outputs;

💡 Experiment with different parameter settings to better understand how the SPP dynamics respond to changes in network size, connectivity and cost.

----
----




