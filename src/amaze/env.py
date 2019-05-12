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
    def __init__(self, level_rep, start_x, start_y, dimx, dimy):
        self.dims_x = dimx
        self.dims_y = dimy
        self.pos_x = start_x
        self.pos_y = start_y
        self.pos = self.pos_y * self.dims_x + self.pos_x
        self.history = []
        self.level_rep = [*level_rep]
        self.level_rep[self.pos] = COLORED
        self.no_change = 0
        self.prev_move = RIGHT

    def goal_reached(self):
        return EMPTY not in self.level_rep

    def set_state(self, state):
        self.state = state

    def do_step(self, op):
        new_env = Env(self.level_rep, self.pos_x, self.pos_y, self.dims_x, self.dims_y)
        new_env.history = [*self.history]
        new_env.no_change = self.no_change
        if op == LEFT:
            delta = -1
        elif op == RIGHT:
            delta = +1
        elif op == UP:
            delta = -self.dims_x
        else:
            delta = +self.dims_x

        l = len(new_env.level_rep)
        pos = new_env.pos
        new_pos = pos+delta
        change = False
        while (new_env.level_rep[new_pos] != '2') and\
              (new_pos > 0) and  \
              (new_pos < l):
            pos = new_pos
            new_pos = pos + delta
            if new_env.level_rep[pos] == '0':
                new_env.level_rep[pos] = '1'
                change = True
        if change:
            new_env.no_change = 0
        else:
            new_env.no_change += 1
        new_env.pos = pos
        new_env.pos_x = pos % new_env.dims_x
        new_env.pos_y = int(pos / new_env.dims_x)
        new_env.history.append(op)
        return new_env

    def possible_ops(self):
        ops = []
        if (self.pos_x > 0) and (self.level_rep[self.pos - 1] != WALL):
            ops.append(LEFT)
        if (self.pos_x < self.dims_x-1) and (self.level_rep[self.pos + 1] != WALL):
            ops.append(RIGHT)
        if (self.pos_y > 0) and (self.level_rep[self.pos - self.dims_x] != WALL):
            ops.append(UP)
        if (self.pos_y < self.dims_y-1) and (self.level_rep[self.pos + self.dims_x] != WALL):
            ops.append(DOWN)
        #random.shuffle(ops)
        return ops

    def state_hash(self):
        #return int(bin(self.pos)[2:] + "".join(self.level_rep).replace('2', ''), 2)
        return bin(self.pos)[2:] + "".join(self.level_rep)

    def coverage(self):
        zeros = self.level_rep.count(EMPTY)
        ones = self.level_rep.count(WALL)
        return ones / (ones + zeros)
