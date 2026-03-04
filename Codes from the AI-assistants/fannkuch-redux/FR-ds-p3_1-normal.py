#!/usr/bin/env python3
"""
Fannkuch-redux implementation using Python's native libraries.
Optimized for performance while respecting system constraints.
"""
import sys
import itertools
from functools import lru_cache
from array import array

def fannkuch_redux(n: int):
    """
    Compute the maximum flips and checksum for all permutations of 1..n
    """
    if n < 1:
        return (0, 0)
    
    # Pre-allocate arrays for better performance
    permutation = array('i', range(1, n + 1))
    temp_perm = array('i', range(1, n + 1))
    count = array('i', [0] * n)
    
    max_flips = 0
    checksum = 0
    perm_count = 0
    r = n
    
    while True:
        # Count flips for current permutation
        first = permutation[0]
        if first != 1:
            # Copy to temp for flipping
            temp_perm[:] = permutation
            
            flips = 0
            k = first
            while k != 1:
                # Reverse the first k elements
                i, j = 0, k - 1
                while i < j:
                    temp_perm[i], temp_perm[j] = temp_perm[j], temp_perm[i]
                    i += 1
                    j -= 1
                flips += 1
                k = temp_perm[0]
            
            # Update statistics
            if flips > max_flips:
                max_flips = flips
            if perm_count % 2 == 0:
                checksum += flips
            else:
                checksum -= flips
        
        # Generate next permutation using Johnson-Trotter algorithm
        while r != 1:
            count[r - 1] = r
            r -= 1
        
        while True:
            if r == n:
                return max_flips, checksum
            
            # Get next permutation
            perm0 = permutation[0]
            i = 0
            while i < r:
                permutation[i] = permutation[i + 1]
                i += 1
            permutation[r] = perm0
            
            count[r] -= 1
            if count[r] > 0:
                break
            r += 1
        
        perm_count += 1

def fannkuch_redux_itertools(n: int):
    """
    Alternative implementation using itertools (more readable but slightly slower)
    """
    max_flips = 0
    checksum = 0
    
    for i, perm in enumerate(itertools.permutations(range(1, n + 1))):
        perm = list(perm)
        flips = 0
        
        while perm[0] != 1:
            k = perm[0]
            # Reverse first k elements
            perm[:k] = perm[k-1::-1]
            flips += 1
        
        if flips > max_flips:
            max_flips = flips
        
        if i % 2 == 0:
            checksum += flips
        else:
            checksum -= flips
    
    return max_flips, checksum

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <n>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: n must be an integer")
        sys.exit(1)
    
    if n < 0 or n > 12:  # n=12 requires ~1.5GB memory with naive approach
        print("Error: n must be between 0 and 12")
        sys.exit(1)
    
    # Use optimized version for better performance
    max_flips, checksum = fannkuch_redux(n)
    
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")

if __name__ == "__main__":
    main()