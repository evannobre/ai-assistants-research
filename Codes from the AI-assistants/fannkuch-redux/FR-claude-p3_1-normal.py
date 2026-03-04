#!/usr/bin/env python3
"""
Fannkuch-Redux benchmark
Usage: python fannkuch.py <n>
"""

import sys
from array import array


def fannkuch(n):
    """
    Compute fannkuch-redux for permutations of size n.
    Returns: (checksum, max_flips)
    """
    # Initialize permutations
    perm = array('i', range(n))
    perm1 = array('i', range(n))
    count = array('i', range(n))
    
    max_flips = 0
    checksum = 0
    perm_count = 0
    sign = 1
    
    while True:
        # Count flips for current permutation
        flips = 0
        first = perm1[0]
        
        if first != 0:
            # Copy perm1 to perm for flipping
            perm[:] = perm1
            
            while True:
                flips += 1
                # Reverse first 'first+1' elements
                i, j = 1, first
                while i < j:
                    perm[i], perm[j] = perm[j], perm[i]
                    i += 1
                    j -= 1
                
                first = perm[0]
                if first == 0:
                    break
            
            if flips > max_flips:
                max_flips = flips
            
            checksum += sign * flips
        
        # Generate next permutation
        if perm_count >= n:
            break
            
        if perm_count < n:
            sign = -sign
            perm_count += 1
        
        # Generate next permutation using counting algorithm
        done = False
        k = 1
        while k < n:
            count[k] -= 1
            if count[k] > 0:
                break
            
            if k == n - 1:
                done = True
                break
            
            count[k] = k + 1
            
            # Rotate first k+1 elements
            tmp = perm1[0]
            for i in range(k + 1):
                perm1[i] = perm1[i + 1]
            perm1[k + 1] = tmp
            
            k += 1
        
        if done:
            break
    
    return checksum, max_flips


def main():
    if len(sys.argv) < 2:
        print("Usage: python fannkuch.py <n>")
        sys.exit(1)
    
    n = int(sys.argv[1])
    
    if n < 3 or n > 12:
        print("n must be between 3 and 12")
        sys.exit(1)
    
    checksum, max_flips = fannkuch(n)
    
    print(f"{checksum}")
    print(f"Pfannkuchen({n}) = {max_flips}")


if __name__ == "__main__":
    main()