import numpy as np
import sys

def A_element(i, j):
    """
    (i) Computes the element A(i, j) of the infinite matrix.
    Indices are 0-based.
    """
    return 1.0 / (((i + j) * (i + j + 1) / 2) + i + 1)

def multiply_A_v(v):
    """
    (ii) Computes the matrix-vector product A*v.
    """
    n = len(v)
    result = np.zeros(n, dtype=np.float64)
    for i in range(n):
        # This is equivalent to the dot product of the i-th row of A with v
        row_A = [A_element(i, j) for j in range(n)]
        result[i] = np.dot(row_A, v)
    return result

def multiply_At_v(v):
    """
    (iii) Computes the transposed matrix-vector product Aᵗ*v.
    """
    n = len(v)
    result = np.zeros(n, dtype=np.float64)
    for i in range(n):
        # This is equivalent to the dot product of the i-th column of A with v
        col_A = [A_element(j, i) for j in range(n)]
        result[i] = np.dot(col_A, v)
    return result

def multiply_AtA_v(v):
    """
    (iv) Computes Aᵗ * (A * v) by composing the two previous functions.
    """
    return multiply_At_v(multiply_A_v(v))

def spectral_norm(n, iterations=10):
    """
    Calculates the spectral norm of an n x n approximation of the matrix A
    using the Power Method.
    """
    # Start with a random vector u of unit length
    u = np.random.rand(n)
    u /= np.linalg.norm(u)
    
    v = np.zeros(n, dtype=np.float64)

    for _ in range(iterations):
        v = multiply_AtA_v(u)
        u = v / np.linalg.norm(v)

    # Calculate the dominant eigenvalue using the Rayleigh quotient
    lambda_max = np.dot(u, multiply_AtA_v(u))
    
    return np.sqrt(lambda_max)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 spectral_norm.py <n>")
        print("Using default n = 5500 for performance check.")
        n = 5500
    else:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Error: The provided argument must be an integer.")
            sys.exit(1)

    if n <= 0:
        print("Error: The matrix size n must be a positive integer.")
        sys.exit(1)
        
    num_iterations = 10
    
    norm = spectral_norm(n, iterations=num_iterations)
    
    print(f"The spectral norm of the {n}x{n} matrix is approximately: {norm:.9f}")