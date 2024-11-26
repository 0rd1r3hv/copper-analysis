from sage.all import (
    crt,
    Integer,
    ceil,
    inverse_mod,
    gcd,
    randint,
    random_prime,
    ZZ,
    GF,
    next_prime,
)
from src.cop96 import cop, hg
from src.tk14 import mixed, msb_1, lsb
from src.tlp17 import large_e, small_e, small_dp_dq
from src.mns21 import dp_dq_with_lsb
from src.mns22 import mixed_kp, small_e_dp_dq_with_msb, small_e_dp_dq_with_lsb
from src.ernst05 import mixed_1, mixed_2
from src.mn23 import automated

test = False


def get_prime(length, proof=False):
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


def get_kp_partial_test(len_N, len_p, len_k, len_m, len_l):
    p = get_prime(len_p)
    q = get_prime(len_N - len_p)
    N = p * q
    k = 2 * get_rand(len_k - 1) + 1
    kp = k * p
    # len_kp = kp.nbits()
    return p, k, N, get_leak(kp, "high", len_m), get_leak(kp, "low", len_l)


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
                break
    dp_l = get_leak(dp, "low", len_l)
    dq_l = get_leak(dq, "low", len_l)
    return p, N, e, dp, dq, dp_l, dq_l


def get_crt_1_test(len_N, len_e, len_dq, len_p):
    while True:
        p = get_prime(len_p)
        q = get_prime(len_N - len_p)
        if (
            gcd(p - 1, q - 1) == 2
            and (p - 1).valuation(2) == 1
            and (q - 1).valuation(2) == 1
        ):
            break
    N = p * q
    phi = (p - 1) * (q - 1)
    while True:
        dq = 2 * get_rand(len_dq - 1) + 1
        if gcd(dq, q - 1) == 1:
            e = (
                inverse_mod(dq, q - 1) + get_rand(len_e - (len_N - len_p)) * (q - 1)
            ) % phi
            if gcd(e, phi) == 1:
                break
    return p, N, e, dq


def get_crt_partial_control_e_test(len_fac, len_e, len_dp_m, len_dq_m, len_l):
    while True:
        p = get_prime(len_fac)
        q = get_prime(len_fac)
        if (p * q - 1) % 4 == 2:
            break
    N = p * q
    phi = (p - 1) * (q - 1)
    while True:
        e = 2 * get_rand(len_e - 1) + 1
        if gcd(N - 1, e) == 1 and gcd(e, phi) == 1:
            d = inverse_mod(e, phi)
            dp = d % (p - 1)
            dq = d % (q - 1)
            if ((e * dp - 1) // (p - 1)) % 2 == 1 and (
                (e * dq - 1) // (q - 1)
            ) % 2 == 1:
                break
    dp_m = get_leak(dp, "high", len_dp_m)
    dq_m = get_leak(dq, "high", len_dq_m)
    dp_l = get_leak(dp, "low", len_l)
    dq_l = get_leak(dq, "low", len_l)
    return p, N, e, dp, dq, dp_m, dq_m, dp_l, dq_l


def hg_cop_test(beta, delta, len_N, deg, mode):
    len_p = ceil(len_N * beta)
    len_q = ceil(len_N * (1 - beta))
    len_X = ceil(len_N * delta)
    p = get_prime(len_p)
    q = get_prime(len_q)
    N = p * q
    x0 = get_rand(len_X)
    PR = ZZ["x"]
    x = PR.gen()
    a = get_rand(len_N)
    g = PR.random_element(degree=deg)
    f = (x + a) ** deg + 2 * g
    strf = f"(x + {a}) ** {deg} + {2 * g}"
    if mode == "cop":
        with open("cop.txt", "w", encoding="utf-8") as file:
            file.write(f"f: {strf + f' - {f(x0) % N}'}\nN: {N}\nlen_X: {len_X}\n")
        res = cop(strf + f" - {f(x0) % N}", N, [len_X], [None])
    elif mode == "hg":
        with open("hg.txt", "w", encoding="utf-8") as file:
            file.write(
                f"f: {strf + f' - {f(x0) % p}'}\nN: {N}\nlen_X: {len_X}\nlen_p: {len_p}\n"
            )
        res = hg(strf + f" - {f(x0) % p}", N, [len_X, len_p], [None])
    return res == x0


