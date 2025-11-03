import sys
import math

# (i) Computes the matrix element A[i][j]
def A(i, j):
    return 1.0 / (((i + j) * (i + j + 1) // 2) + i + 1)

# (ii) Computes A * v
def Av(v):
    n = len(v)
    return [sum(A(i, j) * v[j] for j in range(n)) for i in range(n)]

# (iii) Computes A^T * v
def Atv(v):
    n = len(v)
    return [sum(A(j, i) * v[j] for j in range(n)) for i in range(n)]

# (iv) Computes A^T * (A * v)
def AtAv(v):
    return Atv(Av(v))

# Power method to approximate spectral norm
def spectral_norm(n):
    u = [1.0] * n
    for _ in range(10):  # fixed iteration count
        v = AtAv(u)
        u = AtAv(v)

    vBv = sum(u_i * v_i for u_i, v_i in zip(u, v))
    vv = sum(v_i * v_i for v_i in v)
    return math.sqrt(vBv / vv)

# Entry point for command-line argument
if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"{spectral_norm(n):.9f}")
