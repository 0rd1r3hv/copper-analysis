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
    lp = 512
    p = get_prime(lp)
    q = get_prime(lp)
    p_q = -(p + q)
    N = p * q
    phi = (p - 1) * (q - 1)
    beta = 0.35
    leak_prop = 0.45
    ld = floor(N.nbits() * beta)
    d, e = get_pair(ld, phi)
    d_high = get_leak(d, "high", proportion=leak_prop)
    sol = high_leak(
        N,
        e,
        d_high,
        ld,
        N + 1,
        1 << ceil(ld * (1 - leak_prop)),
        1 << (N.nbits() // 2),
        8,
    )
    if sol:
        print(sol == d)


def tk17_large_e_test():
    ln = 2000
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
    assert small_e(N, e, tk17_small_e(alpha, beta, delta), lp / ln, ldq / ln, (e * dq - 1) // (q - 1) - 1, (e * dq - 1) // (q - 1), p, q) == p


tk17_large_e_test()
tk17_small_e_test()