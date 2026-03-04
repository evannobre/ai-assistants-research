#!/usr/bin/env python3
"""
Fannkuch-Redux implementation optimized for Ubuntu 24.04.4 64-bit
Memory efficient algorithm using native Python libraries
"""

import sys
import math
import itertools
from typing import Tuple
from multiprocessing import Pool, cpu_count
from functools import partial
import array

def fannkuch_slice(n: int, start_idx: int, chunk_size: int) -> Tuple[int, int]:
    """
    Process a slice of permutations for Fannkuch-Redux.
    Uses array module for memory efficiency and optimized reversal.
    """
    # Pre-compute factorial for permutation generation
    factorials = array.array('I', [1])  # Using unsigned int
    for i in range(1, n + 1):
        factorials.append(factorials[-1] * i)
    
    # Initialize permutation and count arrays
    current = array.array('B', list(range(1, n + 1)))  # Using bytes for small ints
    count = array.array('I', [0] * n)
    
    # Calculate the starting permutation for this slice
    remainder = start_idx
    for i in range(n - 1, 0, -1):
        count[i] = remainder // factorials[i]
        remainder %= factorials[i]
        if count[i]:
            # Rotate the permutation to the correct starting point
            perm_slice = current[i - count[i]:i + 1]
            current[i - count[i]:i + 1] = array.array('B', [perm_slice[-1]] + list(perm_slice[:-1]))
    
    max_flips = 0
    checksum = 0
    
    # Process chunk_size permutations
    for idx in range(start_idx, min(start_idx + chunk_size, factorials[n])):
        # Skip if first element is 1 (no flips needed)
        if current[0] != 1:
            # Make a copy for flipping
            perm = array.array('B', current)
            flips = 0
            
            # Efficient flip calculation with in-place reversal
            while perm[0] != 1:
                k = perm[0]
                # Reverse first k elements using slice assignment
                perm[:k] = perm[k-1::-1]
                flips += 1
            
            max_flips = max(max_flips, flips)
            
            # Update checksum with alternating signs
            if idx % 2 == 0:
                checksum += flips
            else:
                checksum -= flips
        
        # Generate next permutation using Heap's algorithm (optimized)
        i = 1
        while i < n:
            if count[i] < i:
                if i % 2 == 0:
                    current[0], current[i] = current[i], current[0]
                else:
                    current[count[i]], current[i] = current[i], current[count[i]]
                
                count[i] += 1
                i = 1
                break
            else:
                count[i] = 0
                i += 1
    
    return max_flips, checksum

def fannkuch_redux(n: int) -> Tuple[int, int]:
    """
    Main Fannkuch-Redux solver using parallel processing.
    """
    if n < 1:
        return 0, 0
    
    # Calculate total permutations
    total_permutations = math.factorial(n)
    
    # Adjust chunk size based on memory constraints
    # For 8GB RAM, we need to be conservative with memory usage
    available_memory_gb = 8
    safe_memory_per_process_mb = 500  # 500MB per process
    max_processes = max(1, (available_memory_gb * 1024) // safe_memory_per_process_mb)
    
    # Use at most CPU cores - 1 to leave one core free
    cpu_cores = max(1, cpu_count() - 1)
    num_processes = min(max_processes, cpu_cores, 8)  # Cap at 8 processes
    
    # Calculate chunk size (ensuring it's not too small)
    chunk_size = max(1, total_permutations // (num_processes * 100))
    
    # Prepare arguments for parallel processing
    ranges = []
    start = 0
    while start < total_permutations:
        end = min(start + chunk_size, total_permutations)
        ranges.append((n, start, end - start))
        start = end
    
    # Process in parallel if we have multiple chunks
    if len(ranges) > 1:
        with Pool(processes=num_processes) as pool:
            results = pool.starmap(fannkuch_slice, ranges)
    else:
        results = [fannkuch_slice(n, 0, total_permutations)]
    
    # Aggregate results
    max_flips = max(r[0] for r in results)
    checksum = sum(r[1] for r in results)
    
    return checksum, max_flips

def optimized_fannkuch_single(n: int) -> Tuple[int, int]:
    """
    Optimized single-threaded version for smaller n or when memory is tight.
    Uses iterative algorithm with minimal memory overhead.
    """
    if n < 1:
        return 0, 0
    
    # Pre-compute factorials
    factorials = [1]
    for i in range(1, n + 1):
        factorials.append(factorials[-1] * i)
    
    # Initialize arrays using efficient types
    perm = array.array('B', list(range(1, n + 1)))
    perm1 = array.array('B', list(range(1, n + 1)))
    count = array.array('I', [0] * n)
    
    max_flips = 0
    checksum = 0
    total_permutations = factorials[n]
    
    r = n
    while True:
        # Count flips for current permutation
        while r != 1:
            count[r - 1] = r
            r -= 1
        
        # Skip if first element is 1
        if perm1[0] != 0 and perm1[0] != n - 1:
            # Copy permutation
            perm[:] = perm1
            
            # Calculate flips
            flips = 0
            k = perm[0]
            while k:
                # Reverse first k elements efficiently
                left = 0
                right = k
                while left < right:
                    perm[left], perm[right] = perm[right], perm[left]
                    left += 1
                    right -= 1
                flips += 1
                k = perm[0]
            
            max_flips = max(max_flips, flips)
            checksum += flips if (total_permutations - factorials[n]) % 2 == 0 else -flips
        
        # Generate next permutation
        while True:
            if r == n:
                return checksum, max_flips
            
            # Rotate permutation
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
    """
    Main entry point with command-line argument parsing.
    """
    if len(sys.argv) != 2:
        print("Usage: python fannkuch_redux.py <n>")
        print("Example: python fannkuch_redux.py 10")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n < 0 or n > 12:
            print("Warning: n should be between 0 and 12 for reasonable execution time")
            print("Larger values will work but may be slow")
        
        # Choose algorithm based on n and available resources
        if n <= 8 or cpu_count() == 1:
            # Use single-threaded for small n or single-core systems
            checksum, max_flips = optimized_fannkuch_single(n)
        else:
            # Use parallel processing for larger n
            checksum, max_flips = fannkuch_redux(n)
        
        print(f"{checksum}")
        print(f"Pfannkuchen({n}) = {max_flips}")
        
    except ValueError:
        print("Error: n must be an integer")
        sys.exit(1)
    except MemoryError:
        print("Error: Insufficient memory for n =", n)
        print("Try a smaller value or use the single-threaded version")
        sys.exit(1)

if __name__ == "__main__":
    # Set recursion limit and optimize for performance
    sys.setrecursionlimit(1000000)
    main()