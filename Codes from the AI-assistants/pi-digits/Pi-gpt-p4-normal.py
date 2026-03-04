#!/usr/bin/env python3
"""
Spigot algorithm (LFT-based) for digits of Pi (classic "pidigits" style).

Requirements satisfied:
- Arbitrary precision arithmetic (Python built-in int)
- Same sequential, single-threaded algorithm (no parallelism)
- Explicitly does extract(3) and extract(4)
- Does not optimize away the work: step-by-step LFT refinement + safe digit check
- Prints 10 digits per line with running total count
"""

import sys


def pidigits(n: int) -> None:
    # LFT state (q, r, t) and refinement parameters (k, l)
    q = 1
    r = 0
    t = 1
    k = 1
    l = 3

    produced = 0
    line_buf = []

    def extract(j: int) -> int:
        # floor((q*j + r) / t)
        return (q * j + r) // t

    while produced < n:
        # Required: do both extract(3) and extract(4)
        y3 = extract(3)
        y4 = extract(4)

        if y3 == y4:
            # Safe to emit digit y3
            d = y3
            line_buf.append(chr(ord('0') + d))
            produced += 1

            # Print 10 digits per line with running total
            if len(line_buf) == 10:
                sys.stdout.write("".join(line_buf) + f"\t:{produced}\n")
                line_buf.clear()

            # "Produce" step: update LFT after emitting digit d
            # (q, r, t) := (10q, 10(r - d*t), t)
            r = 10 * (r - d * t)
            q = 10 * q
            # t unchanged

        else:
            # "Consume/refine" step: incorporate next term of the continued process
            # Using classic sequential refinement:
            # (q, r, t) := (q*k, (2q + r)*l, t*l); k := k+1; l := l+2
            # IMPORTANT: use old q when computing (2q + r)
            q_old = q
            r_old = r
            q = q_old * k
            r = (2 * q_old + r_old) * l
            t = t * l
            k += 1
            l += 2

    # Flush any remaining digits, padded to 10 columns (benchmark-style)
    if line_buf:
        sys.stdout.write("".join(line_buf).ljust(10) + f"\t:{produced}\n")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        sys.stderr.write(f"Usage: {argv[0]} N\n")
        return 2

    try:
        n = int(argv[1])
        if n < 0:
            raise ValueError
    except ValueError:
        sys.stderr.write("N must be a non-negative integer.\n")
        return 2

    pidigits(n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
