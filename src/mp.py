from sage.all import Integer, GF, Ideal, crt
import multiprocessing
from time import time
import queue


def groebner(pols, bound_var, max_fails=10, N=None, neg=False):
    def worker(R, num, p, pols, var, rsts, N=None):
        for i in range(len(pols), num - 1, -1):
            I = Ideal((R * pols[:i]).groebner_basis())
            if I.dimension() == 0:
                sols = I.variety()
                sol_var = set()
                sol_var.update([sol[var] for sol in sols])
                sol_var = list(Integer(e) for e in sol_var)
                if N and len(sol_var) == 2:
                    rsts.put((sol_var[:], p))
                    break
                elif len(sol_var) == 1:
                    rsts.put((sol_var[0], p))
                    break
        else:
            rsts.put(None)

    start = time()
    print(f"mp len(pols): {len(pols)}")
    bound, var = bound_var
    if bound < 0:
        bound = -bound
        neg = True
    R = pols[0].parent()
    num = R.ngens()
    p = Integer(1 << 27)
    m = 1
    fails = 0
    crt_rem = []
    crt_mod = []

    max_proc = 8
    procs = []
    rsts = multiprocessing.Queue()

    # 多进程初始化
    for _ in range(max_proc):
        p = p.next_prime()
        R = R.change_ring(GF(p))

        proc = multiprocessing.Process(
            target=worker, args=(R,num, p, pols, var, rsts, N)
        )
        proc.start()
        procs.append(proc)

    # 轮询结果并补充新进程
    while True:
        if fails < max_fails and m >= bound:
            for p in procs:
                p.terminate()
            for p in procs:
                p.join()
            print(f"groebner success: {time() - start}")

            if N:
                def recursive(res, m, d):
                    if d == len(crt_rem):
                        if N % res == 0:
                            return res
                        return None
                    ret1 = recursive(
                        crt([res, crt_rem[d][0]], [m, crt_mod[d]]),
                        m * crt_mod[d],
                        d + 1,
                    )
                    if ret1:
                        return ret1
                    ret2 = recursive(
                        crt([res, crt_rem[d][1]], [m, crt_mod[d]]),
                        m * crt_mod[d],
                        d + 1,
                    )
                    if ret2:
                        return ret2

                res = recursive(crt_rem[0][0], crt_mod[0], 1)
            else:
                res = crt(crt_rem, crt_mod)
            if neg is True:
                m = 1
                for mod in crt_mod:
                    m *= mod
                return res - m
            else:
                return res

        if fails >= max_fails:
            for p in procs:
                p.terminate()
            for p in procs:
                p.join()
            print(f"groebner fail: {time() - start}")
            return None

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
            r = rsts.get(timeout=0.1)
            if r is None:
                fails += 1
            else:
                crt_rem.append(r[0])
                crt_mod.append(r[1])
                m *= r[1]
        except queue.Empty:
            pass
