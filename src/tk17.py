from sage.all import Matrix, ZZ, inverse_mod, Integer, gcd, ceil, floor
# from mp import groebner
from src.root_methods import groebner
from time import time
from src.fplll_fmt import fplll_fmt, fplll_read
import subprocess
# Small CRT-Exponent RSA Revisited


# Small dq Attack, Attack for Large e
def large_e(N, e, m, beta, delta):
    PR = ZZ["xp, xq, yp, yq"]
    xp, xq, yp, yq = PR.gens()
    Q = PR.quotient(N - yp * yq)
    tp = (1 - 2 * beta - delta) / (2 * beta)
    tq = (1 - beta - delta) / (1 - beta)
    X = 1 << (e.nbits() + floor(N.nbits() * (delta + beta - 1)))
    Yp = 1 << (floor(N.nbits() * beta))
    Yq = 1 << (floor(N.nbits() * (1 - beta)))
    fp = N + xp * (N - yp)
    shifts = []
    monomials = []
    for i in range(m + 1):
        for j in range(0, m - i + 1):
            monomials.append(xp ** (i + j) * yp**i)
            shifts.append((xp**j * fp**i).subs(xp=X * xp, yp=Yp * yp) * e ** (m - i))
    for i in range(m + 1):
        for j in range(1, ceil(tp * m)):
            monomials.append(xp**i * yp ** (i + j))
            shifts.append((yp**j * fp**i).subs(xp=X * xp, yp=Yp * yp) * e ** (m - i))
    for i in range(1, m + 1):
        for j in range(1, ceil(tq * i)):
            orig = Q((N * xq - xp * yp) ** (i - j) * (xq * yq - xp) ** j).lift()
            pt1 = orig.subs(yq=0)
            pt2 = orig - pt1
            trans = pt1.subs(xq=xp + 1) + pt2.subs(xp=xq - 1)
            monomials.append(xq**i * yq**j)
            times = trans.monomial_coefficient(monomials[-1]).valuation(N)
            inv = inverse_mod(N**times, e**i)
            shifts.append(
                ((trans * inv) % (e**i))(X * xp, X * xq, Yp * yp, Yq * yq)
                * e ** (m - i)
            )
    n = len(shifts)
    print(n)
    scales = [mono(X, X, Yp, Yq) for mono in monomials]
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()

    s = fplll_fmt(L)
    file_name = "output.txt"

    # 写入文件，覆盖之前的内容
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(s)

    try:
        rst = subprocess.Popen(
            "flatter.nu",
            text=True,
            stdout=subprocess.PIPE,
            shell=True,
        )
        L = fplll_read(rst.stdout)
    except subprocess.CalledProcessError as e:
        print(e)
        return

    k, p, q = ZZ["k, p, q"].gens()
    pols = [N - p * q]
    # pols = [N - yp * yq, xq - xp - 1]
    for i in range(n):
        pol = 0
        for j in range(n):
            pol += L[i, j] * monomials[j] // scales[j]
        pols.append(pol(k - 1, k, p, q))
    print(time() - start)
    # p0 = groebner(pols, yp, Yp)
    p0 = groebner(pols, p, Yp)
    return p0


