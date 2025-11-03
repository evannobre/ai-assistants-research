from decimal import Decimal, getcontext

def compute_pi_bbp(n):
    """Compute pi to n digits using the BBP formula with Decimal arithmetic."""
    getcontext().prec = n + 2  # extra precision for intermediate steps
    
    pi = Decimal(0)
    for k in range(n + 1):
        term = (Decimal(1)/(16**k)) * (
            Decimal(4)/(8*k + 1) -
            Decimal(2)/(8*k + 4) -
            Decimal(1)/(8*k + 5) -
            Decimal(1)/(8*k + 6)
        )
        pi += term
    
    # Return pi as a string with n digits
    return str(pi)[:n+2]  # +2 for "3."

# Example usage:
n = 100  # Number of digits
pi_digits = compute_pi_bbp(n)
print(f"Pi to {n} digits: {pi_digits}")