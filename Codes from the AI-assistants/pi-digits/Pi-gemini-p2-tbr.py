#!/usr/bin/env python3
import sys
import math
from decimal import Decimal, getcontext
import argparse
import time

def compute_pi(n_digits):
    """
    Computes Pi to n_digits using the Chudnovsky algorithm with binary splitting.
    """
    
    # Extra precision to prevent rounding errors during intermediate calculations
    # We add a buffer of digits
    getcontext().prec = n_digits + 20
    
    # Chudnovsky Algorithm Constants
    C = 640320
    C3_OVER_24 = C**3 // 24
    
    def binary_split(a, b):
        """
        Recursive binary splitting to compute the terms of the series.
        Returns a tuple (P, Q, T) where:
        P = partial product of terms in the numerator
        Q = partial product of terms in the denominator
        T = partial sum of the series (scaled)
        """
        if b - a == 1:
            # Base case for recursion: compute a single term
            if a == 0:
                Pab = 1
                Qab = 1
            else:
                Pab = (6*a - 5) * (2*a - 1) * (6*a - 1)
                Qab = a**3 * C3_OVER_24
            
            Tab = Pab * (13591409 + 545140134 * a)
            
            # For odd indices, the term is negative (handled by (-1)^k logic in series)
            if a & 1:
                Tab = -Tab
            return Pab, Qab, Tab
        
        else:
            # Recursive step: split the range [a, b) into two halves
            m = (a + b) // 2
            Pam, Qam, Tam = binary_split(a, m)
            Pmb, Qmb, Tmb = binary_split(m, b)
            
            # Combine the results
            Pab = Pam * Pmb
            Qab = Qam * Qmb
            Tab = Qam * Tmb + Pam * Tam
            return Pab, Qab, Tab

    # Estimate number of terms needed for N digits
    # Chudnovsky converges at ~14.18 digits per term
    n_terms = n_digits // 14 + 1
    
    print(f"[*] Initializing calculation for {n_digits} digits...")
    print(f"[*] Computed terms required: {n_terms}")
    
    start_time = time.time()
    
    # Perform Binary Splitting
    P, Q, T = binary_split(0, n_terms)
    
    # Final calculation using Decimal for the division and square root
    # Pi = (Q * 426880 * sqrt(10005)) / T
    print("[*] Performing final division and square root...")
    
    # We use Decimal for the final high-precision arithmetic
    Q_dec = Decimal(Q)
    T_dec = Decimal(T)
    const_dec = Decimal(426880) * Decimal(10005).sqrt()
    
    pi_val = (Q_dec * const_dec) / T_dec
    
    end_time = time.time()
    print(f"[*] Calculation completed in {end_time - start_time:.4f} seconds.")
    
    return pi_val

def main():
    parser = argparse.ArgumentParser(description='Generate N digits of Pi using Arbitrary Precision.')
    parser.add_argument('digits', type=int, help='Number of decimal digits to generate')
    parser.add_argument('--out', type=str, help='Output file path (optional)', default=None)
    
    args = parser.parse_args()
    
    if args.digits < 1:
        print("Error: Number of digits must be positive.")
        sys.exit(1)
        
    # Validating generic memory constraints for the provided hardware (8GB RAM)
    # 100 million digits is roughly the safe upper bound for a quick script without swap thrashing.
    if args.digits > 100_000_000:
        print("WARNING: Generating > 100M digits may exceed 8GB RAM depending on system load.")
        confirm = input("Continue? (y/n): ")
        if confirm.lower() != 'y':
            sys.exit(0)

    pi = compute_pi(args.digits)
    
    # Format string to remove the '3.' and print as requested or save
    pi_str = str(pi)
    
    # Result usually looks like "3.14159..."
    # If the user strictly wants N digits (including the 3), we slice string.
    output = pi_str[:args.digits + 1] # +1 to account for decimal point
    
    if args.out:
        with open(args.out, 'w') as f:
            f.write(output)
        print(f"[*] Result saved to {args.out}")
    else:
        # If outputting to CLI, avoid spamming terminal if N is huge
        if args.digits > 1000:
            print(f"\nResult (first 1000 digits):\n{output[:1001]}...")
            print(f"\n(Full output truncated for terminal readability. Use --out to save to file.)")
        else:
            print(f"\nResult:\n{output}")

if __name__ == "__main__":
    main()