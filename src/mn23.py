from sage.all import *
from src.misc import solve_copper
from time import time

MAX_i = 100


# str_vars should be a string, str_pols should be strings
def automated(str_vars, str_pols, len_bounds, modulus, params, test=None):


    def optimize_shift(mono, depth):
        nonlocal max_sum
        nonlocal leadings
        nonlocal opt_exps
        nonlocal exps
        nonlocal m
        if depth == max_depth:
            tot = sum(exps)
            if tot > max_sum:
                max_sum = tot
                opt_exps = exps[:]
            return
        exps[depth] = 0
        optimize_shift(mono, depth + 1)
        while mono % leadings[depth] == 0 and exps[depth] < m:
            exps[depth] += 1
            mono //= leadings[depth]
            optimize_shift(mono, depth + 1)


    print("开始执行 Meers, Nowakowski 的自动化 Coppersmith 攻击…")
    PR = PolynomialRing(ZZ, str_vars)
    gens = PR.gens()
    pols = [PR(str_pol) for str_pol in str_pols]
    max_depth = len(pols)
    leadings = [pol.lm() for pol in pols]
    len_M = modulus.nbits()
    for i in range(1, MAX_i + 1):
        left = right = s_M = 0
        m = max_depth * i
        monomials = (prod(pols) ** i).monomials()
        g = prod(monomials)
        for ind, gen in enumerate(gens):
            left += g.degree(gen) * len_bounds[ind]
        shifts = []
        for mono in monomials:
            max_sum = 0
            exps = [0] * max_depth
            opt_exps = [0] * max_depth
            optimize_shift(mono, 0)
            shift = mono
            for i in range(len(pols)):
                shift //= leadings[i] ** opt_exps[i]
                shift *= pols[i] ** opt_exps[i]
            right += sum(opt_exps) * len_M
            s_M += m - sum(opt_exps)
            shifts.append(shift * modulus ** (m - sum(opt_exps)))
        if left < right:
            print(f"自动使用攻击参数：m = {m}")
            print(f"格的维度：dim = {len(shifts)}")
            print("格行列式中各项幂次：")
            display = ""
            for ind, gen in enumerate(gens):
                display += f"s_{str(gen).upper()} = {g.degree(gen)}, "
            display += f"s_M = {s_M}"
            print(display)
            res = solve_copper(shifts, [1 << max(len_bounds), None], [1 << l for l in len_bounds], test, restrict=True, all_sols=True)
            return res
    print("攻击失败！")