def small_e(N, e, m, beta, delta):
    PR = ZZ["xp, xq, yp, yq"]
    xp, xq, yp, yq = PR.gens()
    Q = PR.quotient(N - yp * yq)
    l = (1 - beta - delta) / beta
    t = (1 - beta - delta) / (1 - beta)
    X = 1 << (e.nbits() + floor(N.nbits() * (delta + beta - 1)))
    Yp = 1 << (floor(N.nbits() * beta))
    Yq = 1 << (floor(N.nbits() * (1 - beta)))
    shifts = []
    monomials = []
    for i in range(m + 1):
        for j in range(m - i + 1):
            if i == 0 or ceil(l * i) - ceil(l * (i - 1)) == 1:
                monomials.append(xp ** (i + j) * yp ** ceil(l * i))
            else:
                monomials.append(xq ** (i + j) * yq ** floor((1 - l) * i))
            if i != 0:
                orig = Q(
                    xp**j
                    * (N * xq - xp * yp) ** ceil(l * i)
                    * (xq * yq - xp) ** floor((1 - l) * i)
                ).lift()
                pt1 = orig.subs(yq=0)
                pt2 = orig - pt1
                trans = pt1.subs(xq=xp + 1) + pt2.subs(xp=xq - 1)
                times = trans.monomial_coefficient(monomials[-1]).valuation(N)
                inv = inverse_mod(N**times, e**i)
                shifts.append(
                    ((trans * inv) % (e**i))(X * xp, X * xq, Yp * yp, Yq * yq)
                    * e ** (m - i)
                )
            else:
                shifts.append((X * xp) ** j * e ** m)
    for i in range(1, m + 1):
        for j in range(1, ceil(t * i) - floor((1 - l) * i) + 1):
            orig = Q(
                yq**j
                * (N * xq - xp * yp) ** ceil(l * i)
                * (xq * yq - xp) ** floor((1 - l) * i)
            ).lift()
            pt1 = orig.subs(yq=0)
            pt2 = orig - pt1
            trans = pt1.subs(xq=xp + 1) + pt2.subs(xp=xq - 1)
            monomials.append(xq**i * yq ** (floor((1 - l) * i + j)))
            times = trans.monomial_coefficient(monomials[-1]).valuation(N)
            inv = inverse_mod(N**times, e**i)
            shifts.append(
                ((trans * inv) % (e**i))(X * xp, X * xq, Yp * yp, Yq * yq)
                * e ** (m - i)
            )
    n = len(shifts)
    print(n)
    scales = [mono(X, X, Yp, Yq) for mono in monomials]
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()
    # L = L.LLL(delta=0.75)

    s = fplll_fmt(L)
    file_name = "output.txt"

    # 写入文件，覆盖之前的内容
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(s)

    try:
        rst = subprocess.Popen(
            "flatter.nu",
            text=True,
            stdout=subprocess.PIPE,
            shell=True,
        )
        L = fplll_read(rst.stdout)
    except subprocess.CalledProcessError as e:
        print(e)
        return

    k, p, q = ZZ["k, p, q"].gens()
    pols = [N - p * q]
    # pols = [N - yp * yq, xq - xp - 1]
    for i in range(n // 2):
        pol = 0
        for j in range(n):
            pol += L[i, j] * monomials[j] // scales[j]
        pols.append(pol(k - 1, k, p, q))
    print(time() - start)
    # p0 = groebner(pols, yp, Yp)
    p0 = groebner(pols, p, Yp)
    return p0


# Small dp and dq
def small_dp_dq(N, e, m, delta1, delta2):
    delta = max(delta1, delta2)
    PR = ZZ["xp1, xq1, xp2, xq2, yp, yq"]
    print(m)
    xp1, xq1, xp2, xq2, yp, yq= PR.gens()
    Q = PR.quotient(N - yp * yq)
    t = 1 - 2 * delta
    Xp = 1 << (e.nbits() + floor(N.nbits() * (delta1 - 1 / 2)))
    Xq = 1 << (e.nbits() + floor(N.nbits() * (delta2 - 1 / 2)))
    Y = 1 << (N.nbits() // 2)
    fp1 = N * xq1 - xp1 * yp
    fp2 = xp2 * yp - xq2
    h = N * xp2 * xq1 - xp1 * xq2
    shifts = []
    monomials = []
    indices_1 = []
    indices_2 = []
    indices_3 = []
    for i1 in range(m // 2 + 1):
        for i2 in range(m // 2 + 1):
            for u in range(min(m // 2 - i1, m // 2 - i2) + 1):
                indices_1.append([i1, i2, 0, 0, u])
    for i1 in range(m // 2):
        for i2 in range(1, m // 2 + 1):
            for u in range(min(m // 2 - i1 - 1, m // 2 - i2) + 1):
                indices_1.append([i1, i2, 1, 0, u])
    for i1 in range(m // 2 + 1):
        for j1 in range(1, m // 2 - i1 + 1):
            for u in range(m // 2 - i1 - j1 + 1):
                indices_1.append([i1, 0, j1, 0, u])
    for i2 in range(m // 2 + 1):
        for j2 in range(1, m // 2 - i2 + 1):
            for u in range(m // 2 - i2 - j2 + 1):
                indices_1.append([0, i2, 0, j2, u])
    indices_1 = sorted(indices_1, key=lambda e: (e[0] + e[1], e[4], e[2], e[3]))
    for i1 in range(m // 2 + 1):
        for i2 in range(m // 2 + 1):
            for j1 in range(1, floor(t * (i1 + i2)) - (i1 + i2 + 1) // 2 + 1):
                indices_2.append([i1, i2, j1])
    indices_2 = sorted(indices_2, key=lambda e: (e[0] + e[1], e[2]))
    for i1 in range(m // 2 + 1):
        for i2 in range(m // 2 + 1):
            for j2 in range(1, floor(t * (i1 + i2)) - (i1 + i2) // 2 + 1):
                indices_3.append([i1, i2, j2])
    indices_3 = sorted(indices_3, key=lambda e: (e[0] + e[1], e[2]))
    for i1, i2, j1, j2, u in indices_1:
        if (i1 + i2) % 2 == 1:
            monomials.append(xp1 ** (i1 + j1 + u) * xp2 ** (i2 + j2 + u) * yp ** ((i1 + i2 + 1) // 2))
        else:
            monomials.append(xq1 ** (i1 + j1 + u) * xq2 ** (i2 + j2 + u) * yq ** ((i1 + i2 + 1) // 2))
        if i1 + i2 + u != 0:
            orig = Q(xp1 ** j1 * xp2 ** j2 * yq ** ((i1 + i2) // 2) * fp1 ** i1 * fp2 ** i2).lift() * h ** u
            pt2 = orig.subs(yp=0)
            pt1 = orig - pt2
            pol = pt1.subs(xq1=xp1 + 1, xq2=xp2 - 1) + pt2.subs(xp1=xq1 - 1, xp2=xq2 + 1)
            coef = pol.monomial_coefficient(monomials[-1])
            if abs(coef) != 1:
                g = gcd(abs(coef), e ** (i1 + i2 + u))
                if coef < 0:
                    pol = -pol
                pol = (pol * inverse_mod(abs(coef) // g, (e ** (i1 + i2 + u)) // g)) % (e ** (i1 + i2 + u))
        else:
            pol = monomials[-1]
        # shifts.append(pol(X * xp1, X * xq1, X * xp2, X * xq2, Yp * yp, Yq * yq) * e ** (m - i1 - i2 - u))
        shifts.append(pol(Xp * xp1, Xq * xq1, Xp * xp2, Xq * xq2, Y * yp, Y * yq) * e ** (m - i1 - i2 - u))
    for i1, i2, j1 in indices_2:
        monomials.append(xp1 ** i1 * xp2 ** i2 * yp ** ((i1 + i2 + 1) // 2 + j1))
        if i1 + i2 != 0:
            orig = Q(yq ** ((i1 + i2) // 2 - j1) * fp1 ** i1 * fp2 ** i2).lift()
            pt2 = orig.subs(yp=0)
            pt1 = orig - pt2
            pol = pt1.subs(xq1=xp1 + 1, xq2=xp2 - 1) + pt2.subs(xp1=xq1 - 1, xp2=xq2 + 1)
            coef = pol.monomial_coefficient(monomials[-1])
            if abs(coef) != 1:
                g = gcd(abs(coef), e ** (i1 + i2))
                if coef < 0:
                    pol = -pol
                pol = (pol * inverse_mod(abs(coef) // g, (e ** (i1 + i2)) // g)) % (e ** (i1 + i2))
        else:
            pol = monomials[-1]
        # shifts.append(pol(X * xp1, X * xq1, X * xp2, X * xq2, Yp * yp, Yq * yq) * e ** (m - i1 - i2))
        shifts.append(pol(Xp * xp1, Xq * xq1, Xp * xp2, Xq * xq2, Y * yp, Y * yq) * e ** (m - i1 - i2))
    for i1, i2, j2 in indices_3:
        monomials.append(xq1 ** i1 * xq2 ** i2 * yq ** ((i1 + i2) // 2 + j2))
        if i1 + i2 != 0:
            orig = Q(yq ** ((i1 + i2) // 2 + j2) * fp1 ** i1 * fp2 ** i2).lift()
            pt2 = orig.subs(yp=0)
            pt1 = orig - pt2
            pol = pt1.subs(xq1=xp1 + 1, xq2=xp2 - 1) + pt2.subs(xp1=xq1 - 1, xp2=xq2 + 1)
            coef = pol.monomial_coefficient(monomials[-1])
            if abs(coef) != 1:
                g = gcd(abs(coef), e ** (i1 + i2))
                if coef < 0:
                    pol = -pol
                pol = (pol * inverse_mod(abs(coef) // g, (e ** (i1 + i2)) // g)) % (e ** (i1 + i2))
        else:
            pol = monomials[-1]
        # shifts.append(pol(X * xp1, X * xq1, X * xp2, X * xq2, Yp * yp, Yq * yq) * e ** (m - i1 - i2))
        shifts.append(pol(Xp * xp1, Xq * xq1, Xp * xp2, Xq * xq2, Y * yp, Y * yq) * e ** (m - i1 - i2))
    n = len(shifts)
    print(n)
    # scales = [mono(X, X, X, X, Yp, Yq) for mono in monomials]
    scales = [mono(Xp, Xq, Xp, Xq, Y, Y) for mono in monomials]
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()
    L = L.LLL(delta=0.75)
    
    # s = fplll_fmt(L)
    # file_name = "tk17_output.txt"

    # with open(file_name, "w", encoding="utf-8") as file:
    #     file.write(s)

    # try:
    #     rst = subprocess.Popen(
    #         "tk17_flatter.nu",
    #         text=True,
    #         stdout=subprocess.PIPE,
    #         shell=True,
    #     )
    #     L = fplll_read(rst.stdout)
    # except subprocess.CalledProcessError as e:
    #     print(e)
    #     return
    
    # kp, kq, p, q = ZZ["kp, kq, p, q"].gens()
    # pols = [N - p * q]
    pols = [N - yp * yq, xp1 - xq1 + 1, xp2 -xq2 - 1]
    for i in range(10):
        pol = 0
        for j in range(n):
            pol += L[i, j] * monomials[j] // scales[j]
        pols.append(pol)
    print(time() - start)
    p0 = groebner(pols, yp, Y, N=N)
    # p0 = groebner(pols, p, Y)
    return p0

