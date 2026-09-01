import pytest

from spp_general_simulator.selection.strategies import (
    NODE_SELECTION_MODES,
    SELECTION_STRATEGIES,
    resolve_selection_strategy,
)


def test_all_25_combinations_exist():
    assert len(SELECTION_STRATEGIES) == 25
    for mode_1 in NODE_SELECTION_MODES:
        for mode_2 in NODE_SELECTION_MODES:
            assert f"{mode_1}-{mode_2}" in SELECTION_STRATEGIES


def test_resolve_selection_strategy_splits_source_and_target():
    assert resolve_selection_strategy("hub-random") == ("hub", "random")
    assert resolve_selection_strategy("domirank-domirank") == ("domirank", "domirank")


def test_resolve_selection_strategy_rejects_unknown_with_helpful_message():
    with pytest.raises(ValueError, match="random-random"):
        resolve_selection_strategy("not-a-strategy")
