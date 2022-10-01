from enum import EnumMeta
from random import Random
from game.game_state import GameState
import game.character_class
import logging
from util.utility import *
from game.item import Item

from game.position import Position
from strategy.strategy import Strategy

class FooFighters(Strategy):

    def walk_dist(self, p1, p2):
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    def attack_dist(self, p1, p2):
        return max(abs(p1.x - p2.x), abs(p1.y - p2.y))

    def in_range(self, pos):
        return 0 <= pos.x < 10 and 0 <= pos.y < 10

    def get_possible_moves(self, player_state):
        my_pos = player_state.position
        my_x, my_y = my_pos.x, my_pos.y
        my_range = player_state.stat_set.speed
        return [Position(my_x + x, my_y + y) for x in range(-my_range, 1 + my_range) \
                              for y in range(-my_range, 1 + my_range) if self.in_range(Position(my_x + x, my_y + y)) and self.walk_dist(Position(0, 0), Position(x, y)) <= my_range]

    def strategy_initialize(self, my_player_index: int):
        self.center_pieces_tuple = [(a, b)
                              for a in range(4, 6) for b in range(4, 6)]
        self.center_pieces = [Position(a, b)
                              for a, b in self.center_pieces_tuple]
        self.safeties_tuple = [(2,3), (3,2), (6,2), (7,3), (2,6), (7,3), (7,6), (6,7)]
        self.safeties = [Position(x, y) for x, y in self.safeties_tuple]
        return game.character_class.CharacterClass.WIZARD

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        state = game_state.player_state_list[my_player_index]
        if state.gold >= 8 and state.item == Item.NONE: # go back and buy stuff D: 
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
        

        my_stats = game_state.player_state_list[my_player_index].character_class
        knight_can_center = False
        for id, player in enumerate(game_state.player_state_list):
            if id == my_player_index:
                continue
            if player.character_class == game.character_class.CharacterClass.KNIGHT and 3 <= player.position.x <= 6 and 3 <= player.position.y <= 6:
                knight_can_center = True

    
        if not knight_can_center and (my_x, my_y) in self.safeties_tuple:
            possible_moves = self.get_possible_moves(state)
            moves_rankings = sorted([(self.walk_dist(cent, mov), (mov.x, mov.y)) for cent in self.center_pieces for mov in possible_moves])
            best = moves_rankings[0]
            if best[0] <= state.stat_set.speed: 
                return Position(best[1][0], best[1][1])

        if knight_can_center and my_pos in self.center_pieces: 
            possible_moves = self.get_possible_moves(state)
            for move in possible_moves:
                if move in self.safeties:
                    return move
            
        if (my_x, my_y) in self.center_pieces_tuple:
            return my_pos 

        possible_moves = self.get_possible_moves(state)

        moves_rankings = sorted([( 2 ** (10) * (self.walk_dist(my_pos, safe)) + self.walk_dist(safe, mov), (safe.x, safe.y)) for safe in self.safeties for mov in possible_moves])
        best = moves_rankings[0]
        return Position(best[1][0], best[1][1]) 

        
    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        my_state = game_state.player_state_list[my_player_index]
        can_attack = [(player, i) for i, player in enumerate(game_state.player_state_list) if i != my_player_index and self.attack_dist(my_state.position, player.position) <= my_state.stat_set.range]
        can_attack.sort(key = lambda x : x[0].health)
        return can_attack[0][1] if len(can_attack) > 0 else 0

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        state = game_state.player_state_list[my_player_index]
        if state.gold >= 8 and state.item == Item.NONE:
            return Item.HUNTER_SCOPE
        return Item.NONE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        return False

