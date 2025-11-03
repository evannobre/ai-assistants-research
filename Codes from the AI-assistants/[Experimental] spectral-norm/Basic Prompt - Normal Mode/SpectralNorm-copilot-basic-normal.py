import math
import random

def apply_A(v):
    """Simulate the matrix-vector product Av for the infinite matrix."""
    result = []
    n = 1
    for i in range(len(v)):
        sum_i = 0.0
        for j in range(i + 1):  # A is lower-triangular
            if j < len(v):
                sum_i += v[j] / n
                n += 1
        result.append(sum_i)
    return result

def vector_norm(v):
    """Compute Euclidean norm (L2) of vector v."""
    return math.sqrt(sum(x * x for x in v))

def normalize(v):
    """Normalize vector to unit norm."""
    norm = vector_norm(v)
    return [x / norm for x in v]

def power_method(k=100, dim=100, tol=1e-10):
    """Approximate the spectral norm of the infinite matrix."""
    # Start with random normalized vector
    v = [random.random() for _ in range(dim)]
    v = normalize(v)
    lambda_old = 0

    for _ in range(k):
        Av = apply_A(v)
        lambda_new = vector_norm(Av)
        if abs(lambda_new - lambda_old) < tol:
            break
        v = normalize(Av)
        lambda_old = lambda_new

    return lambda_new

# Example usage
if __name__ == "__main__":
    est_norm = power_method()
    print(f"Estimated Spectral Norm: {est_norm:.6f}")
