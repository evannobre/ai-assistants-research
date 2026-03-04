import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import LinearOperator
import warnings
warnings.filterwarnings('ignore')

class InfiniteHilbertOperator(LinearOperator):
    """
    Linear operator representing the infinite Hilbert matrix A where a_ij = 1/(i+j-1)
    This allows us to work with the infinite matrix without storing it explicitly.
    """
    
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.dtype = np.float64
        self.shape = (max_size, max_size)
    
    def _matvec(self, x):
        """Matrix-vector multiplication A @ x"""
        result = np.zeros_like(x)
        n = len(x)
        
        for i in range(n):
            for j in range(n):
                if x[j] != 0:  # Skip zero entries for efficiency
                    result[i] += x[j] / (i + j + 1)  # +1 because arrays are 0-indexed
        
        return result
    
    def _rmatvec(self, x):
        """Matrix-vector multiplication A.T @ x"""
        # Since Hilbert matrix is symmetric, A.T = A
        return self._matvec(x)

def power_method_spectral_norm(A, max_iter=1000, tol=1e-10, verbose=True):
    """
    Compute the spectral norm (largest singular value) of matrix A using Power Method.
    
    The spectral norm is the largest singular value, which equals the square root
    of the largest eigenvalue of A^T @ A.
    
    Parameters:
    -----------
    A : LinearOperator
        The matrix operator
    max_iter : int
        Maximum number of iterations
    tol : float
        Convergence tolerance
    verbose : bool
        Print convergence information
    
    Returns:
    --------
    float : The spectral norm (largest singular value)
    """
    
    n = A.shape[1]
    
    # Initialize with random vector
    np.random.seed(42)  # For reproducibility
    x = np.random.randn(n)
    x = x / np.linalg.norm(x)  # Normalize
    
    # Power iteration for A^T @ A
    # We compute (A^T @ A) @ x = A^T @ (A @ x)
    
    eigenvalue_old = 0
    
    if verbose:
        print(f"{'Iteration':<10} {'Eigenvalue':<15} {'Convergence':<15}")
        print("-" * 45)
    
    for i in range(max_iter):
        # Compute A @ x
        Ax = A @ x
        
        # Compute A^T @ (A @ x) = (A^T @ A) @ x
        ATAx = A.T @ Ax
        
        # Compute Rayleigh quotient: x^T @ (A^T @ A) @ x
        eigenvalue = np.dot(x, ATAx)
        
        # Normalize for next iteration
        x = ATAx / np.linalg.norm(ATAx)
        
        # Check convergence
        convergence = abs(eigenvalue - eigenvalue_old)
        
        if verbose and (i % 10 == 0 or i < 10):
            print(f"{i:<10} {eigenvalue:<15.10f} {convergence:<15.2e}")
        
        if convergence < tol:
            if verbose:
                print(f"\nConverged after {i+1} iterations")
            break
            
        eigenvalue_old = eigenvalue
    
    # The spectral norm is the square root of the largest eigenvalue of A^T @ A
    spectral_norm = np.sqrt(eigenvalue)
    
    return spectral_norm, eigenvalue, i+1

def create_finite_hilbert_matrix(n):
    """Create a finite n×n Hilbert matrix for comparison"""
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            H[i, j] = 1.0 / (i + j + 1)
    return H

def main():
    print("Spectral Norm Computation of Infinite Hilbert Matrix")
    print("=" * 55)
    
    # Test with different matrix sizes
    sizes = [50, 100, 200, 500]
    
    for n in sizes:
        print(f"\nMatrix size: {n}×{n}")
        print("-" * 30)
        
        # Create the infinite Hilbert operator
        A = InfiniteHilbertOperator(max_size=n)
        
        # Compute spectral norm using Power Method
        spectral_norm, largest_eigenvalue, iterations = power_method_spectral_norm(
            A, max_iter=1000, tol=1e-10, verbose=False
        )
        
        print(f"Spectral norm (Power Method): {spectral_norm:.10f}")
        print(f"Largest eigenvalue of A^T@A:   {largest_eigenvalue:.10f}")
        print(f"Iterations to converge:       {iterations}")
        
        # Compare with finite Hilbert matrix using NumPy
        if n <= 200:  # Only for smaller matrices due to computational cost
            H_finite = create_finite_hilbert_matrix(n)
            
            # Compute spectral norm using SVD
            singular_values = np.linalg.svd(H_finite, compute_uv=False)
            spectral_norm_exact = singular_values[0]
            
            print(f"Spectral norm (NumPy SVD):    {spectral_norm_exact:.10f}")
            print(f"Relative error:               {abs(spectral_norm - spectral_norm_exact)/spectral_norm_exact:.2e}")
    
    # Detailed run for visualization
    print("\n" + "=" * 55)
    print("Detailed Power Method Convergence (n=100)")
    print("=" * 55)
    
    A = InfiniteHilbertOperator(max_size=100)
    spectral_norm, _, _ = power_method_spectral_norm(A, max_iter=100, tol=1e-12, verbose=True)
    
    print(f"\nFinal spectral norm estimate: {spectral_norm:.12f}")
    
    # Theoretical note
    print("\n" + "=" * 55)
    print("THEORETICAL NOTES:")
    print("=" * 55)
    print("The Hilbert matrix H with entries h_ij = 1/(i+j-1) is:")
    print("- Symmetric and positive definite")
    print("- Notoriously ill-conditioned (condition number grows exponentially)")
    print("- The spectral norm equals the largest singular value")
    print("- For infinite Hilbert matrix, the spectral norm approaches π")
    print("- The convergence rate depends on the spectral gap")

if __name__ == "__main__":
    main()