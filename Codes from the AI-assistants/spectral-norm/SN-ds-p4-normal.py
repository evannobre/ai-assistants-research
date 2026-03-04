import numpy as np
from math import sqrt

def A(i, j):
    return 1.0 / (i + j + 1)

def multiply_Av(n, v):
    return np.array([sum(A(i, j) * v[j] for j in range(n)) 
                     for i in range(n)])

def multiply_Atv(n, v):
    return multiply_Av(n, v)  # Symmetric

def multiply_At_Av(n, v):
    Av = multiply_Av(n, v)
    return multiply_Atv(n, Av)

def spectral_norm(n, iterations=10):
    u = np.ones(n)
    for _ in range(iterations):
        v = multiply_At_Av(n, u)
        v_norm = sqrt(np.dot(v, v))
        v = v / v_norm
        u = v
    return sqrt(np.dot(v, multiply_At_Av(n, v)))

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"Spectral norm: {spectral_norm(n):.12f}")