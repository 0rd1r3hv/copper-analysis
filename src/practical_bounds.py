from sage.all import ceil, floor, Rational
from src.misc import calc_bits


MAX_M = 1000


def l_MSBs(x, km, t):
    return max(0, ceil((x - km) / (t + 1)))


def l_LSBs(x, km, t):
    return max(0, ceil((x - km) / t))


# X, Y, Z, W
def ernst05_eq1(bounds=None, props=None):
    if bounds:
        x, y, z, w = calc_bits(bounds)
    else:
        x, y, z, w = props
    for m in range(1, MAX_M + 1):
        for t in range(m + 1):
            sx = sy = sz = sw = dim = 0
            for i in range(m + 1):
                for j in range(m - i + 1):
                    for k in range(j + t + 1):
                        dim += 1
            sx = sy = sz = dim * m
            sz += dim * t
            for i in range(m + 2):
                j = m + 1 - i
                for k in range(j + t + 1):
                    sx += m + i
                    sy += m + j
                    sz += m + t + k
                    sw += 1
                    dim += 1
            if sx * x + sy * y + sz * z + sw * w < dim * (m * (x + y + z) + t * z + w):
                print(f"sx: {sx} sy: {sy} sz: {sz} sw: {sw} dim: {dim} m: {m} t: {t}")
                return m, t


def ernst05_eq2(bounds=None, props=None):
    if bounds:
        x, y, z, w = calc_bits(bounds)
    else:
        x, y, z, w = props
    for m in range(1, MAX_M + 1):
        for t in range(m + 1):
            sx = sy = sz = sw = dim = 0
            for i in range(m + 1):
                for j in range(m - i + t + 1):
                    for k in range(m - i + 1):
                        dim += 1
            sx = sy = sz = dim * m
            sy += dim * t
            for i in range(m + 2):
                k = m + 1 - i
                for j in range(m + t + 1 - i + 1):
                    sx += m + i
                    sy += m + t + j
                    sz += m + k
                    sw += 1
                    dim += 1
            for i in range(m + 1):
                j = m + t + 1 - i
                for k in range(m - i + 1):
                    sx += m + i
                    sy += m + t + j
                    sz += m + k
                    sw += 1
                    dim += 1
            if sx * x + sy * y + sz * z + sw * w < dim * (m * (x + y + z) + t * y + w):
                print(f"sx: {sx} sy: {sy} sz: {sz} sw: {sw} dim: {dim} m: {m} t: {t}")
                return m, t


def tk14_msb_1(beta, gamma):
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
            print(f"自动使用参数：m = {m}")
            print(f"格的维度：dim = {n}")
            print(
                f"格行列式中各项幂次：s_X = {s_X}, s_Y = {s_Y}, s_Z = {s_Z}, s_e = {s_e}"
            )
            return m


def tk14_lsb(beta, gamma):
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    for m in range(1, MAX_M + 1):
        n = s_X = s_Y = s_Z = s_e = s_M = 0
        km = k * m
        for u in range(m + 1):
            for i in range(u + 1):
                s_X += u
                s_Y += i
                s_e += m - i
                s_M += m - i
                n += 1
            for j in range(1, floor(k * m + t * u) + 1):
                l = l_LSBs(j, km, t)
                s_X += u - l
                s_Y += u + j - l
                s_Z += l
                s_e += m - u
                s_M += m - u + l
                n += 1
        if s_X * beta + s_Y * 1 / 2 + s_Z * (beta + 1 / 2) + s_e + s_M * (
            beta - gamma
        ) < n * m * (1 + beta - gamma):
            print(
                f"s_X: {s_X} s_Y: {s_Y} s_Z: {s_Z} s_e: {s_e} s_M: {s_M} n: {n} m: {m}"
            )
            print(
                f"s_X * beta + s_Y * 1 / 2 + s_Z * (beta + 1 / 2) + s_e + s_M * (beta - gamma) - n * m * (1 + beta - gamma): {(s_X * beta + s_Y * 1 / 2 + s_Z * (beta + 1 / 2) + s_e + s_M * (beta - gamma) - n * m * (1 + beta - gamma)) / n}"
            )
            return m


