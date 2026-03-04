import numpy as np
import sys
from itertools import permutations
from functools import lru_cache

def fannkuch_numpy(n: int) -> Tuple[int, int]:
    """
    NumPy optimized version - much faster for larger n
    """
    if n <= 0:
        return 0, 0
    
    max_flips = 0
    checksum = 0
    
    # Generate permutations using numpy if n is small enough
    if n <= 10:
        # Generate all permutations at once
        perms = np.array(list(permutations(range(n))))
        
        for perm in perms:
            perm = perm.copy()
            first = perm[0]
            if first == 0:
                continue
                
            flips = 0
            while first != 0:
                # Reverse the prefix
                perm[:first+1] = perm[first::-1]
                first = perm[0]
                flips += 1
            
            max_flips = max(max_flips, flips)
            checksum += flips if flips % 2 == 0 else -flips
    else:
        # Use iterative algorithm for larger n
        return fannkuch_redux(n)  # Use the first implementation
    
    return max_flips, checksum

def fannkuch_cython_style(n: int) -> Tuple[int, int]:
    """
    Cython-style optimization using Python's array module
    """
    from array import array
    
    perm = array('i', range(n))
    count = array('i', [0] * n)
    max_flips = 0
    checksum = 0
    r = n
    
    while True:
        while r > 1:
            count[r-1] = r
            r -= 1
        
        # Calculate flips
        k = perm[0]
        if k != 0:
            temp_perm = array('i', perm)
            flips = 0
            first = k
            
            while first != 0:
                # Reverse prefix
                i, j = 0, first
                while i < j:
                    temp_perm[i], temp_perm[j] = temp_perm[j], temp_perm[i]
                    i += 1
                    j -= 1
                flips += 1
                first = temp_perm[0]
            
            max_flips = max(max_flips, flips)
            checksum += flips if (perm[0] % 2 == 0) else -flips
        
        # Generate next permutation
        while True:
            if r == n:
                return max_flips, checksum
            
            perm0 = perm[0]
            i = 0
            while i < r:
                perm[i] = perm[i+1]
                i += 1
            perm[r] = perm0
            
            count[r] -= 1
            if count[r] > 0:
                break
            r += 1

# For benchmarking and comparison
def benchmark(n: int):
    """Benchmark different implementations"""
    import time
    
    print(f"\nBenchmark for n={n}")
    print("-" * 40)
    
    # Implementation 1
    start = time.time()
    max1, check1 = fannkuch_redux(n)
    t1 = time.time() - start
    print(f"Algorithm L: {t1:.4f}s, max={max1}, checksum={check1}")
    
    # Implementation 2 (if n <= 10)
    if n <= 10:
        start = time.time()
        max2, check2 = fannkuch_numpy(n)
        t2 = time.time() - start
        print(f"NumPy version: {t2:.4f}s, max={max2}, checksum={check2}")
    
    # Implementation 3
    start = time.time()
    max3, check3 = fannkuch_cython_style(n)
    t3 = time.time() - start
    print(f"Array version: {t3:.4f}s, max={max3}, checksum={check3}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        if len(sys.argv) > 2 and sys.argv[2] == "--benchmark":
            benchmark(n)
        else:
            max_flips, checksum = fannkuch_redux(n)
            print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")
    else:
        # Run with default n=7
        n = 7
        max_flips, checksum = fannkuch_redux(n)
        print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")