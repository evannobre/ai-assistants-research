#!/usr/bin/env python3
"""
Memory-optimized fannkuch-redux solution
Uses iterative permutation generation to avoid storing all permutations
"""

import sys
import time
from typing import Iterator, Tuple

class MemoryEfficientFannkuch:
    def __init__(self, n: int):
        self.n = n
        self.max_flips = 0
        self.count_max = 0
        
    def count_flips(self, perm: list) -> int:
        """Count flips without creating copies when possible"""
        if perm[0] == 0:
            return 0
            
        flips = 0
        first = perm[0]
        
        # Use the same array for flips to avoid memory allocation
        temp_perm = perm[:]  # Only copy when necessary
        
        while temp_perm[0] != 0:
            k = temp_perm[0]
            # Reverse first k+1 elements in place
            left, right = 0, k
            while left < right:
                temp_perm[left], temp_perm[right] = temp_perm[right], temp_perm[left]
                left += 1
                right -= 1
            flips += 1
            
        return flips
    
    def generate_permutations(self) -> Iterator[list]:
        """Generate permutations iteratively using Heap's algorithm"""
        perm = list(range(self.n))
        c = [0] * self.n
        i = 0
        
        yield perm[:]
        
        while i < self.n:
            if c[i] < i:
                if i % 2 == 0:
                    perm[0], perm[i] = perm[i], perm[0]
                else:
                    perm[c[i]], perm[i] = perm[i], perm[c[i]]
                yield perm[:]
                c[i] += 1
                i = 0
            else:
                c[i] = 0
                i += 1
    
    def solve(self) -> Tuple[int, int]:
        """Solve using iterative permutation generation"""
        count = 0
        for perm in self.generate_permutations():
            flips = self.count_flips(perm)
            if flips > self.max_flips:
                self.max_flips = flips
                self.count_max = 1
            elif flips == self.max_flips:
                self.count_max += 1
                
            count += 1
            if count % 100000 == 0:  # Progress indicator
                print(f"Processed {count} permutations...")
                
        return self.max_flips, self.count_max


def main_memory_efficient():
    """Main function for memory-efficient version"""
    if len(sys.argv) != 2:
        print("Usage: python fannkuch_mem.py <n>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n < 1:
            raise ValueError("n must be positive")
            
        print(f"Calculating fannkuch-redux for n = {n} (memory-efficient)")
        start_time = time.time()
        
        solver = MemoryEfficientFannkuch(n)
        max_flips, count_max = solver.solve()
        
        end_time = time.time()
        
        print(f"\nResults:")
        print(f"Max flips: {max_flips}")
        print(f"Permutations with max flips: {count_max}")
        print(f"Execution time: {end_time - start_time:.4f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_memory_efficient()