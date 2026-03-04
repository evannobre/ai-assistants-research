import sys
import time

def spigot_pi_digits(n):
    """
    Implementation of the Spigot algorithm for π (extract(3))
    Based on Rabinowitz & Wagon's "A Spigot Algorithm for the Digits of Pi"
    """
    # Initialize
    pi_digits = []
    predigit = 0
    
    # Length of array - more than n/4 is sufficient
    array_len = (10 * n) // 3 + 1
    a = [2] * array_len
    
    # Main loop
    for j in range(1, n + 1):
        # Step 1: Multiply by 10
        carry = 0
        
        # Work from right to left
        for i in range(array_len - 1, -1, -1):
            numerator = i
            denominator = 2 * i + 1
            temp = a[i] * 10 + carry
            a[i] = temp % denominator if i > 0 else temp % 10
            carry = temp // denominator if i > 0 else temp // 10
        
        # Step 2: Extract next digit
        q = carry // 10
        r = carry % 10
        
        # Step 3: Adjust
        if q == 9:
            # Accumulate nines
            predigit += 1
        else:
            # Output the predigit
            if predigit > 0:
                pi_digits.append(str(predigit))
                if q == 10:
                    pi_digits.append('0')
            elif q == 10:
                pi_digits.append('1')
                q = 0
            
            # Output current digit
            pi_digits.append(str(q))
            predigit = r if q != 10 else 0
    
    # Handle any remaining predigit
    if predigit > 0:
        pi_digits.append(str(predigit))
    
    return pi_digits

def print_pi_digits(digits):
    """Print digits 10 per line with running total"""
    print(f"3.", end="")
    
    for i, digit in enumerate(digits[:1]):  # First digit after decimal
        print(digit, end="")
    
    # Print remaining digits 10 per line
    remaining_digits = digits[1:] if len(digits) > 1 else []
    
    for i in range(0, len(remaining_digits), 10):
        line_digits = remaining_digits[i:i + 10]
        print("\n" + "".join(line_digits), end="")
        print(f"   : {i + 1 + 1}")  # +1 for the first digit after decimal
    
    print()  # Final newline

def main():
    if len(sys.argv) != 2:
        print("Usage: python pi_spigot.py <number_of_digits>")
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer")
        sys.exit(1)
    
    print(f"Calculating {n} digits of π using Spigot algorithm (extract(3))...")
    start_time = time.time()
    
    digits = spigot_pi_digits(n)
    
    end_time = time.time()
    
    print(f"\nFirst {len(digits)} digits of π:")
    print_pi_digits(digits)
    
    print(f"\nTime taken: {end_time - start_time:.2f} seconds")
    print(f"Digits calculated: {len(digits)}")

if __name__ == "__main__":
    main()