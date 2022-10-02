from strategy.starter_strategy import StarterStrategy, StupidKnight, HeadHunterKnight, BestStepWizard
from strategy.foo_fighters import FooFighters

from strategy.strategy import Strategy

"""Return the strategy that your bot should use.

:param playerIndex: A player index that can be used if necessary.

:returns: A Strategy object.
"""


def get_strategy(player_index: int) -> Strategy:
    if player_index == 0:
        return BestStepWizard()
    return FooFighters()
