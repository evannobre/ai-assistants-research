import itertools
import time
import sys
from typing import Tuple, List

def fannkuch_redux(n: int) -> Tuple[int, int]:
    """
    Solve the Fannkuch Redux problem for given n.
    Returns (max_flips, checksum)
    """
    # Initialize arrays
    perm = list(range(n))
    count = [0] * n
    max_flips = 0
    checksum = 0
    r = n
    
    # Main permutation generation loop using "Algorithm L" (Knuth)
    while True:
        # While r != 1
        while r != 1:
            count[r-1] = r
            r -= 1
        
        # Calculate flips for current permutation
        first = perm[0]
        if first != 0:
            k = perm[first]
            flips = 1
            
            # Perform pancake flip simulation
            while k:
                # Reverse slice [0:first+1]
                i, j = 0, first
                while i < j:
                    perm[i], perm[j] = perm[j], perm[i]
                    i += 1
                    j -= 1
                flips += 1
                
                first = k
                k = perm[k]
            
            # Update max_flips and checksum
            max_flips = max(max_flips, flips)
            checksum += flips if (perm[0] % 2 == 0) else -flips
        
        # Generate next permutation
        while True:
            if r == n:
                return max_flips, checksum
            
            perm0 = perm[0]
            i = 0
            while i < r:
                j = i + 1
                perm[i] = perm[j]
                i = j
            perm[r] = perm0
            
            count[r] = count[r] - 1
            if count[r] > 0:
                break
            r += 1

def main():
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 7  # Default
        
    max_flips, checksum = fannkuch_redux(n)
    
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")

if __name__ == "__main__":
    main()