import numpy as np

def create_matrix(N: int) -> np.ndarray:
    """
    Generates the N x N truncated matrix A using NumPy broadcasting.
    This avoids slow native Python loops.
    """
    # Create column and row index vectors
    i = np.arange(N).reshape(-1, 1)
    j = np.arange(N).reshape(1, -1)
    
    # Apply the Cantor diagonalization formula
    return 1.0 / (((i + j) * (i + j + 1) / 2.0) + i + 1)

def spectral_norm(N: int, tol: float = 1e-9, max_iter: int = 100) -> float:
    """
    Computes the spectral norm of the N x N matrix using the Power Method.
    """
    A = create_matrix(N)
    AtA = A.T @ A  # M = A^T A

    # Step 1: Initialize u as a normalized vector of ones
    u = np.ones(N)
    u /= np.linalg.norm(u)

    # Step 2 & 3: Iterate until convergence
    for _ in range(max_iter):
        u_next = AtA @ u
        u_next /= np.linalg.norm(u_next)

        # Check for convergence
        if np.linalg.norm(u_next - u) < tol:
            u = u_next
            break
            
        u = u_next

    # Step 4: Compute the Rayleigh quotient for A^T A
    eigenvalue = u.T @ AtA @ u
    
    # Step 5: The spectral norm is the square root of the largest eigenvalue
    return np.sqrt(eigenvalue)

if __name__ == "__main__":
    # Simulate for a 1000x1000 truncation
    N = 1000
    norm_value = spectral_norm(N)
    print(f"Approximated Spectral Norm (N={N}): {norm_value:.9f}")