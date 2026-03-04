#!/usr/bin/env python3
"""
Fannkuch-redux algorithm optimized for performance
Uses native Python libraries and efficient permutation generation
"""

import sys
import time
from typing import Tuple
from array import array

def fannkuch(n: int) -> Tuple[int, int]:
    """
    Calculate maximum flips and checksum for fannkuch-redux problem
    Returns: (max_flips, checksum)
    """
    # Initialize permutations and auxiliary arrays
    perm = array('i', range(n))
    perm1 = array('i', range(n))
    count = array('i', [0] * n)
    
    max_flips = 0
    checksum = 0
    perm_sign = 1
    
    r = n
    
    # Main loop for all permutations
    while True:
        # Skip permutations where first element is not 1 (optimization)
        while r != 1:
            count[r - 1] = r
            r -= 1
        
        # Calculate flips for current permutation
        first = perm1[0]
        if first != 0:
            # Copy to working array
            perm[:] = perm1
            
            flips = 0
            k = first
            # Perform flips
            while k:
                # Reverse the first k elements
                i = 0
                j = k
                while i < j:
                    perm[i], perm[j] = perm[j], perm[i]
                    i += 1
                    j -= 1
                flips += 1
                k = perm[0]
            
            # Update max flips and checksum
            if flips > max_flips:
                max_flips = flips
            
            checksum += perm_sign * flips
        
        # Generate next permutation using Heap's algorithm
        while True:
            if r == n:
                return max_flips, checksum
            
            # Update count array
            perm0 = perm1[0]
            i = 0
            while i < r:
                j = i + 1
                perm1[i] = perm1[j]
                i = j
            perm1[r] = perm0
            
            count[r] -= 1
            if count[r] > 0:
                break
            
            r += 1
            perm_sign = -perm_sign

def main():
    if len(sys.argv) != 2:
        print("Usage: python fannkuch.py <n>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: n must be an integer")
        sys.exit(1)
    
    if n < 1:
        print("Error: n must be positive")
        sys.exit(1)
    
    # Check memory usage for n=12
    if n == 12:
        # n! permutations = 479001600
        # Each array of 12 ints (4 bytes) = 48 bytes
        # Main arrays: 4 arrays × 48 bytes = 192 bytes
        # Well within 8GB RAM
        pass
    
    start_time = time.time()
    max_flips, checksum = fannkuch(n)
    end_time = time.time()
    
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")
    print(f"Time: {end_time - start_time:.3f} seconds")

if __name__ == "__main__":
    main()