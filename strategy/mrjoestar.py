from enum import EnumMeta
from random import Random
from random import shuffle
from shutil import move
from game.character_class import CharacterClass
from game.game_state import GameState
import game.character_class
import logging
from util.utility import *
from game.item import Item

from game.position import Position
from strategy.strategy import Strategy

class MrJoestar(Strategy):

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
        return game.character_class.CharacterClass.ARCHER

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:


        state = game_state.player_state_list[my_player_index]
        

        my_pos = game_state.player_state_list[my_player_index].position
        my_x, my_y = my_pos.x, my_pos.y

        archer_count = len([pl for i, pl in enumerate(game_state.player_state_list) if i != my_player_index and pl.character_class == CharacterClass.ARCHER])
        if archer_count == 3 and (0 == my_x or 0 == my_y or 9 == my_x or 9 == my_y) and state.character_class == CharacterClass.ARCHER and state.gold >= 10:
            return my_pos

        
    
        my_stats = game_state.player_state_list[my_player_index].character_class
        knight_can_center = False

        possible_moves = self.get_possible_moves(state)

        if (my_x, my_y) in self.center_pieces_tuple:
            return my_pos 
  
        possible_moves = self.get_possible_moves(state)
        moves_rankings = [(2 ** (10 + self.walk_dist(cent, my_pos)) + self.walk_dist(cent, mov), (mov.x, mov.y)) \
            for cent in self.center_pieces for mov in possible_moves \
            if 1 <= mov.x <= 8 and 1 <= mov.y <= 8]
        shuffle(moves_rankings)
        moves_rankings.sort(key = lambda x : x[0])
        best = moves_rankings[0]
        return Position(best[1][0], best[1][1]) 

        
    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        my_state = game_state.player_state_list[my_player_index]
        can_attack = [(player, i) for i, player in enumerate(game_state.player_state_list) if i != my_player_index and self.attack_dist(my_state.position, player.position) <= my_state.stat_set.range]
        shuffle(can_attack)
        can_attack.sort(key = lambda x : x[0].health)
        return can_attack[0][1] if len(can_attack) > 0 else 0

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        state = game_state.player_state_list[my_player_index]
        archer_count = len([pl for i, pl in enumerate(game_state.player_state_list) if i != my_player_index and pl.character_class == CharacterClass.ARCHER])
        my_pos = game_state.player_state_list[my_player_index].position
        my_x, my_y = my_pos.x, my_pos.y
        
        if archer_count == 3 and (0 == my_x or 0 == my_y or 9 == my_x or 9 == my_y) and state.character_class == CharacterClass.ARCHER and state.gold >= 10:
            return Item.MAGIC_STAFF
        
        
        
        if state.gold >= 5 and state.item == Item.NONE:
            return Item.STRENGTH_POTION
        return Item.NONE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        state = game_state.player_state_list[my_player_index]
        return state.item == Item.MAGIC_STAFF

