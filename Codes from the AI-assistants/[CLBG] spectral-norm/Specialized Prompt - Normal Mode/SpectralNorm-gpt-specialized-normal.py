import sys
import math

# (i) A(i, j) = 1 / (i + j - 1)
def A(i, j):
    return 1.0 / ((i + j - 1))

# (ii) Multiply matrix A by vector v: Av
def multiply_Av(v):
    n = len(v)
    result = [0.0] * n
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += A(i + 1, j + 1) * v[j]
        result[i] = s
    return result

# (iii) Multiply transpose of A by vector v: Aᵗv
def multiply_Atv(v):
    n = len(v)
    result = [0.0] * n
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += A(j + 1, i + 1) * v[j]
        result[i] = s
    return result

# (iv) Multiply Aᵗ * (A * v)
def multiply_AtAv(v):
    return multiply_Atv(multiply_Av(v))

# Main Power Method function
def spectral_norm(n):
    u = [1.0] * n
    for _ in range(10):  # 10 iterations of the power method
        v = multiply_AtAv(u)
        u = multiply_AtAv(v)

    # Compute dot products
    vBv = sum(u_i * v_i for u_i, v_i in zip(u, v))
    vv = sum(v_i * v_i for v_i in v)

    return math.sqrt(vBv / vv)

# Entry point
if __name__ == "__main__":
    try:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
    except ValueError:
        print("Usage: python3 spectral_norm.py <n>")
        sys.exit(1)

    norm = spectral_norm(n)
    print(f"{norm:.9f}")
