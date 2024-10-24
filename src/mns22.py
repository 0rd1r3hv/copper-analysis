from sage.all import *
from src.practical_bounds import mns22_mixed_kp
from src.misc import solve_copper

# leaks = [kp msb, kp lsb], lens = [len kp, len msb, len lsb]
def mixed_kp(N, k, leaks, lens, params, test=None):
    print("开始 May, Nowakowski, Sarkar 的 kp 混合泄露攻击…")
    kp_m, kp_l = leaks
    len_kp, len_m, len_l = lens
    len_N = N.nbits()
    len_k = k.nbits()
    kp_m <<= len_kp - len_m
    beta = (len_kp - len_k) / len_N
    mu = len_k / len_N
    delta = (len_kp - len_m - len_l) / len_N
    print("密钥参数：")
    print(f"β = {Rational(beta).n(digits=3)}, μ = {Rational(mu).n(digits=3)}, δ = {Rational(delta).n(digits=3)}")
    if None in params:
        print("未指定攻击参数，自动选择攻击参数'm', 't'…")
        m, t = mns22_mixed_kp(beta, mu, delta)
    else:
        m, t = params
    X = 1 << (len_kp - len_m - len_l)
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
    if test:
        p, = test
        x0 = (k * p - kp_m - kp_l) >> len_l
        test = [x0]
    res = solve_copper(shifts, [X, x], [X], test, monomials=monomials)
    return res