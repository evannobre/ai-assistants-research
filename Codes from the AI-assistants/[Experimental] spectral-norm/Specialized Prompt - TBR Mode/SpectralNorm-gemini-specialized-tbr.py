#!/usr/bin/env python3
"""
This script calculates the spectral norm of a truncated infinite matrix
using the Power Method.
"""

import numpy as np
import time
import sys

def create_matrix_vectorized(n: int) -> np.ndarray:
    """
    Creates an n x n truncation of the specified infinite matrix using
    vectorized NumPy operations for high performance.

    The formula for entries (1-based indexing) is:
    a_ij = 1 / ( ( (i+j-2)*(i+j-1) )/2 + i )

    Args:
        n: The dimension of the square matrix.

    Returns:
        An n x n NumPy array representing the truncated matrix.
    """
    # Create 1-based index arrays for i and j
    i = np.arange(1, n + 1, dtype=np.float64)[:, np.newaxis]  # Column vector
    j = np.arange(1, n + 1, dtype=np.float64)[np.newaxis, :]  # Row vector
    
    # Calculate the denominator using broadcasting
    s = i + j - 2
    denominator = (s * (s + 1)) / 2 + i
    
    return 1.0 / denominator

def power_method_spectral_norm(A: np.ndarray, tol: float = 1e-9, max_iter: int = 2000) -> float:
    """
    Calculates the spectral norm of matrix A using the Power Method
    by finding its largest singular value.

    Args:
        A: The input matrix (n x m).
        tol: The tolerance for convergence.
        max_iter: The maximum number of iterations.

    Returns:
        The estimated spectral norm (largest singular value).
    """
    n, m = A.shape
    # Start with a random unit vector v of the correct dimension
    v = np.random.rand(m)
    v = v / np.linalg.norm(v)

    sigma_prev = 0.0

    for i in range(max_iter):
        # Apply A to v
        u = A @ v
        # Normalize u (u becomes the left singular vector estimate)
        u = u / np.linalg.norm(u)

        # Apply A's transpose to u
        v = A.T @ u

        # The current estimate for the largest singular value (spectral norm)
        # is the norm of the resulting vector.
        sigma_curr = np.linalg.norm(v)
        
        # Normalize v for the next iteration (v becomes the right singular vector estimate)
        v = v / sigma_curr

        # Check for convergence
        if abs(sigma_curr - sigma_prev) < tol:
            print(f"Converged after {i+1} iterations.")
            return sigma_curr

        sigma_prev = sigma_curr

    print(f"Warning: Did not converge within {max_iter} iterations.")
    return sigma_curr

def main():
    """
    Main function to drive the spectral norm simulation.
    """
    # Set a default matrix size, but allow it to be overridden by a command-line argument
    if len(sys.argv) > 1:
        try:
            matrix_size_n = int(sys.argv[1])
        except ValueError:
            print("Error: Please provide an integer for the matrix size.")
            sys.exit(1)
    else:
        matrix_size_n = 2000  # Default size

    tolerance = 1e-12

    print("--- Spectral Norm Simulation ---")
    print(f"Target Machine: Ubuntu 24.04.2 LTS, 16 GB vRAM, 30 GB SSD\n")
    print(f"Simulating for a truncated {matrix_size_n}x{matrix_size_n} matrix...")

    # --- Hardware Compliance Check ---
    # Memory for one float64 is 8 bytes.
    mem_required_gb = (matrix_size_n ** 2) * 8 / (1024**3)
    print(f"Estimated memory for the matrix alone: {mem_required_gb:.3f} GB")
    
    # Check against available vRAM (using a conservative 15 GB threshold)
    if mem_required_gb > 15.0:
        print("\nError: The chosen matrix size is too large for 16 GB of vRAM.")
        print("Please choose a smaller size (e.g., up to ~42,000).")
        sys.exit(1)

    # 1. Create the matrix
    print("\n[1] Creating the matrix...")
    start_time = time.time()
    A = create_matrix_vectorized(matrix_size_n)
    end_time = time.time()
    print(f"    Matrix creation time: {end_time - start_time:.4f} seconds.")
    # print("    First 5x5 block of A:\n", A[:5, :5])

    # 2. Calculate spectral norm
    print("\n[2] Calculating spectral norm using the Power Method...")
    start_time = time.time()
    spectral_norm = power_method_spectral_norm(A, tol=tolerance)
    end_time = time.time()
    print(f"    Power method calculation time: {end_time - start_time:.4f} seconds.")

    # --- Final Result ---
    print("\n--- Result ---")
    print(f"The estimated spectral norm for the {matrix_size_n}x{matrix_size_n} matrix is:")
    print(f"||A_{matrix_size_n}||₂ = {spectral_norm:.12f}")


if __name__ == "__main__":
    main()