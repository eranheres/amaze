from amaze.search_path import bfs, dfs, count_nodes
from amaze.load_level import env_from_file
from validate_solution import validate_solution
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
for file in sorted(glob.glob("*.xml")):
    env = env_from_file(file)
    if env is None:
        print("Invalid file format")
        continue
    start_time = time.time()
    nodes = count_nodes(env)
    display_file = file+"("+str(nodes)+")"
    if nodes<max_nodes:
        solution = bfs(display_file, env)
        algo = "!!"
    else:
        solution = dfs(display_file, env)
        algo = "??"
    #solution = None
    end_time = time.time()
    if solution:
        if validate_solution(file, env, solution.history):
            print(algo,display_file,",", int(end_time-start_time),",",len(solution.history),",", [x for x in solution.history])
        else:
            print("!! Invalid solution ",file,",", int(end_time-start_time),",", [x for x in solution.history])
    else:
        print(file, "No solution found")
