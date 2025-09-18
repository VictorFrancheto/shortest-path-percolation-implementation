# 🌐 Dynamics of the Quantum Internet Network

---

## 🧩 Step 1 – Fiber-Optics Network Simulation

We begin by uniformly distributing $N$ nodes within a disk of radius $R$. To model how optical fibers connect these nodes, we use the **Waxman model**. In this model, each pair of nodes $i$ and $j$ is connected by a fiber with probability:

$$
\Pi_{ij} = \beta e^{-d_{ij}/\alpha L}
$$

where $d_{ij}$ is the Euclidean distance between nodes $i$ and $j$, $L$ is the maximum distance between any two nodes, $\alpha > 0$ controls the typical edge length of the network, and $0 < \beta \leq 1$ determines the average degree of connectivity. These parameters have been estimated for real-world fiber-optic networks. For example, in the U.S. backbone network it was found that $\alpha L = 226$ km and $\beta = 1$. We adopt these values in the simulations presented here.

---

## 🧩 Step 2 – Photonic Network Simulation

Once the fiber-optics network is constructed, we simulate the transmission of photons through it. Photonic losses are known to grow exponentially with fiber length. More precisely, the **transmissivity**, i.e., the fraction of energy received at the output of a fiber link connecting nodes $i$ and $j$, is given by:

$$
p_{ij} = 10^{-\gamma d_{ij}/10}
$$

where $d_{ij}$ (in kilometers) is the Euclidean distance between the nodes, and $\gamma$ is the fiber loss coefficient, which depends on the photon wavelength. For instance, in silica fibers, losses are minimized at a wavelength of 1550 nm, resulting in $\gamma \approx 0.2$ dB/km, a value we use in our simulations. Even with technological advances, the physical loss limit of silica fibers is estimated to lie between 0.095 and 0.13 dB/km.

Finally, we define the probability $P_{ij}$ that two nodes are effectively connected by a photonic link as:

$$
P_{ij} = 1 - (1 - p_{ij})^{n_p}
$$
