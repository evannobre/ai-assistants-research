import numpy as np

def generate_matrix_truncation(n: int) -> np.ndarray:
    """
    Generates the n x n truncation of the infinite matrix A.

    The matrix is filled with values 1/d where d=1, 2, 3,... along
    the anti-diagonals, starting from the top-left.
    """
    A = np.zeros((n, n))
    d = 1
    # Iterate through the anti-diagonal sums (i + j)
    for s in range(2, 2 * n + 1):
        # For each sum, iterate through possible j values
        for j in range(1, s):
            i = s - j
            # Check if the indices (i, j) are within the n x n bounds
            if i <= n and j <= n:
                A[i - 1, j - 1] = 1.0 / d
                d += 1
    return A

def simulate_spectral_norm(n_max: int = 100, tol: float = 1e-7) -> float:
    """
    Uses the Power Method to solve the spectral-norm simulation of the
    infinite matrix A.

    Args:
        n_max: The maximum size of the matrix truncation to test.
        tol: The convergence tolerance for the spectral norm.

    Returns:
        The estimated spectral norm of the infinite matrix.
    """
    sigma_prev = 0.0
    print("--- Starting Spectral Norm Simulation ---")
    print(f"{'Size (n)':<10}{'Spectral Norm':<25}")
    print("-" * 35)

    for n in range(1, n_max + 1):
        # 1. Generate the n x n truncated matrix An
        A_n = generate_matrix_truncation(n)

        # 2. Apply the Power Method to find the spectral norm of An
        # Initialize a random vector
        v = np.random.rand(n)
        v = v / np.linalg.norm(v)

        # Iterate to find the dominant eigenvector of A_n.T @ A_n
        for _ in range(150): # Max power iterations
            # This combines the two steps: w = A_n.T @ (A_n @ v)
            w = A_n.T @ A_n @ v
            v = w / np.linalg.norm(w)
        
        # The spectral norm is ||A_n @ v||
        sigma_n = np.linalg.norm(A_n @ v)
        
        print(f"{n:<10}{sigma_n:<25.10f}")

        # 3. Check for convergence of the spectral norm sequence
        if n > 1 and np.abs(sigma_n - sigma_prev) < tol:
            print(f"\nConvergence reached at n = {n}.")
            print(f"Estimated Spectral Norm: {sigma_n:.10f}")
            return sigma_n

        sigma_prev = sigma_n

    print(f"\nReached max iterations (n_max = {n_max}) without full convergence.")
    print(f"Final estimated Spectral Norm: {sigma_prev:.10f}")
    return sigma_prev

if __name__ == '__main__':
    # Run the simulation
    spectral_norm = simulate_spectral_norm()