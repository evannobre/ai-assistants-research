#!/usr/bin/env python3
"""
Fannkuch-Redux benchmark implementation.
Optimized for performance while maintaining readability and correctness.
"""

import sys
from array import array


def fannkuch(n):
    """
    Compute the fannkuch-redux benchmark for n.
    
    Args:
        n: The size of the permutation
        
    Returns:
        Tuple of (checksum, max_flips)
    """
    # Use array for better memory efficiency and cache locality
    perm = array('i', range(n))
    perm1 = array('i', range(n))
    count = array('i', range(n))
    
    max_flips = 0
    checksum = 0
    perm_count = 0
    sign = 1
    
    while True:
        # Count flips for current permutation
        flips = count_flips(perm1, perm, n)
        
        if flips:
            checksum += sign * flips
            max_flips = max(max_flips, flips)
        
        # Generate next permutation using Heap's algorithm (optimized)
        sign = -sign
        perm_count += 1
        
        # Find the rightmost position to increment
        k = 0
        while k < n:
            count[k] -= 1
            if count[k] > 0:
                break
            count[k] = k + 1
            k += 1
        
        if k >= n:
            break
        
        # Rotate elements
        perm_0 = perm1[0]
        for i in range(k):
            perm1[i] = perm1[i + 1]
        perm1[k] = perm_0
    
    return checksum, max_flips


def count_flips(perm1, perm, n):
    """
    Count the number of flips needed to sort the permutation.
    
    Args:
        perm1: Working permutation array
        perm: Original permutation array
        n: Size of permutation
        
    Returns:
        Number of flips
    """
    # Copy perm to perm1 for manipulation
    for i in range(n):
        perm1[i] = perm[i]
    
    flips = 0
    k = perm1[0]
    
    # Continue flipping while first element is not 0 (representing 1)
    while k:
        # Reverse the first k+1 elements
        k2 = (k + 1) >> 1  # Equivalent to (k + 1) // 2
        for i in range(k2):
            temp = perm1[i]
            perm1[i] = perm1[k - i]
            perm1[k - i] = temp
        
        flips += 1
        k = perm1[0]
    
    return flips


def fannkuch_optimized(n):
    """
    Highly optimized version using direct array manipulation.
    This version generates permutations inline and minimizes function calls.
    """
    # Initialize arrays
    perm = array('i', range(n))
    count = array('i', [0] * n)
    
    max_flips = 0
    checksum = 0
    sign = 1
    
    # Initialize count array
    for i in range(n):
        count[i] = i + 1
    
    while True:
        # Inline flip counting for better performance
        flips = 0
        k = perm[0]
        
        if k:  # Only count if first element is not 0
            # Create a copy for flipping
            perm_copy = array('i', perm)
            
            while k:
                # Reverse first k+1 elements
                k2 = (k + 1) >> 1
                for i in range(k2):
                    temp = perm_copy[i]
                    perm_copy[i] = perm_copy[k - i]
                    perm_copy[k - i] = temp
                
                flips += 1
                k = perm_copy[0]
            
            checksum += sign * flips
            max_flips = max(max_flips, flips)
        
        # Generate next permutation
        sign = -sign
        
        # Heap's algorithm for permutation generation
        done = True
        k = 0
        while k < n:
            count[k] -= 1
            if count[k] > 0:
                done = False
                break
            count[k] = k + 1
            k += 1
        
        if done:
            break
        
        # Rotate elements 0 to k
        perm_0 = perm[0]
        for i in range(k):
            perm[i] = perm[i + 1]
        perm[k] = perm_0
    
    return checksum, max_flips


def main():
    """Main entry point for the program."""
    if len(sys.argv) < 2:
        print("Usage: python3 fannkuch_redux.py <n>")
        print("Example: python3 fannkuch_redux.py 12")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n < 1:
            raise ValueError("n must be positive")
    except ValueError as e:
        print(f"Error: Invalid input - {e}")
        sys.exit(1)
    
    # Run the benchmark
    checksum, max_flips = fannkuch_optimized(n)
    
    # Output in the required format
    print(f"{checksum}")
    print(f"Pfannkuchen({n}) = {max_flips}")


if __name__ == "__main__":
    main()