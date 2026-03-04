#!/usr/bin/env python3
import sys

def fannkuch(n):
    # initial permutation 1..n
    perm = list(range(1, n+1))
    # count array for generating permutations
    count = list(range(1, n+1))
    max_flips = 0
    checksum = 0
    perm_index = 0

    while True:
        # compute flips for current permutation
        first = perm[0]
        flips = 0
        if first != 1:
            # copy to temp to simulate flips
            temp = perm[:]  # small allocation of size n
            while temp[0] != 1:
                k = temp[0]
                # reverse prefix of length k
                i, j = 0, k-1
                while i < j:
                    temp[i], temp[j] = temp[j], temp[i]
                    i += 1; j -= 1
                flips += 1
        # update checksum: even index -> +flips, odd -> -flips
        if (perm_index & 1) == 0:
            checksum += flips
        else:
            checksum -= flips
        if flips > max_flips:
            max_flips = flips

        # generate next permutation in-place using count/rotation
        # find rightmost position i with count[i] > 1
        i = 1
        while i < n:
            if count[i] > 1:
                break
            count[i] = i + 1
            # rotate left the prefix perm[0..i]
            first = perm[0]
            for j in range(i):
                perm[j] = perm[j+1]
            perm[i] = first
            i += 1
        else:
            # finished all permutations
            return checksum, max_flips

        # decrement count[i]
        count[i] -= 1
        # swap perm[0] and perm[i]
        perm[0], perm[i] = perm[i], perm[0]
        perm_index += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fannkuch.py N")
        sys.exit(1)
    n = int(sys.argv[1])
    checksum, maxflips = fannkuch(n)
    print(f"{checksum}\nPfannkuchen({n}) = {maxflips}")
