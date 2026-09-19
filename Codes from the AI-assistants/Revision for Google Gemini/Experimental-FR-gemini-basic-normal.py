import sys
import math
from multiprocessing import cpu_count, Pool

def task_worker(args):
    """
    Worker function to process a chunk of permutations.
    args: tuple of (n, idxMin, idxMax)
    """
    n, idxMin, idxMax = args
    
    # 0-indexed arrays are used internally for easier math
    p = list(range(n))
    count = [0] * n
    
    # 1. Unrank the starting permutation (jump directly to index idxMin)
    idx = idxMin
    for i in range(n - 1, 0, -1):
        fact = math.factorial(i)
        d = idx // fact
        count[i] = d
        idx %= fact
        # Rotate the first (i+1) elements left by d steps
        p[:i+1] = p[d:i+1] + p[:d]

    max_flips = 0
    checksum = 0
    
    # 2. Iterate through the permutations in this chunk
    for i in range(idxMin, idxMax):
        
        # If p[0] == 0, flips is 0. 0 added to checksum does nothing.
        if p[0] != 0:
            q = p[:]
            flips = 0
            k = q[0]
            
            # The pancake flipping sequence
            while k != 0:
                # Use native C-level slicing to reverse the first k+1 elements
                q[:k+1] = q[k::-1]
                flips += 1
                k = q[0]
            
            if flips > max_flips:
                max_flips = flips
                
            # Checksum parity based on the absolute permutation index
            if i % 2 == 0:
                checksum += flips
            else:
                checksum -= flips
                
        # 3. Generate the next permutation using the Fannkuch rotation method
        if i != idxMax - 1:
            p[0], p[1] = p[1], p[0]
            count[1] += 1
            j = 1
            
            while count[j] > j:
                count[j] = 0
                j += 1
                if j == n:
                    break
                
                # Rotate elements 0 to j (inclusive) left by 1 position
                first = p[0]
                p[:j] = p[1:j+1]
                p[j] = first
                count[j] += 1

    return checksum, max_flips

def fannkuch_redux(n):
    n_fact = math.factorial(n)
    
    # Divide the workload into roughly 150 chunks. 
    # This prevents load imbalance across cores while minimizing IPC overhead.
    n_chunks = 150 
    chunk_size = max(1, (n_fact + n_chunks - 1) // n_chunks)
    
    args = []
    for i in range(0, n_fact, chunk_size):
        args.append((n, i, min(i + chunk_size, n_fact)))
        
    # Utilize Python's native multiprocessing pool to map blocks to CPU cores
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(task_worker, args)
    
    total_checksum = 0
    max_flips = 0
    
    # Recombine results from the worker processes
    for checksum, m_flips in results:
        total_checksum += checksum
        if m_flips > max_flips:
            max_flips = m_flips
            
    return total_checksum, max_flips

if __name__ == '__main__':
    # Standard benchmark values: 7 for quick testing, 12 for performance.
    n = 12 if len(sys.argv) < 2 else int(sys.argv[1])
    
    checksum, max_flips = fannkuch_redux(n)
    
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")