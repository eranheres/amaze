import cProfile
import os
from amaze.load_level import env_from_file
from amaze.env import Env, TUNNEL_OFF
from amaze.search_path import dfs
import re

os.chdir("../data/all")
level, start_pos, width, height = env_from_file("017.xml")
env = Env.from_params(level, width, start_pos, TUNNEL_OFF)
cProfile.run('re.compile(dfs("017.xml",env))')
