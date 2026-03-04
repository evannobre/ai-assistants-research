import math
from itertools import count
from typing import Optional, Tuple
import sys

class InfiniteMatrix:
    """Represents the infinite matrix A with the given pattern."""
    
    def __init__(self):
        # Cache for computed entries to avoid recomputation
        self._cache = {}
        
    def get(self, i: int, j: int) -> float:
        """Get element A[i,j] (1-indexed)."""
        if i <= 0 or j <= 0:
            return 0.0
        
        key = (i, j)
        if key in self._cache:
            return self._cache[key]
        
        # Determine which anti-diagonal (k = i + j - 1)
        k = i + j - 1
        
        # Sum of numbers from 1 to (k-1) using formula: n(n+1)/2
        start_index = (k - 1) * k // 2
        
        # Position within the anti-diagonal (i determines the position)
        pos = i - 1  # 0-based position in the anti-diagonal
        
        # Denominator: start_index + pos + 1
        denominator = start_index + pos + 1
        
        value = 1.0 / denominator
        self._cache[key] = value
        return value
    
    def matvec(self, x: list) -> list:
        """
        Compute matrix-vector product A*x for the infinite matrix.
        Truncates to finite size based on length of x.
        """
        n = len(x)
        result = [0.0] * n
        
        for i in range(1, n + 1):
            total = 0.0
            for j in range(1, n + 1):
                total += self.get(i, j) * x[j - 1]
            result[i - 1] = total
        
        return result
    
    def matvec_transpose(self, x: list) -> list:
        """
        Compute A^T * x for the infinite matrix.
        """
        n = len(x)
        result = [0.0] * n
        
        for j in range(1, n + 1):
            total = 0.0
            for i in range(1, n + 1):
                total += self.get(i, j) * x[i - 1]
            result[j - 1] = total
        
        return result


def power_method(matrix: InfiniteMatrix, 
                 n: int = 1000,
                 max_iter: int = 1000,
                 tol: float = 1e-12,
                 verbose: bool = False) -> Tuple[float, list]:
    """
    Power method to estimate the spectral norm (largest singular value)
    of the infinite matrix.
    
    Args:
        matrix: InfiniteMatrix object
        n: Dimension for truncation
        max_iter: Maximum number of iterations
        tol: Convergence tolerance
        verbose: Print progress information
    
    Returns:
        Tuple of (estimated_spectral_norm, principal_singular_vector)
    """
    
    # Initialize random vector
    import random
    random.seed(42)  # For reproducibility
    
    # Start with random vector of norm 1
    v = [random.random() - 0.5 for _ in range(n)]
    norm_v = math.sqrt(sum(x * x for x in v))
    v = [x / norm_v for x in v]
    
    sigma_old = 0.0
    
    if verbose:
        print(f"Power Method: n={n}, max_iter={max_iter}, tol={tol}")
        print("Iteration\tSigma\t\tRelative Change")
        print("-" * 50)
    
    for iteration in range(1, max_iter + 1):
        # Compute u = A * v
        u = matrix.matvec(v)
        
        # Compute w = A^T * u
        w = matrix.matvec_transpose(u)
        
        # Compute sigma = ||w|| / ||u|| (Rayleigh quotient for A^T A)
        norm_w = math.sqrt(sum(x * x for x in w))
        norm_u = math.sqrt(sum(x * x for x in u))
        
        if norm_u == 0:
            sigma = 0.0
        else:
            sigma = norm_w / norm_u
        
        # Check convergence
        if iteration > 1:
            rel_change = abs(sigma - sigma_old) / abs(sigma_old) if sigma_old != 0 else float('inf')
            
            if verbose and iteration % 10 == 0:
                print(f"{iteration:4d}\t\t{sigma:.12f}\t{rel_change:.2e}")
            
            if rel_change < tol:
                if verbose:
                    print(f"Converged after {iteration} iterations")
                break
        
        sigma_old = sigma
        
        # Update v = w / ||w||
        if norm_w == 0:
            break
        
        v = [x / norm_w for x in w]
    
    return sigma, v


def validate_matrix_pattern():
    """Validate that we generate the correct matrix pattern."""
    matrix = InfiniteMatrix()
    
    print("First few elements of the infinite matrix:")
    print("A[1,1] =", matrix.get(1, 1))  # 1/1 = 1
    print("A[1,2] =", matrix.get(1, 2))  # 1/2
    print("A[2,1] =", matrix.get(2, 1))  # 1/3
    print("A[1,3] =", matrix.get(1, 3))  # 1/4
    print("A[2,2] =", matrix.get(2, 2))  # 1/5
    print("A[3,1] =", matrix.get(3, 1))  # 1/6
    print("A[1,4] =", matrix.get(1, 4))  # 1/7
    print("A[2,3] =", matrix.get(2, 3))  # 1/8
    print("A[3,2] =", matrix.get(3, 2))  # 1/9
    print("A[4,1] =", matrix.get(4, 1))  # 1/10


def convergence_study():
    """Study convergence with different truncation sizes."""
    matrix = InfiniteMatrix()
    
    print("\n" + "="*60)
    print("Convergence Study for Spectral Norm Estimation")
    print("="*60)
    
    sizes = [50, 100, 200, 400, 800, 1600]
    results = []
    
    for n in sizes:
        print(f"\nTruncation size n = {n}")
        sigma, _ = power_method(matrix, n=n, max_iter=200, tol=1e-12, verbose=False)
        results.append((n, sigma))
        print(f"  Estimated spectral norm: {sigma:.10f}")
    
    # Estimate limit by extrapolation
    if len(results) >= 3:
        # Simple Richardson extrapolation using last two points
        n1, s1 = results[-2]
        n2, s2 = results[-1]
        
        # Assuming error ~ 1/n^p, with p estimated from last two points
        # For demonstration, we'll just show the trend
        print(f"\nTrend suggests spectral norm approaches: {s2:.8f} ± {abs(s2-s1):.2e}")


def main():
    """Main function to run the spectral norm estimation."""
    # Validate the matrix pattern
    validate_matrix_pattern()
    
    # Run convergence study
    convergence_study()
    
    # Final accurate estimation
    print("\n" + "="*60)
    print("Final Accurate Estimation")
    print("="*60)
    
    matrix = InfiniteMatrix()
    n = 2000  # Large truncation for final estimate
    sigma, v = power_method(matrix, n=n, max_iter=500, tol=1e-14, verbose=True)
    
    print(f"\nFinal estimated spectral norm: {sigma:.15f}")
    print(f"Truncation size: {n}")
    
    # Also compute the Frobenius norm of the n×n submatrix for comparison
    frob_norm = 0.0
    for i in range(1, min(n, 100) + 1):  # Limit to 100 for performance
        for j in range(1, min(n, 100) + 1):
            val = matrix.get(i, j)
            frob_norm += val * val
    
    frob_norm = math.sqrt(frob_norm)
    print(f"Frobenius norm of {min(n, 100)}×{min(n, 100)} submatrix: {frob_norm:.10f}")
    
    # Theoretical bound: spectral norm ≤ Frobenius norm
    print(f"Spectral norm ≤ Frobenius norm: {sigma} ≤ {frob_norm}")


if __name__ == "__main__":
    main()