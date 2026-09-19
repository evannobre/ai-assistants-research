#!/usr/bin/env python3
import sys
import argparse
import math
import time

def compute_pi_chudnovsky(n: int) -> str:
    """
    Computes n decimal digits of Pi using the Chudnovsky Algorithm 
    and Binary Splitting.
    """
    # System Constraint Override: Ubuntu 24.04 runs Python 3.12+.
    # We must bypass the default 4300-digit string conversion limit.
    if hasattr(sys, "set_int_max_str_digits"):
        # Add a buffer for guard digits and the leading '3.'
        sys.set_int_max_str_digits(max(n + 100, 4300))

    # Chudnovsky Constants
    C = 640320
    C3_OVER_24 = C**3 // 24
    
    # Calculate required terms (~14.18 digits per term)
    terms = int(n / 13.5) + 2

    def binary_split(a: int, b: int):
        """
        Recursively computes the functions P, Q, and T for a given range [a, b).
        """
        if a + 1 == b:
            if a == 0:
                p_ab = 1
                q_ab = 1
                t_ab = 13591409
            else:
                # p_ab = -(6a - 5)(2a - 1)(6a - 1)
                p_ab = -((6 * a - 5) * (2 * a - 1) * (6 * a - 1))
                q_ab = (a**3) * C3_OVER_24
                t_ab = p_ab * (13591409 + 545140134 * a)
            return p_ab, q_ab, t_ab

        mid = (a + b) // 2
        
        # Divide and conquer
        p_am, q_am, t_am = binary_split(a, mid)
        p_mb, q_mb, t_mb = binary_split(mid, b)

        # Merge results
        p_ab = p_am * p_mb
        q_ab = q_am * q_mb
        t_ab = q_mb * t_am + p_am * t_mb

        return p_ab, q_ab, t_ab

    # Execute binary splitting
    _, q, t = binary_split(0, terms)

    # We add 10 guard digits to prevent trailing truncation errors during division
    guard_digits = 10
    precision = n + guard_digits
    
    # To use integer arithmetic for the square root:
    # sqrt(10005) * 10^precision = isqrt(10005 * 10^(2 * precision))
    sqrt_10005_scaled = math.isqrt(10005 * (10 ** (2 * precision)))

    # Compute final Pi: pi = (426880 * sqrt(10005) * Q) / T
    pi_scaled = (426880 * sqrt_10005_scaled * q) // t
    
    # Remove guard digits
    pi_truncated = str(pi_scaled // (10 ** guard_digits))
    
    # Pad string if necessary and format with decimal point
    if len(pi_truncated) < n + 1:
        pi_truncated = pi_truncated.zfill(n + 1)
        
    return f"{pi_truncated[0]}.{pi_truncated[1:n+1]}"


def main():
    parser = argparse.ArgumentParser(
        description="Compute N digits of Pi using arbitrary precision arithmetic."
    )
    parser.add_argument(
        "digits",
        type=int,
        help="Number of decimal digits to calculate"
    )
    args = parser.parse_args()

    if args.digits <= 0:
        sys.exit("Error: The number of digits must be a positive integer.")

    start_time = time.time()
    pi_value = compute_pi_chudnovsky(args.digits)
    end_time = time.time()

    # Output pi to stdout (can be piped to files)
    print(pi_value)
    
    # Output metadata to stderr so it doesn't corrupt piped standard output
    print(f"\n# Computed {args.digits} digits in {end_time - start_time:.4f} seconds", file=sys.stderr)

if __name__ == "__main__":
    main()