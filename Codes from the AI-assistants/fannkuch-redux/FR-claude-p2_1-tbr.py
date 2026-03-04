#!/usr/bin/env python3
"""
Fannkuch-redux algorithm implementation
Optimized for performance using native Python operations
"""

def fannkuch(n):
    """
    Compute fannkuch-redux for a given n
    Returns: (max_flips, checksum)
    """
    # Initialize permutation arrays
    perm = list(range(n))
    perm1 = list(range(n))
    count = list(range(n, 0, -1))
    
    max_flips = 0
    checksum = 0
    sign = 1
    perm_count = 0
    
    while True:
        # Count flips for current permutation
        flips = 0
        k = perm[0]
        
        if k != 0:
            # Copy permutation for flipping
            perm2 = perm[:]
            
            while k != 0:
                # Reverse first k+1 elements
                perm2[:k+1] = perm2[k::-1]
                flips += 1
                k = perm2[0]
            
            max_flips = max(max_flips, flips)
            checksum += sign * flips
        
        sign = -sign
        
        # Generate next permutation
        if not next_permutation(perm, count):
            break
    
    return max_flips, checksum


def next_permutation(perm, count):
    """
    Generate next permutation in-place using counting algorithm
    Returns False when all permutations are exhausted
    """
    n = len(perm)
    i = 1
    
    while i < n:
        # Rotate first i+1 elements
        first = perm[0]
        for j in range(i):
            perm[j] = perm[j + 1]
        perm[i] = first
        
        count[i] -= 1
        if count[i] > 0:
            return True
        
        count[i] = i + 1
        i += 1
    
    return False


if __name__ == "__main__":
    import sys
    
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    
    if n < 3 or n > 12:
        print("Please provide n between 3 and 12")
        sys.exit(1)
    
    max_flips, checksum = fannkuch(n)
    
    print(f"{checksum}")
    print(f"Pfannkuchen({n}) = {max_flips}")