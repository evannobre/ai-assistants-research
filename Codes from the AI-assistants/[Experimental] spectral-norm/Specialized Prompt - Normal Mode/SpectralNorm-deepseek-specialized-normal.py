import numpy as np
from math import sqrt

def matrix_vector_product(v, max_iter=1000):
    """
    Compute the matrix-vector product Av for the infinite matrix A.
    We approximate by considering only the first max_iter components.
    """
    n = len(v)
    result = np.zeros(n)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            # Matrix element is 1/(i + j - 1)
            result[i-1] += v[j-1] / (i + j - 1)
    return result

def spectral_norm_power_method(tol=1e-8, max_iter=1000, n=1000):
    """
    Compute the spectral norm of the infinite matrix A using the Power Method.
    
    Parameters:
    - tol: tolerance for convergence
    - max_iter: maximum number of iterations
    - n: dimension of the vector to use in approximation
    
    Returns:
    - The estimated spectral norm
    """
    # Initialize a random vector
    v = np.random.rand(n)
    v /= np.linalg.norm(v)
    
    lambda_prev = 0
    
    for _ in range(max_iter):
        # Compute Av
        Av = matrix_vector_product(v, n)
        
        # Compute Rayleigh quotient (current eigenvalue estimate)
        lambda_k = np.dot(v, Av)
        
        # Check for convergence
        if abs(lambda_k - lambda_prev) < tol * abs(lambda_k):
            break
            
        lambda_prev = lambda_k
        
        # Normalize for next iteration
        v = Av / np.linalg.norm(Av)
    
    return sqrt(lambda_k)

if __name__ == "__main__":
    # Adjust these parameters based on available memory
    # For 16GB RAM, we can handle vectors of size ~10^5
    n = 10000  # Vector size - can be increased if more precision needed
    tol = 1e-10
    
    print("Calculating spectral norm...")
    norm = spectral_norm_power_method(tol=tol, n=n)
    print(f"Estimated spectral norm: {norm:.10f}")