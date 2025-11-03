import itertools
from multiprocessing import Pool, cpu_count
import sys

def fannkuch_slice(n, start, end):
    """Process a slice of permutations from start to end"""
    max_flips = 0
    checksum = 0
    
    # Generate permutations using native itertools
    count = [0] * n
    perm = list(range(n))
    
    # Skip to starting permutation
    for i in range(start):
        # Generate next permutation in lexicographic order
        j = 1
        while j < n and count[j] >= j:
            count[j] = 0
            j += 1
        if j >= n:
            break
        count[j] += 1
        perm[:j+1] = perm[j::-1]
    
    # Process the slice
    for idx in range(start, end):
        # Calculate flips for current permutation
        first = perm[0]
        if first > 0:
            flips = 0
            temp_perm = perm.copy()
            k = first
            while k:
                # Reverse first k+1 elements
                temp_perm[:k+1] = temp_perm[k::-1]
                flips += 1
                k = temp_perm[0]
            
            if flips > max_flips:
                max_flips = flips
            
            checksum += flips if (idx % 2 == 0) else -flips
        
        # Generate next permutation
        j = 1
        while j < n and count[j] >= j:
            count[j] = 0
            j += 1
        if j >= n:
            break
        count[j] += 1
        perm[:j+1] = perm[j::-1]
    
    return max_flips, checksum

def fannkuch_redux(n):
    if n < 0 or n > 12:  # Practical limit for this approach
        raise ValueError("n must be between 0 and 12")
    
    if n == 0:
        return 0, 0
    
    # Use multiprocessing for parallel computation
    num_workers = cpu_count()
    total_perms = factorial(n)
    chunk_size = max(1, total_perms // (num_workers * 4))
    
    chunks = []
    start = 0
    while start < total_perms:
        end = min(start + chunk_size, total_perms)
        chunks.append((n, start, end))
        start = end
    
    with Pool(num_workers) as pool:
        results = pool.starmap(fannkuch_slice, chunks)
    
    max_flips = max(r[0] for r in results)
    checksum = sum(r[1] for r in results)
    
    return checksum, max_flips

def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 7
    
    checksum, max_flips = fannkuch_redux(n)
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")