def tk14_mixed(beta, delta, eta=Rational("1/2")):
    for m in range(1, MAX_M + 1):
        for t in range(m + 1):
            s_w = s_x = s_y = s_em = dim = 0
            for u in range(m + 1):
                for i in range(u + 1):
                    deg = max(0, i - t)
                    s_w += deg
                    s_x += u - deg
                    s_y += i
                    s_em += m - i
                    dim += 1
                for j in range(1, t + 1):
                    deg = max(0, u + j - t)
                    s_w += deg
                    s_x += u - deg
                    s_y += u + j
                    s_em += m - u
                    dim += 1
            if s_w * beta + s_x * delta + s_y * eta + s_em < dim * m:
                print(
                    f"s_w: {s_w} s_x: {s_x} s_y: {s_y} s_em: {s_em} dim: {dim} m: {m} t: {t}"
                )
                return m, t


def tk14_low_2(kbeta, gamma):
    for m in range(1, MAX_M + 1):
        for t in range(m + 1):
            s_X = s_Y = s_eM = n = 0
            for u in range(m + 1):
                for i in range(u + 1):
                    s_X += u
                    s_Y += i
                    s_eM += m - i
                    n += 1
                for j in range(1, t):
                    s_X += u
                    s_Y += u + j
                    s_eM += m - u
                    n += 1
            if s_X * kbeta + s_Y * 1 / 2 + s_eM * (1 + kbeta - gamma) < n * m * (
                1 + kbeta - gamma
            ):
                print(f"s_X: {s_X} s_Y: {s_Y} s_eM: {s_eM} n: {n} m: {m}")
                print(
                    f"s_X * kbeta + s_Y * 1 / 2 + s_eM * (1 + kbeta - gamma) - n * m * (1 + kbeta - gamma): {s_X * kbeta + s_Y * 1 / 2 + s_eM * (1 + kbeta - gamma) - n * m * (1 + kbeta - gamma)}"
                )
                return m, t


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
            print(f"s_X: {s_X} s_Yp: {s_Yp} s_Yq: {s_Yq} s_e: {s_e} n: {n} m: {m}")
            print(
                f"s_X * (alpha + beta + delta - 1) + s_Yp * beta + s_Yq * (1 - beta) + s_e * alpha - n * m * alpha: {(s_X * (alpha + beta + delta - 1) + s_Yp * beta + s_Yq * (1 - beta) + s_e * alpha - n * m * alpha) / n}"
            )
            print(
                f"alpha + beta + delta - 1: {alpha + beta + delta - 1} beta: {beta} 1 - beta: {1 - beta} alpha: {alpha}"
            )
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
            print(f"s_X: {s_X} s_Yp: {s_Yp} s_Yq: {s_Yq} s_e: {s_e} n: {n} m: {m}")
            print(
                f"s_X * (alpha + beta + delta - 1) + s_Yp * beta + s_Yq * (1 - beta) + s_e * alpha - n * m * alpha: {(s_X * (alpha + beta + delta - 1) + s_Yp * beta + s_Yq * (1 - beta) + s_e * alpha - n * m * alpha) / n}"
            )
            print(
                f"alpha + beta + delta - 1: {alpha + beta + delta - 1} beta: {beta} 1 - beta: {1 - beta} alpha: {alpha}"
            )
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
        if s_X * (alpha + delta - 1 / 2) + s_Y / 2 + s_e * alpha < n * m * alpha:
            print(f"s_X: {s_X} s_Y: {s_Y} s_e: {s_e} n: {n} m: {m}")
            print(
                f"s_X * (alpha + delta - 1 / 2) + s_Y / 2 + s_e * alpha - n * m * alpha: {(s_X * (alpha + delta - 1 / 2) + s_Y / 2 + s_e * alpha - n * m * alpha) / n}"
            )
            return m


