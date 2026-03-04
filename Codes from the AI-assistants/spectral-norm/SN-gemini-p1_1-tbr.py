import numpy as np

def solve_spectral_norm(n_size=2000, tolerance=1e-9, max_iterations=1000):
    """
    Estimates the spectral norm of the specific infinite matrix A using 
    Truncation and the Power Method.
    
    Args:
        n_size (int): The truncation size (NxN) of the infinite matrix.
        tolerance (float): Convergence criterion.
        max_iterations (int): Safety break for the loop.
        
    Returns:
        float: The estimated spectral norm.
    """
    
    print(f"--- Initializing Matrix (Truncated to {n_size}x{n_size}) ---")
    
    # 1. Generate Matrix A using Vectorization (Native C-speed via NumPy)
    # We use 0-based indexing for calculation, so we adjust the math formula:
    # Math formula uses 1-based i,j. Let I, J be 0-based.
    # i = I + 1, j = J + 1.
    # Denom = ((I+1 + J+1 - 2) * (I+1 + J+1 - 1)) / 2 + (I+1)
    #       = ((I+J) * (I+J+1)) / 2 + I + 1
    
    I = np.arange(n_size).reshape(-1, 1) # Column vector of indices
    J = np.arange(n_size).reshape(1, -1) # Row vector of indices
    
    # Broadcasting allows us to compute the whole matrix in one compiled op
    denominators = ((I + J) * (I + J + 1)) / 2 + (I + 1)
    A = 1.0 / denominators
    
    print("Matrix generated. Starting Power Method...")

    # 2. Power Method Initialization
    # Start with a random unit vector
    v = np.random.rand(n_size)
    v = v / np.linalg.norm(v)
    
    sigma = 0.0
    
    for k in range(max_iterations):
        # 3. Iteration step
        # We need to compute eigenvectors of (A.T @ A).
        # Instead of computing M = A.T @ A (which is O(N^3)), 
        # we compute A.T @ (A @ v) which is O(N^2).
        
        # Step A: Apply A
        Av = np.dot(A, v)
        
        # Step B: Apply A_transpose
        ATAv = np.dot(A.T, Av)
        
        # Step C: Normalize
        # The Rayleigh quotient for A^T A approaches lambda_max^2.
        # However, the norm of Av approximates the singular value directly 
        # if v converges to the principal eigenvector.
        
        new_v = ATAv / np.linalg.norm(ATAv)
        
        # Calculate current spectral norm estimate: ||Av||
        # (Since sigma = sqrt(lambda_max(A^T A)))
        current_sigma = np.linalg.norm(np.dot(A, new_v))
        
        # Check convergence
        if abs(current_sigma - sigma) < tolerance:
            print(f"Converged at iteration {k+1}")
            sigma = current_sigma
            break
            
        sigma = current_sigma
        v = new_v

    return sigma

# --- Execution ---
if __name__ == "__main__":
    # N=5000 is usually sufficient for high precision on this specific decaying matrix
    estimated_norm = solve_spectral_norm(n_size=5000)
    
    print("-" * 30)
    print(f"Estimated Spectral Norm: {estimated_norm:.8f}")