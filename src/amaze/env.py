from state import State
from enum import Enum
import copy
import random

EMPTY = '0'
COLORED = '1'
WALL = '2'


RIGHT = 'R'
LEFT = 'L'
UP = 'U'
DOWN = 'D'


class Env:
    def __init__(self):
        self.state = 0
        self.pos = 0
        self.history = []
        self.goal = 0
        self.nodes = {}
        self.prev_move = 'N'
        self.state_len = 0
        self.no_change_count = 0

    @classmethod
    def from_params(cls, level_rep, start_x, start_y, dim_x):
        env = cls()
        env.pos = start_y * dim_x + start_x
        env.history = []
        env.goal = int("".join(level_rep).replace(WALL, '').replace(EMPTY, COLORED), 2)
        env.nodes = {}
        env.state = int("".join(level_rep).replace(WALL, ''), 2)
        env.prev_move = 'N'
        env.no_change_count = 0
        env.state_len = level_rep.count(EMPTY) + level_rep.count(COLORED)
        env.prepare_nodes(level_rep, dim_x, env.pos)
        return env

    @classmethod
    def make_copy(cls, env):
        new_env = cls()
        new_env.history = [*env.history]
        new_env.state = env.state
        new_env.prev_move = env.prev_move
        new_env.no_change_count = env.no_change_count
        new_env.pos = env.pos
        new_env.goal = env.goal
        new_env.nodes = env.nodes
        new_env.state_len = env.state_len
        return new_env

    @staticmethod
    def prepare_nodes_do_step(level_rep, dims_x, start_pos, op):
        lvl = [*level_rep]
        pos = start_pos
        while True:
            delta = {
                LEFT: -1,
                RIGHT: +1,
                UP: -dims_x,
                DOWN: +dims_x
            }[op]
            while True:
                lvl[pos] = COLORED
                pos += delta
                if pos >= len(lvl):
                    break
                if (lvl[pos] == WALL) or (pos < 0) or (pos >= len(lvl)):
                    pos -= delta
                    break
            if pos == start_pos:
                break
            possible_ops = Env.possible_ops(lvl, dims_x, pos)
            if len(possible_ops) == 2:
                if Env.is_opposite_move(possible_ops[0], op):
                    op = possible_ops[1]
                else:
                    op = possible_ops[0]
            else:
                break
        bitwise = int("".join(lvl).replace(WALL, ''), 2)
        return pos, bitwise

    @staticmethod
    def is_opposite_move(op1, op2):
        if op1 == UP:
            return op2 == DOWN
        if op1 == DOWN:
            return op2 == UP
        if op1 == LEFT:
            return op2 == RIGHT
        if op1 == RIGHT:
            return op2 == LEFT

    def prepare_nodes(self, level_rep, dims_x, pos):
        stack = [pos]
        while not len(stack) == 0:
            pos = stack.pop()
            possible_ops = self.possible_ops(level_rep, dims_x, pos)
            for op in possible_ops:
                new_pos, val = self.prepare_nodes_do_step(level_rep, dims_x, pos, op)
                if pos not in self.nodes:
                    self.nodes[pos] = {}
                self.nodes[pos][op] = (new_pos, val)
                if new_pos in self.nodes:
                    continue
                stack.append(new_pos)

    def goal_reached(self):
        return self.state == self.goal

    def do_step(self, op):
        new_env = Env.make_copy(self)
        new_pos, val = self.nodes[self.pos][op]
        new_env.state = self.state | val
        new_env.pos = new_pos
        new_env.history.append(op)
        if new_env.state > self.state:
            new_env.no_change_count = 0
        else:
            new_env.no_change_count += 1
        return new_env

    @staticmethod
    def possible_ops(level_rep, dim_x, pos):
        ops = []
        pos_y = int(pos / dim_x)
        pos_x = pos % dim_x
        dim_y = len(level_rep)/ dim_x
        if (pos_x > 0) and (level_rep[pos - 1] != WALL):
            ops.append(LEFT)
        if (pos_x < dim_x-1) and (level_rep[pos + 1] != WALL):
            ops.append(RIGHT)
        if (pos_y > 0) and (level_rep[pos - dim_x] != WALL):
            ops.append(UP)
        if (pos_y < dim_y-1) and (level_rep[pos + dim_x] != WALL):
            ops.append(DOWN)
        return ops

    def state_hash(self):
        return (self.pos << self.state_len) | self.state

    def coverage(self):
        return float(bin(self.state)[2:].count('1'))/self.state_len
