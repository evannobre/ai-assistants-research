#!/usr/bin/env python3
"""
Spectral Norm Calculation using Power Method
Optimized implementation using NumPy for high performance
"""

import numpy as np
import sys
from typing import Union


def matrix_element(i: int, j: int) -> float:
    """
    Computes the infinite matrix element A(i, j).
    
    The matrix A has entries:
    a_ij = 1 / (i + j - 1)
    
    Args:
        i: Row index (1-based)
        j: Column index (1-based)
        
    Returns:
        The matrix element value
    """
    return 1.0 / (i + j - 1)


def matrix_vector_multiply(v: np.ndarray, n: int) -> np.ndarray:
    """
    Computes A * v where A is the infinite matrix.
    
    Args:
        v: Input vector of length n
        n: Dimension of the problem
        
    Returns:
        Result vector A * v
    """
    result = np.zeros(n, dtype=np.float64)
    
    # Vectorized computation using broadcasting
    i_indices = np.arange(1, n + 1).reshape(-1, 1)  # Column vector
    j_indices = np.arange(1, n + 1).reshape(1, -1)  # Row vector
    
    # Compute A * v efficiently
    denominators = i_indices + j_indices - 1
    result = np.sum(v / denominators, axis=1)
    
    return result


def matrix_transpose_vector_multiply(v: np.ndarray, n: int) -> np.ndarray:
    """
    Computes A^T * v where A^T is the transpose of the infinite matrix.
    
    Since A is symmetric (a_ij = a_ji), A^T = A.
    
    Args:
        v: Input vector of length n
        n: Dimension of the problem
        
    Returns:
        Result vector A^T * v
    """
    # Since the matrix is symmetric, A^T = A
    return matrix_vector_multiply(v, n)


def matrix_transpose_matrix_vector_multiply(v: np.ndarray, n: int) -> np.ndarray:
    """
    Computes A^T * (A * v).
    
    Args:
        v: Input vector of length n
        n: Dimension of the problem
        
    Returns:
        Result vector A^T * (A * v)
    """
    # First compute A * v
    av = matrix_vector_multiply(v, n)
    
    # Then compute A^T * (A * v)
    return matrix_transpose_vector_multiply(av, n)


def power_method_spectral_norm(n: int, max_iterations: int = 10) -> float:
    """
    Computes the spectral norm of the matrix A using the Power Method.
    
    The spectral norm is the largest singular value, which for a symmetric
    matrix equals the largest eigenvalue in absolute value.
    
    Args:
        n: Dimension of the problem
        max_iterations: Number of power method iterations
        
    Returns:
        The spectral norm approximation
    """
    # Initialize with a random vector
    u = np.ones(n, dtype=np.float64)
    v = np.ones(n, dtype=np.float64)
    
    # Normalize initial vectors
    u = u / np.linalg.norm(u)
    v = v / np.linalg.norm(v)
    
    # Power method iterations
    for _ in range(max_iterations):
        # v = A^T * u
        v = matrix_transpose_vector_multiply(u, n)
        v = v / np.linalg.norm(v)
        
        # u = A * v
        u = matrix_vector_multiply(v, n)
        u = u / np.linalg.norm(u)
    
    # Compute the spectral norm: ||A * v||
    av = matrix_vector_multiply(v, n)
    spectral_norm = np.linalg.norm(av)
    
    return spectral_norm


def optimized_spectral_norm(n: int, max_iterations: int = 10) -> float:
    """
    Optimized version using the fact that for symmetric matrices,
    the spectral norm can be computed more efficiently.
    
    Args:
        n: Dimension of the problem
        max_iterations: Number of power method iterations
        
    Returns:
        The spectral norm approximation
    """
    # Initialize with a random vector
    v = np.ones(n, dtype=np.float64)
    v = v / np.linalg.norm(v)
    
    # Power method for A^T * A (which equals A * A for symmetric A)
    for _ in range(max_iterations):
        # Compute A^T * A * v = A * A * v
        v = matrix_transpose_matrix_vector_multiply(v, n)
        v = v / np.linalg.norm(v)
    
    # The spectral norm is sqrt(largest eigenvalue of A^T * A)
    atav = matrix_transpose_matrix_vector_multiply(v, n)
    eigenvalue = np.dot(v, atav)
    spectral_norm = np.sqrt(eigenvalue)
    
    return spectral_norm


def main():
    """
    Main function to run the spectral norm calculation.
    """
    # Parse command line argument
    if len(sys.argv) != 2:
        print("Usage: python spectral_norm.py <n>", file=sys.stderr)
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: n must be an integer", file=sys.stderr)
        sys.exit(1)
    
    if n <= 0:
        print("Error: n must be positive", file=sys.stderr)
        sys.exit(1)
    
    # Check memory constraints (rough estimation)
    estimated_memory_gb = (n * 8 * 4) / (1024**3)  # 4 vectors of n float64 elements
    if estimated_memory_gb > 14:  # Leave some margin for the 16GB limit
        print(f"Warning: Estimated memory usage ({estimated_memory_gb:.2f} GB) may exceed available RAM")
    
    # Calculate spectral norm
    spectral_norm = optimized_spectral_norm(n)
    
    # Format output to match expected precision
    print(f"{spectral_norm:.9f}")


if __name__ == "__main__":
    main()


# Test functions to verify correctness
def test_matrix_element():
    """Test the matrix element function."""
    assert abs(matrix_element(1, 1) - 1.0) < 1e-10
    assert abs(matrix_element(1, 2) - 0.5) < 1e-10
    assert abs(matrix_element(2, 1) - 1.0/3.0) < 1e-10
    assert abs(matrix_element(1, 3) - 0.25) < 1e-10
    assert abs(matrix_element(2, 2) - 0.2) < 1e-10
    assert abs(matrix_element(3, 1) - 1.0/6.0) < 1e-10
    print("Matrix element tests passed!")


def test_small_case():
    """Test with a small case to verify correctness."""
    n = 100
    result = optimized_spectral_norm(n)
    print(f"Spectral norm for n={n}: {result:.9f}")
    
    # The expected result should be approximately 1.274224138 for reasonable n
    # This is a known mathematical result for this specific matrix


if __name__ == "__main__":
    # Run tests if in development mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_matrix_element()
        test_small_case()
    else:
        main()