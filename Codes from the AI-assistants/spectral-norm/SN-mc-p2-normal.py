import numpy as np


def a_ij(i: int, j: int) -> float:
    """
    Entry a_{ij} of the infinite matrix A, using 1-based indices.
    Enumeration along anti-diagonals:
      (1,1)->1, (1,2)->2, (2,1)->3, (1,3)->4, (2,2)->5, (3,1)->6, ...
    """
    s = i + j - 1  # anti-diagonal index
    triangular = (s - 1) * s // 2  # T_{s-1}
    k = triangular + i
    return 1.0 / k


def matvec_A(x: np.ndarray) -> np.ndarray:
    """
    y = A x, where A is the infinite matrix truncated to len(x) x len(x).
    Uses implicit definition of A; 1-based indices in formula, 0-based in code.
    """
    n = x.shape[0]
    y = np.zeros_like(x, dtype=float)
    for i in range(1, n + 1):
        acc = 0.0
        for j in range(1, n + 1):
            acc += a_ij(i, j) * x[j - 1]
        y[i - 1] = acc
    return y


def matvec_AT(y: np.ndarray) -> np.ndarray:
    """
    z = A^T y, with same truncation as matvec_A.
    """
    n = y.shape[0]
    z = np.zeros_like(y, dtype=float)
    for j in range(1, n + 1):
        acc = 0.0
        for i in range(1, n + 1):
            acc += a_ij(i, j) * y[i - 1]
        z[j - 1] = acc
    return z


def spectral_norm_power_method(
    n: int,
    max_iter: int = 200,
    tol: float = 1e-10,
    random_state: int | None = 42,
) -> float:
    """
    Approximate the spectral norm (largest singular value) of the infinite matrix A
    by truncating to n x n and applying the power method to A^T A.

    Returns an estimate of ||A||_2 for the n x n truncation.
    """
    rng = np.random.default_rng(random_state)
    x = rng.normal(size=n)
    x /= np.linalg.norm(x)

    prev_lambda = 0.0

    for _ in range(max_iter):
        # y = A x
        y = matvec_A(x)
        # z = A^T y = (A^T A) x
        z = matvec_AT(y)

        # Normalize
        norm_z = np.linalg.norm(z)
        if norm_z == 0.0:
            # Degenerate case; x is in the null space
            return 0.0
        x = z / norm_z

        # Rayleigh quotient for A^T A: lambda ≈ x^T (A^T A) x = ||A x||^2
        y = matvec_A(x)
        lambda_est = float(np.dot(y, y))

        if abs(lambda_est - prev_lambda) < tol * max(1.0, abs(lambda_est)):
            break
        prev_lambda = lambda_est

    spectral_norm_est = np.sqrt(lambda_est)
    return spectral_norm_est


if __name__ == "__main__":
    # Choose truncation size N based on time/memory tradeoff.
    # Start small, then increase.
    N = 1000
    est = spectral_norm_power_method(N, max_iter=150, tol=1e-9)
    print(f"Estimated spectral norm ||A||_2 for {N}x{N} truncation: {est:.10f}")
