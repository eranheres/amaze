import unittest
from env import Env, EMPTY, COLORED, WALL, UP, DOWN, LEFT, RIGHT
from myqueue import Queue
from load_level import env_from_file
from search_path import get_island_length

class TestEnvMethods(unittest.TestCase):

    def test_init(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000222' \
            '22222222222'
        env = Env(list(level), 3, 1, 11, 4)
        expected = env.level_rep
        self.assertEqual(list(level), expected)
        self.assertEqual(env.pos_x, 3)
        self.assertEqual(env.pos_y, 1)

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
        env = Env(list(level), 3, 1, 11, 4)
        self.assertEqual([LEFT, RIGHT, DOWN], env.possible_ops())
        env = Env(list(level), 2, 2, 11, 4)
        self.assertEqual([RIGHT, UP], env.possible_ops())
        env = Env(list(level), 7, 2, 11, 4)
        self.assertEqual([LEFT], env.possible_ops())

    def test_goal_reached(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000202' \
            '22200000222' \
            '22222222222'
        env = Env(list(level), 3, 1, 11, 4)
        self.assertFalse(env.goal_reached())

        level = \
            '22222222222' \
            '21111122222' \
            '22211111212' \
            '22211111222' \
            '22222222222'
        env = Env(list(level), 3, 1, 11, 4)
        self.assertTrue(env.goal_reached())

    def test_hash(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22210000202' \
            '22200010222' \
            '22222222222'
        env = Env(list(level), start_x=3, start_y=2, dimx=11, dimy=4)
        s = bin(2*11 + 3)[2:] + '0010010000000010'
        # '110010010000000000010'
        # '110010010010000000010'
        expected = int(s, 2)
        self.assertEqual(expected, env.state_hash())

    def test_do_step(self):
        level = \
            '22222222222' \
            '20010022222' \
            '22200000202' \
            '22200000222' \
            '22222222222'

        env = Env(list(level), 3, 1, 11, 4)
        expected = \
            '22222222222' \
            '20011122222' \
            '22200000202' \
            '22200000222' \
            '22222222222'
        new_env = env.do_step(RIGHT)
        self.assertEqual(list(expected), new_env.level_rep)
        self.assertEqual(5, new_env.pos_x)
        self.assertEqual(1, new_env.pos_y)

        env = Env(list(level), 3, 1, 11, 4)
        expected = \
            '22222222222' \
            '20010022222' \
            '22210000202' \
            '22210000222' \
            '22222222222'
        new_env = env.do_step(DOWN)
        self.assertEqual(list(expected), new_env.level_rep)
        self.assertEqual(3, new_env.pos_x)
        self.assertEqual(3, new_env.pos_y)

        level = \
            '22222222222' \
            '20000022222' \
            '22200000202' \
            '22200100222' \
            '22222222222'

        env = Env(list(level), 5, 3, 11, 4)
        expected = \
            '22222222222' \
            '20000022222' \
            '22200000202' \
            '22211100222' \
            '22222222222'
        new_env = env.do_step(LEFT)
        self.assertEqual(list(expected), new_env.level_rep)
        self.assertEqual(3, new_env.pos_x)
        self.assertEqual(3, new_env.pos_y)

        env = Env(list(level), 5, 3, 11, 4)
        expected = \
            '22222222222' \
            '20000122222' \
            '22200100202' \
            '22200100222' \
            '22222222222'
        new_env = env.do_step(UP)
        self.assertEqual(list(expected), new_env.level_rep)
        self.assertEqual(5, new_env.pos_x)
        self.assertEqual(1, new_env.pos_y)


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
        env = Env(list(level), 1, 1, 7, 7)
        self.assertEqual(1, get_island_length(env, DOWN))
        self.assertEqual(4, get_island_length(env, RIGHT))

    def test_islands2(self):
        level = \
            '0,0,0,0,0,0,0,' \
            '0,1,1,1,0,1,0,' \
            '0,1,0,1,0,1,0,' \
            '0,1,1,1,1,1,0,' \
            '0,0,0,1,0,1,0,' \
            '0,1,1,1,0,1,0,' \
            '0,0,0,0,0,0,0'.replace('0', '2').replace('1', '0').replace(',', '')
        env = Env(list(level), 1, 1, 7, 7)
        self.assertEqual(3, get_island_length(env, RIGHT))
        self.assertEqual(4, get_island_length(env, DOWN))

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
        env = Env(list(level), 1, 1, 9, 8)
        self.assertEqual(13, get_island_length(env, RIGHT))
        env = Env(list(level), 3, 1, 9, 8)
        self.assertEqual(1, get_island_length(env, LEFT))
        self.assertEqual(12, get_island_length(env, DOWN))

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
        env = Env(list(level), 1, 1, 9, 8)
        self.assertEqual(-1, get_island_length(env, RIGHT))
        self.assertEqual(4, get_island_length(env, DOWN))

if __name__ == '__main__':
    unittest.main()
