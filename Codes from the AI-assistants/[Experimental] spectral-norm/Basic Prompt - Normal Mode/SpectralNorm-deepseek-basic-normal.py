import numpy as np
from math import sqrt

def infinite_matrix_vector_product(v, max_n):
    """
    Compute A*v for the infinite matrix A, truncated to size max_n x max_n.
    The matrix entries follow the pattern a11=1, a12=1/2, a21=1/3, a13=1/4, etc.
    """
    n = len(v)
    result = np.zeros(n)
    for i in range(n):
        for j in range(n):
            # Calculate the position in the sequence: (1,1), (1,2), (2,1), (1,3), (2,2), (3,1), ...
            # The k-th element is a_{i,j} where i+j increases, and for same i+j, i increases
            # The position can be calculated as: k = (i+j-2)*(i+j-1)//2 + i
            k = (i + j - 2) * (i + j - 1) // 2 + i
            a_ij = 1.0 / k if k > 0 else 0.0
            result[i] += a_ij * v[j]
    return result

def power_method(max_iter=1000, tolerance=1e-10, max_n=100):
    """
    Power method to estimate the spectral norm of the infinite matrix A.
    
    Parameters:
    - max_iter: maximum number of iterations
    - tolerance: convergence threshold
    - max_n: size of the vector to use (truncation of infinite matrix)
    
    Returns:
    - Estimated spectral norm (largest singular value)
    """
    # Initialize a random vector
    v = np.random.rand(max_n)
    v = v / np.linalg.norm(v)
    
    lambda_prev = 0
    
    for _ in range(max_iter):
        # Compute Av
        Av = infinite_matrix_vector_product(v, max_n)
        
        # Compute Rayleigh quotient (current eigenvalue estimate)
        lambda_curr = np.dot(v, Av)
        
        # Normalize the vector
        v = Av / np.linalg.norm(Av)
        
        # Check for convergence
        if abs(lambda_curr - lambda_prev) < tolerance:
            break
            
        lambda_prev = lambda_curr
    
    return lambda_curr

# Example usage
if __name__ == "__main__":
    spectral_norm = power_method(max_iter=1000, tolerance=1e-12, max_n=200)
    print(f"Estimated spectral norm: {spectral_norm}")