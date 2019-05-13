from amaze.search_path import bfs, dfs, count_nodes
from amaze.load_level import env_from_file
from validate_solution import validate_solution
from amaze.env import Env
import glob, os
import time
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--path', default='../data/all', dest='path', help='path to data')
parser.add_argument('--max_nodes', default=47, dest='max_nodes', help='path to data')
args = parser.parse_args()
print("parsing:", args.path)
max_nodes = int(args.max_nodes)
os.chdir(args.path)
tot = ""
for file in sorted(glob.glob("*.xml")):
    level, start_pos, width, height = env_from_file(file)
    if level is None:
        print("Invalid file format")
        continue
    start_time = time.time()
    nodes = count_nodes(level, width, start_pos)
    display_file = file+"("+str(nodes)+")"
    if nodes<max_nodes:
        solution = bfs(display_file, level, width, start_pos)
        tun = False
        algo = "!!"
    else:
        solution = dfs(display_file, level, width, start_pos)
        tun = True
        algo = "??"
    #solution = None
    end_time = time.time()
    if solution:
        if validate_solution(solution.history, level, width, start_pos, tun):
            run_time = int(end_time - start_time)
            print(algo,display_file,",", run_time,",",len(solution.history),",", [x for x in solution.history])
            tot += file+","+str(run_time)+","+Env.get_printable_solution(level, width, start_pos, solution.history, tun)+"\n"
        else:
            print("!! Invalid solution ",file,",", int(end_time-start_time),",", [x for x in solution.history])
    else:
        print(file, "No solution found")

print(tot)
