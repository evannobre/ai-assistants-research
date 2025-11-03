import random
import math

def dot(u, v):
    return sum(ui * vi for ui, vi in zip(u, v))

def norm(v):
    return math.sqrt(dot(v, v))

def matvec_hilbert(x):
    n = len(x)
    return [sum(x[j] / (i + j + 1) for j in range(n)) for i in range(n)]

def power_method(n, tol=1e-10, max_iter=1000):
    # Step 1: Initialize random unit vector
    x = [random.random() for _ in range(n)]
    x_norm = norm(x)
    x = [xi / x_norm for xi in x]

    for _ in range(max_iter):
        y = matvec_hilbert(x)
        y_norm = norm(y)
        x_new = [yi / y_norm for yi in y]

        if norm([x_new[i] - x[i] for i in range(n)]) < tol:
            break
        x = x_new

    return y_norm

if __name__ == "__main__":
    n = 500  # Adjust based on memory constraints
    spectral_norm = power_method(n)
    print(f"Estimated Spectral Norm of {n}x{n} Hilbert Matrix: {spectral_norm:.10f}")
