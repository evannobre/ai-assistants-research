import sys
import math

# (i) Matrix entry A(i, j)
def A(i, j):
    ij = i + j
    return 1.0 / (ij * (ij + 1) / 2 + i + 1)

# (ii) Multiply vector v by matrix A
def multiply_Av(v):
    n = len(v)
    result = [0.0] * n
    for i in range(n):
        total = 0.0
        for j in range(n):
            total += A(i, j) * v[j]
        result[i] = total
    return result

# (iii) Multiply vector v by transpose of A
def multiply_Atv(v):
    n = len(v)
    result = [0.0] * n
    for i in range(n):
        total = 0.0
        for j in range(n):
            total += A(j, i) * v[j]
        result[i] = total
    return result

# (iv) Multiply vector v by Aᵗ(A*v)
def multiply_AtAv(v):
    return multiply_Atv(multiply_Av(v))

# Main function using power method
def spectral_norm(n):
    u = [1.0] * n
    for _ in range(10):  # 10 iterations of the power method
        v = multiply_AtAv(u)
        u = multiply_AtAv(v)

    vBv = sum(uv * vv for uv, vv in zip(u, v))
    vv = sum(vv * vv for vv in v)

    return math.sqrt(vBv / vv)

if __name__ == '__main__':
    try:
        n = int(sys.argv[1])
    except:
        n = 5500

    print("{0:.9f}".format(spectral_norm(n)))
