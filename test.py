from sage.all import *
from tk14 import *
from tk17 import *


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


def tk17_test():
    lp = 405
    ln = 1000
    ldq = 50
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
    assert small_dq(N, e, 7, lp / ln, ldq / ln) == p


tk17_test()
