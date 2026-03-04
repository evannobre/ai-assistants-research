import numpy as np
import sys

# (i) Computes the infinite matrix element A(i, j)
# Using 0-based indexing for i and j.
# The denominator sequence is 1, 2, 3, 4, 5, 6, ...
# For A(0,0) -> 1
# For A(0,1) -> 2
# For A(1,0) -> 3
# For A(0,2) -> 4
# For A(1,1) -> 5
# For A(2,0) -> 6
# The formula for the index k in the sequence corresponding to A(i,j) is
# k = 0.5 * (i + j) * (i + j + 1) + i + 1
# So, A(i,j) = 1 / k
def A_element(i: int, j: int) -> float:
    """
    Computes the (i, j) element of the infinite matrix A.
    Uses 0-based indexing for i and j.
    """
    # Calculate k based on the provided sequence logic
    k = 0.5 * (i + j) * (i + j + 1) + i + 1
    return 1.0 / k

# (ii) Computes A * v
def Av(v: np.ndarray) -> np.ndarray:
    """
    Computes the product of matrix A and vector v (A * v).
    A is implicitly defined by A_element.
    """
    N = v.size
    result = np.zeros(N, dtype=np.float64)
    for i in range(N):
        sum_row = 0.0
        for j in range(N):
            sum_row += A_element(i, j) * v[j]
        result[i] = sum_row
    return result

# (iii) Computes Aᵗ * v
def Atv(v: np.ndarray) -> np.ndarray:
    """
    Computes the product of matrix A transpose and vector v (A^T * v).
    A is implicitly defined by A_element.
    """
    N = v.size
    result = np.zeros(N, dtype=np.float64)
    for i in range(N):
        sum_col = 0.0
        for j in range(N):
            # A^T(i, j) is A(j, i)
            sum_col += A_element(j, i) * v[j]
        result[i] = sum_col
    return result

# (iv) Computes Aᵗ * (A * v)
def AtAv(v: np.ndarray) -> np.ndarray:
    """
    Computes the product A^T * (A * v).
    This is the core operation for the Power Method when finding dominant singular value.
    """
    u = Av(v)
    result = Atv(u)
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python spectral_norm.py <N>")
        sys.exit(1)

    N = int(sys.argv[1])
    if N <= 0:
        print("N must be a positive integer.")
        sys.exit(1)

    # Initialize a vector v of size N with all ones
    # For Power Method, starting with a vector of ones is common.
    # We use float64 for precision.
    v = np.ones(N, dtype=np.float64)

    # Number of iterations for the Power Method
    # Typically 10-20 iterations are sufficient for good convergence.
    # The problem description implicitly suggests enough iterations for performance check.
    # For competitive programming benchmarks, 10 iterations is a common number.
    num_iterations = 10

    for _ in range(num_iterations):
        # Apply AtA to the vector
        v = AtAv(v)
        # Normalize the vector to prevent overflow/underflow.
        # This normalization does not affect the direction of the eigenvector.
        # It's important for numerical stability.
        norm_v = np.linalg.norm(v)
        if norm_v == 0:
            # Handle the case where the vector becomes zero (should not happen with this matrix)
            print("Vector became zero during power iteration. Exiting.")
            sys.exit(1)
        v = v / norm_v

    # After convergence, v is approximately the dominant eigenvector of A^T A.
    # The dominant eigenvalue lambda of A^T A is ||A*v||^2 / ||v||^2
    # Since v is normalized to unit length, ||v||^2 = 1.
    # So, lambda = ||A*v||^2.
    # And the spectral norm ||A||_2 = sqrt(lambda).

    # Compute u = Av after the final iteration
    u = Av(v)

    # Calculate the squared spectral norm (dominant eigenvalue of A^T A)
    # The eigenvalue is (u^T u) / (v^T v)
    # Since v is already normalized to unit length, v^T v = 1.
    # So the eigenvalue is approximately u^T u = ||u||^2.
    # We can also directly compute (v_new^T v) from the last AtAv operation.
    # Let's compute it explicitly using the final v and u.
    
    # Calculate the numerator and denominator for the Rayleigh quotient: (v^T (A^T A) v) / (v^T v)
    # We have computed u = Av, and v has been normalized.
    # So, the numerator becomes v^T u = v^T (Av)
    # Denominator is v^T v (which is 1 since v is normalized)
    
    # Let's re-compute Av and AtAv on the final un-normalized vector to get the correct Rayleigh quotient
    # This is more robust for eigenvalue calculation
    
    # Re-initialize v for the final calculation without intermediate normalizations impacting the ratio directly
    # A common approach is to keep a non-normalized v and compute the Rayleigh quotient at the end
    # For the problem's focus on performance and "native" feel, let's stick to the standard Power Method flow
    # where v is normalized at each step and then compute the norm directly.
    
    # The spectral norm is ||A||_2 = sqrt(largest eigenvalue of A^T A)
    # which is sqrt( (v^T (A^T A) v) / (v^T v) )
    # Let v_final be the normalized vector after iterations.
    # We need to compute v_final^T (A^T A) v_final
    # This is equivalent to (A v_final)^T (A v_final) = ||A v_final||_2^2

    # Calculate the numerator: ||A * v||^2
    numerator_vec = Av(v)
    numerator = np.dot(numerator_vec, numerator_vec) # This is ||A*v||^2

    # Calculate the denominator: ||v||^2
    denominator = np.dot(v, v) # This is ||v||^2. Since v is normalized, this should be close to 1.0

    # The dominant eigenvalue of A^T A is numerator / denominator
    spectral_norm_squared = numerator / denominator
    spectral_norm = np.sqrt(spectral_norm_squared)

    # Print the result formatted to 9 decimal places as per typical benchmark requirements
    print(f"{spectral_norm:.9f}")

if __name__ == "__main__":
    main()