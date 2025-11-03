#!/usr/bin/env python3
"""
Fannkuch-redux benchmark implementation (Python 3, standard library only).
Optimized for clarity and correctness, following benchmark rules.
"""

import itertools
import sys


def fannkuch(n: int) -> tuple[int, int]:
    max_flips = 0
    checksum = 0

    for perm_index, perm in enumerate(itertools.permutations(range(1, n + 1))):
        # Work on a mutable copy of the permutation
        perm_list = list(perm)
        flips_count = 0

        # Count flips until first element is 1
        while perm_list[0] != 1:
            k = perm_list[0]
            perm_list[:k] = reversed(perm_list[:k])  # flip first k elements
            flips_count += 1

        # Update checksum (alternating sign)
        if perm_index % 2 == 0:
            checksum += flips_count
        else:
            checksum -= flips_count

        # Track maximum flips
        if flips_count > max_flips:
            max_flips = flips_count

    return checksum, max_flips


if __name__ == "__main__":
    try:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    except ValueError:
        print("Usage: fannkuch.py <n>")
        sys.exit(1)

    checksum, max_flips = fannkuch(n)
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")
