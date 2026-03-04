#!/usr/bin/env python3
"""
Fannkuch-Redux Algorithm Implementation
Calculates checksum and max flips for all permutations of {1,...,n}
"""

import sys
from array import array


def fannkuch(n):
    """
    Calculate fannkuch-redux for n elements.
    Returns: (checksum, max_flips)
    """
    # Use array for better memory efficiency and performance
    perm = array('b', range(n))
    perm1 = array('b', range(n))
    count = array('b', range(n))
    
    max_flips = 0
    checksum = 0
    perm_sign = 1
    perm_count = 0
    
    while True:
        # Copy current permutation for flipping
        for i in range(n):
            perm1[i] = perm[i]
        
        flips = 0
        k = perm1[0]
        
        # Flip until first element is 0 (representing 1)
        while k != 0:
            # Reverse first k+1 elements
            k2 = (k + 1) >> 1
            for i in range(k2):
                perm1[i], perm1[k - i] = perm1[k - i], perm1[i]
            
            flips += 1
            k = perm1[0]
        
        # Update max flips
        if flips > max_flips:
            max_flips = flips
        
        # Update checksum with sign based on permutation index
        checksum += perm_sign * flips
        perm_sign = -perm_sign
        perm_count += 1
        
        # Generate next permutation using counting algorithm
        # This is Heap's algorithm optimized for sequential generation
        k = 1
        while k < n:
            count[k] -= 1
            if count[k] >= 0:
                break
            count[k] = k
            k += 1
        
        if k >= n:
            break
        
        # Rotate first k+1 elements
        tmp = perm[0]
        for i in range(k):
            perm[i] = perm[i + 1]
        perm[k] = tmp
        
        # Toggle sign for even k (adjusting for alternating pattern)
        if k % 2 == 0:
            perm_sign = -perm_sign
    
    return checksum, max_flips


def fannkuch_optimized(n):
    """
    Optimized version with inline operations for better performance.
    """
    # Initialize arrays
    perm = list(range(n))
    perm1 = [0] * n
    count = [0] * n
    
    max_flips = 0
    checksum = 0
    sign = 1
    
    while True:
        # Count flips for current permutation
        k = perm[0]
        if k > 0:
            # Copy permutation
            for i in range(n):
                perm1[i] = perm[i]
            
            flips = 0
            while True:
                # Reverse first k+1 elements
                for i in range((k + 1) >> 1):
                    perm1[i], perm1[k - i] = perm1[k - i], perm1[i]
                
                flips += 1
                k = perm1[0]
                if k == 0:
                    break
            
            if flips > max_flips:
                max_flips = flips
            
            checksum += sign * flips
        
        # Toggle sign
        sign = -sign
        
        # Generate next permutation (Heap's algorithm)
        done = True
        k = 1
        while k < n:
            if count[k] < k:
                if k & 1:  # k is odd
                    perm[0], perm[k] = perm[k], perm[0]
                else:  # k is even
                    perm[count[k]], perm[k] = perm[k], perm[count[k]]
                
                count[k] += 1
                done = False
                break
            else:
                count[k] = 0
                k += 1
        
        if done:
            break
    
    return checksum, max_flips


def main():
    if len(sys.argv) < 2:
        print("Usage: python fannkuch_redux.py <n>")
        print("Example: python fannkuch_redux.py 12")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n < 1:
            raise ValueError("n must be positive")
        if n > 13:
            print(f"Warning: n={n} may take a very long time (13! = 6 billion permutations)")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    checksum, max_flips = fannkuch_optimized(n)
    
    print(f"{checksum}")
    print(f"Pfannkuchen({n}) = {max_flips}")


if __name__ == "__main__":
    main()