from sage.all import Matrix, ZZ, inverse_mod, gcd, ceil, floor
from src.mp import groebner
from src.practical_bounds import tlp17_large_e, tlp17_small_e, tlp17_small_dp_dq
from src.misc import solve_copper

# from src.root_methods import groebner
from time import time
from src.fplll_fmt import fplll_fmt, fplll_read
import subprocess
# Small CRT-Exponent RSA Revisited

# lens = [len_p, len_dq], params = [m, t], test = [p]
def large_e(N, e, lens, params, test=None):
    len_p, len_dq = lens
    len_N = N.nbits()
    len_e = e.nbits()
    alpha = len_e / len_N
    beta = len_p / len_N
    delta = len_dq / len_N
    if None in params:
        m, t = tlp17_large_e(alpha, beta, delta)
    else:
        m, t = params
    PR = ZZ["xp, xq, yp, yq"]
    xp, xq, yp, yq = PR.gens()
    Q = PR.quotient(N - yp * yq)
    tq = (1 - beta - delta) / (1 - beta)
    X = 1 << (len_e + len_dq + len_p - len_N)
    Yp = 1 << len_p
    Yq = 1 << (len_N - len_p)
    fp = N + xp * (N - yp)
    shifts = []
    monomials = []
    for i in range(m + 1):
        for j in range(0, m - i + 1):
            monomials.append(xp ** (i + j) * yp**i)
            shifts.append(xp**j * fp**i * e ** (m - i))
    for i in range(m + 1):
        for j in range(1, t + 1):
            monomials.append(xp**i * yp ** (i + j))
            shifts.append(yp**j * fp**i * e ** (m - i))
    for i in range(1, m + 1):
        for j in range(1, floor(tq * i) + 1):
            orig = Q((N * xq - xp * yp) ** (i - j) * (xq * yq - xp) ** j).lift()
            pt1 = orig.subs(yq=0)
            pt2 = orig - pt1
            trans = pt1.subs(xq=xp + 1) + pt2.subs(xp=xq - 1)
            monomials.append(xq**i * yq**j)
            times = trans.monomial_coefficient(monomials[-1]).valuation(N)
            inv = inverse_mod(N**times, e**i)
            shifts.append(((trans * inv) % (e**i)) * e ** (m - i))
    if test:
        (p,) = test
        q = N // p
        dq = inverse_mod(e, q - 1)
        ell = (e * dq - 1) // (q - 1)
        test = [ell - 1, ell, p, q]
    res = solve_copper(shifts, [Yp, yp], [X, X, Yp, Yq], test, ex_pols=[N - yp * yq, xp - xq + 1], monomials=monomials, N=N)
    return res


# lens = [len_p, len_dq], params = [m], test = [p]
def small_e(N, e, lens, params, test=None):
    len_p, len_dq = lens
    len_N = N.nbits()
    len_e = e.nbits()
    alpha = len_e / len_N
    beta = len_p / len_N
    delta = len_dq / len_N
    if None in params:
        m = tlp17_small_e(alpha, beta, delta)
    else:
        m = params
    PR = ZZ["xp, xq, yp, yq"]
    xp, xq, yp, yq = PR.gens()
    Q = PR.quotient(N - yp * yq)
    ll = (1 - beta - delta) / beta
    t = (1 - beta - delta) / (1 - beta)
    X = 1 << (len_e + len_dq + len_p - len_N)
    Yp = 1 << len_p
    Yq = 1 << (len_N - len_p)
    shifts = []
    monomials = []
    for i in range(m + 1):
        for j in range(m - i + 1):
            if i == 0 or ceil(ll * i) - ceil(ll * (i - 1)) == 1:
                monomials.append(xp ** (i + j) * yp ** ceil(ll * i))
            else:
                monomials.append(xq ** (i + j) * yq ** floor((1 - ll) * i))
            if i != 0:
                orig = Q(
                    xp**j
                    * (N * xq - xp * yp) ** ceil(ll * i)
                    * (xq * yq - xp) ** floor((1 - ll) * i)
                ).lift()
                pt1 = orig.subs(yq=0)
                pt2 = orig - pt1
                trans = pt1.subs(xq=xp + 1) + pt2.subs(xp=xq - 1)
                times = trans.monomial_coefficient(monomials[-1]).valuation(N)
                inv = inverse_mod(N**times, e**i)
                shifts.append(((trans * inv) % (e**i))* e ** (m - i))
            else:
                shifts.append(xp ** j * e**m)
    for i in range(1, m + 1):
        for j in range(1, ceil(t * i) - floor((1 - ll) * i) + 1):
            orig = Q(
                yq**j
                * (N * xq - xp * yp) ** ceil(ll * i)
                * (xq * yq - xp) ** floor((1 - ll) * i)
            ).lift()
            pt1 = orig.subs(yq=0)
            pt2 = orig - pt1
            trans = pt1.subs(xq=xp + 1) + pt2.subs(xp=xq - 1)
            monomials.append(xq**i * yq ** (floor((1 - ll) * i + j)))
            times = trans.monomial_coefficient(monomials[-1]).valuation(N)
            inv = inverse_mod(N**times, e**i)
            shifts.append(
                ((trans * inv) % (e**i)) * e ** (m - i))
    if test:
        (p,) = test
        q = N // p
        dq = inverse_mod(e, q - 1)
        ell = (e * dq - 1) // (q - 1)
        test = [ell - 1, ell, p, q]
    res = solve_copper(shifts, [Yp, yp], [X, X, Yp, Yq], test, ex_pols=[N - yp * yq, xp - xq + 1], monomials=monomials, N=N)
    return res