def mns21_dp_dq_with_lsb(alpha, delta1, delta2, leak):
    t = max(1 - 2 * max(delta1, delta2), 1 / 2)
    for m in range(1, MAX_M + 1):
        for thres in range(m + 1):
            s_X = s_Y = s_Z = s_M = s_eM = dim = 0
            for c in range(m + 1):
                for a in range(m + 1):
                    b = 0
                    while (b + 1) // 2 <= thres:
                        if b <= a + c:
                            if a <= c and b <= c - a:
                                ef = 0
                                eg = b
                                eh = a
                            elif a > c and b < a - c:
                                ef = b
                                eg = 0
                                eh = c
                            elif (a + b + c) % 2 == 0:
                                ef = (a + b - c) // 2
                                eg = (-a + b + c) // 2
                                eh = (a - b + c) // 2
                            else:
                                ef = (a + b - c + 1) // 2
                                eg = (-a + b + c - 1) // 2
                                eh = (a - b + c - 1) // 2
                        else:
                            ef = a
                            eg = c
                            eh = 0
                        deg = ef + eg + eh
                        s_X += a
                        s_Y += (b + 1) // 2
                        s_Z += c
                        s_eM += 2 * m - deg
                        dim += 1
                        b += 1
            for c in range(m + 1):
                for a in range(m + 1):
                    for b in range(a + c + 1):
                        if (b + 1) // 2 > thres or b == a + c:
                            if a <= c and b <= c - a:
                                ef = 0
                                eg = b
                                eh = a
                            elif a > c and b < a - c:
                                ef = b
                                eg = 0
                                eh = c
                            elif (a + b + c) % 2 == 0:
                                ef = (a + b - c) // 2
                                eg = (-a + b + c) // 2
                                eh = (a - b + c) // 2
                            else:
                                ef = (a + b - c + 1) // 2
                                eg = (-a + b + c - 1) // 2
                                eh = (a - b + c - 1) // 2
                            deg = ef + eg + eh
                            if (b + 1) // 2 > thres:
                                s_X += a
                                s_Y += (b + 1) // 2
                                s_Z += c
                                s_M += deg
                                s_eM += 2 * m - deg
                                dim += 1
                            if b == a + c:
                                for i in range(
                                    max(1, thres - b // 2 + 1),
                                    floor(t * b - b // 2) + 1,
                                ):
                                    s_X += a
                                    s_Y += b // 2 + i
                                    s_Z += c
                                    s_M += deg
                                    s_eM += 2 * m - deg
                                    dim += 1
                                for i in range(
                                    max(1, thres - (b + 1) // 2 + 1),
                                    floor(t * b - (b + 1) // 2) + 1,
                                ):
                                    s_X += a
                                    s_Y += (b + 1) // 2 + i
                                    s_Z += c
                                    s_M += deg
                                    s_eM += 2 * m - deg
                                    dim += 1
            if s_X * (alpha + delta1 - 1 / 2) + s_Y / 2 + s_Z * (
                alpha + delta2 - 1 / 2
            ) + s_M * leak + s_eM * (alpha + leak) < dim * 2 * m * (alpha + leak):
                print(f"自动使用攻击参数：m = {m}, s = {thres}")
                print(f"格的维度：dim = {dim}")
                print(
                    f"格行列式中各项幂次：s_X = {s_X}, s_Y = {s_Y}, s_Z = {s_Z}, s_e = {s_eM}, s_M = {s_eM+s_M}"
                )
                return m, thres


# mns21_dp_dq_with_lsb(1, 0.07, 0.07, 0.03)
# tk17_small_dp_dq(1, 0.05)
# tk14_high(0.3, 0.27)
# tk14_low_1(0.3, 0.27)
# tk14_low_2(0.4, 0.17)
# ernst05_eq1(props=[0.07, 0.7, 0.5, 1 + 0.7])
# beta = 0.7
# ernst05_eq2(props=[0.074, 0.2, 0.5, 1 + 0.2])
