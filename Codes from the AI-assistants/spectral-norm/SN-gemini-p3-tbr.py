import sys
import math
import multiprocessing
from itertools import repeat

# Global configurations
# We use a global variable for N to be accessible by worker processes easily
N = 0 

# Function (i): Computes the infinite matrix element A[i, j]
# Note: Using 0-based indexing to match standard implementation logic
def eval_A(i, j):
    return 1.0 / ((i + j) * (i + j + 1) / 2 + i + 1)

# Helper function for worker processes to calculate a chunk of A * v
def multiply_Av_chunk(args):
    """
    Calculates A * v for a specific range of rows (idx_start to idx_end).
    v is passed via shared memory or argument.
    """
    idx_start, idx_end, v_local = args
    result_chunk = []
    for i in range(idx_start, idx_end):
        sum_val = 0.0
        for j, v_j in enumerate(v_local):
            sum_val += eval_A(i, j) * v_j
        result_chunk.append(sum_val)
    return result_chunk

# Function (ii): Computes A * v
def eval_A_times_v(v, pool, chunk_ranges):
    # Prepare arguments for parallel processing
    # We pass the full vector 'v' to all workers
    inputs = [(start, end, v) for start, end in chunk_ranges]
    
    # Map the work to the pool
    results = pool.map(multiply_Av_chunk, inputs)
    
    # Flatten results
    return [x for block in results for x in block]

# Helper function for worker processes to calculate a chunk of A^T * v
def multiply_Atv_chunk(args):
    """
    Calculates A^T * v for a specific range of rows (idx_start to idx_end).
    Note that A^T[i, j] = A[j, i]
    """
    idx_start, idx_end, v_local = args
    result_chunk = []
    for i in range(idx_start, idx_end):
        sum_val = 0.0
        for j, v_j in enumerate(v_local):
            # A_transpose[i, j] is eval_A(j, i)
            sum_val += eval_A(j, i) * v_j
        result_chunk.append(sum_val)
    return result_chunk

# Function (iii): Computes A^T * v
def eval_At_times_v(v, pool, chunk_ranges):
    inputs = [(start, end, v) for start, end in chunk_ranges]
    results = pool.map(multiply_Atv_chunk, inputs)
    return [x for block in results for x in block]

# Function (iv): Computes A^T * (A * v)
def eval_AtA_times_v(v, pool, chunk_ranges):
    # First compute w = A * v
    w = eval_A_times_v(v, pool, chunk_ranges)
    # Then compute result = A^T * w
    return eval_At_times_v(w, pool, chunk_ranges)

def main():
    global N
    
    # 1. Parse Command Line Argument
    if len(sys.argv) > 1:
        N = int(sys.argv[1])
    else:
        N = 100 # Default if no argument provided
        
    print(f"Calculating Spectral Norm for N={N}...")

    # Set up Multiprocessing Pool
    # We use all available CPU cores to maximize native performance
    cpu_count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpu_count)
    
    # Pre-calculate chunk ranges for workers to split the load evenly
    chunk_size = math.ceil(N / cpu_count)
    chunk_ranges = []
    for i in range(0, N, chunk_size):
        chunk_ranges.append((i, min(i + chunk_size, N)))

    # 2. Initialize vector u with 1.0
    u = [1.0] * N
    v = [0.0] * N

    # 3. Power Method Iterations
    # Standard benchmark requires 10 iterations
    for _ in range(10):
        v = eval_AtA_times_v(u, pool, chunk_ranges)
        u = eval_AtA_times_v(v, pool, chunk_ranges)

    # 4. Final Calculation
    # spectral_norm = sqrt( (u . u) / (u . v) ) -> based on standard benchmark logic
    # (Where u is the latest result and v is the input to the last step)
    
    vBv = 0.0
    vv = 0.0
    
    for i in range(N):
        vBv += u[i] * u[i]
        vv  += u[i] * v[i]

    result = math.sqrt(vBv / vv)
    
    print(f"{result:.9f}")
    
    # Clean up
    pool.close()
    pool.join()

if __name__ == "__main__":
    main()