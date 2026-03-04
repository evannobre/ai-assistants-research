import sys
from decimal import Decimal, getcontext

# Set global precision: slightly more than needed to prevent rounding issues
getcontext().prec = 10500

def extract_digit(numer, accum, denom):
    """
    Performs both extract(3) and extract(4).
    """
    # extract(3)
    temp = numer * 3 + accum
    digit3 = temp // denom

    # extract(4)
    temp = temp + numer
    digit4 = temp // denom

    # Return True if both are equal
    if digit3 == digit4:
        return int(digit3)
    return -1

def eliminate_digit(digit, numer, accum, denom):
    """
    Perform elimination step (push the digit out of the front of the stream).
    """
    accum -= denom * digit
    accum *= 10
    numer *= 10
    return numer, accum, denom

def next_term(k, numer, accum, denom):
    """
    Appends the next term in the series to the stream.
    """
    y2 = 2 * k + 1
    accum += numer * 2
    accum *= y2
    denom *= y2
    numer *= k
    return numer, accum, denom

def pi_spigot(digits):
    k = 1
    numer = Decimal(1)
    accum = Decimal(0)
    denom = Decimal(1)
    count = 0
    line_digits = ""

    while count < digits:
        digit = extract_digit(numer, accum, denom)
        if digit == -1:
            numer, accum, denom = next_term(k, numer, accum, denom)
            k += 1
        else:
            # Emit the digit
            line_digits += str(digit)
            count += 1
            if count % 10 == 0:
                print(f"{line_digits}\t:{count}")
                line_digits = ""
            numer, accum, denom = eliminate_digit(digit, numer, accum, denom)

    # Print remaining digits if not a multiple of 10
    if line_digits:
        print(f"{line_digits}\t:{count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pi_spigot.py <digits>")
        sys.exit(1)

    digits = int(sys.argv[1])
    if digits <= 0:
        print("Please provide a positive number of digits.")
        sys.exit(1)

    pi_spigot(digits)
