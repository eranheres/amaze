import cProfile
import os
from amaze.load_level import env_from_file
from amaze.search_path import bfs, dfs
import re

os.chdir("../../data/test")
env = env_from_file("058.xml")
if env is not None:
    cProfile.run('re.compile(dfs("058.xml",env))')
