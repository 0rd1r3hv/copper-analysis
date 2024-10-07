from sage.all import *
from tk14 import *
from tk17 import *
from practical_bounds import *


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


def tk14_test():
    lp = 500
    p = get_prime(lp)
    q = get_prime(lp)
    p_q = -(p + q)
    N = p * q
    phi = (p - 1) * (q - 1)
    beta = 0.3
    gamma = 0.276
    leak_prop = 1 - gamma / beta
    ld = floor(N.nbits() * beta)
    d, e = get_pair(ld, phi)
    k = (e * d - 1) // phi
    d_high = get_leak(d, "high", proportion=leak_prop)
    assert high_leak(
        N,
        e,
        d_high,
        ld,
        N + 1,
        1 << ceil(ld * (1 - leak_prop)),
        1 << (N.nbits() // 2),
        tk14_high(beta, gamma)
    ) == d


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
        p = get_prime(lp - 1)
        q = get_prime(lq - 1)
        if gcd(p - 1, q - 1) == 2:
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


# tk17_large_e_test()
# tk17_small_e_test()
# tk17_small_dp_dq_test()
tk14_test()