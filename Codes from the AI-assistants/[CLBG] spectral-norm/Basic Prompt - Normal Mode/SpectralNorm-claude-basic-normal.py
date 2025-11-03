#!/usr/bin/env python3
"""
Spectral-Norm calculation using Power Method
Implements the infinite matrix A with entries:
a_ij = 1/((i-1)+(j-1)+1) for 1-indexed i,j
"""

import sys
import numpy as np
from numba import jit, prange
import time


@jit(nopython=True, fastmath=True, cache=True)
def A_element(i, j):
    """
    Computes the infinite matrix element A(i, j)
    A[i,j] = 1/((i-1) + (j-1) + 1) = 1/(i + j - 1)
    Using 1-based indexing as specified
    """
    return 1.0 / (i + j - 1)


@jit(nopython=True, parallel=True, fastmath=True, cache=True)
def multiply_Av(v, n):
    """
    Computes A * v where A is the infinite matrix
    Returns result as numpy array
    """
    result = np.zeros(n, dtype=np.float64)
    
    for i in prange(n):
        sum_val = 0.0
        for j in range(n):
            sum_val += A_element(i + 1, j + 1) * v[j]
        result[i] = sum_val
    
    return result


@jit(nopython=True, parallel=True, fastmath=True, cache=True)
def multiply_Atv(v, n):
    """
    Computes A^T * v where A^T is the transpose of the infinite matrix
    Since A[i,j] = 1/(i+j-1), A^T[i,j] = A[j,i] = 1/(j+i-1) = 1/(i+j-1)
    So A^T = A (the matrix is symmetric)
    """
    result = np.zeros(n, dtype=np.float64)
    
    for i in prange(n):
        sum_val = 0.0
        for j in range(n):
            sum_val += A_element(j + 1, i + 1) * v[j]
        result[i] = sum_val
    
    return result


@jit(nopython=True, fastmath=True, cache=True)
def multiply_AtAv(v, n):
    """
    Computes A^T * (A * v)
    This is the composition of the two operations above
    """
    # First compute A * v
    Av = multiply_Av(v, n)
    
    # Then compute A^T * (A * v)
    AtAv = multiply_Atv(Av, n)
    
    return AtAv


@jit(nopython=True, fastmath=True, cache=True)
def power_method(n, max_iterations=10):
    """
    Power Method implementation to find the largest eigenvalue
    The spectral norm is the square root of the largest eigenvalue of A^T * A
    """
    # Initialize with random vector
    np.random.seed(42)  # For reproducible results
    v = np.random.random(n).astype(np.float64)
    
    # Normalize initial vector
    norm_v = np.linalg.norm(v)
    v = v / norm_v
    
    eigenvalue = 0.0
    
    for iteration in range(max_iterations):
        # Compute A^T * A * v
        AtAv = multiply_AtAv(v, n)
        
        # Compute eigenvalue estimate (Rayleigh quotient)
        eigenvalue = np.dot(v, AtAv)
        
        # Normalize for next iteration
        norm_AtAv = np.linalg.norm(AtAv)
        if norm_AtAv > 0:
            v = AtAv / norm_AtAv
    
    # The spectral norm is sqrt(largest eigenvalue of A^T * A)
    return np.sqrt(eigenvalue)


def main():
    if len(sys.argv) != 2:
        print("Usage: python spectral_norm.py <n>")
        print("Example: python spectral_norm.py 5500")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: Argument must be an integer")
        sys.exit(1)
    
    if n <= 0:
        print("Error: n must be positive")
        sys.exit(1)
    
    print(f"Computing spectral norm for matrix size {n}x{n}")
    
    # Warm up JIT compilation
    print("Warming up JIT compilation...")
    _ = power_method(100, 2)
    
    # Measure execution time
    start_time = time.time()
    
    # Compute spectral norm
    spectral_norm = power_method(n)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"Spectral norm: {spectral_norm:.9f}")
    print(f"Execution time: {execution_time:.3f} seconds")
    
    # Verify with smaller test case
    if n <= 100:
        print("\nVerification with direct computation (small matrix):")
        # Create the actual matrix for verification
        A = np.zeros((n, n), dtype=np.float64)
        for i in range(n):
            for j in range(n):
                A[i, j] = A_element(i + 1, j + 1)
        
        # Compute spectral norm directly
        eigenvalues = np.linalg.eigvals(A.T @ A)
        direct_spectral_norm = np.sqrt(np.max(eigenvalues))
        print(f"Direct computation: {direct_spectral_norm:.9f}")
        print(f"Difference: {abs(spectral_norm - direct_spectral_norm):.2e}")


if __name__ == "__main__":
    main()