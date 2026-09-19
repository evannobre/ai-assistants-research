import sys
import math
import decimal

def calculate_pi(digits):
    if digits < 0:
        raise ValueError("Number of digits cannot be negative.")
    if digits == 0:
        return "3"

    # Set context precision to requested digits + 10 guard digits 
    # to prevent rounding errors at the tail end of the calculation.
    decimal.getcontext().prec = digits + 10

    # Initialization
    a = decimal.Decimal(1)
    b = decimal.Decimal(1) / decimal.Decimal(2).sqrt()
    t = decimal.Decimal(1) / decimal.Decimal(4)
    p = decimal.Decimal(1)

    # Gauss-Legendre doubles correct digits per iteration.
    # log2(digits) gives us the exact number of iterations needed.
    iterations = math.ceil(math.log2(digits)) if digits > 0 else 1

    # Add 2 extra iterations to guarantee mathematical accuracy at the boundaries
    for _ in range(iterations + 2):
        a_next = (a + b) / 2
        b_next = (a * b).sqrt()
        t_next = t - p * (a - a_next) ** 2
        p_next = p * 2

        a, b, t, p = a_next, b_next, t_next, p_next

    # Final Pi approximation
    pi = ((a + b) ** 2) / (4 * t)
    
    # Convert to string and truncate to exact requested decimal places (plus '3.')
    pi_string = str(pi)
    return pi_string[:digits + 2]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pi_generator.py <number_of_digits>")
        sys.exit(1)
    
    try:
        n_digits = int(sys.argv[1])
        print(calculate_pi(n_digits))
    except ValueError:
        print("Error: Please provide a valid integer.")
        sys.exit(1)