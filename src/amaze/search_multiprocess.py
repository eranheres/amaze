from multiprocessing import Pool, Queue, Manager
from amaze.env import Env, TUNNEL_SOFT, TUNNEL_OFF, State
from amaze.validate_solution import validate_solution
from load_level import env_from_file
from multiprocessing import Process, Lock, Queue as MPQueue
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double, c_uint, c_int, c_wchar, c_buffer, c_byte, c_char
import math
import os



STATE_LEN = 55
HISTORY_LEN = 200
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
            #state.state.to_bytes(STATE_LEN-3, byteorder="little"),
            str.encode(hex(state.state)[2:]),    # state.state.to_bytes(STATE_LEN-3, byteorder="little"),
            "NA".encode('utf-8') if len(state.history)>HISTORY_LEN-2 else state.history.encode('utf-8'),
            str.encode(state.move),
            state.no_change_count,
            state.depth)

def state_from_ctype(ctype_state):
    s = State()
    s.pos = ctype_state.pos
    #s.state = int.from_bytes(ctype_state.state, byteorder="little")
    s.state = int(ctype_state.state.decode(), 16)
    s.history = ctype_state.history.decode('utf-8')
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
def print_lock(lock, string):
    if debug:
        lock.acquire()
        print(string)
        lock.release()

class DummyState:
    def __init__(self, history):
        self.history = history

    def get_history(self):
        return self.history

def bfs_job(v):
    proc_num, q, env, list, start, size, lock = v
    new_list = []
    print_lock(lock, f'Process: {proc_num}, start:{start}, size:{size}, starting process')
    found_state = None
    for i in range(start, min(len(list), start+size)):
        c_type_state = list[i]
        #print_cstate("job cstate",c_type_state,lock)
        state = state_from_ctype(c_type_state)
        #print_state("job state ",state,lock)
        if env.state_hash(state) == 16397606763625458197655520905476582158387:
            print_lock(lock, f'found in process 16397606763625458197655520905476582158387')
        for op in env.get_possible_ops(state.pos):
            new_state = env.do_step(state, op)
            #print_state("job new state ",new_state,lock)
            new_state.history = state.history + op
            new_list.append(ctype_state(new_state))
            if env.goal_reached(state):
                found_state = state
                break
    q.put(new_list)
    q.put(found_state)


def bfs_multiproccess(file, env):
    print(file)
    if math.ceil(env.state_len/8) >= STATE_LEN:
        print(f"Increase state len to {math.ceil(env.state_len/4)}")
        return None
    pool = (num_proc)
    queues = []
    for i in range(num_proc):
        queues.append(Manager().Queue())

    hashes = dict()
    lis = []
    lock = Lock()
    init_state = env.get_init_state()
    init_state.history = ""
    lis.append(ctype_state(init_state))  # push the initial state


    found_state = None
    count = 0
    max_shared_block = 10000
    while not found_state and len(lis)>0:
        act_proc = min(max(1,len(lis)), num_proc)
        chunk_size = max(math.ceil(len(lis)/num_proc), 1)
        all_list = lis
        for pos_in_all_lis in range(0, len(lis), max_shared_block):
            print_lock(lock, f"Makeing shared memory at {pos_in_all_lis}-{pos_in_all_lis+max_shared_block}")
            #for x in all_list[pos_in_all_lis:pos_in_all_lis+max_shared_block]:
            #    print_tuple_state("copy to shared mem:",x,lock)
            shared_array = Array(CState, all_list[pos_in_all_lis:pos_in_all_lis+max_shared_block], lock=False)
            print_lock(lock, f"making input for processes. all_size:{len(lis)} chunk_size:{chunk_size}")
            lis = []
            input = [(i, queues[i], env, shared_array, i*chunk_size, chunk_size, lock) for i in list(range(act_proc))]
            print_lock(lock, f"Starting {len(input)} jobs")
            pool = []
            for i in input:
                proc=Process(target=bfs_job, args=(i,))
                pool.append(proc)
            for p in pool:
                p.start()
            i = 0
            for p in pool:
                p.join()
                print_lock(lock, f'Joined on process {i}')
                for state in queues[i].get():
                    state_hash = (state[0] << env.state_len) + int(state[1].decode(), 16)
                    look_for = \
                        ['R', 'D', 'L', 'D', 'L', 'U', 'D', 'R', 'U', 'R', 'D', 'L', 'U', 'D', 'R', 'U', 'R', 'D', 'L', 'U', 'R', 'U', 'L', 'D', 'L', 'U', 'L', 'D', 'L', 'U', 'R']
                    #print(list(state[2].decode('utf-8')))
                    #print_tuple_state("debug ", state, lock)
                    #f = False
                    #if list(state[2].decode('utf-8'))[:5] == look_for[:5]:
                    #    print_tuple_state("Found yyy", state, lock)
                    #    print_lock(lock, f'{env.state_len} {state_hash}')
                    #    f = True
                    if state_hash in hashes and hashes[state_hash] <= state[5]:
                        continue
                    #if f:
                    #    print_tuple_state("Adding ", state, lock)
                    hashes[state_hash] = state[5]
                    lis.append(state)
                state = queues[i].get()
                if state is not None:
                    found_state = state
                    print_lock(lock, "Found "+str(list(found_state.history)))
                    return DummyState(list(found_state.history))
                i += 1
        count += 1
        print_lock(lock, f'count:{count} tree:{len(lis)} hash:{len(hashes)}')
        [p.terminate() for p in pool]

    if not found_state:
        print("not found")