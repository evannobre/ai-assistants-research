import sys
# The code structure for high-performance Fannkuch-Redux often avoids recursion
# and uses an iterative permutation generation technique.

def fannkuch_redux(n):
    """
    Solves the Fannkuch-Redux problem for a given N.
    Uses the iterative factorial-based permutation generation and flip algorithm.
    """
    
    # 1. Setup - Precalculate factorials and initialize state
    # Uses native list for factorials.
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i

    p = list(range(1, n + 1)) # The initial permutation (e.g., [1, 2, 3, 4, 5])
    # cc tracks the index for permutation generation. cc[i] holds the
    # number of rotations for the element at index i (used for rotation-based generation).
    cc = [0] * n 
    
    max_flips = 0
    checksum = 0
    toggle_sign = 1
    
    # Initial state for the permutation generation (p[1] is the element to rotate)
    i = 1 
    
    # Loop over all n! permutations using an iterative/factorial-based method
    while i < n:
        # A. Core Permutation Generation Step (Rotation)
        
        # cc[i] is the number of rotations already performed for the element at p[i].
        if cc[i] < i:
            # Perform a rotation (circular shift)
            j = 0 if (i % 2 == 0) else cc[i] # Calculate the swap index j
            
            # Use native list operations for the rotation/swap
            p[j], p[i] = p[i], p[j]

            # Increment the rotation counter for this element
            cc[i] += 1
            i = 1 # Reset i to 1 to continue generating the next permutation
            
            # B. The Flipping (Fannkuch) Process
            
            # Create a working copy for the flips (crucial for correctness)
            # Uses native list slicing for copying
            perm = p[:] 
            
            flips = 0
            while perm[0] != 1:
                k = perm[0]
                # Native list slicing and assignment for prefix reversal (The Flip)
                # perm[:k] = perm[k-1::-1]
                
                # Optimized in-place reversal using a simple loop is faster:
                for idx in range(k // 2):
                    perm[idx], perm[k - 1 - idx] = perm[k - 1 - idx], perm[idx]
                
                flips += 1
            
            # C. Checksum and Maximum Flips Update
            checksum += toggle_sign * flips
            toggle_sign = -toggle_sign
            
            if flips > max_flips:
                max_flips = flips
                
        # If cc[i] == i, all rotations for element i are done.
        # Reset the rotation count and move to the next index (i+1)
        else:
            cc[i] = 0
            i += 1
            
    return max_flips, checksum

# --- Main execution ---
if __name__ == '__main__':
    # Determine N from command line arguments or default to 5 for small test
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        N = int(sys.argv[1])
    else:
        # Use 12 for performance test as requested
        N = 12 

    if N < 1:
        print("N must be >= 1")
    else:
        # For N=12, this will take a significant amount of time (minutes).
        max_flips, checksum = fannkuch_redux(N)
        
        # Print the required output format
        print(f"Checksum: {checksum}")
        print(f"Max flips: {max_flips}")