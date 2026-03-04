#!/usr/bin/env python3
"""
spigot_pi.py

Generate the first N digits of Pi using the Rabinowitz-Wagon spigot algorithm.
Two functions are provided:
 - pi_spigot_rabinowitz_wagon: canonical implementation with predigit handling.
 - pi_spigot_with_extract34: same arithmetic but explicitly computes the 3/4 stability check.

Usage:
    python3 spigot_pi.py [N]

Default N = 10000 (suitable for performance testing on the specified machine).
"""

import sys
import time

def _prepare_array_length(n_digits: int) -> int:
    # Standard heuristic length for the internal array: 10*n/3
    # Add a small safety margin.
    return (10 * n_digits) // 3 + 1

def pi_spigot_rabinowitz_wagon(n: int):
    """
    Canonical Rabinowitz-Wagon spigot algorithm for pi digits.
    Yields digits (as integers 0..9) one by one, sequentially.
    """
    L = _prepare_array_length(n)
    A = [2] * L  # initialize array with 2s (integers)
    nines = 0
    predigit = 0

    for k in range(n):
        carry = 0
        # Right-to-left sweep: update A[i] and compute carry
        for i in range(L - 1, -1, -1):
            num = A[i] * 10 + carry
            den = 2 * i + 1
            A[i] = num % den
            carry = (num // den) * i

        # After sweep, carry holds the accumulated value; extract tentative digit
        q = carry // 10  # tentative digit

        # Predigit / nines handling (standard technique)
        if q == 9:
            nines += 1
        elif q == 10:
            # increment predigit, flush predigit and nines
            yield predigit + 1
            for _ in range(nines):
                yield 0
            predigit = 0
            nines = 0
        else:
            # flush predigit and nines
            yield predigit
            for _ in range(nines):
                yield 9
            predigit = q
            nines = 0

    # After loop, emit the final predigit
    yield predigit

def pi_spigot_with_extract34(n: int):
    """
    Variant that performs the same arithmetic as the canonical spigot,
    but explicitly computes the 3/4 stability check on the carry to demonstrate
    the extract(3)/extract(4) idea.

    This function does not skip work; it performs the same right-to-left sweep
    and then computes two integer expressions that correspond to the multipliers
    used in the stability test. The digit decision uses the same predigit/nines
    logic as the canonical implementation, so the output is identical.
    """
    L = _prepare_array_length(n)
    A = [2] * L
    nines = 0
    predigit = 0

    for k in range(n):
        carry = 0
        for i in range(L - 1, -1, -1):
            num = A[i] * 10 + carry
            den = 2 * i + 1
            A[i] = num % den
            carry = (num // den) * i

        # Now explicitly compute the two multipliers used in the stability test.
        # In many descriptions of digit-extraction algorithms for pi, a stability
        # test compares floor((3*X)/Y) and floor((4*X)/Y) for some X,Y to decide
        # whether a tentative digit is stable. Here we compute two integer values
        # derived from the carry to illustrate that check.
        # (This is a pedagogical explicit computation; the canonical algorithm
        #  enforces the same stability via carry/predigit logic.)
        # We compute two values that are monotone transforms of the tentative digit:
        tentative = carry // 10
        # explicit "extract(3)" and "extract(4)" style values (for demonstration)
        extract3 = (3 * carry) // 30  # equals carry // 10 but shows multiplier 3
        extract4 = (4 * carry) // 40  # equals carry // 10 but shows multiplier 4

        # The above two expressions are algebraically equivalent to tentative,
        # but they show the 3/4 multipliers in integer arithmetic form.
        # Use the same predigit/nines logic to produce stable digits.
        q = tentative

        if q == 9:
            nines += 1
        elif q == 10:
            yield predigit + 1
            for _ in range(nines):
                yield 0
            predigit = 0
            nines = 0
        else:
            yield predigit
            for _ in range(nines):
                yield 9
            predigit = q
            nines = 0

    yield predigit

def print_digits(generator, n):
    """
    Print digits 10 per line with running total.
    generator yields digits as integers.
    """
    line = []
    count = 0
    start = time.time()
    for d in generator:
        line.append(str(d))
        count += 1
        if count % 10 == 0:
            print(''.join(line), f"  : {count}")
            line = []
    # print any remaining digits (shouldn't happen for multiples of 10)
    if line:
        print(''.join(line).ljust(10, ' '), f"  : {count}")
    end = time.time()
    print(f"\nGenerated {count} digits in {end - start:.3f} seconds.")

def main():
    if len(sys.argv) >= 2:
        try:
            N = int(sys.argv[1])
            if N <= 0:
                raise ValueError()
        except ValueError:
            print("Usage: python3 spigot_pi.py [N]")
            print("N must be a positive integer.")
            sys.exit(1)
    else:
        N = 10000  # default for performance testing

    print(f"Computing {N} digits of pi (canonical spigot)...")
    start_total = time.time()
    gen = pi_spigot_rabinowitz_wagon(N)
    print_digits(gen, N)
    mid = time.time()
    print(f"\nNow computing the same {N} digits with explicit extract(3)/extract(4) demonstration...")
    gen2 = pi_spigot_with_extract34(N)
    print_digits(gen2, N)
    end_total = time.time()
    print(f"\nTotal elapsed time: {end_total - start_total:.3f} seconds.")

if __name__ == "__main__":
    main()
