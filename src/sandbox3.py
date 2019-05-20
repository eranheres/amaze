import os
import struct
import time
from multiprocessing import Pool, Queue, Manager
from amaze.env import Env, TUNNEL_SOFT, TUNNEL_OFF, State
from load_level import env_from_file
from multiprocessing import Process, Lock, Queue as MPQueue
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double, c_uint, c_wchar, c_buffer, c_char
import ctypes
import math


def dfs_job(env, state, best_depth, hashes):
    stack = []
    new_hash = dict()
    stack.append(state)  # push the initial state
    count = 0
    best_state = None
    while len(stack) != 0 and len(stack)<30:
        count += 1
        state = stack.pop()
        for op in env.get_possible_ops(state.pos):
            new_state = env.do_step(state=state, op=op)
            if new_state.depth >= best_depth:
                continue
            new_state_hash = (new_state.pos << env.state_len) | new_state.state # env.state_hash(new_state)
            if (new_state_hash in hashes and hashes[new_state_hash] <= new_state.depth ) or \
               (new_state_hash in new_hash and new_hash[new_state_hash] <= new_state.depth):
                    continue
            new_state.prev_move = op
            new_hash[new_state_hash] = new_state.depth
            if new_state.state == env.goal: #env.goal_reached(new_state):
                best_state = new_state
                best_depth = best_state.depth
                print(f"found ({best_state.depth}):{state.get_history()})")
                continue
            stack.append(new_state)
    return (stack, count, best_depth, best_state, new_hash)

def dfs(env):
    stack = []
    pool = Pool(7)
    manager = Manager()
    hashes = dict()
    best_depth = 200 # manager.Value(int, 200)

    stack.append(env.get_init_state())  # push the initial state
    best_state = None
    results = []
    max_proc = 7
    count = 0
    print_time = time.time()
    start_time = time.time()
    num_proc = 1
    while len(stack) != 0 or len(results) > 0:
        if len(stack)>0 and len(results) < max_proc:
            state = stack.pop()
            results.append(pool.apply_async(func=dfs_job, args=(env, state, best_depth, hashes,)))
        while len(results) > 0: # == num_proc:
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

        if time.time() > print_time + 1:
            print(f"time {time.time()-start_time} | count:{count} | act_proc:{len(results)} | best depth:{best_depth} | hashes:{len(hashes)}")
            print_time = time.time()
            count = 0
    return best_state



level, start_pos, width, height = env_from_file("../data/all/020.xml")
env = Env.from_params(level, width, start_pos, TUNNEL_OFF)
print("Env length:"+str(env.state_len))
solution = dfs(env)
print("The solution ==>"+str(solution.get_history()))
