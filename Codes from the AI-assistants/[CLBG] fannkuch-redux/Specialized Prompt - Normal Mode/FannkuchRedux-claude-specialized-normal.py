#!/usr/bin/env python3
"""
Fannkuch-Redux Algorithm Implementation
Optimized for performance using native Python operations
"""

import sys
from typing import Tuple


def fannkuch(n: int) -> Tuple[int, int]:
    """
    Calculate the fannkuch-redux benchmark for permutations of size n.
    
    Args:
        n: Size of the permutation (typically 7-12 for benchmarking)
    
    Returns:
        Tuple of (checksum, max_flips)
    """
    # Initialize counters
    max_flips = 0
    checksum = 0
    perm_index = 0
    
    # Working arrays - use list for O(1) reversal via slicing
    perm = list(range(n))
    count = list(range(n))
    
    while True:
        # Count flips for current permutation
        flips = count_flips(perm[:])  # Pass a copy
        
        # Update checksum with alternating sign
        if perm_index % 2 == 0:
            checksum += flips
        else:
            checksum -= flips
        
        # Track maximum flips
        if flips > max_flips:
            max_flips = flips
        
        # Generate next permutation using counting algorithm
        # This is more efficient than generating all permutations upfront
        k = 1
        while k < n:
            # Rotate first k+1 elements
            first = perm[0]
            for i in range(k):
                perm[i] = perm[i + 1]
            perm[k] = first
            
            count[k] -= 1
            if count[k] > 0:
                break
            
            count[k] = k + 1
            k += 1
        else:
            # All permutations generated
            break
        
        perm_index += 1
    
    return checksum, max_flips


def count_flips(perm: list) -> int:
    """
    Count the number of flips needed until first element is 0.
    
    Args:
        perm: Current permutation (will be modified)
    
    Returns:
        Number of flips performed
    """
    flips = 0
    first = perm[0]
    
    # Continue flipping while first element is not 0
    while first != 0:
        # Reverse first (first+1) elements using Python's efficient slicing
        # This is O(k) where k is the number of elements to reverse
        perm[:first + 1] = perm[:first + 1][::-1]
        
        flips += 1
        first = perm[0]
    
    return flips


def main():
    """Main entry point for the program."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <n>", file=sys.stderr)
        print("Where n is typically between 7 and 12 for benchmarking", file=sys.stderr)
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n < 1:
            raise ValueError("n must be positive")
        if n > 13:
            print("Warning: n > 13 may take very long time and consume significant memory", 
                  file=sys.stderr)
    except ValueError as e:
        print(f"Error: Invalid argument - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate fannkuch
    checksum, max_flips = fannkuch(n)
    
    # Output results in the expected format
    print(f"{checksum}")
    print(f"Pfannkuchen({n}) = {max_flips}")


if __name__ == "__main__":
    main()