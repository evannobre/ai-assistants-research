#!/usr/bin/env python3
import sys
import math
import numpy as np

# 1-based formula for k: k = (i+j-1)*(i+j-2)/2 + i
def A_element(i, j):
    """
    Compute the infinite-matrix element A(i,j) using 1-based indices.
    i, j are integers >= 1.
    """
    s = i + j - 1
    k = (s * (s - 1)) // 2 + i
    return 1.0 / k

def A_times_v(v):
    """
    Compute u = A * v for the n-length vector v.
    Uses vectorized per-row computation to avoid building the full matrix.
    """
    n = v.shape[0]
    j = np.arange(1, n + 1, dtype=np.float64)  # 1..n
    u = np.empty(n, dtype=np.float64)
    for idx in range(n):
        i = idx + 1  # 1-based
        s = i + j - 1
        k = (s * (s - 1)) / 2.0 + i
        u[idx] = np.dot(1.0 / k, v)
    return u

def At_times_v(v):
    """
    Compute u = A^T * v for the n-length vector v.
    Equivalent to computing rows of A^T (columns of A).
    """
    n = v.shape[0]
    i = np.arange(1, n + 1, dtype=np.float64)  # 1..n
    u = np.empty(n, dtype=np.float64)
    for jdx in range(n):
        j = jdx + 1  # 1-based
        s = i + j - 1
        k = (s * (s - 1)) / 2.0 + i
        u[jdx] = np.dot(1.0 / k, v)
    return u

def AtA_times_v(v):
    """
    Compute u = A^T * (A * v) using the two functions above.
    """
    return At_times_v(A_times_v(v))

def spectral_norm(n, iterations=10):
    """
    Approximate the spectral norm of the n x n truncation of A.
    """
    v = np.ones(n, dtype=np.float64)
    for _ in range(iterations):
        v = AtA_times_v(v)
    u = A_times_v(v)
    v_dot_v = np.dot(v, v)
    u_dot_u = np.dot(u, u)
    return math.sqrt(u_dot_u / v_dot_v)

def main():
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Usage: spectral_norm.py [n]")
            return
    else:
        n = 5500  # default large test as requested

    # For performance measurement you can time this run externally.
    result = spectral_norm(n, iterations=10)
    print("{:.9f}".format(result))

if __name__ == "__main__":
    main()
