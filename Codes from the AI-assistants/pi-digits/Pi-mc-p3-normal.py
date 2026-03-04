#!/usr/bin/env python3
import sys

def extract(q: int, r: int, t: int, j: int) -> int:
    """
    extract(j) = floor((j*q + r) / t)
    """
    return (j * q + r) // t


def pi_digit_generator():
    """
    Unbounded spigot algorithm for digits of pi.
    Uses the classic q, r, t, k state and extract(3), extract(4).
    All arithmetic is with Python's arbitrary-precision ints.
    """
    q, r, t, k = 1, 0, 1, 1

    while True:
        # Do both extract(3) and extract(4) every iteration
        n  = extract(q, r, t, 3)
        n2 = extract(q, r, t, 4)

        if n == n2:
            # Safe to emit digit n
            yield n
            # produce transformation
            q, r, t, k = 10 * q, 10 * (r - n * t), t, k
        else:
            # consume transformation
            q, r, t, k = q * k, (2 * q + r) * k, t * (2 * k + 1), k + 1


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} N", file=sys.stderr)
        sys.exit(1)

    try:
        N = int(sys.argv[1])
    except ValueError:
        print("N must be an integer", file=sys.stderr)
        sys.exit(1)

    gen = pi_digit_generator()
    count = 0
    line = []

    while count < N:
        d = next(gen)
        count += 1
        line.append(str(d))

        if count % 10 == 0 or count == N:
            # Join digits, print 10 per line, plus running total
            print("".join(line), f"\t:{count}")
            line = []


if __name__ == "__main__":
    main()
