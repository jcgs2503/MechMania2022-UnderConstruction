from ast import Param
from enum import EnumMeta
from random import Random

from torch import long
from game.game_state import GameState
import game.character_class
import logging
from util.utility import *
from game.item import Item

from game.position import Position
from strategy.strategy import Strategy


class StarterStrategy(Strategy):
    def strategy_initialize(self, my_player_index: int):
        return game.character_class.CharacterClass.KNIGHT

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
        self.center_pieces = [Position(a, b)
                              for a in range(4, 6) for b in range(4, 6)]
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
            possible_moves = [Position(my_x + x, my_y + y) for x in range(-my_range, 1 + my_range)
                              for y in range(-my_range, 1 + my_range) if self.in_range(Position(my_x + x, my_y + y))]
            moves_dist = sorted([(self.dist(p, c), -self.dist(p, my_pos), (p.x, p.y))
                                for p in possible_moves for c in self.center_pieces])
            logging.info(
                f"At {my_x}, {my_y}, going to {moves_dist[0][2][0]}, {moves_dist[0][2][1]}")
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


class HeadHunterKnight(Strategy):

    def dist(self, p1, p2):
        return max(abs(p1.x - p2.x), abs(p1.y - p2.y))

    def in_range(self, pos):
        return 0 <= pos.x < 10 and 0 <= pos.y < 10

    def in_attack_range(self, game_state: GameState, my_player_index: int, pos):
        my_pos = game_state.player_state_list[my_player_index].position
        my_x, my_y = my_pos.x, my_pos.y
        my_range = game_state.player_state_list[my_player_index].stat_set.range
        if abs(pos.x - my_x) <= my_range or abs(pos.y - my_y) <= my_range:
            return True
        return False

    def strategy_initialize(self, my_player_index: int):
        self.center_pieces = [Position(a, b)
                              for a in range(4, 6) for b in range(4, 6)]
        return game.character_class.CharacterClass.KNIGHT

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        return False

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        state = game_state.player_state_list[my_player_index]

        prefered_enemy_list = []
        not_prefered_enemy_list = []
        closest_index = 0
        closest_dis = 100

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

        for i in range(0, 4):
            if i != my_player_index:
                enemy_pos = game_state.player_state_list[i].position
                if game_state.player_state_list[i].character_class != game.character_class.CharacterClass.KNIGHT:
                    prefered_enemy_list.append(i)
                else:
                    not_prefered_enemy_list.append(i)

        if len(prefered_enemy_list) > 0:
            for i in prefered_enemy_list:
                target_pos = game_state.player_state_list[i].position
                if abs(target_pos.x - my_x) + abs(target_pos.y - my_y) - 1 <= closest_dis:
                    closest_dis = abs(target_pos.x - my_x) + \
                        abs(target_pos.y - my_y) - 1
                    closest_index = i

        target_pos = game_state.player_state_list[closest_index].position

        if closest_dis == 2 or closest_dis == 1:
            if target_pos.x > my_x:
                return Position(target_pos.x-1, target_pos.y)
            if target_pos.x == my_x:
                if target_pos.y > my_y:
                    return Position(target_pos.x, target_pos.y-1)
                if target_pos.y < my_y:
                    return Position(target_pos.x, target_pos.y+1)
            if target_pos.x < my_x:
                return Position(target_pos.x+1, target_pos.y)
            # stick to the enemy

        if closest_dis == 0:
            return Position(target_pos.x, target_pos.y)
            # try to chase enemy if they escape

        if len(prefered_enemy_list) > 0:
            if target_pos.x == my_x:
                if target_pos.y > my_y:
                    return Position(my_x, my_y+2)
                if target_pos.y < my_y:
                    return Position(my_x, my_y-2)
            if target_pos.x - my_x == 1:
                if target_pos.y > my_y:
                    return Position(my_x+1, my_y+1)
                if target_pos.y < my_y:
                    return Position(my_x+1, my_y-1)
            if target_pos.x - my_x == -1:
                if target_pos.y > my_y:
                    return Position(my_x-1, my_y+1)
                if target_pos.y < my_y:
                    return Position(my_x-1, my_y-1)
            if target_pos.x - my_x >= 2:
                return Position(my_x+2, my_y)
            if target_pos.x - my_x <= -2:
                return Position(my_x-2, my_y)
            # move toward the enemy

        if my_pos in self.center_pieces:
            return Position(Random().randint(4, 5), Random().randint(4, 5))
        else:
            possible_moves = [Position(my_x + x, my_y + y) for x in range(-my_range, 1 + my_range)
                              for y in range(-my_range, 1 + my_range) if self.in_range(Position(my_x + x, my_y + y))]
            moves_dist = sorted([(self.dist(p, c), -self.dist(p, my_pos), (p.x, p.y))
                                for p in possible_moves for c in self.center_pieces])
            logging.info(
                f"At {my_x}, {my_y}, going to {moves_dist[0][2][0]}, {moves_dist[0][2][1]}")
            return Position(moves_dist[0][2][0], moves_dist[0][2][1])

    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        Prefered_enemy_list = []
        Not_prefered_enemy_list = []
        attackable = False
        for i in range(0, 4):
            if i != my_player_index:
                enemy_pos = game_state.player_state_list[i].position
                if self.in_attack_range(game_state, my_player_index, enemy_pos):
                    attackable = True
                    if game_state.player_state_list[i].character_class != game.character_class.CharacterClass.KNIGHT:
                        Prefered_enemy_list.append(i)
                    else:
                        Not_prefered_enemy_list.append(i)
        if attackable:
            if Prefered_enemy_list:
                return Prefered_enemy_list[0]
            if Not_prefered_enemy_list:
                return Not_prefered_enemy_list[0]

        return Random().randint(0, 3)

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        state = game_state.player_state_list[my_player_index]
        if state.gold >= 8 and state.item == Item.NONE:
            return Item.HUNTER_SCOPE
        return Item.NONE


