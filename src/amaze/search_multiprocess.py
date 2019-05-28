from multiprocessing import Manager
from env import State
from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import  Array
from ctypes import Structure, c_uint, c_char
import math
import os
import time


STATE_LEN = 55
HISTORY_LEN = 60
num_proc = os.cpu_count()


class CState(Structure):
    _fields_ = [('pos', c_uint),
                ('state', (c_char * STATE_LEN)),
                ('history', (c_char * HISTORY_LEN)),
                ('move', c_char),
                ('no_change_count', c_uint),
                ('depth', c_uint)]


def ctype_state(state):
    return (state.pos,
            str.encode(hex(state.state)[2:]),    # state.state.to_bytes(STATE_LEN-3, byteorder="little"),
            state.history,
            state.move,
            state.no_change_count,
            state.depth)


def state_from_ctype(ctype_state):
    s = State()
    s.pos = ctype_state.pos
    s.state = int(ctype_state.state.decode(), 16)
    s.history = ctype_state.history
    s.move = ctype_state.move
    s.no_change_count = ctype_state.no_change_count
    s.depth = ctype_state.depth
    return s


def print_state(prefix, state, lock):
    lock.acquire()
    print(f"{prefix} | pos {state.pos} | state {state.state}")
    lock.release()


def print_cstate(prefix, state, lock):
    lock.acquire()
    print(f"{prefix} | pos {state.pos} | state {state.state}")
    lock.release()


def print_tuple_state(prefix, cstate, lock):
    lock.acquire()
    print(f"{prefix} | pos {cstate[0]} | state {cstate[1]}")
    lock.release()

debug = False
print_time = time.time()
def print_lock(lock, string):
    if debug:
        lock.acquire()
        t = "{0:.3f}".format(time.time() - print_time)
        print(f'{t}: {string}')
        lock.release()


class DummyState:
    def __init__(self, history):
        self.history = history

    def get_history(self):
        return self.history


def truncate_hash(hash, level):
    entries_to_remove = []
    for k, l in hash.items():
        if l < level - 1:
            entries_to_remove.append(k)
    for k in entries_to_remove:
        hash.pop(k, None)


def bfs_job(v):
    proc_num, q, env, list, start, size, lock, max_no_change_cnt = v
    new_list = []
    print_lock(lock, f'Process: {proc_num}, start:{start}, size:{size}, starting process')
    for i in range(start, min(len(list), start+size)):
        c_type_state = list[i]
        current_state = int(c_type_state.state.decode(), 16)
        for op in env.get_possible_ops(c_type_state.pos):
            new_pos, val, cost = env.nodes[c_type_state.pos][op]
            new_state = current_state | val
            if new_state > current_state:
                no_change_count = 0
            else:
                no_change_count = c_type_state.no_change_count + cost
                if no_change_count > max_no_change_cnt:
                    continue
            new_list.append((new_pos,
                             str.encode(hex(new_state)[2:]),    # state.state.to_bytes(STATE_LEN-3, byteorder="little"),
                             c_type_state.history + op,
                             op,
                             no_change_count,
                             c_type_state.depth + cost))
    #print_lock(lock, f'Process: {proc_num} pushing data. list {len(new_list)}')
    q.put(new_list)
    #print_lock(lock, f'Process: {proc_num} done')


def bfs_multiproccess(file, env, no_change_cnt, truncate):
    print_time = time.time()
    if math.ceil(env.state_len/8) >= STATE_LEN:
        print(f"Increase state len to {math.ceil(env.state_len/4)}")
        return None
    queues = []
    for i in range(num_proc):
        queues.append(Manager().Queue())

    hashes = dict()
    lis = []
    lock = Lock()
    init_state = env.get_init_state()
    init_state.history = b''
    init_state.move = b'N'
    lis.append(ctype_state(init_state))  # push the initial state

    found_state = None
    count = 0
    max_shared_block = 100000
    best_depth = 200
    while len(lis)>0:
        act_proc = min(max(1,len(lis)), num_proc)
        all_list = lis
        lis = []
        chunk_count = 0
        for pos_in_all_lis in range(0, len(all_list), max_shared_block):

            chunk_size = math.ceil(min(max_shared_block, len(all_list))/num_proc)
            chunk_count += 1
            #print_lock(lock, f"Makeing shared memory at {pos_in_all_lis}-{pos_in_all_lis+max_shared_block} ({chunk_count}/{math.ceil(len(all_list)/max_shared_block)})")
            #    print_tuple_state("copy to shared mem:",x,lock)
            shared_array = Array(CState, all_list[pos_in_all_lis:pos_in_all_lis+max_shared_block], lock=False)
            #print_lock(lock, f"making input for processes. all_size:{len(all_list)} chunk_size:{chunk_size}")
            input = [(i, queues[i], env, shared_array, i*chunk_size, chunk_size, lock, no_change_cnt) for i in list(range(act_proc))]
            #print_lock(lock, f"Starting {len(input)} jobs")
            pool = []
            for i in input:
                proc=Process(target=bfs_job, args=(i,))
                pool.append(proc)
            for p in pool:
                p.start()
            while any(pool):
                proc_loc = -1
                while True:
                    for p in range(len(pool)):
                        if pool[p] and not pool[p].is_alive():
                            proc_loc = p
                    if proc_loc != -1:
                        break
                    time.sleep(0.01)
                pool[proc_loc].join()
                #print_lock(lock, f'Pulling from process {proc_loc}')
                for state in queues[proc_loc].get():
                    if state[5]>best_depth:
                        continue
                    s = int(state[1].decode(), 16)
                    state_hash = (state[0] << env.state_len) + s
                    #if state_hash in hashes and hashes[state_hash] <= state[5]:
                    if hashes.get(state_hash, 200) <= state[5]:
                        continue
                    hashes[state_hash] = state[5]
                    lis.append(state)
                    if s == env.goal:
                        found_state = State()
                        found_state.history = state[2]
                        best_depth = state[5]
                        #print_lock(lock, f'{s} {found_state.history}')
                        #return DummyState(list(found_state.history))
                #print_lock(lock, f'Completed pulling from process {proc_loc}')
                pool[proc_loc].terminate()
                pool[proc_loc] = None
        count += 1
        #print(f'truncating hash {len(hashes)}')
        if truncate:
            truncate_hash(hashes, count)
        t = "{0:.3f}".format(time.time() - print_time)
        print(f'\r{t} :=======> count:{count} tree:{len(lis)} hash:{len(hashes)} found:{"true" if found_state else "false"}', end='')
        #print(f'{t} :=======> count:{count} tree:{len(lis)} hash:{len(hashes)}')

    print("\r", end='')
    if not found_state:
        print(f'"{file} solution not found !!!')
        return None
    else:
        print(f'{file} found solution at level {best_depth}')
    return DummyState([chr(x).encode() for x in found_state.history])
