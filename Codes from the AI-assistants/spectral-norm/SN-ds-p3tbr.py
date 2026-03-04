import sys
import math
from typing import List, Callable

def A(i: int, j: int) -> float:
    """Computes the infinite matrix element A(i, j) = 1/(i+j-1)"""
    return 1.0 / (i + j - 1)

def multiply_A(v: List[float]) -> List[float]:
    """Computes A*v for the Hilbert matrix"""
    n = len(v)
    result = [0.0] * n
    
    for i in range(1, n + 1):
        total = 0.0
        # Sum over j: A(i, j) * v[j-1]
        # A(i, j) = 1/(i+j-1)
        for j in range(1, n + 1):
            total += v[j-1] / (i + j - 1)
        result[i-1] = total
    return result

def multiply_At(v: List[float]) -> List[float]:
    """Computes Aᵀ*v for the Hilbert matrix (symmetric, so same as A*v)"""
    # The Hilbert matrix is symmetric: A(i, j) = A(j, i)
    # So Aᵀ = A, and Aᵀ*v = A*v
    return multiply_A(v)

def multiply_AtA(v: List[float]) -> List[float]:
    """Computes Aᵀ*(A*v)"""
    # First compute w = A*v
    w = multiply_A(v)
    # Then compute Aᵀ*w = A*w (since A is symmetric)
    return multiply_A(w)

def spectral_norm(n: int, iterations: int = 10) -> float:
    """
    Computes the spectral norm using the power method.
    
    The spectral norm is the largest singular value of A, which is
    the square root of the largest eigenvalue of AᵀA.
    """
    # Initialize vector v with ones
    v = [1.0] * n
    
    # Normalize initial vector
    norm_v = math.sqrt(sum(x * x for x in v))
    v = [x / norm_v for x in v]
    
    # Power iteration: v = (AᵀA * v) / ||AᵀA * v||
    for _ in range(iterations):
        v = multiply_AtA(v)
        norm_v = math.sqrt(sum(x * x for x in v))
        v = [x / norm_v for x in v]
    
    # Compute Rayleigh quotient for AᵀA: (v·AᵀAv)/(v·v)
    # Since v is normalized, v·v = 1
    Av = multiply_A(v)
    AtAv = multiply_A(Av)  # Aᵀ(Av) = A(Av) since symmetric
    rayleigh = sum(v[i] * AtAv[i] for i in range(n))
    
    # Spectral norm = sqrt(largest eigenvalue of AᵀA)
    return math.sqrt(rayleigh)

def main():
    # Use command-line argument or default to 5500
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Invalid argument: {sys.argv[1]}. Using default n=5500.")
            n = 5500
    else:
        n = 5500
    
    # Compute spectral norm
    result = spectral_norm(n)
    
    # Print with 9 decimal places as in typical benchmarks
    print(f"{result:.9f}")

if __name__ == "__main__":
    main()