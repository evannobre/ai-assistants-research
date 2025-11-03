import numpy as np
import sys
import time

# (i) computes the infinite matrix element A(i, j)
def A_element(i, j):
    """
    Calculates the element A[i, j] of the infinite matrix.
    Using 0-indexed i and j.
    The formula for the denominator is based on the problem description sequence:
    1, 1/2, 1/3, 1/4, 1/5, 1/6, ...
    This corresponds to 1 / (k_th term in natural numbers starting from 1)
    where the k_th term for A[i,j] (0-indexed) is given by
    k = (i+j)*(i+j+1)/2 + i + 1.
    """
    # Cast to int to ensure correct integer arithmetic for large i, j
    k = int((i + j) * (i + j + 1) / 2) + i + 1
    return 1.0 / k

# (ii) computes A*v
def multiply_Av(N, v):
    """
    Computes the product of matrix A (NxN submatrix) and vector v.
    A is not explicitly constructed to save memory.
    """
    result = np.zeros(N, dtype=np.float64)
    for i in range(N):
        for j in range(N):
            result[i] += A_element(i, j) * v[j]
    return result

# (iii) computes A^t*v
def multiply_Atv(N, v):
    """
    Computes the product of A transpose (NxN submatrix) and vector v.
    A transpose is not explicitly constructed.
    A_transpose[i, j] = A[j, i]
    """
    result = np.zeros(N, dtype=np.float64)
    for i in range(N):
        for j in range(N):
            # A_transpose[i, j] is A_element(j, i)
            result[i] += A_element(j, i) * v[j]
    return result

# (iv) computes A^t * (A * v)
def multiply_AtAv(N, v):
    """
    Computes A^t * (A * v) by calling the other functions.
    """
    return multiply_Atv(N, multiply_Av(N, v))

def spectral_norm_power_method(N, iterations=10):
    """
    Calculates the spectral norm of the NxN submatrix of A using the Power Method.
    """
    # Initialize a random vector u
    u = np.ones(N, dtype=np.float64) # Using ones for consistency, random also works

    for _ in range(iterations):
        v = multiply_AtAv(N, u)
        u = multiply_AtAv(N, v)
        # Normalize u to prevent overflow/underflow and for numerical stability
        norm_u_squared = np.dot(u, u)
        if norm_u_squared == 0:
            raise ValueError("Vector became zero, cannot normalize.")
        u = u / np.sqrt(norm_u_squared)
        
    # After iterations, u should be close to the dominant eigenvector of A^T A.
    # The dominant eigenvalue lambda_max of A^T A is approximately (u^T (A^T A) u) / (u^T u)
    # We already have u from the last iteration, and (A^T A)u is approximately proportional to u.
    # A more robust way to get the eigenvalue is to apply A^T A once more and use the Rayleigh quotient.
    
    # Calculate A_t_A_u as A_t_A_u = multiply_AtAv(N, u)
    # Then lambda = np.dot(u, A_t_A_u) / np.dot(u, u)
    
    # Let's re-run for a final calculation of the eigenvalue based on the converged 'u'
    # The spectral norm is sqrt(lambda_max)
    # A simpler way, given u is normalized, is to compute ||A^T A u|| / ||u|| (if u is normalized, just ||A^T A u||)
    # Or, the original Power Method finds largest eigenvalue as limit of ||A^k x|| / ||A^(k-1) x||
    # In our case, we apply (A^T A) twice, so we need to be careful with normalizations.
    # The spectral radius is the eigenvalue of A^T A, let's call it lambda.
    # u is an eigenvector of A^T A for dominant eigenvalue.
    # (A^T A)u = lambda * u
    # so lambda = ||(A^T A)u|| / ||u||
    
    # Let's get the final eigenvalue more carefully using Rayleigh quotient
    u_final_normalized = u # u is already normalized from the loop

    # Apply A^T A one more time to get the eigenvector property more directly
    product_vector = multiply_AtAv(N, u_final_normalized)
    
    # Compute the eigenvalue (Rayleigh Quotient)
    # lambda_max = (u_final_normalized . product_vector) / (u_final_normalized . u_final_normalized)
    # Since u_final_normalized is normalized, u_final_normalized . u_final_normalized is 1
    lambda_max = np.dot(u_final_normalized, product_vector)

    return np.sqrt(lambda_max)


if __name__ == '__main__':
    # Get N from command-line argument
    if len(sys.argv) > 1:
        N = int(sys.argv[1])
    else:
        N = 5500 # Default value if no argument provided

    start_time = time.time()

    # The problem usually specifies a fixed number of iterations for Power Method.
    # A common number is 10 or 20 for these benchmark problems.
    # Let's use 10 as it's typical for convergence for dominant eigenvalues.
    spectral_norm = spectral_norm_power_method(N, iterations=10)

    end_time = time.time()

    print(f"{spectral_norm:.9f}")
    # print(f"Calculation for N={N} took {end_time - start_time:.4f} seconds.")