import numpy as np
import sys

def matrix_element(i, j):
    """(i) Compute the infinite matrix element A(i,j)"""
    return 1.0 / ((i + j) * (i + j + 1) // 2 + i + 1)

def matvec_mult(v):
    """(ii) Compute A*v where A is the infinite matrix"""
    n = len(v)
    u = np.zeros(n)
    for i in range(n):
        for j in range(n):
            u[i] += matrix_element(i, j) * v[j]
    return u

def transpose_matvec_mult(v):
    """(iii) Compute Aᵀ*v where A is the infinite matrix"""
    n = len(v)
    u = np.zeros(n)
    for i in range(n):
        for j in range(n):
            u[i] += matrix_element(j, i) * v[j]
    return u

def ata_mult(v):
    """(iv) Compute Aᵀ*A*v"""
    return transpose_matvec_mult(matvec_mult(v))

def spectral_norm(n):
    """Compute the spectral norm of the n×n submatrix using Power Method"""
    v = np.ones(n)
    for _ in range(10):  # Typically converges in a few iterations
        u = ata_mult(v)
        norm = np.sqrt(np.dot(u, u) / np.sqrt(np.dot(v, v))
        v = u / np.sqrt(np.dot(u, u))
    return norm

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    norm = spectral_norm(n)
    print("{:.9f}".format(norm))