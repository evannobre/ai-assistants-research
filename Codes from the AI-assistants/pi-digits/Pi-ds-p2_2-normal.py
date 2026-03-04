#!/usr/bin/env python3
# pi_gauss_legendre.py
import sys
import math
from decimal import Decimal, getcontext

def pi_gauss_legendre(digits):
    """Calculate pi using Gauss-Legendre algorithm"""
    getcontext().prec = digits + 10
    
    a = Decimal(1)
    b = Decimal(1) / Decimal(2).sqrt()
    t = Decimal(1) / Decimal(4)
    p = Decimal(1)
    
    for _ in range(int(math.log2(digits)) + 5):
        a_next = (a + b) / 2
        b = (a * b).sqrt()
        t -= p * (a - a_next) * (a - a_next)
        a = a_next
        p *= 2
    
    pi = (a + b) * (a + b) / (4 * t)
    return str(pi)[:digits + 2]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <digits>")
        sys.exit(1)
    
    try:
        digits = int(sys.argv[1])
        if digits <= 0:
            raise ValueError
        
        # Memory check
        if digits > 1000000:
            print(f"Warning: {digits} digits may require significant memory")
            response = input("Continue? (y/N): ")
            if response.lower() != 'y':
                sys.exit(0)
        
        pi = pi_gauss_legendre(digits)
        print(f"π to {digits} digits:\n{pi}")
        
    except ValueError:
        print("Please provide a positive integer")
        sys.exit(1)