
EMPTY = '0'
COLORED = '1'
WALL = '2'


RIGHT = 'R'
LEFT = 'L'
UP = 'U'
DOWN = 'D'

TUNNEL_OFF = 0
TUNNEL_SOFT = 1
TUNNEL_DEEP = 2

class State:
    #def __init__(self):
        #self.pos = 0
        #self.state = 0
        #self.prev_move = 'N'
        #self.no_change_count = 0

    def get_history(self):
        state = self
        history = []
        while state is not None:
            if state.move == 'N':
                break
            history.insert(0, state.move)
            state = state.prev_state
        return history

    def to_str(self):
        return f'{self.pos},{self.state},{self.prev_move},{self.no_change_count}'

    def from_str(self, str):
        vals = str.split(',')
        self.pos = int(vals[0])
        self.state = int(vals[1])
        self.prev_move = vals[2]
        self.no_change_count = vals[3]



class Env:
    def __init__(self):
        self.goal = 0
        self.nodes = {}
        self.state_len = 0
        self.tunneling = False
        self.level_rep = []
        self.dim_x = 0
        self.init_pos = 0

    @classmethod
    def from_params(cls, level_rep, dim_x, pos, tunneling=TUNNEL_OFF):
        env = cls()
        env.init_pos = pos
        env.goal = int("".join(level_rep).replace(WALL, '').replace(EMPTY, COLORED), 2)
        env.nodes = {}
        env.level_rep = level_rep
        env.dim_x = dim_x
        env.state_len = level_rep.count(EMPTY) + level_rep.count(COLORED)
        env.tunneling = tunneling
        env.prepare_nodes(pos=pos)
        return env

    def get_init_state(self):
        state = State()
        state.state = int("".join(self.level_rep).replace(WALL, ''), 2)
        state.pos = self.init_pos
        state.prev_state = None
        state.move = 'N'
        state.no_change_count = 0
        state.depth = 0
        return state

    def prepare_nodes_do_step(self, start_pos, op):
        lvl = [*self.level_rep]
        pos = start_pos
        cost = 0
        dead_end = 0
        while True:
            delta = {
                LEFT: -1,
                RIGHT: +1,
                UP: -self.dim_x,
                DOWN: +self.dim_x
            }[op]
            cost += 1
            while True:
                lvl[pos] = COLORED
                pos += delta
                if pos >= len(lvl):
                    break
                if (lvl[pos] == WALL) or (pos < 0) or (pos >= len(lvl)):
                    pos -= delta
                    break
            if pos == start_pos or (pos in self.nodes):
                break
            if not self.tunneling == TUNNEL_DEEP:
                break
            possible_ops = self.calc_possible_ops(pos)
            if len(possible_ops) == 2:
                if Env.is_opposite_move(possible_ops[0], op):
                    op = possible_ops[1]
                else:
                    op = possible_ops[0]
            elif len(possible_ops) == 1:
                op = possible_ops[0]
                dead_end += 1
                if dead_end > 1:
                    break
            else:
                break
        bitwise = int("".join(lvl).replace(WALL, ''), 2)
        return pos, bitwise, cost

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

    def prepare_nodes(self, pos):
        stack = [pos]
        while not len(stack) == 0:
            pos = stack.pop()
            possible_ops = self.calc_possible_ops(pos)
            for op in possible_ops:
                new_pos, val, cost = self.prepare_nodes_do_step(start_pos=pos, op=op)
                if pos not in self.nodes:
                    self.nodes[pos] = {}
                self.nodes[pos][op] = (new_pos, val, cost)
                if new_pos in self.nodes:
                    continue
                stack.append(new_pos)
        self.set_tunnels()

    def goal_reached(self, state):
        return state.state == self.goal

    def do_step(self, state, op):
        #new_state = State.make_copy(state)

        new_state = State()
        new_state.prev_state = state

        new_pos, val, cost = self.nodes[state.pos][op]
        new_state.depth = state.depth + cost
        new_state.state = state.state | val
        new_state.pos = new_pos
        new_state.move = op
        if new_state.state > state.state:
            new_state.no_change_count = 0
        else:
            new_state.no_change_count = state.no_change_count + cost
        return new_state

    def get_possible_ops(self, pos):
        return self.nodes[pos].keys()

    def calc_possible_ops(self, pos):
        ops = []
        pos_y = int(pos / self.dim_x)
        pos_x = pos % self.dim_x
        dim_y = len(self.level_rep) / self.dim_x
        if (pos_x > 0) and (self.level_rep[pos - 1] != WALL):
            ops.append(LEFT)
        if (pos_x < self.dim_x-1) and (self.level_rep[pos + 1] != WALL):
            ops.append(RIGHT)
        if (pos_y > 0) and (self.level_rep[pos - self.dim_x] != WALL):
            ops.append(UP)
        if (pos_y < dim_y-1) and (self.level_rep[pos + self.dim_x] != WALL):
            ops.append(DOWN)
        return ops

    def state_hash(self, state):
        return (state.pos << self.state_len) | state.state

    def coverage(self, state):
        return float(bin(state.state)[2:].count('1'))/self.state_len

    def get_printable_solution(self,  solution):
        ret = []
        lvl = [*self.level_rep]
        lvl[self.init_pos] = 1
        pos = self.init_pos
        for op in solution:
            start_pos = pos
            while True:
                ret.append(op)
                delta = {
                    LEFT: -1,
                    RIGHT: +1,
                    UP: -self.dim_x,
                    DOWN: +self.dim_x
                }[op]
                while True:
                    lvl[pos] = COLORED
                    if lvl.count(EMPTY) == 0:
                        break
                    pos += delta
                    if (lvl[pos] == WALL) or (pos < 0) or (pos >= len(lvl)):
                        pos -= delta
                        break
                if pos == start_pos or (pos in self.nodes):
                    break
                if lvl.count(EMPTY) == 0:
                    break
                if self.tunneling == TUNNEL_OFF:
                    break
                if pos == start_pos:
                    break
                possible_ops = self.calc_possible_ops(pos)
                if len(possible_ops) == 2:
                    if Env.is_opposite_move(possible_ops[0], op):
                        op = possible_ops[1]
                    else:
                        op = possible_ops[0]
                elif len(possible_ops) == 1:
                    op = possible_ops[0]
                else:
                    break
        if lvl.count(EMPTY) > 0:
            print("Solution not valid")
            return "Solution not valid"

        return ",".join(ret).replace(RIGHT, '1').replace(LEFT, '2').replace(UP, '3').replace(DOWN, '4')

    def count_nodes(self):
        return len(self.nodes)

    def is_connected_directly(self, from_node_index, to_node_index):
        node = self.nodes[from_node_index]
        for edge_index in node:
            if node[edge_index][0] == to_node_index:
                return True
        return False

    def is_bi_dir_directly(self, node1_index, node2_index):
        return self.is_connected_directly(node1_index, node2_index) and \
               self.is_connected_directly(node2_index, node1_index)

    def get_edge(self, from_node_index, to_node_index):
        from_node = self.nodes[from_node_index]
        for index, node in from_node.items():
            if node[0] == to_node_index:
                return node
        return None

    def cross_paths_exists(self, node1_index, node2_index):
        val = 0
        # mask of all other edges
        for node_index, node in self.nodes.items():
            if node_index in [node1_index, node2_index]:
                continue
            for edge_index, edge in node.items():
                if node[edge_index][0] not in [node1_index, node2_index]:
                    val |= node[edge_index][1]
        v1 = self.get_edge(node1_index, node2_index)[1]
        v2 = self.get_edge(node2_index, node1_index)[1]
        common =  val & (v1 | v2)
        if common != 0:
            return True
        else:
            return False

    def is_tunnel(self, target_node_index):
        target_node = self.nodes[target_node_index]
        if len(target_node) != 2 or target_node_index == self.init_pos:
            return False
        # check that all children are connected directly
        for target_edge in target_node:
            source_node_index = target_node[target_edge][0]
            if not self.is_bi_dir_directly(target_node_index, source_node_index):
                return False
        # check that there are no other connections to this target node
        count = 0
        n1 = None
        n2 = None
        for source_node_index in self.nodes:
            if self.is_connected_directly(source_node_index, target_node_index):
                if n1 is None:
                    n1 = source_node_index
                else:
                    n2 = source_node_index
                count += 1
            if count > 2:
                return False
        # check that the found nodes dont have other paths crossed
        if self.cross_paths_exists(n1, target_node_index):
            return False
        if self.cross_paths_exists(n2, target_node_index):
            return False
        return True

    def merge_tunnel(self, tunnel_index):
        target_node = self.nodes[tunnel_index]
        val = 0
        weight = 0
        # calculate value
        for edge_key in target_node:
            node = target_node[edge_key]
            val |= node[1]
            weight += node[2]

        # find all nodes that are pointing to this target
        for source_key, source in self.nodes.items():
            if source_key == tunnel_index:
                continue
            # search node pointing to our target
            for edge_key, edge in source.items():
                if edge[0] == tunnel_index:
                    # search node pointing out from the target not to the source
                    for target_edge_key, target_edge in target_node.items():
                        if target_edge[0] == source_key:
                            continue
                        source[edge_key] = (target_edge[0], edge[1]|target_edge[1], edge[2]+target_edge[2])

        self.nodes.pop(tunnel_index)

    def set_tunnels(self):
        if self.tunneling in [TUNNEL_OFF, TUNNEL_DEEP]:
            return
        indices = list(self.nodes.keys())
        tunnels = []
        for target_node_index in indices:
            if not self.is_tunnel(target_node_index):
                continue
            tunnels.append(target_node_index)
        for target_node_index in tunnels:
            if len(self.nodes) <= 2:
                break
            self.merge_tunnel(target_node_index)
            #print("found node:"+str(target_node_index))
