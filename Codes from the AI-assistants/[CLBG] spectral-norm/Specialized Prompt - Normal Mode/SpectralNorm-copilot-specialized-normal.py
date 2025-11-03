import sys
from math import sqrt

def A(i, j):
    return 1.0 / (((i + j) * (i + j + 1) // 2) + i + 1)

def multiply_A(v):
    n = len(v)
    return [sum(A(i, j) * v[j] for j in range(n)) for i in range(n)]

def multiply_At(v):
    n = len(v)
    return [sum(A(j, i) * v[j] for j in range(n)) for i in range(n)]

def multiply_AtA(v):
    return multiply_At(multiply_A(v))

def main(n):
    u = [1.0] * n
    for _ in range(10):
        v = multiply_AtA(u)
        norm = sqrt(sum(x * x for x in v))
        u = [x / norm for x in v]

    vBv = sum(u[i] * v[i] for i in range(n))
    vv = sum(v[i] * v[i] for i in range(n))
    print(f"{sqrt(vBv / vv):.9f}")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
    main(n)
