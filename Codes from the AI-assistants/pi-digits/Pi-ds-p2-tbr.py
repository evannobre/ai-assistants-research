#!/usr/bin/env python3
"""
High-precision Pi calculator using Chudnovsky algorithm.
Optimized for Ubuntu 24.04.4 with 8GB RAM.
Uses Python's native decimal module (libmpdec C library).
"""

import sys
import math
import time
from decimal import Decimal, getcontext
import argparse
import psutil
import os

def check_memory_safety(n_digits, buffer_multiplier=1.2):
    """
    Check if the calculation is safe given 8GB RAM constraint.
    Returns safe digit limit and required memory in MB.
    """
    # Empirical memory usage: ~40 bytes per digit for intermediate calculations
    # Buffer multiplier accounts for Python overhead and other processes
    bytes_per_digit = 40
    estimated_memory_mb = (n_digits * bytes_per_digit * buffer_multiplier) / (1024 * 1024)
    
    total_memory = psutil.virtual_memory().total / (1024 * 1024)  # MB
    safe_memory = total_memory * 0.8  # Use only 80% of total RAM
    
    if estimated_memory_mb > safe_memory:
        max_digits = int((safe_memory * 1024 * 1024) / (bytes_per_digit * buffer_multiplier))
        return False, max_digits, estimated_memory_mb
    
    return True, n_digits, estimated_memory_mb

def chudnovsky_pi(n_digits):
    """
    Calculate pi using the Chudnovsky algorithm with arbitrary precision.
    This implementation is optimized for memory efficiency.
    
    Algorithm complexity: O(n log³ n) using binary splitting
    Memory usage: ~4 * precision bytes
    """
    # Set precision (extra digits for intermediate calculations)
    getcontext().prec = n_digits + 10
    
    # Constants for Chudnovsky algorithm
    C = Decimal(426880) * Decimal(10005).sqrt()
    
    # Initialize sums for binary splitting (memory efficient)
    def bs(a, b):
        """
        Binary splitting recursion for Chudnovsky series.
        Returns (P, Q, T) where pi = C * T / Q
        """
        if b - a == 1:
            if a == 0:
                P = Decimal(1)
                Q = Decimal(1)
            else:
                P = Decimal((6*a - 5) * (2*a - 1) * (6*a - 1))
                Q = Decimal(a * a * a * 26680)  # 26680 = 640320**3 / 24
            T = P * (Decimal(13591409) + Decimal(545140134) * a)
            if a & 1:
                T = -T
        else:
            mid = (a + b) // 2
            P1, Q1, T1 = bs(a, mid)
            P2, Q2, T2 = bs(mid, b)
            P = P1 * P2
            Q = Q1 * Q2
            T = T1 * Q2 + P1 * T2
        
        return P, Q, T
    
    # Calculate using binary splitting with depth control
    # to avoid excessive recursion depth for large n
    depth = 0
    terms_needed = int(n_digits / math.log10(640320**3 / 6 / 2 / 6)) + 10
    
    # Use iterative binary splitting for large calculations
    def compute_terms(terms):
        """Iterative binary splitting to avoid recursion depth issues."""
        stack = [(0, terms)]
        results = []
        
        while stack:
            a, b = stack.pop()
            if b - a == 1:
                if a == 0:
                    P = Decimal(1)
                    Q = Decimal(1)
                else:
                    P = Decimal((6*a - 5) * (2*a - 1) * (6*a - 1))
                    Q = Decimal(a * a * a * 26680)
                T = P * (Decimal(13591409) + Decimal(545140134) * a)
                if a & 1:
                    T = -T
                results.append((P, Q, T, a, b))
            else:
                mid = (a + b) // 2
                stack.append((mid, b))
                stack.append((a, mid))
        
        # Combine results
        while len(results) > 1:
            new_results = []
            for i in range(0, len(results), 2):
                if i + 1 < len(results):
                    P1, Q1, T1, a1, b1 = results[i]
                    P2, Q2, T2, a2, b2 = results[i + 1]
                    P = P1 * P2
                    Q = Q1 * Q2
                    T = T1 * Q2 + P1 * T2
                    new_results.append((P, Q, T, a1, b2))
                else:
                    new_results.append(results[i])
            results = new_results
        
        return results[0][:3] if results else (Decimal(1), Decimal(1), Decimal(0))
    
    # Compute pi
    P, Q, T = compute_terms(terms_needed)
    pi = C * Q / (T + C * Q / 2)  # More stable division
    
    # Set final precision and round
    getcontext().prec = n_digits
    pi = +pi  # Round to current context precision
    
    return pi

