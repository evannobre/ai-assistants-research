import numpy as np

def spectral_norm(N=2000, num_iterations=10):
    """
    Approximates the spectral norm of an infinite matrix truncated to NxN 
    using the Power Method.
    """
    
    # 1. Generate 0-based indices using NumPy broadcasting
    # i represents row indices, j represents column indices
    i = np.arange(N)[:, np.newaxis]
    j = np.arange(N)[np.newaxis, :]
    
    # 2. Build the matrix A entirely in native C-backend
    # Using the Cantor pairing function for 0-based indices
    A = 1.0 / (((i + j) * (i + j + 1) / 2.0) + i + 1.0)
    
    # 3. Initialize the vector u with ones
    u = np.ones(N)
    
    # 4. Power Method Iterations
    # We don't need to normalize inside the loop because the spectral norm 
    # of this specific matrix is ~1.274, so (1.274)^10 will not cause float overflow.
    for _ in range(num_iterations):
        v = A @ u       # Multiply by A
        u = A.T @ v     # Multiply by A Transpose
        
    # 5. Calculate final Rayleigh quotient
    # u is now approximated as (A^T A)^num_iterations * u_initial
    # We calculate v = A * u one last time for the final norm evaluation
    v = A @ u
    
    # Spectral norm is sqrt( (v^T * v) / (u^T * u) )
    result = np.sqrt(np.dot(v, v) / np.dot(u, u))
    
    return result

# Execute the simulation
if __name__ == "__main__":
    N = 2000
    iterations = 10
    norm = spectral_norm(N, iterations)
    
    # Standard Spectral Norm of this infinite matrix converges to ~1.274224153
    print(f"Matrix size: {N}x{N}")
    print(f"Iterations: {iterations}")
    print(f"Approximated Spectral Norm: {norm:.9f}")