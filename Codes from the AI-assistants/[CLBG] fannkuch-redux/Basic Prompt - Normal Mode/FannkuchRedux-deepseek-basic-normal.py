#!/usr/bin/env python3
"""
Fannkuch-redux implementation using efficient permutation generation
and native Python libraries for optimal performance.
"""

import sys
import itertools
from array import array

def fannkuch(n):
    """Calculate maximum flips and checksum for all permutations of 1..n"""
    if n < 1:
        return 0, 0
    
    # Pre-allocate arrays for better performance
    perm = array('i', range(1, n + 1))
    count = array('i', [0] * n)
    max_flips = 0
    checksum = 0
    perm_sign = 1
    r = n
    
    while True:
        # Count flips for current permutation
        flips = 0
        k = perm[0]
        while k != 1:
            # Reverse first k elements in-place
            i, j = 1, k - 1
            while i < j:
                perm[i], perm[j] = perm[j], perm[i]
                i += 1
                j -= 1
            flips += 1
            k = perm[0]
        
        # Update max_flips and checksum
        max_flips = max(max_flips, flips)
        checksum += perm_sign * flips
        
        # Generate next permutation using Johnson-Trotter algorithm
        while r != 1 and count[r - 1] == r - 1:
            count[r - 1] = 0
            r -= 1
        
        if r == 1:
            break
            
        pos = r - 1
        count[pos] += 1
        
        # Swap elements to generate next permutation
        if perm_sign == 1:
            perm[0], perm[pos] = perm[pos], perm[0]
        else:
            perm[pos - 1], perm[pos] = perm[pos], perm[pos - 1]
        
        perm_sign = -perm_sign
        
        # Reset for next iteration
        if r < n:
            r += 1
    
    return max_flips, checksum

def fannkuch_itertools(n):
    """
    Alternative implementation using itertools for clarity,
    though less efficient for large n due to generating all permutations.
    """
    if n < 1:
        return 0, 0
    
    max_flips = 0
    checksum = 0
    
    for i, perm in enumerate(itertools.permutations(range(1, n + 1))):
        current = list(perm)
        flips = 0
        
        while current[0] != 1:
            k = current[0]
            # Reverse first k elements
            current[1:k] = current[k - 1:0:-1]
            flips += 1
        
        max_flips = max(max_flips, flips)
        checksum += flips if i % 2 == 0 else -flips
    
    return max_flips, checksum

def main():
    if len(sys.argv) != 2:
        print("Usage: python fannkuch.py <n>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: n must be an integer")
        sys.exit(1)
    
    if n < 0 or n > 12:
        print("Error: n must be between 0 and 12")
        sys.exit(1)
    
    # Use the optimized implementation
    max_flips, checksum = fannkuch(n)
    
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")

if __name__ == "__main__":
    main()