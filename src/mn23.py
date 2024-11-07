from sage.all import *
from src.misc import solve_copper
from time import time
import copy


def automated(pols, bound_var, bounds, monomials, modulus, m, test=None):
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
    max_depth = len(pols)
    leadings = [pol.lm() for pol in pols]
    shifts = []
    print(f"格的维度：dim = {len(monomials)}")
    x, y, z = pols[0].parent().gens()
    s_M = 0
    g = prod(monomials)
    for mono in monomials:
        max_sum = 0
        exps = [0] * max_depth
        opt_exps = [0] * max_depth
        optimize_shift(mono, 0)
        shift = mono
        for i in range(len(pols)):
            shift //= leadings[i] ** opt_exps[i]
            shift *= pols[i] ** opt_exps[i]
        s_M += m - sum(opt_exps)
        shifts.append(shift * modulus ** (m - sum(opt_exps)))
    print("格行列式中各项幂次：")
    print(f"s_X = {g.degree(x)}, s_Y = {g.degree(y)}, s_Z = {g.degree(z)}, s_M = {s_M}")
    res = solve_copper(shifts, bound_var, bounds, test)
    return res
