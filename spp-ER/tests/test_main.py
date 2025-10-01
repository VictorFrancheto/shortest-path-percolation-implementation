import os
import sys
import tempfile
from src import main


def test_main_runs_with_defaults(tmp_path, monkeypatch):
    """
    Run main() with insufficient args -> should fallback to defaults
    and complete without crashing. Data files should be created.
    """
    # change cwd to tmp_path to avoid polluting repo
    monkeypatch.chdir(tmp_path)

    # run main with argc < 6 to trigger defaults
    main.main(1, ["prog"])

    # check if output directory was created (N=4096 default is heavy, so just existence)
    outdir = tmp_path / "notebook" / "data"
    assert outdir.exists()


def test_main_runs_with_small_args(tmp_path, monkeypatch):
    """
    Run main() with small graph parameters to check functionality.
    """
    monkeypatch.chdir(tmp_path)

    N = 8
    avg_k = 2
    C = 3
    num_iter = 1
    num_instance = 1

    argv = ["prog", str(N), str(avg_k), str(C), str(num_iter), str(num_instance)]
    main.main(len(argv), argv)

    outdir = tmp_path / f"notebook/data/N{N}/k{avg_k}/C{C}/"
    assert outdir.exists()

    files = list(outdir.glob("*.csv"))
    assert len(files) == 1
    # file should not be empty
    with open(files[0]) as f:
        content = f.read()
    assert len(content) > 0
