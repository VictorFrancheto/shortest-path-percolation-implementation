# SPP General Simulator

A Python implementation of the **Shortest-Path Percolation (SPP)** dynamics
described in [`spp-dynamic.ipynb`](../spp-general-notebook/spp-dynamic.ipynb).
That notebook is the single source of truth for the algorithm: this package
reproduces its logic exactly (both removal phases, every source/target
selection criterion, and the cluster-size reconstruction), organized into a
modular, tested, command-line-driven package.

The simulator does **not** generate networks. It only loads a network that
has already been saved as a `.txt` edge list (e.g. inside `network-save/`)
and runs the SPP dynamics on it.

## 1. What the dynamics actually do

Each realization removes edges from the network in two phases, then
reconstructs the giant-component/susceptibility curve from the removal order:

1. **Phase 1 - targeted attack.** Repeatedly picks a `(source, target)` pair
   according to the chosen selection strategy, finds a shortest path between
   them of length at most `C` (sampled *uniformly at random* among all such
   shortest paths), and removes every edge along it. This repeats until a
   number of consecutive failures (no path found) reaches an internal
   threshold, `int(7 * N**0.44)` -- the same formula used in the notebook;
   it is not a CLI parameter.
2. **Phase 2 - uniform mop-up.** Once Phase 1 gives up, Phase 2 keeps
   sampling uniformly among *whichever pairs of nodes are still reachable*
   within `C` hops (regardless of the selection strategy -- Phase 2 is always
   uniform) and removes their connecting path, until no such pair remains.
   Since any surviving edge keeps its two endpoints reachable within 1 hop,
   Phase 2 only stops once **every edge has been removed**: the selection
   strategy controls *the order* in which edges disappear, not whether they
   eventually do.
3. **Cluster reconstruction.** The full removal order (Phase 1 + Phase 2,
   covering every edge) is replayed backwards, adding edges back one at a
   time via a Newman-Ziff union-find, to compute the giant-component
   fraction and the susceptibility `<s^2>/<s>` (excluding the giant
   component) at every step.

Each realization is one independent run of this process from a fresh copy of
the original network, driven by its own random seed.

## 2. Installation

The commands below assume your current directory is `spp_general_simulator/`
(this folder).

### 2.1 Create a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your shell prompt will be prefixed with `(.venv)` once it's active. To leave
the virtual environment later, run `deactivate` (same command on both
platforms). Activation only affects your current shell session, so it stays
active even after you `cd` elsewhere (needed for section 4 below).

### 2.2 Install the dependencies

```bash
pip install -r requirements.txt
```

