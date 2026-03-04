# fannkuch.py
import sys

def fannkuch(n):
    perm = list(range(1, n+1))
    count = list(range(n))
    maxflips = 0
    checksum = 0
    sign = 1

    while True:
        # count flips
        temp = perm[:]  # single allocation per permutation (O(n))
        flips = 0
        while temp[0] != 1:
            k = temp[0]
            temp[:k] = reversed(temp[:k])
            flips += 1
        checksum += sign * flips
        if flips > maxflips:
            maxflips = flips

        # next permutation using count[] as odometer
        i = 1
        while i < n:
            if count[i] > 0:
                # rotate left first i+1
                first = perm.pop(0)
                perm.append(first)
                count[i] -= 1
                sign = -sign
                break
            else:
                count[i] = i
                i += 1
        if i >= n:
            break
    return checksum, maxflips

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    checksum, maxflips = fannkuch(n)
    print(checksum)
    print(f"Pfannkuchen({n}) = {maxflips}")
