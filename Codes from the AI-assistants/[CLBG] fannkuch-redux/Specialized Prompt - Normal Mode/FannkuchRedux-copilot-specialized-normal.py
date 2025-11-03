import sys
import itertools
from array import array

def fannkuch(n: int) -> None:
    max_flips = 0
    checksum = 0
    toggle = 1  # alternates between +1 and -1

    for perm_index, perm in enumerate(itertools.permutations(range(1, n + 1))):
        perm_array = array('i', perm)
        flips_count = 0

        while perm_array[0] != 1:
            k = perm_array[0]
            perm_array[:k] = reversed(perm_array[:k])
            flips_count += 1

        checksum += toggle * flips_count
        toggle *= -1
        max_flips = max(max_flips, flips_count)

    print(f"Checksum: {checksum}")
    print(f"Maximum number of flips: {max_flips}")

if __name__ == "__main__":
    try:
        n = int(sys.argv[1])
        if n < 1 or n > 12:
            raise ValueError("Please provide a number between 1 and 12.")
        fannkuch(n)
    except (IndexError, ValueError) as e:
        print(f"Usage: python3 fannkuch.py <n>\nError: {e}")