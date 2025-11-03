#!/usr/bin/env python3
"""
Spectral Norm computation using Power Method for infinite Hilbert matrix.
Matrix entries: a_ij = 1/(i+j-1)

Author: Computer Scientist specialized in back-end development
Target: Ubuntu 24.04.2 LTS 64-bit, 16GB RAM, 30GB SSD
"""

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import norm as sparse_norm
import psutil
import gc
import time
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)


class InfiniteHilbertMatrix:
    """
    Represents an infinite Hilbert matrix with entries a_ij = 1/(i+j-1).
    Uses truncation and sparse representation for memory efficiency.
    """
    
    def __init__(self, max_size: int = 1000, sparsity_threshold: float = 1e-12):
        """
        Initialize the matrix representation.
        
        Args:
            max_size: Maximum matrix dimension to consider
            sparsity_threshold: Values below this are treated as zero
        """
        self.max_size = max_size
        self.sparsity_threshold = sparsity_threshold
        self.matrix = None
        self._build_matrix()
    
    def _build_matrix(self):
        """Build the truncated Hilbert matrix efficiently using sparse format."""
        print(f"Building {self.max_size}x{self.max_size} Hilbert matrix...")
        
        # Pre-allocate arrays for sparse matrix construction
        rows, cols, data = [], [], []
        
        # Generate matrix entries
        for i in range(self.max_size):
            for j in range(self.max_size):
                value = 1.0 / (i + j + 1)  # a_ij = 1/(i+j-1), 0-indexed
                
                if value >= self.sparsity_threshold:
                    rows.append(i)
                    cols.append(j)
                    data.append(value)
        
        # Create sparse matrix
        self.matrix = sp.csr_matrix(
            (data, (rows, cols)), 
            shape=(self.max_size, self.max_size),
            dtype=np.float64
        )
        
        print(f"Matrix built: {self.matrix.nnz} non-zero elements "
              f"({100*self.matrix.nnz/(self.max_size**2):.2f}% density)")
    
    def matvec(self, x: np.ndarray) -> np.ndarray:
        """Matrix-vector multiplication optimized for the Hilbert structure."""
        return self.matrix.dot(x)
    
    def get_memory_usage(self) -> float:
        """Return memory usage in MB."""
        return self.matrix.data.nbytes / (1024**2)


