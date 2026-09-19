#!/usr/bin/env python3
import sys

def extract(q: int, r: int, t: int, j: int) -> int:
    """
    Extracts a digit from the LFT (Linear Fractional Transformation).
    Evaluates the function (q * j + r) // t.
    """
    return (q * j + r) // t

def pidigits(n: int) -> None:
    """
    Calculates and prints the first `n` digits of Pi using the sequential Spigot algorithm.
    """
    # Initial matrix state for LFT: Z = [q, r; s, t], with s implicitly 0.
    q, r, t = 1, 0, 1
    k = 1
    i = 0
    line = ""

    while i < n:
        # Per specification: perform both extract(3) and extract(4) independently.
        # Do not optimize away the work by short-circuiting.
        e3 = extract(q, r, t, 3)
        e4 = extract(q, r, t, 4)

        if e3 == e4:
            # The digit is stable; we can output it.
            digit = e3
            line += str(digit)
            i += 1

            # Print digits 10-to-a-line with the running total
            if i % 10 == 0:
                print(f"{line}\t:{i}")
                line = ""

            # Matrix multiplication to produce the digit (compose Z with E_y)
            # E_y = [10, -10*digit; 0, 1]
            q, r = q * 10, 10 * r - 10 * digit * t
            # t remains t
        else:
            # The digit is not stable; consume the next term in the infinite series.
            # Matrix multiplication (compose Z with M_k)
            # M_k = [k, 4*k + 2; 0, 2*k + 1]
            q_next = q * k
            r_next = q * (4 * k + 2) + r * (2 * k + 1)
            t_next = t * (2 * k + 1)

            q, r, t = q_next, r_next, t_next
            k += 1

    # Print any remaining digits padded with spaces to maintain colon alignment
    if line:
        print(f"{line:<10}\t:{n}")

def main() -> None:
    """Entry point for the script."""
    # Read target N from the command line, fallback to 10000 if not provided
    n = 10000
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Error: The number of digits must be a valid integer.", file=sys.stderr)
            sys.exit(1)

    pidigits(n)

if __name__ == '__main__':
    main()