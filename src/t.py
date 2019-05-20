from multiprocessing import Process, Manager

def f(d):
    for i in range(10000):
        d['blah'] += 1

if __name__ == '__main__':
    manager = Manager()

    d = manager.dict()
    d['blah'] = 0
    procs = [ Process(target=f, args=(d,)) for _ in range(10) ]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

    print(d)