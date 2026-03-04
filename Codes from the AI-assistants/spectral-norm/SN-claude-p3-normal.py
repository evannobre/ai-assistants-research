#!/usr/bin/env python3
"""
Spectral Norm Calculation using Power Method
Computes the spectral norm of an infinite Hilbert-like matrix
"""

import sys
import numpy as np


def A(i, j):
    """
    Computes the infinite matrix element A(i, j)
    Formula: A[i,j] = 1 / (i + j - 1)
    Using 1-based indexing: A[1,1]=1, A[1,2]=1/2, A[2,1]=1/3, etc.
    """
    return 1.0 / (i + j - 1)


def multiply_Av(v):
    """
    Computes A * v (matrix-vector multiplication)
    
    Args:
        v: input vector (numpy array)
    
    Returns:
        result vector after A * v
    """
    n = len(v)
    result = np.zeros(n)
    
    for i in range(n):
        for j in range(n):
            # Using 1-based indexing for the formula
            result[i] += A(i + 1, j + 1) * v[j]
    
    return result


def multiply_Atv(v):
    """
    Computes A^T * v (transpose matrix-vector multiplication)
    
    For symmetric matrix: A^T[i,j] = A[j,i]
    Since A[i,j] = 1/(i+j-1) is symmetric, A^T = A
    But we implement it explicitly for clarity
    
    Args:
        v: input vector (numpy array)
    
    Returns:
        result vector after A^T * v
    """
    n = len(v)
    result = np.zeros(n)
    
    for i in range(n):
        for j in range(n):
            # A^T[i,j] = A[j,i]
            result[i] += A(j + 1, i + 1) * v[j]
    
    return result


def multiply_AtAv(v):
    """
    Computes A^T * (A * v)
    
    Args:
        v: input vector (numpy array)
    
    Returns:
        result vector after A^T * A * v
    """
    return multiply_Atv(multiply_Av(v))


def spectral_norm(n, iterations=10):
    """
    Calculates the spectral norm (largest singular value) using Power Method
    
    The spectral norm is sqrt(largest eigenvalue of A^T * A)
    
    Args:
        n: matrix dimension
        iterations: number of power iterations
    
    Returns:
        spectral norm value
    """
    # Initialize vector with ones
    u = np.ones(n)
    v = np.ones(n)
    
    # Power iteration
    for _ in range(iterations):
        # v = A^T * A * u
        v = multiply_AtAv(u)
        # u = A * A^T * v
        u = multiply_AtAv(v)
        
    # Compute Rayleigh quotient
    # ||A||_2 = sqrt((A^T*A*u, u) / (u, u))
    vBv = np.dot(v, u)
    vv = np.dot(u, u)
    
    return np.sqrt(vBv / vv)


def main():
    """Main entry point"""
    # Get matrix size from command line, default to 100
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    # Calculate spectral norm
    result = spectral_norm(n)
    
    # Print result with 9 decimal places
    print(f"{result:.9f}")


if __name__ == "__main__":
    main()
