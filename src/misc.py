import subprocess
from sage.all import floor, gcd, Integer, Matrix, QQ, ZZ, prod, sqrt, Sequence, vector
from src.mp import groebner

# from src.root_methods import groebner
from time import time
from src.fplll_fmt import fplll_fmt, fplll_read


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
    if form == "1":
        return sum(map(abs, scaled).coefficients())
    elif form == "inf":
        return max(scaled.coefficients(), key=abs)


def calc_bits(lst):
    return list(map(lambda e: Integer(e).nbits(), lst))


def reduce_varsize(N):
    len_p = (N.nbits() + 1) >> 1
    s_l = floor(2 * sqrt(N))
    s_r = (1 << len_p) + N // (1 << len_p)
    s = (s_l + s_r) >> 1
    s += (N + 1 - s) % 4
    return N + 1 - s, (s_r - s_l) >> 1


def solve_copper(
    shifts, bound_var, bounds, test, delta=0.75, ex_pols=[], select_num=None, N=None, monomials=None, brute=False
):
    if select_num is None:
        select_num = len(shifts)
    if monomials:
        dim = len(shifts)
        L = Matrix(ZZ, dim)
        for i in range(dim):
            for j in range(i + 1):
                L[i, j] = shifts[i].monomial_coefficient(monomials[j])
    else:
        pol_seq = Sequence(shifts)
        L, monomials = pol_seq.coefficient_matrix()
    monomials = vector(monomials)
    # print("单项式集合：")
    # print("{" + str(monomials)[1:-1] + "}")
    scales = list(map(lambda e: e(bounds), monomials))
    for col, scale in enumerate(scales):
        L.rescale_col(col, scale)
    L = L.dense_matrix()
    start = time()

    if brute:
        L = L.LLL(delta)
        print(f"solve_copper original fpLLL: {time() - start}")
        h, w = L.dimensions()
        L_ = L.change_ring(QQ)
        for col, scale in enumerate(scales):
            L_.rescale_col(col, 1 / scale)
        L_ = L_.change_ring(ZZ)
        start = time()
        for i in range(h):
            pol = 0
            for j in range(w):
                pol += L_[i, j] * monomials[j]
            bound, var = brute
            pol = pol.subs({var: var + bound})
            for j in range(w):
                L_[i, j] = pol.monomial_coefficient(monomials[j])
        for col, scale in enumerate(scales):
            L_.rescale_col(col, scale)
        print(f"transformation time: {time() - start}")
        start = time()
        L = L_.LLL(delta)
        print(f"solve_copper recurred fpLLL: {time() - start}")
    else:
        print("开始使用flatter约化格基...")
        s = fplll_fmt(L)
        file_name = "misc_output.txt"

        with open(file_name, "w", encoding="utf-8") as file:
            file.write(s)

        try:
            rst = subprocess.Popen(
                "src/scripts/misc_flatter.nu",
                text=True,
                stdout=subprocess.PIPE,
                shell=True,
            )

            L = fplll_read(rst.stdout)
        except subprocess.CalledProcessError as e:
            print(e)
            return

        print(f"约化完成！用时{round(time() - start, 3)}s")

    L = L.change_ring(QQ)
    for col, scale in enumerate(scales):
        L.rescale_col(col, 1 / scale)
    selected = list(
        filter(
            lambda e: test is None or e(test) == 0,
            L.change_ring(ZZ)[: select_num + 1] * monomials,
        )
    )
    return groebner(ex_pols + selected, bound_var, N=N)
