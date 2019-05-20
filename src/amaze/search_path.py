import time
from env import UP, DOWN, LEFT, RIGHT, Env, TUNNEL_OFF
from myqueue import Queue, PriorityQueue, PriorityStack
from multiprocessing import Pool, Manager
from multiprocessing import Queue as Pqueue

def print_status(filename, max_reps, time, progress, hash_size, queue_size, node_cnt, depth, found_path):
    print("\r File %s | Reps: %d | Time: %d | Coverage: %d%% | Hash: %d | Queue: %d | Rate: %d | Depth: %d | Found: %d" %
                     (filename, max_reps, time, progress, hash_size, queue_size, node_cnt, depth, found_path), end='')


def clean_status():
    print("\r", end='')


def bfs_no_tunneling(filename, env):
    # stats
    max_coverage = 0
    nodes_cnt = 0
    start_time = time.time()
    print_time = time.time() - 2

    # state
    queue = Queue()
    hashes = set()
    queue.append(env.get_init_state())  # push the initial state
    while not queue.empty():
        state = queue.pop()
        nodes_cnt = nodes_cnt + 1
        if time.time() > print_time + 1:
            if env.coverage(state)*100 > max_coverage:
                max_coverage = env.coverage(state)*100
            history = state.get_history()
            print_status(filename, -1, int(time.time() - start_time), max_coverage, len(hashes),
                         queue.items, nodes_cnt, len(history), 0)
            print_time = time.time()
            nodes_cnt = 0
        possible_moves = env.nodes[state.pos].keys()
        #possible_moves_len = len(possible_moves)
        for op in possible_moves:
            #if (possible_moves_len == 2) and Env.is_opposite_move(op, state.move):
            #    continue
            new_state = env.do_step(op=op, state=state)
            new_state_hash = env.state_hash(new_state)
            if new_state_hash in hashes:
                continue
            if env.goal_reached(new_state):
                clean_status()
                return new_state
            hashes.add(new_state_hash)
            queue.append(new_state)
    clean_status()
    return None


def bfs_tunneling(filename, env):
    queue = PriorityQueue()
    hashes = set()
    queue.append(env.get_init_state())  # push the initial state
    max_coverage = 0
    nodes_cnt = 0
    start_time = time.time()
    print_time = time.time() - 2
    best_state = None
    while not queue.empty():
        state = queue.pop()
        nodes_cnt = nodes_cnt + 1
        if time.time() > print_time + 1:
            if env.coverage(state)*100 > max_coverage:
                max_coverage = env.coverage(state)*100
            history = state.get_history()
            print_status(filename, -1, int(time.time() - start_time), max_coverage, len(hashes), len(queue.items),
                         nodes_cnt, len(history), 0 if not best_state else best_state.depth)
            print_time = time.time()
            nodes_cnt = 0
        possible_moves = env.nodes[state.pos]
        for op in possible_moves:
            new_state = env.do_step(op=op, state=state)
            #if (state.prev_state and state.prev_state.pos == new_state.pos) and new_state.pos != env.init_pos:
            #    continue
            new_state_hash = env.state_hash(new_state)
            if new_state_hash in hashes:
                continue
            if env.goal_reached(new_state):
                if (best_state is None) or (best_state.depth > new_state.depth):
                    best_state = new_state
                clean_status()
                continue
            if best_state and best_state.depth < new_state.depth:
                continue
            hashes.add(new_state_hash)
            queue.append(new_state)
    clean_status()
    return best_state


def dfs(filname, env):
    best_state = None
    for max_reps in reversed(range(1)):
        solution = dfs_limited(5*60, best_state.depth if best_state else 100, filname, env)
        if solution is None:
            break
        if best_state is None or solution.depth <= best_state.depth:
            best_state = solution
    return best_state


def dfs_limited(max_time, max_depth, filename, env):
    stack = []
    hashes = dict()

    state = env.get_init_state()
    stack.append(state)  # push the initial state
    max_coverage = 0
    nodes_cnt = 0
    start_time = time.time()
    print_time = time.time() - 2
    best_state = None
    best_state_depth = 100
    while len(stack) != 0:
        state = stack.pop()
        if state.depth >= best_state_depth:
            continue
        nodes_cnt = nodes_cnt + 1
        if nodes_cnt>10000 and time.time() > print_time + 1:
            if env.coverage(state)*100 > max_coverage:
                max_coverage = env.coverage(state)*100
            print_status(filename, -1, (time.time() - start_time), max_coverage, len(hashes), len(stack),
                         nodes_cnt, state.depth, 0)
            print_time = time.time()
            nodes_cnt = 0
            #if int(time.time() - start_time) > max_time:
            #    return best_state
        priorities = []
        for op in env.get_possible_ops(state.pos):
            new_state = env.do_step(state=state, op=op)
            if new_state.depth >= best_state_depth:
                continue
            new_state_hash = (new_state.pos << env.state_len) | new_state.state # env.state_hash(new_state)
            if new_state_hash in hashes:
                if hashes[new_state_hash] < new_state.depth:
                    continue
            new_state.prev_move = op
            hashes[env.state_hash(state)] = new_state.depth
            if new_state.state == env.goal: #env.goal_reached(new_state):
                best_state = new_state
                best_state_depth = best_state.depth
                print(f"found ({best_state.depth}):{state.get_history()})")
                continue
            stack.append(new_state)
            #if state.prev_state and new_state.pos != state.prev_state.pos:
            #    priorities.append(new_state)
            #else:
            #    priorities.insert(0, new_state)
        #stack.extend(priorities)
    clean_status()
    return best_state






def get_island_length(env, op):
    stack = []
    hash = set()
    start_pos = env.pos
    start_move = op
    first_step = env.do_step(op)
    stack.append(first_step)
    hash.add((first_step.pos_x, first_step.pos_y))
    while not len(stack) == 0:
        env = stack.pop()
        for op in env.possible_ops():
            new_env = env.do_step(op)
            new_pos = new_env.pos
            if new_pos == start_pos and not Env.is_opposite_move(start_move, op):
                return -1
            if new_pos == start_pos:
                continue
            if (new_env.pos_x, new_env.pos_y) in hash:
                continue
            stack.append(new_env)
            hash.add((new_env.pos_x, new_env.pos_y))
    return len(hash)


def dfs_islands(filename, env):
    for max_reps in range(100, 100):
        stack = []
        hashes = set()

        stack.append(env)  # push the initial state
        max_coverage = 0
        nodes_cnt = 0
        start_time = time.time()
        print_time = time.time() - 2
        while len(stack) != 0:
            env = stack.pop()
            nodes_cnt = nodes_cnt + 1
            #if time.time() > print_time + 1:
            #    if env.coverage()*100 > max_coverage:
            #        max_coverage = env.coverage()*100
            #    print_status(filename, max_reps, (time.time() - start_time), max_coverage, len(hashes), len(stack), nodes_cnt, len(env.history))
            #    print_time = time.time()
            #    nodes_cnt = 0
                #if (int(time.time() - start_time) > 100):
                #    return None
            for op in env.possible_ops():
                new_env = env.do_step(op)
                if new_env.no_change > max_reps:
                    continue
                new_state_hash = new_env.state_hash()
                if new_state_hash in hashes:
                    continue
                if new_env.goal_reached():
                    clean_status()
                    return new_env
                hashes.add(new_state_hash)
                stack.append(new_env)
    clean_status()
    return None

