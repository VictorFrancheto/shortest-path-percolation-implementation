"""Source/target node-selection criteria (``spp-dynamic.ipynb``, "Nodes Selection Strategies").

Five base modes -- ``random``, ``hub``, ``closeness``, ``betweenness``,
``domirank`` -- combined pairwise into a ``"<source_mode>-<target_mode>"``
``selection_strategy`` string. Nothing here is invented: every function is a
direct port of the corresponding notebook cell.
"""

from .strategies import NODE_SELECTION_MODES, SELECTION_STRATEGIES, resolve_selection_strategy
from .picking import MODE_HUB, MODE_RANDOM, choose_source_target, select_node

__all__ = [
    "NODE_SELECTION_MODES",
    "SELECTION_STRATEGIES",
    "resolve_selection_strategy",
    "MODE_HUB",
    "MODE_RANDOM",
    "choose_source_target",
    "select_node",
]
