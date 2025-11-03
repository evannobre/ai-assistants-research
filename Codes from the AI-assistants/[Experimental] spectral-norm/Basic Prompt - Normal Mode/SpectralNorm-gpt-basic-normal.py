import math

def A(i, j):
    return 1.0 / (((i + j + 1) * (i + j + 2) // 2) + i + 1)

def multiply_Av(v):
    n = len(v)
    result = [0.0] * n
    for i in range(n):
        sum_ = 0.0
        for j in range(n):
            sum_ += A(i, j) * v[j]
        result[i] = sum_
    return result

def multiply_Atv(v):
    n = len(v)
    result = [0.0] * n
    for i in range(n):
        sum_ = 0.0
        for j in range(n):
            sum_ += A(j, i) * v[j]
        result[i] = sum_
    return result

def multiply_AtAv(v):
    return multiply_Atv(multiply_Av(v))

def spectral_norm(n, iterations=10):
    u = [1.0] * n
    for _ in range(iterations):
        v = multiply_AtAv(u)
        u = v[:]
    
    vBv = sum(u_i * v_i for u_i, v_i in zip(u, multiply_AtAv(u)))
    vv = sum(v_i * v_i for v_i in u)
    return math.sqrt(vBv / vv)

# Example usage
if __name__ == "__main__":
    n = 1000  # size of the vector (approximation of infinite matrix)
    norm = spectral_norm(n)
    print(f"Spectral norm (approx): {norm:.9f}")
