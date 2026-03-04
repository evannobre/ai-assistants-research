import sys
from decimal import Decimal, getcontext

def calculate_pi(n):
    # Set precision to N + 2 for safety
    getcontext().prec = n + 2
    
    # Chudnovsky constants
    C = 426880 * Decimal(10005).sqrt()
    K = Decimal(6)
    M = Decimal(1)
    X = Decimal(1)
    L = Decimal(13591409)
    S = L
    
    # Calculate number of iterations required
    # Each iteration gives ~14.18 digits
    iterations = (n // 14) + 1

    for k in range(1, iterations):
        # M = M * (K**3 - 16*K) / k**3
        M = (M * (K**3 - 16 * K) / (k**3))
        L += 545140134
        X *= -262537412640768000
        S += (M * L) / X
        K += 12

    pi = C / S
    # Return exactly N digits
    return str(pi)[:n+2]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pi_gen.py <number_of_digits>")
        sys.exit(1)

    try:
        n_digits = int(sys.argv[1])
        if n_digits < 1:
            raise ValueError
        
        print(calculate_pi(n_digits))
    except ValueError:
        print("Error: Please provide a positive integer for N.")