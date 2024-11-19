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
    print("开始执行 May, Nowakowski, Sarkar 的 dp,dq 高位泄露小 e 攻击…")
    dp_m, dq_m = leaks
    len_dp, len_dq, len_dp_m, len_dq_m = lens
    len_dp_l = len_dp - len_dp_m
    len_dq_l = len_dq - len_dq_m
    len_N = N.nbits()
    len_e = e.nbits()
    alpha = Rational(len_e / len_N)
    beta1 = Rational(len_dp / len_N)
    beta2 = Rational(len_dq / len_N)
    delta1 = Rational(len_dp_l / len_N)
    delta2 = Rational(len_dq_l / len_N)
    print("密钥参数：")
    print(
        f"α = {alpha.n(digits=3)}, β1 = {beta1.n(digits=3)}, β2 = {beta2.n(digits=3)}, δ1 = {delta1.n(digits=3)}, δ2 = {delta2.n(digits=3)}"
    )
    dp_m <<= len_dp_l
    dq_m <<= len_dq_l
    print("判断 k + l 与 e 的大小…")
    kl = ((e ** 2 * dp_m * dq_m) // N) + 1
    s = (1 - kl * (N - 1)) % e
    delt = sqrt(s ** 2 - 4 * kl)
    if delt.is_integer() == False:
        print("e ≤ k + l < 2 * e")
        s += e
        delt = sqrt(s ** 2 - 4 * kl)
    else:
        print("0 < k + l < e")
    k = (s + delt) >> 1
    len_k = k.nbits()
    dp_l = mixed_kp(N, k, [((e * dp_m + k - 1) * inverse_mod(e, k * N)) % (k * N), 0], [len_k + len_N // 2, len_dp_m, 0], [None], len_e=len_e, raw=True)
    if dp_l is None:
        print("小根为 k…")
        k = (s - delt) >> 1
        len_k = k.nbits()
        dp_l = mixed_kp(N, k, [((e * dp_m + k - 1) * inverse_mod(e, k * N)) % (k * N), 0], [len_k + len_N // 2, len_dp_m, 0], [None], len_e=len_e, raw=True)
    else:
        print("大根为 k…")
    if dp_l:
        dp = dp_m + dp_l
        p = (e * dp - 1) // k + 1
        return p

# leaks = [dp lsb, dq lsb], lens = [len dp, len dq, len low], params = [m], test = [p]
def small_e_dp_dq_with_lsb(N, e, leaks, lens, params, test=None):
    print("开始执行 May, Nowakowski, Sarkar 的 dp,dq 低位泄露小 e 攻击…")
    dp_l, dq_l = leaks
    len_dp, len_dq, len_low = lens
    len_N = N.nbits()
    len_e = e.nbits()
    len_k = len_dp + len_e - len_N // 2
    len_l = len_dq + len_e - len_N // 2
    alpha = Rational(len_e / len_N)
    beta1 = Rational(len_dp / len_N)
    beta2 = Rational(len_dq / len_N)
    delta1 = Rational((len_dp - dp_l.nbits()) / len_N)
    delta2 = Rational((len_dq - dq_l.nbits()) / len_N)
    print("密钥参数：")
    print(
        f"α = {alpha.n(digits=3)}, β1 = {beta1.n(digits=3)}, β2 = {beta2.n(digits=3)}, δ1 = {delta1.n(digits=3)}, δ2 = {delta2.n(digits=3)}"
    )
    X = 1 << len_k
    Y = 1 << len_l
    print("开始执行一般化二元攻击…")
    if None in params:
        print("未指定攻击参数，自动选择攻击参数'm', 't'…")
        t = 3 * (len_k + len_l) / (len_e + len_low)
        if t >= 2:
            return
        else:
            m = max(1, ceil((t - 1) / (2 - t)))
            print(f"自动使用攻击参数：\nm = {m}")
            print(f"格的维度：\ndim = {(m + 1) ** 2}")
            print("格行列式中各项幂次：")
            print(f"s_X = {(m * (m + 1) ** 2) // 2}, s_Y = {(m * (m + 1) ** 2) // 2}, s_eM = {m * (m + 1) ** 2 - ((2 * m + 1) * (m + 1) * m) // 6}")
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