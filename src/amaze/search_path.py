import time
from env import UP, DOWN, LEFT, RIGHT, Env
from myqueue import Queue


def print_status(filename, max_reps, time, progress, hash_size, queue_size, node_cnt, depth):
    print("\r File %s | Reps: %d | Time: %d | Coverage: %d%% | Hash: %d | Queue: %d | Rate: %d | Depth: %d " %
                     (filename, max_reps, time, progress, hash_size, queue_size, node_cnt, depth), end='')


def clean_status():
    print("\r", end='')


def bfs(filename, env):
    queue = Queue()
    hashes = set()

    queue.append(env)  # push the initial state
    max_coverage = 0
    nodes_cnt = 0
    start_time = time.time()
    print_time = time.time() - 2
    while not queue.empty():
        env = queue.pop()
        nodes_cnt = nodes_cnt + 1
        if time.time() > print_time + 1:
            if env.coverage()*100 > max_coverage:
                max_coverage = env.coverage()*100
            print_status(filename, -1, int(time.time() - start_time), max_coverage, len(hashes), queue.items, nodes_cnt, len(env.history))
            print_time = time.time()
            nodes_cnt = 0
            #if (int(time.time() - start_time) > 100):
            #    return None
        possible_moves = env.possible_ops()
        possible_moves_len = len(possible_moves)
        for op in possible_moves:
            if possible_moves_len == 2 and is_opposite_move(op, env.prev_move):
                continue
            new_env = env.do_step(op)
            new_env.prev_move = op
            new_state_hash = new_env.state_hash_slow()

            if new_state_hash in hashes:
                continue
            if new_env.goal_reached():
                clean_status()
                return new_env
            hashes.add(new_state_hash)
            queue.append(new_env)
    clean_status()
    return None


def dfs(filname, env):
    best_env = None
    for max_reps in reversed(range(1, 20)):
        solution = dfs_limited(5*60, max_reps, filname, env)
        if solution is None:
            break
        if best_env is None or len(solution.history)<=len(best_env.history):
            best_env = solution
    return best_env


def dfs_limited(max_time, max_reps, filename, env):
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
        if time.time() > print_time + 1:
            if env.coverage()*100 > max_coverage:
                max_coverage = env.coverage()*100
            print_status(filename, max_reps, (time.time() - start_time), max_coverage, len(hashes), len(stack), nodes_cnt, len(env.history))
            print_time = time.time()
            nodes_cnt = 0
            if int(time.time() - start_time) > max_time:
                return
        priorities = []
        for op in env.possible_ops():
            new_env = env.do_step(op)
            new_env.prev_move = op
            if new_env.no_change > max_reps:
                continue
            new_state_hash = new_env.state_hash_fast()
            if new_state_hash in hashes:
                continue
            if new_env.goal_reached():
                clean_status()
                return new_env
            hashes.add(new_state_hash)
            priorities.append(new_env)
        priorities.sort(key=lambda x: x.no_change)
        for penv in priorities:
            if is_opposite_move(penv.prev_move, env.prev_move):
                stack.append(penv)
        for penv in priorities:
            if not is_opposite_move(penv.prev_move, env.prev_move):
                stack.append(penv)
    clean_status()


def count_nodes(env):
    stack = []
    hash = set()
    stack.append(env)
    hash.add(env.pos)
    count_tunnels = 0
    while not len(stack) == 0:
        env = stack.pop()
        possible_ops = env.possible_ops()
        if len(possible_ops) == 2:
            count_tunnels += 1
        for op in env.possible_ops():
            new_env = env.do_step(op)
            new_pos = new_env.pos
            if new_pos in hash:
                continue
            stack.append(new_env)
            hash.add(new_env.pos)
    return len(hash) - count_tunnels


def is_opposite_move(op1, op2):
    if op1 == UP:
        return op2 == DOWN
    if op1 == DOWN:
        return op2 == UP
    if op1 == LEFT:
        return op2 == RIGHT
    if op1 == RIGHT:
        return op2 == LEFT


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
            if new_pos == start_pos and not is_opposite_move(start_move, op):
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
            if time.time() > print_time + 1:
                if env.coverage()*100 > max_coverage:
                    max_coverage = env.coverage()*100
                print_status(filename, max_reps, (time.time() - start_time), max_coverage, len(hashes), len(stack), nodes_cnt, len(env.history))
                print_time = time.time()
                nodes_cnt = 0
                #if (int(time.time() - start_time) > 100):
                #    return None
            for op in env.possible_ops():
                env.get
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

