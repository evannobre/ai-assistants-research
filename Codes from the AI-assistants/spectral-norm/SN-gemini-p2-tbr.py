import sys
import math
from multiprocessing import Pool, cpu_count, current_process

# -----------------------------------------------------------------------------
# 1. Mathematical Definitions
# -----------------------------------------------------------------------------

def eval_A(i: int, j: int) -> float:
    """
    Computes matrix element A[i][j] based on the problem specification:
    A[i, j] = 1 / ((i + j) * (i + j + 1) / 2 + i + 1)
    
    This matches the sequence: 1, 1/2, 1/3, 1/4, 1/5, 1/6...
    mapped to indices (0,0), (0,1), (1,0), (0,2), (1,1), (2,0)...
    """
    return 1.0 / ((i + j) * (i + j + 1) / 2 + i + 1)

def eval_A_times_u_chunk(args):
    """
    Calculates a chunk of the matrix-vector multiplication v = Au.
    Each process handles a specific range of 'i' rows.
    v[i] = sum(A[i][j] * u[j] for j in range(N))
    """
    idx_start, idx_end, u = args
    v_chunk = []
    
    # We pre-calculate range length to avoid repeated len() calls
    u_len = len(u)
    
    for i in range(idx_start, idx_end):
        partial_sum = 0.0
        # Inner loop optimization: This is the hot path.
        for j in range(u_len):
            partial_sum += eval_A(i, j) * u[j]
        v_chunk.append(partial_sum)
        
    return v_chunk

def eval_At_times_u_chunk(args):
    """
    Calculates a chunk of the multiplication v = A.T * u.
    Note indices swap in eval_A(j, i) compared to previous function.
    v[i] = sum(A[j][i] * u[j] for j in range(N))
    """
    idx_start, idx_end, u = args
    v_chunk = []
    u_len = len(u)
    
    for i in range(idx_start, idx_end):
        partial_sum = 0.0
        for j in range(u_len):
            # Notice the swap: eval_A(j, i) effectively transposes A
            partial_sum += eval_A(j, i) * u[j]
        v_chunk.append(partial_sum)
        
    return v_chunk

# -----------------------------------------------------------------------------
# 2. Parallel Orchestration
# -----------------------------------------------------------------------------

class SpectralNormSolver:
    def __init__(self, n: int):
        self.n = n
        # Determine number of workers based on available CPU cores
        self.num_workers = cpu_count()
        self.pool = Pool(processes=self.num_workers)
        
        # Calculate chunk sizes for distributing work
        self.chunk_size = math.ceil(n / self.num_workers)
        self.ranges = []
        for i in range(0, n, self.chunk_size):
            self.ranges.append((i, min(i + self.chunk_size, n)))

    def _parallel_multiply(self, u, target_func):
        """
        Distributes the vector multiplication across processes.
        """
        # Prepare arguments: (start_index, end_index, vector_u)
        # Note: Passing 'u' copies data, but for N < 100,000 this is 
        # negligible compared to math ops overhead.
        tasks = [(r[0], r[1], u) for r in self.ranges]
        
        # Map tasks to the pool
        results = self.pool.map(target_func, tasks)
        
        # Flatten results back into a single list
        full_vector = [val for chunk in results for val in chunk]
        return full_vector

    def eval_AtA_times_u(self, u):
        """
        Computes v = (A.T * A) * u
        Step 1: w = A * u
        Step 2: v = A.T * w
        """
        w = self._parallel_multiply(u, eval_A_times_u_chunk)
        v = self._parallel_multiply(w, eval_At_times_u_chunk)
        return v

    def solve(self, iterations=10):
        # Initialize u with 1s
        u = [1.0] * self.n
        v = [0.0] * self.n
        
        print(f"[*] Starting simulation with N={self.n}, Iterations={iterations}")
        print(f"[*] Workers: {self.num_workers}")
        
        for i in range(iterations):
            v = self.eval_AtA_times_u(u)
            u = v # In the standard benchmark, u becomes v for the next step
        
        # Final Calculation: sqrt( (u . v) / (v . v) )
        # Note: In the benchmark logic, 'v' here is the result of AtA * u_old
        # We need to compute dot products.
        
        # We re-compute v = AtA * u one last time for the final check 
        # or use the last resulting vectors.
        # Standard benchmark logic uses the u and v from the last iteration.
        
        vB = self.eval_AtA_times_u(u)
        
        uv = 0.0
        vv = 0.0
        for i in range(self.n):
            uv += u[i] * vB[i]
            vv += vB[i] * vB[i]
            
        return math.sqrt(uv / vv)

    def close(self):
        self.pool.close()
        self.pool.join()

# -----------------------------------------------------------------------------
# 3. Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Default size N = 2000 if not specified
    try:
        n_val = int(sys.argv[1])
    except IndexError:
        n_val = 2000 # Standard test size
        
    if n_val > 25000:
        print("[!] Warning: N > 25,000 might take considerable time on pure Python.")

    solver = SpectralNormSolver(n_val)
    
    try:
        result = solver.solve(iterations=10)
        print(f"{result:.9f}")
    finally:
        solver.close()