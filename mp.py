from sage.all import Integer, GF, Ideal, crt
import multiprocessing
from time import time, sleep
import queue


def groebner(pols, var, bound, max_fails=10):
    start = time()

    R = pols[0].parent()
    num = R.ngens()
    p = Integer(1 << 27)
    m = 1
    fails = 0
    crt_rem = []
    crt_mod = []

    max_proc = 6
    procs = []
    rsts = multiprocessing.Queue()

    # 多进程初始化
    for _ in range(max_proc):
        p = p.next_prime()
        R = R.change_ring(GF(p))

        proc = multiprocessing.Process(target=worker, args=(R, num, p, pols, var, rsts))
        proc.start()
        procs.append(proc)

    # 轮询结果并补充新进程
    while True:
        if fails >= max_fails:
            for p in procs:
                p.terminate()
            for p in procs:
                p.join()
            print(f"fail: {time() - start}")
            return None

        if m >= bound:
            for p in procs:
                p.terminate()
            for p in procs:
                p.join()
            print(f"succ: {time() - start}")
            return crt(crt_rem, crt_mod)

        procs = [p for p in procs if p.is_alive()]
        if len(procs) < max_proc:
            for _ in range(max_proc - len(procs)):
                p = p.next_prime()
                R = R.change_ring(GF(p))

                proc = multiprocessing.Process(
                    target=worker, args=(R, num, p, pols, var, rsts)
                )
                proc.start()
                procs.append(proc)

        try:
            r = rsts.get(timeout=0.01)
            if r is None:
                fails += 1
            else:
                crt_rem.append(r[0])
                crt_mod.append(r[1])
                m *= r[1]
        except queue.Empty:
            pass


def worker(R, num, p, pols, var, rsts):
    for i in range(len(pols), num - 1, -1):
        I = Ideal((R * pols[:i]).groebner_basis())
        if I.dimension() == 0:
            sols = I.variety()
            sol_var = set()
            sol_var.update([sol[var] for sol in sols])
            if len(sol_var) == 1:
                rsts.put((Integer(sols[0][var]), p))
                break
    else:
        rsts.put(None)
