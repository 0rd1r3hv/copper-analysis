from sage.all import *

def fplll_fmt(M):
    m, n = M.dimensions()
    s = "["
    for i in range(m):
        s += "["
        for j in range(n):
            s += str(M[i, j])
            if j < n - 1:
                s += " "
        s += "]\n"
    s += "]"
    return s


def fplll_read(s):
    rows = []
    for line in s:
        line = line.lstrip("[").rstrip("\n").rstrip("]")
        if len(line) == 0:
            break

        row = [int(x) for x in line.split(" ") if len(x) > 0 and x != "]"]
        rows += [row]
    m = len(rows)
    n = len(rows[0])
    for row in rows:
        assert len(row) == n

    L = Matrix(ZZ, m, n)
    for i in range(m):
        for j in range(n):
            L[i, j] = rows[i][j]
    return L
