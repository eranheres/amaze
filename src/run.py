from amaze.search_path import bfs_no_tunneling, bfs_tunneling, dfs
from amaze.load_level import env_from_file
from validate_solution import validate_solution
from search_multiprocess import bfs_multiproccess
from amaze.env import Env, TUNNEL_DEEP, TUNNEL_OFF, TUNNEL_SOFT
import glob, os
import time
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--path', default='../data/all', dest='path', help='path to data')
parser.add_argument('--max_nodes', default=47, dest='max_nodes', help='path to data')
parser.add_argument('--algo', default='bfs', dest='algo', help='bfs of dfs')
parser.add_argument('--tunnel', default='off', dest='tunnel', help='off soft deep')
args = parser.parse_args()
print("parsing:", args.path)
max_nodes = int(args.max_nodes)
algo = args.algo
os.chdir(args.path)
tot = ""
for file in sorted(glob.glob("*.xml")):
    level, start_pos, width, height = env_from_file(file)
    if level is None:
        print("Invalid file format")
        continue
    start_time = time.time()
    tun = {"off": TUNNEL_OFF, "soft": TUNNEL_SOFT, "deep": TUNNEL_DEEP}[args.tunnel]
    env = Env.from_params(level, width, start_pos, tun)
    nodes = env.count_nodes()
    display_file = file+"("+str(nodes)+")"
    if nodes>max_nodes:
        tot += file +", -1\n"
        print("Skipping level "+file+" with nodes="+str(nodes))
        continue
    solution = None
    if args.algo == "bfs_multi":
        solution = bfs_multiproccess(file, env)
    elif args.algo == "bfs":
        if tun == TUNNEL_OFF:
            solution = bfs_no_tunneling(display_file, env)
        else:
            solution = bfs_tunneling(display_file, env)
    elif args.algo == "dfs":
        solution = dfs(display_file, env)
    #solution = None
    end_time = time.time()
    if solution:
        history = solution.get_history()
        if validate_solution(history, level, width, start_pos, tun):
            run_time = int(end_time - start_time)
            print(algo,",tunn:",str(tun),",",display_file,",", run_time,",",len(history),",", [x for x in history])

            tot += file+","+str(run_time)+","+ \
                   Env.from_params(level, width, start_pos, tun).get_printable_solution(history)+"\n"
        else:
            print("!! Invalid solution ",file,",", int(end_time-start_time),",", [x for x in history])
    else:
        print(file, "No solution found")

print(tot)
