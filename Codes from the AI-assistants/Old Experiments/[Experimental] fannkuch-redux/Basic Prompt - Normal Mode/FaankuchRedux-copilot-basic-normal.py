import itertools

def fannkuch(n):
    max_flips = 0
    checksum = 0

    for perm in itertools.permutations(range(n)):
        flips_count = 0
        perm_copy = list(perm)

        while perm_copy[0] != 0:
            k = perm_copy[0]
            perm_copy[:k+1] = reversed(perm_copy[:k+1])
            flips_count += 1

        max_flips = max(max_flips, flips_count)
        checksum += flips_count if (perm[0] % 2 == 0) else -flips_count

    return checksum, max_flips

# Example usage
n = 7
checksum, max_flips = fannkuch(n)
print(f"Checksum: {checksum}")
print(f"Max flips: {max_flips}")