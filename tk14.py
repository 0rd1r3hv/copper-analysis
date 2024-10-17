from sage.all import *
from root_methods import groebner
from time import time


# Partial Key Exposure Attacks on RSA: Achieving the Boneh-Durfee Bound


def l_MSBs(x, km, t):
    return max(0, ceil((x - km) / (t + 1)))


# f_MSBs(x, y) = 1 + (k0 + x)(A + y) ≡ 0 (mod e)
def high_leak(N, e, d_high, d_len, A, X, Y, m, kk, s):
    beta = d_len / N.nbits()
    gamma = Integer(X).nbits() / N.nbits()
    k0 = e * d_high // N
    Z = k0 * Y
    PR = ZZ['x, y, z']
    x, y, z = PR.gens()
    Q = PR.quotient(x * y + 1 - z)
    f = z + A * x
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    km = k * m
    shifts = []
    monomials = []
    trans_x = [z ** 0]
    trans_y = [[z ** 0] * max(floor(km + t * m) + 1, floor(km) + 1)] + [[z ** 0] for _ in range(m)]
    for i in range(1, m + 1):
        deg = l_MSBs(i, km, t)
        if deg == 0:
            trans_x.append((1 + x * y) ** i)
        else:
            pol = (x * y) ** (i - deg) * z ** deg
            rem = z ** i - (z - 1) ** (i - deg) * z ** deg
            for j in range(i):
                pol += rem.monomial_coefficient(z ** j) * trans_x[j]
            trans_x.append(pol)
    for u in range(1, m + 1):
        for j in range(1, floor(km + t * u) + 1):
            deg = l_MSBs(u + j, km, t)
            if deg == 0:
                trans_y[u].append((1 + x * y) ** u)
            else:
                pol = (x * y) ** (u - deg) * z ** deg
                rem = z ** u - (z - 1) ** (u - deg) * z ** deg
                for k in range(deg, u):
                    pol += rem.monomial_coefficient(z ** k) * trans_y[k][j]
                trans_y[u].append(pol)
    for u in range(m + 1):
        for i in range(u + 1):
            orig = f ** i
            pol = 0
            for mono in orig.monomials():
                deg_z = mono.degree(z)
                pol += orig.monomial_coefficient(mono) * trans_x[deg_z] * mono // (z ** deg_z)
            pol = x ** (u - i) * (pol.subs(x=k0 + x))
            assert pol.subs(z=(k0 + x) * y + 1) == x ** (u - i) * ((f ** i).subs(x=k0 + x, z=(k0 + x) * y + 1))
            deg = l_MSBs(i, km, t)
            monomials.append(x ** (u - deg) * y ** (i - deg) * z ** deg)
            shifts.append(pol(X * x, Y * y, Z * z) * e ** (m - i))
        for j in range(1, floor(km + t * u) + 1):
            orig = Q(y ** j * f ** u).lift()
            pol = 0
            for mono in orig.monomials():
                deg_y = mono.degree(y)
                deg_z = mono.degree(z)
                if deg_y != 0:
                    pol += orig.monomial_coefficient(mono) * trans_y[deg_z][deg_y] * mono // (z ** deg_z)
                else:
                    pol += orig.monomial_coefficient(mono) * trans_x[deg_z] * mono // (z ** deg_z)
            pol = pol.subs(x=k0 + x)
            assert pol.subs(z=(k0 + x) * y + 1) == (y ** j * f ** u).subs(x=k0 + x, z=(k0 + x) * y + 1)
            deg = l_MSBs(u + j, km, t)
            monomials.append(x ** (u - deg) * y ** (u + j - deg) * z ** deg)
            shifts.append(pol(X * x, Y * y, Z * z) * e ** (m - u))
    scales = [mono(X, Y, Z) for mono in monomials]
    n = len(shifts)
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()
    L = L.LLL(delta=0.75)
    pols = [z - (k0 + x) * y - 1]
    cnt = 0
    for i in range(n):
        pol = 0
        for j in range(n):
            pol += L[i, j] * monomials[j] // scales[j]
        pols.append(pol)
        assert pols[-1](kk - k0, s, kk * s + 1) % (e ** m) == 0
        if pols[-1](kk - k0, s, kk * s + 1) == 0:
            cnt += 1
    print(time() - start)
    print(cnt)
    x0 = groebner(pols, x, X)
    if x0:
        return floor(((k0 + x0) * N) // e)

