from decimal import Decimal, getcontext

def extract_digit(carry, denominators):
    """Extracts a single digit of Pi."""
    numerator = Decimal(2) * carry
    digit = numerator // denominators[0]
    carry = numerator % denominators[0]
    return int(digit), carry

def update_carry(carry, denominators):
    """Updates the carry for the next iteration."""
    n = len(denominators)
    for i in range(n - 1, 0, -1):
        carry = carry * (i + 1) + denominators[i] * carry
        carry //= denominators[i]
    return carry

def spigot_pi_digits(n_digits):
    """Generates n digits of Pi using the Spigot algorithm."""
    getcontext().prec = n_digits * 3  # Set precision for arbitrary arithmetic
    denominators = [Decimal(2 * i + 1) for i in range(1, n_digits + 2)]
    carry = Decimal(0)
    digits = []
    print("Generating Pi digits:")
    digits_count = 0

    for _ in range(n_digits):
        carry = update_carry(carry, denominators)
        digit, carry = extract_digit(carry, denominators)
        digits.append(str(digit))
        digits_count += 1
        if digits_count % 10 == 0:
            print("".join(digits[digits_count - 10:digits_count]), f"({digits_count})")

    return "".join(digits)

def extract(n):
    """Demonstrates extracting the nth digit (0-indexed) using intermediate state."""
    getcontext().prec = (n + 5) * 3
    denominators = [Decimal(2 * i + 1) for i in range(1, n + 6)]
    carry = Decimal(0)

    for i in range(n + 1):
        carry = update_carry(carry, denominators)
        digit, carry = extract_digit(carry, denominators)
        if i == n:
            return digit

if __name__ == "__main__":
    print("\nDemonstrating extract(3):")
    fourth_digit = extract(3)
    print(f"The 4th digit of Pi is: {fourth_digit}")

    print("\nDemonstrating extract(4):")
    fifth_digit = extract(4)
    print(f"The 5th digit of Pi is: {fifth_digit}")

    print("\nGenerating the first 20 digits of Pi:")
    spigot_pi_digits(20)

    print("\nGenerating the first 100 digits of Pi (for performance check - might take a moment):")
    spigot_pi_digits(100)