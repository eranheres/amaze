from amaze.search_path import bfs_no_tunneling, bfs_tunneling, dfs
from amaze.load_level import env_from_file
from validate_solution import validate_solution
from search_multiprocess import bfs_multiproccess
from amaze.env import Env, TUNNEL_DEEP, TUNNEL_OFF, TUNNEL_SOFT
from amaze.dfs_multi import dfs_multi
import glob, os
import time
import math
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--path', default='../data/all', dest='path', help='path to data')
parser.add_argument('--l0', default=1, dest='l0', type=int)
parser.add_argument('--l1', default=5, dest='l1', type=int)
parser.add_argument('--l2', default=6, dest='l2', type=int)
parser.add_argument('--l3', default=6, dest='l3', type=int)
parser.add_argument('--l4', default=8, dest='l4', type=int)
parser.add_argument('--l5', default=9, dest='l5', type=int)
parser.add_argument('--l6', default=11, dest='l6', type=int)
parser.add_argument('--l7', default=100, dest='l7', type=int)
parser.add_argument('-inspect', default=False, nargs='?', dest='inspect')
args = parser.parse_args()
print("parsing:", args.path)
os.chdir(args.path)
tot = ""

# level0 - bfs single process no tunneling
# level1 - bfs single process soft tunneling
# level2 - bfs multi process soft tunneling (no count = 3)
# level3 - bfs multi process soft tunneling (no count = 2)
# level4 - bfs multi process soft tunneling (no count = 1)
# level5 - bfs multi process deep tunneling (no count = 2)
# level6 - bfs multi process deep tunneling (no count = 1) truncating hash
algos = [
        {"name": "l-0", "max_comp": args.l0, "algo": "bfs", "tun": TUNNEL_OFF, "no_count": -1, "trunc": False},
        {"name": "l-1", "max_comp": args.l1, "algo": "bfs", "tun": TUNNEL_SOFT, "no_count": -1, "trunc": False},
        {"name": "l-2", "max_comp": args.l2, "algo": "bfs_multi", "tun": TUNNEL_SOFT, "no_count": 1, "trunc": False},
        {"name": "l-3", "max_comp": args.l3, "algo": "bfs_multi", "tun": TUNNEL_SOFT, "no_count": 2, "trunc": False},
        {"name": "l-4", "max_comp": args.l4, "algo": "bfs_multi", "tun": TUNNEL_SOFT, "no_count": 3, "trunc": False},
        {"name": "l-5", "max_comp": args.l5, "algo": "bfs_multi", "tun": TUNNEL_DEEP, "no_count": 0, "trunc": False},
        {"name": "l-6", "max_comp": args.l6, "algo": "bfs_multi", "tun": TUNNEL_DEEP, "no_count": 1, "trunc": True},
        {"name": "l-7", "max_comp": args.l7, "algo": "dfs", "tun": TUNNEL_DEEP, "no_count": 1, "trunc": True},
       ]


def get_algo_props(algos, level, width, start_pos):
    for algo in algos:
        env = Env.from_params(level, width, start_pos, algo["tun"])
        complexity = len(str(env.calc_complexity()))
        if complexity <= algo["max_comp"]:
            return algo
    return None


for file in sorted(glob.glob("*.xml")):
    level, start_pos, width, height = env_from_file(file)
    if level is None:
        print("Invalid file format")
        continue
    start_time = time.time()
    info_env = Env.from_params(level, width, start_pos, TUNNEL_OFF)
    display_file = file+"("+str(info_env.count_nodes())+")"
    complexity = info_env.calc_complexity()
    complexity_len = len(str(complexity))

    algo = get_algo_props(algos, level, width, start_pos)
    if not algo:
        print(f"{display_file} : no algo selected")
        continue

    env = Env.from_params(level, width, start_pos, algo["tun"])
    act_complex = len(str(env.calc_complexity()))
    print(f"=> {display_file} level:{algo['name']} base_comp:{complexity_len} act_complex:{act_complex} algo:{algo['algo']} "+\
          f"tunn:{ {0:'off', 1:'soft', 2:'deep'}[algo['tun']]} no_count:{algo['no_count']}")
    if args.inspect:
        continue
    if algo["algo"] == "bfs":
        if algo['tun'] == TUNNEL_OFF:
            solution = bfs_no_tunneling(display_file, env)
        else:
            solution = bfs_tunneling(display_file, env)
    elif algo["algo"] == "bfs_multi":
        no_count = algo["no_count"]
        solution = None
        while not solution:
            solution = bfs_multiproccess(display_file, env, no_count, algo["trunc"])
            no_count+=1
    elif algo["algo"] == "dfs":
        solution = dfs_multi(env)
    else:
        continue

    end_time = time.time()
    if solution:
        history = solution.get_history()
        if validate_solution(history, level, width, start_pos, algo["tun"]):
            run_time = int(end_time - start_time)
            print(f'{display_file} time:{run_time}  algo:{algo["name"]} tunn:{algo["tun"]} depth:{len(history)} solution:{[x for x in history]}')

            tot += file+","+str(run_time)+","+ \
                   Env.from_params(level, width, start_pos, algo["tun"]).get_printable_solution(history)+"\n"
        else:
            print("!! Invalid solution ",file,",", int(end_time-start_time),",", [x for x in history])
    else:
        print(file, "No solution found")

print(tot)
