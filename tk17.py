from sage.all import *
from root_methods import groebner
from time import time
from fplll_fmt import *
import subprocess
# Small CRT-Exponent RSA Revisited


# Small dq Attack, Attack for Large e
def small_dq(N, e, m, beta, deltay):
    PR = ZZ["xp, xq, yp, yq"]
    xp, xq, yp, yq = PR.gens()
    Q = PR.quotient(N - yp * yq)
    tp = (1 - 2 * beta - deltay) / (2 * beta)
    tq = (1 - beta - deltay) / (1 - beta)
    # tp = 1 / 2
    # tq = 1 / 2
    # print(tp, tq)
    X = 1 << (e.nbits() + floor(N.nbits() * (deltay + beta - 1)))
    Yp = (1 << (floor(N.nbits() * beta))) + 3
    Yq = (1 << (floor(N.nbits() * (1 - beta)))) + 1
    # print(X.bit_length(), Yp.bit_length(), Yq.bit_length())
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
    # print(n)
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
