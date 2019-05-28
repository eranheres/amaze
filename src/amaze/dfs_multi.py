import time
from multiprocessing import Pool, Manager


def dfs_job(env, state, best_depth, hashes):
    stack = []
    new_hash = dict()
    stack.append(state)  # push the initial state
    count = 0
    best_state = None
    while len(stack) != 0 and len(stack)<25:
        state = stack.pop()
        for op in env.get_possible_ops(state.pos):
            count += 1
            new_state_hash, depth = env.eval_hash_step(state, op)
            if depth >= best_depth:
                continue
            if (new_state_hash in new_hash and new_hash[new_state_hash] <= depth) or \
               (new_state_hash in hashes and hashes[new_state_hash] <= depth):
                    continue
            new_state = env.do_step(state=state, op=op)
            new_state.prev_move = op
            new_hash[new_state_hash] = depth
            if new_state.state == env.goal:
                best_state = new_state
                best_depth = best_state.depth
                continue
            stack.append(new_state)
    return stack, count, best_depth, best_state, new_hash


def dfs_multi(env):
    stack = []
    pool = Pool(7)
    hashes = dict()
    start_depth = 200
    best_depth = start_depth

    stack.append(env.get_init_state())  # push the initial state
    best_state = None
    results = []
    max_proc = 7
    count = 0
    print_time = time.time()
    start_time = time.time()
    while (len(stack) != 0 or len(results) > 0) and (time.time()-start_time < 5*59):
        while len(stack)>0 and len(results) < max_proc:
            state = stack.pop()
            results.append(pool.apply_async(func=dfs_job, args=(env, state, best_depth, hashes,)))
        while len(results) > 0: # == num_proc:
            if time.time() > print_time + 1:
                print(f"\rtime {time.time()-start_time} | count:{count} | act_proc:{len(results)} |"
                      f" best depth:{best_depth} | hashes:{len(hashes)} |"
                      f" best {best_depth if best_depth<start_depth else 'NA'}", end='')
                print_time = time.time()
                count = 0
            for i in range(len(results)):
                if results[i].ready():
                    result = results[i].get()
                    stack += result[0]
                    count += result[1]
                    if best_depth > result[2]:
                        best_depth = result[2]
                        best_state = result[3]
                    new_hash = result[4]
                    for key, val in new_hash.items():
                        if key in hashes and hashes[key] <= val:
                            continue
                        hashes[key] = val
                    results.pop(i)
                    break
                time.sleep(0.02)
    return best_state

