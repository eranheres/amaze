from multiprocessing import Pool, Queue, Manager
from amaze.env import Env, TUNNEL_SOFT, State
from load_level import env_from_file
from multiprocessing import Process, Lock, Queue as MPQueue
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double, c_uint, c_wchar, c_buffer, c_char
import ctypes


class Strct(Structure):
    _fields_ = [('x', c_uint), ('s', (c_char * 30))]

def my_job(v, lock):
    lock.acquire()
    print([x.s for x in v])
    #v.s[0] = str.encode('d')
    lock.release()


v = 'str'
l = Lock()
# arr = Array(c_char, str.encode('eran'), lock=False)
arr = Array(Strct, [(1,str.encode('eran'))], lock=False)
p = Process(target=my_job, args=(arr, l, ))
p.start()
p.join()
print([x for x in arr])
