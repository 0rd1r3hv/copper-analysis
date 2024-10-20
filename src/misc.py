from sage.all import *
from src.root_methods import groebner
from time import time


def assure_coprime(nums, n):
    res = []
    for num in nums:
        while gcd(num, n) != 1:
            num += 1
        res.append(num)
    return res


def scale_vars(varlst, bounds):
    return list(map(prod, zip(varlst, bounds)))


def poly_norm(pol, bounds, form):
    scaled = pol(scale_vars(pol.parent().gens(), bounds))
    if form == '1':
        return sum(map(abs, scaled).coefficients())
    elif form == 'inf':
        return max(scaled.coefficients(), key=abs)


def calc_bits(lst):
    return list(map(lambda e: Integer(e).nbits(), lst))


def solve_copper(shifts, bound_var, bounds, test, delta=0.75, ex_pols=[], select_num=None, N=None):
    if select_num is None:
        select_num = len(shifts)
    pol_seq = Sequence(shifts)
    L, monomials = pol_seq.coefficient_matrix()
    scales = list(map(lambda e: e(bounds)[0], monomials))
    monomials = vector(monomials)
    for col, scale in enumerate(scales):
        L.rescale_col(col, scale)
    start = time()
    L = L.dense_matrix().LLL(delta).change_ring(QQ)
    print(time() - start)
    for col, scale in enumerate(scales):
        L.rescale_col(col, 1 / scale)
    selected = list(filter(lambda e: test == None or e(test) == 0, L.change_ring(ZZ)[:select_num + 1] * monomials))
    return groebner(ex_pols + selected, bound_var, N=N)