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


def get_leak(num, pos, length=None, proportion=None, rand_mod=False):
    if proportion:
        bits = ceil(num.nbits() * proportion)
    else:
        bits = length
    if pos == "high":
        bits = num.nbits() - bits
    if rand_mod == False:
        mod = 2**bits
    else:
        mod = get_rand(bits)
    if pos == "high":
        return (num // mod) * mod
    elif pos == "low":
        return num % mod


def ernst05_mixed_1_test():
    lp = 512
    p = get_prime(lp)
    q = get_prime(lp)
    p_q = -(p + q)
    N = p * q
    phi = (p - 1) * (q - 1)
    beta = 0.4
    delta = 0.15
    high = 0.15
    ld = ceil(N.nbits() * beta)
    d, e = get_pair(ld, phi)
    k = (e * d - 1) // phi
    d_low = get_leak(d, "low", ceil(ld - lp * 2 * (delta + high)))
    d_high = get_leak(d, "high", ceil(lp * 2 * high))
    print(
        f"N:{N}\ne:{e}\nd_msb d_lsb:{[d_high // (1 << (ld - ceil(lp * 2 * high))), d_low]}\nd_len, msb_len, lsb_len:{[ld, ceil(lp * 2 * high), ceil(ld - lp * 2 * (delta + high))]}\n"
    )
    sol = mixed_1(
        N,
        e,
        [d_high // (1 << (ld - ceil(lp * 2 * high))), d_low],
        [ld, ceil(lp * 2 * high), ceil(ld - lp * 2 * (delta + high))],
    )
    assert sol == d


def ernst05_mixed_2_test():
    lp = 512
    p = get_prime(lp)
    q = get_prime(lp)
    p_q = p + q
    N = p * q
    phi = (p - 1) * (q - 1)
    beta = 0.7
    delta = 0.07
    high = 0.6
    ld = ceil(N.nbits() * beta)
    d, e = get_pair(ld, phi)
    k = (e * d - 1) // phi
    d_low = get_leak(d, "low", ceil(ld - lp * 2 * (delta + high)))
    d_high = get_leak(d, "high", ceil(lp * 2 * high))
    sol = mixed_2(
        N,
        e,
        [d_high // (1 << ceil(lp * 2 * high)), d_low],
        [ld, ceil(lp * 2 * high), ceil(ld - lp * 2 * (delta + high))],
        test=[d, p_q],
    )
    assert sol == d


def tk14_high_leak_test():
    lp = 512
    p = get_prime(lp)
    q = get_prime(lp)
    p_q = -(p + q)
    N = p * q
    phi = (p - 1) * (q - 1)
    # beta = 0.3
    # delta = 0.27
    beta = 0.8
    delta = 0.12
    ld = ceil(N.nbits() * beta)
    d, e = get_pair(ld, phi)
    k = (e * d - 1) // phi
    d_high = get_leak(d, "high", ceil(ld - lp * 2 * delta))
    # sol = high_leak(N, e, d_high, ld, N + 1, 1 << floor(lp * 2 * delta), (1 << (N.nbits() // 2)), 19)
    sol = high_leak(
        N,
        e,
        d_high,
        ld,
        N + 1,
        1 << ceil(lp * 2 * delta),
        1 << (N.nbits() // 2),
        6,
        k,
        p_q,
    )
    assert sol == d


def tk14_low_leak_1_test():
    lp = 512
    p = get_prime(lp)
    q = get_prime(lp)
    p_q = -(p + q)
    N = p * q
    phi = (p - 1) * (q - 1)
    beta = 0.3
    delta = 0.24
    ld = ceil(N.nbits() * beta)
    d, e = get_pair(ld, phi)
    k = (e * d - 1) // phi
    d_low = get_leak(d, "low", ceil(ld - lp * 2 * delta))
    sol = low_leak_1(
        N,
        e,
        d_low,
        ld,
        ceil(ld - lp * 2 * delta),
        N + 1,
        1 << ceil(N.nbits() * beta),
        (1 << (N.nbits() // 2)),
        6,
    )
    assert sol == d


def tk14_low_leak_2_test():
    lp = 512
    p = get_prime(lp)
    q = get_prime(lp)
    p_q = -(p + q)
    N = p * q
    phi = (p - 1) * (q - 1)
    beta = 0.4
    delta = 0.17
    ld = ceil(N.nbits() * beta)
    d, e = get_pair(ld, phi)
    k = (e * d - 1) // phi
    d_low = get_leak(d, "low", ceil(ld - lp * 2 * delta))
    sol = low_leak_2(
        N,
        e,
        d_low,
        ld,
        ceil(ld - lp * 2 * delta),
        N + 1,
        1 << ceil(N.nbits() * beta),
        (1 << (N.nbits() // 2)),
        7,
        3,
    )
    assert sol == d


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


def tk17_small_dp_dq_test():
    ln = 1000
    beta = 0.5
    delta1 = 0.062
    delta2 = 0.062
    lp = ceil(beta * ln)
    lq = ceil(beta * ln)
    ldp = ceil(delta1 * ln)
    ldq = ceil(delta2 * ln)
    while True:
        p = get_prime(lp)
        q = get_prime(lq)
        if (
            gcd(p - 1, q - 1) == 2
            and (p - 1).valuation(2) == 1
            and (q - 1).valuation(2) == 1
        ):
            break
    N = p * q
    phi = (p - 1) * (q - 1)
    while True:
        dp = 2 * get_rand(ldp - 1) + 1
        dq = 2 * get_rand(ldq - 1) + 1
        if gcd(dp, p - 1) == 1 and gcd(dq, q - 1) == 1:
            d = crt([dp, dq], [p - 1, q - 1])
            e = inverse_mod(d, phi)
            if gcd(e, N - 1) == 1:
                le = e.nbits()
                alpha = le / ln
                break
    res = small_dp_dq(N, e, 4, delta1, delta2)
    print(res)
    print(p, q)
    assert res == p or res == q


def mns21_test():
    ln = 1000
    beta = 0.5
    delta1 = 0.07
    delta2 = 0.07
    lp = ceil(beta * ln)
    lq = ceil(beta * ln)
    ldp = ceil(delta1 * ln)
    ldq = ceil(delta2 * ln)
    leak_prop = 0.03
    while True:
        p = get_prime(lp - 1)
        q = get_prime(lq - 1)
        if (
            gcd(p - 1, q - 1) == 2
            and (p - 1).valuation(2) == 1
            and (q - 1).valuation(2) == 1
        ):
            break
    N = p * q
    phi = (p - 1) * (q - 1)
    while True:
        dp = 2 * get_rand(ldp - 1) + 1
        dq = 2 * get_rand(ldq - 1) + 1
        if gcd(dp, p - 1) == 1 and gcd(dq, q - 1) == 1:
            d = crt([dp, dq], [p - 1, q - 1])
            e = inverse_mod(d, phi)
            if gcd(e, N - 1) == 1:
                k = (e * dp - 1) // (p - 1)
                l = (e * dq - 1) // (q - 1)
                le = e.nbits()
                alpha = le / ln
                break
    leak_1 = get_leak(dp, "low", ceil(dp.nbits() * leak_prop))
    leak_2 = get_leak(dq, "low", ceil(dp.nbits() * leak_prop))
    dp_dq_with_lsb(
        N,
        e,
        delta1,
        delta2,
        leak_1,
        leak_2,
        (5, 2),
        k,
        k - 1,
        p,
        q,
        l - 1,
        l,
        l_leak=ceil(dp.nbits() * leak_prop),
    )


ernst05_mixed_1_test()
# ernst05_mixed_2_test()
# tk14_high_leak_test()
# tk14_low_leak_1_test()
# tk14_low_leak_2_test()
# tk17_large_e_test()
# tk17_small_e_test()
# tk17_small_dp_dq_test()
# mns21_test()
