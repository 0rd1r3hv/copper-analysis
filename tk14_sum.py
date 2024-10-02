from sage.all import *

var('u', 'i', 'j', 'm', 'k', 't', 'a', 'b', 'd', 'e', 'g', 'l', 'x', 'y')
eq = (2 * x ** 2 - 2 * (1 + y) * x + 2 * y ** 2 - 2 * y + 1 == 0).subs(x=(1 - 2 * k - t) /2, y=(1 - k - t) / 2)
general = eq.subs(k=(a+b-g-1)/e, t=(2-a-e+g+l-2*b)/e)
print(general.solve(g))