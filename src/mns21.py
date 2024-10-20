from sage.all import *
# from mp import groebner
from src.root_methods import groebner
from time import time
from src.fplll_fmt import fplll_fmt, fplll_read
import subprocess


def transform(PR, Q, pol, mono, mod, i):
    xp, xq, yp, yq, zp, zq = PR.gens()
    lifted = Q(pol).lift()
    pt1 = lifted.subs(yp=0)
    pt2 = lifted - pt1
    p = pt1.subs(xp=xq + 1, zp=zq - 1) + pt2.subs(xq=xp - 1, zq=zp + 1)
    if i == 0:
        return p
    mod = mod ** i
    coef = p.monomial_coefficient(mono)
    if coef < 0:
        p = -p
    g = gcd(coef, mod)
    return (p * inverse_mod(abs(coef) // g, mod // g)) % mod

def dp_dq_with_lsb(N, e, delta1, delta2, ldp, ldq, m_thres, x1, x2, x3, x4, x5, x6, l_leak=None, M=None):
    m, thres = m_thres
    if M is None:
        M = 1 << l_leak
    PR = ZZ['xp, xq, yp, yq, zp, zq']
    xp, xq, yp, yq, zp, zq = PR.gens()
    Q = PR.quotient(N - yp * yq)
    X = 1 + (1 << (e.nbits() + floor(N.nbits() * (delta1 - 1 / 2))))
    Y = 3 + (1 << (N.nbits() // 2))
    Z = 5 + (1 << (e.nbits() + floor(N.nbits() * (delta2 - 1 / 2))))
    t = max(1 - 2 * max(delta1, delta2), 1 / 2)
    f_b = xp * yp - xq - e * ldp
    g_b = yp * zp - N * zq + e * ldq * yp
    h_b = N * xp * zq - xq * zp - e ** 2 * ldp * ldq - e * ldp * zp - e * ldq * xq
    f = M * (xp * yp - xq)
    g = M * (yp * zp - N * zq)
    h = M * (N * xp * zq - xq * zp)
    eM = e * M
    shifts = []
    monomials = []
    order = []
    for c in range(m + 1):
        for a in range(m + 1):
            b = 0
            while (b + 1) // 2 <= thres:
                if b <= a + c:
                    if a <= c and b <= c - a:
                        ef = 0
                        eg = b
                        eh = a
                        ex = 0
                        ez = -a - b + c
                    elif a > c and b < a - c:
                        ef = b
                        eg = 0
                        eh = c
                        ex = a - b - c
                        ez = 0
                    elif (a + b + c) % 2 == 0:
                        ef = (a + b - c) // 2
                        eg = (-a + b + c) // 2
                        eh = (a - b + c) // 2
                        ex = 0
                        ez = 0
                    else:
                        ef = (a + b - c + 1) // 2
                        eg = (-a + b + c - 1) // 2
                        eh = (a - b + c - 1) // 2
                        ex = 0
                        ez = 1
                else:
                    ef = a
                    eg = c
                    eh = 0
                    ex = 0
                    ez = 0
                deg = ef + eg + eh
                p = f_b ** ef * g_b ** eg * h_b ** eh * xp ** ex * zp ** ez
                if b <= a + c:
                    p *= yq ** (b // 2)
                elif b % 2 == 0:
                    p *= yq ** ((a + c) // 2 + (b - a - c + 1) // 2)
                else:
                    p *= yq ** ((a + c) // 2) * yp ** ((b - a - c + 1) // 2)
                if b % 2 == 0:
                    monomials.append(xq ** a * yq ** ((b + 1) // 2) * zq ** c)
                else:
                    monomials.append(xp ** a * yp ** ((b + 1) // 2) * zp ** c)
                shifts.append(transform(PR, Q, p, monomials[-1], eM, deg)(X * xp, X * xq, Y * yp, Y * yq, Z * zp, Z * zq) * (eM ** (2 * m - deg)))
                order.append((c, a, b))
                b += 1
    for c in range(m + 1):
        for a in range(m + 1):
            for b in range(a + c + 1):
                if (b + 1) // 2 > thres or b == a + c:
                    if a <= c and b <= c - a:
                        ef = 0
                        eg = b
                        eh = a
                        ex = 0
                        ez = -a - b + c
                    elif a > c and b < a - c:
                        ef = b
                        eg = 0
                        eh = c
                        ex = a - b - c
                        ez = 0
                    elif (a + b + c) % 2 == 0:
                        ef = (a + b - c) // 2
                        eg = (-a + b + c) // 2
                        eh = (a - b + c) // 2
                        ex = 0
                        ez = 0
                    else:
                        ef = (a + b - c + 1) // 2
                        eg = (-a + b + c - 1) // 2
                        eh = (a - b + c - 1) // 2
                        ex = 0
                        ez = 1
                    deg = ef + eg + eh
                    p = f ** ef * g ** eg * h ** eh * xp ** ex * zp ** ez * yq ** (b // 2)
                    if (b + 1) // 2 > thres:
                        if b % 2 == 0:
                            monomials.append(xq ** a * yq ** ((b + 1) // 2) * zq ** c)
                        else:
                            monomials.append(xp ** a * yp ** ((b + 1) // 2) * zp ** c)
                        shifts.append(transform(PR, Q, p, monomials[-1], eM, deg)(X * xp, X * xq, Y * yp, Y * yq, Z * zp, Z * zq) * (eM ** (2 * m - deg)))
                        order.append((c, a, b))
                    if b == a + c:
                        mono = xq ** a * yq ** (b // 2) * zq ** c
                        for i in range(max(1, thres - b // 2 + 1), floor(t * b - b // 2) + 1):
                            monomials.append(mono * yq ** i)
                            shifts.append(transform(PR, Q, p * yq ** i, monomials[-1], eM, deg)(X * xp, X * xq, Y * yp, Y * yq, Z * zp, Z * zq) * (eM ** (2 * m - deg)))
                            order.append((c, a, b))
                        mono = xp ** a * yp ** ((b + 1) // 2) * zp ** c
                        for i in range(max(1, thres - (b + 1) // 2 + 1), floor(t * b - (b + 1) // 2) + 1):
                            monomials.append(mono * yp ** i)
                            shifts.append(transform(PR, Q, p * yp ** i, monomials[-1], eM, deg)(X * xp, X * xq, Y * yp, Y * yq, Z * zp, Z * zq) * (eM ** (2 * m - deg)))
                            order.append((c, a, b))
    n = len(shifts)
    ords_monos_shifts = [(order[i], monomials[i], shifts[i]) for i in range(n)]
    ords_monos_shifts.sort(key=lambda e: (e[0][0], e[0][1], e[0][2]))
    monomials = [_[1] for _ in ords_monos_shifts]
    scales = [mono(X, X, Y, Y, Z, Z) for mono in monomials]
    shifts = [_[2] for _ in ords_monos_shifts]
    start = time()
    L = Matrix(ZZ, n)
    for i in range(n):
        for j in range(i + 1):
            L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    for i in range(n):
        pol = 0
        for j in range(i + 1):
            pol += L[i, j] * monomials[j]
        assert pol == shifts[i]
    # L = L.LLL(delta=0.75)
    s = fplll_fmt(L)
    file_name = "mns21_output.txt"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(s)

    try:
        rst = subprocess.Popen(
            "mns21_flatter.nu",
            text=True,
            stdout=subprocess.PIPE,
            shell=True,
        )
        L = fplll_read(rst.stdout)
    except subprocess.CalledProcessError as e:
        print(e)
        return
    
    pols = [N - yp * yq, xp - xq - 1, zp - zq + 1]
    for i in range(10):
        pol = 0
        for j in range(n):
            pol += L[i, j] * monomials[j] // scales[j]
        pols.append(pol)
    print(time() - start)
    p0 = groebner(pols, yp, Y, N=N)
    assert p0 == x3
    return p0