def ernst05_mixed_1_test(beta, delta, kappa, len_fac):
    print(
        f"ernst05_mixed_1_test beta: {beta}, delta: {delta}, kappa: {kappa}, len_fac: {len_fac}"
    )
    len_d = ceil(2 * len_fac * beta)
    len_m = ceil(2 * len_fac * (beta - delta - kappa))
    len_l = ceil(2 * len_fac * kappa)
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)
    with open("ernst05_mixed_1.txt", "w", encoding="utf-8") as file:
        file.write(
            f"N: {N}\ne: {e}\nd_m: {d_m}\nd_l: {d_l}\nlen_d: {len_d}\nlen_m: {len_m}\nlen_l: {len_l}\n"
        )
    if test:
        return mixed_1(N, e, [d_m, d_l], [len_d, len_m, len_l], [None], [p]) == d
    else:
        return mixed_1(N, e, [d_m, d_l], [len_d, len_m, len_l], [None]) == d


def ernst05_mixed_2_test(beta, delta, kappa, len_fac):
    print(
        f"ernst05_mixed_2_test beta: {beta}, delta: {delta}, kappa: {kappa}, len_fac: {len_fac}"
    )
    len_d = ceil(2 * len_fac * beta)
    len_m = ceil(2 * len_fac * (beta - delta - kappa))
    len_l = ceil(2 * len_fac * kappa)
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)
    with open("ernst05_mixed_2.txt", "w", encoding="utf-8") as file:
        file.write(
            f"N: {N}\ne: {e}\nd_m: {d_m}\nd_l: {d_l}\nlen_d: {len_d}\nlen_m: {len_m}\nlen_l: {len_l}\n"
        )
    if test:
        return mixed_2(N, e, [d_m, d_l], [len_d, len_m, len_l], [None], [p]) == d
    else:
        return mixed_2(N, e, [d_m, d_l], [len_d, len_m, len_l], [None]) == d


def tk14_msb_1_test(beta, delta, len_fac, test=True):
    print(f"tk14_msb_1_test beta: {beta}, delta: {delta}, len_fac: {len_fac}")
    len_d = ceil(2 * len_fac * beta)
    len_m = ceil(2 * len_fac * (beta - delta))
    len_l = 0
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)

    with open("tk14_msb.txt", "w", encoding="utf-8") as file:
        file.write(
            f"N: {N}\ne: {e}\nd_m: {d_m}\nlen_d: {len_d}\nlen_m: {len_m}\nlen_l: {len_l}\n"
        )

    if test:
        res = msb_1(N, e, [d_m], [len_d, len_m], [None], [p])
    else:
        res = msb_1(N, e, [d_m], [len_d, len_m], [None])
    return res == d


def tk14_lsb_test(beta, delta, len_fac):
    print(f"tk14_lsb_test beta: {beta}, delta: {delta}, len_fac: {len_fac}")
    len_d = ceil(2 * len_fac * beta)
    len_l = ceil(2 * len_fac * (beta - delta))
    len_m = 0
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)
    with open("tk14_lsb.txt", "w", encoding="utf-8") as file:
        file.write(f"N: {N}\ne: {e}\nd_l: {d_l}\nlen_d: {len_d}\nlen_l: {len_l}\n")
    if test:
        return lsb(N, e, [d_l], [len_d, len_l], [None], [p]) == d
    else:
        return lsb(N, e, [d_l], [len_d, len_l], [None]) == d