# lens = [len_dp, len_dq], params = [m], test = [p]
def small_dp_dq(N, e, lens, params, test=None):
    len_dp, len_dq = lens
    len_N = N.nbits()
    len_e = e.nbits()
    alpha = len_e / len_N
    delta1 = len_dp / len_N
    delta2 = len_dq / len_N
    delta = max(delta1, delta2)
    if None in params:
        m = tlp17_small_dp_dq(alpha, delta)
    else:
        (m,) = params
    PR = ZZ["xp1, xq1, xp2, xq2, yp, yq"]
    xp1, xq1, xp2, xq2, yp, yq = PR.gens()
    Q = PR.quotient(N - yp * yq)
    t = 1 - 2 * delta
    Xp = 1 << (len_e + len_dp - len_N // 2)
    Xq = 1 << (len_e + len_dq - len_N // 2)
    Y = 1 << (len_N // 2)
    bounds = [Xq, Xq, Xp, Xp, Y, Y]
    fp1 = N * xq1 - xp1 * yp
    fp2 = xp2 * yp - xq2
    h = N * xp2 * xq1 - xp1 * xq2
    shifts = []
    monomials = []
    indices_1 = []
    indices_2 = []
    indices_3 = []
    for i1 in range(m // 2 + 1):
        for i2 in range(m // 2 + 1):
            for u in range(min(m // 2 - i1, m // 2 - i2) + 1):
                indices_1.append([i1, i2, 0, 0, u])
    for i1 in range(m // 2):
        for i2 in range(1, m // 2 + 1):
            for u in range(min(m // 2 - i1 - 1, m // 2 - i2) + 1):
                indices_1.append([i1, i2, 1, 0, u])
    for i1 in range(m // 2 + 1):
        for j1 in range(1, m // 2 - i1 + 1):
            for u in range(m // 2 - i1 - j1 + 1):
                indices_1.append([i1, 0, j1, 0, u])
    for i2 in range(m // 2 + 1):
        for j2 in range(1, m // 2 - i2 + 1):
            for u in range(m // 2 - i2 - j2 + 1):
                indices_1.append([0, i2, 0, j2, u])
    indices_1 = sorted(indices_1, key=lambda e: (e[0] + e[1], e[4], e[2], e[3]))
    for i1 in range(m // 2 + 1):
        for i2 in range(m // 2 + 1):
            for j1 in range(1, floor(t * (i1 + i2)) - (i1 + i2 + 1) // 2 + 1):
                indices_2.append([i1, i2, j1])
    indices_2 = sorted(indices_2, key=lambda e: (e[0] + e[1], e[2]))
    for i1 in range(m // 2 + 1):
        for i2 in range(m // 2 + 1):
            for j2 in range(1, floor(t * (i1 + i2)) - (i1 + i2) // 2 + 1):
                indices_3.append([i1, i2, j2])
    indices_3 = sorted(indices_3, key=lambda e: (e[0] + e[1], e[2]))
    for i1, i2, j1, j2, u in indices_1:
        if (i1 + i2) % 2 == 1:
            monomials.append(
                xp1 ** (i1 + j1 + u) * xp2 ** (i2 + j2 + u) * yp ** ((i1 + i2 + 1) // 2)
            )
        else:
            monomials.append(
                xq1 ** (i1 + j1 + u) * xq2 ** (i2 + j2 + u) * yq ** ((i1 + i2 + 1) // 2)
            )
        if i1 + i2 + u != 0:
            orig = (
                Q(xp1**j1 * xp2**j2 * yq ** ((i1 + i2) // 2) * fp1**i1 * fp2**i2).lift()
                * h**u
            )
            pt2 = orig.subs(yp=0)
            pt1 = orig - pt2
            pol = pt1.subs(xq1=xp1 + 1, xq2=xp2 - 1) + pt2.subs(
                xp1=xq1 - 1, xp2=xq2 + 1
            )
            coef = pol.monomial_coefficient(monomials[-1])
            if abs(coef) != 1:
                g = gcd(abs(coef), e ** (i1 + i2 + u))
                if coef < 0:
                    pol = -pol
                pol = (pol * inverse_mod(abs(coef) // g, (e ** (i1 + i2 + u)) // g)) % (
                    e ** (i1 + i2 + u)
                )
        else:
            pol = monomials[-1]
        shifts.append(pol * e ** (m - i1 - i2 - u))
    for i1, i2, j1 in indices_2:
        monomials.append(xp1**i1 * xp2**i2 * yp ** ((i1 + i2 + 1) // 2 + j1))
        if i1 + i2 != 0:
            orig = Q(yq ** ((i1 + i2) // 2 - j1) * fp1**i1 * fp2**i2).lift()
            pt2 = orig.subs(yp=0)
            pt1 = orig - pt2
            pol = pt1.subs(xq1=xp1 + 1, xq2=xp2 - 1) + pt2.subs(
                xp1=xq1 - 1, xp2=xq2 + 1
            )
            coef = pol.monomial_coefficient(monomials[-1])
            if abs(coef) != 1:
                g = gcd(abs(coef), e ** (i1 + i2))
                if coef < 0:
                    pol = -pol
                pol = (pol * inverse_mod(abs(coef) // g, (e ** (i1 + i2)) // g)) % (
                    e ** (i1 + i2)
                )
        else:
            pol = monomials[-1]
        shifts.append(pol * e ** (m - i1 - i2))
    for i1, i2, j2 in indices_3:
        monomials.append(xq1**i1 * xq2**i2 * yq ** ((i1 + i2) // 2 + j2))
        if i1 + i2 != 0:
            orig = Q(yq ** ((i1 + i2) // 2 + j2) * fp1**i1 * fp2**i2).lift()
            pt2 = orig.subs(yp=0)
            pt1 = orig - pt2
            pol = pt1.subs(xq1=xp1 + 1, xq2=xp2 - 1) + pt2.subs(
                xp1=xq1 - 1, xp2=xq2 + 1
            )
            coef = pol.monomial_coefficient(monomials[-1])
            if abs(coef) != 1:
                g = gcd(abs(coef), e ** (i1 + i2))
                if coef < 0:
                    pol = -pol
                pol = (pol * inverse_mod(abs(coef) // g, (e ** (i1 + i2)) // g)) % (
                    e ** (i1 + i2)
                )
        else:
            pol = monomials[-1]
        # shifts.append(pol(X * xp1, X * xq1, X * xp2, X * xq2, Yp * yp, Yq * yq) * e ** (m - i1 - i2))
        shifts.append(pol * e ** (m - i1 - i2))
    if test:
        (p,) = test
        q = N // p
        dp = inverse_mod(e, p - 1)
        dq = inverse_mod(e, q - 1)
        k = (e * dp - 1) // (p - 1)
        ell = (e * dq - 1) // (q - 1)
        test = [ell - 1, ell, k, k - 1, p, q]
    res = solve_copper(
        shifts,
        [Y, yp],
        bounds,
        test,
        ex_pols=[N - yp * yq, xp1 - xq1 + 1, xp2 - xq2 - 1],
        monomials=monomials,
        N=N,
        variety=True,
        restrict=True
    )
    return res