import decimal
from decimal import Decimal, getcontext
import math

def compute_pi(n_digits: int) -> str:
    # Set precision higher than needed to ensure accuracy
    extra_digits = 10
    getcontext().prec = n_digits + extra_digits

    def factorial(n):
        if n == 0:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    def chudnovsky_term(k):
        # Constants
        C = 426880 * Decimal(10005).sqrt()
        M = factorial(6 * k)
        L = 545140134 * k + 13591409
        X = (-262537412640768000) ** k  # = -640320^3
        K = factorial(3 * k) * (factorial(k) ** 3)

        return Decimal(M * L) / Decimal(K * X)

    # Sum series until desired precision
    total = Decimal(0)
    k = 0
    while True:
        term = chudnovsky_term(k)
        total += term
        if term < Decimal(10) ** -(n_digits + 5):  # heuristic stop
            break
        k += 1

    pi = (426880 * Decimal(10005).sqrt()) / total

    # Return as a string with only the first n digits
    pi_str = str(pi)[:n_digits + 2]  # +2 for "3."
    return pi_str

# Example: compute 100 digits of Pi
if __name__ == "__main__":
    digits = 100
    pi_value = compute_pi(digits)
    print(f"Pi to {digits} digits:\n{pi_value}")