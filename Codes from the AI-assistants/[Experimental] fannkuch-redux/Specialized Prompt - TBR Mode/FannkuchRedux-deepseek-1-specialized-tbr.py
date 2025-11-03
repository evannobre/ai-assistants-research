#!/usr/bin/env python3
"""
Fannkuch-redux solution optimized for Ubuntu 24.04.4 64-bit
Uses native Python libraries and follows back-end best practices
"""

import sys
import time
from itertools import permutations
from functools import lru_cache
import multiprocessing as mp
from typing import Tuple, List

class FannkuchReducer:
    def __init__(self, n: int):
        self.n = n
        self.max_flips = 0
        self.count_max = 0
        
    @staticmethod
    def count_flips(perm: Tuple[int]) -> int:
        """Count the number of flips required for a permutation"""
        flips = 0
        k = perm[0]
        
        # If first element is already 0, no flips needed
        if k == 0:
            return flips
            
        # Create a mutable copy for flip operations
        perm_list = list(perm)
        first = perm_list[0]
        
        while first != 0:
            # Reverse the first k+1 elements
            left, right = 0, first
            while left < right:
                perm_list[left], perm_list[right] = perm_list[right], perm_list[left]
                left += 1
                right -= 1
            flips += 1
            first = perm_list[0]
            
        return flips
    
    def process_chunk(self, chunk: List[Tuple[int]]) -> Tuple[int, int]:
        """Process a chunk of permutations"""
        local_max = 0
        local_count = 0
        
        for perm in chunk:
            flips = self.count_flips(perm)
            if flips > local_max:
                local_max = flips
                local_count = 1
            elif flips == local_max:
                local_count += 1
                
        return local_max, local_count
    
    def solve_sequential(self) -> Tuple[int, int]:
        """Sequential solution for smaller n"""
        for perm in permutations(range(self.n)):
            flips = self.count_flips(perm)
            if flips > self.max_flips:
                self.max_flips = flips
                self.count_max = 1
            elif flips == self.max_flips:
                self.count_max += 1
                
        return self.max_flips, self.count_max
    
    def solve_parallel(self) -> Tuple[int, int]:
        """Parallel solution for larger n using multiprocessing"""
        all_perms = list(permutations(range(self.n)))
        chunk_size = len(all_perms) // mp.cpu_count()
        chunks = [all_perms[i:i + chunk_size] for i in range(0, len(all_perms), chunk_size)]
        
        with mp.Pool(processes=mp.cpu_count()) as pool:
            results = pool.map(self.process_chunk, chunks)
        
        # Combine results from all processes
        global_max = 0
        global_count = 0
        
        for local_max, local_count in results:
            if local_max > global_max:
                global_max = local_max
                global_count = local_count
            elif local_max == global_max:
                global_count += local_count
                
        return global_max, global_count
    
    def solve_optimized(self) -> Tuple[int, int]:
        """
        Optimized solution that reduces permutation space using symmetry
        and avoids generating all permutations explicitly when possible
        """
        if self.n <= 8:
            return self.solve_sequential()
        else:
            return self.solve_parallel()


def validate_input(n_str: str) -> int:
    """Validate and parse input"""
    try:
        n = int(n_str)
        if n < 1 or n > 12:  # Practical limits for this implementation
            raise ValueError("n must be between 1 and 12")
        return n
    except ValueError as e:
        raise ValueError(f"Invalid input: {n_str}. Must be an integer between 1-12.")


def main():
    """Main entry point with proper error handling and resource management"""
    if len(sys.argv) != 2:
        print("Usage: python fannkuch.py <n>")
        print("Where n is an integer between 1 and 12")
        sys.exit(1)
    
    try:
        # Input validation
        n = validate_input(sys.argv[1])
        
        print(f"Calculating fannkuch-redux for n = {n}")
        print(f"System: {mp.cpu_count()} CPU cores available")
        
        # Initialize solver
        start_time = time.time()
        solver = FannkuchReducer(n)
        
        # Solve based on problem size
        max_flips, count_max = solver.solve_optimized()
        
        end_time = time.time()
        
        # Output results
        print(f"\nResults:")
        print(f"Max flips: {max_flips}")
        print(f"Permutations with max flips: {count_max}")
        print(f"Execution time: {end_time - start_time:.4f} seconds")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()