def tk14_mixed_test(beta, delta, kappa, len_fac, brute, triangluarize):
    print(
        f"tk14_mixed_test: {beta}, delta: {delta}, kappa: {kappa}, len_fac: {len_fac}"
    )
    len_d = ceil(2 * len_fac * beta)
    len_m = ceil(2 * len_fac * (beta - delta - kappa))
    len_l = ceil(2 * len_fac * kappa)
    p, N, e, d, d_m, d_l = get_partial_test(len_fac, len_d, len_m, len_l)
    with open("tk14_mixed.txt", "w", encoding="utf-8") as file:
        file.write(
            f"N: {N}\ne: {e}\nd_m: {d_m}\nd_l: {d_l}\nlen_d: {len_d}\nlen_m: {len_m}\nlen_l: {len_l}\n"
        )
    if test:
        res = mixed(
            N,
            e,
            [d_m, d_l],
            [len_d, len_m, len_l],
            [None],
            [p],
            brute=brute,
            triangluarize=triangluarize,
        )
    else:
        res = mixed(
            N,
            e,
            [d_m, d_l],
            [len_d, len_m, len_l],
            [None],
            brute=brute,
            triangluarize=triangluarize,
        )
    return res == d


def tlp17_large_e_test(alpha, beta, delta, len_N):
    print(f"tlp17_large_e_test alpha: {alpha}, beta: {beta}, delta: {delta}")
    len_dq = ceil(len_N * delta)
    len_p = ceil(len_N * beta)
    len_e = ceil(len_N * alpha)
    p, N, e, dq = get_crt_1_test(len_N, len_e, len_dq, len_p)
    with open("tlp17_large_e.txt", "w", encoding="utf-8") as file:
        file.write(f"N: {N}\ne: {e}\nlen_p: {len_p}\nlen_dq: {len_dq}\n")
    if test:
        res = large_e(N, e, [len_p, len_dq], [None], test=[p])
    else:
        res = large_e(N, e, [len_p, len_dq], [None])
    return res == p


def tlp17_small_e_test(alpha, beta, delta, len_N):
    print(f"tlp17_small_e_test alpha: {alpha}, beta: {beta}, delta: {delta}")
    len_dq = ceil(len_N * delta)
    len_p = ceil(len_N * beta)
    len_e = ceil(len_N * alpha)
    p, N, e, dq = get_crt_1_test(len_N, len_e, len_dq, len_p)
    with open("tlp17_small_e.txt", "w", encoding="utf-8") as file:
        file.write(f"N: {N}\ne: {e}\nlen_p: {len_p}\nlen_dq: {len_dq}\n")
    if test:
        res = small_e(N, e, [len_p, len_dq], [None], test=[p])
    else:
        res = small_e(N, e, [len_p, len_dq], [None])
    return res == p


def tlp17_small_dp_dq_test(delta1, delta2, len_fac):
    print(
        f"tlp17_small_dp_dq_test delta1: {delta1}, delta2: {delta2}, len_fac: {len_fac}"
    )
    len_dp = ceil(2 * len_fac * delta1)
    len_dq = ceil(2 * len_fac * delta2)
    len_l = 0
    p, N, e, dp, dq, dp_l, dq_l = get_crt_partial_test(len_fac, len_dp, len_dq, len_l)
    with open("tlp17_small_dp_dq.txt", "w", encoding="utf-8") as file:
        file.write(f"N: {N}\ne: {e}\nlen_dp: {len_dp}\nlen_dq: {len_dq}\n")
    if test:
        res = small_dp_dq(N, e, [len_dp, len_dq], [None], test=[p])
    else:
        res = small_dp_dq(N, e, [len_dp, len_dq], [None])
    return res == p or res == N // p


