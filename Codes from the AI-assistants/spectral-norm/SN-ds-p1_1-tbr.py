import numpy as np
import time
from math import isclose

def get_matrix_entry(i, j):
    """
    Get the entry A[i,j] for the infinite matrix where indices start at 1.
    The pattern fills by anti-diagonals: 
    (1,1)=1/1, (1,2)=1/2, (2,1)=1/3, (1,3)=1/4, (2,2)=1/5, (3,1)=1/6, ...
    
    Returns: A[i,j] = 1/k where k is determined by anti-diagonal ordering
    """
    # i and j are 1-indexed
    # Anti-diagonal number d = i + j - 1
    d = i + j - 1
    
    # Number of entries in anti-diagonals 1 through (d-1)
    # This is triangular number T(d-1) = (d-1)*d/2
    entries_before = (d - 1) * d // 2
    
    # Position within current anti-diagonal (starting from top)
    position_within = i
    
    # Global index k
    k = entries_before + position_within
    
    return 1.0 / k

def matrix_vector_product(x, max_row=None, max_col=None):
    """
    Compute y = A * x for the infinite matrix A.
    Since A is infinite, we truncate computation when entries become negligible.
    
    Args:
        x: Input vector (assumed infinite, but we use its computed length)
        max_row: Maximum row to compute (None for adaptive)
        max_col: Maximum column to compute (None for adaptive)
    
    Returns:
        y: Result vector
    """
    n = len(x)
    
    # Adaptive truncation based on matrix entry magnitude
    if max_row is None or max_col is None:
        # Determine reasonable truncation
        # Since entries decay as O(1/k) ~ O(1/(i+j)^2), we can truncate
        # when entries become smaller than machine epsilon relative to largest entry
        max_dim = min(2 * n, 10000)  # Reasonable upper bound
    else:
        max_dim = min(max_row, max_col, 2 * n, 10000)
    
    y = np.zeros(n)
    
    # Compute matrix-vector product with adaptive truncation
    for i in range(1, min(max_dim, n) + 1):
        row_sum = 0.0
        # We can truncate columns when entries become negligible
        for j in range(1, min(max_dim, n) + 1):
            entry = get_matrix_entry(i, j)
            # Early termination if entry is negligible
            if abs(entry * x[j-1]) < 1e-16 * abs(row_sum) and j > i + 10:
                break
            row_sum += entry * x[j-1]
        y[i-1] = row_sum
    
    return y

def transpose_matrix_vector_product(y, max_row=None, max_col=None):
    """
    Compute x = A^T * y for the infinite matrix A.
    This is equivalent to A^T * y = (y^T * A)^T
    """
    n = len(y)
    
    if max_row is None or max_col is None:
        max_dim = min(2 * n, 10000)
    else:
        max_dim = min(max_row, max_col, 2 * n, 10000)
    
    x = np.zeros(n)
    
    for j in range(1, min(max_dim, n) + 1):
        col_sum = 0.0
        for i in range(1, min(max_dim, n) + 1):
            entry = get_matrix_entry(i, j)  # A[i,j]
            # Early termination
            if abs(entry * y[i-1]) < 1e-16 * abs(col_sum) and i > j + 10:
                break
            col_sum += entry * y[i-1]
        x[j-1] = col_sum
    
    return x

