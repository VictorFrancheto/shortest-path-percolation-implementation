import pytest

from spp_general_simulator.config import build_config


def _base_kwargs(network_save_dir):
    return dict(network_dir=str(network_save_dir), network_file="tiny.txt", C=2, realizations=3, selection="random-random")


def test_build_config_defaults(network_save_dir):
    cfg = build_config(**_base_kwargs(network_save_dir))
    assert cfg.workers == 1
    assert cfg.rank_source == 1 and cfg.rank_target == 1
    assert cfg.seed is None
    assert cfg.attack_mode_1 == "random" and cfg.attack_mode_2 == "random"
    assert cfg.output_dir.name == "spp-results"


def test_build_config_splits_selection_into_modes(network_save_dir):
    kwargs = _base_kwargs(network_save_dir)
    kwargs["selection"] = "hub-closeness"
    cfg = build_config(**kwargs)
    assert cfg.attack_mode_1 == "hub"
    assert cfg.attack_mode_2 == "closeness"


def test_build_config_rejects_missing_network_file(network_save_dir):
    kwargs = _base_kwargs(network_save_dir)
    kwargs["network_file"] = "does-not-exist.txt"
    with pytest.raises(ValueError, match="not found"):
        build_config(**kwargs)


@pytest.mark.parametrize("bad_C", [0, -1, -100])
def test_build_config_rejects_non_positive_C(network_save_dir, bad_C):
    kwargs = _base_kwargs(network_save_dir)
    kwargs["C"] = bad_C
    with pytest.raises(ValueError, match="C must be"):
        build_config(**kwargs)


@pytest.mark.parametrize("bad_realizations", [0, -5])
def test_build_config_rejects_non_positive_realizations(network_save_dir, bad_realizations):
    kwargs = _base_kwargs(network_save_dir)
    kwargs["realizations"] = bad_realizations
    with pytest.raises(ValueError, match="realizations must be"):
        build_config(**kwargs)


@pytest.mark.parametrize("bad_workers", [0, -1])
def test_build_config_rejects_non_positive_workers(network_save_dir, bad_workers):
    kwargs = _base_kwargs(network_save_dir)
    kwargs["workers"] = bad_workers
    with pytest.raises(ValueError, match="workers must be"):
        build_config(**kwargs)


def test_build_config_rejects_unknown_selection(network_save_dir):
    kwargs = _base_kwargs(network_save_dir)
    kwargs["selection"] = "not-a-strategy"
    with pytest.raises(ValueError, match="Unknown selection"):
        build_config(**kwargs)


@pytest.mark.parametrize("field,value", [("rank_source", 0), ("rank_target", -1)])
def test_build_config_rejects_non_positive_ranks(network_save_dir, field, value):
    kwargs = _base_kwargs(network_save_dir)
    kwargs[field] = value
    with pytest.raises(ValueError, match="rank_"):
        build_config(**kwargs)
