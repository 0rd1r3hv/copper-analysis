from sage.all import Ideal, Integer, QQ, ZZ, Zmod, GF, crt, jacobian, vector, random_prime
from time import time
from random import sample


'''
def groebner(pols, bound_var, max_fails=10, N=None, neg=False):
    start = time()
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
    while m < bound and fails < max_fails:
        p = p.next_prime()
        R = R.change_ring(GF(p))
        for i in range(len(pols), num - 1, -1):
            Id = Ideal((R * pols[:i]).groebner_basis())
            if Id.dimension() == 0:
                sols = Id.variety()
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
    if fails < max_fails:
        print(f"groebner success: {time() - start}s")
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
        if neg:
            m = 1
            for mod in crt_mod:
                m *= mod
            return res - m
        else:
            return res
    print(f"groebner failed: {time() - start}s")
'''


def groebner(pols, bound_var, max_fails=10, ex_pols=[]):
    start = time()
    bound, var = bound_var
    R = pols[0].parent()
    varlst = R.gens()
    num = R.ngens()
    p = random_prime((1 << 28) - 1, True, 1 << (27 - 1))
    R = R.change_ring(GF(p))
    ZM = Zmod(p)
    fails = 0
    len_selected = len(pols) // 2
    while fails < max_fails:
        selected = ex_pols + sample(pols, len_selected)
        Id = Ideal((R * selected).groebner_basis())
        if Id.dimension() == 0:
            sols = Id.variety()
            if len(sols) == 1:
                sol = sols[0]
                v = vector([ZM(sol[v_]) for v_ in varlst])
                break
        else:
            fails += 1
    else:
        print('failed')
        return
    f = vector(selected[:num])
    J = jacobian(f, varlst)
    while p < bound:
        p **= 2
        ZM = Zmod(p)
        R = R.change_ring(ZM)
        v = v.change_ring(ZM)
        v -= J.change_ring(R)(list(v)).solve_right(f.change_ring(R)(list(v)))
    if fails < max_fails:
        print(f"groebner success: {time() - start}s")
        for i, v_ in enumerate(varlst):
            if v_ == var:
                return Integer(v[i])


def newton(sys, boundslst, it=20):
    st = time()
    sys_l = len(sys)
    varlst = sys[0].parent().gens()
    jacob = jacobian(sys, varlst)
    for bounds in boundslst:
        v0 = vector(QQ, bounds)
        for i in range(it):
            fv0 = vector(ZZ, [eq.subs(v0) for eq in sys])
            if fv0 == 0:
                print(f"newton done: {time() - st}s")
                return v0
            v0 -= jacob.subs(v0).solve_right(fv0)
            for j in range(sys_l):
                v0[j] = round(v0[j])
        print("newton failed!")
