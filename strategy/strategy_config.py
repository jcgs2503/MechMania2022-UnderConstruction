from strategy.starter_strategy import StarterStrategy, StupidKnight, HeadHunterKnight
from strategy.foo_fighters import FooFighters

from strategy.strategy import Strategy

"""Return the strategy that your bot should use.

:param playerIndex: A player index that can be used if necessary.

:returns: A Strategy object.
"""


def get_strategy(player_index: int) -> Strategy:
    return FooFighters()

