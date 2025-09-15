# Shortest Path Percolation (SPP-ER)

Python implementation of the Shortest Path Percolation model on Erdős–Rényi (ER) networks.  
The source code is located in the src/ folder, and execution is done via main.py.

----------------------------------------------------
📂 Structure
----------------------------------------------------
```
spp-er/
├── README.md
└── src/
    ├── __init__.py
    ├── bfs.py
    ├── main.py
    ├── network.py
    ├── removal.py
    ├── tree.py
    └── utils.py

----------------------------------------------------
▶️ Execution (positional arguments)
----------------------------------------------------
Run the script with positional arguments in the following order:

python src/main.py N avg_k C num_iter num_instance

Parameters:
- N            → number of nodes (e.g., 4096)
- avg_k        → target average degree of the ER network (e.g., 4)
- C            → SPP cost/control parameter (e.g., 1, 2, 3, …)
- num_iter     → number of iterations per instance (e.g., 50)
- num_instance → number of independent instances (e.g., 1)

Examples:
python src/main.py 4096 8 1 50 1
python src/main.py 1024 16 2 30 1

----------------------------------------------------
🧠 What main.py does (high level)
----------------------------------------------------
1. Generates an ER network with N nodes and probability p = avg_k / (N - 1).
2. Runs the SPP dynamics with cost C for num_iter iterations across num_instance instances.
3. Saves/displays aggregated metrics (depending on your implementation).

----------------------------------------------------
📜 Notes
----------------------------------------------------
- For each realization, a CSV file is generated.
- This avoids memory overload, since memory is reset after each run.
- Example output files are stored in: notebook/data

