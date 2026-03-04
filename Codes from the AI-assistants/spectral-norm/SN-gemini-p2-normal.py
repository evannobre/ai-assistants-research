import numpy as np
import time

def solve_spectral_norm(n_size=15000, tolerance=1e-10, max_iter=1000):
    """
    Computes the spectral norm of truncated infinite matrix A using the Power Method.
    Matrix A entries: a_ij = 1/k following diagonal traversal.
    """
    print(f"Initializing {n_size}x{n_size} matrix (Approx { (n_size**2 * 8) / 1e9 :.2f} GB)...")
    
    # 1. Construct the Matrix A (Truncated)
    # We use a vectorized approach to fill A to stay efficient
    A = np.zeros((n_size, n_size))
    
    # Logic: k = (i+j-1)(i+j-2)/2 + j (standard Cantor-like diagonal mapping)
    # For simplicity and speed, we'll use the specific sequence order provided
    for i in range(1, n_size + 1):
        for j in range(1, n_size + 1):
            # Sum of indices (s) determines the diagonal
            s = i + j
            k = (s - 1) * (s - 2) // 2 + j
            A[i-1, j-1] = 1.0 / k

    # 2. Power Method for Spectral Norm
    # Spectral Norm ||A|| = sqrt(max_eigenvalue(A^T * A))
    # We apply Power Method on M = A.T @ A
    
    print("Starting Power Method iterations...")
    x = np.random.rand(n_size)
    x = x / np.linalg.norm(x)
    
    last_sigma = 0
    start_time = time.time()

    for i in range(max_iter):
        # Calculate A^T * (A * x) to avoid large matrix multiplication M = A^T @ A
        # This is more memory-efficient: O(N^2) vs O(N^3)
        ax = A @ x
        at_ax = A.T @ ax
        
        # Eigenvalue estimate (Rayleigh quotient)
        sigma_sq = np.dot(x, at_ax)
        sigma = np.sqrt(sigma_sq)
        
        # Re-normalize
        x = at_ax / np.linalg.norm(at_ax)
        
        # Check convergence
        if abs(sigma - last_sigma) < tolerance:
            print(f"Converged in {i} iterations.")
            break
        last_sigma = sigma
    
    end_time = time.time()
    print(f"Execution Time: {end_time - start_time:.4f} seconds")
    return sigma

if __name__ == "__main__":
    norm = solve_spectral_norm()
    print(f"Estimated Spectral Norm: {norm}")