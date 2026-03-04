import sys

def fannkuch(n):
    perm = list(range(1, n+1))
    count = list(range(1, n+1))
    checksum = 0
    maxflips = 0
    sign = 1

    while True:
        # compute flips
        if perm[0] != 1:
            perm1 = perm[:]            # reuse a single buffer if you want
            flips = 0
            while perm1[0] != 1:
                k = perm1[0]
                # reverse prefix 0..k-1
                i, j = 0, k-1
                while i < j:
                    perm1[i], perm1[j] = perm1[j], perm1[i]
                    i += 1; j -= 1
                flips += 1
            if flips > maxflips:
                maxflips = flips
        else:
            flips = 0

        checksum += sign * flips
        sign = -sign

        # next permutation using count
        i = 1
        while i < n:
            count[i] -= 1
            if count[i] > 0:
                # rotate left first i+1 elements
                first = perm[0]
                for j in range(i):
                    perm[j] = perm[j+1]
                perm[i] = first
                break
            else:
                count[i] = i+1
                i += 1
        if i == n:
            break

    return checksum, maxflips

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    checksum, maxflips = fannkuch(n)
    print(checksum)
    print("Pfannkuchen({}) = {}".format(n, maxflips))
