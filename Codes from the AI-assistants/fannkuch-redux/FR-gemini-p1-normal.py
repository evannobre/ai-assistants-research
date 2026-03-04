def count_flips(perm):
    flips = 0
    first = perm[0]
    while first != 0: # 0-indexed representation of '1'
        # Reverse the first 'first + 1' elements
        perm[:first + 1] = perm[:first + 1][::-1]
        first = perm[0]
        flips += 1
    return flips

import multiprocessing
from itertools import permutations, islice

def task(chunk):
    max_flips = 0
    checksum = 0
    for p in chunk:
        # Convert tuple to list for in-place mutation
        data = list(p)
        f = count_flips(data)
        max_flips = max(max_flips, f)
        checksum += f if (sum(p) % 2 == 0) else -f
    return max_flips, checksum

def fannkuch(n):
    # Generate all permutations (native C-iterator)
    all_perms = permutations(range(n))
    
    # Split work into chunks based on CPU count
    num_cpus = multiprocessing.cpu_count()
    chunk_size = 10000  # Adjust based on n
    
    with multiprocessing.Pool(processes=num_cpus) as pool:
        # We process permutations in batches to avoid IPC overhead
        results = pool.map(task, [islice(all_perms, i, i + chunk_size) 
                                 for i in range(0, 1000, chunk_size)]) 
                                 # Note: logic above needs adjustment for full n!