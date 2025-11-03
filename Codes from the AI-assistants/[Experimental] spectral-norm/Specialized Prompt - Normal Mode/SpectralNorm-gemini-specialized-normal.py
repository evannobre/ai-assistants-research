import numpy as np
import time

def infinite_matrix_vector_product(N, x):
    """
    Computes the matrix-vector product y = Ax for the infinite matrix A
    where a_ij = 1/(i+j-1), truncated to size N x N.

    Parameters:
    N (int): The dimension of the truncated matrix (and vector x).
    x (numpy.ndarray): The input vector of shape (N,).

    Returns:
    numpy.ndarray: The resulting vector y = Ax of shape (N,).
    """
    y = np.zeros(N, dtype=np.float64) # Use float64 for precision

    # We cannot vectorize this sum directly with a pre-computed matrix.
    # Iterating through rows for y_i = sum_j (1/(i+j-1)) * x_j
    # This is the most computationally intensive part (O(N^2))
    for i in range(N):
        # i and j are 0-indexed in Python/NumPy, so we adjust for the formula
        # a_ij = 1/((i+1)+(j+1)-1) = 1/(i+j+1)
        # We pre-compute 1/(i+j+1) for better performance in the inner loop
        # (This avoids repeated division by the same denominator)
        # Note: A more optimized approach might be possible by considering the structure
        # of the matrix, e.g., via FFT for Toeplitz-like matrices, but for
        # the given form, a direct sum is often used as a baseline.
        # However, this matrix is a Cauchy matrix, which is a specific type
        # of Hankel matrix. While there are fast algorithms for multiplying
        # some structured matrices, a general fast algorithm for Cauchy matrix
        # vector product might be complex to implement natively.
        # For simplicity and using "native libraries" concept, direct sum is more direct.
        
        # Create the row vector efficiently
        # Denominators for current row i: (i+1)+1-1, (i+1)+2-1, ..., (i+1)+N-1
        # which simplifies to i+1, i+2, ..., i+N
        denominators = np.arange(i + 1, i + N + 1, dtype=np.float64)
        a_row_i = 1.0 / denominators
        y[i] = np.dot(a_row_i, x) # Dot product for the sum

    return y

def power_method_spectral_norm(N, max_iter=500, tol=1e-7):
    """
    Estimates the spectral norm of the infinite matrix A (truncated to N x N)
    using the Power Method.

    Parameters:
    N (int): The dimension of the truncated matrix.
    max_iter (int): Maximum number of iterations for the Power Method.
    tol (float): Tolerance for convergence.

    Returns:
    tuple: (spectral_norm, num_iterations, dominant_eigenvector)
    """
    print(f"Starting Power Method for N = {N}")
    print(f"Memory for vectors (approx): {2 * N * 8 / (1024**2):.2f} MB")

    # Initialize a random vector
    np.random.seed(42) # for reproducibility
    x = np.random.rand(N)
    x = x / np.linalg.norm(x) # Normalize x

    dominant_eigenvalue = 0.0
    num_iterations = 0

    start_time = time.time()

    for k in range(max_iter):
        num_iterations = k + 1

        # Compute y = Ax
        y = infinite_matrix_vector_product(N, x)

        # Calculate the Rayleigh quotient for the eigenvalue approximation
        # lambda_k = (x^T A x) / (x^T x) = x^T y / (x^T x)
        # Since x is normalized, x^T x = 1, so lambda_k = x^T y
        current_eigenvalue = np.dot(x, y)

        # Normalize y to get the next approximation of the eigenvector
        norm_y = np.linalg.norm(y)

        # Avoid division by zero if y becomes a zero vector (very unlikely for this matrix)
        if norm_y == 0:
            print("Warning: Vector y became zero. Terminating.")
            break

        x_new = y / norm_y

        # Check for convergence
        # We check the difference between successive eigenvectors or eigenvalues.
        # For spectral norm, we care about the magnitude of the dominant eigenvalue.
        # The convergence criteria can be based on the difference of the eigenvalue,
        # or the change in the eigenvector.
        if np.abs(np.abs(current_eigenvalue) - np.abs(dominant_eigenvalue)) < tol * np.abs(current_eigenvalue):
             print(f"Converged after {num_iterations} iterations. Eigenvalue diff: {np.abs(np.abs(current_eigenvalue) - np.abs(dominant_eigenvalue)):.2e}")
             dominant_eigenvalue = current_eigenvalue
             break
        
        if np.linalg.norm(x_new - x) < tol:
            print(f"Converged by eigenvector difference after {num_iterations} iterations. Norm diff: {np.linalg.norm(x_new - x):.2e}")
            dominant_eigenvalue = current_eigenvalue
            break
        
        x = x_new
        dominant_eigenvalue = current_eigenvalue
        
        if (k + 1) % 10 == 0:
            print(f"Iteration {k+1}: Current Eigenvalue approx = {current_eigenvalue:.6f}")


    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Power Method completed in {elapsed_time:.2f} seconds.")

    # The spectral norm is the absolute value of the dominant eigenvalue for symmetric matrices.
    spectral_norm = np.abs(dominant_eigenvalue)
    return spectral_norm, num_iterations, x # Return the dominant eigenvector as well

if __name__ == "__main__":
    # Choose N based on your computational budget and desired accuracy.
    # For a few seconds/minutes, N=2000 to N=5000 is a good starting point.
    # N=10000 might take several minutes to an hour on a typical CPU.
    # The problem description hints at a "simulation of an infinite matrix",
    # so we should aim for as large an N as possible without exceeding resources.
    
    # Let's test with a moderate N first, then comment on larger N.
    # A general guideline for N on a 16GB RAM for O(N^2) operation is usually
    # N up to 10,000 to 20,000 before it becomes too slow or memory bound by factors
    # other than just vectors (e.g., intermediate arrays in optimized linear algebra).
    # Here, we only store two vectors of size N.
    
    # N = 2000 is a reasonable starting point for quick testing.
    # N = 5000 might take a few minutes.
    # N = 10000 could take tens of minutes depending on CPU.
    
    # For a practical execution on the specified machine, and considering a "simulation"
    # that might run for some time, N up to 5000-8000 seems reasonable for the given constraints.
    # Let's try N = 5000 for a balance.
    N_sim = 5000 
    
    # The max_iter and tol might need tuning based on the specific matrix.
    # For this matrix, convergence can be relatively fast, but also depends on N.
    max_iterations = 500
    convergence_tolerance = 1e-6 # A slightly looser tolerance for faster results, 1e-7 is good.

    try:
        spectral_norm_estimate, iters, dominant_vec = power_method_spectral_norm(
            N_sim, max_iter=max_iterations, tol=convergence_tolerance
        )

        print(f"\nEstimated Spectral Norm (for N={N_sim}): {spectral_norm_estimate:.8f}")
        print(f"Total Iterations: {iters}")
        # print(f"Dominant Eigenvector (first 5 elements): {dominant_vec[:5]}")

    except MemoryError as e:
        print(f"MemoryError: {e}. Try reducing N or increasing available RAM/vRAM.")
    except Exception as e:
        print(f"An error occurred: {e}")