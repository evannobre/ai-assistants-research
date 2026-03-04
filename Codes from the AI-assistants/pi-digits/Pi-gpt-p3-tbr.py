#!/usr/bin/env python3
"""
Spigot algorithm (LFT / Jeremy Gibbons style) for generating digits of Pi.

- Arbitrary precision: uses Python's built-in `int`.
- Single-threaded, sequential algorithm.
- Uses BOTH extract(3) and extract(4) each step to decide when a digit is safe.
- Prints digits 10-to-a-line with running total (benchmarkgames-style).
"""

from __future__ import annotations
import sys


def extract(q: int, r: int, t: int, j: int) -> int:
    """extract(j) = floor((q*j + r) / t)"""
    return (q * j + r) // t


def pidigits(n: int):
    """
    Generator yielding the first n digits of Pi (including the leading '3').

    State represents the LFT: (q*x + r) / t
    with a term stream consumed via (k, l).
    """
    q, r, t = 1, 0, 1
    k, l = 1, 3

    produced = 0
    while produced < n:
        y3 = extract(q, r, t, 3)          # extract(3)
        y4 = extract(q, r, t, 4)          # extract(4)

        if y3 == y4:
            # Safe digit
            yield y3
            produced += 1

            # produce(y3): refine to the next digit
            # q = 10*q
            # r = 10*(r - y3*t)
            q *= 10
            r = (r - y3 * t) * 10
            # t unchanged
        else:
            # consume next term (k, l):
            # (q, r, t) = (q*k, (2*q + r)*l, t*l)
            q0 = q
            r = (2 * q0 + r) * l
            q = q0 * k
            t *= l
            k += 1
            l += 2


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} N", file=sys.stderr)
        return 2

    try:
        n = int(argv[1])
    except ValueError:
        print("N must be an integer.", file=sys.stderr)
        return 2

    if n < 0:
        print("N must be >= 0.", file=sys.stderr)
        return 2

    # Print 10 digits per line, with running total.
    buf = []
    count = 0
    for d in pidigits(n):
        buf.append(chr(ord('0') + d))
        count += 1

        if len(buf) == 10:
            sys.stdout.write("".join(buf) + f"\t:{count}\n")
            buf.clear()

    if buf:
        # Pad last line with spaces to 10 chars (benchmark format)
        sys.stdout.write("".join(buf) + " " * (10 - len(buf)) + f"\t:{count}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
