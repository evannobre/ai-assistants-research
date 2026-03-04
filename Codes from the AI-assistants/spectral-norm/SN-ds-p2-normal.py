import numpy as np
import sys
import time
from math import sqrt
from typing import Tuple

class HilbertInfiniteMatrix:
    """
    Represents the infinite matrix A with entries:
    a11=1, a12=1/2, a21=1/3, a13=1/4, a22=1/5, a31=1/6, etc.
    
    The matrix is stored implicitly - we compute matrix-vector products on the fly.
    """
    
    def __init__(self, max_iterations: int = 1000, tolerance: float = 1e-10):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
    def get_denominator(self, i: int, j: int) -> int:
        """
        Get the denominator for element (i, j) using the anti-diagonal pattern.
        
        The pattern: elements are filled along anti-diagonals:
        Anti-diagonal 1: (1,1) -> denominator 1
        Anti-diagonal 2: (1,2), (2,1) -> denominators 2, 3
        Anti-diagonal 3: (1,3), (2,2), (3,1) -> denominators 4, 5, 6
        etc.
        
        For position (i,j) on anti-diagonal k = i + j - 1
        Position within anti-diagonal: p = i - 1
        Starting denominator for anti-diagonal k: 1 + sum_{m=1}^{k-1} m = 1 + k(k-1)/2
        So denominator = 1 + k(k-1)/2 + (i-1)
        """
        k = i + j - 1  # anti-diagonal number (1-indexed)
        # Starting denominator for this anti-diagonal
        start_denom = 1 + k * (k - 1) // 2
        # Position within anti-diagonal (0-indexed)
        pos = i - 1
        return start_denom + pos
    
    def matvec(self, x: np.ndarray, n: int) -> np.ndarray:
        """
        Compute y = A_n * x where A_n is the n×n leading principal submatrix.
        
        Args:
            x: Vector of length n
            n: Dimension of the submatrix to consider
            
        Returns:
            y: Result of matrix-vector multiplication
        """
        y = np.zeros_like(x)
        
        # Pre-compute denominators for efficiency
        # We'll compute in blocks to leverage vectorization
        for i in range(1, n + 1):
            # Compute all denominators for row i
            j_indices = np.arange(1, n + 1)
            denominators = np.zeros(n, dtype=np.float64)
            
            for idx, j in enumerate(j_indices):
                denominators[idx] = self.get_denominator(i, j)
            
            # Vectorized computation for this row
            y[i-1] = np.sum(x / denominators)
        
        return y
    
    def matvec_transpose(self, x: np.ndarray, n: int) -> np.ndarray:
        """
        Compute y = A_n^T * x.
        Since the matrix is symmetric in pattern? Let's verify...
        Actually, let's compute the transpose explicitly.
        """
        y = np.zeros_like(x)
        
        # For transpose, we need to access elements as if swapping i and j
        # But our denominator function depends on both i and j
        # So we compute column by column instead of row by row
        
        for j in range(1, n + 1):
            i_indices = np.arange(1, n + 1)
            denominators = np.zeros(n, dtype=np.float64)
            
            for idx, i in enumerate(i_indices):
                denominators[idx] = self.get_denominator(i, j)
            
            # For A^T * x, we sum over i: y[j-1] = Σ_i x[i-1] / denominator(i,j)
            y[j-1] = np.sum(x / denominators)
        
        return y
    
    def power_iteration(self, n: int) -> Tuple[float, np.ndarray, int]:
        """
        Perform power iteration to find the largest singular value (spectral norm)
        of the n×n leading principal submatrix.
        
        Returns:
            sigma: Estimated spectral norm
            v: Right singular vector
            iterations: Number of iterations performed
        """
        # Initialize random vector
        np.random.seed(42)  # For reproducibility
        v = np.random.randn(n)
        v = v / np.linalg.norm(v)
        
        sigma_old = 0.0
        
        for iteration in range(self.max_iterations):
            # Compute u = A * v
            u = self.matvec(v, n)
            
            # Normalize u
            u_norm = np.linalg.norm(u)
            if u_norm < 1e-15:
                # Handle zero vector case
                u = np.random.randn(n)
                u = u / np.linalg.norm(u)
            else:
                u = u / u_norm
            
            # Compute v = A^T * u
            v_new = self.matvec_transpose(u, n)
            
            # Normalize v_new
            v_new_norm = np.linalg.norm(v_new)
            if v_new_norm < 1e-15:
                v_new = np.random.randn(n)
                v_new = v_new / np.linalg.norm(v_new)
            else:
                v_new = v_new / v_new_norm
            
            # Estimate singular value: sigma = ||A * v||
            sigma = np.linalg.norm(self.matvec(v_new, n))
            
            # Check convergence
            if abs(sigma - sigma_old) < self.tolerance * sigma:
                v = v_new
                return sigma, v, iteration + 1
            
            sigma_old = sigma
            v = v_new
        
        print(f"Warning: Power iteration did not converge in {self.max_iterations} iterations")
        return sigma, v, self.max_iterations
    
    def spectral_norm_estimation(self, max_n: int = 1000) -> dict:
        """
        Estimate spectral norm for increasing matrix sizes to observe convergence.
        
        Args:
            max_n: Maximum dimension to consider
            
        Returns:
            Dictionary with results
        """
        results = {
            'dimensions': [],
            'spectral_norms': [],
            'iterations': [],
            'times': []
        }
        
        # Start with small n and increase
        for n in [10, 20, 50, 100, 200, 500, 1000]:
            if n > max_n:
                break
            
            print(f"\nComputing spectral norm for n = {n}...")
            start_time = time.time()
            
            sigma, v, iterations = self.power_iteration(n)
            
            elapsed = time.time() - start_time
            
            results['dimensions'].append(n)
            results['spectral_norms'].append(sigma)
            results['iterations'].append(iterations)
            results['times'].append(elapsed)
            
            print(f"  Spectral norm: {sigma:.10f}")
            print(f"  Iterations: {iterations}")
            print(f"  Time: {elapsed:.4f} seconds")
            
            # Memory check
            memory_used = (n * 8 * 2) / (1024 ** 2)  # Two vectors of doubles in MB
            if memory_used > 100:  # Alert if using more than 100MB
                print(f"  Warning: Using {memory_used:.2f} MB for n={n}")
        
        return results
    
    def verify_symmetry(self, n: int = 10) -> bool:
        """
        Verify if the matrix is symmetric (which would simplify calculations).
        
        Returns:
            True if symmetric, False otherwise
        """
        print(f"\nVerifying symmetry for n={n}...")
        
        # Compute a few sample elements and their transposes
        test_pairs = [(1, 2), (2, 3), (3, 1), (4, 2)]
        
        for i, j in test_pairs:
            if i <= n and j <= n:
                a_ij = 1.0 / self.get_denominator(i, j)
                a_ji = 1.0 / self.get_denominator(j, i)
                print(f"  A({i},{j}) = {a_ij:.6f}, A({j},{i}) = {a_ji:.6f}, "
                      f"Difference: {abs(a_ij - a_ji):.2e}")
        
        # Check if it's symmetric
        is_symmetric = True
        for i in range(1, min(5, n) + 1):
            for j in range(1, min(5, n) + 1):
                a_ij = 1.0 / self.get_denominator(i, j)
                a_ji = 1.0 / self.get_denominator(j, i)
                if abs(a_ij - a_ji) > 1e-12:
                    is_symmetric = False
        
        print(f"  Matrix is {'symmetric' if is_symmetric else 'not symmetric'}")
        return is_symmetric


