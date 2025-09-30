# 📘 Shortest Path Percolation – ER Network

This directory contains the implementation of the **Shortest Path Percolation (SPP)** model applied to **Erdős–Rényi (ER)** networks.  
Here, the network is fixed (generated according to the ER model), and only the network configurations and the **$C$** parameter (maximum allowed path cost) are editable.

---

## 📂 Structure

```
.  
├── data                        # Results from executions using the simulator 
├── data_notebook               # Results from executions using the notebook
├── README.md                   # Readme file
├── plot-ER.ipynb               # Notebook for plotting the dynamics
└── spp-ER.ipynb                # Notebook for shortest path percolation dynamics  
````
---

## 🎯 Purpose

This notebook was designed for:  
- Users with **little familiarity with command-line execution**;  
- Running the full dynamics in environments such as **Jupyter** or **Google Colab**;  
- Serving as a **validation of the Python implementation** of the dynamics.  

---

## 🔗 Original C Implementation

The original implementation of the Shortest Path Percolation was developed in **C** and can be accessed here: [Implementation in C](https://github.com/danielhankim/shortest-path-percolation)

---

## ▶️ How to Use

1. Open the `spp-ER.ipynb` notebook;
2. Set the network parameters (number of nodes, average degree, etc.) and the **$C$** parameter; 
3. Run the cells to execute the dynamics and visualize the results.  

---

## 🧩 Note

This repository aims to provide a **more accessible version** of the model for testing and visualization, while preserving the essence of the dynamics described in the original C version.


----
----




