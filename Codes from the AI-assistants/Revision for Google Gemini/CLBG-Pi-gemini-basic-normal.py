#!/usr/bin/env python3
import sys

def extract(x, q, r, t):
    """
    Evaluates the linear fractional transformation at x.
    Formula: (q * x + r) // t
    """
    return (q * x + r) // t

def pidigits(n):
    # Initial state for the LFT (Linear Fractional Transformation)
    q, r, t = 1, 0, 1
    k = 1
    
    digits_printed = 0
    current_line = ""

    while digits_printed < n:
        # Do both extract(3) and extract(4) as requested
        next_3 = extract(3, q, r, t)
        next_4 = extract(4, q, r, t)
        
        # If they match, the digit is stable and ready to be produced
        if next_3 == next_4:
            y = next_3
            
            # Produce the digit (multiply by 10)
            # q_new = 10 * q
            # r_new = 10 * r - 10 * y * t
            # t_new = t
            q, r, t = q * 10, 10 * (r - y * t), t
            
            current_line += str(y)
            digits_printed += 1
            
            # Print digits 10-to-a-line with the running total
            if digits_printed % 10 == 0:
                print(f"{current_line}\t:{digits_printed}")
                current_line = ""
                
        else:
            # If they don't match, we need more precision.
            # Consume the next term in the sequence k.
            # q_new = q * k
            # r_new = q * (4 * k + 2) + r * (2 * k + 1)
            # t_new = t * (2 * k + 1)
            q, r, t = (
                q * k,
                q * (4 * k + 2) + r * (2 * k + 1),
                t * (2 * k + 1)
            )
            k += 1

    # Handle any remaining digits if N is not a clean multiple of 10
    if digits_printed % 10 != 0:
        padding = 10 - (digits_printed % 10)
        print(f"{current_line}{' ' * padding}\t:{digits_printed}")

if __name__ == "__main__":
    # Use a larger command-line argument (defaulting to 10000)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    pidigits(n)