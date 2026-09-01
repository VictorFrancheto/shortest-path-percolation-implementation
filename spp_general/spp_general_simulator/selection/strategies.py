"""``selection_strategy`` -> ``(attack_mode_1, attack_mode_2)`` (notebook cell 25).

All the logic that translates the ``selection_strategy`` string into attack
modes lives here plus ``choose_source_target`` (in ``picking.py``) -- the only
piece that changes when switching ``selection_strategy``.
"""

NODE_SELECTION_MODES = ("random", "hub", "closeness", "betweenness", "domirank")

#: All 5x5 = 25 valid "source-target" combinations of `selection_strategy`.
SELECTION_STRATEGIES = {
    f"{mode_1}-{mode_2}": {"attack_mode_1": mode_1, "attack_mode_2": mode_2}
    for mode_1 in NODE_SELECTION_MODES
    for mode_2 in NODE_SELECTION_MODES
}


def resolve_selection_strategy(strategy_name: str):
    """Validate ``strategy_name`` and return ``(attack_mode_1, attack_mode_2)``.

    Raises
    ------
    ValueError
        If ``strategy_name`` is not one of the known "<mode_1>-<mode_2>" combinations.
    """
    if strategy_name not in SELECTION_STRATEGIES:
        available = ", ".join(sorted(SELECTION_STRATEGIES))
        raise ValueError(f"Unknown selection_strategy={strategy_name!r}. Available options: {available}")
    cfg = SELECTION_STRATEGIES[strategy_name]
    return cfg["attack_mode_1"], cfg["attack_mode_2"]
