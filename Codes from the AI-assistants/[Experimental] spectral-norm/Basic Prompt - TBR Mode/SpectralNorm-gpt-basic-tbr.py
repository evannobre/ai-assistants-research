import numpy as np

def spectral_norm(n_iters, size):
    """
    Approximate the spectral norm of the infinite matrix A (truncated to size×size)
    using n_iters of the power method.
    """
    # Helper: define A times vector
    def multiply_A(x):
        # x is a NumPy array of length `size`
        y = np.zeros_like(x)
        for i in range(size):
            # compute row i of A · x
            # A[i,j] = 1/(((i+j+1)*(i+j+2)//2) + i+1)
            j = np.arange(size)
            denom = ((i + j + 1)*(i + j + 2)//2) + (i + 1)
            y[i] = np.dot(x, 1.0/denom)
        return y

    # Helper: define A^T times vector
    def multiply_At(x):
        # x is a NumPy array of length `size`
        y = np.zeros_like(x)
        for j in range(size):
            # compute column j of A (row j of A^T) · x
            i = np.arange(size)
            denom = ((i + j + 1)*(i + j + 2)//2) + (i + 1)
            y[j] = np.dot(x, 1.0/denom)
        return y

    # Combined multiply by A^T A
    def multiply_AtA(x):
        return multiply_At(multiply_A(x))

    # Initialize v (random or constant)
    v = np.ones(size)
    # Power iterations
    for _ in range(n_iters):
        v = multiply_AtA(v)
        v /= np.linalg.norm(v)

    # Rayleigh quotient for λ ≈ vᵀ (AᵀA v)
    Av = multiply_A(v)
    AtAv = multiply_At(Av)
    rayleigh = np.dot(v, AtAv)
    return np.sqrt(rayleigh)

if __name__ == "__main__":
    # e.g. 20 iterations on a 2000×2000 truncation
    norm_est = spectral_norm(n_iters=20, size=2000)
    print(f"Estimated spectral norm ≈ {norm_est:.12f}")
