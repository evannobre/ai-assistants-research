#!/usr/bin/env python3
"""
Fannkuch-redux benchmark implementation
Optimized for performance using native Python libraries and best practices
"""

def fannkuch_redux(n: int) -> tuple[int, int]:
    """
    Calculate fannkuch-redux for a given number n.
    
    Args:
        n: The number of elements in the permutation
        
    Returns:
        tuple: (checksum, maxflips)
    """
    # Initialize permutation arrays
    perm = list(range(n))
    perm1 = list(range(n))
    count = list(range(n, 0, -1))
    
    maxflips = 0
    checksum = 0
    sign = 1
    perm_count = 0
    
    while True:
        # Copy current permutation for flipping
        if perm1[0] != 0:
            perm[:] = perm1
            flips = 0
            
            # Perform flips
            while True:
                k = perm[0]
                if k == 0:
                    break
                    
                # Reverse first k+1 elements
                perm[:k+1] = perm[k::-1]
                flips += 1
            
            maxflips = max(maxflips, flips)
            checksum += sign * flips
        
        # Generate next permutation
        if perm_count == n - 1:
            break
            
        sign = -sign
        perm_count += 1
        
        # Update permutation using counting algorithm
        perm1[0], perm1[1] = perm1[1], perm1[0]
        i = 1
        
        while count[i] == 0:
            count[i] = i + 1
            i += 1
            
            # Rotate elements
            first = perm1[0]
            for j in range(i + 1):
                perm1[j] = perm1[j + 1]
            perm1[i + 1] = first
            
            if i >= n - 1:
                return checksum, maxflips
        
        count[i] -= 1
    
    return checksum, maxflips


def main():
    import sys
    
    # Get n from command line or use default
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    
    if n < 3 or n > 12:
        print(f"Warning: n should be between 3 and 12. Got {n}")
        if n > 12:
            print("Values above 12 may take excessive time/memory")
    
    checksum, maxflips = fannkuch_redux(n)
    
    print(f"{checksum}")
    print(f"Pfannkuchen({n}) = {maxflips}")


if __name__ == "__main__":
    main()