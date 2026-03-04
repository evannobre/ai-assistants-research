#!/usr/bin/env python3
from decimal import Decimal, getcontext
import sys
import math

def compute_pi(n_digits: int) -> str:
    # Extra guard digits for internal precision
    extra = 5
    getcontext().prec = n_digits + extra

    # Chudnovsky constants
    C = 426880 * Decimal(10005).sqrt()

    # Number of terms needed (each term ~14 digits)
    terms = n_digits // 14 + 1

    # Chudnovsky series
    sum_ = Decimal(0)
    for k in range(terms):
        k = Decimal(k)
        num = ((-1) ** int(k)) * math.factorial(6 * int(k)) * (13591409 + 545140134 * k)
        den = (math.factorial(3 * int(k)) *
               (math.factorial(int(k)) ** 3) *
               (640320 ** (3 * int(k))))
        sum_ += Decimal(num) / Decimal(den)

    pi = C / sum_

    # Convert to string and trim to exactly n_digits
    s = format(pi, 'f')  # decimal string like '3.14159...'
    s = s.replace('.', '')  # remove decimal point: '314159...'
    s = s[:n_digits]        # keep exactly n_digits
    # Reinsert decimal point after first digit
    if n_digits == 1:
        return s[0]
    return s[0] + '.' + s[1:]


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} N")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError
    except ValueError:
        print("N must be a positive integer.")
        sys.exit(1)

    pi_str = compute_pi(n)
    print(pi_str)


if __name__ == "__main__":
    main()
