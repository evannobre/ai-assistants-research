import sys
import math
import multiprocessing
from array import array

def run_fannkuch(n):
    """
    Driver function to calculate fannkuch-redux for size n using all available cores.
    """
    # 1. Use native multiprocessing to utilize all CPU cores
    cpu_count = multiprocessing.cpu_count()
    
    # 2. Divide the total n! permutations into chunks
    fact_n = math.factorial(n)
    chunk_size = (fact_n + cpu_count - 1) // cpu_count
    
    tasks = []
    for i in range(0, fact_n, chunk_size):
        # Define ranges for each worker
        idx_min = i
        idx_max = min(i + chunk_size, fact_n)
        tasks.append((n, idx_min, idx_max))
    
    # 3. Native Pool execution
    with multiprocessing.Pool(processes=cpu_count) as pool:
        # starmap unpacks the arguments for us
        results = pool.starmap(fannkuch_worker, tasks)
    
    # 4. Aggregating results (summing checksums, finding absolute max flips)
    final_checksum = sum(r[0] for r in results)
    final_max_flips = max(r[1] for r in results)
    
    return final_checksum, final_max_flips

def fannkuch_worker(n, idx_min, idx_max):
    """
    Worker function to process a chunk of permutations.
    """
    # Initialize 'perm' based on the factoradic representation of idx_min
    # This allows us to jump directly to the i-th permutation.
    perm1 = list(range(n))
    count = list(range(n))
    
    # Standard library math to set up the initial state for this chunk
    temp_idx = idx_min
    for i in range(n - 1, 0, -1):
        d = temp_idx // math.factorial(i)
        count[i] = d
        temp_idx %= math.factorial(i)
        
        # Native list rotation logic to match the starting state
        perm1[:i+1] = perm1[1:d+1] + perm1[:1] + perm1[d+1:i+1]
        # Note: The above is a simplified rotation visualization. 
        # For strict factoradic setup, we often just rotate elements into place.
        # Below is the iterative construction often used in the benchmark:
        if d > 0:
            # Rotate left d times
             perm1[:i+1] = perm1[d:i+1] + perm1[:d]

    # Local variable optimization
    current_perm = list(perm1)
    max_flips_count = 0
    checksum = 0
    
    # Iterate through the chunk
    for i in range(idx_min, idx_max):
        
        # --- Core Fannkuch Logic ---
        # 1. Check if flipping is needed
        if current_perm[0] != 0: # Using 0-based indexing (0 represents 1)
            # Copy current state to work on it without destroying next step's state
            work_perm = current_perm[:] 
            flips = 0
            
            # 2. Flip until the first element is '0' (which represents 1)
            # We use native slicing [::-1] which is highly optimized in C
            k = work_perm[0]
            while k != 0:
                # Reverse the first k+1 elements
                # Logic: slice the first k+1 items, reverse them, assign back
                work_perm[:k+1] = work_perm[:k+1][::-1]
                flips += 1
                k = work_perm[0]
            
            # 3. Update Max Flips
            if flips > max_flips_count:
                max_flips_count = flips
            
            # 4. Update Checksum (Even index adds, Odd index subtracts)
            if i % 2 == 0:
                checksum += flips
            else:
                checksum -= flips
        
        # --- Generate Next Permutation (Native Rotation Method) ---
        if i + 1 < idx_max:
            # Rotate first 2
            current_perm[0], current_perm[1] = current_perm[1], current_perm[0]
            count[1] += 1
            j = 1
            while count[j] > j:
                count[j] = 0
                j += 1
                # Rotate the perm at index j
                # p = p[1] + p[2]... + p[0]
                # Native slice rotation
                next_first = current_perm[1]
                current_perm[1:j+1] = current_perm[2:j+1]
                current_perm[j] = next_first
                
                # Update count
                count[j] += 1
                
    return checksum, max_flips_count

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    checksum, max_flips = run_fannkuch(n)
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")