def mns21_dp_dq_with_lsb_test(delta1, delta2, leak, len_fac):
    print(
        f"mns21_dp_dq_with_lsb_test delta1: {delta1}, delta2: {delta2}, leak: {leak}, len_fac: {len_fac}"
    )
    len_dp = ceil(2 * len_fac * delta1)
    len_dq = ceil(2 * len_fac * delta2)
    len_l = ceil(2 * len_fac * leak)
    p, N, e, dp, dq, dp_l, dq_l = get_crt_partial_test(len_fac, len_dp, len_dq, len_l)

    with open("mns21_dp_dq_with_lsb.txt", "w", encoding="utf-8") as file:
        file.write(
            f"N: {N}\ne: {e}\ndp_l: {dp_l}\ndq_l: {dq_l}\nlen_dp: {len_dp}\nlen_dq: {len_dq}\nlen_l: {len_l}\n"
        )

    if test:
        res = dp_dq_with_lsb(
            N, e, [dp_l, dq_l], [len_dp, len_dq, len_l], [None], test=[p]
        )
    else:
        res = dp_dq_with_lsb(N, e, [dp_l, dq_l], [len_dp, len_dq, len_l], [None])
    return res == p or res == N // p


def mns22_mixed_kp_test(beta, mu, delta, kappa, len_N):
    len_p = ceil(len_N * beta)
    len_k = ceil(len_N * mu)
    len_l = ceil(len_N * kappa)
    len_m = ceil(len_N * (beta + mu - delta - kappa))
    p, k, N, kp_m, kp_l = get_kp_partial_test(len_N, len_p, len_k, len_m, len_l)
    len_kp = (k * p).nbits()
    with open("mns22_mixed_kp.txt", "w", encoding="utf-8") as file:
        file.write(
            f"N: {N}\nk: {k}\nkp_m: {kp_m}\nkp_l: {kp_l}\nlen_kp: {len_kp}\nlen_m: {len_m}\nlen_l: {len_l}"
        )
    res = mixed_kp(N, k, [kp_m, kp_l], [len_kp, len_m, len_l], [None])
    if res:
        return (kp_m << (len_kp - len_m)) + (res << len_l) + kp_l == k * p
    else:
        return False


def mns22_small_e_dp_dq_with_msb_test(alpha, delta, len_fac):
    len_e = ceil(2 * len_fac * alpha)
    len_dp_m = len_dq_m = ceil(2 * len_fac * (1 / 2 - delta))
    len_l = 0
    p, N, e, dp, dq, dp_m, dq_m, dp_l, dq_l = get_crt_partial_control_e_test(
        len_fac, len_e, len_dp_m, len_dq_m, len_l
    )
    len_dp = dp.nbits()
    len_dq = dq.nbits()
    print(
        f"N: {N}, e: {e}, dp_m: {dp_m}, dq_m: {dq_m}, len_dp: {len_dp}, len_dq: {len_dq}, len_dp_m: {len_dp_m}, len_dq_m: {len_dq_m}"
    )
    with open("mns22_small_e_dp_dq_with_msb.txt", "w", encoding="utf-8") as file:
        file.write(
            f"N: {N}\ne: {e}\ndp_m: {dp_m}\ndq_m: {dq_m}\nlen_dp: {len_dp}\nlen_dq: {len_dq}\nlen_dp_m: {len_dp_m}\nlen_dq_m: {len_dq_m}\n"
        )
    res = small_e_dp_dq_with_msb(
        N, e, [dp_m, dq_m], [len_dp, len_dq, len_dp_m, len_dq_m]
    )
    return res == p or res == N // p


def mns22_small_e_dp_dq_with_lsb_test(alpha, delta, len_fac):
    len_e = ceil(2 * len_fac * alpha)
    len_dp_m = len_dq_m = 0
    len_l = ceil(2 * len_fac * (1 / 2 - delta))
    p, N, e, dp, dq, dp_m, dq_m, dp_l, dq_l = get_crt_partial_control_e_test(
        len_fac, len_e, len_dp_m, len_dq_m, len_l
    )
    len_dp = dp.nbits()
    len_dq = dq.nbits()
    with open("mns22_small_e_dp_dq_with_lsb.txt", "w", encoding="utf-8") as file:
        file.write(
            f"N: {N}\ne: {e}\ndp_l: {dp_l}\ndq_l: {dq_l}\nlen_dp: {len_dp}\nlen_dq: {len_dq}\nlen_l: {len_l}\n"
        )
    if test:
        res = small_e_dp_dq_with_lsb(
            N, e, [dp_l, dq_l], [len_dp, len_dq, len_l], [None], test=[p]
        )
    else:
        res = small_e_dp_dq_with_lsb(
            N, e, [dp_l, dq_l], [len_dp, len_dq, len_l], [None]
        )
    return res == p


