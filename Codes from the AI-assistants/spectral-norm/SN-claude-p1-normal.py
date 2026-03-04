import numpy as np
from scipy.sparse.linalg import LinearOperator, svds

def hilbert_matvec(v, n):
    """
    Matrix-vector product for the Hilbert matrix H where H[i,j] = 1/(i+j+1)
    Entries: a11=1, a12=1/2, a21=1/3, a13=1/4, a22=1/5, a31=1/6, ...
    Following pattern: a_ij = 1/(i+j-1)
    """
    result = np.zeros(n)
    for i in range(n):
        for j in range(n):
            result[i] += v[j] / (i + j + 1)
    return result

def power_method_spectral_norm(n, max_iter=1000, tol=1e-10):
    """
    Compute spectral norm using Power Method for n×n truncation of infinite matrix.
    
    The spectral norm is the largest singular value, which equals the square root
    of the largest eigenvalue of A^T A.
    
    Parameters:
    -----------
    n : int
        Dimension of the truncated matrix
    max_iter : int
        Maximum number of iterations
    tol : float
        Convergence tolerance
        
    Returns:
    --------
    spectral_norm : float
        Estimated spectral norm (largest singular value)
    iterations : int
        Number of iterations performed
    """
    # Initialize random vector
    np.random.seed(42)
    v = np.random.randn(n)
    v = v / np.linalg.norm(v)
    
    eigenvalue = 0
    
    for iteration in range(max_iter):
        # Compute A^T * A * v efficiently
        # First compute A * v
        Av = hilbert_matvec(v, n)
        # Then compute A^T * (A * v)
        AtAv = hilbert_matvec(Av, n)
        
        # Compute eigenvalue (Rayleigh quotient)
        new_eigenvalue = np.dot(v, AtAv)
        
        # Normalize
        v = AtAv / np.linalg.norm(AtAv)
        
        # Check convergence
        if abs(new_eigenvalue - eigenvalue) < tol:
            eigenvalue = new_eigenvalue
            break
            
        eigenvalue = new_eigenvalue
    
    # Spectral norm is sqrt of largest eigenvalue of A^T A
    spectral_norm = np.sqrt(eigenvalue)
    
    return spectral_norm, iteration + 1

def power_method_with_linear_operator(n, max_iter=1000, tol=1e-10):
    """
    Alternative implementation using scipy's LinearOperator for efficiency.
    """
    def matvec(v):
        return hilbert_matvec(v, n)
    
    A = LinearOperator((n, n), matvec=matvec)
    
    # Initialize
    np.random.seed(42)
    v = np.random.randn(n)
    v = v / np.linalg.norm(v)
    
    eigenvalue = 0
    
    for iteration in range(max_iter):
        # A^T A v = A^T (A v)
        Av = A.matvec(v)
        AtAv = A.matvec(Av)  # Since A is symmetric, A^T = A
        
        new_eigenvalue = np.dot(v, AtAv)
        v = AtAv / np.linalg.norm(AtAv)
        
        if abs(new_eigenvalue - eigenvalue) < tol:
            eigenvalue = new_eigenvalue
            break
            
        eigenvalue = new_eigenvalue
    
    return np.sqrt(eigenvalue), iteration + 1

def verify_with_scipy(n):
    """
    Verify result using scipy's svds function.
    """
    # Create explicit Hilbert matrix
    H = np.array([[1/(i+j+1) for j in range(n)] for i in range(n)])
    
    # Compute largest singular value
    try:
        # svds requires k < min(m,n), so for small n use full SVD
        if n < 3:
            U, s, Vt = np.linalg.svd(H)
            return s[0]
        else:
            s = svds(H, k=1, return_singular_vectors=False)
            return s[0]
    except:
        # Fallback to full SVD
        U, s, Vt = np.linalg.svd(H)
        return s[0]

# Example usage
if __name__ == "__main__":
    print("Spectral Norm Estimation for Hilbert Matrix")
    print("=" * 60)
    
    dimensions = [5, 10, 20, 50, 100]
    
    for n in dimensions:
        # Power method
        spectral_norm, iters = power_method_spectral_norm(n, max_iter=1000)
        
        # Verification
        scipy_norm = verify_with_scipy(n)
        
        # Error
        error = abs(spectral_norm - scipy_norm)
        rel_error = error / scipy_norm * 100
        
        print(f"\nDimension n = {n}")
        print(f"  Power Method:    {spectral_norm:.10f} ({iters} iterations)")
        print(f"  SciPy SVD:       {scipy_norm:.10f}")
        print(f"  Relative Error:  {rel_error:.2e}%")
    
    # Demonstrate convergence for a specific case
    print("\n" + "=" * 60)
    print("Convergence Analysis for n = 20")
    print("=" * 60)
    
    n = 20
    np.random.seed(42)
    v = np.random.randn(n)
    v = v / np.linalg.norm(v)
    
    eigenvalue = 0
    print(f"{'Iter':<6} {'Spectral Norm':<20} {'Change':<15}")
    print("-" * 45)
    
    for iteration in range(50):
        Av = hilbert_matvec(v, n)
        AtAv = hilbert_matvec(Av, n)
        new_eigenvalue = np.dot(v, AtAv)
        v = AtAv / np.linalg.norm(AtAv)
        
        spectral_norm = np.sqrt(new_eigenvalue)
        change = abs(new_eigenvalue - eigenvalue)
        
        if iteration % 5 == 0:
            print(f"{iteration:<6} {spectral_norm:<20.12f} {change:<15.2e}")
        
        if change < 1e-10:
            print(f"{iteration:<6} {spectral_norm:<20.12f} {change:<15.2e} (Converged)")
            break
            
        eigenvalue = new_eigenvalue