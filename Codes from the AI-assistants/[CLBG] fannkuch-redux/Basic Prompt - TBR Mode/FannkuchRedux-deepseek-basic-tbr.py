import sys
import itertools
from functools import lru_cache

def fannkuch(n):
    if n == 0:
        return (0, 0)
    
    max_flips = 0
    checksum = 0
    sign = 1
    
    # Generate permutations using itertools - this is memory efficient
    for i, perm in enumerate(itertools.permutations(range(1, n + 1))):
        current_perm = list(perm)
        flips_count = 0
        
        # Count flips for current permutation
        while current_perm[0] != 1:
            k = current_perm[0]
            # Reverse first k elements efficiently using slicing
            current_perm[:k] = current_perm[k-1::-1]
            flips_count += 1
        
        # Update max flips and checksum
        if flips_count > max_flips:
            max_flips = flips_count
        
        checksum += sign * flips_count
        sign = -sign
    
    return (max_flips, checksum)

def fannkuch_optimized(n):
    """Optimized version that reduces function calls and uses efficient algorithms"""
    if n == 0:
        return (0, 0)
    
    max_flips = 0
    checksum = 0
    
    # Use efficient permutation generation
    for i, perm in enumerate(itertools.permutations(range(n))):
        # Convert to 1-based indexing
        perm_array = [x + 1 for x in perm]
        flips_count = 0
        first_element = perm_array[0]
        
        while first_element != 1:
            # Reverse the first 'first_element' elements
            left, right = 1, first_element - 1
            while left < right:
                perm_array[left-1], perm_array[right-1] = perm_array[right-1], perm_array[left-1]
                left += 1
                right -= 1
            flips_count += 1
            first_element = perm_array[0]
        
        if flips_count > max_flips:
            max_flips = flips_count
        
        if i % 2 == 0:
            checksum += flips_count
        else:
            checksum -= flips_count
    
    return (max_flips, checksum)

def fannkuch_fastest(n):
    """Fastest version using iterative permutation generation without itertools"""
    if n == 0:
        return (0, 0)
    
    max_flips = 0
    checksum = 0
    perm = list(range(1, n + 1))
    count = [0] * n
    i = 0
    perm_index = 0
    
    while True:
        # Count flips for current permutation
        flips_count = 0
        temp_perm = perm.copy()
        first = temp_perm[0]
        
        while first != 1:
            # Reverse first 'first' elements
            k = first
            left, right = 0, k - 1
            while left < right:
                temp_perm[left], temp_perm[right] = temp_perm[right], temp_perm[left]
                left += 1
                right -= 1
            flips_count += 1
            first = temp_perm[0]
        
        # Update statistics
        if flips_count > max_flips:
            max_flips = flips_count
        
        if perm_index % 2 == 0:
            checksum += flips_count
        else:
            checksum -= flips_count
        
        # Generate next permutation using Johnson-Trotter algorithm
        i = 1
        while i < n and count[i] >= i:
            count[i] = 0
            i += 1
        
        if i >= n:
            break
            
        count[i] += 1
        
        # Swap elements to generate next permutation
        j = 0
        if i % 2 == 1:
            j = count[i]
        perm[j], perm[i] = perm[i], perm[j]
        perm_index += 1
    
    return (max_flips, checksum)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 7  # Default for testing
    
    # Use the fastest implementation for n >= 10
    if n <= 8:
        max_flips, checksum = fannkuch(n)
    else:
        max_flips, checksum = fannkuch_fastest(n)
    
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")