class PowerMethodSpectralNorm:
    """
    Implements the Power Method for computing the spectral norm (largest singular value).
    Optimized for memory efficiency and numerical stability.
    """
    
    def __init__(self, matrix: InfiniteHilbertMatrix, max_iterations: int = 1000, 
                 tolerance: float = 1e-10, memory_limit_gb: float = 12.0):
        """
        Initialize the Power Method solver.
        
        Args:
            matrix: The infinite matrix representation
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            memory_limit_gb: Memory limit in GB
        """
        self.matrix = matrix
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.memory_limit_bytes = memory_limit_gb * 1024**3
        self.convergence_history = []
    
    def _check_memory_usage(self) -> bool:
        """Check if current memory usage exceeds limit."""
        current_memory = psutil.virtual_memory().used
        return current_memory < self.memory_limit_bytes
    
    def _power_iteration(self, x: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Perform one iteration of the power method.
        
        Args:
            x: Current vector
            
        Returns:
            Tuple of (normalized vector, eigenvalue estimate)
        """
        # Compute A^T * A * x for spectral norm (largest singular value)
        Ax = self.matrix.matvec(x)
        ATAx = self.matrix.matrix.T.dot(Ax)
        
        # Compute Rayleigh quotient
        eigenvalue = np.dot(x, ATAx) / np.dot(x, x)
        
        # Normalize
        norm_ATAx = np.linalg.norm(ATAx)
        if norm_ATAx > 0:
            x_new = ATAx / norm_ATAx
        else:
            x_new = x
        
        return x_new, eigenvalue
    
    def compute_spectral_norm(self, initial_vector: Optional[np.ndarray] = None) -> dict:
        """
        Compute the spectral norm using the Power Method.
        
        Args:
            initial_vector: Initial guess vector (random if None)
            
        Returns:
            Dictionary with results and convergence information
        """
        n = self.matrix.max_size
        
        # Initialize vector
        if initial_vector is None:
            np.random.seed(42)  # For reproducibility
            x = np.random.randn(n)
        else:
            x = initial_vector.copy()
        
        x = x / np.linalg.norm(x)
        
        print(f"Starting Power Method iteration (max_iter={self.max_iterations}, tol={self.tolerance})")
        print(f"Matrix size: {n}x{n}")
        print(f"Memory usage: {self.matrix.get_memory_usage():.2f} MB")
        
        start_time = time.time()
        prev_eigenvalue = 0.0
        
        for iteration in range(self.max_iterations):
            # Check memory usage periodically
            if iteration % 100 == 0 and not self._check_memory_usage():
                print(f"Memory limit exceeded at iteration {iteration}")
                break
            
            # Power iteration
            x, eigenvalue = self._power_iteration(x)
            
            # Check convergence
            error = abs(eigenvalue - prev_eigenvalue)
            self.convergence_history.append(error)
            
            if iteration % 50 == 0:
                print(f"Iteration {iteration:4d}: λ = {eigenvalue:.10f}, error = {error:.2e}")
            
            if error < self.tolerance:
                print(f"Converged at iteration {iteration}")
                break
            
            prev_eigenvalue = eigenvalue
            
            # Memory cleanup
            if iteration % 200 == 0:
                gc.collect()
        
        # Spectral norm is sqrt of largest eigenvalue of A^T*A
        spectral_norm = np.sqrt(eigenvalue)
        computation_time = time.time() - start_time
        
        # Theoretical spectral norm for Hilbert matrix (for comparison)
        theoretical_norm = np.pi  # Known result for infinite Hilbert matrix
        
        results = {
            'spectral_norm': spectral_norm,
            'largest_eigenvalue_ATA': eigenvalue,
            'iterations': iteration + 1,
            'final_error': error,
            'computation_time': computation_time,
            'theoretical_norm': theoretical_norm,
            'relative_error': abs(spectral_norm - theoretical_norm) / theoretical_norm,
            'convergence_history': self.convergence_history.copy(),
            'memory_usage_mb': self.matrix.get_memory_usage()
        }
        
        return results


def adaptive_matrix_size(target_accuracy: float = 1e-6, max_size: int = 2000) -> int:
    """
    Determine optimal matrix size based on available memory and target accuracy.
    
    Args:
        target_accuracy: Desired accuracy
        max_size: Maximum allowed matrix size
        
    Returns:
        Optimal matrix size
    """
    available_memory = psutil.virtual_memory().available
    
    # Estimate memory per matrix element (sparse storage)
    bytes_per_element = 24  # 8 bytes for data + 16 bytes for indices
    
    # Calculate maximum size based on memory (using ~80% of available memory)
    max_size_memory = int(np.sqrt(0.8 * available_memory / bytes_per_element))
    
    # Choose conservative size
    optimal_size = min(max_size, max_size_memory, 1500)
    
    print(f"Available memory: {available_memory/(1024**3):.1f} GB")
    print(f"Calculated optimal matrix size: {optimal_size}")
    
    return optimal_size


def main():
    """Main execution function."""
    print("=== Spectral Norm Computation for Infinite Hilbert Matrix ===")
    print("Using Power Method with optimized sparse matrix representation")
    print()
    
    # System information
    print("System Information:")
    print(f"CPU cores: {psutil.cpu_count()}")
    print(f"Total RAM: {psutil.virtual_memory().total/(1024**3):.1f} GB")
    print(f"Available RAM: {psutil.virtual_memory().available/(1024**3):.1f} GB")
    print()
    
    # Determine optimal matrix size
    matrix_size = adaptive_matrix_size()
    
    try:
        # Create matrix representation
        hilbert_matrix = InfiniteHilbertMatrix(
            max_size=matrix_size,
            sparsity_threshold=1e-15
        )
        
        # Initialize Power Method solver
        solver = PowerMethodSpectralNorm(
            matrix=hilbert_matrix,
            max_iterations=1000,
            tolerance=1e-10,
            memory_limit_gb=12.0
        )
        
        # Compute spectral norm
        results = solver.compute_spectral_norm()
        
        # Display results
        print("\n=== RESULTS ===")
        print(f"Matrix size: {matrix_size}x{matrix_size}")
        print(f"Computed spectral norm: {results['spectral_norm']:.10f}")
        print(f"Theoretical spectral norm: {results['theoretical_norm']:.10f}")
        print(f"Relative error: {results['relative_error']:.2e}")
        print(f"Iterations: {results['iterations']}")
        print(f"Final convergence error: {results['final_error']:.2e}")
        print(f"Computation time: {results['computation_time']:.2f} seconds")
        print(f"Memory usage: {results['memory_usage_mb']:.2f} MB")
        
        # Performance analysis
        print(f"\nPerformance Analysis:")
        print(f"Convergence rate: {results['final_error']:.2e} in {results['iterations']} iterations")
        print(f"Time per iteration: {results['computation_time']/results['iterations']:.4f} seconds")
        
        return results
        
    except Exception as e:
        print(f"Error during computation: {e}")
        return None


if __name__ == "__main__":
    # Set numpy to use single thread for reproducible results
    import os
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    
    results = main()