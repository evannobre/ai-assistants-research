import sys
import math
from itertools import count

def matrix_element(i, j):
    """(i) Compute the infinite matrix element A(i, j)"""
    # The matrix is indexed starting from 1
    return 1.0 / ((i + j - 1) * (i + j) // 2 + i)

def multiply_A_v(v):
    """(ii) Compute A*v where A is the infinite matrix and v is a vector"""
    n = len(v)
    return [sum(matrix_element(i+1, j+1) * v[j] for j in range(n)) for i in range(n)]

def multiply_At_v(v):
    """(iii) Compute Aᵀ*v where A is the infinite matrix and v is a vector"""
    n = len(v)
    return [sum(matrix_element(j+1, i+1) * v[j] for j in range(n)) for i in range(n)]

def multiply_AtAv(v):
    """(iv) Compute Aᵀ*A*v"""
    return multiply_At_v(multiply_A_v(v))

def spectral_norm(n):
    """Compute the spectral norm of the n×n submatrix of A using power method"""
    # Initial vector - can be random, but we'll use all ones for reproducibility
    u = [1.0] * n
    v = [0.0] * n
    
    # Power iteration
    for _ in range(10):
        v = multiply_AtAv(u)
        u = multiply_AtAv(v)
    
    # Compute the norm
    vBv = sum(v[i] * u[i] for i in range(n))
    vv = sum(v[i] * v[i] for i in range(n))
    
    return math.sqrt(vBv / vv)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print("%.9f" % spectral_norm(n))