"""
def mn23_automated_test(n, k, m):


    def split(x, bits):
        lsb = (x % (1 << bits))
        msb = x - lsb
        return msb, lsb


    p = next_prime(ZZ.random_element(1 << (n - 1), 1 << n))
    while p % 4 != 3:
        p = next_prime(p + 1)

    A = ZZ(GF(p).random_element())
    B = (2 * (A + 6) * inverse_mod(-A + 2, p)) % p
    C = (2 * (A - 6) * inverse_mod(A + 2, p)) % p

    unknown_bits = n - k

    A_MSB, A_LSB = split(A, unknown_bits)
    B_MSB, B_LSB = split(B, unknown_bits)
    C_MSB, C_LSB = split(C, unknown_bits)

    x, y, z = ZZ['x, y, z'].gens()

    f = (A_MSB + x)*(B_MSB + y) + 2 * (A_MSB + x) - 2 * (B_MSB + y) + 12
    g = (C_MSB + z)*(B_MSB + y) + 2 * (B_MSB + y) - 2 * (C_MSB + z) + 12
    h = (A_MSB + x)*(C_MSB + z) - 2 * (A_MSB + x) + 2 * (C_MSB + z) + 12

    X = 1 << unknown_bits
    Y = 1 << unknown_bits
    Z = 1 << unknown_bits
    i = m // 3
    polys = [f, g, h]
    bounds = [X, Y, Z]
    solutions_verify = [A_LSB, B_LSB, C_LSB]
    with open('mn23.txt', "w", encoding="utf-8") as file:
        file.write(f"p: {p}\nm: {m}\nf: {str(f)}\ng: {str(g)}\nh: {str(h)}\nx: {A_LSB}\ny: {B_LSB}\nz: {C_LSB}")
    res = automated(polys, [X, x], bounds, (prod(polys) ** i).monomials(), p, 3 * i, solutions_verify)
    if res:
        print(f"攻击成功！\nx = {A_LSB}\ny = {B_LSB}\nz = {C_LSB}")
"""


def mn23_automated_test(n, k):
    def split(x, bits):
        lsb = x % (1 << bits)
        msb = x - lsb
        return msb, lsb

    p = next_prime(ZZ.random_element(1 << (n - 1), 1 << n))
    while p % 4 != 3:
        p = next_prime(p + 1)

    A = ZZ(GF(p).random_element())
    B = (2 * (A + 6) * inverse_mod(-A + 2, p)) % p
    C = (2 * (A - 6) * inverse_mod(A + 2, p)) % p

    unknown_bits = n - k

    A_MSB, A_LSB = split(A, unknown_bits)
    B_MSB, B_LSB = split(B, unknown_bits)
    C_MSB, C_LSB = split(C, unknown_bits)

    x, y, z = ZZ["x, y, z"].gens()

    f = (A_MSB + x) * (B_MSB + y) + 2 * (A_MSB + x) - 2 * (B_MSB + y) + 12
    g = (C_MSB + z) * (B_MSB + y) + 2 * (B_MSB + y) - 2 * (C_MSB + z) + 12
    h = (A_MSB + x) * (C_MSB + z) - 2 * (A_MSB + x) + 2 * (C_MSB + z) + 12

    polys = [f, g, h]
    len_bounds = [unknown_bits] * 3
    solutions_verify = [A_LSB, B_LSB, C_LSB]
    """
    with open('mn23.txt', "w", encoding="utf-8") as file:
        file.write(f"p: {p}\nm: {m}\nf: {str(f)}\ng: {str(g)}\nh: {str(h)}\nx: {A_LSB}\ny: {B_LSB}\nz: {C_LSB}")
    """
    str_vars = "x, y, z"
    str_pols = [str(pol) for pol in polys]
    if test:
        with open("mn23_automated.txt", "w", encoding="utf-8") as file:
            file.write(
                f"str_vars: {str_vars}\nstr_pols: {str_pols}\nlen_bounds: {len_bounds}\np: {p}\ntest: {solutions_verify}"
            )
        res = automated(str_vars, str_pols, len_bounds, p, test=solutions_verify)
    else:
        with open("mn23_automated.txt", "w", encoding="utf-8") as file:
            file.write(
                f"str_vars: {str_vars}\nstr_pols: {str_pols}\nlen_bounds: {len_bounds}\np: {p}"
            )
        res = automated(str_vars, str_pols, len_bounds, p)
    return res == solutions_verify


