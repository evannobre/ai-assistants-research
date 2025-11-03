#!/usr/bin/env python3
import sys

def fannkuch(n):
    p = list(range(1, n+1))
    count = [0] * n
    maxflips = 0
    checksum = 0
    sign = 1

    # factorial count for loop limit
    fact = 1
    for i in range(2, n+1):
        fact *= i

    for _ in range(fact):
        # compute flips on a copy
        q = p[:]  # small list copy
        flips = 0
        while q[0] != 1:
            k = q[0]
            q[:k] = reversed(q[:k])
            flips += 1
        checksum += sign * flips
        if flips > maxflips:
            maxflips = flips

        # generate next permutation (factoradic-like)
        i = 1
        while i < n:
            count[i] += 1
            if count[i] <= i:
                # rotate left prefix 0..i
                first = p.pop(0)
                p.insert(i, first)
                sign = -sign
                break
            count[i] = 0
            i += 1
        if i >= n:
            break

    return checksum, maxflips

if __name__ == '__main__':
    n = 7
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    checksum, maxflips = fannkuch(n)
    print(f"{checksum}\nPfannkuchen({n}) = {maxflips}")