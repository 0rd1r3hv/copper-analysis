from sage.all import *
from root_methods import groebner
from time import time
from fplll_fmt import *
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

    s = encode_fplll_format(L)
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
        L = read_fplll_format(rst.stdout)
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


def small_e(N, e, m, beta, delta, x1, x2, y1, y2):
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
                monomials.append(xp**(i + j) * yp**ceil(l * i))
            else:
                monomials.append(xq**(i + j) * yq**floor((1 - l) * i))
            if i != 0:
                orig = Q(xp ** j * (N * xq - xp * yp) ** ceil(l * i) * (xq * yq - xp) ** floor((1 - l) * i)).lift()
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
            assert Integer(shifts[-1](x1 / X, x2 / X, y1 / Yp, y2 / Yq)) % (e ** m) == 0
    for i in range(1, m + 1):
        for j in range(1, ceil(t * i) - floor((1 - l) * i) + 1):
            orig = Q(yq ** j * (N * xq - xp * yp) ** ceil(l * i) * (xq * yq - xp) ** floor((1 - l) * i)).lift()
            pt1 = orig.subs(yq=0)
            pt2 = orig - pt1
            trans = pt1.subs(xq=xp + 1) + pt2.subs(xp=xq - 1)
            monomials.append(xq**i * yq**(floor((1 - l) * i + j)))
            times = trans.monomial_coefficient(monomials[-1]).valuation(N)
            inv = inverse_mod(N**times, e**i)
            shifts.append(
                ((trans * inv) % (e**i))(X * xp, X * xq, Yp * yp, Yq * yq)
                * e ** (m - i)
            )
            assert Integer(shifts[-1](x1 / X, x2 / X, y1 / Yp, y2 / Yq)) % (e ** m) == 0
    n = len(shifts)
    print(n)
    scales = [mono(X, X, Yp, Yq) for mono in monomials]
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    start = time()
    L = L.LLL(delta=0.75)
    '''
    s = encode_fplll_format(L)
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
        L = read_fplll_format(rst.stdout)
    except subprocess.CalledProcessError as e:
        print(e)
        return
    '''
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