# ernst05_mixed_1_test(0.4, 0.14, 0.1, 512)
# ernst05_mixed_2_test()
# tk14_high_leak_test()
# tk14_low_leak_1_test()
# tk14_low_leak_2_test()
# tlp17_large_e_test()
# tlp17_small_e_test()
# tlp17_small_dp_dq_test()
# mns21_test()
# tk14_msb_1(0.3, 0.25)
# tk14_msb_1_test(0.37, 0.2, 512)
# tk14_msb_1_test(0.292, 0.282, 512)
# tk14_msb_1_test(0.31, 0.25, 512)
# tk14_msb_1_test(0.31, 0.25, 512)
# tk14_lsb_test(0.3, 0.25, 512)
# ernst05_mixed_1_test(0.4, 0.14, 0.1, 512)
# ernst05_mixed_2_test(0.7, 0.06, 0.05, 512)
# mns21_dp_dq_with_lsb(1, 0.02, 0.02, 0)
# mns21_dp_dq_with_lsb_test(0.07, 0.07, 0.03, 512)
# mns21_dp_dq_with_lsb_test(0.07, 0.07, 0.03, 512)
# tk14_mixed(Rational(0.49), Rational(0.155))
# ernst05_eq1(props=[Rational(0.155), Rational(0.49), Rational(0.5), Rational(1 + 0.49)])
# print(f"get_partial_test: {get_partial_test(768, 400, 70, 70)}")
# print(f"p, N, e, dp, dq, dp_l, dq_l: {get_crt_partial_test(256, 120, 120, 100)}")

# tk14_mixed_test(0.292, 0.248, 0.02, 512, brute=False, triangluarize=True)
# tk14_msb_1_test(0.292, 0.26, 512)
# mns21_dp_dq_with_lsb_test(0.05, 0.05, 0.2, 512)
# tk14_mixed(Rational(0.292), Rational(0.26), Rational('513/1023'))
# tk14_mixed(Rational(0.292), Rational(0.26), Rational('509/1023'))
# mns22_mixed_kp_test(0.5, 0.1, 0.347, 0.1, 512)
# mn23(512, 300, 6)

# print(hg_cop_test(1 / 2, 0.18, 1024, 5, "cop"))
# print(hg_cop_test(1 / 2, 0.07, 1024, 3, "hg"))
# print(ernst05_mixed_1_test(0.4, 0.16, 0.1, 512))
# print(ernst05_mixed_2_test(0.7, 0.06, 0.05, 512))
# print(tk14_msb_1_test(0.292, 0.26, 512))
# print(tk14_lsb_test(0.292, 0.26, 512))
# print(tk14_mixed_test(0.4, 0.18, 0.1, 512, brute=False, triangluarize=True))
# print(tlp17_large_e_test(1, 0.29, 0.19, 1024))
# print(tlp17_small_e_test(0.6, 0.5, 0.06, 1024))
# print(tlp17_small_dp_dq_test(0.03, 0.03, 512))
print(mns21_dp_dq_with_lsb_test(0.07, 0.07, 0.063, 512))
# print(mns22_mixed_kp_test(0.55, 0.05, 0.346, 0.1, 512))
# print(mns22_small_e_dp_dq_with_msb_test(1 / 12, 0.32, 512))
# print(mns22_small_e_dp_dq_with_lsb_test(1 / 12, 0.31, 512))
# print(mn23_automated_test(512, 318))
