import math
from array import array

# Define matrix entry: A[i,j] = 1 / ((i + j + 1)*(i + j + 2)/2 + i + 1)
def a(i, j):
    ij = i + j
    return 1.0 / (((ij + 1) * (ij + 2) // 2) + i + 1)

# Multiply A * u
def multiply_Au(u, n):
    result = array('d', (0.0,) * n)
    for i in range(n):
        total = 0.0
        for j in range(n):
            total += a(i, j) * u[j]
        result[i] = total
    return result

# Multiply Aᵗ * u
def multiply_Atu(u, n):
    result = array('d', (0.0,) * n)
    for i in range(n):
        total = 0.0
        for j in range(n):
            total += a(j, i) * u[j]
        result[i] = total
    return result

# Multiply AᵗA * u
def multiply_AtAu(u, n):
    return multiply_Atu(multiply_Au(u, n), n)

# Power Method to approximate spectral norm
def spectral_norm(n, iterations=10):
    u = array('d', [1.0] * n)
    for _ in range(iterations):
        v = multiply_AtAu(u, n)
        norm = math.sqrt(sum(x * x for x in v))
        u = array('d', [x / norm for x in v])
    vBv = sum(u_i * v_i for u_i, v_i in zip(u, multiply_AtAu(u, n)))
    return math.sqrt(vBv)

# Example usage
if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
    print("{0:.9f}".format(spectral_norm(n)))
