#!/usr/bin/env python3
"""
Fannkuch-redux using numpy for better performance
"""

import sys
import time
import numpy as np
from numba import jit

@jit(nopython=True, cache=True)
def calculate_flips(perm):
    """Calculate number of flips for a permutation"""
    flips = 0
    first = perm[0]
    
    if first == 0:
        return flips
    
    # Working copy
    work_perm = perm.copy()
    k = first
    
    while k:
        # Reverse first k elements
        i = 0
        j = k
        while i < j:
            work_perm[i], work_perm[j] = work_perm[j], work_perm[i]
            i += 1
            j -= 1
        flips += 1
        k = work_perm[0]
    
    return flips

@jit(nopython=True, cache=True)
def fannkuch_numba(n):
    """Optimized fannkuch implementation using Numba"""
    perm = np.arange(n, dtype=np.int32)
    count = np.zeros(n, dtype=np.int32)
    
    max_flips = 0
    checksum = 0
    perm_sign = 1
    r = n
    
    while True:
        while r != 1:
            count[r - 1] = r
            r -= 1
        
        flips = calculate_flips(perm)
        
        if flips > max_flips:
            max_flips = flips
        
        checksum += perm_sign * flips
        
        while True:
            if r == n:
                return max_flips, checksum
            
            perm0 = perm[0]
            i = 0
            while i < r:
                j = i + 1
                perm[i] = perm[j]
                i = j
            perm[r] = perm0
            
            count[r] -= 1
            if count[r] > 0:
                break
            
            r += 1
            perm_sign = -perm_sign

def main_numpy():
    if len(sys.argv) != 2:
        print("Usage: python fannkuch_numpy.py <n>")
        sys.exit(1)
    
    n = int(sys.argv[1])
    
    start_time = time.time()
    max_flips, checksum = fannkuch_numba(n)
    end_time = time.time()
    
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")
    print(f"Time: {end_time - start_time:.3f} seconds")

if __name__ == "__main__":
    main_numpy()