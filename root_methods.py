from sage.all import *
from time import time

def groebner(pols, var, bound):
    start = time()
    R = pols[0].parent()
    p = Integer(1 << 25)
    m = 1
    fails = 0
    crt_rem = []
    crt_mod = []
    while m < bound and fails < 10:
        p = p.next_prime()
        for i in range(len(pols), 0, -1):
            R = R.change_ring(GF(p))
            I = Ideal((R * pols[:i]).groebner_basis())
            if I.dimension() == 0:
                sols = I.variety()
                sol_var = set()
                sol_var.update([sol[var] for sol in sols])
                if len(sol_var) == 1:
                    crt_rem.append(Integer(sols[0][var]))
                    crt_mod.append(p)
                    m *= p
                    break
        else:
            fails += 1
    if fails < 10:
        print(time() - start)
        return crt(crt_rem, crt_mod)


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
                print(time() - st)
                return v0
            v0 -= jacob.subs(v0).solve_right(fv0)
            for j in range(l):
                v0[j] = round(v0[j])
        print('Failed')