def fannkuch_redux(n):
    """
    Solve the fannkuch-redux benchmark for a given number n.
    Returns (checksum, max_flips)
    """
    # Initialize permutation and count arrays
    perm = list(range(n))
    perm1 = list(range(n))
    count = list(range(n))
    
    max_flips = 0
    checksum = 0
    sign = 1
    perm_count = 0
    
    while True:
        # Count flips for current permutation
        flips = 0
        k = perm[0]
        
        if k != 0:
            # Copy current permutation
            perm1[:] = perm
            
            # Perform flips
            while k != 0:
                # Reverse elements from 0 to k
                perm1[:k+1] = perm1[:k+1][::-1]
                flips += 1
                k = perm1[0]
            
            # Update max flips
            max_flips = max(max_flips, flips)
            
            # Update checksum (alternating sum)
            checksum += sign * flips
        
        # Generate next permutation using Heap's algorithm variant
        sign = -sign
        perm_count += 1
        
        # Find rightmost position to increment
        i = 1
        while i < n:
            # Rotate left the first i+1 elements
            first = perm[0]
            perm[:i+1] = perm[1:i+2] + [first]
            
            count[i] -= 1
            if count[i] > 0:
                break
            
            # Reset count and continue
            count[i] = i + 1
            i += 1
        else:
            # All permutations generated
            break
    
    return checksum, max_flips


# Example usage
if __name__ == "__main__":
    n = 10  # Change this value as needed
    checksum, max_flips = fannkuch_redux(n)
    print(f"Pfannkuchen({n}) = {max_flips}")
    print(f"Checksum = {checksum}")