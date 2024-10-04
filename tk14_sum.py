from sage.all import *

var('u', 'i', 'j', 'm', 'k', 't', 'a', 'b', 'd', 'e', 'g', 's', 'l', 'x', 'y')
eq1 = (2 * x ** 2 - 2 * (1 + y) * x + 2 * y ** 2 - 2 * y + 1 == 0).subs(x=(1 - 2 * k - t) /2, y=(1 - k - t) / 2)
general1 = eq1.subs(k=(a+b-g-1)/e, t=(2-a-e+g+l-2*b)/e)
print(general1.solve(g))
eq2 = ((6 * x * s - 3 * s ** 2 + 2 * s ** 3) * (2 + 2 * x - 4 * y) - (s - 2 * (x - y)) ** 3).subs(x=(1 - 2 * k - t) /2, y=(1 - k - t) / 2)
general2 = eq2.subs(k=(a+b-g-1)/e, t=(2-a-e+g+l-2*b)/e)
print(general2)