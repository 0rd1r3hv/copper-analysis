from sage.all import *
from src.misc import *
from src.practical_bounds import *
# from mp import groebner
from src.root_methods import groebner
from time import time
import subprocess


# test = [x, y, z]
# a * x + b * y + c * y * z + d = 0
def eq1(coefs, bounds, mt, test):
    x, y, z = ZZ['x, y, z'].gens()
    a, b, c, d = coefs
    f0 = a * x + b * y + c * y * z + d
    X, Y, Z, W = assure_coprime(bounds + [poly_norm(f0, bounds, 'inf')], d)
    bounds = [X, Y, Z]
    if mt:
        m, t = mt
    else:
        m, t = ernst05_eq1(bounds + [W])
    n = (X * Y * Z) ** m * Z ** t * W
    f = (inverse_mod(d, n) * f0) % n
    shifts = []
    for i in range(m + 2):
        j = m + 1 - i
        for k in range(j + t + 1):
            shifts.append(n * x ** i * y ** j * z ** k)
    for i in range(m + 1):
        for j in range(m - i + 1):
            for k in range(j + t + 1):
                shifts.append(x ** i * y ** j * z ** k * f * X ** (m - i) * Y ** (m - j) * Z ** (m + t - k))
    return solve_copper(shifts, min(zip(bounds, [x, y, z])), bounds, test, ex_pols=[f0])


# test = [x, y, z]
# a * x + b * y + c * y * z + d * z + e = 0
def eq2(coefs, bounds, mt, test):
    x, y, z = ZZ['x, y, z'].gens()
    a, b, c, d, e = coefs
    f0 = a * x + b * y + c * y * z + d * z + e
    X, Y, Z, W = assure_coprime(bounds + [poly_norm(f0, bounds, 'inf')], e)
    if mt:
        m, t = mt
    else:
        m, t = ernst05_eq2(bounds + [W])
    n = (X * Y * Z) ** m * Y ** t * W
    f = (inverse_mod(e, n) * f0) % n
    shifts = []
    for i in range(m + 2):
        k = m + 1 - i
        for j in range(m + t + 1 - i + 1):
            shifts.append(n * x ** i * y ** j * z ** k)
    for i in range(m + 1):
        j = m + t + 1 - i
        for k in range(m - i + 1):
            shifts.append(n * x ** i * y ** j * z ** k)
    for i in range(m + 1):
        for j in range(m - i + t + 1):
            for k in range(m - i + 1):
                shifts.append(x ** i * y ** j * z ** k * f * X ** (m - i) * Y ** (m + t - j) * Z ** (m - k))
    return solve_copper(shifts, min(zip(bounds, [x, y, z])), bounds, test, ex_pols=[f0])


# leaks = [d msb, d lsb], lens = [len d, len msb, len lsb], mt = [m ,t], test = [d, p + q]
def mixed_1(N, e, leaks, lens, mt=None, test=None):
    len_p = (N.nbits() + 1) // 2
    s_l = floor(2 * sqrt(N))
    s_r = (1 << len_p) + N // (1 << len_p)
    s = (s_l + s_r) >> 1
    A = N + 1 - s - ((N + 1 - s) % 4)
    len_d, len_m, len_l = lens
    d_m, d_l = leaks
    d_m <<= len_d - len_m
    coefs = [e << len_l, -A, 4, e * (d_m + d_l) - 1]
    bounds = [1 << (len_d - len_m - len_l), 1 << len_d, (s_r - s_l) >> 1]
    if test:
        d, p_q = test
        test = [(d - d_high - d_low) >> len_l, (e * d - 1) // (N + 1 - p_q), (p_q - s - ((N + 1 - s) % 4)) >> 2]
    res = eq1(coefs, bounds, mt, test)
    if res:
        return d_m + (res << len_l) + d_l


# leaks = [d msb, d lsb], lens = [len msb, len lsb], mt = [m ,t], test = [d, p + q]
def mixed_2(N, e, leaks, lens, mt=None, test=None):
    len_p = (N.nbits() + 1) // 2
    s_l = floor(2 * sqrt(N))
    s_r = (1 << len_p) + N // (1 << len_p)
    s = (s_l + s_r) >> 1
    A = N + 1 - s - ((N + 1 - s) % 4)
    len_d, len_m, len_l = lens
    d_m, d_l = leaks
    d_m <<= len_d - len_m
    k0 = e * d_m // N
    coefs = [e << len_l, -A, 4, 4 * k0, e * (d_m + d_l) - k0 * A - 1]
    bounds = [1 << (len_d - len_m - len_l), 1 << (max(len_d - len_m, len_d - len_p)), (s_r - s_l) >> 1]
    if test:
        d, p_q = test
        test = [(d - d_m - d_l) >> len_l, (e * d - 1) // (N + 1 - p_q) - k0, (p_q - s - ((N + 1 - s) % 4)) >> 2]
    res = eq2(coefs, bounds, mt, test)
    if res:
        return d_m + (res << len_l) + d_l