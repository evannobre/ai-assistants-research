from decimal import Decimal, getcontext

def extract_digit(z, j):
    """Extracts the j-th digit from the representation of z."""
    return int(z[j - z.as_tuple().exponent]) if j >= z.as_tuple().exponent else 0

def print_digits(digits):
    """Prints digits 10-to-a-line with a running total."""
    count = 0
    for i, digit in enumerate(digits):
        print(digit, end="")
        count += 1
        if (i + 1) % 10 == 0:
            print(f"\t({count})")
    if count % 10 != 0:
        print(f"\t({count})")

def spigot_pi(n_digits):
    """
    Generates n_digits of Pi using the Spigot algorithm with arbitrary precision.
    This implementation strictly follows the sequential algorithm without optimizations.
    """
    getcontext().prec = n_digits * 10 // 3 + 5  # Set precision high enough

    k = 1
    a = [Decimal(2) for _ in range(n_digits * 10 // 3 + 1)]
    s = Decimal(0)
    digits = []

    for i in range(n_digits):
        q = Decimal(0)
        for j in range(len(a) - 1, 0, -1):
            t = a[j] * k + q
            a[j] = t % (2 * j + 1)
            q = t // (2 * j + 1)
        t = a[0] * k + q
        a[0] = t % 10
        q = t // 10
        s += q
        digits.append(extract_digit(s, 0))
        s -= Decimal(digits[-1])
        s *= 10
        k += 1

    return digits

if __name__ == "__main__":
    print("Extracting the first 3 digits of Pi:")
    first_3_digits = spigot_pi(3)
    print_digits(first_3_digits)
    print("\n")

    print("Extracting the first 4 digits of Pi:")
    first_4_digits = spigot_pi(4)
    print_digits(first_4_digits)