#!/usr/bin/env python3
import sys

def flip(arr):
    flips = 0
    first = arr[0]
    while first != 0:
        arr[:first+1] = arr[:first+1][::-1]
        flips += 1
        first = arr[0]
    return flips

def fannkuch(n):
    from itertools import permutations
    
    max_flips = 0
    checksum = 0
    
    for idx, perm in enumerate(permutations(range(n))):
        arr = list(perm)
        flips = flip(arr)
        max_flips = max(max_flips, flips)
        checksum += flips if idx % 2 == 0 else -flips
    
    print(checksum)
    print(f"Pfannkuchen({n}) = {max_flips}")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    fannkuch(n)