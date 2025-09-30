# 🐍 Python implementation of the Shortest Path Percolation dynamics

This repository provides a **Python implementation** of the *Shortest Path Percolation* dynamics proposed in [1].  
The goal is to offer an accessible and extensible version of the model, while keeping the original logic presented by the authors.  

The original **C implementation**, developed by the article’s authors, can be found here:  
👉 [Shortest Path Percolation in C](https://github.com/danielhankim/shortest-path-percolation)

### 📂 Implementations

- 📌 The [spp-ER](https://github.com/VictorFrancheto/shortest-path-percolation-implementation/tree/main/spp-ER) folder contains the **Python implementation** of the *Shortest Path Percolation* dynamics introduced in [1], along with all the instructions required to run the model.  
  - Network considered: Erdős–Rényi (fixed);
  - Adjustable parameters: network size, average degree, and the percolation cost $C$. 

- ⚙️ The [spp_general](https://github.com/VictorFrancheto/shortest-path-percolation-implementation/tree/main/spp_general) folder provides a more general and flexible version of the percolation model, and the results obtained from this dynamics and the corresponding attacks are presented in [2].

  - Networks: **fully customizable**; 
  - Targeted attacks: **configurable**;
  - Includes: **quantum network implementation** used in the analyses of article [2];
  - Adjustable parameters: network, targeted attack, and the percolation cost $C$;
  - A detailed step-by-step guide for execution and usage is available in the corresponding *README*.


## 📖 Reference

[1] [Minsuk Kim and Filippo Radicchi. *Shortest-path percolation on random networks*. **Physical Review Letters**, 133(4), July 2024.](https://arxiv.org/pdf/2402.06753)\
[2] 

---

### 🔄 Main Idea of the Dynamics 
Shortest Path Percolation model: **$(a)$** There are two possible shortest paths connecting the origin–destination pair $o_t \rightarrow d_t$ demanded by agent $t$. These paths are represented by orange dotted edges and purple dashed edges, both of length $Q_t = 4$. **$(b)$** If the maximum length allowed in the SPP model is $C \geq 4$, one of the two shortest paths is selected uniformly at random, and all of its edges are removed from the graph. In this example, the **blue dashed edges** are deleted, fragmenting the graph into four clusters.  


<p align="center">
  <img src="https://github.com/VictorFrancheto/shortest-path-percolation-implementation/blob/main/spp_diagram.png">
</p>


### Definition of the Shortest Path Percolation (SPP) Model on Erdős–Rényi Networks
The Shortest Path Percolation (SPP) model is defined as follows.  
For $t > 0$, we denote with $G_t = (V, 𝓔_t)$, composed of $N = |V|$ nodes and $E_t = |𝓔_t|$ edges, the undirected and unweighted graph available to the agent $t$, and with $o_t \to d_t$ the origin-destination pair demanded by the agent $t$.  

If at least a path between $o_t$ and $d_t$ exists in $G_t$, we denote with $Q_t$ the length of the shortest one(s). The demand of the agent $t$ can be supplied only if $d_t$ is reachable from $o_t$ and $Q_t \leq C$, where $C > 0$ is a tunable parameter of the model.  

If one shortest path satisfying this condition is identified (one path is selected at random if more than one exists), namely  

$$
(o_t = i_1, i_2, \ldots, i_{Q_t+1} = d_t),
$$  

all edges in the path are removed from $G_t$, i.e.,  

$$
E_t \mapsto E_t \setminus \bigcup_{q=1}^{Q_t} (i_q, i_{q+1}),
$$  

see the figure above. If no path exists between $o_t$ and $d_t$ or if $Q_t > C$, no edge is removed from the graph. In either case, we copy the graph $G_{t+1} \mapsto G_t$ and then increase $t \mapsto t + 1$. The process is repeated until no more demand is requested or can be supplied.  

The behavior of the SPP model depends on the structure of the graph $G_1$ and the demand of the agents. Here, for simplicity, we assume that the graph $G_1$ is an instance of the Erdős–Rényi (ER) model with exactly $E_1 = \bar{k}N/2$ edges, with $\bar{k}$ the average degree of the graph. We further assume that the origin-destination nodes $o_t \to d_t$ demanded by the agent $t$ are chosen uniformly at random.  

These assumptions are not reasonable for the study of a real infrastructure and are made with the sole purpose of understanding the physics of the SPP model. They in fact allow us to contrast results obtained for the SPP model to those of other well-studied percolation models.  

For $C = 1$, the SPP model effectively reduces to the ordinary bond-percolation model on ER graphs, displaying a smooth transition when a fraction $p_c = 1 - 1/\bar{k}$ of randomly selected edges is removed from the graph. For $1 < C \leq N$, the SPP model differentiates from the ordinary bond-percolation model as edges in the graph are no longer deleted independently, but rather in a correlated fashion (note that $C = N$ is a limiting case, as the inequality $Q_t \leq C$ always holds as long as $o_t$ and $d_t$ are in the same connected component of the graph $G_t$).  

We explicitly refer to the *infinite*$-C$ *SPP model* when $\lim_{N \to \infty} C = \infty$; the *finite*$-C$ *SPP model* occurs otherwise.

-----

## ⚙️ Project Structure & How to Run

Before getting started, let’s highlight an important point.
Inside the `spp-ER` folder, you will find the Python implementation of the *Shortest Path Percolation* model presented in \[1].

It contains two main subdirectories:

📓 **Notebook** – here you will find examples to generate plots and a monolithic version of the code that runs the full dynamics.
This folder was created for users who may not be familiar with running code via command line, making it easier to use in environments like Jupyter or Colab.

📂 **src** – this folder contains the modular Python source code.
To run it, just follow the instructions provided in the **README** file inside the main `spp-ER` directory.

🚩 **Observation:** The folder structure of `spp-ER` is explicitly described below.

```

spp-ER/
│
├── notebook/                 # exploration notebooks
│   ├── plot-ER.ipynb
│   └── spp-ER.ipynb
│
├── src/
│   └── spp_er/               # package name (better in snake_case)
│       ├── __init__.py       # makes the directory a package
│       ├── main.py           # entry point
│       ├── utils.py          # utility functions
│       ├── bfs.py            # bfs and related functions
│       ├── removal.py        # pair removal functions
│       ├── tree.py           # tree and percolation functions
│       └── network.py        # basic network functions
│
├── tests/                    # unit tests
│   └── test_utils.py
│
├── README.md                 # usage documentation
├── requirements.txt          # dependencies (pandas, numpy, etc.)
├── setup.py                  # or pyproject.toml (for installation as a library)
└── .gitignore


