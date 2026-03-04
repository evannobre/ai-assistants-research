#!/usr/bin/env python3
import sys
from math import factorial, ceil
from decimal import Decimal, getcontext


def chudnovsky_pi(n_digits: int) -> Decimal:
    """
    Compute pi to at least n_digits decimal digits using the Chudnovsky series
    and Python's decimal module (arbitrary precision).
    """
    if n_digits <= 0:
        raise ValueError("Number of digits must be positive")

    # Extra guard digits to reduce rounding error
    extra_digits = 10
    getcontext().prec = n_digits + extra_digits

    # Chudnovsky constants
    C = 426880 * Decimal(10005).sqrt()

    # Number of terms needed (each term ~14.18 digits)
    digits_per_term = 14.181647462
    max_k = ceil(n_digits / digits_per_term)

    S = Decimal(0)
    for k in range(max_k):
        # (-1)^k
        sign = -1 if (k % 2) else 1

        # Factorials are exact with Python's arbitrary-precision integers
        num = sign * factorial(6 * k) * (13591409 + 545140134 * k)
        den = factorial(3 * k) * (factorial(k) ** 3) * (640320 ** (3 * k))

        S += Decimal(num) / Decimal(den)

    pi = C / S
    return +pi  # unary plus applies the current context precision


def format_pi(pi: Decimal, n_digits: int) -> str:
    """
    Format a Decimal pi value into a string with exactly n_digits after the decimal point.
    """
    # Convert to plain string (no exponent)
    s = format(pi, "f")

    # Ensure there's a decimal point
    if "." not in s:
        s = s + ".0"

    int_part, frac_part = s.split(".")

    # Pad fractional part if needed
    if len(frac_part) < n_digits:
        frac_part = frac_part + "0" * (n_digits - len(frac_part))

    # Truncate to exactly n_digits
    frac_part = frac_part[:n_digits]

    return f"{int_part}.{frac_part}"


def main(argv):
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <N_digits>", file=sys.stderr)
        sys.exit(1)

    try:
        n_digits = int(argv[1])
    except ValueError:
        print("N_digits must be an integer", file=sys.stderr)
        sys.exit(1)

    if n_digits <= 0:
        print("N_digits must be positive", file=sys.stderr)
        sys.exit(1)

    # Soft sanity check for this hardware; adjust if you know what you're doing
    # This is not a hard limit, just a friendly warning.
    if n_digits > 5_000_000:
        print(
            "Warning: requesting more than ~5,000,000 digits in pure Python may be very slow "
            "and memory-intensive on this machine.",
            file=sys.stderr,
        )

    pi = chudnovsky_pi(n_digits)
    pi_str = format_pi(pi, n_digits)
    print(pi_str)


if __name__ == "__main__":
    main(sys.argv)
