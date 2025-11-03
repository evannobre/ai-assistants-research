from decimal import Decimal, getcontext

def compute_pi(n):
    # Set the precision to n digits plus a buffer to handle rounding
    extra_digits = 20
    getcontext().prec = n + extra_digits

    # Constants for the Chudnovsky formula
    A = Decimal(13591409)
    B = Decimal(545140134)
    C = Decimal(640320)
    C_cubed = C ** 3
    twenty_four = Decimal(24)
    one = Decimal(1)
    two = Decimal(2)
    six = Decimal(6)

    # Initialize the sum with the first term (k=0)
    sum_S = A
    term = A
    k = 1

    while True:
        # Calculate components of the recurrence relation
        k_decimal = Decimal(k)
        numerator_part = (six * k_decimal - one) * (two * k_decimal - one) * (six * k_decimal - Decimal(5))
        numerator = -twenty_four * numerator_part * (A + B * k_decimal)
        denominator = (A + B * (k_decimal - one)) * (k_decimal ** 3) * C_cubed

        # Update the term using the recurrence relation
        term *= numerator / denominator

        # Add the new term to the sum
        sum_S += term

        # Check if the term is smaller than the desired epsilon
        if abs(term) < Decimal(10) ** (-(n + extra_digits - 1)):
            break

        k += 1

    # Compute the final value of pi
    pi = (Decimal(426880) * Decimal(10005).sqrt()) / sum_S

    # Round to the desired number of digits
    getcontext().prec = n
    return +pi.quantize(Decimal(10) ** (-n + 1))

# Example usage:
n = 100  # Number of digits
pi = compute_pi(n)
print(pi)