#!/usr/bin/env python3
"""
Spectral Norm Simulation of Infinite Hilbert-like Matrix
Using Power Method with Optimized Memory Management
"""

import sys
import math
import time
from functools import lru_cache
from typing import Tuple
import numpy as np

class HilbertMatrixOperator:
    """
    Operator that simulates the infinite matrix A without explicitly storing it.
    Matrix entries follow: a11=1, a12=1/2, a21=1/3, a13=1/4, a22=1/5, a31=1/6, ...
    Pattern: Anti-diagonal ordering (Cantor pairing function)
    """
    
    @staticmethod
    @lru_cache(maxsize=10000)
    def _cantor_pairing(i: int, j: int) -> int:
        """
        Cantor pairing function to map (i,j) to a unique natural number.
        Returns the position in the anti-diagonal sequence.
        """
        # 1-based indices for mathematical clarity
        i1 = i - 1
        j1 = j - 1
        k = i1 + j1  # anti-diagonal index
        return k * (k + 1) // 2 + i1 + 1
    
    @staticmethod
    def matrix_element(i: int, j: int) -> float:
        """
        Returns A[i-1, j-1] (0-based indices in implementation, 1-based in math)
        """
        if i <= 0 or j <= 0:
            return 0.0
        position = HilbertMatrixOperator._cantor_pairing(i, j)
        return 1.0 / position
    
    def apply_A(self, x: np.ndarray) -> np.ndarray:
        """
        Compute y = A * x without forming the full matrix A.
        Uses vectorized operations where possible.
        """
        n = len(x)
        y = np.zeros(n, dtype=np.float64)
        
        # Vectorized approach for the main diagonal and nearby elements
        # We'll compute in chunks to balance performance and memory
        chunk_size = min(1000, n)
        
        for i_start in range(0, n, chunk_size):
            i_end = min(i_start + chunk_size, n)
            i_range = np.arange(i_start, i_end)
            
            # Create broadcasted i,j indices
            for j_start in range(0, n, chunk_size):
                j_end = min(j_start + chunk_size, n)
                j_range = np.arange(j_start, j_end)
                
                # Create meshgrid for this chunk
                I, J = np.meshgrid(i_range, j_range, indexing='ij')
                
                # Compute matrix elements vectorized
                # Convert to 1-based indices for the mathematical formula
                I_1based = I + 1
                J_1based = J + 1
                
                # Compute Cantor pairing vectorized
                k = I_1based + J_1based - 2  # anti-diagonal index
                positions = k * (k + 1) // 2 + I_1based
                A_chunk = 1.0 / positions
                
                # Multiply with corresponding x values
                y[i_start:i_end] += np.sum(A_chunk * x[j_start:j_end], axis=1)
        
        return y
    
    def apply_AT(self, x: np.ndarray) -> np.ndarray:
        """
        Compute y = A^T * x.
        For this symmetric pattern (in ordering), A^T has same pattern as A.
        """
        return self.apply_A(x)
    
    def apply_ATA(self, x: np.ndarray) -> np.ndarray:
        """
        Compute y = A^T * A * x efficiently.
        """
        return self.apply_AT(self.apply_A(x))


class SpectralNormCalculator:
    """
    Power Method implementation for spectral norm calculation.
    """
    
    def __init__(self, epsilon: float = 1e-12, max_iter: int = 1000):
        self.epsilon = epsilon
        self.max_iter = max_iter
    
    def power_method(self, operator: HilbertMatrixOperator, n: int) -> float:
        """
        Power method to compute the largest singular value (spectral norm).
        
        Args:
            operator: Matrix operator implementing apply_ATA
            n: Dimension for finite approximation
            
        Returns:
            Spectral norm (largest singular value)
        """
        # Initialize random vector with unit norm
        rng = np.random.default_rng(42)  # Fixed seed for reproducibility
        x = rng.standard_normal(n)
        x = x / np.linalg.norm(x)
        
        sigma_old = 0.0
        
        for iteration in range(self.max_iter):
            # Compute y = A^T A x
            y = operator.apply_ATA(x)
            
            # Rayleigh quotient
            sigma = np.sqrt(np.dot(x, y) / np.dot(x, x))
            
            # Check convergence
            if abs(sigma - sigma_old) < self.epsilon:
                print(f"Converged after {iteration + 1} iterations")
                break
            
            sigma_old = sigma
            
            # Normalize for next iteration
            norm_y = np.linalg.norm(y)
            if norm_y < 1e-14:
                break
            x = y / norm_y
        
        return sigma
    
    def analyze_convergence(self, operator: HilbertMatrixOperator, 
                           min_n: int = 100, max_n: int = 2000) -> dict:
        """
        Analyze spectral norm convergence as dimension increases.
        
        Args:
            operator: Matrix operator
            min_n: Minimum dimension
            max_n: Maximum dimension
            
        Returns:
            Dictionary with results and convergence analysis
        """
        results = {
            'dimensions': [],
            'spectral_norms': [],
            'relative_changes': [],
            'extrapolated_infinity': None
        }
        
        prev_sigma = None
        
        # Test with geometrically increasing dimensions
        dimensions = []
        current = min_n
        while current <= max_n:
            dimensions.append(current)
            current = int(current * 1.5)
        
        for n in dimensions:
            print(f"\nComputing for n = {n}")
            start_time = time.time()
            
            sigma = self.power_method(operator, n)
            elapsed = time.time() - start_time
            
            results['dimensions'].append(n)
            results['spectral_norms'].append(sigma)
            
            if prev_sigma is not None:
                rel_change = abs(sigma - prev_sigma) / prev_sigma
                results['relative_changes'].append(rel_change)
                print(f"  σ = {sigma:.10f}, Δ = {rel_change:.2e}, time = {elapsed:.2f}s")
            else:
                print(f"  σ = {sigma:.10f}, time = {elapsed:.2f}s")
            
            prev_sigma = sigma
        
        # Try Richardson extrapolation for infinite dimension
        if len(results['spectral_norms']) >= 3:
            # Simple extrapolation using last two points
            sigmas = results['spectral_norms']
            ns = results['dimensions']
            
            # Assume convergence as O(1/n^p), estimate p
            if len(sigmas) >= 3:
                p = math.log((sigmas[-2] - sigmas[-3]) / (sigmas[-1] - sigmas[-2])) / \
                    math.log(ns[-2] / ns[-1])
                
                # Extrapolate to infinity
                results['extrapolated_infinity'] = sigmas[-1] + \
                    (sigmas[-1] - sigmas[-2]) / (1 - (ns[-2]/ns[-1])**p)
        
        return results


