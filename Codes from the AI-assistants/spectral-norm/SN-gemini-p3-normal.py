import sys
import numpy as np

def get_element(i, j):
    """(i) Computes the matrix element A(i, j) based on the formula."""
    return 1.0 / ((i + j) * (i + j + 1) / 2 + i + 1)

def multiply_Av(n, v):
    """(ii) Computes A * v."""
    res = np.zeros(n)
    for i in range(n):
        for j in range(n):
            res[i] += get_element(i, j) * v[j]
    return res

def multiply_Atv(n, v):
    """(iii) Computes At * v."""
    res = np.zeros(n)
    for i in range(n):
        for j in range(n):
            res[i] += get_element(j, i) * v[j]
    return res

def multiply_AtAv(n, v):
    """(iv) Computes At * (A * v)."""
    return multiply_Atv(n, multiply_Av(n, v))

def calculate_spectral_norm(n):
    # Initialize vector v with ones
    u = np.ones(n)
    v = np.zeros(n)
    
    # Power method iterations (typically 10 is enough for convergence)
    for _ in range(10):
        v = multiply_AtAv(n, u)
        u = multiply_AtAv(n, v)
    
    # Calculate spectral norm: sqrt( (u.v) / (v.v) )
    v_dot_v = np.dot(v, v)
    u_dot_v = np.dot(u, v)
    
    return np.sqrt(u_dot_v / v_dot_v)

if __name__ == "__main__":
    # Use 5500 as default or from command line
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
    
    result = calculate_spectral_norm(n)
    print(f"{result:.9f}")