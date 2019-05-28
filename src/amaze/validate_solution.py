from load_level import env_from_file
from env import Env, RIGHT, UP, LEFT, DOWN


def validate_solution(solution, level, dimx, pos, tun):
    env = Env.from_params(level, dimx, pos, tun)
    state = env.get_init_state()
    for op in solution:
        if env.goal_reached(state):
            return False
        state = env.do_step(state, op)

    return env.goal_reached(state)


def validate_solution_text(solution_text, tun, numbers=False):
    splitted = solution_text.split(',')
    filename = splitted[0]
    #time = int(splitted[1])
    solution = [x.replace(" ","") for x in splitted[2:]]
    if numbers:
        #solution = [x.replace('1', RIGHT).replace('2',LEFT).replace('3',UP).replace('4',DOWN) for x in solution]
        solution = [{'1': RIGHT, '2': LEFT, '3': UP, '4': DOWN}[x] for x in solution]
    level, start_pos, width, height = env_from_file(filename)
    return validate_solution(solution, level, width, start_pos, tun)

