from itertools import permutations

def fannkuch_redux(n):
    """
    Solve the fannkuch-redux problem for n pancakes.
    Returns: (checksum, maxflips)
    - checksum: alternating sum of flip counts for all permutations
    - maxflips: maximum number of flips needed for any permutation
    """
    def count_flips(perm):
        """Count flips needed to sort a permutation"""
        p = list(perm)
        flips = 0
        
        while p[0] != 0:
            # Reverse first p[0]+1 elements
            k = p[0]
            p[:k+1] = reversed(p[:k+1])
            flips += 1
        
        return flips
    
    maxflips = 0
    checksum = 0
    sign = 1
    
    # Generate all permutations using itertools
    for perm in permutations(range(n)):
        flips = count_flips(perm)
        
        # Update maximum flips
        maxflips = max(maxflips, flips)
        
        # Update checksum with alternating signs
        checksum += sign * flips
        sign = -sign
    
    return checksum, maxflips


def fannkuch_redux_optimized(n):
    """
    Optimized version that generates permutations manually
    and uses in-place operations for better performance.
    """
    def count_flips(perm):
        """Count flips with in-place array manipulation"""
        p = perm[:]
        flips = 0
        
        while p[0] != 0:
            k = p[0]
            # In-place reversal
            for i in range((k + 1) // 2):
                p[i], p[k - i] = p[k - i], p[i]
            flips += 1
        
        return flips
    
    # Initialize
    perm = list(range(n))
    count = [0] * n
    maxflips = 0
    checksum = 0
    sign = 1
    
    # Process first permutation
    flips = count_flips(perm)
    maxflips = flips
    checksum = flips
    
    # Generate permutations using Heap's algorithm
    i = 0
    while i < n:
        if count[i] < i:
            # Swap elements
            if i % 2 == 0:
                perm[0], perm[i] = perm[i], perm[0]
            else:
                perm[count[i]], perm[i] = perm[i], perm[count[i]]
            
            # Count flips for this permutation
            sign = -sign
            flips = count_flips(perm)
            checksum += sign * flips
            maxflips = max(maxflips, flips)
            
            count[i] += 1
            i = 0
        else:
            count[i] = 0
            i += 1
    
    return checksum, maxflips


# Example usage
if __name__ == "__main__":
    n = 7  # Try with n=7 (larger values take longer)
    
    print(f"Computing fannkuch-redux for n={n}")
    print("\nUsing itertools.permutations:")
    checksum, maxflips = fannkuch_redux(n)
    print(f"Checksum: {checksum}")
    print(f"Max flips: {maxflips}")
    
    print("\nUsing optimized version:")
    checksum, maxflips = fannkuch_redux_optimized(n)
    print(f"Checksum: {checksum}")
    print(f"Max flips: {maxflips}")