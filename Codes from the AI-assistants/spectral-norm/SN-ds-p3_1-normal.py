import sys
import math
from typing import List, Tuple

def A(i: int, j: int) -> float:
    """Compute infinite matrix element A(i,j) for Hilbert-like matrix.
    
    The matrix is defined with entries: a11=1, a12=1/2, a21=1/3, a13=1/4, 
    a22=1/5, a31=1/6, etc. This follows the pattern where elements are
    filled along anti-diagonals: (1,1), (1,2), (2,1), (1,3), (2,2), (3,1), ...
    """
    # Convert (i,j) to position in anti-diagonal filling
    # The element at position k in the sequence has i+j = k+1
    k = i + j - 1  # This gives us the anti-diagonal number
    # The position within the anti-diagonal: for fixed k, i goes from 1 to k
    # The index within the anti-diagonal is (i-1)
    # The sequence number for element (i,j) is: sum_{m=1}^{k-1} m + i
    seq_num = (k-1)*k//2 + i
    
    # The value is 1 / seq_num
    return 1.0 / seq_num


def mat_vec_mul(v: List[float], n: int) -> List[float]:
    """Compute A*v for the first n components.
    
    Args:
        v: Input vector of length n
        n: Dimension to consider
        
    Returns:
        Result vector A*v of length n
    """
    result = [0.0] * n
    
    for i in range(n):
        for j in range(n):
            result[i] += A(i+1, j+1) * v[j]
    
    return result


def mat_transpose_vec_mul(v: List[float], n: int) -> List[float]:
    """Compute Aᵀ*v for the first n components.
    
    Args:
        v: Input vector of length n
        n: Dimension to consider
        
    Returns:
        Result vector Aᵀ*v of length n
    """
    result = [0.0] * n
    
    for j in range(n):
        for i in range(n):
            result[j] += A(i+1, j+1) * v[i]
    
    return result


def at_mul_a_mul_v(v: List[float], n: int) -> List[float]:
    """Compute Aᵀ*(A*v) for the first n components.
    
    Args:
        v: Input vector of length n
        n: Dimension to consider
        
    Returns:
        Result vector Aᵀ*A*v of length n
    """
    # Compute A*v first
    av = mat_vec_mul(v, n)
    # Then compute Aᵀ*(A*v)
    return mat_transpose_vec_mul(av, n)


def spectral_norm(n: int) -> float:
    """Compute spectral norm of the n×n leading principal submatrix.
    
    Uses the power method to find the largest singular value.
    
    Args:
        n: Dimension of the matrix
        
    Returns:
        Spectral norm (largest singular value)
    """
    # Initialize vector u with ones
    u = [1.0] * n
    
    # Power iteration: u = Aᵀ*A*u / ||Aᵀ*A*u||
    for _ in range(10):  # Fixed number of iterations (converges quickly)
        # Compute v = Aᵀ*A*u
        v = at_mul_a_mul_v(u, n)
        
        # Compute norm of v
        v_norm = math.sqrt(sum(x*x for x in v))
        
        # Normalize u
        for i in range(n):
            u[i] = v[i] / v_norm
    
    # Final computation of the eigenvalue (Rayleigh quotient)
    v_final = at_mul_a_mul_v(u, n)
    eigenvalue = sum(u[i] * v_final[i] for i in range(n))
    
    # Return square root (since we computed Aᵀ*A's eigenvalue)
    return math.sqrt(eigenvalue)


def main():
    """Main function to compute spectral norm."""
    # Default value if no argument provided
    n = 5500
    
    # Read command-line argument if provided
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid argument '{sys.argv[1]}'. Using default n={n}")
    
    print(f"Computing spectral norm for n={n}")
    
    # Compute spectral norm
    norm = spectral_norm(n)
    
    print(f"Spectral norm: {norm:.9f}")
    return norm


if __name__ == "__main__":
    main()