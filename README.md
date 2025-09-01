# 🐍 Python implementation of the Shortest Path Percolation dynamics

This repository provides a **Python implementation** of the *Shortest Path Percolation* dynamics proposed in [1].  
The goal is to offer an accessible and extensible version of the model, while keeping the original logic presented by the authors.  

The original **C implementation**, developed by the article’s authors, can be found here:  
👉 [Shortest Path Percolation in C](https://github.com/danielhankim/shortest-path-percolation)


## 📖 Reference

[1] [Minsuk Kim and Filippo Radicchi. *Shortest-path percolation on random networks*. **Physical Review Letters**, 133(4), July 2024.](https://arxiv.org/pdf/2402.06753)

---

### Main Idea of the Dynamics 
Shortest Path Percolation model: $(a)$ Agent $t$ demands the origin–destination pair $o_t\to d_t$. There are two shortest paths of length $Q_t=4$, marked by blue dotted and red dashed edges. $(b)$ If $C\ge4$, the agent selects one of these paths uniformly at random and removes all its edges. Here, the red dashed edges fragmenting the network into four components.

<p align="center">
  <img src="https://github.com/VictorFrancheto/shortest-path-percolation-implementation/blob/main/spp_diagram.png">
</p>


### Definition of the Shortest Path Percolation (SPP) Model
The Shortest Path Percolation (SPP) model is defined as follows.  
For $t > 0$, we denote with $G_t = (V, E_t)$, composed of $N = |V|$ nodes and $E_t = |E_t|$ edges, the undirected and unweighted graph available to the agent $t$, and with $o_t \to d_t$ the origin-destination pair demanded by the agent $t$.  

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

