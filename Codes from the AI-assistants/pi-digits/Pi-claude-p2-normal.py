#!/usr/bin/env python3
"""
Pi Calculator using Chudnovsky Algorithm with arbitrary precision
Optimized for Ubuntu 24.04 with 8GB RAM and 256GB SSD
Author: Backend Specialist
"""

import sys
import argparse
from decimal import Decimal, getcontext
from math import factorial
import time


def calculate_pi_chudnovsky(digits):
    """
    Calculate Pi to N digits using the Chudnovsky algorithm.
    
    Formula:
    1/π = 12 * Σ(k=0 to ∞) [(-1)^k * (6k)! * (545140134k + 13591409)] / 
                              [(3k)! * (k!)^3 * 640320^(3k + 3/2)]
    
    Args:
        digits (int): Number of decimal digits to compute
        
    Returns:
        str: Pi to the specified number of digits
    """
    # Set precision higher than needed to account for rounding errors
    # Rule of thumb: add 10-15 extra digits for intermediate calculations
    getcontext().prec = digits + 15
    
    # Chudnovsky algorithm constants
    C = 426880 * Decimal(10005).sqrt()
    K = Decimal(6)
    M = Decimal(1)
    X = Decimal(1)
    L = Decimal(13591409)
    S = Decimal(13591409)
    
    # Calculate number of iterations needed
    # Each iteration gives approximately 14 digits
    iterations = digits // 14 + 1
    
    print(f"Computing {digits} digits of Pi...")
    print(f"Iterations needed: {iterations}")
    print(f"Precision set to: {getcontext().prec}")
    
    for i in range(1, iterations):
        # Progress indicator for large computations
        if i % 100 == 0:
            print(f"Progress: {i}/{iterations} iterations ({100*i//iterations}%)")
        
        M = M * (K ** 3 - 16 * K) / ((i) ** 3)
        K += 12
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / X
    
    pi = C / S
    
    # Return as string with requested precision
    getcontext().prec = digits + 1
    return str(pi)[:digits + 2]  # +2 for "3."


def validate_memory_requirements(digits):
    """
    Estimate memory requirements and validate against system constraints.
    
    Args:
        digits (int): Number of digits to calculate
        
    Returns:
        bool: True if calculation is feasible
    """
    # Rough estimation: each digit requires ~4-8 bytes in memory
    # Plus overhead for intermediate calculations (multiply by 3-5)
    estimated_mb = (digits * 8 * 5) / (1024 * 1024)
    
    # Conservative limit: use max 6GB (leaving 2GB for OS)
    MAX_MEMORY_MB = 6 * 1024
    
    if estimated_mb > MAX_MEMORY_MB:
        print(f"ERROR: Estimated memory usage (~{estimated_mb:.0f} MB) exceeds safe limit ({MAX_MEMORY_MB} MB)")
        print(f"Maximum recommended digits for this system: ~{int(MAX_MEMORY_MB * 1024 * 1024 / (8 * 5))}")
        return False
    
    print(f"Estimated memory usage: ~{estimated_mb:.0f} MB")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Calculate Pi to arbitrary precision using Chudnovsky algorithm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 100          # Calculate 100 digits
  %(prog)s 10000        # Calculate 10,000 digits
  %(prog)s 1000000 -o pi.txt  # Calculate 1M digits and save to file
        """
    )
    
    parser.add_argument('digits', type=int, 
                        help='Number of decimal digits to calculate')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file path (default: print to stdout)')
    parser.add_argument('--no-validation', action='store_true',
                        help='Skip memory validation check')
    
    args = parser.parse_args()
    
    # Validate input
    if args.digits < 1:
        print("ERROR: Number of digits must be positive", file=sys.stderr)
        sys.exit(1)
    
    if args.digits > 100_000_000:
        print("WARNING: Calculations above 100M digits may take extremely long")
        print("Press Ctrl+C to cancel or wait 5 seconds to continue...")
        time.sleep(5)
    
    # Memory validation
    if not args.no_validation:
        if not validate_memory_requirements(args.digits):
            sys.exit(1)
    
    # Start calculation
    start_time = time.time()
    
    try:
        pi_value = calculate_pi_chudnovsky(args.digits)
        
        elapsed_time = time.time() - start_time
        print(f"\nCalculation completed in {elapsed_time:.2f} seconds")
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                f.write(pi_value)
            print(f"Pi written to: {args.output}")
            print(f"File size: {len(pi_value)} bytes")
        else:
            # Print first and last digits for verification
            if args.digits <= 1000:
                print(f"\nPi = {pi_value}")
            else:
                print(f"\nFirst 100 digits: {pi_value[:102]}")
                print(f"Last 100 digits: ...{pi_value[-100:]}")
                print(f"\nUse --output flag to save all {args.digits} digits to file")
        
        # Performance statistics
        digits_per_second = args.digits / elapsed_time
        print(f"\nPerformance: {digits_per_second:.0f} digits/second")
        
    except KeyboardInterrupt:
        print("\n\nCalculation interrupted by user")
        sys.exit(1)
    except MemoryError:
        print("\nERROR: Out of memory. Try reducing the number of digits.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
