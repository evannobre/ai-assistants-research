#!/usr/bin/env python3
"""
Pi Calculator using the Chudnovsky Algorithm
Computes N digits of Pi using arbitrary precision arithmetic

Usage: python3 pi_calculator.py <number_of_digits>
Example: python3 pi_calculator.py 1000
"""

import sys
import time
from decimal import Decimal, getcontext

def compute_pi_chudnovsky(digits):
    """
    Compute Pi to the specified number of digits using Chudnovsky algorithm.
    
    The Chudnovsky algorithm converges very rapidly:
    π = 1 / (12 * Σ((-1)^k * (6k)! * (13591409 + 545140134k)) / 
                    ((3k)! * (k!)^3 * 640320^(3k + 3/2)))
    
    Args:
        digits: Number of decimal digits of Pi to compute
    
    Returns:
        Decimal: Pi computed to the specified precision
    """
    # Set precision with extra guard digits for intermediate calculations
    # Extra 10 digits to account for rounding errors
    getcontext().prec = digits + 10
    
    # Constants for Chudnovsky algorithm
    C = 426880 * Decimal(10005).sqrt()
    K = Decimal(6)
    M = Decimal(1)
    X = Decimal(1)
    L = Decimal(13591409)
    S = Decimal(13591409)
    
    # Number of iterations needed (each iteration gives ~14 digits)
    iterations = digits // 14 + 1
    
    print(f"Computing {digits} digits of Pi...")
    print(f"Iterations required: {iterations}")
    print(f"Precision set to: {getcontext().prec} digits")
    print()
    
    for i in range(1, iterations):
        # Update M = (K^3 - 16K) * M / (i^3)
        M = M * (K ** 3 - 16 * K) / (i ** 3)
        
        # Update K
        K += 12
        
        # Update L
        L += 545140134
        
        # Update X = X * (-262537412640768000)
        X *= -262537412640768000
        
        # Update sum
        S += Decimal(M * L) / X
        
        # Progress indicator every 100 iterations
        if i % 100 == 0:
            print(f"Progress: {i}/{iterations} iterations completed")
    
    # Final calculation of Pi
    pi = C / S
    
    # Adjust precision to exact requested digits
    getcontext().prec = digits + 1
    
    return +pi

def validate_input(n_str):
    """
    Validate command-line input.
    
    Args:
        n_str: String representation of number of digits
    
    Returns:
        int: Validated number of digits
    
    Raises:
        ValueError: If input is invalid
    """
    try:
        n = int(n_str)
    except ValueError:
        raise ValueError(f"Invalid input: '{n_str}' is not a valid integer")
    
    if n <= 0:
        raise ValueError(f"Number of digits must be positive, got: {n}")
    
    # Memory estimation: roughly 10 bytes per digit of computation
    # With 8GB RAM, safe limit is around 100M digits
    max_safe_digits = 100_000_000
    if n > max_safe_digits:
        raise ValueError(
            f"Requested {n} digits exceeds safe limit of {max_safe_digits:,} digits\n"
            f"This would require more than the available 8GB RAM"
        )
    
    return n

def format_pi_output(pi_decimal, digits, show_full=True):
    """
    Format Pi for display.
    
    Args:
        pi_decimal: Decimal representation of Pi
        digits: Number of digits computed
        show_full: Whether to show all digits or truncate
    """
    pi_str = str(pi_decimal)
    
    print("\n" + "="*70)
    print(f"Pi to {digits} decimal places:")
    print("="*70)
    
    if show_full and digits <= 1000:
        # Show all digits for reasonable lengths
        print(pi_str[:digits + 2])  # +2 for "3."
    else:
        # Show first 100 and last 100 digits for very long results
        if len(pi_str) > 200:
            print(pi_str[:102] + "\n...\n" + pi_str[-(100):])
        else:
            print(pi_str[:digits + 2])
    
    print("="*70)

def main():
    """Main entry point for the Pi calculator."""
    if len(sys.argv) != 2:
        print("Usage: python3 pi_calculator.py <number_of_digits>")
        print("Example: python3 pi_calculator.py 1000")
        sys.exit(1)
    
    try:
        # Validate and parse input
        n_digits = validate_input(sys.argv[1])
        
        # Start timing
        start_time = time.time()
        
        # Compute Pi
        pi = compute_pi_chudnovsky(n_digits)
        
        # End timing
        elapsed_time = time.time() - start_time
        
        # Display results
        format_pi_output(pi, n_digits, show_full=(n_digits <= 10000))
        
        print(f"\nComputation completed in {elapsed_time:.2f} seconds")
        print(f"Memory-efficient: Used native Python decimal module")
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nComputation interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
