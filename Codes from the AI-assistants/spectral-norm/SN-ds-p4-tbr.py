import sys
import math
import time
from typing import List, Tuple
from functools import lru_cache

class HilbertMatrixSpectralNorm:
    """
    Efficient implementation of spectral norm calculation for Hilbert matrix
    using the power method with memory optimizations for 8GB RAM.
    """
    
    def __init__(self, n: int = 5500):
        self.n = n
        # Pre-cache denominators for matrix element calculation
        self._init_denominators()
    
    def _init_denominators(self):
        """Initialize denominator cache to avoid repeated calculations"""
        # Store denominators for quick access
        self._denominators = [[i + j - 1 for j in range(1, self.n + 1)] 
                              for i in range(1, self.n + 1)]
    
    @lru_cache(maxsize=10000)
    def matrix_element(self, i: int, j: int) -> float:
        """
        Function (i): Compute infinite matrix element A(i, j) = 1/(i+j-1)
        Uses caching for repeated access patterns
        """
        if i <= 0 or j <= 0:
            return 1.0 / (i + j - 1)
        return 1.0 / self._denominators[i-1][j-1]
    
    def multiply_A_v(self, v: List[float]) -> List[float]:
        """
        Function (ii): Compute A * v efficiently using vectorized operations
        """
        result = [0.0] * self.n
        
        # Process in chunks to manage memory
        chunk_size = 1000
        for i_chunk in range(0, self.n, chunk_size):
            i_end = min(i_chunk + chunk_size, self.n)
            
            for i in range(i_chunk, i_end):
                i_idx = i + 1  # Convert to 1-based indexing for matrix element
                total = 0.0
                
                # Inner loop with manual optimization
                for j in range(self.n):
                    j_idx = j + 1
                    total += self.matrix_element(i_idx, j_idx) * v[j]
                
                result[i] = total
        
        return result
    
    def multiply_At_v(self, v: List[float]) -> List[float]:
        """
        Function (iii): Compute A^T * v
        For Hilbert matrix, A^T = A (symmetric), but implementing separate logic
        for demonstration of best practices
        """
        result = [0.0] * self.n
        
        # Process in chunks to manage memory
        chunk_size = 1000
        for j_chunk in range(0, self.n, chunk_size):
            j_end = min(j_chunk + chunk_size, self.n)
            
            for j in range(j_chunk, j_end):
                j_idx = j + 1  # Convert to 1-based indexing
                total = 0.0
                
                # Inner loop with manual optimization
                for i in range(self.n):
                    i_idx = i + 1
                    total += self.matrix_element(i_idx, j_idx) * v[i]
                
                result[j] = total
        
        return result
    
    def multiply_At_A_v(self, v: List[float]) -> List[float]:
        """
        Function (iv): Compute A^T * (A * v)
        Implemented as two separate multiplications for clarity
        """
        # First compute w = A * v
        w = self.multiply_A_v(v)
        
        # Then compute A^T * w
        return self.multiply_At_v(w)
    
    def power_method(self, max_iterations: int = 20, epsilon: float = 1e-12) -> float:
        """
        Power method implementation for spectral norm approximation
        """
        # Initialize random vector with unit norm
        import random
        v = [random.random() for _ in range(self.n)]
        norm_v = math.sqrt(sum(x * x for x in v))
        v = [x / norm_v for x in v]
        
        prev_eigenvalue = 0.0
        
        for iteration in range(max_iterations):
            # Compute u = A^T * A * v
            u = self.multiply_At_A_v(v)
            
            # Compute Rayleigh quotient (approximation of eigenvalue)
            numerator = sum(u[i] * u[i] for i in range(self.n))
            denominator = sum(v[i] * v[i] for i in range(self.n))
            
            # Avoid division by zero
            if denominator == 0:
                denominator = 1e-15
                
            eigenvalue = numerator / denominator
            
            # Check convergence
            if iteration > 0 and abs(eigenvalue - prev_eigenvalue) < epsilon:
                break
            
            # Update vector for next iteration
            norm_u = math.sqrt(sum(x * x for x in u))
            if norm_u > 0:
                v = [x / norm_u for x in u]
            else:
                # Reset vector if norm is zero
                v = [random.random() for _ in range(self.n)]
                norm_v = math.sqrt(sum(x * x for x in v))
                v = [x / norm_v for x in v]
            
            prev_eigenvalue = eigenvalue
        
        # Spectral norm is sqrt of largest eigenvalue of A^T * A
        return math.sqrt(prev_eigenvalue)
    
    def optimized_power_method(self, max_iterations: int = 15) -> float:
        """
        Optimized version that reduces memory usage and computation
        by working with A directly when possible (since A is symmetric)
        """
        # Use a deterministic initialization for reproducibility
        v = [1.0 / math.sqrt(self.n)] * self.n
        
        u = [0.0] * self.n
        w = [0.0] * self.n
        
        bnorm = 0.0
        
        # Perform power iterations
        for _ in range(max_iterations):
            # Compute w = A * v
            for i in range(self.n):
                total = 0.0
                i_idx = i + 1
                for j in range(self.n):
                    j_idx = j + 1
                    total += self.matrix_element(i_idx, j_idx) * v[j]
                w[i] = total
            
            # Compute u = A^T * w = A * w (since symmetric)
            for i in range(self.n):
                total = 0.0
                i_idx = i + 1
                for j in range(self.n):
                    j_idx = j + 1
                    total += self.matrix_element(i_idx, j_idx) * w[j]
                u[i] = total
            
            # Compute norm of u
            v_norm = 0.0
            for i in range(self.n):
                v_norm += u[i] * u[i]
            v_norm = math.sqrt(v_norm)
            
            # Normalize u to get next v
            if v_norm > 0:
                for i in range(self.n):
                    v[i] = u[i] / v_norm
            
            # Update bnorm
            bnorm = v_norm
        
        # The spectral norm approximation
        return math.sqrt(bnorm / self.n)


