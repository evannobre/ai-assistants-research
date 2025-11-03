import itertools
import sys

def fannkuch_redux(n):
    max_flips = 0
    checksum = 0
    # permutations yields tuples of 0..n-1 in lexicographic order
    for idx, perm in enumerate(itertools.permutations(range(n))):
        # copy to list for mutable operations
        p = list(perm)
        # working copy for flipping so original perm isn't needed further
        q = p[:] 
        flips = 0
        while q[0] != 0:
            k = q[0] + 1
            # reverse prefix of length k in-place
            i, j = 0, k - 1
            while i < j:
                q[i], q[j] = q[j], q[i]
                i += 1
                j -= 1
            flips += 1
        max_flips = max(max_flips, flips)
        checksum += flips if (idx % 2 == 0) else -flips
    return checksum, max_flips

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    checksum, max_flips = fannkuch_redux(n)
    print(f"{checksum}\nPfannkuchen({n}) = {max_flips}")