def main():
    """
    Main function to compute spectral norm of the infinite matrix.
    """
    print("=" * 60)
    print("Spectral Norm Computation of Infinite Matrix A")
    print("Matrix pattern: a11=1, a12=1/2, a21=1/3, a13=1/4, a22=1/5, a31=1/6, ...")
    print("=" * 60)
    
    # Initialize matrix operator
    matrix = HilbertInfiniteMatrix(
        max_iterations=2000,
        tolerance=1e-12
    )
    
    # Verify symmetry property
    is_symmetric = matrix.verify_symmetry(n=10)
    
    if is_symmetric:
        print("\nNote: Matrix is symmetric, so spectral norm equals largest eigenvalue.")
        print("We can use simplified power iteration for symmetric matrices.")
    
    # Estimate spectral norm for increasing dimensions
    print("\n" + "=" * 60)
    print("Spectral Norm Estimation for Increasing Matrix Sizes")
    print("=" * 60)
    
    results = matrix.spectral_norm_estimation(max_n=2000)
    
    # Display summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for i, n in enumerate(results['dimensions']):
        sigma = results['spectral_norms'][i]
        iterations = results['iterations'][i]
        t = results['times'][i]
        print(f"n={n:4d}: σ={sigma:.8f}, iterations={iterations:3d}, time={t:.3f}s")
    
    # Extrapolate to infinite matrix
    if len(results['dimensions']) >= 3:
        # Simple extrapolation using last two values
        n1 = results['dimensions'][-2]
        n2 = results['dimensions'][-1]
        sigma1 = results['spectral_norms'][-2]
        sigma2 = results['spectral_norms'][-1]
        
        # Assuming convergence like σ(n) = σ(∞) + C/n
        # σ(∞) ≈ (n2*σ2 - n1*σ1) / (n2 - n1)
        sigma_inf = (n2 * sigma2 - n1 * sigma1) / (n2 - n1)
        
        print(f"\nExtrapolated spectral norm for infinite matrix: {sigma_inf:.10f}")
    
    # Memory usage report
    print("\n" + "=" * 60)
    print("MEMORY USAGE ESTIMATE")
    print("=" * 60)
    print(f"System RAM: 8 GB")
    print(f"SSD: 256 GB")
    print("\nMemory usage for different matrix sizes (vectors only):")
    
    for n in [100, 500, 1000, 2000, 5000]:
        # Memory for two vectors of doubles
        memory_mb = (n * 8 * 2) / (1024 ** 2)
        print(f"  n={n:5d}: {memory_mb:6.2f} MB")
    
    print("\nNote: Full matrix is never stored. Only O(n) memory used.")
    
    return results


if __name__ == "__main__":
    # Set numpy to use single thread for more predictable performance
    # and to avoid memory issues
    import os
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    
    try:
        results = main()
    except MemoryError:
        print("\nERROR: Memory allocation failed!")
        print("Try reducing the maximum dimension.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nComputation interrupted by user.")
        sys.exit(0)