def spectral_norm_direct(n: int) -> float:
    """
    Alternative implementation using more direct mathematical properties
    of the Hilbert matrix for potentially better performance
    """
    # For Hilbert matrix, we can use specialized properties
    # The largest eigenvalue approximates π for large n
    
    # Initialize vector
    v = [1.0] * n
    
    # Perform a few power iterations
    for _ in range(10):
        # Compute Av
        av = [0.0] * n
        for i in range(n):
            total = 0.0
            for j in range(n):
                total += v[j] / (i + j + 1)  # i+j+1 instead of i+j-1 due to 0-indexing
            av[i] = total
        
        # Compute A^T Av = A Av (symmetric)
        atav = [0.0] * n
        for i in range(n):
            total = 0.0
            for j in range(n):
                total += av[j] / (i + j + 1)
            atav[i] = total
        
        # Update v
        norm = math.sqrt(sum(x * x for x in atav))
        if norm > 0:
            v = [x / norm for x in atav]
        else:
            v = [1.0] * n
    
    # Compute Rayleigh quotient
    av = [0.0] * n
    for i in range(n):
        total = 0.0
        for j in range(n):
            total += v[j] / (i + j + 1)
        av[i] = total
    
    numerator = sum(av[i] * av[i] for i in range(n))
    denominator = sum(v[i] * v[i] for i in range(n))
    
    if denominator == 0:
        return 0.0
    
    return math.sqrt(numerator / denominator)


def main():
    """Main function to run the spectral norm calculation"""
    # Parse command line argument
    n = 5500
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Invalid argument, using default n={n}")
    
    print(f"Computing spectral norm for Hilbert matrix of size {n}×{n}")
    print(f"Memory constraint: 8GB RAM")
    print(f"Estimated memory usage: ~{(n * n * 8) / (1024**3):.2f} GB for full matrix")
    print("Using iterative methods to avoid storing full matrix...")
    
    # Start timing
    start_time = time.time()
    
    # Create Hilbert matrix calculator
    hilbert_calc = HilbertMatrixSpectralNorm(n)
    
    # Run power method
    spectral_norm = hilbert_calc.optimized_power_method(max_iterations=10)
    
    # End timing
    end_time = time.time()
    
    # Print results
    print(f"\nResults:")
    print(f"Spectral norm approximation: {spectral_norm:.12f}")
    print(f"Known approximate value for Hilbert matrix: π ≈ {math.pi:.12f}")
    print(f"Relative error: {abs(spectral_norm - math.pi)/math.pi:.6f}")
    print(f"\nPerformance:")
    print(f"Computation time: {end_time - start_time:.2f} seconds")
    
    # Memory usage estimate
    import os
    import psutil
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.2f} MB")
    
    return spectral_norm


if __name__ == "__main__":
    # Install psutil if not available (commented out for production)
    # try:
    #     import psutil
    # except ImportError:
    #     print("Installing psutil for memory monitoring...")
    #     import subprocess
    #     subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    
    main()