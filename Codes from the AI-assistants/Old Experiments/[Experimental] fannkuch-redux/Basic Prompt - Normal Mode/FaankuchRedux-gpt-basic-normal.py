import itertools

def fannkuch_redux(n):
    max_flips = 0
    checksum = 0

    # Generate all permutations of 0..n-1
    for perm in itertools.permutations(range(n)):
        perm = list(perm)
        flips = 0
        first = perm[0]

        # Make a copy to flip
        temp = perm[:]

        while first != 0:
            k = first + 1
            # Flip the first k elements
            temp[:k] = temp[:k][::-1]
            flips += 1
            first = temp[0]

        checksum += flips if perm[0] == 0 else -flips
        max_flips = max(max_flips, flips)

    return checksum, max_flips

# Example usage
n = 7
checksum, max_flips = fannkuch_redux(n)
print(f"Checksum: {checksum}, Max flips: {max_flips}")
