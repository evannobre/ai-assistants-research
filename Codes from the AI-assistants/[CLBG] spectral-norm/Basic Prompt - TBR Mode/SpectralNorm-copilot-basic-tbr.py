import sys
from math import sqrt

def A(i, j):
    return 1.0 / (((i + j) * (i + j + 1) // 2) + i + 1)

def multiply_Av(v):
    n = len(v)
    return [
        sum(A(i, j) * v[j] for j in range(n))
        for i in range(n)
    ]

def multiply_Atv(v):
    n = len(v)
    return [
        sum(A(j, i) * v[j] for j in range(n))
        for i in range(n)
    ]

def multiply_AtA_v(v):
    return multiply_Atv(multiply_Av(v))

def dot(u, v):
    return sum(ui * vi for ui, vi in zip(u, v))

def spectral_norm(n, iterations=10):
    v = [1.0] * n
    for _ in range(iterations):
        v = multiply_AtA_v(v)
    w = multiply_AtA_v(v)
    return sqrt(dot(v, w) / dot(w, w))

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
    result = spectral_norm(n)
    print(f"{result:.9f}")
