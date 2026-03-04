#!/usr/bin/env python3
"""
Calculate Pi to N digits using the Chudnovsky algorithm.
Uses Python's native decimal module for arbitrary precision arithmetic.
"""

import sys
from decimal import Decimal, getcontext
from math import factorial

def compute_pi(n_digits):
    """
    Compute Pi to n_digits precision using the Chudnovsky algorithm.
    
    The Chudnovsky algorithm:
    1/π = 12 * Σ((-1)^k * (6k)! * (545140134k + 13591409)) / ((3k)! * (k!)^3 * 640320^(3k + 3/2))
    
    Args:
        n_digits: Number of decimal digits to compute
    
    Returns:
        String representation of Pi to n_digits
    """
    # Set precision higher than needed to account for intermediate calculations
    getcontext().prec = n_digits + 10
    
    C = 426880 * Decimal(10005).sqrt()
    K = Decimal(6)
    M = Decimal(1)
    X = Decimal(1)
    L = Decimal(13591409)
    S = Decimal(13591409)
    
    # Calculate number of iterations needed
    # Each iteration gives approximately 14.18 digits
    iterations = int(n_digits / 14) + 1
    
    for i in range(1, iterations):
        M = M * (K ** 3 - 16 * K) / ((i) ** 3)
        K += 12
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / X
    
    pi = C / S
    
    # Convert to string with exact number of digits
    getcontext().prec = n_digits + 1
    pi_str = str(+pi)  # The + forces rounding to current precision
    
    # Format output: keep "3." and then n_digits-1 more digits
    if '.' in pi_str:
        integer_part, decimal_part = pi_str.split('.')
        return f"{integer_part}.{decimal_part[:n_digits-1]}"
    
    return pi_str


def main():
    """Main function to handle command-line arguments."""
    if len(sys.argv) != 2:
        print("Usage: python pi_calculator.py <number_of_digits>")
        print("Example: python pi_calculator.py 100")
        sys.exit(1)
    
    try:
        n_digits = int(sys.argv[1])
        if n_digits <= 0:
            print("Error: Number of digits must be positive")
            sys.exit(1)
        
        if n_digits > 100000:
            print(f"Warning: Computing {n_digits} digits may take a while...")
        
        pi = compute_pi(n_digits)
        print(f"Pi to {n_digits} digits:")
        print(pi)
        
    except ValueError:
        print("Error: Please provide a valid integer")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCalculation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
