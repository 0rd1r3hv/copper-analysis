from sage.all import *

MAX_M = 1000


def l_MSBs(x, km, t):
    return max(0, ceil((x - km) / (t + 1)))


def tk14_high(beta, gamma):
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    for m in range(1, MAX_M + 1):
        n = s_X = s_Y = s_Z = s_e = 0
        km = k * m
        for u in range(m + 1):
            for i in range(u + 1):
                l = l_MSBs(i, km, t)
                s_X += u - l
                s_Y += i - l
                s_Z += l
                s_e += m - i
                n += 1
            for j in range(1, floor(k * m + t * u) + 1):
                l = l_MSBs(u + j, km, t)
                s_X += u - l
                s_Y += u + j - l
                s_Z += l
                s_e += m - u
                n += 1
        if s_X * gamma + s_Y * 1 / 2 + s_Z * (beta + 1 / 2) + s_e < n * m:
            print((s_X * gamma + s_Y * 1 / 2 + s_Z * (beta + 1 / 2) + s_e - n * m) / n)
            print(s_X, s_Y, s_Z, s_e, n, m)
            return m


def tk17_large_e(alpha, beta, delta):
    tp = (1 - 2 * beta - delta) / (2 * beta)
    tq = (1 - beta - delta) / (1 - beta)
    for m in range(1, MAX_M + 1):
        n = s_X = s_Yp = s_Yq = s_e = 0
        for i in range(m + 1):
            for j in range(m - i + 1):
                n += 1
                s_X += i + j
                s_Yp += i
                s_e += m - i
            for j in range(1, ceil(tp * m)):
                n += 1
                s_X += i
                s_Yp += i + j
                s_e += m - i
        for i in range(1, m + 1):
            for j in range(1, ceil(tq * i)):
                n += 1
                s_X += i
                s_Yq += j
                s_e += m - i
        if (
            s_X * (alpha + beta + delta - 1)
            + s_Yp * beta
            + s_Yq * (1 - beta)
            + s_e * alpha
            < n * m * alpha
        ):
            print(
                (
                    s_X * (alpha + beta + delta - 1)
                    + s_Yp * beta
                    + s_Yq * (1 - beta)
                    + s_e * alpha
                    - n * m * alpha
                )
                / n
            )
            print(s_X, s_Yp, s_Yq, s_e, n, m)
            print(alpha + beta + delta - 1, beta, 1 - beta, alpha)
            return m


def tk17_small_e(alpha, beta, delta):
    l = (1 - beta - delta) / beta
    t = (1 - beta - delta) / (1 - beta)
    for m in range(1, MAX_M + 1):
        n = s_X = s_Yp = s_Yq = s_e = 0
        for i in range(m + 1):
            for j in range(m - i + 1):
                n += 1
                s_X += i + j
                s_Yp += ceil(l * i)
                s_Yq += floor((1 - l) * i)
                s_e += m - i
        for i in range(1, m + 1):
            for j in range(1, ceil(t * i) - floor((1 - l) * i) + 1):
                n += 1
                s_X += i
                s_Yq += floor((1 - l) * i) + j
                s_e += m - i
        if (
            s_X * (alpha + beta + delta - 1)
            + s_Yp * beta
            + s_Yq * (1 - beta)
            + s_e * alpha
            < n * m * alpha
        ):
            print(
                (
                    s_X * (alpha + beta + delta - 1)
                    + s_Yp * beta
                    + s_Yq * (1 - beta)
                    + s_e * alpha
                    - n * m * alpha
                )
                / n
            )
            print(s_X, s_Yp, s_Yq, s_e, n, m)
            print(alpha + beta + delta - 1, beta, 1 - beta, alpha)
            return m


def tk17_small_dp_dq(alpha, delta):
    t = 1 - 2 * delta
    for m in range(1, MAX_M + 1):
        n = s_X = s_Y = s_e = 0
        indices = []
        for i1 in range(m // 2 + 1):
            for i2 in range(m // 2 + 1):
                for u in range(min(m // 2 - i1, m // 2 - i2) + 1):
                    indices.append([i1, i2, 0, 0, u])
        for i1 in range(m // 2):
            for i2 in range(1, m // 2 + 1):
                for u in range(min(m // 2 - i1 - 1, m // 2 - i2) + 1):
                    indices.append([i1, i2, 1, 0, u])
        for i1 in range(m // 2 + 1):
            for j1 in range(1, m // 2 - i1 + 1):
                for u in range(m // 2 - i1 - j1 + 1):
                    indices.append([i1, 0, j1, 0, u])
        for i2 in range(m // 2 + 1):
            for j2 in range(1, m // 2 - i2 + 1):
                for u in range(m // 2 - i2 - j2 + 1):
                    indices.append([0, i2, 0, j2, u])
        for i1, i2, j1, j2, u in indices:
            n += 1
            s_X += i1 + i2 + j1 + j2 + 2 * u
            s_Y += (i1 + i2 + 1) // 2
            s_e += m - (i1 + i2 + u)
        for i1 in range(m // 2 + 1):
            for i2 in range(m // 2 + 1):
                for j1 in range(1, floor(t * (i1 + i2)) - (i1 + i2 + 1) // 2 + 1):
                    n += 1
                    s_X += i1 + i2
                    s_Y += (i1 + i2 + 1) // 2 + j1
                    s_e += m - (i1 + i2)
        for i1 in range(m // 2 + 1):
            for i2 in range(m // 2 + 1):
                for j2 in range(1, floor(t * (i1 + i2)) - (i1 + i2) // 2 + 1):
                    n += 1
                    s_X += i1 + i2
                    s_Y += (i1 + i2) // 2 + j2
                    s_e += m - (i1 + i2)
        if (
            s_X * (alpha + delta - 1 / 2)
            + s_Y / 2
            + s_e * alpha
            < n * m * alpha
        ):
            print(
                (
                    s_X * (alpha + delta - 1 / 2)
                    + s_Y / 2
                    + s_e * alpha
                    - n * m * alpha
                ) / n
            )
            print(s_X, s_Y, s_e, n, m)
            print(alpha + delta - 1 / 2, 1 / 2, alpha)
            return m