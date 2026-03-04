import sys
import numpy as np
from numba import jit  # Optional: Use for JIT compilation
from concurrent.futures import ThreadPoolExecutor

@jit(nopython=True)
def count_flips_numba(perm):
    """JIT-compiled function for counting flips"""
    n = len(perm)
    flips = 0
    
    # Create a copy to work with
    temp = perm.copy()
    k = temp[0]
    
    while k != 0:
        # Reverse first k+1 elements
        i = 0
        j = k
        while i < j:
            temp[i], temp[j] = temp[j], temp[i]
            i += 1
            j -= 1
        flips += 1
        k = temp[0]
    
    return flips

def fannkuch_numpy(n):
    """Using NumPy for vectorized operations"""
    try:
        import numpy as np
        
        # Generate all permutations at once (memory intensive for large n)
        if n <= 10:  # Adjust based on available memory
            perms = np.array(list(itertools.permutations(range(n))))
            
            # Vectorized flip counting
            max_flips = 0
            checksum = 0
            
            for perm in perms:
                flips = count_flips_numba(perm)
                if flips > max_flips:
                    max_flips = flips
                checksum += flips if flips % 2 == 0 else -flips
            
            return max_flips, checksum
    except ImportError:
        pass
    
    # Fall back to standard algorithm
    return fannkuch_redux(n)

def generate_permutations_heap(n):
    """Heap's algorithm for generating permutations without storing them all"""
    a = list(range(n))
    c = [0] * n
    i = 0
    
    yield a.copy()
    
    while i < n:
        if c[i] < i:
            if i % 2 == 0:
                a[0], a[i] = a[i], a[0]
            else:
                a[c[i]], a[i] = a[i], a[c[i]]
            yield a.copy()
            c[i] += 1
            i = 0
        else:
            c[i] = 0
            i += 1

def fannkuch_iterative(n):
    """Iterative approach using Heap's algorithm"""
    max_flips = 0
    checksum = 0
    
    for perm in generate_permutations_heap(n):
        flips = 0
        k = perm[0]
        
        if k != 0:
            # Work on a copy
            temp = perm.copy()
            
            while k:
                # Reverse first k+1 elements efficiently
                temp[:k+1] = temp[k::-1]
                flips += 1
                k = temp[0]
        
        # Update results
        if flips > max_flips:
            max_flips = flips
        checksum += flips if flips % 2 == 0 else -flips
    
    return max_flips, checksum

# Choose implementation based on available libraries
def fannkuch(n, use_numpy=False):
    if use_numpy:
        try:
            import numpy as np
            return fannkuch_numpy(n)
        except:
            pass
    
    # For n > 10, use parallel processing
    if n > 10:
        return fannkuch_redux(n)
    else:
        return fannkuch_iterative(n)