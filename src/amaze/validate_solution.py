from load_level import env_from_file


def validate_solution(filename, env, solution):
    for op in solution:
        if env.goal_reached():
            return False
        env = env.do_step(op)

    return env.goal_reached()


def validate_solution_text(solution_text):
    splitted = solution_text.split(',')
    filename = int(splitted[0])
    time = int(splitted[1])
    solution = [x for x in splitted[2:]]
    env = env_from_file(filename)
    validate_solution(env, solution)
