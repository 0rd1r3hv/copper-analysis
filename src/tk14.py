from sage.all import *
from src.root_methods import groebner
from time import time
from src.fplll_fmt import fplll_fmt, fplll_read
import subprocess

# Partial Key Exposure Attacks on RSA: Achieving the Boneh-Durfee Bound


def l_MSBs(x, km, t):
    return max(0, ceil((x - km) / (t + 1)))


def l_LSBs(x, km, t):
    return max(0, ceil((x - km) / t))


# f_MSBs(x, y) = 1 + (k0 + x)(A + y) ≡ 0 (mod e)
def high_leak(N, e, d_high, d_len, A, X, Y, m):
    beta = d_len / N.nbits()
    gamma = Integer(X).nbits() / N.nbits()
    k0 = e * d_high // N
    Z = k0 * Y
    PR = ZZ["x, y, z"]
    x, y, z = PR.gens()
    Q = PR.quotient(x * y + 1 - z)
    f = z + A * x
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    km = k * m
    shifts = []
    monomials = []
    trans_x = [z**0]
    trans_y = [[z**0] * max(floor(km + t * m) + 1, floor(km) + 1)] + [
        [z**0] for _ in range(m)
    ]
    for i in range(1, m + 1):
        deg = l_MSBs(i, km, t)
        if deg == 0:
            trans_x.append((1 + x * y) ** i)
        else:
            pol = (x * y) ** (i - deg) * z ** deg
            rem = z ** i - (z - 1) ** (i - deg) * z ** deg
            for d in range(deg, i):
                pol += rem.monomial_coefficient(z ** d) * trans_x[d]
            trans_x.append(pol)
    for u in range(1, m + 1):
        for j in range(1, floor(km + t * u) + 1):
            deg = l_MSBs(u + j, km, t)
            if deg == 0:
                trans_y[u].append((1 + x * y) ** u)
            else:
                pol = (x * y) ** (u - deg) * z ** deg
                rem = z ** u - (z - 1) ** (u - deg) * z ** deg
                for d in range(deg, u):
                    pol += rem.monomial_coefficient(z ** d) * trans_y[d][j]
                trans_y[u].append(pol)
    for u in range(m + 1):
        for i in range(u + 1):
            orig = f**i
            pol = 0
            for mono in orig.monomials():
                deg_z = mono.degree(z)
                pol += (
                    orig.monomial_coefficient(mono)
                    * trans_x[deg_z]
                    * mono
                    // (z**deg_z)
                )
            pol = x ** (u - i) * (pol.subs(x=k0 + x))
            assert pol.subs(z=(k0 + x) * y + 1) == x ** (u - i) * (
                (f**i).subs(x=k0 + x, z=(k0 + x) * y + 1)
            )
            deg = l_MSBs(i, km, t)
            monomials.append(x ** (u - deg) * y ** (i - deg) * z**deg)
            shifts.append(pol(X * x, Y * y, Z * z) * e ** (m - i))
        for j in range(1, floor(km + t * u) + 1):
            orig = Q(y**j * f**u).lift()
            pol = 0
            for mono in orig.monomials():
                deg_y = mono.degree(y)
                deg_z = mono.degree(z)
                if deg_y != 0:
                    pol += (
                        orig.monomial_coefficient(mono)
                        * trans_y[deg_z][deg_y]
                        * mono
                        // (z**deg_z)
                    )
                else:
                    pol += (
                        orig.monomial_coefficient(mono)
                        * trans_x[deg_z]
                        * mono
                        // (z**deg_z)
                    )
            pol = pol.subs(x=k0 + x)
            assert pol.subs(z=(k0 + x) * y + 1) == (y**j * f**u).subs(
                x=k0 + x, z=(k0 + x) * y + 1
            )
            deg = l_MSBs(u + j, km, t)
            monomials.append(x ** (u - deg) * y ** (u + j - deg) * z**deg)
            shifts.append(pol(X * x, Y * y, Z * z) * e ** (m - u))
    scales = [mono(X, Y, Z) for mono in monomials]
    n = len(shifts)
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()
    # L = L.LLL(delta=0.75)
    s = fplll_fmt(L)
    file_name = "tk14_output.txt"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(s)

    try:
        rst = subprocess.Popen(
            "tk14_flatter.nu",
            text=True,
            stdout=subprocess.PIPE,
            shell=True,
        )

        L = fplll_read(rst.stdout)
    except subprocess.CalledProcessError as e:
        return

    pols = [z - (k0 + x) * y - 1]
    for i in range(n):
        pol = 0
        for j in range(n):
            pol += L[i, j] * monomials[j] // scales[j]
        pols.append(pol)

    print(time() - start)
    x0 = groebner(pols, x, X)
    if x0:
        return floor(((k0 + x0) * N) // e)


def low_leak_1(N, e, d_low, d_len, leak_len, A, X, Y, m):
    beta = d_len / N.nbits()
    gamma = (d_len - leak_len) / N.nbits()
    Z = X * Y
    PR = ZZ["x, y, z"]
    x, y, z = PR.gens()
    Q = PR.quotient(x * y + 1 - z)
    f1 = z + A * x
    f2 = x * (A + y) + 1 - e * d_low
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    km = k * m
    M = 1 << leak_len
    eM = e * M
    shifts = []
    monomials = []
    trans_y = [[z**0] * (floor(km + t * m) + 1)] + [[z**0] for _ in range(m)]
    for u in range(1, m + 1):
        for j in range(1, floor(km + t * u) + 1):
            deg = l_LSBs(j, km, t)
            if deg == 0:
                trans_y[u].append((1 + x * y) ** u)
            else:
                pol = (x * y) ** (u - deg) * z**deg
                rem = z**u - (z - 1) ** (u - deg) * z**deg
                for k in range(deg, u):
                    pol += rem.monomial_coefficient(z**k) * trans_y[k][j]
                trans_y[u].append(pol)
    for u in range(m + 1):
        for i in range(u + 1):
            monomials.append(x ** u * y ** i)
            shifts.append((x ** (u - i) * f2 ** i)(X * x, Y * y, Z * z) * eM ** (m - i))
        for j in range(1, floor(km + t * u) + 1):
            deg = l_LSBs(j, km, t)
            orig = Q(y**j * f1**deg * f2 ** (u - deg)).lift()
            pol = 0
            for mono in orig.monomials():
                deg_y = mono.degree(y)
                deg_z = mono.degree(z)
                if deg_y != 0:
                    pol += (
                        orig.monomial_coefficient(mono)
                        * trans_y[deg_z][deg_y]
                        * mono
                        // (z**deg_z)
                    )
                else:
                    pol += orig.monomial_coefficient(mono) * mono.subs(z=x * y + 1)
            monomials.append(x ** (u - deg) * y ** (u + j - deg) * z**deg)
            shifts.append(pol(X * x, Y * y, Z * z) * eM ** (m - u) * M**deg)
    scales = [mono(X, Y, Z) for mono in monomials]
    n = len(shifts)
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()
    # L = L.LLL(delta=0.75)
    s = fplll_fmt(L)
    file_name = "tk14_output.txt"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(s)

    try:
        rst = subprocess.Popen(
            "tk14_flatter.nu",
            text=True,
            stdout=subprocess.PIPE,
            shell=True,
        )

        L = fplll_read(rst.stdout)
    except subprocess.CalledProcessError as e:
        return
    
    pols = [z - x * y - 1]
    for i in range(n):
        pol = 0
        for j in range(n):
            pol += L[i, j] * monomials[j] // scales[j]
        pols.append(pol)
    print(time() - start)
    x0 = groebner(pols, x, X)
    if x0:
        return (x0 * N) // e


def low_leak_2(N, e, d_low, d_len, leak_len, A, X, Y, m, t):
    beta = d_len / N.nbits()
    gamma = (d_len - leak_len) / N.nbits()
    PR = ZZ['x, y']
    x, y = PR.gens()
    f = x * (A + y) + 1 - e * d_low
    M = 1 << leak_len
    eM = e * M
    shifts = []
    monomials = []
    for u in range(m + 1):
        for i in range(u + 1):
            monomials.append(x ** u * y ** i)
            shifts.append((x ** (u - i) * f ** i)(X * x, Y * y) * eM ** (m - i))
        for j in range(1, t):
            monomials.append(x ** u * y ** (u + j))
            shifts.append((y ** j * f ** u)(X * x, Y * y) * eM ** (m - u))
    scales = [mono(X, Y) for mono in monomials]
    n = len(shifts)
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()
    L = L.LLL(delta=0.75)
    pols = []
    for i in range(n):
        pol = 0
        for j in range(n):
            pol += L[i, j] * monomials[j] // scales[j]
        pols.append(pol)
    print(time() - start)
    x0 = groebner(pols, x, X)
    if x0:
        return (x0 * N) // e