#!/usr/bin/env python3
"""
Fannkuch-redux benchmark
Ubuntu 24.04.4 LTS 64-bit
Back-end optimized implementation using Python stdlib
"""

import itertools
import sys

def fannkuch(n: int) -> tuple[int, int]:
    """Return (checksum, max_flips) for fannkuch-redux with size n."""
    max_flips = 0
    checksum = 0

    # Generate permutations lazily using itertools
    for perm_index, perm in enumerate(itertools.permutations(range(n))):
        # Convert tuple to list for flipping
        p = list(perm)
        flips = 0

        # Flip until first element is 0
        while p[0] != 0:
            k = p[0]
            # Reverse prefix of length k+1
            p[:k+1] = reversed(p[:k+1])
            flips += 1

        max_flips = max(max_flips, flips)
        # Alternate sign by permutation index
        checksum += flips if perm_index % 2 == 0 else -flips

    return checksum, max_flips


def main():
    # Read input n from command line
    if len(sys.argv) != 2:
        print("Usage: fannkuch-redux N")
        sys.exit(1)

    n = int(sys.argv[1])
    checksum, max_flips = fannkuch(n)
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")


if __name__ == "__main__":
    main()
