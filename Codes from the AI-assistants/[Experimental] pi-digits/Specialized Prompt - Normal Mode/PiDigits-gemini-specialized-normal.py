from decimal import Decimal, getcontext
import math

def factorial(n):
    if n == 0:
        return Decimal(1)
    res = Decimal(1)
    for i in range(1, n + 1):
        res *= Decimal(i)
    return res

def chudnovsky(n_digits):
    getcontext().prec = n_digits + 20  # Set precision

    k = 0
    total = Decimal(0)
    C = 640320
    C3_24 = C**3 * 24  # Optimization

    while True:
        term_numerator = Decimal((-1)**k) * factorial(6 * k) * (13591409 + 545140134 * k)
        term_denominator = factorial(3 * k) * (factorial(k)**3) * (C3_24**(k))
        term = term_numerator / term_denominator
        total += term

        if abs(term) < Decimal(10)**(-(n_digits + 1)): # Check for convergence
            break
        k += 1

    pi_inverse = (12 / Decimal(C).sqrt()) * total
    pi = 1 / pi_inverse
    return format(pi, f".{n_digits}f")

if __name__ == "__main__":
    n = 1000  # Example: Generate 1000 digits of Pi
    pi_value = chudnovsky(n)
    print(f"First {n} digits of Pi:\n{pi_value}")