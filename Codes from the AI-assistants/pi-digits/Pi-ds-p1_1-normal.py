# pi_generator.py
import sys
import math
from decimal import Decimal, getcontext

def chudnovsky_pi(digits):
    """Chudnovsky algorithm for calculating Pi"""
    getcontext().prec = digits + 10  # Extra precision for intermediate calculations
    
    C = Decimal(426880) * Decimal(10005).sqrt()
    K = Decimal(6)
    M = Decimal(1)
    X = Decimal(1)
    L = Decimal(13591409)
    S = Decimal(13591409)
    
    for i in range(1, digits // 14 + 10):  # Rough estimate of iterations needed
        M = (K**3 - 16*K) * M // (i**3)
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / X
        K += 12
    
    pi = C / S
    return str(pi)[:digits + 2]  # +2 for "3."

def bailey_borwein_plouffe(digits):
    """BBP algorithm - allows digit extraction at arbitrary positions"""
    getcontext().prec = digits + 10
    
    pi = Decimal(0)
    for k in range(digits + 10):
        pi += (Decimal(1)/(16**k)) * (
            Decimal(4)/(8*k + 1) -
            Decimal(2)/(8*k + 4) -
            Decimal(1)/(8*k + 5) -
            Decimal(1)/(8*k + 6)
        )
    
    return str(pi)[:digits + 2]

def main():
    if len(sys.argv) != 2:
        print("Usage: python pi_generator.py <digits>")
        sys.exit(1)
    
    try:
        digits = int(sys.argv[1])
        if digits <= 0:
            print("Please provide a positive integer for digits")
            sys.exit(1)
        
        print(f"Generating {digits} digits of Pi...")
        pi = chudnovsky_pi(digits)
        print(pi)
        
    except ValueError:
        print("Please provide a valid integer")
        sys.exit(1)

if __name__ == "__main__":
    main()