def spectral_norm_power_method(max_iter=100, tol=1e-10, initial_size=100):
    """
    Power method to estimate the spectral norm (largest singular value) of infinite matrix A.
    
    The power method for A^T A: 
    Start with random vector b0
    For k = 0, 1, 2, ...
        bk+1 = A^T A bk / ||A^T A bk||
        σ^2 ≈ ||A^T A bk||
    
    Returns: Estimated spectral norm σ
    """
    # Start with reasonable vector size
    n = initial_size
    b = np.random.randn(n)
    b = b / np.linalg.norm(b)
    
    # Track convergence
    sigma_sq_old = 0
    converged = False
    
    print(f"{'Iter':<6} {'Size':<8} {'σ':<15} {'Change':<15}")
    print("-" * 50)
    
    for iteration in range(max_iter):
        # Compute A * b
        Ab = matrix_vector_product(b)
        
        # Compute A^T * (A * b)
        ATAb = transpose_matrix_vector_product(Ab)
        
        # Current Rayleigh quotient approximation for largest eigenvalue of A^T A
        sigma_sq = np.linalg.norm(ATAb)
        
        # Update vector
        b = ATAb / sigma_sq
        
        # Check convergence
        change = abs(sigma_sq - sigma_sq_old)
        sigma = np.sqrt(sigma_sq)
        
        print(f"{iteration:<6} {n:<8} {sigma:<15.10f} {change:<15.10f}")
        
        if change < tol:
            converged = True
            break
        
        sigma_sq_old = sigma_sq
        
        # Adaptively increase vector size if needed
        # Check if we're losing significant components at the tail
        if iteration % 5 == 0 and n < 10000:
            tail_magnitude = np.linalg.norm(b[-min(10, n//10):])
            if tail_magnitude > 0.01 * np.linalg.norm(b):
                # Increase size by 50% (but cap)
                new_n = min(int(n * 1.5), 10000)
                if new_n > n:
                    # Extend vector with small random components
                    b_extended = np.zeros(new_n)
                    b_extended[:n] = b
                    b_extended[n:] = np.random.randn(new_n - n) * 0.01
                    b = b_extended / np.linalg.norm(b_extended)
                    n = new_n
    
    sigma = np.sqrt(sigma_sq)
    
    if converged:
        print(f"\nConverged after {iteration} iterations")
        print(f"Estimated spectral norm: {sigma}")
    else:
        print(f"\nStopped after {max_iter} iterations (did not converge)")
        print(f"Current estimate: {sigma}")
    
    return sigma

def verify_small_matrix():
    """Verify the pattern for a small matrix"""
    print("Small matrix verification (4x4):")
    print("Matrix entries A[i,j]:")
    for i in range(1, 5):
        row = []
        for j in range(1, 5):
            row.append(f"{get_matrix_entry(i, j):.4f}")
        print(f"Row {i}: {row}")
    
    # Check pattern matches description
    expected = [
        [1/1, 1/2, 1/4, 1/7],
        [1/3, 1/5, 1/8, 1/11],
        [1/6, 1/9, 1/12, 1/16],
        [1/10, 1/13, 1/17, 1/21]
    ]
    
    print("\nExpected pattern by anti-diagonals:")
    print("Anti-diagonal 1: (1,1)=1")
    print("Anti-diagonal 2: (1,2)=1/2, (2,1)=1/3")
    print("Anti-diagonal 3: (1,3)=1/4, (2,2)=1/5, (3,1)=1/6")
    print("Anti-diagonal 4: (1,4)=1/7, (2,3)=1/8, (3,2)=1/9, (4,1)=1/10")

def main():
    """Main function to run the spectral norm estimation"""
    print("=" * 60)
    print("Spectral Norm Estimation of Infinite Matrix A")
    print("Pattern: a11=1, a12=1/2, a21=1/3, a13=1/4, a22=1/5, a31=1/6, ...")
    print("=" * 60)
    
    # Verify the pattern
    verify_small_matrix()
    
    print("\n" + "=" * 60)
    print("Running Power Method for Spectral Norm Estimation")
    print("=" * 60)
    
    # Run power method
    start_time = time.time()
    spectral_norm = spectral_norm_power_method(
        max_iter=50, 
        tol=1e-12,
        initial_size=200
    )
    end_time = time.time()
    
    print(f"\nTotal time: {end_time - start_time:.2f} seconds")
    
    # Additional analysis
    print("\n" + "=" * 60)
    print("Additional Analysis")
    print("=" * 60)
    
    # Estimate decay rate of matrix entries
    print("\nMatrix entry decay (along anti-diagonals):")
    for d in [1, 2, 3, 5, 10]:
        entry = get_matrix_entry(1, d)  # First entry of anti-diagonal d
        print(f"Anti-diagonal {d}: A[1,{d}] = {entry:.6f} ≈ 1/{int(1/entry)}")
    
    # The matrix is not symmetric, let's check a sample
    print("\nSample symmetry check (not expected to be symmetric):")
    print(f"A[1,2] = {get_matrix_entry(1, 2):.6f}")
    print(f"A[2,1] = {get_matrix_entry(2, 1):.6f}")
    print(f"Difference: {abs(get_matrix_entry(1, 2) - get_matrix_entry(2, 1)):.6f}")

if __name__ == "__main__":
    main()