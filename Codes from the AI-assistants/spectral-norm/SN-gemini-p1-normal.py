import numpy as np

def get_entry_value(i, j):
    """Calculates a_ij based on the zig-zag sequence 1/k."""
    # i, j are 0-indexed here
    row, col = i + 1, j + 1
    s = row + col
    preceding = (s - 2) * (s - 1) // 2
    
    if s % 2 == 1: # Odd diagonal sum: moving up-right
        offset = col
    else:          # Even diagonal sum: moving down-left
        offset = row
        
    k = preceding + offset
    return 1.0 / k

def power_method_spectral_norm(n_dims, iterations=100, tolerance=1e-9):
    # 1. Construct the matrix A for the finite simulation
    A = np.fromfunction(np.vectorize(get_entry_value), (n_dims, n_dims))
    
    # The spectral norm of A is sqrt(max_eigenvalue(A.T @ A))
    # Let's apply Power Method to M = A.T @ A
    M = A.T @ A
    
    # 2. Initialize a random vector
    v = np.random.rand(n_dims)
    v = v / np.linalg.norm(v)
    
    last_sigma = 0
    
    for _ in range(iterations):
        # 3. Multiply by M
        w = M @ v
        
        # 4. Estimate eigenvalue (Rayleigh quotient)
        sigma_sq = np.dot(v, w)
        sigma = np.sqrt(sigma_sq)
        
        # 5. Re-normalize
        v = w / np.linalg.norm(w)
        
        # Check convergence
        if abs(sigma - last_sigma) < tolerance:
            break
        last_sigma = sigma
        
    return sigma

# Execution
n = 500  # Approximation of the 'infinite' matrix
norm = power_method_spectral_norm(n)
print(f"Approximated Spectral Norm for N={n}: {norm:.10f}")