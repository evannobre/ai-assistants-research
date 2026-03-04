#!/usr/bin/env python3
"""
Spectral Norm Calculation using Power Method
Computes the spectral norm of an infinite Hilbert-like matrix
where A(i,j) = 1/((i+j-1)(i+j)/2 + i)
"""

import sys
import numpy as np


def A(i, j):
    """
    (i) Computes the infinite matrix element A(i, j)
    Matrix entry formula: 1/((i+j-1)(i+j)/2 + i)
    
    Args:
        i: row index (0-based)
        j: column index (0-based)
    
    Returns:
        Matrix element value
    """
    return 1.0 / ((i + j) * (i + j + 1) // 2 + i + 1)


def multiply_Av(v):
    """
    (ii) Computes A*v (matrix-vector product)
    
    Args:
        v: input vector (numpy array)
    
    Returns:
        Result vector A*v (numpy array)
    """
    n = len(v)
    result = np.zeros(n)
    
    for i in range(n):
        sum_val = 0.0
        for j in range(n):
            sum_val += A(i, j) * v[j]
        result[i] = sum_val
    
    return result


def multiply_Atv(v):
    """
    (iii) Computes A^T*v (transpose matrix-vector product)
    
    Args:
        v: input vector (numpy array)
    
    Returns:
        Result vector A^T*v (numpy array)
    """
    n = len(v)
    result = np.zeros(n)
    
    for i in range(n):
        sum_val = 0.0
        for j in range(n):
            sum_val += A(j, i) * v[j]
        result[i] = sum_val
    
    return result


def multiply_AtAv(v):
    """
    (iv) Computes A^T*(A*v)
    
    Args:
        v: input vector (numpy array)
    
    Returns:
        Result vector A^T*A*v (numpy array)
    """
    return multiply_Atv(multiply_Av(v))


def spectral_norm(n, iterations=10):
    """
    Calculates the spectral norm using the Power Method
    
    Args:
        n: matrix dimension
        iterations: number of power iterations (default: 10)
    
    Returns:
        Approximation of the spectral norm
    """
    # Initialize with a vector of ones
    u = np.ones(n)
    v = np.ones(n)
    
    # Power iteration
    for _ in range(iterations):
        v = multiply_AtAv(u)
        u = multiply_AtAv(v)
    
    # Calculate the Rayleigh quotient
    # ||A||_2 = sqrt((u^T * A^T*A*v) / (v^T * v))
    vv = np.dot(v, v)
    vBv = np.dot(u, v)
    
    return np.sqrt(vBv / vv)


def main():
    """Main function to run spectral norm calculation"""
    # Get matrix size from command line argument, default to 100
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    # Calculate spectral norm
    result = spectral_norm(n)
    
    # Print result with 9 decimal places
    print(f"{result:.9f}")


if __name__ == "__main__":
    main()
