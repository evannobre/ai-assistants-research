import numpy as np
import sys

def A_numpy(i: int, j: int) -> float:
    """NumPy version of matrix element computation."""
    k = i + j - 1
    seq_num = (k-1)*k//2 + i
    return 1.0 / seq_num

def spectral_norm_numpy(n: int) -> float:
    """NumPy-optimized spectral norm computation."""
    # Build the matrix explicitly (memory intensive for large n)
    A_mat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            A_mat[i, j] = A_numpy(i+1, j+1)
    
    # Use SVD to compute spectral norm
    # For very large matrices, use iterative methods instead
    sigma_max = np.linalg.svd(A_mat, compute_uv=False)[0]
    return sigma_max

def main_numpy():
    """NumPy version main function."""
    n = 5500 if len(sys.argv) < 2 else int(sys.argv[1])
    norm = spectral_norm_numpy(n)
    print(f"Spectral norm (NumPy): {norm:.9f}")
    return norm