This installs everything required to run the simulator and its test suite
(NumPy, SciPy, NetworkX, joblib, pytest). Optionally, install
[`numba`](https://numba.readthedocs.io/) as well (`pip install numba`) to
JIT-compile the BFS/removal kernels for a large speedup -- everything runs
correctly without it too, just slower in pure Python.

## 3. Network file format

Networks live in a directory such as `network-save/` and are plain-text edge
lists, one edge per line:

```
1 2
1 3
2 4
5 5
```

Rules (matching `network-save/er1500-graph.txt` and the other files the
notebook produces):

- Each line is `i j`, two whitespace-separated integers.
- Node IDs are **1-indexed**.
- An isolated node (no edges) is still represented, as a self-loop line
  `i i` -- the loader keeps the node and strips the self-loop.

The simulator only *reads* these files; it never creates or modifies them.

## 4. How to run

`spp_general_simulator` is a Python package, so `python -m spp_general_simulator`
must be run from the directory that *contains* `spp_general_simulator/`, one
level above this folder -- otherwise Python can't resolve the package by
that name. Go up one directory first:

```bash
cd ..
```

(if you created a virtual environment in step 2.1, it stays active after
`cd` -- no need to reactivate it)

```bash
python -m spp_general_simulator \
    --network-dir spp_general_simulator/network-save \
    --network-file er1500-graph.txt \
    --C 3 \
    --realizations 1000 \
    --workers 4 \
    --selection random-random
```

More examples, one per base selection mode (still run from that same parent
directory):

```bash
# Random source and target (classic percolation).
python -m spp_general_simulator --network-dir spp_general_simulator/network-save --network-file er1500-graph.txt --C 3 --realizations 200 --selection random-random

# Attack starting from the highest-degree hub, random target, C finite, single worker (the default).
python -m spp_general_simulator --network-dir spp_general_simulator/network-save --network-file er1500-graph.txt --C 2 --realizations 200 --selection hub-random

# Both endpoints are the most "central" nodes by closeness.
python -m spp_general_simulator --network-dir spp_general_simulator/network-save --network-file er1500-graph.txt --C 3 --realizations 100 --selection closeness-closeness

# Betweenness-guided source, random target.
python -m spp_general_simulator --network-dir spp_general_simulator/network-save --network-file er1500-graph.txt --C 3 --realizations 100 --selection betweenness-random

# DomiRank-guided dismantling attack, 4 parallel workers.
python -m spp_general_simulator --network-dir spp_general_simulator/network-save --network-file er1500-graph.txt --C 3 --realizations 100 --workers 4 --selection domirank-random
```

Results land in `spp-results/` by default, relative to wherever you ran the
command from (see `--output-dir` in section 5) -- so with the `cd ..` above,
that's the parent directory, not inside `spp_general_simulator/`. Pass an
explicit `--output-dir spp_general_simulator/spp-results` if you'd rather
keep results alongside the package.

`--workers 1` (the default, shown by omission above) runs every realization
sequentially in the current process. Passing `--workers N` with `N > 1`
distributes the realizations across `N` processes (via `joblib`); the split
across processes never changes the result: each realization's random seed
depends only on `--seed` and its own index, never on which worker ran it.

## 5. Parameters

| Argument | Required | Default | Meaning |
|---|---|---|---|
| `--network-dir` | yes | - | Directory containing the network file (e.g. `network-save`). |
| `--network-file` | yes | - | Name of the `.txt` edge-list file inside `--network-dir`. |
| `--C` | yes | - | Maximum shortest-path length (in hops) considered by the dynamics. Positive integer. |
| `--realizations` | yes | - | Number of independent realizations (seeds) to run. |
| `--selection` | yes | - | Source/target selection strategy, `"<source_mode>-<target_mode>"`. See section 6. |
| `--workers` | no | **`1`** | Number of parallel worker processes. `1` = sequential. |
| `--rank-source` | no | `1` | Rank of the source node for ranking-based modes (`hub`/`closeness`/`betweenness`/`domirank`); ignored for `random`. |
| `--rank-target` | no | `1` | Rank of the target node for ranking-based modes; ignored for `random`. |
| `--output-dir` | no | `./spp-results` | Where per-realization `.npz` result files are written. |
| `--seed` | no | `None` | Base seed. Same seed + same pending realizations => identical results, regardless of `--workers`. Without it, seeds are derived from wall-clock time (non-reproducible). |

Each realization's result is written to
`{output-dir}/{selection}/C{C}/realization_{i}.npz`, containing `removed`
(fraction of edges removed so far), `largest` (giant-component fraction),
`chi` (susceptibility), `edges_a`/`edges_b` (the endpoints removed at each
step) and `update_time` (the internal step counter at which that edge was
removed). If a realization's file already exists, it is skipped -- an
interrupted run can simply be re-launched with the same arguments to resume.

## 6. Selection criteria (source/target)

This is the notebook's `selection_strategy`, unchanged: a string
`"<source_mode>-<target_mode>"`, where each side is one of five base modes.
Any of the 5 x 5 = 25 combinations is valid. The **same five modes** are used
for both the source and the target; only the *rank* (`--rank-source` /
`--rank-target`) can differ.

| Mode | How it picks a node |
|---|---|
| `random` | Uniformly at random among all `N` nodes (excluding the node already picked for the other side). |
| `hub` | The `rank`-th highest-degree node. Ties (equal degree) are broken by the **smallest node id**. |
| `closeness` | The `rank`-th highest [closeness-centrality](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.closeness_centrality.html) node. |
| `betweenness` | The `rank`-th highest [betweenness-centrality](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html) node. |
| `domirank` | The `rank`-th highest [DomiRank-centrality](https://github.com/mengsig/DomiRank) node (dominance-based centrality; falls back to `hub` ranking if the underlying eigen-solve does not converge). |

How a pair is chosen at each step of the dynamics:

1. The **source** is selected first using `<source_mode>` at rank
   `--rank-source` (no exclusions).
2. The **target** is selected using `<target_mode>` at rank `--rank-target`,
   **excluding the node just picked as source** -- source and target are
   always different nodes.
3. `random` and `hub` are recomputed cheaply at every step (`hub` from the
   current degree sequence, in `O(1)` amortized via a degree bucket).
   `closeness`, `betweenness` and `domirank` rebuild the graph and recompute
   the metric **from scratch on the current, partially-stripped network**
   at every step, since edges keep disappearing -- this makes them
   noticeably slower and is only practical on small/medium networks.
4. Whichever of the two chosen nodes currently has the **higher degree** is
   treated as the path's target for the internal search (the lower-degree
   node is explored from first); this never changes *which* pair is
   attacked or *which* edges can be removed, it only affects the search
   order.
5. Once `(source, target)` is fixed, a shortest path between them of length
   `<= C` is sampled uniformly at random among all such shortest paths, and
   every edge on it is removed. If no such path exists, that step counts as
   a failure (see section 1) and no selection-strategy state changes as a
   result -- the same rule is retried on the next step.

Two things worth calling out explicitly:

- Phase 2 (the mop-up phase, described in section 1) **always** samples
  uniformly among the remaining reachable pairs, regardless of
  `--selection`. The selection strategy only shapes Phase 1.
- There is no separate "default" selection in the notebook -- `--selection`
  is always required. Its default *rank* is 1 for both sides.

Examples of what the strategy name means:

- `random-random`: classic percolation, no bias.
- `hub-random`: attack starts at the network's current highest-degree hub,
  ends at a random node.
- `random-hub`: ends at the hub instead.
- `betweenness-betweenness`: both endpoints are the highest-betweenness
  ("bridge") nodes.
- `closeness-random`: source is the most central node by closeness, target
  is random.
- `domirank-domirank`: a pure DomiRank dismantling attack.

## 7. Tests

```bash
pytest
```

The suite uses small, fully deterministic networks (triangles, paths,
stars, 4-cycles, disconnected pairs) so that expected outputs -- removed
edges, giant-component sizes, susceptibility values -- can be checked
exactly, plus a fixed-seed Erdos-Renyi network (N=24) for the
centrality-based selection modes. It covers: network loading (including the
self-loop/isolated-node convention), CSR edge removal and the degree
bucket, parameter validation, every selection criterion, the BFS/path
sampler, both removal phases (including the Fenwick-tree lazy sampler),
cluster reconstruction, the full per-realization pipeline, running multiple
realizations sequentially and in parallel (`--workers`), and the CLI itself.
