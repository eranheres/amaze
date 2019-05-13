import unittest
from env import Env, EMPTY, COLORED, WALL, UP, DOWN, LEFT, RIGHT
from myqueue import Queue
from load_level import env_from_file
from search_path import get_island_length, count_nodes, dfs

class TestEnvMethods(unittest.TestCase):

    def test_init(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000222' \
            '22222222222'
        env = Env.from_params(list(level), 11, 3+11*1, tunneling=True)
        self.assertEqual(env.pos, 3+11*1)
        self.assertEqual(env.nodes[1+1*11][RIGHT][0],2*11+5)
        self.assertEqual(env.nodes[1+1*11][RIGHT][2],2)

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_possible_pos(self):
        level = \
            '22222222222' \
            '20000022222' \
            '22200000222' \
            '22222222222'
        self.assertEqual([LEFT, RIGHT, DOWN], Env.possible_ops(list(level), 11, 1*11+3))
        self.assertEqual([RIGHT, UP], Env.possible_ops(list(level), 11, 2*11+2))
        self.assertEqual([LEFT], Env.possible_ops(list(level), 11, 2*11+7))

    def test_goal_reached(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000202' \
            '22200000222' \
            '22222222222'
        env = Env.from_params(list(level), 11, 3*11+1)
        self.assertFalse(env.goal_reached())

        level = \
            '22222222222' \
            '21111122222' \
            '22211111212' \
            '22211111222' \
            '22222222222'
        env = Env.from_params(list(level), 11, 3+11*4)
        self.assertTrue(env.goal_reached())

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
        self.assertEqual(expected, env.state_hash())

    def test_do_step_tunneling(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000202' \
            '22200000222' \
            '22222222222'

        env = Env.from_params(list(level), 11, 3+1*11, tunneling=False)
        expected = \
            '22222222222' \
            '20011122222' \
            '22200000202' \
            '22200000222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 5+1*11)
        new_env = env.do_step(RIGHT)
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(5+1*11, new_env.pos)
        self.assertEqual(env.nodes[3+1*11][RIGHT][2],1)

        env = Env.from_params(list(level), 11, 3+1*11)
        expected = \
            '22222222222' \
            '20010022222' \
            '22210000202' \
            '22210000222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 3*11+3, tunneling=False)
        new_env = env.do_step(DOWN)
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(3*11+3, new_env.pos)
        self.assertEqual(env.nodes[3+3*11][RIGHT][2],1)


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
        new_env = env.do_step(LEFT)
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(3*11+3, new_env.pos)

        env = Env.from_params(list(level), 11, 5+3*11, tunneling=False)
        expected = \
            '22222222222' \
            '20000122222' \
            '22200100202' \
            '22200100222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 1*11+5)
        new_env = env.do_step(UP)
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(1*11+5, new_env.pos)

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
        new_env = env.do_step(RIGHT)
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(1*11+9, new_env.pos)
        self.assertEqual(env.nodes[1+1*11][RIGHT][2],1)

    def test_do_step_no_tunneling(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000202' \
            '22200000222' \
            '22222222222'

        env = Env.from_params(list(level), 11, 3+1*11, tunneling=True)
        expected = \
            '22222222222' \
            '20011122222' \
            '22200100202' \
            '22200100222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 5+3*11)
        new_env = env.do_step(RIGHT)
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(3*11+5, new_env.pos)
        self.assertEqual(env.nodes[3+1*11][RIGHT][2],2)

        env = Env.from_params(list(level), 11, 1*11+3, tunneling=True)
        expected = \
            '22222222222' \
            '20010022222' \
            '22211111202' \
            '22211111222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 3+2*11, tunneling=True)
        new_env = env.do_step(DOWN)
        #print(bin(expected.state_hash()))
        #print(bin(new_env.state_hash()))
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(2*11+3, new_env.pos)
        self.assertEqual(env.nodes[3+2*11][RIGHT][2],4)

        level = \
            '22222222222' \
            '20000022222' \
            '22200000202' \
            '22200100222' \
            '22222222222'

        env = Env.from_params(list(level), 11, 5+3*11, tunneling=True)
        expected = \
            '22222222222' \
            '20010022222' \
            '22210000202' \
            '22211100222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 3+1*11)
        new_env = env.do_step(LEFT)
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(1*11+3, new_env.pos)
        self.assertEqual(env.nodes[5+3*11][LEFT][2],2)

        env = Env.from_params(list(level), 11, 5+3*11, tunneling=True)
        expected = \
            '22222222222' \
            '21111122222' \
            '22200100202' \
            '22200100222' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 1*11+1)
        new_env = env.do_step(UP)
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(1*11+1, new_env.pos)

        level = \
            '22222222222' \
            '20000000002' \
            '20222222202' \
            '20000000002' \
            '22222222222'

        env = Env.from_params(list(level), 11, 1*11+1, tunneling=True)
        expected = \
            '22222222222' \
            '21111111112' \
            '21222222212' \
            '21111111112' \
            '22222222222'
        expected = Env.from_params(list(expected), 11, 1*11+1)
        new_env = env.do_step(RIGHT)
        self.assertEqual(expected.state_hash(), new_env.state_hash())
        self.assertEqual(1*11+1, new_env.pos)
        self.assertEqual(env.nodes[1+1*11][RIGHT][2],4)


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
        env = Env.from_params(list(level), 7, 7*1+1)
#        self.assertEqual(1, get_island_length(env, DOWN))
#        self.assertEqual(4, get_island_length(env, RIGHT))
        self.assertEqual(3, count_nodes(list(level), 7, 1*7+1))

    def test_islands2(self):
        level = \
            '0,0,0,0,0,0,0,' \
            '0,1,1,1,0,1,0,' \
            '0,1,0,1,0,1,0,' \
            '0,1,1,1,1,1,0,' \
            '0,0,0,1,0,1,0,' \
            '0,1,1,1,0,1,0,' \
            '0,0,0,0,0,0,0'.replace('0', '2').replace('1', '0').replace(',', '')
#        self.assertEqual(3, get_island_length(env, RIGHT))
#        self.assertEqual(4, get_island_length(env, DOWN))
        self.assertEqual(5, count_nodes(list(level), 7, 1*7+1))

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
        dfs("test", level, 7, 1*7+1)


if __name__ == '__main__':
    unittest.main()
