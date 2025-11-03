import numpy as np

def spectral_norm(n, it=10):
    """
    Approximate the spectral norm of the infinite matrix A truncated to n×n.

    Parameters
    ----------
    n : int
        Truncation size.
    it : int, optional
        Number of power-method iterations (default: 10).

    Returns
    -------
    float
        Approximate spectral norm.
    """
    # Precompute row and column index vectors
    i = np.arange(n)[:, None]  # shape (n,1)
    j = np.arange(n)[None, :]  # shape (1,n)

    # Denominator matrix for A[i,j]
    denom = (i + j) * (i + j + 1) / 2 + i + 1  # shape (n,n)

    def mul_A(x):
        # A @ x
        return (x / denom).sum(axis=1)

    def mul_At(x):
        # Aᵀ @ x  (just transpose denom)
        return (x[:, None] / denom).sum(axis=0)

    # Power method iteration
    u = np.ones(n)
    for _ in range(it):
        v = mul_A(u)
        u = mul_At(v)
        u /= np.linalg.norm(u)

    # Final multiplication & Rayleigh quotient
    v = mul_A(u)
    return np.sqrt(np.dot(u, v))


if __name__ == "__main__":
    # Example: n = 1000, 10 iterations
    est = spectral_norm(1000, it=10)
    print(f"Spectral norm ≈ {est:.9f}")