class Parameters:
    def __init__(self, centerParams):
        self.centerParams = centerParams


class BestStepWizard(Strategy):
    def walk_dist(self, p1, p2):
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    def dist(self, p1, p2):
        return max(abs(p1.x - p2.x), abs(p1.y - p2.y))

    def man_dist(self, p1, p2):
        return abs(p1.x-p2.x) + abs(p1.y-p2.y)

    def attack_dist(self, p1, p2):
        return max(abs(p1.x - p2.x), abs(p1.y - p2.y))

    def in_range(self, pos):
        return 0 <= pos.x < 10 and 0 <= pos.y < 10

    def strategy_initialize(self, my_player_index: int):
        self.parameters = {"kill_params": 1.3, "die_params": 1.8,
                           "center_params": 2.5, "threshold": -5}
        self.center_pieces_tuple = [(a, b)
                                    for a in range(4, 6) for b in range(4, 6)]
        self.center_pieces = [Position(a, b)
                              for a, b in self.center_pieces_tuple]
        return game.character_class.CharacterClass.WIZARD

    def calculate_point(self, game_state: GameState, my_player_index: int, possible_move: Position):
        self.center_point = 0
        speed = game_state.player_state_list[my_player_index].stat_set.speed
        for i in self.center_pieces:
            dist = self.man_dist(possible_move, i)
            if speed > dist:
                self.center_point += self.parameters["center_params"]*(
                    speed-dist)/speed
        self.center_point = self.center_point/4

        for id, player in enumerate(game_state.player_state_list):
            if id == my_player_index:
                continue

            my_range = game_state.player_state_list[my_player_index].stat_set.range
            p_range = player.stat_set.range
            killable = game_state.player_state_list[my_player_index].stat_set.damage > player.health
            killedable = player.stat_set.damage > game_state.player_state_list[
                my_player_index].health
            p_possible_moves = self.get_possible_moves(player)
            kill_sum_point = 0
            killed_sum_point = 0
            for ppm in p_possible_moves:
                if killable:
                    if self.dist(ppm, possible_move) < my_range:
                        kill_sum_point += self.parameters["kill_params"]
                else:
                    if self.dist(ppm, possible_move) < my_range:
                        kill_sum_point += self.parameters["kill_params"] * \
                            game_state.player_state_list[my_player_index].stat_set.damage/player.health

                if killedable:
                    if self.dist(ppm, possible_move) < p_range:
                        killed_sum_point -= self.parameters["die_params"]
                else:
                    if self.dist(ppm, possible_move) < p_range:
                        killed_sum_point -= self.parameters["die_params"] * player.stat_set.damage / \
                            game_state.player_state_list[my_player_index].health

            self.kill_avg_point = kill_sum_point/len(p_possible_moves)
            self.killed_avg_point = killed_sum_point/len(p_possible_moves)

        return self.center_point + self.kill_avg_point + self.killed_avg_point

    def get_possible_moves(self, player_state):
        my_pos = player_state.position
        my_x, my_y = my_pos.x, my_pos.y
        my_range = player_state.stat_set.speed
        return [Position(my_x + x, my_y + y) for x in range(-my_range, 1 + my_range)
                for y in range(-my_range, 1 + my_range) if self.in_range(Position(my_x + x, my_y + y)) and self.walk_dist(Position(0, 0), Position(x, y)) <= my_range]

    def move_action_decision(self, game_state: GameState, my_player_index: int) -> Position:
        my_state = game_state.player_state_list[my_player_index]
        pms = self.get_possible_moves(my_state)
        max_point = self.calculate_point(game_state, my_player_index, pms[0])
        max_position = pms[0]
        for i in pms:
            if self.calculate_point(game_state, my_player_index, i) >= max_point:
                max_point = self.calculate_point(
                    game_state, my_player_index, i)
                max_position = i
        print(max_point)
        if (max_point < self.parameters["threshold"]):
            if my_player_index == 0:
                return Position(0, 0)
            elif my_player_index == 1:
                return Position(9, 0)
            elif my_player_index == 2:
                return Position(9, 9)
            else:
                return Position(0, 9)

        if my_state.gold >= 8 and my_state.item == Item.NONE:  # go back and buy stuff D:
            if my_player_index == 0:
                return Position(0, 0)
            elif my_player_index == 1:
                return Position(9, 0)
            elif my_player_index == 2:
                return Position(9, 9)
            else:
                return Position(0, 9)

        return max_position

    def attack_action_decision(self, game_state: GameState, my_player_index: int) -> int:
        my_state = game_state.player_state_list[my_player_index]
        can_attack = [(player, i) for i, player in enumerate(game_state.player_state_list) if i !=
                      my_player_index and self.attack_dist(my_state.position, player.position) <= my_state.stat_set.range]
        can_kill = [(player, i) for player,
                    i in can_attack if player.health < my_state.stat_set.damage]
        can_kill.sort(key=lambda x: self.attack_dist(
            x[0].position, my_state.position))
        can_attack.sort(key=lambda x: x[0].health)

        if len(can_kill) > 0:
            return can_kill[0][1]
        return can_attack[0][1] if len(can_attack) > 0 else 0

    def buy_action_decision(self, game_state: GameState, my_player_index: int) -> Item:
        state = game_state.player_state_list[my_player_index]
        if state.gold >= 8 and state.item == Item.NONE:
            return Item.HUNTER_SCOPE
        return Item.NONE

    def use_action_decision(self, game_state: GameState, my_player_index: int) -> bool:
        return False
