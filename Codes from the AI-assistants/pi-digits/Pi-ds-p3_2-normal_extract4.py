import sys
import time

def spigot_pi_digits_v2(n):
    """
    Implementation of the Spigot algorithm for π (extract(4))
    Improved version with better performance
    """
    # Initialize arrays
    len_array = (10 * n) // 3
    a = [2] * (len_array + 1)
    result_digits = []
    
    nines = 0
    predigit = 0
    
    for j in range(1, n + 1):
        # Multiply by 10
        q = 0
        
        # Process from right to left
        for i in range(len_array, 0, -1):
            x = 10 * a[i] + q * i
            a[i] = x % (2 * i - 1)
            q = x // (2 * i - 1)
        
        # Handle first element
        a[1] = q % 10
        q = q // 10
        
        # Determine digit
        if q == 9:
            nines += 1
        elif q == 10:
            result_digits.append(str(predigit + 1))
            for k in range(nines):
                result_digits.append('0')
            predigit = 0
            nines = 0
        else:
            if predigit != 0 or not result_digits:  # Handle first digit
                result_digits.append(str(predigit))
            
            for k in range(nines):
                result_digits.append('9')
            
            predigit = q
            nines = 0
    
    # Add final predigit
    if predigit != 0:
        result_digits.append(str(predigit))
    
    return result_digits

def print_pi_digits_v2(digits):
    """Print digits 10 per line with running total"""
    print(f"3.", end="")
    
    if digits:
        # Print first digit after decimal
        print(digits[0], end="")
    
    # Print remaining digits 10 per line
    for i in range(1, len(digits), 10):
        line_end = min(i + 10, len(digits))
        line_digits = digits[i:line_end]
        print("\n" + "".join(line_digits), end="")
        print(f"   : {line_end}")
    
    print()

def main_v2():
    if len(sys.argv) != 2:
        print("Usage: python pi_spigot_v2.py <number_of_digits>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer")
        sys.exit(1)
    
    print(f"Calculating {n} digits of π using Spigot algorithm (extract(4))...")
    start_time = time.time()
    
    digits = spigot_pi_digits_v2(n)
    
    end_time = time.time()
    
    print(f"\nFirst {len(digits)} digits of π:")
    print_pi_digits_v2(digits)
    
    print(f"\nTime taken: {end_time - start_time:.2f} seconds")
    print(f"Digits calculated: {len(digits)}")

if __name__ == "__main__":
    main_v2()