def write_pi_to_file(pi, n_digits, filename=None):
    """Write pi digits to file or stdout."""
    pi_str = str(pi)
    
    # Format with line breaks for readability
    digits_per_line = 100
    formatted = []
    
    # Handle the "3." part
    if pi_str.startswith('3.'):
        current = pi_str[:2]
        digits = pi_str[2:2 + n_digits - 1]
    else:
        current = pi_str[0]
        digits = pi_str[1:1 + n_digits - 1]
    
    # Add remaining digits in chunks
    for i in range(0, len(digits), digits_per_line):
        formatted.append(digits[i:i + digits_per_line])
    
    result = current + '\n' + '\n'.join(formatted)
    
    if filename:
        with open(filename, 'w') as f:
            f.write(f"Pi to {n_digits} digits:\n")
            f.write(result + '\n')
        print(f"Pi written to {filename}")
    else:
        print(f"Pi to {n_digits} digits:")
        print(result)

def main():
    parser = argparse.ArgumentParser(
        description='Calculate pi to N digits using arbitrary precision arithmetic.',
        epilog='Memory optimized for 8GB RAM systems. Uses native libmpdec (C library).'
    )
    parser.add_argument('digits', type=int, 
                       help='Number of pi digits to calculate')
    parser.add_argument('-o', '--output', type=str,
                       help='Output file (default: stdout)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output with performance metrics')
    parser.add_argument('-c', '--check', action='store_true',
                       help='Check memory safety before calculation')
    
    args = parser.parse_args()
    
    if args.digits <= 0:
        print("Error: Number of digits must be positive.", file=sys.stderr)
        sys.exit(1)
    
    # Memory safety check
    if args.check or args.digits > 10000:
        safe, max_digits, estimated_memory = check_memory_safety(args.digits)
        
        if args.verbose:
            total_memory = psutil.virtual_memory().total / (1024 * 1024)
            print(f"System RAM: {total_memory:.1f} MB")
            print(f"Estimated memory needed: {estimated_memory:.1f} MB")
            print(f"Safe memory limit: {total_memory * 0.8:.1f} MB")
        
        if not safe:
            print(f"Warning: Requested {args.digits} digits requires ~{estimated_memory:.1f} MB")
            print(f"Maximum safe digits for your system: {max_digits}")
            response = input(f"Continue with {max_digits} digits instead? (y/N): ")
            if response.lower() != 'y':
                print("Calculation cancelled.")
                sys.exit(0)
            args.digits = max_digits
    
    try:
        if args.verbose:
            print(f"Calculating pi to {args.digits} digits...")
            print(f"Using decimal precision: {args.digits + 10}")
            start_time = time.time()
            start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        
        # Calculate pi
        pi = chudnovsky_pi(args.digits)
        
        if args.verbose:
            end_time = time.time()
            end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            elapsed = end_time - start_time
            memory_used = end_memory - start_memory
            
            print(f"Calculation time: {elapsed:.2f} seconds")
            print(f"Memory used: {memory_used:.1f} MB")
            print(f"Digits per second: {args.digits / elapsed:.0f}")
        
        # Output results
        write_pi_to_file(pi, args.digits, args.output)
        
        # Verify first few digits if verbose
        if args.verbose and args.digits >= 10:
            known_pi = "3.1415926535"
            calculated = str(pi)[:12]
            if calculated == known_pi:
                print("Verification: First 10 digits correct ✓")
            else:
                print(f"Verification issue: {calculated} vs {known_pi}")
    
    except MemoryError:
        print(f"Error: Insufficient memory for {args.digits} digits.", file=sys.stderr)
        safe, max_digits, _ = check_memory_safety(args.digits)
        print(f"Try with {max_digits} digits or less.", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCalculation interrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Set resource limits to prevent system overload
    try:
        import resource
        # Soft limit of 6GB (leaves 2GB for system)
        resource.setrlimit(resource.RLIMIT_AS, 
                          (6 * 1024**3, 6 * 1024**3))
    except (ImportError, ValueError):
        pass  # Resource module not available or permission denied
    
    main()