from itertools import permutations

def count_flips(perm):
    """
    Count the number of flips needed to sort a permutation.
    A flip reverses the first k elements where k is the first element's value.
    """
    p = list(perm)  # Make a copy to modify
    flips = 0
    
    while p[0] != 1:
        k = p[0]
        # Reverse the first k elements
        p[:k] = reversed(p[:k])
        flips += 1
    
    return flips

def fannkuch_redux(n):
    """
    Solve the fannkuch-redux problem for a given number n.
    
    Returns:
        tuple: (checksum, max_flips)
        - checksum: alternating sum of flip counts
        - max_flips: maximum number of flips for any permutation
    """
    checksum = 0
    max_flips = 0
    sign = 1
    
    # Generate all permutations of 1 to n
    for perm in permutations(range(1, n + 1)):
        flips = count_flips(perm)
        
        # Update checksum with alternating sign
        checksum += sign * flips
        sign = -sign
        
        # Track maximum flips
        max_flips = max(max_flips, flips)
    
    return checksum, max_flips

# Example usage
if __name__ == "__main__":
    # Test with different values
    for n in range(1, 11):
        checksum, max_flips = fannkuch_redux(n)
        print(f"n={n}: checksum={checksum}, max_flips={max_flips}")
    
    # For larger values (warning: this gets very slow for n > 11)
    # n = 12
    # checksum, max_flips = fannkuch_redux(n)
    # print(f"\nn={n}: checksum={checksum}, max_flips={max_flips}")