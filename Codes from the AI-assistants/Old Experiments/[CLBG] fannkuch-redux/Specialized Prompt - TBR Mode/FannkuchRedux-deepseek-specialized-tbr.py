import sys
import itertools
from multiprocessing import Pool, cpu_count

def fannkuch_slice(args):
    n, start, end = args
    max_flips = 0
    checksum = 0
    
    # Generate permutations in our slice
    perm = list(range(1, n + 1))
    indices = list(range(n))
    cycles = list(range(n, 0, -1))
    
    # Skip to our starting position
    for _ in range(start):
        # Use Heap's algorithm to generate permutations efficiently
        i = 0
        while i < n and cycles[i] == 1:
            cycles[i] = n - i
            i += 1
        if i >= n:
            break
            
        cycles[i] -= 1
        j = 0 if i % 2 == 0 else cycles[i]
        indices[i], indices[j] = indices[j], indices[i]
    
    # Process our slice of permutations
    for count in range(start, end):
        # Calculate flips for current permutation
        if indices[0] != 0:  # Skip if first element is 1 (no flips needed)
            perm = [indices[i] + 1 for i in range(n)]
            flips = 0
            k = perm[0]
            
            while k != 1:
                # Reverse first k elements
                i, j = 0, k - 1
                while i < j:
                    perm[i], perm[j] = perm[j], perm[i]
                    i += 1
                    j -= 1
                flips += 1
                k = perm[0]
            
            if flips > max_flips:
                max_flips = flips
            
            checksum += flips if count % 2 == 0 else -flips
        
        # Generate next permutation using Heap's algorithm
        i = 0
        while i < n and cycles[i] == 1:
            cycles[i] = n - i
            i += 1
        if i >= n:
            break
            
        cycles[i] -= 1
        j = 0 if i % 2 == 0 else cycles[i]
        indices[i], indices[j] = indices[j], indices[i]
    
    return max_flips, checksum

def fannkuch_redux(n):
    if n <= 0:
        return 0, 0
    
    total_permutations = 1
    for i in range(2, n + 1):
        total_permutations *= i
    
    # Use multiprocessing for parallel computation
    num_workers = min(cpu_count(), total_permutations)
    chunk_size = max(1, total_permutations // (num_workers * 4))
    
    tasks = []
    start = 0
    while start < total_permutations:
        end = min(start + chunk_size, total_permutations)
        tasks.append((n, start, end))
        start = end
    
    with Pool(processes=num_workers) as pool:
        results = pool.map(fannkuch_slice, tasks)
    
    # Combine results
    max_flips = 0
    checksum = 0
    for local_max, local_checksum in results:
        if local_max > max_flips:
            max_flips = local_max
        checksum += local_checksum
    
    return max_flips, checksum

def main():
    if len(sys.argv) != 2:
        print("Usage: python fannkuch_redux.py <n>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: n must be an integer")
        sys.exit(1)
    
    if n < 0 or n > 12:
        print("Warning: n should be between 0 and 12 for reasonable performance")
    
    max_flips, checksum = fannkuch_redux(n)
    
    print(f"{checksum}")
    print(f"Pfannkuchen({n}) = {max_flips}")

if __name__ == "__main__":
    main()