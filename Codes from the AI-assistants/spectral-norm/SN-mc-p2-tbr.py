import numpy as np

def a_ij(i, j):
    return 1.0 / (((i + j - 1) * (i + j - 2)) // 2 + i)

def multiply_Av(v):
    N = v.size
    j = np.arange(1, N+1)
    out = np.empty(N, dtype=np.float64)
    for i in range(1, N+1):
        denom = ((i + j - 1) * (i + j - 2)) // 2 + i
        out[i-1] = np.sum(v / denom)
    return out

def multiply_Atv(v):
    # A is symmetric in the benchmark formulation when used via A^T A,
    # but implement explicitly for clarity
    N = v.size
    i = np.arange(1, N+1)
    out = np.empty(N, dtype=np.float64)
    for j in range(1, N+1):
        denom = ((i + j - 1) * (i + j - 2)) // 2 + i
        out[j-1] = np.sum(v / denom)
    return out

def spectral_norm(N=5500, iterations=10):
    u = np.ones(N, dtype=np.float64)
    for _ in range(iterations):
        v = multiply_Av(u)
        u = multiply_Atv(v)
        u /= np.linalg.norm(u)
    v = multiply_Av(u)
    Au = multiply_Atv(v)
    norm = np.sqrt(np.dot(u, Au) / np.dot(u, u))
    return norm

if __name__ == "__main__":
    print(spectral_norm(5500, iterations=10))
