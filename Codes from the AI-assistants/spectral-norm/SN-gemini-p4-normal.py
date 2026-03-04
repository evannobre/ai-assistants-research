import sys
import math
from multiprocessing import Pool

# (i) Computes the infinite matrix element A(i, j)
# Based on the formula: 1 / ((i + j) * (i + j + 1) / 2 + i + 1)
def a_element(i, j):
    return 1.0 / ((i + j) * (i + j + 1) / 2 + i + 1)

# (ii) Computes A * v
def multiply_av(n, v):
    u = [0.0] * n
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += a_element(i, j) * v[j]
        u[i] = s
    return u

# (iii) Computes At * v (Transpose of A * v)
def multiply_atv(n, v):
    u = [0.0] * n
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += a_element(j, i) * v[j]
        u[i] = s
    return u

# (iv) Computes At * (A * v)
def multiply_at_av(n, v):
    return multiply_atv(n, multiply_av(n, v))

def main():
    # Use n=5500 as requested via command line
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
    
    u = [1.0] * n
    v = [0.0] * n
    
    # Power Method Iteration
    for _ in range(10):
        v = multiply_at_av(n, u)
        u = multiply_at_av(n, v)
    
    # Calculate Spectral Norm
    v_bv = 0.0
    vv = 0.0
    for i in range(n):
        v_bv += u[i] * v[i]
        vv += v[i] * v[i]
    
    spectral_norm = math.sqrt(v_bv / vv)
    print(f"{spectral_norm:.9f}")

if __name__ == "__main__":
    main()