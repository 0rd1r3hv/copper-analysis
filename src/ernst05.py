from sage.all import floor, sqrt, ZZ, inverse_mod, PolynomialRing, Rational
from src.misc import solve_copper, assure_coprime, poly_norm, known_d
from src.practical_bounds import ernst05_eq1, ernst05_eq2
# from src.mp import groebner
# from src.root_methods import groebner


# test = [x, y, z]
# a * x + b * y + c * y * z + d = 0
def eq1(coefs, bounds, params, test):
    x, y, z = PolynomialRing(ZZ, "x, y, z", order="lex").gens()
    a, b, c, d = coefs
    f0 = a * x + b * y + c * y * z + d
    X, Y, Z, W = assure_coprime(bounds + [poly_norm(f0, bounds, "inf")], d)
    bounds = [X, Y, Z]
    if None in params:
        print("未指定攻击参数，自动选择攻击参数'm', 't'…")
        m, t = ernst05_eq1(bounds + [W])
    else:
        m, t = params
    n = (X * Y * Z) ** m * Z**t * W
    f = (inverse_mod(d, n) * f0) % n
    monomials = []
    shifts = []
    for i in range(m + 2):
        j = m + 1 - i
        for k in range(j + t + 1):
            monomials.append(x**i * y**j * z**k)
            shifts.append(n * x**i * y**j * z**k)
    monomials2 = []
    shifts2 = []
    for i in range(m + 1):
        for j in range(m - i + 1):
            for k in range(j + t + 1):
                monomials2.append(x**i * y**j * z**k)
                shifts2.append(
                    x**i
                    * y**j
                    * z**k
                    * f
                    * X ** (m - i)
                    * Y ** (m - j)
                    * Z ** (m + t - k)
                )
    monomials += sorted(monomials2, reverse=True)
    shifts += sorted(shifts2, reverse=True)
    return solve_copper(
        shifts,
        min(zip(bounds, [x, y, z])),
        bounds,
        test,
        ex_pols=[f0],
        monomials=monomials,
    )


# test = [x, z, y]
# a * x + b * y + c * y * z + d * z + e = 0
def eq2(coefs, bounds, params, test):
    x, y, z = PolynomialRing(ZZ, "x, y, z", order="lex").gens()
    a, b, c, d, e = coefs
    f0 = a * x + b * y + c * y * z + d * z + e
    X, Y, Z, W = assure_coprime(bounds + [poly_norm(f0, bounds, "inf")], e)
    if None in params:
        print("未指定攻击参数，自动选择攻击参数'm', 't'…")
        m, t = ernst05_eq2(bounds + [W])
    else:
        m, t = params
    n = (X * Y * Z) ** m * Y**t * W
    f = (inverse_mod(e, n) * f0) % n
    shifts = []
    monomials = []
    for i in range(m + 2):
        k = m + 1 - i
        for j in range(m + t + 1 - i + 1):
            monomials.append(x**i * y**j * z**k)
            shifts.append(n * x**i * y**j * z**k)
    for i in range(m + 1):
        j = m + t + 1 - i
        for k in range(m - i + 1):
            monomials.append(x**i * y**j * z**k)
            shifts.append(n * x**i * y**j * z**k)
    monomials2 = []
    shifts2 = []
    for i in range(m + 1):
        for j in range(m + t - i + 1):
            for k in range(m - i + 1):
                monomials2.append(x**i * y**j * z**k)
                shifts2.append(
                    x**i
                    * y**j
                    * z**k
                    * f
                    * X ** (m - i)
                    * Y ** (m + t - j)
                    * Z ** (m - k)
                )
    monomials += sorted(monomials2, reverse=True)
    shifts += sorted(shifts2, reverse=True)
    return solve_copper(
        shifts,
        min(zip(bounds, [x, y, z])),
        bounds,
        test,
        ex_pols=[f0],
        monomials=monomials,
    )


