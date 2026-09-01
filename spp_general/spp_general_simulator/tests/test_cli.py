from spp_general_simulator.cli import main
from spp_general_simulator.runner.results import RealizationResult, realization_path


def test_cli_rejects_unknown_selection(network_save_dir, capsys):
    code = main(["--network-dir", str(network_save_dir), "--network-file", "tiny.txt", "--C", "1", "--realizations", "1", "--selection", "not-a-strategy"])
    assert code == 2
    assert "Unknown selection" in capsys.readouterr().err


def test_cli_rejects_missing_network_file(tmp_path, capsys):
    code = main(["--network-dir", str(tmp_path), "--network-file", "missing.txt", "--C", "1", "--realizations", "1", "--selection", "random-random"])
    assert code == 2
    assert "not found" in capsys.readouterr().err


def test_cli_end_to_end_writes_realization_files(network_save_dir, tmp_path):
    output_dir = tmp_path / "results"
    code = main(["--network-dir", str(network_save_dir), "--network-file", "tiny.txt", "--C", "1", "--realizations", "2", "--selection", "random-random", "--workers", "1", "--seed", "5", "--output-dir", str(output_dir)])
    assert code == 0
    for i in range(2):
        path = realization_path(output_dir, "random-random", 1, i)
        assert path.exists()
        assert RealizationResult.load(path).edge_count == 3  # the tiny.txt triangle
