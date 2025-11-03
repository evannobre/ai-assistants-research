#!/usr/bin/env python3
import sys
import itertools

def fannkuch(n: int):
    max_flips = 0
    checksum = 0
    perm_index = 0

    # Precompute a range for slicing speed
    rng = list(range(n))

    for perm in itertools.permutations(rng, n):
        # Convert tuple to list for mutability
        p = list(perm)
        flips = 0

        # Simulate flipping
        while p[0] != 0:  # when first element is 0 (== "1" in 1-based), stop
            k = p[0]
            p[:k+1] = reversed(p[:k+1])  # flip first k+1 elements
            flips += 1

        # Update checksum (toggle sign depending on permutation index)
        if perm_index % 2 == 0:
            checksum += flips
        else:
            checksum -= flips

        # Track maximum flips
        if flips > max_flips:
            max_flips = flips

        perm_index += 1

    return checksum, max_flips


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    checksum, maxflips = fannkuch(n)
    print(f"{checksum}\nPfannkuchen({n}) = {maxflips}")
