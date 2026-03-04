#!/usr/bin/env python3
from array import array
from math import sqrt
import sys

def a(i0: int, j0: int) -> float:
    """
    A_ij with i0,j0 zero-based:
      i = i0+1, j = j0+1
      k = ((i+j-2)(i+j-1))/2 + i
    """
    i = i0 + 1
    j = j0 + 1
    s = i + j - 2
    k = (s * (s + 1)) // 2 + i
    return 1.0 / k

def mult_Av(n: int, v: array, out: array) -> None:
    # out[i] = sum_j A[i,j] * v[j]
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += a(i, j) * v[j]
        out[i] = s

def mult_Atv(n: int, v: array, out: array) -> None:
    # out[i] = sum_j A[j,i] * v[j]
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += a(j, i) * v[j]
        out[i] = s

def mult_AtAv(n: int, v: array, out: array, tmp: array) -> None:
    # out = A^T(A v)
    mult_Av(n, v, tmp)
    mult_Atv(n, tmp, out)

def dot(u: array, v: array) -> float:
    s = 0.0
    for x, y in zip(u, v):
        s += x * y
    return s

def spectral_norm(n: int, iters: int = 10) -> float:
    u = array('d', [1.0]) * n
    v = array('d', [0.0]) * n
    tmp = array('d', [0.0]) * n

    for _ in range(iters):
        mult_AtAv(n, u, v, tmp)   # v = A^T(Au)
        mult_AtAv(n, v, u, tmp)   # u = A^T(Av)

    # v is from the last mult_AtAv(n, u, v, tmp) inside loop? Not anymore.
    # We ended with u = AtA(v). So recompute v = AtA(u) once to pair u with v.
    mult_AtAv(n, u, v, tmp)

    vBv = dot(u, v)
    vv = dot(v, v)
    return sqrt(vBv / vv)

def main():
    # Common benchmark convention: n from CLI, default 100
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    val = spectral_norm(n, iters=10)
    print(f"{val:.9f}")

if __name__ == "__main__":
    main()
