#!/usr/bin/env python3
"""
Spigot algorithm for generating digits of Pi using extract(3) or extract(4).
Prints digits 10 per line with running total.
"""
import argparse

def spigot(m, N):
    """
    Generate N digits of Pi using the spigot algorithm with parameter m (3 or 4).
    Yields one digit (0..9) at a time.
    """
    # Initialize state
    q, r, t, k, n, l = 1, 0, 1, 1, m, 3
    for _ in range(N):
        # extraction test
        if 4*q + r - t < n * t:
            # emit next digit
            d = n
            yield d
            # update for next extraction
            new_q = q * 10
            new_r = 10 * (r - d * t)
            new_n = (3 * new_q + new_r) // t - 10 * d
            # apply updates
            q, r, n = new_q, new_r, new_n
            # t, k, l unchanged
        else:
            # refinement step
            new_q = q * k
            new_r = l * (2 * q + r)
            new_t = t * l
            new_k = k + 1
            new_l = l + 2
            new_n = (q * (m * k + 2) + r * l) // (t * l)
            # apply updates
            q, r, t, k, n, l = new_q, new_r, new_t, new_k, new_n, new_l


def main():
    parser = argparse.ArgumentParser(
        description="Spigot algorithm for Pi digits using extract(3) or extract(4)."
    )
    parser.add_argument(
        'digits', type=int,
        help='Number of digits of Pi to compute'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--extract3', action='store_true',
        help='Use extract(3) variant (default)'
    )
    group.add_argument(
        '--extract4', action='store_true',
        help='Use extract(4) variant'
    )
    args = parser.parse_args()

    m = 4 if args.extract4 else 3
    N = args.digits

    count = 0
    line_digits = []
    for digit in spigot(m, N):
        line_digits.append(str(digit))
        count += 1
        if count % 10 == 0:
            print(''.join(line_digits), '\t', count)
            line_digits = []
    # print any remaining digits
    if line_digits:
        print(''.join(line_digits), '\t', count)

if __name__ == '__main__':
    main()
