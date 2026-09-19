#!/usr/bin/env python3
import sys
import math
import argparse
import time

def chudnovsky_bs(a, b):
    """
    Computes the partial sum of the Chudnovsky series using Binary Splitting.
    """
    if b - a == 1:
        # Base case: compute P, Q, and T for a single term
        if a == 0:
            Pab = 1
            Qab = 1
        else:
            Pab = -(6 * a - 5) * (2 * a - 1) * (6 * a - 1)
            Qab = (a ** 3) * 10939058860032000  # (640320**3) // 24
            
        Tab = Pab * (13591409 + 545140134 * a)
        return Pab, Qab, Tab
    
    # Divide and conquer
    m = (a + b) // 2
    Pam, Qam, Tam = chudnovsky_bs(a, m)
    Pmb, Qmb, Tmb = chudnovsky_bs(m, b)
    
    # Recombine fractions
    Pab = Pam * Pmb
    Qab = Qam * Qmb
    Tab = Tam * Qmb + Pam * Tmb
    
    return Pab, Qab, Tab

def compute_pi(n_digits):
    """
    Computes Pi to `n_digits` using integer arithmetic exclusively.
    """
    # The Chudnovsky series yields approx 14.18 digits per term
    terms = int(n_digits / 14.181647462725477) + 2
    
    # Calculate the fraction P, Q, T
    _, Q, T = chudnovsky_bs(0, terms)
    
    # We use 10 guard digits to prevent rounding errors at the final decimal boundary
    guard_digits = 10
    total_digits = n_digits + guard_digits
    
    # Pi = (426880 * sqrt(10005) * Q) / T
    # To compute this purely with integers, scale the sqrt by 10^(2 * total_digits)
    scale = 10 ** (2 * total_digits)
    sqrt_term = math.isqrt(10005 * scale)
    
    numerator = 426880 * sqrt_term * Q
    pi_scaled = numerator // T
    
    # Convert to string and drop the guard digits
    pi_str = str(pi_scaled)[:-guard_digits]
    
    if n_digits == 0:
        return "3"
    
    # Format the output as 3.1415...
    return f"{pi_str[0]}.{pi_str[1:]}"

def main():
    parser = argparse.ArgumentParser(description="Generate N digits of Pi using the Chudnovsky Algorithm.")
    parser.add_argument("digits", type=int, help="Number of decimal digits of Pi to generate.")
    args = parser.parse_args()

    if args.digits < 0:
        print("Error: The number of digits must be a non-negative integer.")
        sys.exit(1)

    # In Python 3.11+, we must increase the string-to-int conversion limit for huge outputs.
    # We cap the lower bound to 4300 to respect standard Python environment rules.
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(max(args.digits + 100, 4300))

    try:
        start_time = time.time()
        pi_val = compute_pi(args.digits)
        elapsed_time = time.time() - start_time
        
        print(pi_val)
        print(f"\n# Successfully computed {args.digits} digits in {elapsed_time:.4f} seconds.")
        
    except MemoryError:
        print("Error: The requested number of digits exceeds your available 8 GB system memory limit.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()