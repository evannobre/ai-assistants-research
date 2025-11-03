import decimal
from decimal import Decimal, getcontext
import math

def compute_pi(n_digits):
    # Set precision: a few extra digits to prevent round-off errors
    getcontext().prec = n_digits + 10

    def factorial(n):
        if n < 2:
            return 1
        return math.prod(range(1, n + 1))

    def chudnovsky_term(k):
        # Components of the formula
        numerator = Decimal(factorial(6 * k)) * (13591409 + 545140134 * k)
        denominator = Decimal(factorial(3 * k)) * (factorial(k) ** 3) * (Decimal(640320) ** (3 * k))
        return ((-1) ** k) * numerator / denominator

    def compute_series(terms):
        return sum(chudnovsky_term(k) for k in range(terms))

    # Number of terms needed for n_digits
    terms = n_digits // 14 + 1

    # Chudnovsky constant factor
    C = 426880 * Decimal(10005).sqrt()
    pi_inverse = compute_series(terms)
    pi = C / pi_inverse

    # Return the result as a string with exactly n_digits
    return str(+pi)[:n_digits + 2]  # 2 accounts for "3."

# Example usage: Get 100 digits of pi
if __name__ == "__main__":
    N = 100  # You can change this to any number of digits
    pi_digits = compute_pi(N)
    print(f"Pi to {N} digits:\n{pi_digits}")
