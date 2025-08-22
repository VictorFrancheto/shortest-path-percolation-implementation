# 🐍 Python implementation of the Shortest Path Percolation dynamics

This repository provides a **Python implementation** of the *Shortest Path Percolation* dynamics proposed in [1].  
The goal is to offer an accessible and extensible version of the model, while keeping the original logic presented by the authors.  

The original **C implementation**, developed by the article’s authors, can be found here:  
👉 [Shortest Path Percolation in C](https://github.com/danielhankim/shortest-path-percolation)

---

## 📖 Reference

[1] [Minsuk Kim and Filippo Radicchi. *Shortest-path percolation on random networks*. **Physical Review Letters**, 133(4), July 2024.](https://arxiv.org/pdf/2402.06753)



### Main Idea of the Dynamics 
Shortest Path Percolation model: $(a)$ Agent $t$ demands the origin–destination pair $o_t\to d_t$. There are two shortest paths of length $Q_t=4$, marked by blue dotted and red dashed edges. $(b)$ If $C\ge4$, the agent selects one of these paths uniformly at random and removes all its edges. Here, the red dashed edges fragmenting the network into four components.

<p align="center">
  <img src="https://github.com/VictorFrancheto/shortest-path-percolation-implementation/blob/main/spp_diagram.png">
</p>

