#!/usr/bin/env python3
"""
fannkuch-redux implementation using Python's native libraries.
- Uses itertools.permutations to enumerate permutations
- Uses list slicing for prefix flips
- Computes permutation parity by counting inversions (native loops)

Usage:
    python fannkuch_redux.py 7

Outputs the checksum and the maximum number of flips (Pfannkuchen).
"""
import sys
import itertools


def fannkuch(n: int):
    """Compute (checksum, maxflips) for given n.

    Uses native Python features: itertools.permutations, list slicing for flips,
    and a simple inversion count to determine permutation parity (even/odd).
    """
    maxflips = 0
    checksum = 0

    for perm in itertools.permutations(range(n)):
        p = list(perm)

        # Compute parity by counting inversions (O(n^2), but uses only native ops)
        parity = 0
        for i in range(n - 1):
            ai = p[i]
            for j in range(i + 1, n):
                if ai > p[j]:
                    parity ^= 1

        # Count flips for this permutation using a copy and prefix reversals
        q = p[:]  # work on a copy
        flips = 0
        while q[0] != 0:
            k = q[0]
            # reverse prefix 0..k in-place via slicing
            q[: k + 1] = q[: k + 1][::-1]
            flips += 1

        # checksum: +flips for even permutations, -flips for odd permutations
        checksum += (-flips if parity else flips)

        if flips > maxflips:
            maxflips = flips

    return checksum, maxflips


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Please provide an integer n (e.g. 7).", file=sys.stderr)
            sys.exit(1)
    else:
        n = 7  # default if not provided

    checksum, maxflips = fannkuch(n)
    print(f"{checksum}\nPfannkuchen({n}) = {maxflips}")
