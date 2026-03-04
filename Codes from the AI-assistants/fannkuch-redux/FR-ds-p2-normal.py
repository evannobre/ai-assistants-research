#!/usr/bin/env python3
"""
Fannkuch-Redux Simulation
Optimized for performance on Ubuntu 24.04.4 with 8GB RAM
Uses native libraries and efficient algorithms
"""
import sys
import math
import time
import itertools
from typing import List, Tuple
import argparse
import logging
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from functools import lru_cache
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FannkuchResult:
    """Container for Fannkuch simulation results"""
    checksum: int
    max_flips: int
    duration: float


class FannkuchReducer:
    """Optimized Fannkuch-Redux implementation"""
    
    def __init__(self, n: int):
        if n <= 0 or n > 12:
            raise ValueError("n must be between 1 and 12 for practical performance")
        self.n = n
        self.factorials = self._precompute_factorials()
        
    @staticmethod
    @lru_cache(maxsize=128)
    def _precompute_factorials() -> List[int]:
        """Precompute factorials for permutation indexing"""
        facts = [1]
        for i in range(1, 13):
            facts.append(facts[-1] * i)
        return facts
    
    def count_flips(self, perm: List[int]) -> int:
        """
        Count the number of flips required for a permutation.
        Optimized with in-place operations to avoid copies.
        """
        # First element optimization
        if perm[0] == 0:
            return 0
            
        # Use numpy array for faster operations
        perm_array = np.array(perm, dtype=np.int8)
        flips = 0
        
        while perm_array[0] != 0:
            # Reverse the prefix up to perm[0] + 1
            k = perm_array[0]
            left, right = 1, k
            while left < right:
                perm_array[left], perm_array[right] = perm_array[right], perm_array[left]
                left += 1
                right -= 1
            flips += 1
            
        return flips
    
    def permutation_from_index(self, idx: int) -> List[int]:
        """
        Generate permutation from Lehmer code using factorials.
        More efficient than itertools.permutations for large n.
        """
        perm = list(range(self.n))
        for i in range(self.n):
            f = self.factorials[self.n - 1 - i]
            j = idx // f
            idx %= f
            perm[i], perm[i + j] = perm[i + j], perm[i]
        return perm
    
    def process_chunk(self, start_idx: int, end_idx: int) -> Tuple[int, int]:
        """
        Process a chunk of permutations for parallel execution.
        Returns (checksum, max_flips) for the chunk.
        """
        chunk_checksum = 0
        chunk_max_flips = 0
        
        for idx in range(start_idx, min(end_idx, self.factorials[self.n])):
            perm = self.permutation_from_index(idx)
            
            # Apply sign based on permutation parity
            sign = 1 if idx % 2 == 0 else -1
            
            flips = self.count_flips(perm)
            
            # Update statistics
            chunk_checksum += sign * flips
            chunk_max_flips = max(chunk_max_flips, flips)
            
        return chunk_checksum, chunk_max_flips
    
    def solve_sequential(self) -> FannkuchResult:
        """Sequential solution for smaller n values"""
        start_time = time.perf_counter()
        
        max_flips = 0
        checksum = 0
        
        # Use itertools for n <= 8 (more efficient for small n)
        if self.n <= 8:
            for idx, perm in enumerate(itertools.permutations(range(self.n))):
                sign = 1 if idx % 2 == 0 else -1
                flips = self.count_flips(list(perm))
                checksum += sign * flips
                max_flips = max(max_flips, flips)
        else:
            # Use factorial-based generation for larger n
            total_perms = self.factorials[self.n]
            for idx in range(total_perms):
                perm = self.permutation_from_index(idx)
                sign = 1 if idx % 2 == 0 else -1
                flips = self.count_flips(perm)
                checksum += sign * flips
                max_flips = max(max_flips, flips)
        
        duration = time.perf_counter() - start_time
        return FannkuchResult(checksum, max_flips, duration)
    
    def solve_parallel(self, num_workers: int = None) -> FannkuchResult:
        """
        Parallel solution using multiprocessing.
        Automatically determines optimal chunk size.
        """
        if num_workers is None:
            num_workers = max(1, cpu_count() - 1)  # Leave one core free
        
        start_time = time.perf_counter()
        total_perms = self.factorials[self.n]
        
        # Calculate chunk size (balance load between workers)
        chunk_size = max(1, total_perms // (num_workers * 4))
        chunks = []
        
        for i in range(0, total_perms, chunk_size):
            chunks.append((i, min(i + chunk_size, total_perms)))
        
        logger.info(f"Processing {total_perms} permutations with {num_workers} workers")
        logger.info(f"Chunk size: {chunk_size}, Total chunks: {len(chunks)}")
        
        # Process chunks in parallel
        with Pool(processes=num_workers) as pool:
            results = pool.starmap(self.process_chunk, chunks)
        
        # Aggregate results
        checksum = 0
        max_flips = 0
        for chunk_checksum, chunk_max_flips in results:
            checksum += chunk_checksum
            max_flips = max(max_flips, chunk_max_flips)
        
        duration = time.perf_counter() - start_time
        return FannkuchResult(checksum, max_flips, duration)
    
    def solve(self, use_parallel: bool = True) -> FannkuchResult:
        """
        Main solver with automatic strategy selection.
        Uses parallel processing for n >= 7.
        """
        # For n <= 6, sequential is faster due to overhead
        if self.n <= 6 or not use_parallel:
            logger.info(f"Using sequential solver for n={self.n}")
            return self.solve_sequential()
        else:
            logger.info(f"Using parallel solver for n={self.n}")
            return self.solve_parallel()


def validate_environment():
    """Validate system environment and dependencies"""
    import platform
    import os
    
    logger.info(f"System: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"CPU Cores: {cpu_count()}")
    
    # Check available memory (Linux-specific)
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemAvailable' in line:
                    mem_available = int(line.split()[1]) // 1024  # Convert to MB
                    logger.info(f"Available Memory: {mem_available} MB")
                    if mem_available < 100:
                        logger.warning("Low memory available!")
                    break
    except:
        logger.warning("Could not read memory info")
    
    # Verify numpy is available
    try:
        import numpy
        logger.info(f"NumPy version: {numpy.__version__}")
    except ImportError:
        logger.error("NumPy is required. Install with: pip install numpy")
        sys.exit(1)


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Fannkuch-Redux Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 7          # Run simulation for n=7
  %(prog)s 10 --sequential  # Force sequential execution
  %(prog)s 8 --benchmark    # Run benchmark with different strategies
        """
    )
    parser.add_argument('n', type=int, help='Number of elements (1-12 recommended)')
    parser.add_argument('--sequential', action='store_true', 
                       help='Force sequential execution')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run benchmark comparing strategies')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate input
    if args.n < 1:
        logger.error("n must be at least 1")
        sys.exit(1)
    
    if args.n > 12:
        logger.warning(f"n={args.n} is large. Execution may be slow and memory-intensive.")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Validate environment
    validate_environment()
    
    # Create solver
    try:
        solver = FannkuchReducer(args.n)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Run benchmark if requested
    if args.benchmark and args.n >= 7:
        logger.info("Running benchmark...")
        
        # Sequential
        seq_start = time.perf_counter()
        seq_result = solver.solve_sequential()
        seq_time = time.perf_counter() - seq_start
        
        # Parallel
        par_start = time.perf_counter()
        par_result = solver.solve_parallel()
        par_time = time.perf_counter() - par_start
        
        logger.info(f"\nBenchmark Results for n={args.n}:")
        logger.info(f"Sequential: {seq_time:.3f}s, Checksum: {seq_result.checksum}")
        logger.info(f"Parallel:   {par_time:.3f}s, Checksum: {par_result.checksum}")
        logger.info(f"Speedup:    {seq_time/par_time:.2f}x")
        
        # Use parallel result for output
        result = par_result
    else:
        # Normal execution
        result = solver.solve(use_parallel=not args.sequential)
    
    # Output results
    print(f"\nFannkuch-Redux Results for n={args.n}:")
    print(f"Checksum: {result.checksum}")
    print(f"Maximum flips: {result.max_flips}")
    print(f"Execution time: {result.duration:.3f} seconds")
    print(f"Permutations per second: {math.factorial(args.n) / result.duration:,.0f}")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(130)
    except MemoryError:
        logger.error("Out of memory! Try reducing n or using a machine with more RAM")
        sys.exit(137)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)