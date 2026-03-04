import itertools
from numba import jit
import numpy as np

@jit(nopython=True)
def fannkuch_flips_count(perm):
    """Count flips for a single permutation"""
    n = len(perm)
    count = 0
    first = perm[0]
    
    if first == 0:
        return count
    
    # Create a mutable copy for flipping
    current = perm.copy()
    
    while current[0] != 0:
        k = current[0] + 1
        # Reverse first k elements
        for i in range(k // 2):
            current[i], current[k - 1 - i] = current[k - 1 - i], current[i]
        count += 1
    
    return count

def fannkuch_redux(n):
    """Main Fannkuch-redux algorithm"""
    max_flips = 0
    checksum = 0
    
    # Generate permutations using itertools
    for i, perm in enumerate(itertools.permutations(range(n))):
        perm_array = np.array(perm, dtype=np.int32)
        flips = fannkuch_flips_count(perm_array)
        
        if flips > max_flips:
            max_flips = flips
        
        if i % 2 == 0:
            checksum += flips
        else:
            checksum -= flips
    
    return max_flips, checksum

# Example usage
if __name__ == "__main__":
    n = 7
    max_flips, checksum = fannkuch_redux(n)
    print(f"Pfannkuchen({n}) = {max_flips}")
    print(f"Checksum = {checksum}")