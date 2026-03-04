#!/usr/bin/env python3
"""
Spectral Norm Calculator using Power Method
Computes the largest eigenvalue of A^T * A for an infinite matrix A
where A[i,j] = 1/((i+j)*(i+j+1)/2 + i + 1)

Matrix entries pattern:
a11=1, a12=1/2, a21=1/3, a13=1/4, a22=1/5, a31=1/6, etc.
"""

import sys
from math import sqrt


def eval_A(i, j):
    """
    Compute matrix entry A[i,j] efficiently.
    Uses the formula: 1/((i+j)*(i+j+1)/2 + i + 1)
    
    Args:
        i: row index (0-based)
        j: column index (0-based)
    
    Returns:
        float: matrix entry value
    """
    return 1.0 / ((i + j) * (i + j + 1) // 2 + i + 1)


def eval_A_times_u(u, v, n):
    """
    Compute matrix-vector product: v = A * u
    
    Args:
        u: input vector
        v: output vector (modified in-place)
        n: dimension of vectors
    """
    for i in range(n):
        total = 0.0
        for j in range(n):
            total += eval_A(i, j) * u[j]
        v[i] = total


def eval_At_times_u(u, v, n):
    """
    Compute transpose matrix-vector product: v = A^T * u
    
    Args:
        u: input vector
        v: output vector (modified in-place)
        n: dimension of vectors
    """
    for i in range(n):
        total = 0.0
        for j in range(n):
            total += eval_A(j, i) * u[j]
        v[i] = total


def eval_AtA_times_u(u, v, n):
    """
    Compute A^T * A * u efficiently using temporary storage.
    
    Args:
        u: input vector
        v: output vector (modified in-place)
        n: dimension of vectors
    """
    tmp = [0.0] * n
    eval_A_times_u(u, tmp, n)
    eval_At_times_u(tmp, v, n)


def spectral_norm(n, iterations=10):
    """
    Calculate spectral norm using Power Method.
    
    The spectral norm is the largest singular value of matrix A,
    which equals sqrt(largest eigenvalue of A^T * A).
    
    Args:
        n: matrix dimension (approximation of infinite matrix)
        iterations: number of power iterations (default: 10)
    
    Returns:
        float: spectral norm approximation
    """
    # Initialize vectors
    u = [1.0] * n
    v = [0.0] * n
    
    # Power iteration
    for _ in range(iterations):
        eval_AtA_times_u(u, v, n)
        eval_AtA_times_u(v, u, n)
    
    # Compute Rayleigh quotient
    vBv = vv = 0.0
    for i in range(n):
        vBv += u[i] * v[i]
        vv += v[i] * v[i]
    
    return sqrt(vBv / vv)


def main():
    """
    Main entry point for spectral norm calculation.
    Accepts matrix size as command-line argument.
    """
    # Default size or from command line
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    # Memory check: ensure we don't exceed system constraints
    # Each vector takes n * 8 bytes (float64)
    # We use approximately 4 vectors simultaneously
    required_memory_mb = (n * 8 * 4) / (1024 * 1024)
    
    if required_memory_mb > 1000:  # Conservative limit
        print(f"Warning: Requested size requires ~{required_memory_mb:.1f} MB", 
              file=sys.stderr)
        print("This may exceed safe memory limits for your system.", 
              file=sys.stderr)
        sys.exit(1)
    
    # Calculate spectral norm
    result = spectral_norm(n)
    
    # Output with precision
    print(f"{result:.9f}")


if __name__ == "__main__":
    main()
