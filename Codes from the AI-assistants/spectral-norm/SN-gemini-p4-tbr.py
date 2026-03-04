import sys
from math import sqrt
from typing import List

# ==============================================================================
#  Algorithm: Spectral Norm (Power Method on Hilbert Matrix)
# ==============================================================================

def eval_A(i: int, j: int) -> float:
    """
    (i) Computes the infinite matrix element A(i, j).
    Formula: A_ij = 1 / ((i + j) * (i + j + 1) / 2 + i + 1)
    """
    return 1.0 / ((i + j) * (i + j + 1) / 2 + i + 1)

def eval_A_times_v(v: List[float]) -> List[float]:
    """
    (ii) Computes A * v.
    Multiplies matrix A by vector v.
    """
    n = len(v)
    result = [0.0] * n
    for i in range(n):
        partial_sum = 0.0
        for j in range(n):
            partial_sum += eval_A(i, j) * v[j]
        result[i] = partial_sum
    return result

def eval_At_times_v(v: List[float]) -> List[float]:
    """
    (iii) Computes A_transpose * v.
    Multiplies matrix A_transpose by vector v.
    Note: A_transpose[i][j] is A[j][i].
    """
    n = len(v)
    result = [0.0] * n
    for i in range(n):
        partial_sum = 0.0
        for j in range(n):
            # We swap i and j here to simulate the transpose
            partial_sum += eval_A(j, i) * v[j]
        result[i] = partial_sum
    return result

def eval_AtA_times_v(v: List[float]) -> List[float]:
    """
    (iv) Computes A_transpose * (A * v).
    This represents the linear operator B = A^T * A.
    """
    # First compute u = A * v
    u = eval_A_times_v(v)
    # Then compute w = A^T * u
    w = eval_At_times_v(u)
    return w

def main():
    """
    Main execution driver.
    """
    # Parse command line argument or default to 100 for testing
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    # Initialize vector u with 1.0
    u = [1.0] * n
    v = [0.0] * n
    
    # Run the Power Method for 10 iterations
    # In each step, we apply the operator A^T * A
    for _ in range(10):
        v = eval_AtA_times_v(u)
        u = eval_AtA_times_v(v)
        
    # Final calculation of the spectral norm
    # Rayleigh quotient approximation: sqrt( (u . v) / (v . v) )
    vBv = 0.0
    vv = 0.0
    for i in range(n):
        vBv += u[i] * v[i]
        vv += v[i] * v[i]
        
    result = sqrt(vBv / vv)
    
    # Print result formatted to 9 decimal places
    print(f"{result:.9f}")

if __name__ == "__main__":
    main()