# leaks = [d msb, d lsb], lens = [len d, len msb, len lsb], params = [m, t], test = [p]
def mixed_1(N, e, leaks, lens, params=None, test=None):
    print("开始执行 Ernst, Jochemsz, May, Weger 的 d 高低位混合泄露攻击1…")
    len_p = (N.nbits() + 1) // 2
    s_l = floor(2 * sqrt(N))
    s_r = (1 << len_p) + N // (1 << len_p)
    s = (s_l + s_r) >> 1
    A = N + 1 - s - ((N + 1 - s) % 4)
    len_d, len_m, len_l = lens
    len_N = N.nbits()
    len_e = e.nbits()
    alpha = len_e / len_N
    beta = len_d / len_N
    delta = (len_d - len_m - len_l) / len_N
    kappa = len_l / len_N
    print("密钥参数：")
    print(
        f"α = {Rational(alpha).n(digits=3)}, β = {Rational(beta).n(digits=3)}, δ = {Rational(delta).n(digits=3)}, κ = {Rational(kappa).n(digits=3)}"
    )
    d_m, d_l = leaks
    d_m <<= len_d - len_m
    coefs = [e << len_l, -A, 4, e * (d_m + d_l) - 1]
    bounds = [1 << (len_d - len_m - len_l), 1 << len_d, (s_r - s_l) >> 1]
    if test:
        (p,) = test
        p_q = p + N // p
        d = inverse_mod(e, N + 1 - p_q)
        test = [
            (d - d_m - d_l) >> len_l,
            (e * d - 1) // (N + 1 - p_q),
            (p_q - s - ((N + 1 - s) % 4)) >> 2,
        ]
    res = eq1(coefs, bounds, params, test)
    if res:
        d = d_m + (res << len_l) + d_l
        p, q = known_d(N, e, d)
        print(f"d = {d}\np = {p}\nq = {q}")
        return d


# leaks = [d msb, d lsb], lens = [len d, len msb, len lsb], params = [m, t], test = [p]
def mixed_2(N, e, leaks, lens, params=None, test=None):
    print("开始执行 Ernst, Jochemsz, May, Weger 的 d 高低位混合泄露攻击2…")
    len_p = (N.nbits() + 1) // 2
    s_l = floor(2 * sqrt(N))
    s_r = (1 << len_p) + N // (1 << len_p)
    s = (s_l + s_r) >> 1
    A = N + 1 - s - ((N + 1 - s) % 4)
    len_d, len_m, len_l = lens
    len_N = N.nbits()
    len_e = e.nbits()
    alpha = len_e / len_N
    beta = len_d / len_N
    delta = (len_d - len_m - len_l) / len_N
    kappa = len_l / len_N
    print("密钥参数：")
    print(
        f"α = {Rational(alpha).n(digits=3)}, β = {Rational(beta).n(digits=3)}, δ = {Rational(delta).n(digits=3)}, κ = {Rational(kappa).n(digits=3)}"
    )
    d_m, d_l = leaks
    d_m <<= len_d - len_m
    k0 = e * d_m // N
    coefs = [e << len_l, -A, 4, 4 * k0, e * (d_m + d_l) - k0 * A - 1]
    bounds = [
        1 << (len_d - len_m - len_l),
        1 << (max(len_d - len_m, len_d - len_p)),
        (s_r - s_l) >> 1,
    ]
    if test:
        (p,) = test
        p_q = p + N // p
        d = inverse_mod(e, N + 1 - p_q)
        test = [
            (d - d_m - d_l) >> len_l,
            (e * d - 1) // (N + 1 - p_q) - k0,
            (p_q - s - ((N + 1 - s) % 4)) >> 2,
        ]
    res = eq2(coefs, bounds, params, test)
    if res:
        d = d_m + (res << len_l) + d_l
        p, q = known_d(N, e, d)
        print(f"d = {d}\np = {p}\nq = {q}")
        return d
