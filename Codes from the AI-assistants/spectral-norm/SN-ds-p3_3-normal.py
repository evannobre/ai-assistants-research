import sys
import math
from typing import List

def A_fast(i: int, j: int) -> float:
    """Fast computation of matrix element."""
    k = i + j - 1
    seq_num = (k-1)*k//2 + i
    return 1.0 / seq_num

def mat_vec_mul_fast(v: List[float], n: int) -> List[float]:
    """Optimized A*v computation."""
    result = [0.0] * n
    
    # Pre-compute row sums for efficiency
    for i in range(n):
        i1 = i + 1
        row_sum = 0.0
        for j in range(n):
            j1 = j + 1
            k = i1 + j1 - 1
            seq_num = (k-1)*k//2 + i1
            row_sum += v[j] / seq_num
        result[i] = row_sum
    
    return result

def spectral_norm_power_method(n: int, iterations: int = 10) -> float:
    """Power method for spectral norm with convergence check."""
    # Initialize random vector
    import random
    u = [random.random() for _ in range(n)]
    
    # Normalize initial vector
    norm_u = math.sqrt(sum(x*x for x in u))
    u = [x/norm_u for x in u]
    
    for it in range(iterations):
        # Compute v = Aᵀ*A*u
        v = [0.0] * n
        
        # Direct computation of Aᵀ*A*u without intermediate storage
        for i in range(n):
            i1 = i + 1
            for j in range(n):
                j1 = j + 1
                # Compute (Aᵀ*A)[i,j] directly
                aij = 0.0
                for k in range(n):
                    k1 = k + 1
                    # A[i,k] * A[j,k]
                    aik = A_fast(i1, k1)
                    ajk = A_fast(j1, k1)
                    aij += aik * ajk
                v[i] += aij * u[j]
        
        # Compute norm
        norm_v = math.sqrt(sum(x*x for x in v))
        
        # Update u
        u = [x/norm_v for x in v]
        
        # Early convergence check (optional)
        if it > 0 and abs(norm_v - prev_norm) < 1e-12:
            break
            
        prev_norm = norm_v
    
    # Compute Rayleigh quotient
    v_final = [0.0] * n
    for i in range(n):
        i1 = i + 1
        for j in range(n):
            j1 = j + 1
            aij = 0.0
            for k in range(n):
                k1 = k + 1
                aik = A_fast(i1, k1)
                ajk = A_fast(j1, k1)
                aij += aik * ajk
            v_final[i] += aij * u[j]
    
    eigenvalue = sum(u[i] * v_final[i] for i in range(n))
    return math.sqrt(eigenvalue)

def main_fast():
    """Fast version main function."""
    n = 5500 if len(sys.argv) < 2 else int(sys.argv[1])
    print(f"Computing spectral norm for n={n} (fast version)")
    norm = spectral_norm_power_method(n, iterations=10)
    print(f"Spectral norm: {norm:.9f}")
    return norm

if __name__ == "__main__":
    main_fast()