from sage.all import *
from src.practical_bounds import mns22_mixed_kp
from src.misc import solve_copper


# leaks = [kp msb, kp lsb], lens = [len kp, len msb, len lsb]
def mixed_kp(N, k, leaks, lens, params, len_e=0, raw=False):
    print("开始执行 May, Nowakowski, Sarkar 的 kp 混合泄露攻击…")
    kp_m, kp_l = leaks
    len_kp, len_m, len_l = lens
    len_N = N.nbits()
    len_k = k.nbits()
    if raw == False:
        kp_m <<= len_kp - len_m
    beta = (len_kp - len_k) / len_N
    mu = len_k / len_N
    delta = (len_kp - len_m - len_l - len_e) / len_N
    print("密钥参数：")
    print(f"β = {Rational(beta).n(digits=3)}, μ = {Rational(mu).n(digits=3)}, δ = {Rational(delta).n(digits=3)}")
    if None in params:
        print("未指定攻击参数，自动选择攻击参数'm', 't'…")
        m, t = mns22_mixed_kp(beta, mu, delta)
    else:
        m, t = params
    X = 1 << (len_kp - len_m - len_l - len_e)
    x = ZZ['x'].gen()
    a = kp_m + kp_l
    f = (x + (a * inverse_mod(1 << len_l, k * N))) % (k * N)
    shifts = []
    monomials = []
    for i in range(m + 1):
        monomials.append(x**i)
        shifts.append(f**i * k**t * (k * N) ** (m - i))
    for i in range(1, t + 1):
        monomials.append(x**(m + i))
        shifts.append(f ** (m + i) * k ** (t - i))
    res = solve_copper(shifts, [X, x], [X], None, monomials=monomials)
    return res


# leaks = [dp msb, dq msb], lens = [len dp, len dq, len dp msb, len dq msb]
def small_e_dp_dq_with_msb(N, e, leaks, lens):
    dp_m, dq_m = leaks
    len_dp, len_dq, len_dp_m, len_dq_m = lens
    len_dp_l = len_dp - len_dp_m
    len_dq_l = len_dq - len_dq_m
    len_N = N.nbits()
    len_e = e.nbits()
    dp_m <<= len_dp_l
    dq_m <<= len_dq_l
    kl = ((e ** 2 * dp_m * dq_m) // N) + 1
    s = (1 - kl * (N - 1)) % e
    delt = sqrt(s ** 2 - 4 * kl)
    if delt.is_integer() == False:
        s += e
        delt = sqrt(s ** 2 - 4 * kl)
    k = (s + delt) >> 1
    len_k = k.nbits()
    dp_l = mixed_kp(N, k, [((e * dp_m + k - 1) * inverse_mod(e, k * N)) % (k * N), 0], [len_k + len_N // 2, len_dp_m, 0], [None], len_e=len_e, raw=True)
    if dp_l is None:
        k = (s - delt) >> 1
        len_k = k.nbits()
        dp_l = mixed_kp(N, k, [((e * dp_m + k - 1) * inverse_mod(e, k * N)) % (k * N), 0], [len_k + len_N // 2, len_dp_m, 0], [None], len_e=len_e, raw=True)
    if dp_l:
        dp = dp_m + dp_l
        p = (e * dp - 1) // k + 1
        return p

# leaks = [dp lsb, dq lsb], lens = [len dp, len dq, len low], params = [m], test = [p]
def small_e_dp_dq_with_lsb(N, e, leaks, lens, params, test=None):
    dp_l, dq_l = leaks
    len_dp, len_dq, len_low = lens
    len_N = N.nbits()
    len_e = e.nbits()
    len_k = len_dp + len_e - len_N // 2
    len_l = len_dq + len_e - len_N // 2
    X = 1 << len_k
    Y = 1 << len_l
    if None in params:
        t = 3 * (len_k + len_l) / (len_e + len_low)
        if t >= 2:
            return
        else:
            m = max(1, ceil((t - 1) / (2 - t)))
    else:
        m, = params
    A = -e ** 2 * dp_l * dq_l + e * dp_l + e * dq_l - 1
    eM = e << len_low
    x, y = ZZ['x, y'].gens()
    g = gcd(N - 1, eM)
    f = (((N - 1) * x * y - (e * dq_l - 1) * x - (e * dp_l - 1) * y + A) * inverse_mod((N - 1) // g, eM // g)) % eM
    shifts = []
    monomials = []
    for i in range(m + 1):
        for j in range(m + 1):
            monomials.append(x ** i * y ** j)
            if i >= j:
                shifts.append(x ** (i - j) * f ** j * eM ** (m - j))
            else:
                shifts.append(y ** (j - i) * f ** i * eM ** (m - i))
    if test:
        p, = test
        q = N // p
        dp = inverse_mod(e, p - 1)
        dq = inverse_mod(e, q - 1)
        k = (e * dp - 1) // (p - 1)
        ll = (e * dq - 1) // (q - 1)
        test = [k, ll]
    k = solve_copper(shifts, [X, x], [X, Y], test, monomials=monomials, restrict=True)
    if k:
        dp_m = mixed_kp(N, k, [0, ((e * dp_l + k - 1) * inverse_mod(e, k * N)) % (k * N)], [len_k + len_N // 2, 0, len_low], [None], len_e=len_e)
        if dp_m:
            dp = (dp_m << len_low) + dp_l
            p = (e * dp - 1) // k + 1
            return p