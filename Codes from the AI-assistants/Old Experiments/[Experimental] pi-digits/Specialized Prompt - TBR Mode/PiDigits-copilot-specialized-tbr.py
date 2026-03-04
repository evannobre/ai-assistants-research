from decimal import Decimal, getcontext
from math import factorial
import math

def compute_pi(n_digits):
    """
    Compute Pi to a specified number of decimal digits using the Chudnovsky algorithm.
    
    Args:
      n_digits (int): Number of decimal digits desired.
    
    Returns:
      A string representing π to the specified precision.
    """
    # Add some extra digits to the precision to ensure accuracy during intermediate steps.
    extra_digits = 10
    getcontext().prec = n_digits + extra_digits

    # The Chudnovsky algorithm converges such that each term yields roughly 14 digits.
    iterations = (n_digits // 14) + 1

    # Precompute the constant: 426880 * sqrt(10005)
    constant = Decimal(426880) * Decimal(10005).sqrt()

    total = Decimal(0)
    
    # Sum the series:
    #   term_k = (-1)**k * (6k)! * (13591409 + 545140134*k)
    #            -------------------------------------------------- 
    #            (3k)! * (k!)^3 * (640320)^(3k)
    for k in range(iterations):
        # Compute numerator and denominator using high-precision arithmetic.
        numerator = Decimal(((-1) ** k)) * Decimal(factorial(6 * k)) * Decimal(13591409 + 545140134 * k)
        denominator = Decimal(factorial(3 * k)) * (Decimal(factorial(k)) ** 3) * (Decimal(640320) ** (3 * k))
        term = numerator / denominator
        total += term

    # Calculate π using the summed series.
    pi = constant / total

    # Format the result to exactly n_digits decimal places.
    # Find the decimal point and slice the string appropriately.
    pi_str = str(pi)
    dot_index = pi_str.find('.')
    if dot_index != -1:
        # Retain the integer part, the decimal point, and n_digits after the decimal.
        desired_length = dot_index + 1 + n_digits
        pi_str = pi_str[:desired_length]
    
    return pi_str

# Example usage
if __name__ == "__main__":
    n = 50  # Change this to the desired number of digits after the decimal point.
    print("Pi to", n, "decimal digits:")
    print(compute_pi(n))