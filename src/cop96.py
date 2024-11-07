from sage.all import *
from src.practical_bounds import cop96_univariate
from src.misc import solve_copper


def univariate(f, len_X, len_p, N, params):
    len_N = N.nbits()
    delta = len_X / len_N
    beta = len_p / len_N
    X = 1 << len_X
    x = f.parent().gen()
    deg = f.degree()
    if None in params:
        m, t = cop96_univariate(beta, delta, deg)
    else:
        m, t = params
    f = (f * inverse_mod(f.monomial_coefficient(x ** deg), N)) % N
    shifts = []
    monomials = []
    for i in range(m):
        for j in range(deg):
            monomials.append(x ** (i * deg + j))
            shifts.append(x ** j * f ** i * N ** (m - i))
    for i in range(t + 1):
        monomials.append(x ** (m * deg + i))
        shifts.append(x ** i * f ** m)
    res = solve_copper(shifts, [X, x], [X], monomials=monomials)
    return res


# lens = [len X], params = [m]
def cop(f, N, lens, params, test=None):
    len_X, = lens
    PR = ZZ['x']
    f = PR(f)
    return univariate(f, len_X, N.nbits(), N, params + [0])


# lens = [len X, len p], params = [m, t]
def hg(f, N, lens, params):
    len_X, len_p = lens
    PR = ZZ['x']
    f = PR(f)
    return univariate(f, len_X, len_p, N, params)