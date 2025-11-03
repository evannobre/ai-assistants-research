#!/usr/bin/env python3
"""
Fannkuch-redux benchmark implementation.
Optimized for performance using native Python operations and best practices.

Usage: python3 fannkuch_redux.py <n>
Example: python3 fannkuch_redux.py 12
"""

import sys
from typing import List, Tuple


def flip_count(perm: List[int]) -> int:
    """
    Count the number of flips needed to bring 1 to the front.
    Uses in-place reversal for memory efficiency.
    
    Args:
        perm: A permutation list (will be modified)
    
    Returns:
        Number of flips performed
    """
    flips = 0
    first = perm[0]
    
    while first != 1:
        # Reverse the first 'first' elements in-place
        # Using slice assignment for native Python optimization
        perm[:first] = perm[:first][::-1]
        flips += 1
        first = perm[0]
    
    return flips


def fannkuch(n: int) -> Tuple[int, int]:
    """
    Calculate fannkuch-redux for all permutations of size n.
    
    This implementation uses an optimized permutation generation algorithm
    that generates permutations in-place, avoiding excessive memory allocation.
    
    Args:
        n: The size of permutations to generate
    
    Returns:
        Tuple of (checksum, max_flips)
    """
    # Initialize permutation arrays
    perm = list(range(1, n + 1))      # Current permutation
    perm1 = list(range(1, n + 1))     # Working copy for flipping
    count = [0] * n                    # Count array for permutation generation
    
    max_flips = 0
    checksum = 0
    perm_index = 0
    sign = 1
    
    while True:
        # Create a working copy for flipping (avoid modifying original)
        perm1[:] = perm
        
        # Count flips for current permutation
        flips = flip_count(perm1)
        
        # Update max flips
        if flips > max_flips:
            max_flips = flips
        
        # Update checksum with alternating sign
        checksum += sign * flips
        sign = -sign
        
        # Generate next permutation using Heap's algorithm (optimized)
        # This generates permutations in-place with O(1) per permutation
        k = 0
        while k < n:
            if count[k] < k:
                # Swap based on parity
                if k % 2 == 0:
                    perm[0], perm[k] = perm[k], perm[0]
                else:
                    perm[count[k]], perm[k] = perm[k], perm[count[k]]
                
                count[k] += 1
                break
            else:
                count[k] = 0
                k += 1
        else:
            # All permutations generated
            break
        
        perm_index += 1
    
    return checksum, max_flips


def main():
    """
    Main entry point for the fannkuch-redux program.
    Follows best practices with proper error handling and validation.
    """
    # Input validation
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <n>", file=sys.stderr)
        print("Example: python3 fannkuch_redux.py 12", file=sys.stderr)
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print(f"Error: Argument must be an integer", file=sys.stderr)
        sys.exit(1)
    
    # Validate range
    if n < 1:
        print(f"Error: n must be at least 1", file=sys.stderr)
        sys.exit(1)
    
    if n > 13:
        print(f"Warning: n={n} will take significant time and memory", file=sys.stderr)
    
    # Calculate fannkuch-redux
    checksum, max_flips = fannkuch(n)
    
    # Output results in standard format
    print(f"{checksum}")
    print(f"Pfannkuchen({n}) = {max_flips}")


if __name__ == "__main__":
    main()