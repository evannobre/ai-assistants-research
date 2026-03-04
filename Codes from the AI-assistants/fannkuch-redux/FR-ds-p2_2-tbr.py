#!/usr/bin/env python3
"""
Minimal optimized Fannkuch-Redux for benchmarking
"""

import sys
import array

def fannkuch(n):
    if n < 1:
        return 0, 0
    
    perm = array.array('B', list(range(n)))
    perm1 = array.array('B', list(range(n)))
    count = array.array('I', [0] * n)
    
    max_flips = 0
    checksum = 0
    r = n
    
    while True:
        while r != 1:
            count[r-1] = r
            r -= 1
        
        if perm1[0] != 0 and perm1[0] != n-1:
            # Copy to working array
            perm[:] = perm1
            
            # Count flips
            flips = 0
            k = perm[0]
            while k:
                # Reverse first k+1 elements
                i, j = 0, k
                while i < j:
                    perm[i], perm[j] = perm[j], perm[i]
                    i += 1
                    j -= 1
                flips += 1
                k = perm[0]
            
            max_flips = max(max_flips, flips)
            checksum += flips if (perm1[0] % 2 == 0) else -flips
        
        # Generate next permutation
        while True:
            if r == n:
                return checksum, max_flips
            
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

def main():
    if len(sys.argv) != 2:
        print("Usage: python fannkuch_minimal.py <n>")
        sys.exit(1)
    
    n = int(sys.argv[1])
    checksum, max_flips = fannkuch(n)
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")

if __name__ == "__main__":
    main()