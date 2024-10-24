from sage.all import gcd, inverse_mod, ZZ, floor, Rational
from sage.all import gcd, inverse_mod, ZZ, floor, Rational

# from src.mp import groebner
# from src.root_methods import groebner
# from src.fplll_fmt import fplll_fmt, fplll_read
from src.practical_bounds import mns21_dp_dq_with_lsb
from src.misc import solve_copper


def transform(PR, Q, pol, mono, mod, i):
    xp, xq, _, _, zp, zq = PR.gens()
    lifted = Q(pol).lift()
    pt1 = lifted.subs(yp=0)
    pt2 = lifted - pt1
    p = pt1.subs(xp=xq + 1, zp=zq - 1) + pt2.subs(xq=xp - 1, zq=zp + 1)
    if i == 0:
        return p
    mod = mod**i
    coef = p.monomial_coefficient(mono)
    if coef < 0:
        p = -p
    g = gcd(coef, mod)
    return (p * inverse_mod(abs(coef) // g, mod // g)) % mod


# leaks = [dp_l, dq_l], lens = [len_dp, len_dq, len_l], params = [m, s], test = [p]
def dp_dq_with_lsb(N, e, leaks, lens, params, test=None):
    print("开始 May, Nowakowski, Sarkar 的 dp,dq 纯低位泄露攻击…")
    dp_l, dq_l = leaks
    len_dp, len_dq, len_l = lens
    len_N = N.nbits()
    len_e = e.nbits()
    alpha = len_e / len_N
    delta1 = len_dp / len_N
    delta2 = len_dq / len_N
    leak = len_l / len_N
    print("密钥参数：")
    print(f"α = {Rational(alpha).n(digits=3)}, δ1 = {delta1.n(digits=3)}, δ2 = {delta2.n(digits=3)}, κ = {leak.n(digits=3)}")
    print(f"α = {Rational(alpha).n(digits=3)}, δ1 = {delta1.n(digits=3)}, δ2 = {delta2.n(digits=3)}, κ = {leak.n(digits=3)}")
    if None in params:
        print("未指定攻击参数，自动选择攻击参数'm', 's'…")
        m, thres = mns21_dp_dq_with_lsb(alpha, delta1, delta2, leak)
    else:
        m, thres = params
    M = 1 << len_l
    PR = ZZ["xp, xq, yp, yq, zp, zq"]
    xp, xq, yp, yq, zp, zq = PR.gens()
    Q = PR.quotient(N - yp * yq)
    X = 1 << (len_e + len_dp - len_N // 2)
    Y = 1 << (len_N // 2)
    Z = 1 << (len_e + len_dq - len_N // 2)
    bounds = [X, X, Y, Y, Z, Z]
    t = max(1 - 2 * max(delta1, delta2), 1 / 2)
    f_b = xp * yp - xq - e * dp_l
    g_b = yp * zp - N * zq + e * dq_l * yp
    h_b = N * xp * zq - xq * zp - e**2 * dp_l * dq_l - e * dp_l * zp - e * dq_l * xq
    f = M * (xp * yp - xq)
    g = M * (yp * zp - N * zq)
    h = M * (N * xp * zq - xq * zp)
    eM = e * M
    shifts = []
    monomials = []
    order = []
    for c in range(m + 1):
        for a in range(m + 1):
            b = 0
            while (b + 1) // 2 <= thres:
                if b <= a + c:
                    if a <= c and b <= c - a:
                        ef = 0
                        eg = b
                        eh = a
                        ex = 0
                        ez = -a - b + c
                    elif a > c and b < a - c:
                        ef = b
                        eg = 0
                        eh = c
                        ex = a - b - c
                        ez = 0
                    elif (a + b + c) % 2 == 0:
                        ef = (a + b - c) // 2
                        eg = (-a + b + c) // 2
                        eh = (a - b + c) // 2
                        ex = 0
                        ez = 0
                    else:
                        ef = (a + b - c + 1) // 2
                        eg = (-a + b + c - 1) // 2
                        eh = (a - b + c - 1) // 2
                        ex = 0
                        ez = 1
                else:
                    ef = a
                    eg = c
                    eh = 0
                    ex = 0
                    ez = 0
                deg = ef + eg + eh
                p = f_b**ef * g_b**eg * h_b**eh * xp**ex * zp**ez
                if b <= a + c:
                    p *= yq ** (b // 2)
                elif b % 2 == 0:
                    p *= yq ** ((a + c) // 2 + (b - a - c + 1) // 2)
                else:
                    p *= yq ** ((a + c) // 2) * yp ** ((b - a - c + 1) // 2)
                if b % 2 == 0:
                    monomials.append(xq**a * yq ** ((b + 1) // 2) * zq**c)
                else:
                    monomials.append(xp**a * yp ** ((b + 1) // 2) * zp**c)
                shifts.append(
                    transform(PR, Q, p, monomials[-1], eM, deg) * (eM ** (2 * m - deg))
                )
                order.append((c, a, b))
                b += 1
    for c in range(m + 1):
        for a in range(m + 1):
            for b in range(a + c + 1):
                if (b + 1) // 2 > thres or b == a + c:
                    if a <= c and b <= c - a:
                        ef = 0
                        eg = b
                        eh = a
                        ex = 0
                        ez = -a - b + c
                    elif a > c and b < a - c:
                        ef = b
                        eg = 0
                        eh = c
                        ex = a - b - c
                        ez = 0
                    elif (a + b + c) % 2 == 0:
                        ef = (a + b - c) // 2
                        eg = (-a + b + c) // 2
                        eh = (a - b + c) // 2
                        ex = 0
                        ez = 0
                    else:
                        ef = (a + b - c + 1) // 2
                        eg = (-a + b + c - 1) // 2
                        eh = (a - b + c - 1) // 2
                        ex = 0
                        ez = 1
                    deg = ef + eg + eh
                    p = f**ef * g**eg * h**eh * xp**ex * zp**ez * yq ** (b // 2)
                    if (b + 1) // 2 > thres:
                        if b % 2 == 0:
                            monomials.append(xq**a * yq ** ((b + 1) // 2) * zq**c)
                        else:
                            monomials.append(xp**a * yp ** ((b + 1) // 2) * zp**c)
                        shifts.append(
                            transform(PR, Q, p, monomials[-1], eM, deg)
                            * (eM ** (2 * m - deg))
                        )
                        order.append((c, a, b))
                    if b == a + c:
                        mono = xq**a * yq ** (b // 2) * zq**c
                        for i in range(
                            max(1, thres - b // 2 + 1), floor(t * b - b // 2) + 1
                        ):
                            monomials.append(mono * yq**i)
                            shifts.append(
                                transform(PR, Q, p * yq**i, monomials[-1], eM, deg)
                                * (eM ** (2 * m - deg))
                            )
                            order.append((c, a, b))
                        mono = xp**a * yp ** ((b + 1) // 2) * zp**c
                        for i in range(
                            max(1, thres - (b + 1) // 2 + 1),
                            floor(t * b - (b + 1) // 2) + 1,
                        ):
                            monomials.append(mono * yp**i)
                            shifts.append(
                                transform(PR, Q, p * yp**i, monomials[-1], eM, deg)
                                * (eM ** (2 * m - deg))
                            )
                            order.append((c, a, b))
    n = len(shifts)
    ords_monos_shifts = [(order[i], monomials[i], shifts[i]) for i in range(n)]
    ords_monos_shifts.sort(key=lambda e: (e[0][0], e[0][1], e[0][2]))
    monomials = [_[1] for _ in ords_monos_shifts]
    shifts = [_[2] for _ in ords_monos_shifts]
    if test:
        (p,) = test
        q = N // p
        dp = inverse_mod(e, p - 1)
        dq = inverse_mod(e, q - 1)
        k = (e * dp - 1) // (p - 1)
        ell = (e * dq - 1) // (q - 1)
        test = [k, k - 1, p, q, ell - 1, ell]
    return solve_copper(
        shifts,
        [Y, yp],
        bounds,
        test,
        ex_pols=[N - yp * yq, xp - xq - 1, zp - zq + 1],
        monomials=monomials,
        N=N,
    )
