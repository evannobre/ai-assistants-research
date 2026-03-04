import numpy as np

def generate_cantor_matrix(n):
    """
    Generates the N x N truncation of the infinite matrix 
    based on the Cantor pairing function.
    
    A_ij = 1 / k
    where k is the 1-based index in the diagonal traversal.
    """
    # Create a grid of indices (0 to n-1)
    # i represents rows, j represents columns
    i, j = np.indices((n, n))
    
    # Calculate the sum of indices for the diagonal group
    s = i + j
    
    # Cantor pairing function adapted for the specific sequence:
    # 1. Count elements in full diagonals before sum 's': s*(s+1)/2
    # 2. Add current row index 'i' (since we sort by row within diagonals)
    # 3. Add 1 because the value is 1/k (and k is 1-based)
    k = (s * (s + 1)) // 2 + i + 1
    
    # Generate the matrix entries
    return 1.0 / k

def power_method_spectral_norm(A, tolerance=1e-9, max_iterations=1000):
    """
    Approximates the spectral norm using the Power Method.
    Spectral Norm = sqrt(largest eigenvalue of A.T @ A)
    """
    n = A.shape[0]
    
    # 1. Initialize a random vector with L2 norm of 1
    v = np.random.rand(n)
    v = v / np.linalg.norm(v)
    
    sigma = 0.0
    
    for iteration in range(max_iterations):
        # 2. Apply A then A.T (equivalent to multiplying by A.T @ A)
        # We do this in two steps to avoid computing the expensive A.T @ A matrix explicitely
        # if A were sparse (though here A is dense).
        Av = np.dot(A, v)
        ATAv = np.dot(A.T, Av)
        
        # 3. Calculate the magnitude (approximation of eigenvalue of A.T @ A)
        # The eigenvalue of A.T @ A is sigma^2
        new_val_magnitude = np.linalg.norm(ATAv)
        
        # 4. Normalize the vector for the next iteration
        v_next = ATAv / new_val_magnitude
        
        # 5. Check for convergence
        # The spectral norm is the square root of the eigenvalue of A.T @ A.
        # However, power iteration on M=A.T@A gives us the eigenvalue directly as growth factor.
        current_sigma = np.sqrt(new_val_magnitude)
        
        if np.abs(current_sigma - sigma) < tolerance:
            print(f"Converged in {iteration + 1} iterations.")
            return current_sigma
        
        sigma = current_sigma
        v = v_next
        
    print("Max iterations reached.")
    return sigma

# --- Main Execution ---

# Simulation parameters
# N=5000 is sufficient; values at index 5000 are extremely small (~1/12,500,000)
truncation_size = 5000 

print(f"Generating {truncation_size}x{truncation_size} matrix block...")
A_truncated = generate_cantor_matrix(truncation_size)

print("Calculating Spectral Norm...")
estimated_norm = power_method_spectral_norm(A_truncated)

print(f"\nEstimated Spectral Norm: {estimated_norm:.6f}")

# Verification (only for smaller matrices as svd is expensive)
if truncation_size <= 2000:
    print("Verifying with numpy.linalg.norm (SVD based)...")
    exact_norm = np.linalg.norm(A_truncated, 2)
    print(f"Reference Spectral Norm: {exact_norm:.6f}")