#!/usr/bin/env python3
"""
Fannkuch-Redux Algorithm Implementation
Optimized for performance using Python native features
"""

import sys
from itertools import permutations
from multiprocessing import Pool, cpu_count


def count_flips(perm):
    """
    Count the number of flips required for a single permutation.
    
    Args:
        perm: A list representing a permutation
        
    Returns:
        Number of flips needed
    """
    # Work on a copy to avoid modifying the original
    arr = list(perm)
    flips = 0
    
    # Continue flipping until the first element is 1
    while arr[0] != 1:
        k = arr[0]
        # Reverse the first k elements
        arr[:k] = reversed(arr[:k])
        flips += 1
    
    return flips


def fannkuch_worker(perms_chunk):
    """
    Worker function for parallel processing of permutation chunks.
    
    Args:
        perms_chunk: A chunk of permutations to process
        
    Returns:
        Tuple of (max_flips, checksum) for this chunk
    """
    max_flips = 0
    checksum = 0
    
    for idx, perm in perms_chunk:
        flips = count_flips(perm)
        
        # Update checksum (alternate signs based on index)
        checksum += flips if idx % 2 == 0 else -flips
        
        # Track maximum flips
        if flips > max_flips:
            max_flips = flips
    
    return max_flips, checksum


def chunk_iterable(iterable, chunk_size):
    """
    Generator to yield chunks from an iterable.
    
    Args:
        iterable: The iterable to chunk
        chunk_size: Size of each chunk
        
    Yields:
        Lists of items from the iterable
    """
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def fannkuch_redux_parallel(n, num_processes=None):
    """
    Parallel implementation of fannkuch-redux using multiprocessing.
    
    Args:
        n: The number to generate permutations for (1 to n)
        num_processes: Number of processes to use (default: CPU count)
        
    Returns:
        Tuple of (checksum, max_flips)
    """
    if num_processes is None:
        num_processes = cpu_count()
    
    # Generate all permutations with their indices
    base_perm = list(range(1, n + 1))
    indexed_perms = enumerate(permutations(base_perm))
    
    # Calculate chunk size based on factorial(n) / num_processes
    # For memory efficiency, use smaller chunks
    chunk_size = max(1000, 10000 // n)
    
    # Create chunks of permutations
    chunks = chunk_iterable(indexed_perms, chunk_size)
    
    # Process chunks in parallel
    with Pool(processes=num_processes) as pool:
        results = pool.map(fannkuch_worker, chunks)
    
    # Aggregate results
    max_flips = max(r[0] for r in results)
    checksum = sum(r[1] for r in results)
    
    return checksum, max_flips


def fannkuch_redux_sequential(n):
    """
    Sequential implementation of fannkuch-redux (memory efficient).
    
    Args:
        n: The number to generate permutations for (1 to n)
        
    Returns:
        Tuple of (checksum, max_flips)
    """
    max_flips = 0
    checksum = 0
    
    base_perm = list(range(1, n + 1))
    
    for idx, perm in enumerate(permutations(base_perm)):
        flips = count_flips(perm)
        
        # Update checksum
        checksum += flips if idx % 2 == 0 else -flips
        
        # Track maximum
        if flips > max_flips:
            max_flips = flips
    
    return checksum, max_flips


def fannkuch_redux(n, use_parallel=True):
    """
    Main function to compute fannkuch-redux.
    
    Args:
        n: The number to generate permutations for (1 to n)
        use_parallel: Whether to use parallel processing (default: True)
        
    Returns:
        Tuple of (checksum, max_flips)
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    
    if n > 12:
        print(f"Warning: n={n} will generate {factorial_estimate(n)} permutations", 
              file=sys.stderr)
        print("This may consume significant memory and time.", file=sys.stderr)
    
    if use_parallel and n >= 8:
        return fannkuch_redux_parallel(n)
    else:
        return fannkuch_redux_sequential(n)


def factorial_estimate(n):
    """Quick factorial estimate for warning messages."""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def main():
    """Main entry point for the program."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <n>")
        print("Computes fannkuch-redux for permutations of 1..n")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: n must be an integer", file=sys.stderr)
        sys.exit(1)
    
    if n < 1:
        print("Error: n must be at least 1", file=sys.stderr)
        sys.exit(1)
    
    # Use parallel processing for n >= 8
    use_parallel = n >= 8
    
    checksum, max_flips = fannkuch_redux(n, use_parallel=use_parallel)
    
    print(f"{checksum}")
    print(f"Pfannkuchen({n}) = {max_flips}")


if __name__ == "__main__":
    main()