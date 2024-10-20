from sage.all import *
from time import time


def groebner(pols, bound_var, max_fails=10, N=None, neg=False):
    start = time()
    print(len(pols))
    bound, var = bound_var
    if bound < 0:
        bound = -bound
        neg = True
    R = pols[0].parent()
    num = R.ngens()
    p = Integer(1 << 27)
    m = 1
    fails = 0
    test_sol = []
    test_prime = 0
    crt_rem = []
    crt_mod = []
    while m < bound and fails < max_fails:
        p = p.next_prime()
        R = R.change_ring(GF(p))
        for i in range(len(pols), num - 1, -1):
            I = Ideal((R * pols[:i]).groebner_basis())
            if I.dimension() == 0:
                sols = I.variety()
                sol_var = set()
                sol_var.update([sol[var] for sol in sols])
                sol_var = list(Integer(e) for e in sol_var)
                if N and len(sol_var) == 2:
                    crt_rem.append(sol_var[:])
                    crt_mod.append(p)
                    m *= p
                    break
                elif len(sol_var) == 1:
                    crt_rem.append(sol_var[0])
                    crt_mod.append(p)
                    m *= p
                    break
        else:
            fails += 1
    print(f"groebner: {time() - start}")
    if fails < max_fails:
        if N:

            def recursive(res, m, d):
                if d == len(crt_rem):
                    if N % res == 0:
                        return res
                    return None
                ret1 = recursive(
                    crt([res, crt_rem[d][0]], [m, crt_mod[d]]), m * crt_mod[d], d + 1
                )
                if ret1:
                    return ret1
                ret2 = recursive(
                    crt([res, crt_rem[d][1]], [m, crt_mod[d]]), m * crt_mod[d], d + 1
                )
                if ret2:
                    return ret2

            res = recursive(crt_rem[0][0], crt_mod[0], 1)
        else:
            res = crt(crt_rem, crt_mod)
        if neg == True:
            m = 1
            for mod in crt_mod:
                m *= mod
            return res - m
        else:
            return res


def newton(sys, boundslst, it=20):
    st = time()
    l = len(sys)
    varlst = sys[0].parent().gens()
    jacob = jacobian(sys, varlst)
    for bounds in boundslst:
        v0 = vector(QQ, bounds)
        for i in range(it):
            fv0 = vector(ZZ, [eq.subs(v0) for eq in sys])
            if fv0 == 0:
                print(f"newton: {time() - st}")
                return v0
            v0 -= jacob.subs(v0).solve_right(fv0)
            for j in range(l):
                v0[j] = round(v0[j])
        print("Newton Failed")
