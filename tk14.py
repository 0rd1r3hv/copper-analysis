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
    Z = k0 * Y
    PR = ZZ['x, y, z']
    x, y, z = PR.gens()
    Q = PR.quotient((k0 + x) * y - z)
    f = z + A * (k0 + x) + 1
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    km = k * m
    shifts = []
    monomials = []
    for u in range(m + 1):
        for i in range(u + 1):
            orig = x ** (u - i) * f ** i
            pol = 0
            for mono in orig.monomials():
                deg_y = mono.degree(y)
                deg_z = mono.degree(z)
                pre = l_MSBs(deg_y + deg_z, km, t)
                pol += orig.monomial_coefficient(mono) * (mono // (z ** pre)).subs(z=(k0 + x) * y) * z ** pre
            pre = l_MSBs(i, km, t)
            monomials.append(x ** (u - pre) * y ** (i - pre) * z ** pre)
            shifts.append(pol(X * x, Y * y, Z * z) * modulus ** (m - i))
        for j in range(1, floor(km + t * u) + 1):
            orig = Q(y ** j * f ** u).lift()
            pol = 0
            for mono in orig.monomials():
                deg_y = mono.degree(y)
                deg_z = mono.degree(z)
                pre = l_MSBs(deg_y + deg_z, km, t)
                pol += orig.monomial_coefficient(mono) * (mono // (z ** pre)).subs(z=(k0 + x) * y) * z ** pre
            pre = l_MSBs(u + j, km, t)
            monomials.append(x ** (u - pre) * y ** (u + j - pre) * z ** pre)
            shifts.append(pol(X * x, Y * y, Z * z) * modulus ** (m - u))
    scales = [mono(X, Y, Z) for mono in monomials]
    n = len(shifts)
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()
    L = L.LLL(delta=0.75)
    pols = [z - (k0 + x) * y]
    for i in range(n):
        pol = 0
        for j in range(n):
            pol += L[i, j] * monomials[j] // scales[j]
        pols.append(pol)
    print(time() - start)
    x0 = groebner(pols, x, X)
    if x0:
        return floor(((k0 + x0) * N) // e)

