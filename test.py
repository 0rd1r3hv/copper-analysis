from sage.all import *
from src.tk14 import *
from src.tk17 import *
from src.mns21 import *
from src.ernst05 import *
from src.practical_bounds import *


def get_prime(length, proof=True):
    return random_prime((1 << length) - 1, proof, 1 << (length - 1))


def get_rand(length):
    return Integer(randint(1 << (length - 1), (1 << length) - 1))


def get_pair(length, phi):
    while True:
        a = get_rand(length)
        if gcd(a, phi) == 1:
            b = inverse_mod(a, phi)
            if b.nbits() == phi.nbits():
                return a, b


def get_leak(num, pos, length):
    if pos == "high":
        return num >> (num.nbits() - length)
    else:
        return num % (1 << length)


def get_partial_test(len_fac, len_control, len_m, len_l, control="d"):
    p = get_prime(len_fac)
    q = get_prime(len_fac)
    N = p * q
    phi = (p - 1) * (q - 1)
    if control == "d":
        d, e = get_pair(len_control, phi)
    else:
        e, d = get_pair(len_control, phi)
    return p, N, e, d, get_leak(d, "high", len_m), get_leak(d, "low", len_l)


def get_crt_partial_test(len_fac, len_dp, len_dq, len_l):
    while True:
        p = get_prime(len_fac)
        q = get_prime(len_fac)
        if (
            gcd(p - 1, q - 1) == 2
            and (p - 1).valuation(2) == 1
            and (q - 1).valuation(2) == 1
        ):
            break
    N = p * q
    phi = (p - 1) * (q - 1)
    while True:
        dp = 2 * get_rand(len_dp - 1) + 1
        dq = 2 * get_rand(len_dq - 1) + 1
        if gcd(dp, p - 1) == 1 and gcd(dq, q - 1) == 1:
            d = crt([dp, dq], [p - 1, q - 1])
            e = inverse_mod(d, phi)
            if gcd(e, N - 1) == 1 and e.nbits() == phi.nbits():
                k = (e * dp - 1) // (p - 1)
                l = (e * dq - 1) // (q - 1)
                break
    dp_l = get_leak(dp, 'low', len_l)
    dq_l = get_leak(dq, 'low', len_l)
    return p, N, e, dp, dq, dp_l, dq_l


def ernst05_mixed_1_test(beta, delta, kappa, len_fac):
    print(f"ernst05_mixed_1_test beta: {beta}, delta: {delta}, kappa: {kappa}, len_fac: {len_fac}")
    len_d = ceil(2 * len_fac * beta)
    len_m = ceil(2 * len_fac * (beta - delta - kappa))
    len_l = ceil(2 * len_fac * kappa)
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)
    return mixed_1(N, e, [d_m, d_l], [len_d, len_m, len_l], [None], [p]) == d


def ernst05_mixed_2_test(beta, delta, kappa, len_fac):
    print(f"ernst05_mixed_2_test beta: {beta}, delta: {delta}, kappa: {kappa}, len_fac: {len_fac}")
    len_d = ceil(2 * len_fac * beta)
    len_m = ceil(2 * len_fac * (beta - delta - kappa))
    len_l = ceil(2 * len_fac * kappa)
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)
    return mixed_2(N, e, [d_m, d_l], [len_d, len_m, len_l], [None], [p]) == d


def tk14_msb_1_test(beta, delta, len_fac):
    print(f"tk14_msb_1_test beta: {beta}, delta: {delta}, len_fac: {len_fac}")
    len_d = ceil(2 * len_fac * beta)
    len_m = ceil(2 * len_fac * (beta - delta))
    len_l = 0
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)
    return msb_1(N, e, [d_m], [len_d, len_m], [None], [p]) == d


def tk14_lsb_test(beta, delta, len_fac):
    print(f"tk14_lsb_test beta: {beta}, delta: {delta}, len_fac: {len_fac}")
    len_d = ceil(2 * len_fac * beta)
    len_l = ceil(2 * len_fac * (beta - delta))
    len_m = 0
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)
    return lsb(N, e, [d_l], [len_d, len_l], [None], [p]) == d


