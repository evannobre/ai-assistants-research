import numpy as np
from scipy.sparse.linalg import LinearOperator
from scipy.sparse.linalg import svds

def create_matrix_operator(n):
    """
    Create a LinearOperator for the truncated n x n matrix.
    This allows using scipy's optimized linear algebra routines.
    """
    def matvec(x):
        """Compute A * x for the truncated matrix"""
        y = np.zeros_like(x)
        for i in range(n):
            for j in range(n):
                # Get matrix entry (1-indexed)
                entry = get_matrix_entry(i+1, j+1)
                y[i] += entry * x[j]
        return y
    
    def rmatvec(x):
        """Compute A^T * x for the truncated matrix"""
        y = np.zeros_like(x)
        for j in range(n):
            for i in range(n):
                # Get matrix entry (1-indexed)
                entry = get_matrix_entry(i+1, j+1)
                y[j] += entry * x[i]
        return y
    
    return LinearOperator((n, n), matvec=matvec, rmatvec=rmatvec)

def estimate_spectral_norm_scipy(max_n=500):
    """
    Use scipy's svds to estimate the largest singular value for increasing n.
    """
    norms = []
    
    for n in [50, 100, 200, 300, 400, 500]:
        if n > max_n:
            break
            
        A_op = create_matrix_operator(n)
        
        # Compute largest singular value using ARPACK
        # k=1 means compute only the largest singular value
        # which=’LM’ means largest magnitude
        U, s, Vt = svds(A_op, k=1, which='LM', tol=1e-6)
        
        norms.append((n, s[0]))
        print(f"n={n}: σ ≈ {s[0]:.10f}")
        
        # Check convergence
        if len(norms) > 1:
            rel_change = abs(norms[-1][1] - norms[-2][1]) / norms[-2][1]
            if rel_change < 1e-4:
                print(f"Converged at n={n}")
                break
    
    return norms[-1][1] if norms else None

# To run:
# spectral_norm = estimate_spectral_norm_scipy()
# print(f"Estimated spectral norm: {spectral_norm}")