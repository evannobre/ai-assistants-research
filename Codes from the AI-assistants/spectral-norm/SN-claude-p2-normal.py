#!/usr/bin/env python3
"""
Spectral Norm Calculation using Power Method
Computes the spectral norm (largest singular value) of an infinite matrix A
where A[i,j] = 1/(i+j-1) using matrix-free operations.

Author: Backend Optimization Specialist
Target: Ubuntu 24.04.4 64-bit, 8GB RAM, 256GB SSD
"""

import numpy as np
import sys
from typing import Tuple


def eval_A(i: int, j: int) -> float:
    """
    Evaluate matrix element A[i,j] = 1/(i+j-1)
    
    Args:
        i: Row index (0-based)
        j: Column index (0-based)
    
    Returns:
        Matrix element value
    """
    return 1.0 / (i + j + 1)


def eval_A_times_u(u: np.ndarray, n: int) -> np.ndarray:
    """
    Compute matrix-vector product A*u without storing A.
    
    Memory complexity: O(n) instead of O(n²)
    Time complexity: O(n²)
    
    Args:
        u: Input vector of length n
        n: Matrix dimension
    
    Returns:
        Result vector A*u
    """
    result = np.zeros(n, dtype=np.float64)
    
    # Vectorized computation for each row
    for i in range(n):
        # Compute row i of A using vectorized operations
        # A[i,j] = 1/(i+j+1) for j in [0, n-1]
        j_indices = np.arange(n, dtype=np.float64)
        row = 1.0 / (i + j_indices + 1)
        result[i] = np.dot(row, u)
    
    return result


def eval_At_times_u(u: np.ndarray, n: int) -> np.ndarray:
    """
    Compute matrix-vector product A^T*u without storing A.
    
    Since A is symmetric (A[i,j] = A[j,i] for this matrix),
    we still compute it explicitly for clarity.
    
    Args:
        u: Input vector of length n
        n: Matrix dimension
    
    Returns:
        Result vector A^T*u
    """
    result = np.zeros(n, dtype=np.float64)
    
    # Vectorized computation for each column
    for j in range(n):
        # Compute column j of A (= row j of A^T)
        i_indices = np.arange(n, dtype=np.float64)
        col = 1.0 / (i_indices + j + 1)
        result[j] = np.dot(col, u)
    
    return result


def eval_AtA_times_u(u: np.ndarray, n: int) -> np.ndarray:
    """
    Compute (A^T * A) * u efficiently.
    
    This is the core operation for power iteration on A^T*A,
    which gives us the squared singular values.
    
    Args:
        u: Input vector of length n
        n: Matrix dimension
    
    Returns:
        Result vector (A^T*A)*u
    """
    return eval_At_times_u(eval_A_times_u(u, n), n)


def power_method(n: int, num_iterations: int = 10) -> float:
    """
    Compute spectral norm (largest singular value) using power method.
    
    The spectral norm is sqrt(λ_max(A^T*A)) where λ_max is the
    largest eigenvalue.
    
    Algorithm:
    1. Start with random vector u
    2. Iterate: v = A^T*A*u, u = v/||v||
    3. Eigenvalue ≈ u^T*(A^T*A)*u
    4. Spectral norm = sqrt(eigenvalue)
    
    Args:
        n: Matrix dimension (approximation of infinite matrix)
        num_iterations: Number of power iterations (default: 10)
    
    Returns:
        Spectral norm (largest singular value)
    """
    # Initialize with uniform vector
    u = np.ones(n, dtype=np.float64)
    v = np.zeros(n, dtype=np.float64)
    
    # Power iteration
    for _ in range(num_iterations):
        # v = (A^T * A) * u
        v = eval_AtA_times_u(u, n)
        
        # u = (A * A^T) * v
        u = eval_AtA_times_u(v, n)
        
        # Normalize u
        u_norm = np.linalg.norm(u)
        if u_norm > 0:
            u = u / u_norm
    
    # Compute Rayleigh quotient for final eigenvalue estimate
    v = eval_AtA_times_u(u, n)
    
    # λ ≈ u^T * v / (u^T * u)
    eigenvalue = np.dot(u, v) / np.dot(u, u)
    
    # Spectral norm is square root of largest eigenvalue of A^T*A
    spectral_norm = np.sqrt(eigenvalue)
    
    return spectral_norm


def estimate_memory_usage(n: int) -> Tuple[float, str]:
    """
    Estimate memory usage for given matrix size.
    
    Args:
        n: Matrix dimension
    
    Returns:
        Tuple of (memory in bytes, human-readable string)
    """
    # Each vector: n * 8 bytes (float64)
    # We use approximately 3-4 vectors at most
    vector_memory = n * 8 * 4
    
    # Overhead and Python objects
    overhead = 1024 * 1024 * 100  # ~100 MB overhead
    
    total_bytes = vector_memory + overhead
    
    if total_bytes < 1024**2:
        return total_bytes, f"{total_bytes / 1024:.2f} KB"
    elif total_bytes < 1024**3:
        return total_bytes, f"{total_bytes / (1024**2):.2f} MB"
    else:
        return total_bytes, f"{total_bytes / (1024**3):.2f} GB"


def main():
    """
    Main execution function with command-line interface.
    """
    # Default parameters
    n = 5500  # Standard benchmark size
    iterations = 10
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Invalid matrix size: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            iterations = int(sys.argv[2])
        except ValueError:
            print(f"Invalid iteration count: {sys.argv[2]}", file=sys.stderr)
            sys.exit(1)
    
    # Estimate memory usage
    memory_bytes, memory_str = estimate_memory_usage(n)
    
    # Check if we exceed available RAM (8GB)
    max_memory = 8 * 1024**3
    if memory_bytes > max_memory * 0.8:  # Use max 80% of RAM
        print(f"Warning: Estimated memory usage ({memory_str}) may exceed available RAM", 
              file=sys.stderr)
        recommended_n = int(np.sqrt((max_memory * 0.8 - 100*1024**2) / (8 * 4)))
        print(f"Recommended maximum n: {recommended_n}", file=sys.stderr)
    
    print(f"Computing spectral norm for {n}×{n} matrix")
    print(f"Iterations: {iterations}")
    print(f"Estimated memory usage: {memory_str}")
    print()
    
    # Compute spectral norm
    result = power_method(n, iterations)
    
    # Output result with high precision
    print(f"{result:.9f}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
