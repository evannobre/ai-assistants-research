import numpy as np

def a_entry(i, j):
    """
    Return a_{ij} for 1-based indices i,j.
    """
    k = i + j - 1
    denom = (k - 1) * k // 2 + i
    return 1.0 / denom

def matvec_A(v, N):
    """
    Compute w = A_N @ v where A_N is the N x N principal submatrix.
    v is length-N numpy array.
    """
    # Precompute j indices and i+j-1 diagonals
    w = np.zeros_like(v, dtype=float)
    # vectorized loop over rows i
    # For each row i, compute sum_j a_{ij} * v[j-1]
    j_idx = np.arange(1, N+1)
    for i in range(1, N+1):
        k = i + j_idx - 1
        denom = (k - 1) * k // 2 + i
        a_row = 1.0 / denom
        w[i-1] = a_row.dot(v)
    return w

def matvec_AT(v, N):
    """
    Compute w = A_N.T @ v for N x N principal submatrix.
    """
    w = np.zeros_like(v, dtype=float)
    i_idx = np.arange(1, N+1)
    for j in range(1, N+1):
        k = i_idx + j - 1
        denom = (k - 1) * k // 2 + i_idx
        a_col = 1.0 / denom  # this is column j entries a_{i,j}
        w[j-1] = a_col.dot(v)
    return w

def power_method_A_spectral_norm(N, maxiter=2000, tol=1e-10, verbose=False):
    """
    Estimate spectral norm of A_N using power method on A^T A.
    Returns estimated norm, number of iterations, and residual.
    """
    # initialize random vector
    x = np.random.randn(N)
    x /= np.linalg.norm(x)
    lambda_old = 0.0
    for it in range(1, maxiter+1):
        y = matvec_A(x, N)          # y = A x
        z = matvec_AT(y, N)         # z = A^T A x
        norm_z = np.linalg.norm(z)
        if norm_z == 0:
            return 0.0, it, 0.0
        x = z / norm_z
        # Rayleigh quotient for A^T A equals (x^T (A^T A) x) = ||A x||^2
        Ax = matvec_A(x, N)
        lambda_est = np.dot(Ax, Ax)  # eigenvalue estimate of A^T A
        sigma_est = np.sqrt(lambda_est)
        if verbose and (it % 50 == 0 or it == 1):
            print(f"iter {it:4d}: sigma ≈ {sigma_est:.12e}")
        if abs(lambda_est - lambda_old) <= tol * max(1.0, abs(lambda_est)):
            return sigma_est, it, abs(lambda_est - lambda_old)
        lambda_old = lambda_est
    # maxiter reached
    Ax = matvec_A(x, N)
    lambda_est = np.dot(Ax, Ax)
    return np.sqrt(lambda_est), maxiter, abs(lambda_est - lambda_old)

def estimate_spectral_norm_until_converged(N0=50, step=50, maxN=1000, tol_norm=1e-8, tol_power=1e-10, verbose=False):
    """
    Increase N starting at N0 by 'step' until spectral norm estimate stabilizes.
    Returns (sigma, N_used).
    """
    prev_sigma = None
    N = N0
    while N <= maxN:
        sigma, iters, resid = power_method_A_spectral_norm(N, tol=tol_power, verbose=verbose)
        if verbose:
            print(f"N={N}, sigma={sigma:.12e}, iters={iters}, resid={resid:.2e}")
        if prev_sigma is not None:
            if abs(sigma - prev_sigma) <= tol_norm * max(1.0, abs(sigma)):
                return sigma, N
        prev_sigma = sigma
        N += step
    # return last computed if maxN reached
    return prev_sigma, N-step
