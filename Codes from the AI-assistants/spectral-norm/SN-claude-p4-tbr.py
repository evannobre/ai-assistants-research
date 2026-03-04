import numpy as np
import sys

def A(i, j):
    return 1.0 / (i + j - 1)

def multiply_Av(v):
    n = len(v)
    return np.array([sum(A(i+1, j+1) * v[j] for j in range(n)) 
                     for i in range(n)])

def multiply_Atv(v):
    n = len(v)
    return np.array([sum(A(j+1, i+1) * v[j] for j in range(n)) 
                     for i in range(n)])

def multiply_AtAv(v):
    return multiply_Atv(multiply_Av(v))

def spectral_norm(n):
    v = np.ones(n)
    for _ in range(10):
        u = multiply_AtAv(v)
        v = multiply_AtAv(u)
    
    vAv = np.dot(v, multiply_AtAv(v))
    vv = np.dot(v, v)
    return np.sqrt(vAv / vv)

if __name__ == "__main__":
    n = int(sys.argv[1])
    print(f"{spectral_norm(n):.9f}")