from sage.all import Ideal, Integer, QQ, ZZ, Zmod, GF, crt, jacobian, vector, random_prime, Matrix, gcd
from time import time
from random import sample, choice


def groebner(pols, bound_var, max_fails=40, ex_pols=[], variety=False, restrict=False):
    start = time()
    bound, var = bound_var
    R = pols[0].parent()
    varlst = vector(R.gens())
    num = R.ngens()
    p = random_prime((1 << 29) - 1, True, 1 << (29 - 1))
    R = R.change_ring(GF(p), order='degrevlex')
    ZM = Zmod(p)
    fails = 0
    while fails < max_fails:
        if restrict:
            len_selected = num + 1 - len(ex_pols)
        else:
            len_selected = min(pols[0].degree() - len(ex_pols), len(pols))
        selected = ex_pols + sample(pols, len_selected)
        try:
            st = time()
            gb = (R * selected).groebner_basis()
            print(f"groebner basis time: {time() - st}")
            if len(gb) == num:
                if variety:
                    st = time()
                    sols = Ideal(gb).variety()
                    print(f"variety time: {time() - st}")
                    sol = sols[0]
                    v = vector([ZM(sol[v_]) for v_ in varlst])
                else:
                    v = vector([ZM(-g.constant_coefficient()) for g in gb])
                break
            else:
                fails += 1
        except:
            fails += 1
    else:
        print(f"求解失败！用时 {round(time() - start, 3)}s")
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
        print(f"求解成功！用时 {round(time() - start, 3)}s")
        for i, v_ in enumerate(varlst):
            if v_ == var:
                return Integer(v[i])

