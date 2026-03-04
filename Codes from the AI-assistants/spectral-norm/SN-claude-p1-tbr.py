import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import LinearOperator, svds

def get_matrix_entry(i, j):
    """
    Compute entry a_ij of the infinite matrix.
    Entries are filled along anti-diagonals: a11=1, a12=1/2, a21=1/3, etc.
    The k-th value (k=1,2,3,...) appears at position where i+j-1=k in some ordering.
    """
    # Anti-diagonal index: positions (1,1), (1,2), (2,1), (1,3), (2,2), (3,1), ...
    # correspond to k = 1, 2, 3, 4, 5, 6, ...
    # For position (i,j), we need to find which k it corresponds to
    diagonal = i + j - 1  # Which anti-diagonal (1-indexed)
    # Number of entries before this diagonal: 1+2+...+(diagonal-1) = diagonal*(diagonal-1)/2
    position_in_diagonal = i  # Position within the anti-diagonal
    k = diagonal * (diagonal - 1) // 2 + position_in_diagonal
    return 1.0 / k

def create_finite_approximation(n):
    """Create an n×n approximation of the infinite matrix."""
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            A[i, j] = get_matrix_entry(i + 1, j + 1)  # Convert to 1-indexed
    return A

def power_method_spectral_norm(A, max_iter=1000, tol=1e-10):
    """
    Compute spectral norm using Power Method on A^T A.
    Spectral norm of A = sqrt(largest eigenvalue of A^T A)
    """
    n = A.shape[0]
    # Start with random vector
    v = np.random.rand(n)
    v = v / np.linalg.norm(v)
    
    # Compute A^T A
    AtA = A.T @ A
    
    for iteration in range(max_iter):
        v_old = v.copy()
        
        # Power iteration: v = (A^T A) v
        v = AtA @ v
        
        # Compute eigenvalue estimate (Rayleigh quotient)
        eigenvalue = v @ v_old
        
        # Normalize
        v = v / np.linalg.norm(v)
        
        # Check convergence
        if np.linalg.norm(v - v_old) < tol:
            print(f"Converged in {iteration + 1} iterations")
            break
    
    # Final eigenvalue estimate
    eigenvalue = v @ (AtA @ v)
    spectral_norm = np.sqrt(eigenvalue)
    
    return spectral_norm, v

def power_method_direct(A, max_iter=1000, tol=1e-10):
    """
    Alternative: Compute largest singular value directly using power method on A.
    This computes the spectral norm by iterating v = A^T A v.
    """
    n = A.shape[1]
    v = np.random.rand(n)
    v = v / np.linalg.norm(v)
    
    for iteration in range(max_iter):
        # Apply A
        u = A @ v
        sigma_old = np.linalg.norm(u)
        
        # Apply A^T
        v_new = A.T @ u
        v_new = v_new / np.linalg.norm(v_new)
        
        # Check convergence
        if np.linalg.norm(v_new - v) < tol:
            print(f"Converged in {iteration + 1} iterations")
            v = v_new
            break
        
        v = v_new
    
    # Compute final singular value
    spectral_norm = np.linalg.norm(A @ v)
    
    return spectral_norm, v

# Main execution
if __name__ == "__main__":
    # Test with increasing matrix sizes
    sizes = [10, 20, 50, 100, 200]
    
    print("Spectral Norm Approximation using Power Method")
    print("=" * 60)
    
    for n in sizes:
        print(f"\nMatrix size: {n}×{n}")
        A = create_finite_approximation(n)
        
        # Method 1: Power method on A^T A
        spectral_norm_1, _ = power_method_spectral_norm(A)
        print(f"  Power Method (A^T A): {spectral_norm_1:.10f}")
        
        # Method 2: Direct power method
        spectral_norm_2, _ = power_method_direct(A)
        print(f"  Power Method (direct): {spectral_norm_2:.10f}")
        
        # Verification using NumPy's SVD
        singular_values = np.linalg.svd(A, compute_uv=False)
        spectral_norm_exact = singular_values[0]
        print(f"  NumPy SVD (exact):     {spectral_norm_exact:.10f}")
        
        # Error
        error = abs(spectral_norm_2 - spectral_norm_exact)
        print(f"  Error: {error:.2e}")
    
    print("\n" + "=" * 60)
    print("Note: As matrix size increases, the approximation converges")
    print("to the true spectral norm of the infinite matrix.")
