from itertools import permutations

def fannkuch_redux(n: int) -> tuple[int, int]:
    base = list(range(1, n + 1))
    checksum = 0
    max_flips = 0

    for idx, perm in enumerate(permutations(base)):
        # Work on a mutable copy
        q = list(perm)
        flips = 0

        # Flip until first element is 1
        while q[0] != 1:
            k = q[0]  # 1-based length of prefix to flip
            # Reverse prefix q[0:k]
            q[:k] = reversed(q[:k])
            flips += 1

        # Update checksum (alternating sign)
        if idx % 2 == 0:
            checksum += flips
        else:
            checksum -= flips

        # Track maximum flips
        if flips > max_flips:
            max_flips = flips

    return checksum, max_flips


if __name__ == "__main__":
    n = 7
    checksum, max_flips = fannkuch_redux(n)
    print(f"Checksum: {checksum}")
    print(f"Pfannkuchen({n}) = {max_flips}")
