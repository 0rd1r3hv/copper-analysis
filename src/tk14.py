from sage.all import ceil, floor, inverse_mod, ZZ, Rational
from src.misc import reduce_varsize, solve_copper
from src.practical_bounds import tk14_msb_1, tk14_lsb, tk14_mixed
# from src.root_method import groebner
# from src.mp import groebner
# from time import time
# from src.fplll_fmt import fplll_fmt, fplll_read


# Partial Key Exposure Attacks on RSA: Achieving the Boneh-Durfee Bound


def l_MSBs(x, km, t):
    return max(0, ceil((x - km) / (t + 1)))


def l_LSBs(x, km, t):
    return max(0, ceil((x - km) / t))


# leaks = [d msb], lens = [len d, len msb], params = [m], test = [p]
def msb_1(N, e, leaks, lens, params, test=None):
    print("开始执行 Takayasu, Kunihiro 的 d 纯高位泄露攻击…")
    (d_m,) = leaks
    len_d, len_m = lens
    d_m <<= len_d - len_m
    k0 = e * d_m // N
    X = 1 << (len_d - len_m)
    A, Y = reduce_varsize(N)
    Z = (k0 + X) * Y
    bounds = [X, Y, Z]
    beta = len_d / N.nbits()
    gamma = (len_d - len_m) / N.nbits()
    print("密钥参数：")
    print(f"β = {beta.n(digits=3)}, γ = {gamma.n(digits=3)}")
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    print("有益格基参数：")
    print(f"κ = {k.n(digits=3)}, τ = {t.n(digits=3)}")
    if None in params:
        print("未指定攻击参数，自动选择攻击参数'm'…")
        m = tk14_msb_1(beta, gamma)
    else:
        (m,) = params
    km = k * m
    PR = ZZ["x, y, z"]
    x, y, z = PR.gens()
    Q = PR.quotient(x * y + 1 - z)
    f = z + A * x
    shifts = []
    monomials = []
    trans_x = [z**0]
    trans_y = [[z**0] * max(floor(km + t * m) + 1, floor(km) + 1)] + [
        [z**0] for _ in range(m)
    ]
    for i in range(1, m + 1):
        deg = l_MSBs(i, km, t)
        if deg == 0:
            trans_x.append((1 + x * y) ** i)
        else:
            pol = (x * y) ** (i - deg) * z**deg
            rem = z**i - (z - 1) ** (i - deg) * z**deg
            for d in range(deg, i):
                pol += rem.monomial_coefficient(z**d) * trans_x[d]
            trans_x.append(pol)
    for u in range(1, m + 1):
        for j in range(1, floor(km + t * u) + 1):
            deg = l_MSBs(u + j, km, t)
            if deg == 0:
                trans_y[u].append((1 + x * y) ** u)
            else:
                pol = (x * y) ** (u - deg) * z**deg
                rem = z**u - (z - 1) ** (u - deg) * z**deg
                for d in range(deg, u):
                    pol += rem.monomial_coefficient(z**d) * trans_y[d][j]
                trans_y[u].append(pol)
    for u in range(m + 1):
        for i in range(u + 1):
            orig = f**i
            pol = 0
            for mono in orig.monomials():
                deg_z = mono.degree(z)
                pol += (
                    orig.monomial_coefficient(mono)
                    * trans_x[deg_z]
                    * mono
                    // (z**deg_z)
                )
            pol = x ** (u - i) * (pol.subs(x=k0 + x))
            assert pol.subs(z=(k0 + x) * y + 1) == x ** (u - i) * (
                (f**i).subs(x=k0 + x, z=(k0 + x) * y + 1)
            )
            deg = l_MSBs(i, km, t)
            monomials.append(x ** (u - deg) * y ** (i - deg) * z**deg)
            shifts.append(pol * e ** (m - i))
        for j in range(1, floor(km + t * u) + 1):
            orig = Q(y**j * f**u).lift()
            pol = 0
            for mono in orig.monomials():
                deg_y = mono.degree(y)
                deg_z = mono.degree(z)
                if deg_y != 0:
                    pol += (
                        orig.monomial_coefficient(mono)
                        * trans_y[deg_z][deg_y]
                        * mono
                        // (z**deg_z)
                    )
                else:
                    pol += (
                        orig.monomial_coefficient(mono)
                        * trans_x[deg_z]
                        * mono
                        // (z**deg_z)
                    )
            pol = pol.subs(x=k0 + x)
            assert pol.subs(z=(k0 + x) * y + 1) == (y**j * f**u).subs(
                x=k0 + x, z=(k0 + x) * y + 1
            )
            deg = l_MSBs(u + j, km, t)
            monomials.append(x ** (u - deg) * y ** (u + j - deg) * z**deg)
            shifts.append(pol * e ** (m - u))
    if test:
        (p,) = test
        x0 = (e * inverse_mod(e, N + 1 - p - N // p) - 1) // (N + 1 - p - N // p) - k0
        y0 = -(p + N // p - (N + 1 - A))
        test = [x0, y0, (k0 + x0) * y0 + 1]
    res = solve_copper(
        shifts,
        [X, x],
        bounds,
        test,
        ex_pols=[z - (k0 + x) * y - 1],
        monomials=monomials,
    )
    if res:
        return ((k0 + res) * N) // e


# leaks = [d lsb], lens = [len d, len lsb], params = [m], test = [p]
def lsb(N, e, leaks, lens, params, test=None):
    print("开始执行 Takayasu, Kunihiro 的 d 纯低位泄露攻击…")
    (d_l,) = leaks
    len_d, len_l = lens
    X = 1 << len_d
    A, Y = reduce_varsize(N)
    Z = X * Y
    bounds = [X, Y, Z]
    beta = len_d / N.nbits()
    gamma = (len_d - len_l) / N.nbits()
    print("密钥参数：")
    print(f"β = {Rational(beta).n(digits=3)}, γ = {Rational(gamma).n(digits=3)}")
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    print("有益格基参数：")
    print(f"κ = {Rational(k).n(digits=3)}, τ = {Rational(t).n(digits=3)}")
    if None in params:
        print("未指定参数，自动选择参数'm'…")
        m = tk14_lsb(beta, gamma)
    else:
        (m,) = params
    km = k * m
    PR = ZZ["x, y, z"]
    x, y, z = PR.gens()
    Q = PR.quotient(x * y + 1 - z)
    f1 = z + A * x
    f2 = x * (A + y) + 1 - e * d_l
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    km = k * m
    M = 1 << len_l
    eM = e * M
    shifts = []
    monomials = []
    trans_y = [[z**0] * (floor(km + t * m) + 1)] + [[z**0] for _ in range(m)]
    for u in range(1, m + 1):
        for j in range(1, floor(km + t * u) + 1):
            deg = l_LSBs(j, km, t)
            if deg == 0:
                trans_y[u].append((1 + x * y) ** u)
            else:
                pol = (x * y) ** (u - deg) * z**deg
                rem = z**u - (z - 1) ** (u - deg) * z**deg
                for k in range(deg, u):
                    pol += rem.monomial_coefficient(z**k) * trans_y[k][j]
                trans_y[u].append(pol)
    for u in range(m + 1):
        for i in range(u + 1):
            monomials.append(x**u * y**i)
            shifts.append(x ** (u - i) * f2**i * eM ** (m - i))
        for j in range(1, floor(km + t * u) + 1):
            deg = l_LSBs(j, km, t)
            orig = Q(y**j * f1**deg * f2 ** (u - deg)).lift()
            pol = 0
            for mono in orig.monomials():
                deg_y = mono.degree(y)
                deg_z = mono.degree(z)
                if deg_y != 0:
                    pol += (
                        orig.monomial_coefficient(mono)
                        * trans_y[deg_z][deg_y]
                        * mono
                        // (z**deg_z)
                    )
                else:
                    pol += orig.monomial_coefficient(mono) * mono.subs(z=x * y + 1)
            monomials.append(x ** (u - deg) * y ** (u + j - deg) * z**deg)
            shifts.append(pol * eM ** (m - u) * M**deg)
    if test:
        (p,) = test
        x0 = (e * inverse_mod(e, N + 1 - p - N // p) - 1) // (N + 1 - p - N // p)
        y0 = -(p + N // p - (N + 1 - A))
        test = [x0, y0, x0 * y0 + 1]
    res = solve_copper(
        shifts, [X, x], bounds, test, ex_pols=[z - x * y - 1], monomials=monomials
    )
    if res:
        return (res * N) // e


# leaks = [d msb, d lsb], lens = [len d, len msb, len lsb], params = [m, t]
def mixed(N, e, leaks, lens, params, test=None, brute=False, triangluarize=True):
    print("开始执行 Takayasu, Kunihiro 的 d 高低位混合泄露攻击…")
    d_m, d_l = leaks
    len_d, len_m, len_l = lens
    d_m <<= len_d - len_m
    k0 = e * d_m // N
    X = 1 << (len_d - len_m)
    A, Y = reduce_varsize(N)
    W = k0 + X
    M = 1 << len_l
    eM = e * M
    bounds = [W, X, Y]
    beta = len_d / N.nbits()
    delta = (len_d - len_m - len_l) / N.nbits()
    kappa = len_l / N.nbits()
    print("密钥参数：")
    print(
        f"β = {Rational(beta).n(digits=3)}, δ = {Rational(delta).n(digits=3)}, κ = {Rational(kappa).n(digits=3)}"
    )
    if None in params:
        print("未指定攻击参数，自动选择攻击参数'm', 't'…")
        m, t = tk14_mixed(beta, delta)
    else:
        m, t = params
    if brute:
        PR = ZZ["x, y"]
        x, y = PR.gens()
        f = 1 - e * d_l + (k0 + x) * (A - Y + y)
        shifts = []
        for u in range(m + 1):
            for i in range(u + 1):
                shifts.append(x ** (u - i) * f**i * eM ** (m - i))
            for j in range(1, t + 1):
                shifts.append(y**j * f**u * eM ** (m - u))
        if test:
            (p,) = test
            x0 = (e * inverse_mod(e, N + 1 - p - N // p) - 1) // (
                N + 1 - p - N // p
            ) - k0
            y0 = -(p + N // p - (N + 1 - A))
            test = [x0, y0]
        res = solve_copper(shifts, [X, x], [X, Y], test, brute=[Y, y])
    else:
        PR = ZZ["w, x, y"]
        w, x, y = PR.gens()
        f = 1 - e * d_l + w * (A + y)
        shifts = []
        monomials = []
        for u in range(m + 1):
            for i in range(u + 1):
                deg = max(0, i - t)
                monomials.append(w**deg * x ** (u - deg) * y**i)
                orig = x ** (u - i) * f**i
                pol = 0
                for mono in orig.monomials():
                    deg = max(0, mono.degree(y) - t)
                    pol += (
                        orig.monomial_coefficient(mono)
                        * (mono // (w**deg)).subs(w=k0 + x)
                        * (w**deg)
                    )
                shifts.append(pol * eM ** (m - i))
            for j in range(1, t + 1):
                deg = max(0, u + j - t)
                monomials.append(w**deg * x ** (u - deg) * y ** (u + j))
                orig = y**j * f**u
                pol = 0
                for mono in orig.monomials():
                    deg = max(0, mono.degree(y) - t)
                    pol += (
                        orig.monomial_coefficient(mono)
                        * (mono // (w**deg)).subs(w=k0 + x)
                        * (w**deg)
                    )
                shifts.append(pol * eM ** (m - u))
        if test:
            (p,) = test
            x0 = (e * inverse_mod(e, N + 1 - p - N // p) - 1) // (
                N + 1 - p - N // p
            ) - k0
            y0 = -(p + N // p - (N + 1 - A))
            test = [k0 + x0, x0, y0]
        if not triangluarize:
            monomials = None
        res = solve_copper(
            shifts, [X, x], bounds, test, ex_pols=[w - k0 - x], monomials=monomials
        )
    if res:
        return ((k0 + res) * N) // e
