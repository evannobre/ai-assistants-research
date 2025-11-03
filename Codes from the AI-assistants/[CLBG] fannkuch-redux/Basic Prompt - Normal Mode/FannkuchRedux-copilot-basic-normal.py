import sys
import itertools

def fannkuch(n):
    max_flips = 0
    checksum = 0
    toggle = 1  # Alternates between +1 and -1

    for perm_index, perm in enumerate(itertools.permutations(range(1, n + 1))):
        flips = 0
        perm_copy = list(perm)

        while perm_copy[0] != 1:
            k = perm_copy[0]
            perm_copy[:k] = reversed(perm_copy[:k])
            flips += 1

        max_flips = max(max_flips, flips)
        checksum += toggle * flips
        toggle *= -1  # Alternate sign

    return checksum, max_flips

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    checksum, max_flips = fannkuch(n)
    print(f"Checksum: {checksum}")
    print(f"Max flips: {max_flips}")