from sage.all import *
MAX_M= 1000

def l_MSBs(x, km, t):
    return max(0, ceil((x - km) / (t + 1)))

def tk14_high(beta, gamma):
    k = 2 * (beta - gamma)
    t = 1 + 2 * gamma - 4 * beta
    for m in range(1, MAX_M):
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
            for j in range(1, floor(k * m + t * u)):
                l = l_MSBs(u + j, km, t)
                s_X += u - l
                s_Y += u + j - l
                s_Z += l
                s_e += m - u
                n += 1
        if s_X * gamma + s_Y * 1 / 2 + s_Z * (beta + 1 / 2) +  s_e < n * m:
            print(s_X * gamma + s_Y * 1 / 2 + s_Z * (beta + 1 / 2) +  s_e - n * m)
            print(n)
            return m

print(tk14_high(0.35, 0.6 * 0.35))