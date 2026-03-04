import sys
from decimal import Decimal, getcontext

def calculate_pi(n):
    # Set precision to N + a small buffer to handle rounding errors
    getcontext().prec = n + 3
    
    num_iterations = n // 14 + 1  # Each term gives ~14.1 digits
    
    a_k = Decimal(10005).sqrt() * 426880
    k = 0
    linear_sum = Decimal(0)
    
    # Constants for the series
    K = Decimal(6)
    M = Decimal(1)
    L = Decimal(13591409)
    X = Decimal(1)
    S = Decimal(13591409)
    
    for k in range(1, num_iterations):
        # Update M (the ratio of factorials)
        M = (K**3 - 16*K) * M // Decimal(k)**3 
        L += 545140134
        X *= -262537412640768000
        S += (M * L) / X
        K += 12
        
    pi = a_k / S
    
    # Return pi truncated to N digits
    return str(pi)[:-3]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pi.py <number_of_digits>")
    else:
        digits = int(sys.argv[1])
        print(calculate_pi(digits))