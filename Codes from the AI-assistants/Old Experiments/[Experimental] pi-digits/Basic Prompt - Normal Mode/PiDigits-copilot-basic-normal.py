from decimal import Decimal, getcontext

def calculate_pi(n_digits):
    # Set precision (higher than n_digits to ensure accuracy)
    getcontext().prec = n_digits + 2  # Extra digits for safety

    pi = Decimal(0)
    k = 0
    while True:
        # BBP formula terms
        new_term = (Decimal(4) / (8 * k + 1) 
                    - Decimal(2) / (8 * k + 4)
                    - Decimal(1) / (8 * k + 5) 
                    - Decimal(1) / (8 * k + 6)) / (16 ** k)

        # If terms are negligible, break
        if abs(new_term) < Decimal(10) ** -n_digits:
            break
        
        pi += new_term
        k += 1

    # Truncate to requested digits
    pi_str = str(pi)[:n_digits + 2]  # Account for "3."
    return pi_str

# Example: Generate 100 digits of Pi
n = 100
result = calculate_pi(n)
print(result)