def tk14_mixed_test(beta, delta, kappa, len_fac):
    print(f"tk14_mixed_test: {beta}, delta: {delta}, kappa: {kappa}, len_fac: {len_fac}")
    len_d = ceil(2 * len_fac * beta)
    len_m = ceil(2 * len_fac * (beta - delta - kappa))
    len_l = ceil(2 * len_fac * kappa)
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)
    return mixed(N, e, [d_m, d_l], [len_d, len_m, len_l], [None], [p]) == d


def tk17_small_dp_dq_test(delta1, delta2, len_fac):
    print(f"tk17_small_dp_dq_test delta1: {delta1}, delta2: {delta2}, len_fac: {len_fac}")
    len_dp = ceil(2 * len_fac * delta1)
    len_dq = ceil(2 * len_fac * delta2)
    len_l = 0
    p, N, e, dp, dq, dp_l, dq_l = get_crt_partial_test(len_fac, len_dp, len_dq, len_l)
    res = small_dp_dq(N, e, [len_dp, len_dq], [None], test=[p])
    return res == p or res == N // p


def mns21_dp_dq_with_lsb_test(delta1, delta2, leak, len_fac):
    print(f"mns21_dp_dq_with_lsb_test delta1: {delta1}, delta2: {delta2}, leak: {leak}, len_fac: {len_fac}")
    len_dp = ceil(2 * len_fac * delta1)
    len_dq = ceil(2 * len_fac * delta2)
    len_l = ceil(2 * len_fac * leak)
    p, N, e, dp, dq, dp_l, dq_l = get_crt_partial_test(len_fac, len_dp, len_dq, len_l)
    res = dp_dq_with_lsb(N, e, [dp_l, dq_l], [len_dp, len_dq, len_l], [None], test=[p])
    return res == p or res == N // p


def tk17_large_e_test():
    ln = 1000
    alpha = 1
    beta = 0.405
    delta = 0.07
    le = ceil(alpha * ln)
    lp = ceil(beta * ln)
    ldq = ceil(delta * ln)
    p = get_prime(lp)
    q = get_prime(ln - lp)
    N = p * q
    phi = (p - 1) * (q - 1)
    while True:
        dq = get_rand(ldq)
        if gcd(dq, q - 1) == 1:
            e = inverse_mod(dq, q - 1) + get_rand(lp) * (q - 1)
            if gcd(e, phi) == 1 and e.nbits() == phi.nbits():
                break
    assert large_e(N, e, tk17_large_e(alpha, beta, delta), lp / ln, ldq / ln) == p


def tk17_small_e_test():
    ln = 2000
    alpha = 0.6
    beta = 0.5
    delta = 0.065
    le = ceil(alpha * ln)
    lp = ceil(beta * ln)
    ldq = ceil(delta * ln)
    p = get_prime(lp)
    q = get_prime(ln - lp)
    N = p * q
    phi = (p - 1) * (q - 1)
    while True:
        dq = get_rand(ldq)
        if gcd(dq, q - 1) == 1:
            e = inverse_mod(dq, q - 1) + get_rand(le - (ln - lp)) * (q - 1)
            if gcd(e, phi) == 1:
                break
    assert small_e(N, e, tk17_small_e(alpha, beta, delta), lp / ln, ldq / ln) == p


# ernst05_mixed_1_test()
# ernst05_mixed_2_test()
# tk14_high_leak_test()
# tk14_low_leak_1_test()
# tk14_low_leak_2_test()
# tk17_large_e_test()
# tk17_small_e_test()
# tk17_small_dp_dq_test()
# mns21_test()
# tk14_msb_1(0.3, 0.25)
# tk14_msb_1_test(0.37, 0.205, 512)
# tk14_msb_1_test(0.292, 0.282, 512)
# tk14_msb_1_test(0.31, 0.25, 512)
# tk14_msb_1_test(0.31, 0.25, 512)
# tk14_lsb_test(0.3, 0.25, 512)
# ernst05_mixed_1_test(0.4, 0.14, 0.1, 512)
# mns21_dp_dq_with_lsb(1, 0.02, 0.02, 0)
# mns21_dp_dq_with_lsb_test(0.07, 0.07, 0.03, 512)
tk14_mixed(Rational(0.35), Rational(0.24))
ernst05_eq1(props=[Rational(0.24), Rational(0.35), Rational(0.5), Rational(1 + 0.35)])
# tk14_mixed_test(0.35, 0.22, 0, 512)