import sys

def fannkuch(n: int) -> int:
    # Initialize permutation and counters
    perm = list(range(n))
    count = list(range(n))
    max_flips = 0
    total_permutations = 0

    while True:
        # Copy current permutation for flipping
        perm_copy = perm[:]
        flips = 0

        # Count flips for this permutation
        while perm_copy[0] != 0:
            k = perm_copy[0]
            perm_copy[:k+1] = reversed(perm_copy[:k+1])
            flips += 1

        max_flips = max(max_flips, flips)
        total_permutations += 1

        # Generate next permutation using counting
        i = n - 1
        while i > 0:
            count[i] -= 1
            if count[i] > 0:
                perm[:i+1] = perm[i:i+1] + perm[:i]
                break
            count[i] = i
            i -= 1
        else:
            # All permutations generated
            return max_flips

if __name__ == "__main__":
    try:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
        print(f"Maximum number of flips for n={n}: {fannkuch(n)}")
    except ValueError:
        print("Please provide a valid integer.")