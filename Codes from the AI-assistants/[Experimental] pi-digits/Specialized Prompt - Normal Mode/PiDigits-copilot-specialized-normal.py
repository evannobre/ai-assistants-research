import decimal

def calculate_pi(n):
    # Set the precision to calculate N digits of Pi
    decimal.getcontext().prec = n + 2  # Extra precision to avoid rounding errors
    pi = decimal.Decimal(0)
    k = 0
    while True:
        # BBP formula
        new_term = (decimal.Decimal(1) / (16 ** k)) * (
            decimal.Decimal(4) / (8 * k + 1) -
            decimal.Decimal(2) / (8 * k + 4) -
            decimal.Decimal(1) / (8 * k + 5) -
            decimal.Decimal(1) / (8 * k + 6)
        )
        if new_term == 0:
            break
        pi += new_term
        k += 1
    return +pi  # Unary plus applies rounding to the set precision

if __name__ == "__main__":
    # Number of digits to compute
    n = int(input("Enter the number of digits of Pi to calculate: "))
    pi = calculate_pi(n)
    print(f"Pi to {n} digits is:\n{str(pi)[:n + 2]}")