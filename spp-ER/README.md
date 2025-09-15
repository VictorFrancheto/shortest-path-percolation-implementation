# ⚙️ How to execute the script (src)

The source code is located in the `src/` folder, and execution is done via `main.py`.

----------------------------------------------------
📂 Project Structure
----------------------------------------------------
```
spp-er/
├── README.md
├── requirements.txt
└── src/
    ├── __init__.py
    ├── bfs.py
    ├── main.py
    ├── network.py
    ├── removal.py
    ├── tree.py
    └── utils.py
```

⚙️ Installation

# Requires Python 3.9+ and pip
pip install -r requirements.txt


▶️ How to Run (positional arguments)

# Run the script with the following arguments in order:
python src/main.py N avg_k C num_iter num_instance

Parameters:
- $N$            → number of nodes (e.g., 4096)
- $avg_k$        → grau average degree of the ER network (e.g., 4)
- $C$            → SPP cost/control parameter (e.g., 1, 2, 3, …)
- num_iter      → number of iterations per instance (e.g., 50)
- num_instance  → number of independent instances (e.g., 1)

Examples:
python src/main.py 4096 8 1 50 1
python src/main.py 1024 16 2 30 1


🧠 What main.py does

1. Generates an Erdős–Rényi network with N nodes and probability
   $p = \frac{avg_k}}{N - 1}$

2. Runs the Shortest Path Percolation (SPP) dynamics with cost parameter C
   for num_iter iterations across num_instance runs.

3. Stores aggregated results such as order parameters, averages,
   and possible critical thresholds.


📜 Notes

- 📝 For each realization, a CSV file is generated automatically.
- 🧹 After each run, memory is reset to avoid overload.
- 📂 Example output files are stored in: notebook/data








