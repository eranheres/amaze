import cProfile
import os
from amaze.load_level import env_from_file
from amaze.search_path import bfs, dfs
import re

os.chdir("../../data/test")
level, start_pos, width, height = env_from_file("057.xml")
cProfile.run('re.compile(bfs("057.xml",level,width,start_pos))')
