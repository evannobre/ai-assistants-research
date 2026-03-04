def fannkuch_redux(n):
    """
    Fannkuch-redux benchmark implementation.
    
    Args:
        n: The size of the permutation (typically 7-12 for benchmarking)
    
    Returns:
        tuple: (maxflips, checksum)
    """
    # Initialize permutation and counts
    perm = list(range(n))
    perm1 = list(range(n))
    count = list(range(n, 0, -1))
    
    maxflips = 0
    checksum = 0
    sign = 1
    permcount = 0
    
    while True:
        # Copy current permutation for flipping
        perm[:] = perm1
        flips = 0
        k = perm[0]
        
        # Count flips for current permutation
        while k != 0:
            # Reverse elements from 0 to k (inclusive)
            perm[:k+1] = perm[k::-1]
            flips += 1
            k = perm[0]
        
        # Update max flips
        maxflips = max(maxflips, flips)
        
        # Update checksum (alternating sum)
        checksum += flips * sign
        sign = -sign
        
        # Generate next permutation (Knuth's algorithm)
        done = True
        k = n - 1
        while k > 0:
            count[k] -= 1
            if count[k] > 0:
                done = False
                break
            count[k] = k + 1
            k -= 1
        
        if done:
            break
        
        # Rotate permutation at position k
        temp = perm1[0]
        for i in range(k + 1):
            perm1[i] = perm1[i + 1]
        perm1[k + 1] = temp
    
    return maxflips, checksum


# Example usage
if __name__ == "__main__":
    n = 10  # You can adjust this (7-12 are common benchmark values)
    maxflips, checksum = fannkuch_redux(n)
    print(f"Pfannkuchen({n}) = {maxflips}")
    print(f"Checksum: {checksum}")