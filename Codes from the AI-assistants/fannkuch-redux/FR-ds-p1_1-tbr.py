import sys
import itertools
import array
from collections import deque
from multiprocessing import Pool, cpu_count

def fannkuch_worker(args):
    """Worker function for parallel processing"""
    n, chunk_start, chunk_size = args
    max_flips = 0
    checksum = 0
    
    # Generate permutation indices for this chunk
    perm = list(range(n))
    count = list(range(n))
    
    # Move to starting position
    for i in range(chunk_start):
        # Generate next permutation
        for j in range(1, n):
            rotate_index = count[j]
            if rotate_index == 0:
                continue
            perm[:j+1] = perm[rotate_index:j+1] + perm[:rotate_index]
            count[j] = 0
            break
        else:
            break
    
    # Process chunk
    for _ in range(chunk_size):
        # Calculate flips
        k = perm[0]
        if k > 0:
            temp_perm = array.array('i', perm)
            flips = 0
            
            while k:
                # Reverse first k elements
                i, j = 0, k
                while i < j:
                    temp_perm[i], temp_perm[j] = temp_perm[j], temp_perm[i]
                    i += 1
                    j -= 1
                flips += 1
                k = temp_perm[0]
            
            # Update results
            if flips > max_flips:
                max_flips = flips
            checksum += flips if flips % 2 == 0 else -flips
        
        # Generate next permutation
        for j in range(1, n):
            rotate_index = count[j]
            if rotate_index == 0:
                continue
            perm[:j+1] = perm[rotate_index:j+1] + perm[:rotate_index]
            count[j] = 0
            break
        else:
            break
    
    return max_flips, checksum

def fannkuch_redux(n):
    """Main Fannkuch-redux algorithm"""
    total_permutations = 1
    for i in range(2, n + 1):
        total_permutations *= i
    
    # Determine chunk size for parallel processing
    num_workers = cpu_count()
    chunk_size = max(10000, total_permutations // (num_workers * 10))
    
    # Prepare work chunks
    chunks = []
    start = 0
    while start < total_permutations:
        current_chunk_size = min(chunk_size, total_permutations - start)
        chunks.append((n, start, current_chunk_size))
        start += current_chunk_size
    
    # Process in parallel
    max_flips = 0
    checksum = 0
    
    with Pool(processes=num_workers) as pool:
        results = pool.map(fannkuch_worker, chunks)
    
    # Combine results
    for worker_max_flips, worker_checksum in results:
        if worker_max_flips > max_flips:
            max_flips = worker_max_flips
        checksum += worker_checksum
    
    return max_flips, checksum

def main():
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 7  # Default value
    
    max_flips, checksum = fannkuch_redux(n)
    print(f"{max_flips}\nPfannkuchen({n}) = {checksum}")

if __name__ == "__main__":
    main()