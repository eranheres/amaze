import unittest
import os
import glob
from env import Env, UP, DOWN, LEFT, RIGHT, TUNNEL_SOFT, TUNNEL_OFF, TUNNEL_DEEP
from myqueue import Queue, PriorityQueue
from search_path import dfs, bfs_tunneling, bfs_no_tunneling
from search_multiprocess import bfs_multiproccess
from validate_solution import validate_solution, validate_solution_text
from load_level import env_from_file

class TestEnvMethods(unittest.TestCase):

    def test_init(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000222' \
            '22222222222'
        env = Env.from_params(list(level), 11, 3+11*1, tunneling=TUNNEL_OFF)
        state = env.get_init_state()
        self.assertEqual(state.pos, 3+11*1)
        self.assertEqual(env.nodes[1+1*11][RIGHT][0], 1*11+5)
        self.assertEqual(env.nodes[1+1*11][RIGHT][2], 1)

    def test_possible_pos(self):
        level = \
            '22222222222' \
            '20000022222' \
            '22200000222' \
            '22222222222'
        self.assertEqual([LEFT, RIGHT, DOWN], Env.from_params(list(level), 11, 1*11+3).calc_possible_ops(1*11+3))
        self.assertEqual([RIGHT, UP], Env.from_params(list(level), 11, 2*11+2).calc_possible_ops(2*11+2))
        self.assertEqual([LEFT], Env.from_params(list(level), 11, 2*11+7).calc_possible_ops(2*11+7))

    def test_goal_reached(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000202' \
            '22200000222' \
            '22222222222'
        env = Env.from_params(list(level), 11, 3*11+1)
        self.assertFalse(env.goal_reached(env.get_init_state()))

        level = \
            '22222222222' \
            '21111122222' \
            '22211111212' \
            '22211111222' \
            '22222222222'
        env = Env.from_params(list(level), 11, 3+11*4)
        self.assertTrue(env.goal_reached(env.get_init_state()))

    def test_hash(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22210000202' \
            '22200010222' \
            '22222222222'
        env = Env.from_params(list(level), 11, 3+2*11)
        s = bin(2*11 + 3)[2:] + '0010010000000010'
        # '110010010000000000010'
        # '110010010010000000010'
        expected = int(s, 2)
        self.assertEqual(expected, env.state_hash(env.get_init_state()))

    def test_do_step_tunneling(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000202' \
            '22200000222' \
            '22222222222'

        env = Env.from_params(list(level), 11, 3+1*11, tunneling=TUNNEL_OFF)
        expected = \
            '22222222222' \
            '20011122222' \
            '22200000202' \
            '22200000222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 5+1*11)
        new_state = env.do_step(env.get_init_state(), RIGHT)
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(5+1*11, new_state.pos)
        self.assertEqual(env.nodes[3+1*11][RIGHT][2], 1)

        env = Env.from_params(list(level), 11, 3+1*11)
        expected = \
            '22222222222' \
            '20010022222' \
            '22210000202' \
            '22210000222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 3*11+3, tunneling=TUNNEL_OFF)
        new_state = env.do_step(env.get_init_state(), DOWN)
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(3*11+3, new_state.pos)
        self.assertEqual(env.nodes[3+3*11][RIGHT][2], 1)

        level = \
            '22222222222' \
            '20000022222' \
            '22200000202' \
            '22200100222' \
            '22222222222'

        env = Env.from_params(list(level), 11, 5+3*11)
        expected = \
            '22222222222' \
            '20000022222' \
            '22200000202' \
            '22211100222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 3+3*11)
        new_state = env.do_step(env.get_init_state(), LEFT)
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(3*11+3, new_state.pos)

        env = Env.from_params(list(level), 11, 5+3*11, tunneling=TUNNEL_OFF)
        expected = \
            '22222222222' \
            '20000122222' \
            '22200100202' \
            '22200100222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 1*11+5)
        new_state = env.do_step(env.get_init_state(), UP)
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(1*11+5, new_state.pos)

        level = \
            '22222222222' \
            '20000000002' \
            '20222222202' \
            '20000000002' \
            '22222222222'

        env = Env.from_params(list(level), 11, 1*11+1)
        expected = \
            '22222222222' \
            '21111111112' \
            '20222222202' \
            '20000000002' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 1*11+9)
        new_state = env.do_step(env.get_init_state(), RIGHT)
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(1*11+9, new_state.pos)
        self.assertEqual(env.nodes[1+1*11][RIGHT][2], 1)

    def test_do_step_no_tunneling(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000202' \
            '22200000222' \
            '22222222222'

        env = Env.from_params(list(level), 11, 3+1*11, tunneling=TUNNEL_DEEP)
        expected = \
            '22222222222' \
            '20011122222' \
            '22200100202' \
            '22200100222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 5+3*11)
        new_state = env.do_step(env.get_init_state(), RIGHT)
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(3*11+5, new_state.pos)
        self.assertEqual(env.nodes[3+1*11][RIGHT][2], 2)

        env = Env.from_params(list(level), 11, 1*11+3, tunneling=TUNNEL_DEEP)
        expected = \
            '22222222222' \
            '20010022222' \
            '22211111202' \
            '22211111222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 3+2*11, tunneling=TUNNEL_DEEP)
        new_state = env.do_step(env.get_init_state(), DOWN)
        # print(bin(expected.state_hash()))
        # print(bin(new_env.state_hash()))
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(2*11+3, new_state.pos)
        self.assertEqual(env.nodes[3+2*11][RIGHT][2], 4)

        level = \
            '22222222222' \
            '20000022222' \
            '22200000202' \
            '22200100222' \
            '22222222222'

        env = Env.from_params(list(level), 11, 5+3*11, tunneling=TUNNEL_DEEP)
        expected = \
            '22222222222' \
            '20010022222' \
            '22210000202' \
            '22211100222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 3+1*11)
        new_state = env.do_step(env.get_init_state(), LEFT)
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(1*11+3, new_state.pos)
        self.assertEqual(env.nodes[5+3*11][LEFT][2], 2)

        env = Env.from_params(list(level), 11, 5+3*11, tunneling=TUNNEL_DEEP)
        expected = \
            '22222222222' \
            '21111122222' \
            '22200100202' \
            '22200100222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 3*11+5)
        new_state = env.do_step(env.get_init_state(), UP)
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(3*11+5, new_state.pos)

        level = \
            '22222222222' \
            '20000000002' \
            '20222222202' \
            '20000000002' \
            '22222222222'

        env = Env.from_params(list(level), 11, 1*11+1, tunneling=TUNNEL_DEEP)
        expected = \
            '22222222222' \
            '21111111112' \
            '21222222212' \
            '21111111112' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 1*11+1)
        new_state = env.do_step(env.get_init_state(), RIGHT)
        self.assertEqual(expected.state_hash(expected.get_init_state()), env.state_hash(new_state))
        self.assertEqual(1*11+1, new_state.pos)
        self.assertEqual(env.nodes[1+1*11][RIGHT][2], 4)


class TestQueue(unittest.TestCase):
    def test_pop(self):
        q = Queue()
        self.assertTrue(q.empty())
        q.append("1")
        self.assertFalse(q.empty())

        self.assertEqual("1", q.pop())
        self.assertTrue(q.empty())
        q.append("2")
        self.assertFalse(q.empty())
        q.append("3")
        q.append("4")
        q.append("5")
        q.append("6")

        self.assertFalse(q.empty())
        self.assertEqual("2", q.pop())
        self.assertEqual("3", q.pop())
        self.assertEqual("4", q.pop())
        self.assertEqual("5", q.pop())
        self.assertFalse(q.empty())
        self.assertEqual("6", q.pop())
        self.assertTrue(q.empty())

    def test_priority_queue(self):
        class Item:
            def __init__(self, priority, val):
                self.depth = priority
                self.val = val

        q = PriorityQueue()
        self.assertTrue(q.empty())
        q.append(Item(1, "1"))
        self.assertFalse(q.empty())

        self.assertEqual("1", q.pop().val)
        self.assertTrue(q.empty())
        q.append(Item(2, "2"))
        self.assertFalse(q.empty())
        q.append(Item(2, "3"))
        q.append(Item(1, "4"))
        q.append(Item(3, "5"))
        q.append(Item(1, "6"))

        self.assertFalse(q.empty())
        self.assertEqual("4", q.pop().val)
        self.assertEqual("6", q.pop().val)
        self.assertEqual("2", q.pop().val)
        self.assertEqual("3", q.pop().val)
        self.assertFalse(q.empty())
        self.assertEqual("5", q.pop().val)
        self.assertTrue(q.empty())


class TestIslands(unittest.TestCase):
    def test_islands1(self):
        level = \
            '0,0,0,0,0,0,0,' \
            '0,1,1,1,1,1,0,' \
            '0,1,0,0,0,1,0,' \
            '0,1,0,1,0,1,0,' \
            '0,1,0,1,0,1,0,' \
            '0,1,0,1,1,1,0,' \
            '0,0,0,0,0,0,0'.replace('0', '2').replace('1', '0').replace(',', '')
        env = Env.from_params(list(level), 7, 7*1+1, TUNNEL_DEEP)
#        self.assertEqual(1, get_island_length(env, DOWN))
#        self.assertEqual(4, get_island_length(env, RIGHT))
        self.assertEqual(1, env.count_nodes())

    def test_islands2(self):
        level = \
            '0,0,0,0,0,0,0,' \
            '0,1,1,1,0,1,0,' \
            '0,1,0,1,0,1,0,' \
            '0,1,1,1,1,1,0,' \
            '0,0,0,1,0,1,0,' \
            '0,1,1,1,0,1,0,' \
            '0,0,0,0,0,0,0'.replace('0', '2').replace('1', '0').replace(',', '')
        env = Env.from_params(list(level), 7, 7*1+1, TUNNEL_DEEP)
#        self.assertEqual(3, get_island_length(env, RIGHT))
#        self.assertEqual(4, get_island_length(env, DOWN))
        self.assertEqual(4, env.count_nodes())

    def test_islands3(self):
        level = \
            '0,0,0,0,0,0,0,0,0,' \
            '0,1,1,1,0,0,1,1,0,' \
            '0,0,0,1,1,1,1,1,0,' \
            '0,1,1,1,1,1,1,0,0,' \
            '0,1,1,1,1,1,1,1,0,' \
            '0,0,0,0,0,0,0,1,0,' \
            '0,1,1,1,1,1,1,1,0,' \
            '0,0,0,0,0,0,0,0,0'.replace('0', '2').replace('1', '0').replace(',', '')
        #env = Env.from_params(list(level), 1, 1, 9, 8)
        #self.assertEqual(13, get_island_length(env, RIGHT))
        #env = Env.from_params(list(level), 3, 1, 9, 8)
        #self.assertEqual(1, get_island_length(env, LEFT))
        #self.assertEqual(12, get_island_length(env, DOWN))

    def test_islands4(self):
        level = \
            '0,0,0,0,0,0,0,0,0,' \
            '0,1,1,1,0,0,0,0,0,' \
            '0,1,0,1,0,0,0,0,0,' \
            '0,1,1,1,1,1,1,0,0,' \
            '0,1,1,1,1,1,1,0,0,' \
            '0,0,0,0,0,0,0,0,0,' \
            '0,0,0,0,0,0,0,0,0,' \
            '0,0,0,0,0,0,0,0,0'.replace('0', '2').replace('1', '0').replace(',', '')
        env = Env.from_params(list(level), 9, 9*1+1)
#        self.assertEqual(-1, get_island_length(env, RIGHT))
#        self.assertEqual(4, get_island_length(env, DOWN))


class TestDfs(unittest.TestCase):
    def test_dfs(self):
        level = \
            '0,0,0,0,0,0,0,' \
            '0,1,1,1,1,1,0,' \
            '0,1,0,0,0,1,0,' \
            '0,1,0,1,0,1,0,' \
            '0,1,0,1,0,1,0,' \
            '0,1,0,1,1,1,0,' \
            '0,0,0,0,0,0,0'.replace('0', '2').replace('1', '0').replace(',', '')
        env = Env.from_params(list(level), 7, 1*7+1, TUNNEL_OFF)
        dfs("test", env)


class TestTunnels(unittest.TestCase):
        # 0:  --,--,--,--,--,--,--,--,--,
        # 9:  --,10,**,**,--,14,15,16,--,
        # 18: --,19,**,21,**,**,**,25,--,
        # 27: --,**,--,--,--,32,**,34,--,
        # 36: --,37,**,**,**,41,42,--,--,
        # 45: --,--,--,--,--,--,51,52,--,
        # 54: --,**,**,**,--,--,**,**,--,
        # 63: --,64,--,66,**,**,69,70,--,
        # 72: --,--,--,--,--,--,--,--,--
        def test_level_9(self):
            level = \
                '0,0,0,0,0,0,0,0,0,'\
                '0,1,1,1,0,1,1,1,0,'\
                '0,1,1,1,1,1,1,1,0,'\
                '0,1,0,0,0,1,1,1,0,'\
                '0,1,1,1,1,1,1,0,0,'\
                '0,0,0,0,0,0,1,1,0,'\
                '0,1,1,1,0,0,1,1,0,'\
                '0,1,0,1,1,1,1,1,0,'\
                '0,0,0,0,0,0,0,0,0'.replace('0', '2').replace('1', '0').replace(',', '')

            tun_env = Env.from_params(list(level), 9, 10, TUNNEL_SOFT)
            #self.assertEqual(19, tun_env.count_nodes())
            bfs_tun_state = bfs_tunneling("test", env=tun_env)

            env_no_tun = Env.from_params(list(level), 9, 10, TUNNEL_OFF)
            #self.assertEqual(21, env.count_nodes())
            bfs_no_tun_state = bfs_no_tunneling("test", env=env_no_tun)

            #bfs_history = env.get_printable_solution(bfs_state.get_history())
            #bfs_tun_history = tun_env.get_printable_solution(bfs_tun_state.get_history())

            print("with tunneling:", bfs_tun_state.get_history())
            print("no tunneling  :", bfs_no_tun_state.get_history())

            sol_tun = tun_env.get_printable_solution(bfs_tun_state.get_history())
            sol_no_tun = env_no_tun.get_printable_solution(bfs_no_tun_state.get_history())

            print("with tunneling:", sol_tun)
            print("no tunneling  :", sol_no_tun)

            solution_tun = [x.replace('1', 'R').replace('2', 'L').replace('3', 'U').replace('4', 'D') for x in sol_tun.split(",")]
            self.assertTrue(validate_solution(solution_tun, level, 9, 10, TUNNEL_OFF))
            solution_no_tun = [x.replace('1', 'R').replace('2', 'L').replace('3', 'U').replace('4', 'D') for x in sol_no_tun.split(",")]
            self.assertTrue(validate_solution(solution_no_tun, level, 9, 10, TUNNEL_OFF))
            self.assertTrue(validate_solution(solution_tun, level, 9, 10, TUNNEL_OFF))

            self.assertEqual(len(solution_no_tun), len(solution_tun))

        def test_multiple_levels(self):
            os.chdir("../../data/test")
            for file in sorted(glob.glob("*.xml")):
                level, start_pos, width, height = env_from_file(file)
                self.assertIsNotNone(level)
                no_tun_env = Env.from_params(level, width, start_pos, TUNNEL_OFF)
                tun_soft_env = Env.from_params(level, width, start_pos, TUNNEL_SOFT)
                print(f'Testing {file}: {tun_soft_env.count_nodes()}/{no_tun_env.count_nodes()}')
                no_tun_state = bfs_no_tunneling(file, no_tun_env)
                tun_soft_state = bfs_tunneling(file, tun_soft_env)
                no_tun_dfs_state = dfs(file, no_tun_env)
                no_tun_multi_state = bfs_multiproccess(file, no_tun_env)
                self.assertIsNotNone(no_tun_state)
                self.assertIsNotNone(tun_soft_state)
                self.assertIsNotNone(no_tun_dfs_state)
                self.assertIsNotNone(no_tun_multi_state)
                no_tun_printable = no_tun_env.get_printable_solution(no_tun_state.get_history())
                tun_soft_printable = tun_soft_env.get_printable_solution(tun_soft_state.get_history())
                no_tun_dfs_printable = no_tun_env.get_printable_solution(no_tun_dfs_state.get_history())
                no_tun_mp_printable = no_tun_env.get_printable_solution(no_tun_multi_state.get_history())
                no_tun_sol = [x.replace('1', 'R').replace('2', 'L').replace('3', 'U').replace('4', 'D') for x in no_tun_printable.split(",")]
                tun_soft_sol = [x.replace('1', 'R').replace('2', 'L').replace('3', 'U').replace('4', 'D') for x in tun_soft_printable.split(",")]
                no_tun_dfs_sol = [x.replace('1', 'R').replace('2', 'L').replace('3', 'U').replace('4', 'D') for x in no_tun_dfs_printable.split(",")]
                no_tun_mul_sol = [x.replace('1', 'R').replace('2', 'L').replace('3', 'U').replace('4', 'D') for x in no_tun_mp_printable.split(",")]
                self.assertTrue(validate_solution(no_tun_sol, level, width, start_pos, TUNNEL_OFF))
                self.assertTrue(validate_solution(tun_soft_sol, level, width, start_pos, TUNNEL_OFF))
                self.assertTrue(validate_solution(no_tun_dfs_sol, level, width, start_pos, TUNNEL_OFF))
                self.assertTrue(validate_solution(no_tun_mul_sol, level, width, start_pos, TUNNEL_OFF))
                self.assertEqual(len(no_tun_sol), len(tun_soft_sol))
                print(no_tun_state.get_history())
                self.assertEqual(len(no_tun_sol), len(no_tun_dfs_sol))
                self.assertEqual(len(no_tun_sol), len(no_tun_mul_sol))


if __name__ == '__main__':
    unittest.main()
