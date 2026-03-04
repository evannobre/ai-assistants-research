#!/usr/bin/env python3
import sys
import math
from decimal import Decimal, getcontext

def chudnovsky_pi(digits):
    """Chudnovsky algorithm for pi calculation"""
    getcontext().prec = digits + 10
    
    C = 426880 * Decimal(10005).sqrt()
    K = Decimal(6)
    M = Decimal(1)
    X = Decimal(1)
    L = Decimal(13591409)
    S = L
    
    for i in range(1, digits//14 + 10):
        M = M * (K**3 - 16*K) / ((i+1)**3)
        K += 12
        L += 545140134
        X *= -262537412640768000
        S += M * L / X
    
    pi = C / S
    return str(pi)[:digits + 2]  # +2 for "3."

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <number_of_digits>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            print("Number of digits must be positive")
            sys.exit(1)
        
        # Simple pi generation using built-in math.pi for small n
        if n <= 15:
            print(f"{math.pi:.{n}f}")
        else:
            print(chudnovsky_pi(n))
    except ValueError:
        print("Please provide a valid integer")