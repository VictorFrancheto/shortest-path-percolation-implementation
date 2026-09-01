import numpy as np

from spp_general_simulator.network_loader import (
    load_csr_mmap,
    load_network_csr,
    network_to_csr,
    read_network_from_txt,
    save_csr_to_disk,
)


def test_read_network_from_txt_shifts_one_indexed_ids(network_save_dir):
    G = read_network_from_txt(network_save_dir / "tiny.txt", one_indexed=True)
    assert set(G.nodes()) == {0, 1, 2, 3}
    assert set(map(frozenset, G.edges())) == {frozenset((0, 1)), frozenset((1, 2)), frozenset((0, 2))}


def test_read_network_from_txt_preserves_isolated_node_via_selfloop(network_save_dir):
    G = read_network_from_txt(network_save_dir / "tiny.txt", one_indexed=True, remove_selfloops=True)
    assert G.degree(3) == 0
    assert not nx_has_selfloop(G, 3)


def nx_has_selfloop(G, node):
    return G.has_edge(node, node)


def test_read_network_from_txt_keeps_selfloop_when_not_removed(network_save_dir):
    G = read_network_from_txt(network_save_dir / "tiny.txt", one_indexed=True, remove_selfloops=False)
    assert G.has_edge(3, 3)


def test_read_network_from_txt_zero_indexed_no_shift(tmp_path):
    (tmp_path / "zero.txt").write_text("0 1\n1 2\n")
    G = read_network_from_txt(tmp_path / "zero.txt", one_indexed=False)
    assert set(G.nodes()) == {0, 1, 2}


def test_network_to_csr_shapes_and_degrees(network_save_dir):
    G = read_network_from_txt(network_save_dir / "tiny.txt", one_indexed=True)
    deg, indptr, adj, twin, N = network_to_csr(G)

    assert N == 4
    assert deg.shape == (N + 1,)
    assert indptr.shape == (N + 2,)
    # triangle {1,2,3} each have degree 2 (1-indexed node ids), isolated node 4 has degree 0.
    assert deg[1] == 2 and deg[2] == 2 and deg[3] == 2 and deg[4] == 0
    total_adj = int(indptr[N + 1])
    assert total_adj == 2 * 3  # 3 edges, undirected -> 6 directed slots
    assert adj.shape == (total_adj,)
    assert twin.shape == (total_adj,)


def test_network_to_csr_twin_pointer_is_involutive_and_consistent(er_csr_n24):
    deg, indptr, adj, twin, N = er_csr_n24
    total_adj = int(indptr[N + 1])
    for e in range(total_adj):
        # twin is its own inverse.
        assert twin[twin[e]] == e
        # slot e belongs to some node i (indptr[i] <= e < indptr[i]+deg[i] initially,
        # but indptr never changes so we can find i from indptr directly).
        owner = np.searchsorted(indptr, e, side="right") - 1
        neighbor = adj[e]
        twin_owner = np.searchsorted(indptr, twin[e], side="right") - 1
        assert twin_owner == neighbor
        assert adj[twin[e]] == owner


def test_save_and_load_csr_mmap_roundtrip(tmp_path, triangle_csr):
    deg, indptr, adj, twin, N = triangle_csr
    base = save_csr_to_disk(deg, indptr, adj, twin, tmp_path / "csr")
    deg2, indptr2, adj2, twin2 = load_csr_mmap(base)
    assert np.array_equal(deg, deg2)
    assert np.array_equal(indptr, indptr2)
    assert np.array_equal(adj, adj2)
    assert np.array_equal(twin, twin2)


def test_load_network_csr_end_to_end(network_save_dir):
    deg, indptr, adj, twin, N = load_network_csr(network_save_dir, "tiny.txt")
    assert N == 4
    assert deg[4] == 0
