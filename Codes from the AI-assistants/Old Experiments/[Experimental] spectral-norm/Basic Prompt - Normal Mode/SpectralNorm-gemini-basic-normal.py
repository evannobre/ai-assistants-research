import numpy as np

def generate_matrix_entry(i, j):
    """
    Generates the entry A_ij based on the provided pattern.
    i, j are 0-indexed for Python arrays, so we convert them to 1-indexed for the formula.
    """
    _i = i + 1
    _j = j + 1
    s = _i + _j
    k = (s - 2) * (s - 1) // 2 + _i
    return 1.0 / k

def construct_truncated_matrix(N):
    """
    Constructs the N x N truncated matrix A_N.
    """
    A_N = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            A_N[i, j] = generate_matrix_entry(i, j)
    return A_N

def power_method_spectral_norm(N, max_iterations=1000, tolerance=1e-7):
    """
    Estimates the spectral norm of the N x N truncated matrix
    using the Power Method on A_N.T @ A_N.

    Args:
        N (int): Dimension of the truncated matrix.
        max_iterations (int): Maximum number of iterations for the Power Method.
        tolerance (float): Tolerance for convergence.

    Returns:
        float: Estimated spectral norm.
        numpy.ndarray: Estimated dominant eigenvector of A_N.T @ A_N.
        list: History of estimated eigenvalues of A_N.T @ A_N.
    """
    if N <= 0:
        raise ValueError("N must be a positive integer.")

    print(f"Constructing {N}x{N} matrix A_N...")
    A_N = construct_truncated_matrix(N)
    print("Matrix A_N constructed.")

    # Form B = A_N.T @ A_N
    B = A_N.T @ A_N
    print("Matrix B = A_N.T @ A_N formed.")

    # Initialize a random vector
    v = np.random.rand(N)
    v = v / np.linalg.norm(v)  # Normalize it

    eigenvalue_history = []
    
    print("Starting Power Method iterations...")
    for k in range(max_iterations):
        # Apply B to v
        w = B @ v
        
        # Calculate the Rayleigh quotient for the eigenvalue estimate (or just the norm)
        # Using the norm for the eigenvalue magnitude and then normalizing for the eigenvector.
        current_eigenvalue_mag = np.linalg.norm(w)

        # Handle potential division by zero if w is a zero vector (highly unlikely with random init)
        if current_eigenvalue_mag < 1e-15:
            print("Warning: Vector norm too small, exiting.")
            break

        # Normalize v for the next iteration
        v_next = w / current_eigenvalue_mag

        eigenvalue_history.append(current_eigenvalue_mag)

        # Check for convergence
        if k > 0:
            if abs(current_eigenvalue_mag - eigenvalue_history[k-1]) < tolerance * current_eigenvalue_mag:
                print(f"Converged after {k+1} iterations.")
                break
        
        v = v_next
    else:
        print(f"Power Method did not converge within {max_iterations} iterations.")

    # The spectral norm is the square root of the largest eigenvalue of B
    estimated_spectral_norm = np.sqrt(eigenvalue_history[-1])

    return estimated_spectral_norm, v, eigenvalue_history

if __name__ == "__main__":
    N_values = [5, 10, 20] # Example truncation sizes

    for N in N_values:
        print(f"\n--- Running for N = {N} ---")
        spectral_norm, dominant_eigenvector, history = power_method_spectral_norm(N)
        
        print(f"Estimated Spectral Norm for N={N}: {spectral_norm}")
        # print(f"Dominant Eigenvector for N={N}:\n{dominant_eigenvector}")
        # print(f"Eigenvalue history (last 10 values) for N={N}: {history[-10:]}")

        # Verification with NumPy's svd (Singular Value Decomposition)
        # SVD directly gives singular values, the largest of which is the spectral norm.
        # This is for comparison/verification, not part of the Power Method itself.
        A_N_verify = construct_truncated_matrix(N)
        _, s, _ = np.linalg.svd(A_N_verify)
        np_spectral_norm = s[0]
        print(f"NumPy's SVD Spectral Norm for N={N}: {np_spectral_norm}")
        print(f"Difference: {abs(spectral_norm - np_spectral_norm):.2e}")