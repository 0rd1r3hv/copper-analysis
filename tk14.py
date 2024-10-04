from sage.all import *
from root_methods import groebner
from time import time


# Partial Key Exposure Attacks on RSA: Achieving the Boneh-Durfee Bound


def l_MSBs(x, km, t):
    return max(0, ceil((x - km) / (t + 1)))


# f_MSBs(x, y) = 1 + (k0 + x)(A + y) ≡ 0 (mod e)
def high_leak(N, e, d_high, d_len, A, X, Y, m, modulus=None):
    if modulus is None:
        modulus = e
    beta = d_len / modulus.nbits()
    gamma = Integer(X).nbits() / modulus.nbits()
    k0 = e * d_high // N
    x, y = ZZ['x, y'].gens()
    f = 1 + (k0 + x) * (A + y)
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    shifts = []
    '''
    for u in range(m + 1):
        for i in range(u + 1):
            shifts.append((x ** (u - i) * f ** i)(X * x, Y * y) * modulus ** (m - i))
        for j in range(1, floor(2 * (beta - gamma) * m + (1 + 2 * gamma - 4 * beta) * u)):
            shifts.append((y ** j * f ** u)(X * x, Y * y) * modulus ** (m - u))
    '''
    for u in range(m + 1):
        for i in range(u + 1):
            shifts.append((x ** (u - i) * f ** i)(X * x, Y * y) * modulus ** (m - i))
        for j in range(1, floor(k * m + t * u)):
            shifts.append((y ** j * f ** u)(X * x, Y * y) * modulus ** (m - u))
    monomials = set()
    for shift in shifts:
        monomials.update(shift.monomials())
    monomials = sorted(monomials)
    scales = [mono(X, Y) for mono in monomials]
    h = len(shifts)
    w = len(monomials)
    L = Matrix(ZZ, h, w)
    for i in range(h):
        for j in range(w):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()
    print(h, w)
    L = L.LLL(delta=0.75)
    pols = []
    for i in range(h):
        pols.append(0)
        for j in range(w):
            pols[i] += L[i, j] * monomials[j] // scales[j]
    print(time() - start)
    x0 = groebner(pols, x, X)
    if x0:
        return floor(((k0 + x0) * N) // e)