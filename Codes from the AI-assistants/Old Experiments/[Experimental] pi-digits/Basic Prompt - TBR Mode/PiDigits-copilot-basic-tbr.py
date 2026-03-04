import math
from decimal import Decimal, getcontext

def compute_pi(n_digits: int) -> str:
    """
    Computes π to n_digits after the decimal point using the Chudnovsky algorithm.
    
    Parameters:
      n_digits (int): Number of digits after the decimal point to compute.
      
    Returns:
      str: π as a string, truncated to the requested number of digits.
    """
    # Add extra precision to counteract round-off error during intermediate computations.
    extra_digits = 10
    getcontext().prec = n_digits + extra_digits

    # Constants used in the Chudnovsky formula.
    # C = 426880 * sqrt(10005)
    C = Decimal(426880) * Decimal(10005).sqrt()

    # Initialize the series accumulators.
    M = Decimal(1)         # Multiplier for the term
    L = Decimal(13591409)   # Linear term (which increases by 545140134 per iteration)
    X = Decimal(1)         # Denominator multiplier (grows rapidly)
    S = L                  # Initialize series sum with the first term.

    # Number of iterations required (each iteration provides ~14 digits).
    iterations = n_digits // 14 + 1

    # Loop to add the series terms
    for k in range(1, iterations):
        # Update the multiplier M.
        # The formula below updates M using:
        #   M[k] = M[k-1] * ( (6*k-5) * (2*k-1) * (6*k-1) ) / (k^3)
        M = (M * Decimal((6 * k - 5) * (2 * k - 1) * (6 * k - 1))) / Decimal(k ** 3)
        
        # Update L and X.
        L += Decimal(545140134)
        X *= Decimal(-262537412640768000)
        
        # Add the new term to the sum S.
        S += M * L / X

    # Compute pi using the formula.
    pi = C / S

    # Convert to string. The str() conversion of a Decimal gives us a string
    # that we can then truncate appropriately.
    str_pi = format(pi, 'f')
    
    # Now, we want exactly n_digits after the decimal.
    if '.' in str_pi:
        integer_part, dot, fraction = str_pi.partition('.')
        # Ensure that we have at least n_digits in the fractional part.
        fraction = fraction[:n_digits].ljust(n_digits, '0')
        result = f"{integer_part}.{fraction}"
    else:
        # Unlikely scenario since π has a fractional part.
        result = str_pi

    return result

# Example usage: compute 100 digits of π.
if __name__ == "__main__":
    digits = 100  # Change N to whatever number of digits you require.
    pi_digits = compute_pi(digits)
    print(f"π to {digits} digits:\n{pi_digits}")