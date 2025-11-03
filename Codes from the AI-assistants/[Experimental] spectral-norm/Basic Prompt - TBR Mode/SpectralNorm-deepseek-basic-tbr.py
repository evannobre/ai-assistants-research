import numpy as np

def main(N=500, max_iter=20):
    # Construct the truncated matrix A of size N x N
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            n = i + j + 1  # anti-diagonal index (0-indexed adjustment)
            T = (n - 1) * n // 2  # triangular number T_{n-1}
            A[i, j] = 1.0 / (T + i + 1)  # a_{i+1,j+1} = 1/(T_{n-1} + i+1)
    
    # Initialize a random unit vector
    x = np.random.randn(N)
    x /= np.linalg.norm(x)
    
    # Power Method iterations
    for _ in range(max_iter):
        y = A @ x
        x_new = A.T @ y
        x_norm = np.linalg.norm(x_new)
        x = x_new / x_norm
    
    # Final singular value estimation
    y_final = A @ x
    sigma = np.linalg.norm(y_final)
    
    return sigma

if __name__ == "__main__":
    spectral_norm = main()
    print(f"Estimated spectral norm: {spectral_norm}")