def memory_efficient_power_method(n: int = 500) -> float:
    """
    Memory-optimized version for large n.
    Uses chunked operations and careful memory management.
    """
    # Initialize
    rng = np.random.default_rng(42)
    x = rng.standard_normal(n)
    x = x / np.linalg.norm(x)
    
    # Pre-allocate workspace
    y = np.zeros(n, dtype=np.float64)
    z = np.zeros(n, dtype=np.float64)
    
    sigma_old = 0.0
    epsilon = 1e-12
    max_iter = 500
    
    operator = HilbertMatrixOperator()
    
    for iteration in range(max_iter):
        # Step 1: z = A * x
        z.fill(0.0)
        
        # Process in chunks to control memory usage
        chunk_size = min(500, n)
        
        for i_start in range(0, n, chunk_size):
            i_end = min(i_start + chunk_size, n)
            
            for j_start in range(0, n, chunk_size):
                j_end = min(j_start + chunk_size, n)
                
                # Compute contributions to z[i_start:i_end]
                for i in range(i_start, i_end):
                    # 1-based indices for mathematical formula
                    i_1based = i + 1
                    row_sum = 0.0
                    
                    for j in range(j_start, j_end):
                        j_1based = j + 1
                        k = i_1based + j_1based - 2
                        pos = k * (k + 1) // 2 + i_1based
                        row_sum += x[j] / pos
                    
                    z[i] += row_sum
        
        # Step 2: y = A^T * z = A * z (since pattern is symmetric)
        y.fill(0.0)
        
        for i_start in range(0, n, chunk_size):
            i_end = min(i_start + chunk_size, n)
            
            for j_start in range(0, n, chunk_size):
                j_end = min(j_start + chunk_size, n)
                
                for i in range(i_start, i_end):
                    i_1based = i + 1
                    row_sum = 0.0
                    
                    for j in range(j_start, j_end):
                        j_1based = j + 1
                        k = i_1based + j_1based - 2
                        pos = k * (k + 1) // 2 + i_1based
                        row_sum += z[j] / pos
                    
                    y[i] += row_sum
        
        # Rayleigh quotient for A^T A
        sigma = math.sqrt(np.dot(x, y) / np.dot(x, x))
        
        # Check convergence
        if abs(sigma - sigma_old) < epsilon:
            print(f"Converged after {iteration + 1} iterations")
            break
        
        sigma_old = sigma
        
        # Normalize for next iteration
        norm_y = math.sqrt(np.dot(y, y))
        if norm_y < 1e-14:
            break
        
        # Update x = y / ||y||
        x = y / norm_y
    
    return sigma


def main():
    """Main execution function with command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Compute spectral norm of infinite Hilbert-like matrix"
    )
    parser.add_argument("-n", "--dimension", type=int, default=500,
                       help="Dimension for finite approximation")
    parser.add_argument("-m", "--memory-efficient", action="store_true",
                       help="Use memory-efficient implementation")
    parser.add_argument("-a", "--analyze", action="store_true",
                       help="Run convergence analysis")
    args = parser.parse_args()
    
    print(f"System: Ubuntu 24.04.4, 8GB RAM, 256GB SSD")
    print(f"Matrix pattern: a11=1, a12=1/2, a21=1/3, a13=1/4, a22=1/5, ...")
    print(f"Using dimension: n = {args.dimension}")
    print("-" * 60)
    
    if args.memory_efficient:
        print("Using memory-efficient implementation...")
        sigma = memory_efficient_power_method(args.dimension)
        print(f"\nSpectral norm estimate: σ ≈ {sigma:.10f}")
    else:
        operator = HilbertMatrixOperator()
        calculator = SpectralNormCalculator()
        
        if args.analyze:
            print("Running convergence analysis...")
            results = calculator.analyze_convergence(operator, min_n=100, 
                                                    max_n=min(args.dimension, 2000))
            
            if results['extrapolated_infinity']:
                print(f"\nExtrapolated value for infinite matrix: "
                      f"σ∞ ≈ {results['extrapolated_infinity']:.10f}")
        else:
            print("Computing spectral norm...")
            sigma = calculator.power_method(operator, args.dimension)
            print(f"\nSpectral norm estimate: σ ≈ {sigma:.10f}")
    
    # Memory usage report
    import psutil
    process = psutil.Process()
    mem_info = process.memory_info()
    print(f"\nMemory usage: {mem_info.rss / 1024**2:.2f} MB")
    print(f"Available memory: {psutil.virtual_memory().available / 1024**3:.2f} GB")


if __name__ == "__main__":
    main()