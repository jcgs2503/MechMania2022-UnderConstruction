from random import Random
from game.game_state import GameState
import game.character_class
import logging
from util.utility import *
from game.item import Item

from game.position import Position
from strategy.strategy import Strategy
class StarterStrategy(Strategy):
    def strategy_initialize(self, my_player_index: int):
        return game.character_class.CharacterClass.WIZARD

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        return game_state.player_state_list[my_player_index].position

    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        return Random().randint(0, 3)

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        return Item.NONE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        return False
class StupidKnight(Strategy):

    def dist(self, p1, p2):
        return max(abs(p1.x - p2.x), abs(p1.y - p2.y))

    def in_range(self, pos):
        return 0 <= pos.x < 10 and 0 <= pos.y < 10

    

    def strategy_initialize(self, my_player_index: int):
        self.center_pieces = [Position(a, b) for a in range(4, 6) for b in range(4, 6)]
        return game.character_class.CharacterClass.KNIGHT

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        state = game_state.player_state_list[my_player_index]
        if state.gold >= 8 and state.item == Item.NONE:
            if my_player_index == 0:
                return Position(0, 0)
            elif my_player_index == 1:
                return Position(9, 0)
            elif my_player_index == 2:
                return Position(9, 9)
            else:
                return Position(0, 9)
        my_pos = game_state.player_state_list[my_player_index].position
        my_x, my_y = my_pos.x, my_pos.y
        my_range = game_state.player_state_list[my_player_index].stat_set.range

        my_stats = game_state.player_state_list[my_player_index].character_class
        if my_pos in self.center_pieces:
            return Position(Random().randint(4, 5), Random().randint(4, 5))
        else: 
            possible_moves = [Position(my_x + x, my_y + y) for x in range(-my_range, 1 + my_range) for y in range(-my_range, 1 + my_range) if self.in_range(Position(my_x + x, my_y + y))]
            moves_dist = sorted([(self.dist(p, c), -self.dist(p, my_pos), (p.x, p.y)) for p in possible_moves for c in self.center_pieces])
            logging.info(f"At {my_x}, {my_y}, going to {moves_dist[0][2][0]}, {moves_dist[0][2][1]}")
            return Position(moves_dist[0][2][0], moves_dist[0][2][1])



    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        return Random().randint(0, 3)

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        state = game_state.player_state_list[my_player_index]
        if state.gold >= 8 and state.item == Item.NONE:
            return Item.PROCRUSTEAN_IRON
        return Item.NONE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        return False