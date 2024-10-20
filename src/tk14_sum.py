from sage.all import *

var('u', 'i', 'j', 'm', 'k', 't', 'a', 'b', 'd', 'e', 'g', 's', 'l', 'x', 'y')
n = Rational('1/2') + k + t / 2
sx = Rational('1/6') + k / 2 + t / 6
sy = k / 2 + k ** 2 / 2 + k * t / 2 + t / 6 + t ** 2 / 6
sz = Rational('1/6') + t / 6
se = Rational('1/3') + k / 2 + t / 6


def solve(X, Y, Z, E, var):
    eq = (sx * X + sy * Y + sz * Z + se * E - n * E == 0)
    # K = (Z - X - Y) / Y
    # T = (X + Y + E - 2 * Z) / Y
    K = k
    T = -k
    print(K, T)
    print((K + T).full_simplify())
    return eq.subs(k=K, t=T).solve(var)


# tk 14 extension MSBs mixed with LSBs
# print(solve(X=d + l, Y=e, Z=e + b, E=a + l, var=d))
# tk 14 extension pure LSBs
# print(solve(X=b, Y=e, Z=e + b, E=a + b - d, var=d))
# print(solve(X=Rational('1/2'), Y=d, Z=d + 1, E=1, var=d))