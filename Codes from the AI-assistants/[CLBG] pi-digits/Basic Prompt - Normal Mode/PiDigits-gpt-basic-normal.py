import sys
from decimal import Decimal, getcontext

# Arbitrary precision setup
def spigot_pi(n_digits):
    getcontext().prec = n_digits * 3  # More precision to avoid rounding errors

    # Initialize variables
    k = 1
    acc = Decimal(0)
    den = Decimal(1)
    num = Decimal(1)
    tmp = Decimal(0)

    produced_digits = 0
    line = ''
    i = 0

    while produced_digits < n_digits:
        # Produce digits until reaching N
        i += 1

        # Digit extraction candidates
        y = extract_digit(3, acc, num, den)
        if y != extract_digit(4, acc, num, den):
            # If digits don't match, refine
            k += 1
            acc, num, den = next_term(k, acc, num, den)
            continue

        # Digit is valid
        line += str(int(y))
        produced_digits += 1

        if produced_digits % 10 == 0:
            print(f"{line}\t:{produced_digits}")
            line = ''

        # Eliminate digit y
        acc = (acc - den * y) * 10
        num = num * 10

def extract_digit(j, acc, num, den):
    """Extract digit using j = 3 or 4"""
    # Compute (num * j + acc) // den
    tmp = num * j + acc
    return (tmp // den)

def next_term(k, acc, num, den):
    """Generate the next term in the sequence"""
    k2 = Decimal(2 * k + 1)
    acc = acc + num * 2
    acc = acc * k2
    den = den * k2
    num = num * k
    return acc, num, den

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python spigot_pi.py <number_of_digits>")
        sys.exit(1)

    n = int(sys.argv[1])
    spigot_pi(n)